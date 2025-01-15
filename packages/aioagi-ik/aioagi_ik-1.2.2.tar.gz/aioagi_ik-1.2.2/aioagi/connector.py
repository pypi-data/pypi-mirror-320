import functools

from aiohttp import TCPConnector

from aioagi.client_proto import AGIResponseHandler


class AGITCPConnector(TCPConnector):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._factory = functools.partial(AGIResponseHandler, loop=self._loop)
