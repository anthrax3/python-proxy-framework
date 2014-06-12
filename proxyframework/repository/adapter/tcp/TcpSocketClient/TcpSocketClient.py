from proxyframework.core import SimpleModule
import threading
import socket
import binascii

class TcpSocketClient(SimpleModule):
    """ Simple Module
    """
    
    def __init__(self, configuration_parameters):
        # call superclasses constructor
        super(TcpSocketClient, self).__init__(configuration_parameters)

        # Create a TCP/IP socket
        self.sock = None

    def connect_socket(self):

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        print "host: %s" %(self.config["host"])
        print "port: %s" %(str(self.config["port"]))
        
        # Connect the socket to the port where the server is listening
        server_address = (self.config["host"], int(self.config["port"]))
        self.sock.connect(server_address)

        self.readerThread = TcpSocketReaderThread(self.sock, self.tcp_payload_output)
        self.readerThread.start()

        print "connected (method: connect_socket)"

    def start(self):
        # start socket reader thread
        pass

    def stop(self):
        pass

    def tcp_payload_input(self, pbuf, **kwargs):
        """ TCP payload as input from another module
        """

        print "[+] python-socket: tcp_payload_input called"

        if pbuf == None and kwargs["new_initialized"] == True:
            print "[+] TCP_SOCKET: Got signal to establish a TCP connection"
            self.connect_socket()
          
        else:
            print "[+] TCP_SOCKET: forward payload (pbuf=%s, hexpbuf=%s, len=%d)" %(pbuf, binascii.hexlify(pbuf), len(pbuf))
            self.sock.send(pbuf)


    def tcp_payload_output(self, pbuf, **kwargs):
        """ TCP payload coming from TcpSocketReader Thread,
        which should be dispatched over the SAPF.
        """

        print "[+] TCP_SOCKET: payload received (pbuf=%s, hexpbuf=%s, len=%d)" %(pbuf, binascii.hexlify(pbuf), len(pbuf))
        self.send("output_out1", pbuf)
    
        

class TcpSocketReaderThread(threading.Thread):
    """ Thread for reading data from the socket
    """

    def __init__(self, socket, input_handler): 
        threading.Thread.__init__(self)

        # unix domain socket
        self.socket = socket

        # input handler (simple module)
        self.input_handler = input_handler

        print "[+] ReaderThread started"
        
    def run(self):
         
        while True:
            data = self.socket.recv(4096)
            if data:
                self.input_handler(data)

