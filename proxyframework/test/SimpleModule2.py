# -*- coding: utf-8 -*-

from proxyframework.core import SimpleModule

class SimpleModule2(SimpleModule):
    
    def input_handler_1(self, pbuf, **kwargs):    
        print "[+] Input-method of SimpleModule2"
        self.send("output_out1", pbuf)
        
        print "[+] SimpleModule2: Received Parameters:"
        print self.config

