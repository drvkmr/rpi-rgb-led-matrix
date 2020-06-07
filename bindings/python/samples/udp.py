#!/usr/bin/env python
from samplebase import SampleBase
from socket import socket
import signal
from Queue import Queue
from UDPHandler import UdpHandler

sockUnity = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

class SimpleSquare(SampleBase):
    def __init__(self, *args, **kwargs):
        super(SimpleSquare, self).__init__(*args, **kwargs)

    def run(self):
        offset_canvas = self.matrix.CreateFrameCanvas()
        while True:
            for x in range(0, self.matrix.width):
                offset_canvas.SetPixel(x, x, 255, 255, 255)
                offset_canvas.SetPixel(offset_canvas.height - 1 - x, x, 255, 0, 255)

            for x in range(0, offset_canvas.width):
                offset_canvas.SetPixel(x, 0, 255, 0, 0)
                offset_canvas.SetPixel(x, offset_canvas.height - 1, 255, 255, 0)

            for y in range(0, offset_canvas.height):
                offset_canvas.SetPixel(0, y, 0, 0, 255)
                offset_canvas.SetPixel(offset_canvas.width - 1, y, 0, 255, 0)
            offset_canvas = self.matrix.SwapOnVSync(offset_canvas)

class Udp_handler(socket):
    def __init__(self, IP="172.16.100.87", port=5006):
        self._sockReceive = socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._UDP_IP = IP
        self._UDP_PORT = port
        self._sockReceive.bind(self._UDP_IP, self._UDP_PORT)
        self._sockSend = socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Ctrl-C callback. Cleans up stuff when the program exits
        signal.signal(signal.SIGINT, self._signal_handler)

        # # initialize queue
        # self._q = Queue()

        # # initialize udp handler
        # self._udp_handler = UdpHandler(self._UDP_PORT, queue=self._q)

        # self._udp_handler.start()
    def getData(self, num_bytes=1024):
        data,addr = self._sockReceive.recvfrom(1024)
        return data

    def _signal_handler(self, signal, frame):
        self._udp_handler.stop_thread()
        self._udp_handler.join()
        self._running = False
    
    def _onReceive(self, data, addr):
        print(data)

# Main function
if __name__ == "__main__":
    udp = Udp_handler()
    print(udp.getData())
