# -*- coding: utf-8 -*-

""" Parts taken from the proxypy-project: https://code.google.com/p/proxpy/

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
import httplib
import urllib

class ProxyClient(SimpleModule):
    """ Simple Module as wrapper for ppf-interaction
    """
    
    def __init__(self, configuration_parameters):
        # call superclasses constructor
        super(ProxyClient, self).__init__(configuration_parameters)

    def start(self):
        pass

    def stop(self):
        pass

    def http_request_input(self, req, **kwargs):

        try:
            host, port = req.getHost()

            
            # GET-REQUEST
            if req.getMethod() == http.HTTPRequest.METHOD_GET:
                res = self.doGET(host, port, req)
     
                self.send("output_out1", res, **kwargs)


            # POST-REQUEST
            elif req.getMethod() == http.HTTPRequest.METHOD_POST:
                res = self.doPOST(host, port, req)
    
                self.send("output_out1", res, **kwargs)

        except AttributeError:
            pass

    def doGET(self, host, port, req):
        conn = httplib.HTTPConnection(host, port)
        if not self.doRequest(conn, "GET", req.getPath(), '', req.headers): return ''

        res = self._getresponse(conn)
        data = res.serialize()

        return data

    def doPOST(self, host, port, req):
        conn = httplib.HTTPConnection(host, port)
        params = urllib.urlencode(req.getParams(HTTPRequest.METHOD_POST))
        if not self.doRequest(conn, "POST", req.getPath(), params, req.headers): return ''

        res = self._getresponse(conn)
        data = res.serialize()
        
        return data

    def doRequest(self, conn, method, path, params, headers):

        try:
            self._request(conn, method, path, params, headers)
            return True
        except IOError as e:

            return False

    def _getresponse(self, conn):
        try:
            res = conn.getresponse()
        except httplib.HTTPException as e:

            return None

        body = res.read()
        if res.version == 10:
            proto = "HTTP/1.0"
        else:
            proto = "HTTP/1.1"

        code = res.status
        msg = res.reason

        res = http.HTTPResponse(proto, code, msg, res.msg.headers, body)

        return res

    def _request(self, conn, method, path, params, headers):

        conn.putrequest(method, path, skip_host = True, skip_accept_encoding = True)
        for header,v in headers.iteritems():
            # auto-fix content-length
            if header.lower() == 'content-length':
                conn.putheader(header, str(len(params)))
            else:
                for i in v:
                    conn.putheader(header, i)
        conn.endheaders()

        if len(params) > 0:
            conn.send(params)