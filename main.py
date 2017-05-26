#!/usr/bin/env python3
#
# MIT License
#
# Copyright (c) 2017 Sebastian Bachmann
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import usocket as socket
import time
from ustruct import pack
import ustruct as struct
import os
from itertools import chain
import machine
import sys
import network

class ArtNet(object):
    def __init__(self, dst="255.255.255.255", port=0x1936):

        self.seq = 0
        self.dst = dst
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
        #self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.universe = 3

        #                    Protocol name               DMX         Version   Seq   Phy
        self.hdr = bytearray(b'Art-Net\x00') + bytearray([0, 0x50] + [0, 14])

    def sendrgb(self, r, g, b):
        buf = bytearray([r, g, b, 0, 0] * 12)
        self.sock.sendto(self.hdr + pack(">B", self.seq) + b'\x00' + pack("<H", self.universe) + pack(">H", len(buf)) + buf, (self.dst, self.port))
        self.seq = (self.seq + 1) % 256


    def sendwa(self, w, a):
        buf = bytearray([0, 0, 0, a, w] * 12)
        self.sock.sendto(self.hdr + pack(">B", self.seq) + b'\x00' + pack("<H", self.universe) + pack(">H", len(buf)) + buf, (self.dst, self.port))
        self.seq = (self.seq + 1) % 256




if __name__ == "__main__":
    sta_if = network.WLAN(network.STA_IF) 
    sta_if.active(True)
    sta_if.connect('metalights', 'metalights') 
    sta_if.ifconfig()
    # NOTE: Artnet supports only 512 light values per universe.
    # Therefore we should in practise use two universes and parse the header...
    analog = machine.ADC(0)
    art = ArtNet(dst="10.20.255.255")
    pinval = 0
    while True:
        pinnew = int(analog.read()/4)
        if pinnew >= 256:
            pinnew = 255
        if  pinnew >= pinval + 10 or pinnew <= pinval - 10 :
            pinval = pinnew
            print(pinnew)
            for x in range(0, 100):
                print('.')
                time.sleep(0.01)
                art.sendwa(pinval, pinval)
