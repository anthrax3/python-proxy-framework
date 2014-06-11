# -*- coding: utf-8 -*-

from proxyframework.core import SimpleModule

class SimpleModule4(SimpleModule):
    def input_handler_1(self, pbuf, **kwargs):
		
        print "[+] SimpleModule4: Received Parameters:"
        print self.config
        
        print "[+] Input-method of SimpleModule4"
        print "[+] Finished!"

