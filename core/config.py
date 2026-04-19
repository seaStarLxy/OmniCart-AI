import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # 项目基础信息
    PROJECT_NAME: str = "OmniCart-AI"
    VERSION: str = "0.3.0"
    
    # 服务配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # 模型与 API 配置
    SILICONFLOW_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    API_BASE_URL: str = "https://api.siliconflow.cn/v1"
    
    # 模型名称集中管理
    LLM_MODEL_NAME: str = "Qwen/Qwen2.5-7B-Instruct"
    EMBEDDING_MODEL_NAME: str = "BAAI/bge-m3"
    
    # LLM 温度设置 (可以根据 Agent 覆盖，但这里提供默认基准)
    DEFAULT_TEMPERATURE: float = 0.0
    EMPATHY_TEMPERATURE: float = 0.3
    
    # 路径与日志配置
    LOG_DIR: str = "logs"
    AUDIT_LOG_FILE: str = "logs/audit_logs.json"
    
    # 读取环境变量配置文件
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8", 
        extra="ignore"
    )

# 实例化全局配置对象
settings = Settings()

# 确保日志目录存在
os.makedirs(settings.LOG_DIR, exist_ok=True)