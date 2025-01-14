from typing import Any, Dict, Optional, Union
from pydantic import BaseModel
from enum import Enum
import json
from datetime import datetime
import os
from azure.storage.blob import BlobServiceClient

# A bespoke logger that will be used to stream events to a destination
class JSONSerializer:
    @staticmethod
    def serialize(obj):
        if hasattr(obj, 'isoformat'):  # datetime objects
            return obj.isoformat()
        elif hasattr(obj, 'to_dict'):  # custom objects with to_dict method
            return JSONSerializer.serialize(obj.to_dict())
        elif isinstance(obj, dict):
            return {k: JSONSerializer.serialize(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [JSONSerializer.serialize(item) for item in obj]
        return obj

class LoggerDestination(str, Enum):
    NO_OP = "no_op"
    CONSOLE = "console"
    FILE = "file"
    EVALUATION = "evaluation"
    AZURE_BLOB = "azure_blob"

class BaseLoggerConfig(BaseModel):
    pass

class FileDestinationConfig(BaseLoggerConfig):
    root_dir: str
    filename: Optional[str] = None # If None, will use the current timestamp

class AzureBlobDestinationConfig(BaseLoggerConfig):
    container_name: str
    base_path: str
    connection_string: str

class WildcardLogger(BaseModel):
    destination: LoggerDestination
    config: BaseLoggerConfig
    
    def log(self, event: str, data: Union[Dict[str, Any], str]):
        raise NotImplementedError("Subclass must implement log method")
    
class NoOpLogger(WildcardLogger):
    def __init__(self):
        super().__init__(destination=LoggerDestination.NO_OP, config=BaseLoggerConfig())
    
    def log(self, event: str, data: Dict[str, Any]):
        pass
    
class ConsoleLogger(WildcardLogger):
    def log(self, event: str, data: Dict[str, Any]):
        serialized_data = JSONSerializer.serialize(data)
        print(json.dumps({"event": event, "data": serialized_data}))
        
class FileLogger(WildcardLogger):
    def log(self, event: str, data: Dict[str, Any]):
        filename = self.config.filename or datetime.now().strftime("%Y-%m-%d_%H-%M-%S.jsonl")
        serialized_data = JSONSerializer.serialize(data)
        with open(os.path.join(self.config.root_dir, filename), "w") as f:
            f.write(json.dumps({"event": event, "data": serialized_data}) + "\n")
            
class EvaluationLogger(WildcardLogger):
    def log_to_file(self, filepath: str, data: Dict[str, Any]):
        serialized_data = JSONSerializer.serialize(data)
        with open(filepath, "w") as f:
            f.write(json.dumps(serialized_data))
            
    def log_to_console(self, data: Dict[str, Any]):
        serialized_data = JSONSerializer.serialize(data)
        print(json.dumps(serialized_data))
    
    def log(self, event: str, data: Dict[str, Any]):
        filepath = os.path.join(self.config.root_dir, f"{event}.json")
        os.makedirs(self.config.root_dir, exist_ok=True)
        self.log_to_file(filepath, data)

class AzureBlobLogger(WildcardLogger):
    blob_service: Any = None
    container_client: Any = None  # Using Any since container client type isn't easily importable
    
    def __init__(self, destination: LoggerDestination, config: AzureBlobDestinationConfig):
        super().__init__(destination=destination, config=config)
        self.blob_service = BlobServiceClient.from_connection_string(self.config.connection_string)
        self.container_client = self.blob_service.get_container_client(self.config.container_name)
        if not self.container_client.exists():
            self.container_client.create_container()

    def log(self, event: str, data: Dict[str, Any], override_path: Optional[str] = None):
        serialized_data = JSONSerializer.serialize(data)
        json_data = json.dumps({"event": event, "data": serialized_data})
        
        # Use override_path if provided, otherwise construct path from base_path and event
        blob_path = override_path if override_path else f"{self.config.base_path}/{event}.json"
        
        blob_client = self.container_client.get_blob_client(blob_path)
        blob_client.upload_blob(json_data, overwrite=True)

LoggerType = Union[ConsoleLogger, FileLogger, EvaluationLogger, AzureBlobLogger]

class LoggerFactory(BaseModel):
    @staticmethod
    def create_logger(destination: LoggerDestination, **config) -> LoggerType:
        if destination == LoggerDestination.CONSOLE:
            return WildcardLogger(destination=destination, config=BaseModel())
        elif destination == LoggerDestination.FILE:
            if "root_dir" not in config:
                raise ValueError("root_dir is required for FILE destination")
            config_model = FileDestinationConfig(**config)
            return FileLogger(destination=destination, config=config_model)
        elif destination == LoggerDestination.EVALUATION:
            config_model = FileDestinationConfig(**config)
            return EvaluationLogger(destination=destination, config=config_model)
        elif destination == LoggerDestination.AZURE_BLOB:
            if any(key not in config for key in ["container_name", "base_path", "connection_string"]):
                raise ValueError("container_name, base_path, and connection_string are required for AZURE_BLOB destination")
            config_model = AzureBlobDestinationConfig(**config)
            return AzureBlobLogger(destination=destination, config=config_model)
        else:
            raise ValueError(f"Unknown destination: {destination}")
