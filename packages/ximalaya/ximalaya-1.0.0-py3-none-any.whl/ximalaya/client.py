import json
import logging
import urllib.request
from typing import Generic, Iterator, TypeVar

from jsonpath_ng import parse


class XimalayaClient:
    host: str

    def __init__(self, host: str = 'www.ximalaya.com', headers: dict = None):
        self.host = host

        self.headers = {} if headers is None else headers

        if 'User-Agent' not in self.headers:
            self.headers['User-Agent'] = ''

    def get(self, path: str, method: str = 'GET'):
        url = f'https://{self.host}/{path.lstrip("/")}'

        logging.debug('[XimalayaClient][GET]: %s', url)

        req = urllib.request.Request(url, headers=self.headers, method=method)

        with urllib.request.urlopen(req) as fp:
            return json.loads(fp.read().decode('utf-8'))


T = TypeVar('T')


class ResponsePaginator(Generic[T], Iterator):
    client: XimalayaClient
    url_path: str
    page_name: str
    page_num: int

    def __init__(self, client: XimalayaClient, url_path: str, data_path: str, page_name: str = 'page', page_num: int = 1):
        self.client = client
        self.url_path = url_path
        self.page_name = page_name
        self.page_num = page_num
        self.jsonpath_expression = parse(f'$.{data_path}')

    def __next__(self) -> list[T]:
        json_data = self.client.get(f'{self.url_path}&{self.page_name}={self.page_num}')

        match = self.jsonpath_expression.find(json_data)

        if match is None or len(match[0].value) == 0:
            raise StopIteration()

        self.page_num += 1

        return match[0].value
