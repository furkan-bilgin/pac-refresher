import requests
import json
import time
from settings import settings, refresh_settings

PROXY_TEST_URL = "https://httpbin.org/status/200"
PROXY_TIMEOUT_MS = 3000


def test_proxy(proxy_url, proxy_protocol):
    try:
        r = requests.get(PROXY_TEST_URL, proxies={
                         proxy_protocol: f"{proxy_protocol}://{proxy_url}"}, timeout=PROXY_TIMEOUT_MS)
        return r.ok
    except Exception as ex:
        print(ex)
        return False


def start():
    while True:
        refresh_settings()

        working_proxies = []
        failed_proxies = []
        for proxy_protocol in settings.config.proxies:
            for proxy in settings.config.proxies[proxy_protocol]:
                if test_proxy(proxy, proxy_protocol):
                    working_proxies.append(proxy)
                else:
                    failed_proxies.append(proxy)
                print(
                    f"Testing proxies (working count: {len(working_proxies)}, failed count: {len(failed_proxies)})")

        proxies_json = json.dumps(working_proxies)
        pac_output_text = settings.pac_template.replace(
            settings.config.pac_proxy_placeholder, proxies_json)

        with open(settings.config.pac_output_path, "w") as f:
            f.write(pac_output_text)

        print(
            f"PAC has been refreshed with {len(working_proxies)} working proxies!")
        time.sleep(settings.config.refresh_frequency_in_secs)


if __name__ == "__main__":
    start()
