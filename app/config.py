# app/config.py
from pathlib import Path

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="",      
        env_file=".env",    
    )

    model_dir: Path = Field(default=Path("models"))
    model_name: str | None = None

    # параметри Llama
    n_ctx: int = 8192           # стандартно можна підняти
    n_threads: int = 8          # скільки потоків CPU виділити
    n_batch: int = 512          # розмір батчу для генерації

    frontend_path: Path = Path("frontend/index.html")

    @model_validator(mode="before")
    @classmethod
    def pick_first_model(cls, values: dict) -> dict:
        if values.get("model_name"):
            return values

        dir_path = Path(values.get("model_dir", Path("models")))
        candidates = sorted(dir_path.glob("*.gguf"))
        if not candidates:
            raise RuntimeError(f"No .gguf files found in {dir_path!r}")
        values["model_name"] = candidates[0].name
        return values

    @property
    def model_path(self) -> str:
        return str(self.model_dir / self.model_name)

settings = Settings()
