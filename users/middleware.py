from django.http import HttpResponse
from ipware import get_client_ip
import requests

security_as_names = [
    "google ",
    'name',
    "microsoft",
    "amazon",
    "apple",
    "yandex",
    "baidu",
    "meta platforms",
    "bytedance",
    "anthropic",
    "openai",
    "ahrefs",
    "semrush",
    "majestic",
    "moz",
    "censys",
    "shodan",
    "rapid7",
    "qualys",
    "internet ",
    "digitalocean",
    "linode",
    "vultr",
    "hetzner",
    "ovh",
    "akamai",
    "imperva",
    "incapsula",
    "fortinet",
    "palo",
    "crowdstrike",
    "zscaler",
    "proofpoint",
    "sophos",
    "mcafee",
    "eset",
    "trend",
    "rapidapi",
    "security",
    "bitsight",
    "binaryedge",
    "onyphe",
    "project",
    "netcraft",
    "internet",
    "shadowserver",
    "spamhaus",
    "abuse",
    "sucuri",
    "uptimerobot"
]


class BlockIp:
    def __init__(self, get_response):
        self.get_response = get_response

    def __user_ip(self, request):
        ip, routable = get_client_ip(request)
        return ip

    def __call__(self, request):
        ip = self.__user_ip(request)
        if ip == '127.0.0.1':
            return self.get_response(request)

        elif ip is None:
            return HttpResponse('page under construction')

        token = "139400fd3c3cf6"
        url = f"https://api.ipinfo.io/lite/{ip}"
        params = {"token": token}
        response = requests.get(url, params=params)
        data = response.json()
        check_asn = data.get("as_name", "").lower().strip()
        is_there = any(
            as_name.strip() in check_asn for as_name in security_as_names)

        if is_there:
            return HttpResponse('page under construction')
        return self.get_response(request)
