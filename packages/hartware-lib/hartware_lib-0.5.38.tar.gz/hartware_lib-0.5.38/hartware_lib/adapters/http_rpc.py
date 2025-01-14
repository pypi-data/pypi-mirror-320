from __future__ import annotations

import asyncio
import logging
import traceback
from dataclasses import dataclass
from typing import Any, Dict

from aiohttp import ClientSession, ClientTimeout, web

from hartware_lib.serializers.builders import SerializerBuilder
from hartware_lib.serializers.main import Serializer
from hartware_lib.settings import HttpRpcSettings
from hartware_lib.types import AnyDict

probe_logger = logging.getLogger("hartware_lib.http_rpc_probe")
caller_logger = logging.getLogger("hartware_lib.http_rpc_caller")


@dataclass
class HttpRpcProbe:
    app: web.Application
    runner: web.AppRunner
    subject: Any
    settings: HttpRpcSettings
    serializer: Serializer

    @classmethod
    def build(
        cls,
        settings: HttpRpcSettings,
        subject: Any,
        serializer: Serializer | None = None,
    ) -> HttpRpcProbe:
        if serializer is None:
            serializer = Serializer()

        app = web.Application()
        runner = web.AppRunner(app)

        obj = cls(app, runner, subject, settings, serializer)

        app.add_routes([web.post("/", obj.handle)])

        return obj

    async def handle(self, request: web.Request) -> web.Response:
        data = (await request.post())["order"]
        assert isinstance(data, str)

        order = self.serializer.from_json(data)
        assert isinstance(order, dict)

        if "ping" in order:
            probe_logger.info("ping received, pong sent")

            return web.Response(body=self.serializer.to_json({"result": {"pong": True}}))

        func = order.get("func")
        property = order.get("property")
        property_set = order.get("property_set")
        get_properties = order.get("get_properties")
        args = order.get("args") or []
        kwargs = order.get("kwargs") or {}

        if not func and not property and not get_properties:
            return web.Response(
                body=self.serializer.to_json(
                    {"error": "should have func or property specified"}
                ),
            )

        result = None
        try:
            if func:
                probe_logger.info(f"call: {str(func)} = {args=}, {kwargs=}")

                func = getattr(self.subject, func)

                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)
            elif get_properties:
                probe_logger.info("get_properties")

                result = {}
                for attr in dir(self.subject):
                    if attr.startswith("__"):
                        continue

                    obj = getattr(self.subject, attr)
                    result[attr] = not (callable(obj) or asyncio.iscoroutine(obj))
            else:
                assert isinstance(property, str)

                if "property_set" in order:
                    probe_logger.info(f"set_property: {property} to {property_set:r}")

                    setattr(self.subject, property, property_set)
                else:
                    probe_logger.info(f"get_property: {property}")

                    result = getattr(self.subject, property)
        except Exception:
            probe_logger.info("got an exception:", exc_info=True)

            return web.Response(body=self.serializer.to_json({"error": traceback.format_exc()}))

        body = self.serializer.to_json({"result": result})

        probe_logger.info(f"returns {len(body)} bytes ({type(result).__name__})")

        return web.Response(body=body)

    async def run(self) -> None:
        probe_logger.info("start")

        await self.runner.setup()

        site = web.TCPSite(self.runner, self.settings.host, self.settings.port)
        await site.start()

        await asyncio.Future()

    async def cleanup(self) -> None:
        probe_logger.info("cleaning up")

        await self.runner.cleanup()
        await self.app.cleanup()

        probe_logger.info("stopped")


@dataclass
class HttpRpcCaller:
    settings: HttpRpcSettings
    serializer: Serializer

    @classmethod
    def build(
        cls,
        settings: HttpRpcSettings,
        serializer: Serializer | None = None,
    ) -> HttpRpcCaller:
        if serializer is None:
            serializer = SerializerBuilder().get()

        return cls(settings, serializer)

    async def _process(self, data: AnyDict, timeout: float = 300.0) -> Any:
        async with ClientSession(
            timeout=ClientTimeout(timeout), raise_for_status=True
        ) as session:
            response = await session.post(
                f"http://{self.settings.host}:{self.settings.port}/",
                data={"order": self.serializer.to_json(data)},
                raise_for_status=True,
            )

            text = await response.text()

        data = self.serializer.from_json(text)
        error = data.get("error")

        caller_logger.info(f"received {len(text)} bytes ({type(data).__name__})")

        if error:
            raise Exception(f"{error}")

        return data.get("result")

    async def ping(self, timeout: float = 5.0) -> bool:
        caller_logger.info("ping")

        try:
            result = await self._process({"ping": True}, timeout=timeout)

            if result.get("pong") is True:
                caller_logger.info("pong received")

                return True
        except asyncio.exceptions.TimeoutError:
            caller_logger.info("No pong received")
        except Exception as exc:
            caller_logger.warning(f"No pong received: {exc}", exc_info=True)

        return False

    async def get_properties(self, timeout: float = 5.0) -> Any:
        caller_logger.info("get_properties")

        return await self._process({"get_properties": True}, timeout=timeout)

    async def get_property(self, name: str, timeout: float = 10.0) -> Any:
        caller_logger.info(f"get_property: {name}")

        return await self._process({"property": name}, timeout=timeout)

    async def set_property(self, name: str, value: Any, timeout: float = 10.0) -> None:
        caller_logger.info(f"set_property: {name} to {value:r}")

        await self._process({"property": name, "property_set": value}, timeout=timeout)

    async def call(
        self, func: str, *args: Any, timeout: float = 300.0, **kwargs: Any
    ) -> Any:
        caller_logger.info(f"call: {str(func)} = *{args}, **{kwargs}")

        return await self._process(
            {"func": func, "args": args, "kwargs": kwargs}, timeout=timeout
        )


class HttpRpcObject:
    caller: HttpRpcCaller
    connected: bool
    properties: Dict[str, bool]

    def __init__(self, caller: HttpRpcCaller):
        object.__setattr__(self, "caller", caller)
        object.__setattr__(self, "connected", False)
        object.__setattr__(self, "properties", {})

    def connect(self) -> None:
        properties = asyncio.run(self.caller.get_properties())

        object.__setattr__(self, "connected", True)
        object.__setattr__(self, "properties", properties)

    def __setattr__(self, attr: str, value: Any) -> None:
        asyncio.run(self.caller.set_property(attr, value))

    def __getattr__(self, attr: str) -> Any:
        if not self.connected:
            self.connect()

        if self.properties.get(attr) is False:
            def run(*args: Any, **kwargs: Any) -> Any:
                return asyncio.run(self.caller.call(attr, *args, **kwargs))

            return run
        else:
            return asyncio.run(self.caller.get_property(attr))
