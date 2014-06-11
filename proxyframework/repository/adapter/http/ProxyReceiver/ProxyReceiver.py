# -*- coding: utf-8 -*-

"""  Parts taken from the proxypy-project: https://code.google.com/p/proxpy/

Copyright notice for proxpy:
================
  
Copyright (C) 2011
    Roberto Paleari     <roberto.paleari@gmail.com>
    Alessandro Reina    <alessandro.reina@gmail.com>
  
This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.
  
HyperDbg is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
  
You should have received a copy of the GNU General Public License along with
this program. If not, see <http://www.gnu.org/licenses/>.
  
"""


from proxyframework.core import SimpleModule
import proxyframework.datatypes.http as http
import socket
import asyncore
import SocketServer

class ProxyReceiver(SimpleModule):
    
    def __init__(self, configuration_parameters):
        super(ProxyReceiver, self).__init__(configuration_parameters)
        
    def start(self):

        HOST, PORT = "localhost", 8080

        # dict for storing references to internal tcp-handlers
        self.tcp_handlers = {}
        
        global sim_module
        sim_module = self
        
        self.server = SocketServer.TCPServer((HOST, PORT), MyTCPHandler)
        self.server.serve_forever()

    def response_in(self, pbuf, **kwargs):
        """ Delegates incomming response data to the corresponding TCP-handler
        """
        self.tcp_handlers[kwargs["host_port"][0]][kwargs["host_port"][1]].sendResponse(pbuf)

    def handle_request(self, request, handler_instance, id_tuple):

        self.send("output_out1", request, host_port = id_tuple)
        
    def stop(self):
        self.server.shutdown()


    def register_tcp_handler(self, tcp_handler_instance, id_tuple):
        """ Registers a simple-module's internal reference for an instantiated
        tcp-handler
        """

        if self.tcp_handlers.has_key(id_tuple[0]):
            self.tcp_handlers[id_tuple[0]][id_tuple[1]] = tcp_handler_instance

        else:
            self.tcp_handlers[id_tuple[0]] = {}
            self.tcp_handlers[id_tuple[0]][id_tuple[1]] = tcp_handler_instance


class MyTCPHandler(SocketServer.StreamRequestHandler):

    def __init__(self, request, client_address, server):
        global sim_module

        sim_module.register_tcp_handler(self, client_address)

        # store identification tuple
        self.client_address = client_address

        # TODO - seems to be a python-related bug
        # http://bugs.python.org/issue14574
        try:
            SocketServer.StreamRequestHandler.__init__(self, request, client_address, server)
        except socket.error, e:
            pass
        except IOError, e:
            if e.errno == errno.EPIPE:
                pass
            else:
                pass
        
    def handle(self):
        global sim_module

        req = http.HTTPRequest.build(self.rfile)
        sim_module.handle_request(req, self, self.client_address)
        
    def sendResponse(self, res):
        self.wfile.write(res)

