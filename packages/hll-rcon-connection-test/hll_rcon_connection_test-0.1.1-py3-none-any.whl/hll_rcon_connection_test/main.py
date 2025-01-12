import sys
import socket
import sys
from itertools import cycle


def xor_encode(
    message: str | bytes | bytearray, xor_key: bytes, encoding: str = "utf-8"
) -> bytes:
    """XOR encrypt the given message with the given XOR key"""
    if isinstance(message, str):
        message = message.encode(encoding=encoding)

    return bytes(
        [
            message_char ^ xor_char
            for message_char, xor_char in zip(message, cycle(xor_key))
        ]
    )


def xor_decode(cipher_text: str | bytes | bytearray, xor_key: bytes) -> str:
    """XOR decrypt the given cipher text with the given XOR key"""
    return xor_encode(cipher_text, xor_key).decode("utf-8")


def main():
    try:
        addr = sys.argv[1]
        password = sys.argv[2]
        ip, port = addr.split(":")
        port = int(port)
    except Exception:
        print(
            f"You must provide the IP, RCON port and RCON password in the format: IP:port password"
        )
        sys.exit(1)

    try:
        sock = socket.socket(socket.AF_INET)
        sock.connect((ip, port))
        xor_key = sock.recv(1024)

        sock.send(xor_encode(f"login {password}", xor_key))
        resp = xor_decode(sock.recv(1024), xor_key)
        if resp != "SUCCESS":
            print(
                f"Unable to login, double check your IP, RCON port and RCON password, you may need to restart the game server if you have changed the RCON password."
            )
        else:
            print("Connection/login successful")
        sock.send(xor_encode("get name", xor_key))
        raw_server_name = sock.recv(1024)
        server_name = xor_decode(raw_server_name, xor_key)
        print(f"Server name: {server_name}")

    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()
