import logging
logger = logging.getLogger("Inputstream")

import asyncio
from datetime import datetime, timedelta, date
from enum import Enum
import gzip
import hashlib
import os
import json
import struct
from uuid import UUID
import requests
from acelerai_inputstream.inputstream import INSERTION_MODE, Inputstream, InputstreamStatus, InputstreamType
#from jsonschema import Draft4Validator
import fastjsonschema
from dateutil import parser
import httpx
import gzip
from decimal import Decimal
import msgpack

global __mode
__mode = os.environ.get("EXEC_LOCATION", "CLOUD")
SEM = asyncio.Semaphore(20)  # Limitar concurrencia a 20 conexiones

def custom_encoder(obj):
    """Convierte tipos no serializables como datetime y Decimal."""
    if isinstance(obj, datetime):
        return obj.isoformat()  # Serializar datetime como cadena ISO 8601
    if isinstance(obj, Decimal):
        return float(obj)  # Serializar Decimal como flotante
    raise TypeError(f"Object of type {type(obj).__name__} is not serializable")

def decode_datetime(obj):
    """Deserializa cadenas ISO 8601 a objetos datetime."""
    for key, value in obj.items():
        if isinstance(value, str):
            try:
                obj[key] = datetime.fromisoformat(value)  # Deserializar datetime
            except ValueError:
                pass
        elif isinstance(value, float):
            obj[key] = Decimal(value)  # Convertir flotantes de regreso a Decimal
    return obj

def load_full_object(file_path):
    """Carga completamente el objeto desde un archivo MessagePack en memoria."""
    try:
        with open(file_path, "rb") as file:
            # Cargar todos los registros en memoria como una lista
            unpacker = msgpack.Unpacker(file, raw=False)
            data = [record for record in unpacker]  # Deserializar todos los registros
        return data
    except Exception as e:
        logger.error(f"Error al cargar el archivo: {e}", exc_info=True)
        return None

if __mode != "LOCAL":
    # Environment production
    DATA_URL        = os.environ.get("DATA_URL"         , "https://stream.aceler.ai")
    QUERY_MANAGER   = os.environ.get("QUERY_MANAGER"    , "https://stream.aceler.ai")  
    INPUTSTREAM_URL = os.environ.get("INPUTSTREAM_URL"  , "https://apigw.aceler.ai")
    verify_https = True
else:
    # Environment development
    DATA_URL        = os.environ.get("DATA_URL", "https://localhost:1008")
    QUERY_MANAGER   = os.environ.get("QUERY_MANAGER", "https://localhost:8000")
    INPUTSTREAM_URL = os.environ.get("INPUTSTREAM_URL", "https://localhost:1006")
    verify_https = False

packer = msgpack.Packer(default=custom_encoder)  # Configurar el hook de serialización


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Enum):
            return obj.value
        
        elif isinstance(obj, datetime):
            return obj.isoformat()
        
        elif isinstance(obj,date):
            return obj.isoformat()
        
        elif isinstance(obj, UUID):
            return str(obj)
        else:
            return super().default(obj)


class CustomJsonDecoder(json.JSONDecoder):
    def __init__(self, *args ,**kargs):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kargs)

    def object_hook(self, obj:dict):
        for k, v in obj.items():
            if isinstance(v, str) and 'T' in v and '-' in v and ':' in v and len(v) < 40:
                try:
                    dv = parser.parse(v)
                    dt = dv.replace(tzinfo=None)
                    obj[k] = dt
                except:
                    pass
            elif isinstance(v, str) and '-' in v and len(v) < 11:
                try:
                    obj[k] = parser.parse(v).date()
                except:
                    pass
        return obj


class CacheManager:
    duration_inputstream:int
    duration_data:int

    def __init__(self, cache_options: dict | None = None):
        if cache_options is None:
            self.duration_data = 60 * 24
            self.duration_inputstream = 60 * 24
        else:
            self.duration_data = cache_options.get("duration_data", 60 * 24)
            self.duration_inputstream = cache_options.get("duration_inputstream", 60 * 24)

        # create cache directories
        if not os.path.exists(".acelerai_cache"):
            os.mkdir(".acelerai_cache")
            os.mkdir(".acelerai_cache/data")
        
    def get_inputstream(self, ikey:str) -> Inputstream | None:
        """
        return Inputstream if exists in cache and is not expired
        otherwise return None
        params:
            ikey: str
        """
        file_name = f".acelerai_cache/inputstreams/{ikey}.json"
        if os.path.exists(file_name):
            logger.info(f"Inputstream - Ikey: {ikey}, Checking cache expiration...")
            data = json.loads(open(file_name, "r").read(), cls=CustomJsonDecoder)
            if datetime.utcnow() < data["duration"]:
                logger.info(f"Inputstream - Ikey: {ikey}, from cache")
                return Inputstream(**data["inputstream"])
            else:
                logger.info(f"Inputstream - Ikey: {ikey}, Cache expired, removing file...")
                os.remove(file_name)
                return None
        return None

    def set_inputstream(self, inputstream:Inputstream):
        cache_register = {
            "inputstream": inputstream.get_dict(),
            "duration": datetime.utcnow() + timedelta(minutes=self.duration_inputstream)
        }

        file_name = inputstream.Ikey
        if not os.path.exists(f".acelerai_cache/inputstreams/"): os.mkdir(f".acelerai_cache/inputstreams/")
        open(f".acelerai_cache/inputstreams/{file_name}.msgpack", "w+").write(json.dumps(cache_register, cls=CustomJSONEncoder))

    def get_data(self, ikey:str, hash_query:str) -> list[dict] | None:
        """
        return data if exists in cache and is not expired
        otherwise return None
        params:
            ikey: str
            query: dict
        """
        file_name = f".acelerai_cache/data/{ikey}/{hash_query}.msgpack"
        index_ttl_file = f".acelerai_cache/data/ttl_index.json"
        if os.path.exists(file_name) and os.path.exists(index_ttl_file):

            # check if cache is expired
            logger.info(f"Data - Ikey: {ikey}, Checking cache expiration...")
            index = json.loads(open(index_ttl_file, "r").read(), cls=CustomJsonDecoder)
            ttl_key = f"{ikey}_{hash_query}"
            if ttl_key in index:
                ttl = index[ttl_key]
                if datetime.utcnow() > ttl:
                    logger.info(f"Data - Ikey: {ikey}, Cache expired, removing file...")
                    os.remove(file_name)
                    return None

            # recover data from cache
            try:
                logger.info(f"Data - Ikey: {ikey}, Recovering data from cache...")
                data = load_full_object(file_name)
                logger.info(f"Data - Ikey: {ikey}, from cache")
                return data
            except Exception as e:
                if os.path.exists(file_name): os.remove(file_name)
                raise Exception(f"Error reading cache file: {file_name} - {e}", stack_info=True)
        else:
            if os.path.exists(file_name): os.remove(file_name)
            return None
    
    def set_data(self, ikey:str, hash_query:str):
        # update ttl index
        ttl_key = f"{ikey}_{hash_query}"
        ttl = datetime.utcnow() + timedelta(minutes=self.duration_data)
        index_file = f".acelerai_cache/data/ttl_index.json"
        if os.path.exists(index_file):
            index = json.loads(open(index_file, "r").read(), cls=CustomJsonDecoder)
            index[ttl_key] = ttl
            open(index_file, "w+").write(json.dumps(index, cls=CustomJSONEncoder))
        else:
            open(index_file, "w+").write(json.dumps({ttl_key: ttl}, cls=CustomJSONEncoder))


class AcelerAIHttpClient():

    def __init__(self, token:str):
        self.token = token
        self.lock = asyncio.Lock()

    def get_inputstream_by_ikey(self, ikey:str) -> Inputstream:
        try:
            headers = { "Authorization": f"A2G {self.token}"}
            # proxies = {'https': 'http://127.0.0.1:1000'}

            res = requests.get(INPUTSTREAM_URL + f"/Inputstream/Ikey/{ikey}", headers=headers, verify=verify_https)
            logger.info(f"Getting inputstream with ikey: {ikey} from ACELER.AI...")
            if res.status_code != 200:
                if res.status_code == 404: raise Exception("Inputstream not found, please check your ikey")
                if res.status_code == 401: raise Exception("Unauthorized: please check your token or access permissions")
                if res.status_code == 403: raise Exception("Forbidden: please check your access permissions")
                raise Exception(f"Error getting inputstream, {res.status_code} {res.text}")
            content = res.json(cls=CustomJsonDecoder)
            if not content["success"]: raise Exception(content["errorMessage"])
            return Inputstream(from_response=True, **content["data"])
        except Exception as e:
            raise e
        
    async def _write_to_file(self, ikey, query, data):
        query_str = json.dumps(query, cls=CustomJSONEncoder)
        query_hash = hashlib.sha256(query_str.encode()).hexdigest()

        # save data
        file_name = f".acelerai_cache/data/{ikey}/{query_hash}.msgpack"

        async with self.lock:  # Garantiza que solo una tarea escriba a la vez
            with open(file_name, "ab") as file:
                for record in data:
                    file.write(packer.pack(record))
    
    async def fetch_page(self, ikey:str, query:dict,delete_id:bool=True, page:int=1, page_size:int=1000):
        async with SEM:
            headers = {
                "Authorization": f"A2G {self.token}",
                "ikey": ikey,
                'Content-Type': 'application/json'
            }
       
            my_body = {
                "delete_id": delete_id,
                "query": json.dumps(query, cls=CustomJSONEncoder) 
            }

            buffer = b""  # Buffer para ensamblar datos incompletos
            s = datetime.utcnow()
            timeout = httpx.Timeout(60.0, connect=10.0, read=600.0)

            async with httpx.AsyncClient(http2=True, verify=False, timeout=timeout) as client:
                async with client.stream("POST", f"{QUERY_MANAGER}/QueryData/Find", 
                    json=my_body, 
                    headers=headers,
                    params={"page": page, "page_size": page_size }) as response:

                    if response.status_code != 200:
                        msg = ''
                        async for chunk in response.aiter_bytes():
                            if chunk:
                                msg += chunk.decode("utf-8")

                        raise Exception(f"{response.status_code} {msg}")
                    
                    async for chunk in response.aiter_bytes():
                        buffer += chunk  # Agregar los datos al buffer
                        while len(buffer) >= 4:  # Asegurarse de que al menos 4 bytes están disponibles
                            obj_length = struct.unpack(">I", buffer[:4])[0]

                            if len(buffer) < 4 + obj_length:
                                break  # Esperar más datos si el objeto no está completo

                            obj_data = buffer[4: 4 + obj_length]
                            buffer = buffer[4 + obj_length:]  # Actualizar el buffer
                            decompressed_data = gzip.decompress(obj_data)  # Descomprimir los datos
                            data = msgpack.unpackb(decompressed_data, object_hook=decode_datetime)  # Deserializar el objeto
                            
                            await self._write_to_file(ikey, query, data)
            
                    logger.info(f"Page {page} downloaded")
            
    def find_one(self, ikey:str, query:dict) -> list[dict]:
        try:
            headers = {
                "Authorization": f"A2G {self.token}",
                "ikey": ikey,
                'Content-Type': 'application/json'
            }
            res = requests.post(QUERY_MANAGER + "/QueryData/FindOne", 
                data=json.dumps(query, cls=CustomJSONEncoder),
                headers=headers, 
                verify=verify_https
            )
            if res.status_code != 200: raise Exception(f"Error getting inputstream {res.status_code} {res.content}")
            content = res.json(cls=CustomJsonDecoder)
            if not content["success"]: raise Exception(content["errorMessage"])
            return content["data"]
        except Exception as e:
            raise e
        
    def aggregate(self, ikey:str, pipeline: list[dict]) -> list[dict]:
        try:
            headers = {
                "Authorization": f"A2G {self.token}",
                "ikey": ikey,
                'Content-Type': 'application/json'
            }

            if not all(isinstance(x, dict) for x in pipeline):      raise Exception("Invalid pipeline, the steps must be dictionaries")
            if len(pipeline) == 0:                                  raise Exception("Invalid pipeline, length must be greater than 0" )
            if any("$out" in x or "$merge" in x for x in pipeline): raise Exception("Invalid pipeline, write operations not allowed"  )

            res = requests.post(f"{QUERY_MANAGER}/QueryData/ExecutionPlanningAggregate", 
                data = json.dumps(pipeline, cls=CustomJSONEncoder), 
                headers=headers, 
                verify=verify_https
            )
            if res.status_code != 200: 
                raise Exception(f"Error getting execution planning {res.status_code} {res.content}")
            
            content = res.json(cls=CustomJsonDecoder)
            if not content["success"]: raise Exception(content["errorMessage"])
            
            total_query     = content["data"]["total"]
            page_size       = content["data"]["size"]

            total_batchs    = (total_query // page_size) + 1
            logger.info(f"Total documents to download {total_query}.")
            logger.info(f"Batch 1/{total_batchs}")

            downloaded_docs = 0
            page            = 1
            total_batchs    = (total_query // page_size) + 1
            docs            = []
            while downloaded_docs < total_query:
                res = requests.post(f"{QUERY_MANAGER}/QueryData/Aggregate", 
                    data=json.dumps(pipeline, cls=CustomJSONEncoder),
                    headers=headers, 
                    verify=verify_https
                )

                if res.status_code != 200: raise Exception(f"Error getting inputstream data {res.status_code} {res.content}")
                content = res.json(cls=CustomJsonDecoder)
                if not content["success"]: raise Exception(content["errorMessage"])
                logger.info(f"Batch {page}/{total_batchs}")
                downloaded_docs += content["data"]["size"]
                docs += content["data"]["data"]
                page += 1
                
            logger.info(f"Data downloaded, total docs: {total_query}")    
            return docs#content["data"]
        except Exception as e:
            raise e

    def insert(self, ikey:str, data:list[dict], mode:INSERTION_MODE, wait_response:bool) -> tuple[int, str]:
        try:
            headers = {
                "Authorization": f"A2G {self.token}",
                "ikey": ikey
            }

            if mode == INSERTION_MODE.REPLACE: 
                headers["Replace"] = "true"
                headers["Transaction"] = "false"

            elif mode == INSERTION_MODE.INSERT_UNORDERED: 
                headers["Replace"] = "false"
                headers["Transaction"] = "false"

            elif mode == INSERTION_MODE.TRANSACTION:
                headers["Replace"] = "false"
                headers["Transaction"] = "true"

            if wait_response: headers["WaitResponse"] = "true"

            res = requests.post(DATA_URL + "/Data/Insert", headers=headers, json=data, verify=verify_https)
            if res.status_code != 200: raise Exception(f"Error to insert data in inputstream {res.status_code} {res.text}")
            return res.status_code, res.text
        except Exception as e:
            raise e

    async def insert_data_native(self, ikey:str,table: str, data:list[dict], start: int, end:int, wait_response = False, cache:bool=True):
        async with SEM:
            """
            validate data against inputstream JsonSchema and insert into inputstream collection
            params:
                ikey: str
                table_name: str
                data: list[dict]
            """
            timeout = httpx.Timeout(60.0, connect=10.0, read=600.0)
            async with httpx.AsyncClient(http2=True, verify=False, timeout=timeout) as client:
                headers = {
                    "Authorization": f"A2G {self.token}",
                    "ikey": ikey,
                    'Content-Type': 'text/plain',
                }

                if type(data) is not list: raise Exception("Data must be a list of dictionaries")

                """Envia un lote de datos al servidor"""
                my_body = {
                    "list_data": data[start:end],
                    "table_name": table,
                }
                async with client.stream("POST",f"{QUERY_MANAGER}/QueryData/InsertAll",
                    content=json.dumps(my_body, default=str),
                    headers=headers,
                ) as response:
                    if response.status_code != 200:
                        msg = ""
                        async for chunk in response.aiter_bytes():
                            if chunk:
                                msg += chunk.decode("utf-8")
                        raise Exception(f"{response.status_code} {msg}")

    def remove_documents(self, ikey:str, query:dict) -> int:
        try:
            logger.info("Removing data...")
            headers = {
                "Authorization": f"A2G {self.token}",
                "ikey": ikey,
                'Content-Type': 'application/json'
            }

            if len(query) == 0: 
                raise Exception("Query is empty, please provide a valid query, if you desire to delete all documents, use the delete_all method.")

            response = requests.post(f"{QUERY_MANAGER}/QueryData/RemoveDocuments", 
                data=json.dumps(query, cls=CustomJSONEncoder), 
                headers=headers, 
                verify=verify_https
            )
            if response.status_code != 200: 
                raise Exception(f"Error to remove data in inputstream {response.status_code} {response.content}")
            res_object = response.json(cls=CustomJsonDecoder)
            if not res_object["success"]: raise Exception(res_object["errorMessage"])

            content = res_object["data"]
            deleted_docs = content["docs_affected"]
            logger.info(f"Operation complete, total docs deleted: {deleted_docs}")

            return deleted_docs
        except Exception as e:
            raise e

    def clear_inputstream(self, ikey:str) -> int:
        try:
            logger.info("Removing all data...")
            headers = {
                "Authorization": f"A2G {self.token}",
                "ikey": ikey
            }

            response = requests.post(f"{QUERY_MANAGER}/QueryData/Clear", headers=headers, verify=verify_https)
            if response.status_code != 200:
                raise Exception(f"Error to remove all data in inputstream {response.status_code} {response.content}")
            res_object = response.json(cls=CustomJsonDecoder)
            if not res_object["success"]: raise Exception(res_object["errorMessage"])
            
            content = res_object["data"]
            deleted_docs = content["docs_affected"]
            logger.info(f"Operation complete, total docs deleted: {deleted_docs}")
            return deleted_docs
        except Exception as e:
            raise e


class InputstreamClient:

    def __init__(self, token:str, cache_options:dict = None):
        """
        Constructor for LocalInputstream
        :param token: Token to authenticate with ACELER.AI
        :param cache_options: { duration_data: int, duration_inputstream: int } | None
        """        
        self.acelerai_client = AcelerAIHttpClient(token) 
        self.cache_manager = CacheManager(cache_options)
        self.__mode = os.environ.get("EXEC_LOCATION", "LOCAL")

    def __get_inputstream(self, ikey:str) -> Inputstream:
        inputstream = self.acelerai_client.get_inputstream_by_ikey(ikey)
        return inputstream
    
    async def __allPages(self, ikey, query,delete_id):
        headers = {
            "Authorization": f"A2G {self.acelerai_client.token}",
            "ikey": ikey,
            'Content-Type': 'application/json'
        }

        logger.info("Getting Execution Planning...")

        res = requests.post(f"{QUERY_MANAGER}/QueryData/ExecutionPlanningFind", 
            data = json.dumps(query, cls=CustomJSONEncoder), 
            headers=headers, 
            verify=verify_https
        )

        logger.info(f"Getting Status {res.status_code}")

        if res.status_code != 200:
            msg = ''
            async for chunk in res.aiter_bytes():
                if chunk:
                    msg += chunk.decode("utf-8")
            raise Exception(f"{res.status_code} {msg}")

        inputstream = self.acelerai_client.get_inputstream_by_ikey(ikey)
        logger.info(f"Getting inputstream with ikey: {ikey}, Name {inputstream.Name}  from ACELER.AI...")
        
        content = res.json(cls=CustomJsonDecoder)

        total_query     = content["total"]
        page_size:int   = content["size"]

        if total_query == 0:
            logger.info("No data found with the query provided.")
            return []
        
        page: int = 1

        if content['stage'] != None:
            stage = content["stage"].replace('_',' -> ')
            logger.info(f"The query stages are {stage}")
            logger.info(F"The index used in query is {content['indexName']}")
        
        elif inputstream.InputstreamType !=InputstreamType.Native:
            logger.info(f"Complex query the explain was not saved")
        
        tasks = []
        total_pages = (total_query + page_size - 1) // page_size

        if not os.path.exists(f".acelerai_cache/")               : os.mkdir(f".acelerai_cache/")
        if not os.path.exists(f".acelerai_cache/data/")          : os.mkdir(f".acelerai_cache/data/")
        if not os.path.exists(f".acelerai_cache/data/{ikey}/")   : os.mkdir(f".acelerai_cache/data/{ikey}/")

        logger.info('Downloading data, please wait...')
        start_time = datetime.utcnow()
        for page in range(total_pages):
            tasks.append(self.acelerai_client.fetch_page(ikey, query, delete_id, page, page_size))
        await asyncio.gather(*tasks)

        end_time = datetime.utcnow()
        logger.info(f"Total time for downloading {total_pages} pages: {round((end_time - start_time).total_seconds()/60, 2)} minutes")
    
    async def __get_data(self, ikey:str, query, mode:str, cache:bool, delete_id:bool=True) -> list[dict]:
        try:
            logger.info(f"Cache: {cache}")
            logger.info(f"Mode: {self.__mode}")
            query_str = json.dumps(query, cls=CustomJSONEncoder)
            query_hash = hashlib.sha256(query_str.encode()).hexdigest()

            logger.info(f"Getting data sdadsadsadasdsad...")

            data = self.cache_manager.get_data(ikey, query_hash) if cache and self.__mode=='LOCAL' else None
            if data is None:
                if   mode == "find"     :   await self.__allPages(ikey, query,delete_id)
                elif mode == "find_one" :   data = self.acelerai_client.find_one(ikey, query)
                elif mode == "aggregate":   data = self.acelerai_client.aggregate(ikey, query)
                
                self.cache_manager.set_data(ikey, query_hash)

                output_file = f".acelerai_cache/data/{ikey}/{query_hash}.msgpack"
                data = load_full_object(output_file)

            return data
        except Exception as e:
            raise e

    def get_inputstream_schema(self, ikey:str) -> dict:
        """
        return Inputstream schema
        params:
            ikey: str
            cache: bool = True -> if True, use cache if exists and is not expired
        """
        inputstream = self.__get_inputstream(ikey)
        return json.loads(inputstream.Schema)

    async def find(self, ikey:str, query:dict,cache:bool=True,delete_id:bool=True):
        """
        return data from inputstream
        params:
            ikey: str
            query: dict
            cache: bool = True -> if True, use cache if exists and is not expired
        """
        mode = "find"
        return await self.__get_data(ikey, query, mode, cache,delete_id)

    def find_one(self, ikey:str, query:dict, cache:bool=True):
        """
        return one data from inputstream
        params:
            collection: str
            query: dict
        """
        mode = "find_one"
        return self.__get_data(ikey, query, mode, cache)   

    def get_data_aggregate(self, ikey:str, query: list[dict], cache:bool=True):
        """
        return data from inputstream
        params:
            ikey: str
            query: list[dict]
        """
        mode = "aggregate"
        return self.__get_data(ikey, query, mode, cache)  

    async def __validate_data_async(self, d, schema, schema_validator):
        try:
            schema_validator(d)
            return None  # Si no hay errores, retornamos None
        except Exception as e:
            return f"Error validating data: {e}"  # Devolvemos el error

    async def insert_data(self, ikey:str, data:list[dict], table: str=None, mode:INSERTION_MODE = INSERTION_MODE.REPLACE, wait_response = True, batch_size:int=1000, cache:bool=True):
        """
        validate data against inputstream JsonSchema and insert into inputstream collection
        params:
            ikey: str
            data: list[dict]
            table: str -> table is required only when inserting to a local inputstream
            mode: INSERTION_MODE = INSERTION_MODE.REPLACE -> insertion mode
            wait_response: bool = True -> if True, wait for response from server
            batch_size: int = 1000 -> batch size for insert data
            cache: bool = True -> if True, use cache if exists and is not expired
        """
        start = datetime.utcnow()
        inputstream:Inputstream = self.__get_inputstream(ikey)
        end = datetime.utcnow()

        logger.info(f'Demoró {(end - start).total_seconds()} segs en obtener el inputstream')

        if type(data) is not list: raise Exception("Data must be a list of dictionaries")
        data_parsed = json.loads(json.dumps(data, cls=CustomJSONEncoder)) 

        if inputstream.InputstreamType != InputstreamType.Native:
            if inputstream.Status == InputstreamStatus.Undiscovered: #raise Exception("Inputstream undiscovered")
                logger.info("Inputstream undiscovered, you must discovered the schema first")
                return False
            elif inputstream.Status == InputstreamStatus.Exposed: #raise Exception("Inputstream undiscovered")
                start = datetime.utcnow()

                schema = json.loads(inputstream.Schema)
                schema_validator = fastjsonschema.compile(schema)
                #schema_validator = Draft4Validator(schema=schema)
                
                resultados = await asyncio.gather(*(self.__validate_data_async(d, schema, schema_validator) for d in data_parsed))

                # Manejo de errores
                errores = [error for error in resultados if error is not None]
                if errores:
                    for error in errores:
                        logger.error(error)
                    raise Exception("Hubo errores durante la validación de datos.")
                
                end = datetime.utcnow()

                logger.info(f'Demoró {(end - start).total_seconds()} segs en validar los datos')


            for i in range(0, len(data_parsed), batch_size):
                code, message = self.acelerai_client.insert(ikey, data_parsed[i:i+batch_size], mode, wait_response)
                batch_size_aux = batch_size if i+batch_size < len(data_parsed) else len(data_parsed) - i
                logger.info(f"batch {(i//batch_size) + 1}, docs: [{i} - {i+batch_size_aux}] - {code} - {message}")
        else:
            logger.info('Inserting data, please wait...')
            if not table or table=='': raise Exception("Table name is required when inserting to a native inputstream")
            start_time = datetime.utcnow()
            await asyncio.gather(*(self.acelerai_client.insert_data_native(ikey, table, data_parsed, i, min(i + batch_size, len(data_parsed)), wait_response, cache) for i in range(0, len(data_parsed), batch_size)))
            endt = datetime.utcnow()
            logger.info(f'{len(data)} registries inserted successfully in {(endt - start_time).total_seconds() / 60} minutes')

    def remove_documents(self, ikey:str, query:dict) -> int:
        """
        delete data from inputstream
        params:
            ikey: str
            query: dict
        """
        docs = self.acelerai_client.remove_documents(ikey, query)
        return docs
 
    def clear_inputstream(self, ikey:str) -> int:
        """
        delete all data from inputstream
        params:
            ikey: str
        """
        docs = self.acelerai_client.clear_inputstream(ikey)
        return docs
    
