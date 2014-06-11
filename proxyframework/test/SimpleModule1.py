# -*- coding: utf-8 -*-

from proxyframework.core import SimpleModule

class SimpleModule1(SimpleModule):

    def start(self):

        print "[+] SimpleModule1: Input Handlers:"
        print self.input_handler
        print "[+] SimpleModule1: Output Handlers:"
        print self.output_handler
        
        print "[+] SimpleModule1: Received Parameters:"
        print self.config
        
        print "[+] SimpleModule1: output data"
        self.send("output_out1", "Test from SimpleModule1")
