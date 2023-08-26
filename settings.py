from dataclasses import dataclass
import json


@dataclass(kw_only=True)
class Config:
    pac_template_path: str
    pac_output_path: str
    pac_proxy_placeholder: str
    refresh_frequency_in_secs: int
    proxies: dict[str, list[str]]


class Settings:
    config: Config
    pac_template: str

settings = Settings()


with open("./config.json") as f:    
    settings.config = Config(**json.load(f))
    with open(settings.config.pac_template_path) as f:
        settings.pac_template = f.read()