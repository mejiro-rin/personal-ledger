from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "personal-ledger"
    env: str = "development"

    def set_dev(self):
        self.env = "development"

    def set_prod(self):
        self.env = "production"

    @property
    def dev_env(self) -> bool:
        return self.env == "development"


settings = Settings()