from pydantic import BaseModel


class AppConfig(BaseModel):
    service_name: str = "cloud-investment-strategy-lab"
    environment: str = "local"


settings = AppConfig()
