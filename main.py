from settings import settings, refresh_settings
from multiprocessing.pool import ThreadPool
import requests
import json
import time
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


PROXY_TEST_URL = "https://httpbun.com/get"
PROXY_TIMEOUT_SEC = 2.5
THREAD_POOL_SIZE = 20


def test_proxy(proxy_url, proxy_protocol):
    try:
        r = requests.get(PROXY_TEST_URL, proxies={
                         "https": f"{proxy_protocol}://{proxy_url}"}, timeout=PROXY_TIMEOUT_SEC)
        _ = r.json()
        return r.ok
    except Exception as ex:
        if "sslv3" in str(ex):
            return True

        return False


def test_proxy_thread(data):
    proxy_protocol, proxy_url = data
    return test_proxy(proxy_url, proxy_protocol), proxy_url


def start():
    while True:
        print("Started testing...")
        refresh_settings()

        p = ThreadPool(THREAD_POOL_SIZE)
        thread_data = []
        for proxy_protocol in settings.config.proxies:
            for proxy in settings.config.proxies[proxy_protocol]:
                thread_data.append((proxy_protocol, proxy))

        working_proxies = p.map(test_proxy_thread, thread_data)
        working_proxies = [proxy for is_ok, proxy in working_proxies if is_ok]

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
