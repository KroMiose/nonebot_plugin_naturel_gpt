import argparse
import getpass
import os
import socket
import ssl
import select
import struct
import time
import platform

if platform.system() != "Windows":
    import signal


class MCRconException(Exception):
    pass


def timeout_handler(signum, frame):
    raise MCRconException("Connection timeout error")


class MCRcon(object):
    """A client for handling Remote Commands (RCON) to a Minecraft server

    The recommend way to run this client is using the python 'with' statement.
    This ensures that the socket is correctly closed when you are done with it
    rather than being left open.

    Example:
    In [1]: from mcrcon import MCRcon
    In [2]: with MCRcon("10.1.1.1", "sekret") as mcr:
       ...:     resp = mcr.command("/whitelist add bob")
       ...:     print(resp)

    While you can use it without the 'with' statement, you have to connect
    manually, and ideally disconnect:
    In [3]: mcr = MCRcon("10.1.1.1", "sekret")
    In [4]: mcr.connect()
    In [5]: resp = mcr.command("/whitelist add bob")
    In [6]: print(resp)
    In [7]: mcr.disconnect()
    """

    socket = None

    def __init__(self, host, password, port=25575, tlsmode=0, timeout=5):
        self.host = host
        self.password = password
        self.port = port
        self.tlsmode = tlsmode
        self.timeout = timeout
        if platform.system() != "Windows":
            signal.signal(signal.SIGALRM, timeout_handler)

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, type, value, tb):
        self.disconnect()

    def connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Enable TLS
        if self.tlsmode > 0:
            ctx = ssl.create_default_context()

            # Disable hostname and certificate verification
            if self.tlsmode > 1:
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE

            self.socket = ctx.wrap_socket(self.socket, server_hostname=self.host)

        self.socket.connect((self.host, self.port))
        self._send(3, self.password)

    def disconnect(self):
        if self.socket is not None:
            self.socket.close()
            self.socket = None

    def _read(self, length):
        if platform.system() != "Windows":
            signal.alarm(self.timeout)
        data = b""
        while len(data) < length:
            data += self.socket.recv(length - len(data))
        if platform.system() != "Windows":
            signal.alarm(0)
        return data

    def _send(self, out_type, out_data):
        if self.socket is None:
            raise MCRconException("Must connect before sending data")

        # Send a request packet
        out_payload = (
            struct.pack("<ii", 0, out_type) + out_data.encode("utf8") + b"\x00\x00"
        )
        out_length = struct.pack("<i", len(out_payload))
        self.socket.send(out_length + out_payload)

        # Read response packets
        in_data = ""
        while True:
            # Read a packet
            (in_length,) = struct.unpack("<i", self._read(4))
            in_payload = self._read(in_length)
            in_id, in_type = struct.unpack("<ii", in_payload[:8])
            in_data_partial, in_padding = in_payload[8:-2], in_payload[-2:]

            # Sanity checks
            if in_padding != b"\x00\x00":
                raise MCRconException("Incorrect padding")
            if in_id == -1:
                raise MCRconException("Login failed")

            # Record the response
            in_data += in_data_partial.decode("utf8")

            # If there's nothing more to receive, return the response
            if len(select.select([self.socket], [], [], 0)[0]) == 0:
                return in_data

    def command(self, command):
        result = self._send(2, command)
        time.sleep(0.003)  # MC-72390 workaround
        return result


def mcrcon_cli():
    try:
        parser = argparse.ArgumentParser(
            description="connect to and use Minecraft Server remote console protocol"
        )
        parser.add_argument("host", metavar="HOST", help="the host to connect to")
        parser.add_argument(
            "--password",
            metavar="PASSWORD",
            help="the password to connect with, default is a prompt or envvar RCON_PASSWORD.",
        )
        parser.add_argument(
            "-p",
            "--port",
            metavar="PORT",
            dest="port",
            type=int,
            default=25575,
            help="the port to connect to",
        )
        parser.add_argument(
            "-t",
            "--tls",
            dest="tlsmode",
            action="store_true",
            help="connect to the server with tls encryption",
        )
        args = parser.parse_args()

        if not args.password and not os.environ.get("RCON_PASSWORD"):
            password = getpass.getpass("Password: ")
        elif os.environ.get("RCON_PASSWORD"):
            password = os.environ.get("RCON_PASSWORD")
        else:
            password = args.password

        try:
            with MCRcon(args.host, password, args.port, args.tlsmode) as mcr:
                while True:
                    cmd = input("> ")
                    if cmd.strip() == "exit":
                        break
                    else:
                        try:
                            resp = mcr.command(cmd)
                            print(resp)
                        except (ConnectionResetError, ConnectionAbortedError):
                            print(
                                "The connection was terminated, the server may have been stopped."
                            )
                            break
                        if cmd == "stop":
                            break
        except ConnectionRefusedError:
            print("The connection could not be made as the server actively refused it.")
        except ConnectionError as e:
            print(e)
    except KeyboardInterrupt:
        pass
