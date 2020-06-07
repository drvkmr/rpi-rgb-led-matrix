#!/usr/bin/python

import sys
import signal
import socket
import time
import threading
from Queue import Queue
import traceback
import logging

# Version:      0.2
# Last changed: 01/01/18

# TODO:
#   -
#   -


# ===========================================================================//
# ----------------------------------------------------------------// UdpHandler

class UdpHandler(threading.Thread):

    def __init__(self, port, queue = None, buffer_size = 1024):
        threading.Thread.__init__(self)
        self.running = False
        self.queue = queue
        self.callback = None
        self.port = port
        self.buffer_size = buffer_size
        self.exit_msg = "owqlc5n465vvvk34op2j3iugbx8kjhk3"
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    def set_queue(self, queue):
        self.queue = queue

    def set_callback(self, callback, *args):
        self.callback = callback
        self.callback_args = args

    def stop_thread(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.sendto(str.encode(self.exit_msg), ("127.0.0.1", self.port))
        s.close()
        self.sock.close()
        time.sleep(1)
        print("UDP thread closed.")

    def send_message(self, ip_addr, port, msg):
        self.sock.sendto(msg, (ip_addr, port))

    def run(self):
        self.running = True
        self.sock.bind(("0.0.0.0", self.port))
        while (self.running):
            try:
                data, addr = self.sock.recvfrom(self.buffer_size)
                if (data == str.encode(self.exit_msg)):
                    print("Exit msg received")
                    self.running = False
                else:
                    if (self.queue is not None):
                        self.queue.put((data, addr))
                    if (self.callback is not None):
                        self.callback(data, addr, *self.callback_args)
            except Exception as e:
                print("Something went wrong with the socket")
                logging.error(traceback.format_exc())
                break


# ===========================================================================//
# ----------------------------------------------------// Test and usage example

# -----------------------------------------/
# ---/ Callback w/ arguments

def callback_01(data, addr, arg1, arg2):
    print("<Callback_01> Msg from %s: %s" % (addr, data))


# -----------------------------------------/
# ---/ Callback w/o arguments

def callback_02(data, addr):
    print("<Callback_02> Msg from %s: %s" % (addr, data))


# -----------------------------------------/
# ---/ Signal handler to catch Ctrl+C

def signal_handler(signal, frame):
    global running, udp_handler
    udp_handler.stop_thread()
    udp_handler.join()
    running = False


# -----------------------------------------/
# ---/ Main program logic

if __name__ == '__main__':

    # add signal handler for SIGINT
    signal.signal(signal.SIGINT, signal_handler)

    # init stuff
    q = Queue()
    udp_handler = UdpHandler(8086, queue = q)
    udp_handler.set_callback(callback_01, "foo", "bar")
    # udp_handler.set_callback(callback_02)
    udp_handler.start()

    # main program loop
    running = True
    while (running):
        if (not q.empty()):
            data, addr = q.get()
            print("<Main> Msg from %s: %s" % (addr, data))
        time.sleep(0.1)

    # cleanup
    print('Closing program!')
    sys.exit(0)
