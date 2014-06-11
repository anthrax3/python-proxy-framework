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

import proxyframework.datatypes.http as http
from proxyframework.core import SimpleModule

class UserAgentChanger(SimpleModule):
    """ Change user-agent in a given HTTP-request
    """

    def __init__(self, configuration_parameters):
        super(UserAgentChanger, self).__init__(configuration_parameters)
        self.config = configuration_parameters
        
    def module_input(self, request, **kwargs):
        try:
            if request.getHeader("User-Agent") != None:
                request.setHeader("User-Agent", self.config["user-agent"])

        except AttributeError:
            pass
            
        self.send("output_out1", request, **kwargs)