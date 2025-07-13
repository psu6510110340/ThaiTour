from pydantic_settings import BaseSettings
from pydantic import Field
import os

class Settings(BaseSettings):
    # App settings
    app_name: str = "ThaiTour API"
    debug: bool = Field(default=False, env="DEBUG")
    
    # Database settings
    database_url: str = Field(default="sqlite:///./thaitour.db", env="DATABASE_URL")
    
    # Security settings
    secret_key: str = Field(default="your-secret-key-change-this-in-production", env="SECRET_KEY")
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    algorithm: str = "HS256"
    
    # API settings
    api_v1_str: str = "/api/v1"
    
    # Thai provinces data
    primary_provinces: list[str] = [
        "กรุงเทพมหานคร", "เชียงใหม่", "ภูเก็ต", "ขอนแก่น", "นครราชสีมา"
    ]
    
    secondary_provinces: list[str] = [
        "กาญจนบุรี", "เชียงราย", "สุราษฎร์ธานี", "อุดรธานี", "นครศรีธรรมราช",
        "อุบลราชธานี", "สงขลา", "ลำปาง", "ระยอง", "จันทบุรี"
    ]
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
