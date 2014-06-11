# -*- coding: utf-8 -*-

from proxyframework.core import SimpleModule

class SimpleModule3(SimpleModule):
    
    def input_handler_1(self, pbuf, **kwargs):
        print "[+] Input-method of SimpleModule3"
        self.send("output_out1", pbuf)
        
        print "[+] SimpleModule3: Received Parameters:"
        print self.config
