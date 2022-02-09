import socketserver
import socket

from board import SCL, SDA
import busio
from adafruit_motor import servo
from adafruit_pca9685 import PCA9685

servo_controller_connected = False

try:
    i2c = busio.I2C(SCL, SDA)
    pca = PCA9685(i2c)
    pca.frequency = 50

    servoX = servo.Servo(pca.channels[0])
    servoY = servo.Servo(pca.channels[1])
    servoX.angle = 0
    servoY.angle = 0
    servo_controller_connected = True
except Exception:
    print("[ERROR]Please make sure the I2C connection is working correctly")

def get_ip():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        ip = None
        try:
            sock.connect(('10.255.255.255', 1))
            ip = sock.getsockname()[0]
        except Exception:
            ip = '127.0.0.1'
        return ip


def start(port):
    host_ip = get_ip()
    host_addr = (host_ip, port)

    print("TCP server started  on " + str(host_addr) + "...")
    with socketserver.TCPServer(host_addr, RaspiServerReqHandler) as server:
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass


class RaspiServerReqHandler(socketserver.BaseRequestHandler):
    def handle(self):
        addr = self.client_address[0]
        print("[{}]: connected".format(addr))
        while True:
            try:
                s = self.request.recv(1024)
                if s:
                    rec_data = s.decode()
                    print("[{}]: {}".format(addr, rec_data))
                    if servo_controller_connected:
                        x = int(rec_data[rec_data.index('[') + 1:rec_data.index(':')])
                        y = int(rec_data[rec_data.index(':') + 1:rec_data.index(']')])
                        servoX.angle = x
                        servoY.angle = y
                else:
                    raise ConnectionError
            except ConnectionError:
                print("[{}]: closed".format(addr))
                break


if __name__ == "__main__":
    port = 9999
    
    start(port)

