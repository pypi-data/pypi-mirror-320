import os
from importlib import resources

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def get_default_env_path():
    # Get the package directory
    for file in resources.files("chronulus.etc").iterdir():
        if file.is_file() and file.name == 'default.env':
            return str(file)


class Env(BaseSettings):
    API_URI: str
    CHRONULUS_API_KEY: str | None = Field(default=os.environ.get("CHRONULUS_API_KEY"))

    model_config = SettingsConfigDict(
        env_file=(
            # List them in order of precedence (last one wins)
            get_default_env_path()
        ),
        # Optional: Use case-sensitive names (default is case-insensitive)
        case_sensitive=True,
    )

def get_default_headers(env: Env):
    return {
            'X-API-Key': env.CHRONULUS_API_KEY
        }

class BaseEnv:

    def __init__(self, **kwargs):
        self.env = Env(**kwargs)
        self.headers = get_default_headers(self.env)
