"""
Support for https proxy.
"""

import ssl
from typing import Any

import certifi
from aiogram import __version__ as aiogram_version
from aiogram.client.session.aiohttp import AiohttpSession
from aiohttp import ClientSession
from aiohttp.hdrs import USER_AGENT
from aiohttp.http import SERVER_SOFTWARE
from yarl import URL

_SUPPORTED_SCHEMES = {"http", "https"}


class AiohttpProxySession(AiohttpSession):
    """AiohttpSession that routes requests through an HTTP(S) proxy.

    Proxy credentials may be embedded in the URL
    (``https://user:password@proxy.example.com:8443``): aiohttp takes them from
    the URL and sends them as ``Proxy-Authorization`` to the proxy only.
    """

    def __init__(self, proxy: str, ca_file: str | None = None, **kwargs: Any) -> None:
        # Don't pass ``proxy`` to the parent: it would build an aiohttp_socks
        # connector, which rejects the https:// scheme.
        super().__init__(**kwargs)

        if ca_file:
            # aiohttp uses a single SSL context for both TLS hops: the tunnel to
            # the proxy and the connection to the target. A proxy with a private
            # CA must therefore be trusted by this very context.
            context = ssl.create_default_context(cafile=certifi.where())
            context.load_verify_locations(cafile=ca_file)
            self._connector_init["ssl"] = context

        self.proxy = proxy

    async def create_session(self) -> ClientSession:
        if self._should_reset_connector:
            await self.close()

        if self._session is None or self._session.closed:
            self._session = ClientSession(
                connector=self._connector_type(**self._connector_init),
                headers={USER_AGENT: f"{SERVER_SOFTWARE} aiogram/{aiogram_version}"},
                proxy=self._proxy_url,
            )
            self._should_reset_connector = False

        return self._session

    @property
    def proxy(self) -> str:
        return self._proxy_url

    @proxy.setter
    def proxy(self, proxy: Any) -> None:
        scheme = URL(proxy).scheme
        if scheme not in _SUPPORTED_SCHEMES:
            raise ValueError(f"{type(self).__name__} supports only http(s) proxies, got {scheme!r}")

        # Keep the parent's attribute in sync as well: it is what the parent
        # class uses internally (its getter/setter build a socks connector).
        self._proxy = str(proxy)
        self._proxy_url = str(proxy)
        self._should_reset_connector = True


def create_session(proxy_url: str | None = None, ca_file: str | None = None) -> AiohttpSession | None:
    """Create a session for the given proxy URL (or ``None`` without a proxy)."""
    if not proxy_url:
        return None

    url = URL(proxy_url)
    if url.scheme in _SUPPORTED_SCHEMES:
        return AiohttpProxySession(proxy_url, ca_file=ca_file)

    return AiohttpSession(proxy=str(url))
