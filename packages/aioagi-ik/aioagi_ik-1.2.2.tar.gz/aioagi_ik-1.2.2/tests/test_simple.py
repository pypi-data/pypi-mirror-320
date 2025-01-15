import sys
import pytest
import pytest_asyncio
from aiohttp.test_utils import unused_port
from aiohttp.web_runner import AppRunner
from os.path import abspath, dirname

# Add the parent directory of 'migrations' to sys.path
sys.path.append(dirname(dirname(abspath(__file__))))

from aioagi.app import AGIApplication
from aioagi.client import AGIClientSession
from aioagi.log import agi_server_logger
from aioagi.parser import AGICode, AGIMessage
from aioagi.runner import get_site
from aioagi.urldispathcer import AGIView


@pytest_asyncio.fixture
async def server_port():
    async def hello(request):
        message = await request.agi.stream_file("hello-world")
        await request.agi.verbose("Hello handler: {}.".format(request.rel_url.query))
        agi_server_logger.debug(message)

    class HelloView(AGIView):
        async def sip(self):
            message = await self.request.agi.stream_file("hello-world")
            await self.request.agi.verbose(
                "HelloView handler: {}.".format(self.request.rel_url.query)
            )
            agi_server_logger.debug(message)

    app = AGIApplication()
    app.router.add_route("SIP", "/hello/", hello)
    app.router.add_route("SIP", "/hello-view/", HelloView)

    port = unused_port()

    runner = AppRunner(app)
    await runner.setup()

    await get_site(runner, host="127.0.0.1", port=port)

    yield port
    await runner.cleanup()


@pytest.mark.asyncio
async def test_server(server_port):
    headers = {
        # 'agi_type': 'SIP',
        # 'agi_network': 'yes',
        # 'agi_network_script': 'agi/',
        # 'agi_request': 'agi://localhost:8080/agi/',
        "agi_channel": "SIP/100-00000001",
        "agi_language": "ru",
        "agi_uniqueid": "1532375920.8",
        "agi_version": "14.0.1",
        "agi_callerid": "100",
        "agi_calleridname": "test",
        "agi_callingpres": "0",
        "agi_callingani2": "0",
        "agi_callington": "0",
        "agi_callingtns": "0",
        "agi_dnid": "101",
        "agi_rdnis": "unknown",
        "agi_context": "from-internal",
        "agi_extension": "101",
        "agi_priority": "1",
        "agi_enhanced": "0.0",
        "agi_accountcode": "",
        "agi_threadid": "139689736754944",
    }
    commands = [
        list(reversed(["STREAM FILE", "VERBOSE"])),
        list(reversed(["STREAM FILE", "VERBOSE"])),
    ]
    async with AGIClientSession(headers=headers) as session:
        messages = []
        async with session.sip(
            "agi://127.0.0.1:{}/hello/?a=test1&b=var1".format(server_port)
        ) as response:
            async for message in response:
                messages.append(message)
                assert message.command == commands[0].pop()
                await response.send(AGIMessage(AGICode.OK, "0", {}))

        assert messages
        assert len(messages) == 2

        async with session.sip(
            "agi://127.0.0.1:{}/hello-view/?a=test2&b=var2".format(server_port)
        ) as response:
            async for message in response:
                messages.append(message)
                assert message.command == commands[1].pop()
                await response.send(AGIMessage(AGICode.OK, "0", {}))

        assert len(messages) == 4
