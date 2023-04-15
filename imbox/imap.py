from imaplib import IMAP4, IMAP4_SSL

import socks
import socket

import logging
import ssl as pythonssllib

logger = logging.getLogger(__name__)


class ImapTransport:

    PROXY_TYPES = {"socks4": socks.PROXY_TYPE_SOCKS4,
                   "socks5": socks.PROXY_TYPE_SOCKS5,
                   "http": socks.PROXY_TYPE_HTTP}

    def __init__(self, hostname, port=None, ssl=True, ssl_context=None, starttls=False,
                proxy_type=False, proxy_host=None, proxy_port=None, rdns=True, proxy_username=None, proxy_password=None):
        self.hostname = hostname
        proxy_type = ImapTransport.PROXY_TYPES[proxy_type.lower()]

        if proxy_type:
            self.temp = socket.socket
            socks.set_default_proxy(proxy_type=proxy_type, addr=proxy_host, port=proxy_port, rdns=rdns, username=proxy_username, password=proxy_password)
            socket.socket = socks.socksocket
        if ssl:
            self.port = port or 993
            if ssl_context is None:
                ssl_context = pythonssllib.create_default_context()
            self.server = IMAP4_SSL(self.hostname, self.port, ssl_context=ssl_context)
        else:
            self.port = port or 143
            self.server = IMAP4(self.hostname, self.port)

        if starttls:
            self.server.starttls()
        logger.debug("Created IMAP4 transport for {host}:{port}"
                     .format(host=self.hostname, port=self.port))
        
    def __del__(self):
        socket.socket = self.temp

    def list_folders(self):
        logger.debug("List all folders in mailbox")
        return self.server.list()

    def connect(self, username, password):
        self.server.login(username, password)
        self.server.select()
        logger.debug("Logged into server {} and selected mailbox 'INBOX'"
                     .format(self.hostname))
        return self.server
