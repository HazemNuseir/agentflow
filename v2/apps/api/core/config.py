import os
import secrets
from pydantic import BaseModel, Field

class Settings(BaseModel):
    PROJECT_NAME: str = "DME AgentFlow V2"
    VERSION: str = "2.0.0"
    TAGLINE: str = "Your Business. Your Data. Your AI. (V2 LAN Edition)"
    COMPANY: str = "Digital Mind Engineering (DME), Jordan"
    API_V1_STR: str = "/api/v1"
    
    # Server network bindings for LAN shared usage
    SERVER_HOST: str = os.getenv("SERVER_HOST", "127.0.0.1")
    SERVER_PORT: int = int(os.getenv("SERVER_PORT", "8080"))  # V2 uses port 8080 (V1 uses 8000)
    
    # Cryptographically generated unique secret for V2 sessions
    SECRET_KEY: str = os.getenv("SECRET_KEY", secrets.token_hex(32))
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", str(60 * 24 * 7)))  # 7 days
    
    # Deployment Profiles: CLOUD_SAAS, CUSTOMER_HOSTED_HYBRID, FULLY_PRIVATE_AIRGAPPED
    DEPLOYMENT_PROFILE: str = os.getenv("DEPLOYMENT_PROFILE", "FULLY_PRIVATE_AIRGAPPED")
    
    # V2 Dedicated Isolated Database & Storage (completely separated from V1)
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./agentflow_v2.db")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/1")  # DB 1 for V2
    DATA_DIR: str = os.getenv("DATA_DIR", "./data_v2")
    MODELS_DIR: str = os.getenv("MODELS_DIR", "./models_v2")
    UPLOADS_DIR: str = os.getenv("UPLOADS_DIR", "./data_v2/uploads")
    DOCUMENTS_DIR: str = os.getenv("DOCUMENTS_DIR", "./data_v2/documents")
    
    # Inference parameters & concurrency controls
    DEFAULT_MODEL_NAME: str = os.getenv("DEFAULT_MODEL_NAME", "gemma-4-e4b-instruct.Q4_K_M.gguf")
    DEFAULT_CONTEXT_LENGTH: int = int(os.getenv("DEFAULT_CONTEXT_LENGTH", "4096"))
    DEFAULT_CPU_THREADS: int = int(os.getenv("DEFAULT_CPU_THREADS", "4"))
    DEFAULT_GPU_LAYERS: int = int(os.getenv("DEFAULT_GPU_LAYERS", "0"))
    MAX_CONCURRENT_INFERENCE: int = int(os.getenv("MAX_CONCURRENT_INFERENCE", "2"))
    INFERENCE_TIMEOUT_SECONDS: int = int(os.getenv("INFERENCE_TIMEOUT_SECONDS", "30"))
    
    # Offline and network controls
    ALLOW_OUTBOUND_NETWORK: bool = os.getenv("ALLOW_OUTBOUND_NETWORK", "false").lower() == "true"
    
    # License & Commercial Edition
    DEFAULT_EDITION: str = os.getenv("DEFAULT_EDITION", "ENTERPRISE_PRIVATE")

settings = Settings()

os.makedirs(settings.DATA_DIR, exist_ok=True)
os.makedirs(settings.MODELS_DIR, exist_ok=True)
os.makedirs(settings.UPLOADS_DIR, exist_ok=True)
os.makedirs(settings.DOCUMENTS_DIR, exist_ok=True)
