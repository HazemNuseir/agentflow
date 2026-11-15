import os
import secrets
from pydantic import BaseModel, Field

class Settings(BaseModel):
    PROJECT_NAME: str = "DME AgentFlow"
    TAGLINE: str = "Your Business. Your Data. Your AI."
    COMPANY: str = "Digital Mind Engineering (DME), Jordan"
    API_V1_STR: str = "/api/v1"
    
    # Cryptographically generated fallback key if SECRET_KEY env is unset
    SECRET_KEY: str = os.getenv("SECRET_KEY", secrets.token_hex(32))
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", str(60 * 24 * 7)))  # 7 days
    
    # Deployment Profiles: CLOUD_SAAS, CUSTOMER_HOSTED_HYBRID, FULLY_PRIVATE_AIRGAPPED
    DEPLOYMENT_PROFILE: str = os.getenv("DEPLOYMENT_PROFILE", "FULLY_PRIVATE_AIRGAPPED")
    
    # Storage and Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./agentflow.db")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    DATA_DIR: str = os.getenv("DATA_DIR", "./data")
    MODELS_DIR: str = os.getenv("MODELS_DIR", "./models")
    UPLOADS_DIR: str = os.getenv("UPLOADS_DIR", "./data/uploads")
    DOCUMENTS_DIR: str = os.getenv("DOCUMENTS_DIR", "./data/documents")
    
    # Inference parameters
    DEFAULT_MODEL_NAME: str = os.getenv("DEFAULT_MODEL_NAME", "gemma-4-e4b-instruct.Q4_K_M.gguf")
    DEFAULT_CONTEXT_LENGTH: int = int(os.getenv("DEFAULT_CONTEXT_LENGTH", "4096"))
    DEFAULT_CPU_THREADS: int = int(os.getenv("DEFAULT_CPU_THREADS", "4"))
    DEFAULT_GPU_LAYERS: int = int(os.getenv("DEFAULT_GPU_LAYERS", "0"))
    
    # Offline and network controls
    ALLOW_OUTBOUND_NETWORK: bool = os.getenv("ALLOW_OUTBOUND_NETWORK", "false").lower() == "true"
    
    # License & Commercial Edition
    DEFAULT_EDITION: str = os.getenv("DEFAULT_EDITION", "ENTERPRISE_PRIVATE")

settings = Settings()

os.makedirs(settings.DATA_DIR, exist_ok=True)
os.makedirs(settings.MODELS_DIR, exist_ok=True)
os.makedirs(settings.UPLOADS_DIR, exist_ok=True)
os.makedirs(settings.DOCUMENTS_DIR, exist_ok=True)
