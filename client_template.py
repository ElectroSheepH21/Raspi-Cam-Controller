import socket
import threading


def connect(ip, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        try:
            client.connect((ip, port))
            print("Connected")
            threading.Thread(target=update_server(client), daemon=True)
        except ConnectionError:
            print("Unable to connect")


def update_server(client):
    while True:
        try:
            data = input("Send: ")
            if data != 'q':
                client.send(bytes(data, "utf-8"))
            else:
                break
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    ip = "192.168.1.134"
    port = 9999

    connect(ip, port)
