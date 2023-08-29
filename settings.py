from dataclasses import dataclass
import json
import re


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


def refresh_settings():
    with open("./config.json") as f:
        settings.config = Config(**json.load(f))
        with open(settings.config.pac_template_path) as f:
            settings.pac_template = f.read()

        parse_proxies()


def parse_proxies():
    REGEX = r"{(?P<from>.+)->(?P<to>.+)}"
    remove = []
    for protocol, proxies in settings.config.proxies.items():
        for proxy in proxies:
            match = re.search(REGEX, proxy)
            if not match:
                continue

            proxy_ids_from, proxy_ids_to = match.groups()
            for i in range(int(proxy_ids_from), int(proxy_ids_to) + 1):
                settings.config.proxies[protocol].append(
                    proxy.replace(match.group(0), str(i)))

            remove.append((proxies, proxy))

    for list, item in remove:
        list.remove(item)


refresh_settings()
