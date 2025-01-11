import socket
import select

from serial_com.serial_com import Port
from logger.logger import serial_logger as logger


class  SocketClosedError(Exception):
    ...


class IPPort(Port, socket.socket):

    chunk_size = 1024

    def __init__(self, *args, addr_port: tuple[str, int] = None,
                 read_timeout: float = 0.5, **kwargs):
        """To intialize the object call IPPort()"""
        super(IPPort, self).__init__(socket.AF_INET, socket.SOCK_STREAM, *args, **kwargs)
        self.addr_port = addr_port
        self.read_timeout = read_timeout

    @property
    def name(self):
        return str(self.addr_port)

    def apply_settings(self, data: dict):
        self.read_timeout = data["timeout"]

    def read(self, size=chunk_size, *args, **kwargs) -> bytes:
        try:
            ans = super().recv(size)
        except TimeoutError:
            logger.debug(f"{self} no answer")
            ans = b""
        except OSError as e:
            if e.errno in (10038, 10054):  # socket was closed
                raise SocketClosedError("Socket was closed. A new one must be created")
        return ans

    def write(self, bl: bytes, *args, **kwargs) -> int:
        try:
            return super().send(bl)
        except OSError as e:
            if e.errno in (10038, 10054):  # socket was closed
                raise SocketClosedError("Socket was closed. A new one must be created")

    def read_until(self):
        buffer = []
        is_carriage = False
        while True:
            chunk = self.read(1)
            if not chunk:
                break
            if is_carriage:
                if chunk == b"\n":
                    buffer.append(chunk)
                    break
                else:
                    is_carriage = False
            else:
                if chunk == b"\r":
                    is_carriage = True
            buffer.append(chunk)
        return b"".join(buffer)

    @property
    def in_waiting(self) -> int:
        sockets = select.select([self], [], [], 0.1)
        if sockets[0]:
            return self.chunk_size
        return 0

    @property
    def out_waiting(self) -> int:
        return 0

    def reset_input_buffer(self) -> None:
        if self.in_waiting:
            self.read()

    def reset_output_buffer(self) -> None:
        ...

    def open(self):
        if self.fileno() == -1:
            raise SocketClosedError
        try:
            self.connect(self.addr_port)
        except OSError as e:
            if e.errno == 10056:
                # normal state: if the socket is opened it throws 10056
                pass
            else:
                logger.debug(f"On trying to connect to {self} e")
                raise e

    def close(self):
        self.close()

    def is_open(self):
        """As the socket can't be checked properly if it's connected
        return False, assuming that .open method can be called easily"""
        try:
            sent = super().send(b"A")
        except OSError as e:
            if e.errno in (10038, 10054):  # socket was closed
                return False
            raise e
        if sent:
            return True
        return False



    def is_closed(self):
        ...

    def __call__(self):
        return IPPort(addr_port=self.addr_port, read_timeout=self.read_timeout)




