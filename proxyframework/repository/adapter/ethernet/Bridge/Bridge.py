# -*- coding: utf-8 -*-

""" python-proxy-framework
Copyright (C) 2014 Frederik Hauser

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from proxyframework.core import SimpleModule
import asyncore
from subprocess import call
import threading
import time
import nfqueue
from socket import AF_INET, AF_INET6, inet_ntoa


class Bridge(SimpleModule):
    """ Gathers packets specified by parameters out of
    the 5-tuple on a specified interface.
    """

    def __init__(self, configuration_parameters):
        # call parents constructor
        super(Bridge, self).__init__(configuration_parameters)

        self.nfq_threads = []
        self.nfq_rules = []

        print "[+] Bridge Module started"

        """
        Parsing key:value-tupels as "q1-...", where qn determines,
        to which queue the specified rules belong to
        """

        self.queue_dict = {}

        # creating queue_dict-entries
        for name, value in self.config.iteritems():

            # check, if config-parameter belongs to queue-config
            if name[0:1] == "q":

                if name[0:2] not in self.queue_dict:
                    self.queue_dict[name[0:2]] = {}

                self.queue_dict[name[0:2]][name[3:]] = value

        # setup bridge device
        if call("brctl addbr brpf", shell = True):  
            print "[!] Bridge-Device was not created!"

        if call("brctl addif brpf " + self.config["interface-in"], shell=True):
            print "[!] Source-Interface was not setup correctly!"

        if call("brctl addif brpf " + self.config["interface-out"], shell=True):
            print "[!] Sink-Interface was not setup correctly!"
            
        """
        Building together configuration-strings for passing
        to iptables
        """

        for queue, properties in self.queue_dict.iteritems():
            ipt_filter = ""
            ipt_protocol = ""

            for param, value in properties.iteritems():
                if param == "protocol":
                    ipt_protocol = "-p " + value + " "

                elif param == "source-port":
                    ipt_filter += "--sport " + value + " "

                elif param == "destination-port":
                    ipt_filter += "--dport " + value + " "

                elif param == "source-ip":
                    ipt_filter += "--src " + value + " "

                elif param == "destination-ip":
                    ipt_filter += "--dst " + value + " "

                elif param == "interface-in":
                    ipt_filter += "-m physdev --physdev-in " + value + " "

                elif param == "output":
                    self.queue_dict[queue]["output"] = value

                elif param == "interface":
                    self.queue_dict[queue]["interface"] = value

            # store queue-number
            self.queue_dict[queue]["queuenum"] = int(queue[1:])

            ipt_rule =  ipt_protocol + ipt_filter + "-j NFQUEUE --queue-num " + str(self.queue_dict[queue]["queuenum"])

            print "iptables -t filter -A FORWARD " + ipt_rule
            
            # store iptables-rule in dictionary
            self.queue_dict[queue]["ipt"] = ipt_rule


            if call("iptables -t filter -A FORWARD " + ipt_rule, shell = True):
                print "[!] Invalid iptables command!"
                print "[!] " + ipt_rule

        print "[+] Final dict"
        print self.queue_dict

    def start(self):
        """
        Method is called AFTER all classes were instantiated
        """

        print "[+] start() of Bridge"

        """
        Create asynchronous nfqueue-queuehandlers
        """

        print "queue dict"
        print self.queue_dict

        for queue, properties in self.queue_dict.iteritems():
            th_handler = NetfilterQueueHandler(self.from_nfq, properties["queuenum"])
            self.nfq_threads.append(th_handler)

        print "[+] input-handlers"
        print self.input_handler

        print "[+] output-handlers"
        print self.output_handler
        
        asyncore.loop()
        print "startup done"

    def stop(self):
        """ Stop all Threads + delete set iptables rules
        """

        for thread in self.nfq_threads:
            thread.stop()
            thread.join()

        # iterate over existing queues
        for queue, properties in self.queue_dict.iteritems():

            # delete set iptables-rules
            ipt_rule = properties["ipt"]
            if call("iptables -t filter -D FORWARD " + ipt_rule, shell = True):
                print "[!] Invalid iptables command!"
                print "[!] " + ipt_rule

            # delete iptables-rule, if not present any longer
            del properties["ipt"]

        #if call("iptables --flush", shell = True):
        #   print "[!] Invalid iptables command!"


    def from_nfq(self, pbuf, **kwargs):
        """ Callback-function for nfqueue, which handels all
        arriving data
        """

        print "[+] callback-function called!"

        self.send("output_out1", pbuf)


class NetfilterQueueHandler(asyncore.file_dispatcher):
    """ Asyncore dispatcher of nfqueue-events
    Sourcecode adapted from nfqueue-bindings example set
    """

    def __init__(self, cb, nqueue=0, family=AF_INET, maxlen=5000, map=None):
        self.queue = nfqueue.queue()
        self.queue.set_callback(cb)
        self.queue.fast_open(nqueue, family)
        self.queue.set_queue_maxlen(maxlen)
        self.fd = self.queue.get_fd()
        asyncore.file_dispatcher.__init__(self, self.fd, map)
        self.queue.set_mode(nfqueue.NFQNL_COPY_PACKET)

    def handle_read(self):
        self.queue.process_pending(5)

    def writable(self):
        return False




