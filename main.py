from settings import settings, refresh_settings
import requests
import json
import time
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


PROXY_TEST_URL = "http://httpbun.com/get"
PROXY_TIMEOUT_SEC = 2.5


def test_proxy(proxy_url, proxy_protocol):
    try:
        r = requests.get(PROXY_TEST_URL, proxies={
                         "http": f"{proxy_protocol}://{proxy_url}"}, timeout=PROXY_TIMEOUT_SEC)
        _ = r.json()
        return r.ok
    except Exception as ex:
        if "sslv3" in str(ex):
            return True

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
