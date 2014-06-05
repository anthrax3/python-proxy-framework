# -*- coding: utf-8 -*-

from proxyframework.configuration_parser import ConfigParser
import argparse, importlib
import logging, os
from abc import ABCMeta, abstractmethod
import sys
import imp
import pprint

level_of_recursion = 1

# enable logging
logging.basicConfig(
    filename = "proxy-framework.log",
    filemode = "a",
    level = logging.INFO)


class Module(object):
    """ Abstract superclass for all module-implementations
    """
    
    __metaclass__ = ABCMeta

    @abstractmethod
    def register_input_handler(self, port_name, function_name, receiver_object=None):
        """ Register an input-handler for each input-channel as
        specified in the configuration. Method is called externally
        while instantiation."""
        pass

    @abstractmethod
    def register_output_handler(self, port_name, receiver_object):
        """ Register an output-handler entry for each output-port as
        specified in the configuration. Method is called externally
        because only the main-object (proxy) knows all references
        to the corresponding receiver-objects.
        """
        pass
    
    @abstractmethod
    def start(self):
        """ Method for startup-routines - mostly relevant for active-modules, if
        an outern signal is needed to start some kind of processing-routine.
        """
        pass

    @abstractmethod
    def stop(self):
        """ Method for shutdown-routines (e.g. cache-clearances in the case
        of an ARP-spoofer)
        """
        pass

    @abstractmethod
    def send(self, port, pbuf, **kwargs):
        """ Method is called each time a packet should
        be sended out over a specified output-port
        """
        pass
        
    @abstractmethod
    def receive(self, port, pbuf, **kwargs):
        """ Method is called each time a packet arrives at
        the module
        """
        pass
        
class SimpleModule(Module):
    """ SimpleModule for implementing actual functionality-nodes
    in the proxy-framework. Subclasses should implement at least the
    functions that are used by input-ports
    """

    def __init__(self, config_parameters):
        # { config_param : value }
        self.config = config_parameters

        # { input_port_name : handling-function reference }
        self.input_handler = {}
        
        # { output_port_name : reference to target object's receive-function}
        self.output_handler = {}
        self.debugging = False
        
    def register_input_handler(self, port_name, function_name):
        self.input_handler[port_name] = getattr(self, function_name)
        
    def register_output_handler(self, port_name, input_name, receiver_object):
        self.output_handler[port_name] = (receiver_object, input_name)

    def send(self, port, pbuf, **kwargs):
        if self.debugging:
            print "[!] send called with: port=%s, pbuf=%s" %(port, pbuf)
            print "[!] available output-handlers: " + str(self.output_handler)
                
        self.output_handler[port][0](self.output_handler[port][1], pbuf, **kwargs)

    def receive(self, port, pbuf, **kwargs):
        if self.debugging:
            print "[!] receive called with: port=%s, pbuf=%s" %(port, pbuf)
            print "[!] available input-handlers: " + str(self.input_handler)

        self.input_handler[port](pbuf, **kwargs)

    def start(self):
        print "[+] Module started."
        
    def stop(self):
        print "[+] Module stopped"

    def set_debugging(self, debugging):
        self.debugging = debugging
        
class CompoundModule(Module):
    """ CompoundModules can encapsulate other modules (simple- as well as other
    compound-modules) and their configuration as well as connection-setting.
    """

    def __init__(self, module_setup, debugging):

        global level_of_recursion
        self.debugging = debugging
        
        test = True
        
        ws_recursion = level_of_recursion * str(" ")
        level_of_recursion += 6

        if self.debugging:
            print ws_recursion + "---------------------------"
            print ws_recursion + "[+] Compound-Module"
            print ws_recursion + "---------------------------"

        if self.debugging:
                pp = pprint.PrettyPrinter()
                pp.pprint(module_setup)
        
        # {module_name : object_reference}
        self.modules = {}
            
        # holds all ports in the current compound-module as
        # { port : reference to object }
        self.ports = {}

        # {compound's ports as { port_name : reference of compound-module }
        self.external_ports = {}

        # { input_port of cm : function_reference of sm }
        self.input_handler = {}

        # { output_port of cm : function_reference of sm}
        self.output_handler = {}

        # (1) instantiate all modules
        # search through modules INSIDE the current compound-module
        for module_name, module_dict in module_setup["modules"].items():

            # (1.1) COMPOUND-MODULES
            if module_name[:4] == "comp":

                # recursive call 'til no compound-modules are left
                self.modules[module_name[5:]] = CompoundModule(module_dict, debugging)

                
                for port_name, port_reference in self.modules[module_name.split("_")[1]].external_ports.items():

                    if self.debugging:
                        print "module_name=%s" %(module_name)
                        print "port_name=%s, port_reference=%s" %(port_name, port_reference)

                    # "output"
                    prefix = port_name.split("_")[0]
                    # "cm1"
                    mod_id = module_name.split("_")[1]
                    # "out1"
                    postfix = port_name.split("_")[1]
                    
                    self.ports[prefix + "_" + mod_id + "." + postfix] = port_reference

            # (1.2) SIMPLE-MODULES
            elif module_name[:3] == "sim":                
                self.instantiate_simple_module(module_name, module_dict, debugging)

        # (2) futher setup for compound-modules
        if module_setup["type"] == "compound":

            # (2.1) store external ports
            for compound_port, x in module_setup["ports"].items():
                self.external_ports[compound_port] = self

            # (2.2) initialize input-handlers
            # input_handler needs { compound_in : reference to SimpleModule1:simple1_in}
            for mapping_from, mapping_to in module_setup["mapping"].items():
                if mapping_from[:5] == "input":
                    if debugging:
                        print "[+] Registering Input-Handler for Mapping"
                        print "[+] Port-Dictionary:"
                        print self.ports

                        print "[+] Modules-Dictionary:"
                        print self.modules

                        print "mapping_from=%s, mapping_to=%s" %(mapping_from, mapping_to)

                    # eliminate module-id in the channel - NEEDS TO BE IMPROVED
                    prefix = mapping_to.split("_")[0]
                    portname = mapping_to.split("_")[1].split(".")[1]
                        
                    self.register_input_handler(mapping_from, prefix + "_" + portname, getattr(self.modules[mapping_to.split(".")[0].split("_")[1]], "receive"))

                elif mapping_from[:6] == "output":

                    if debugging:
                        print "[+] Registering Output-Handler for Mapping"
                        print "[+] Port-Dictionary:"
                        print self.ports

                        print "mapping_from=%s, mapping_to=%s" %(mapping_from, mapping_to)

                    # eliminate module-id in the channel - NEEDS TO BE IMPROVED
                        
                    # get the module which holds the mapping_from port
                    self.ports[mapping_from].register_output_handler(mapping_from, mapping_to, getattr(self, "send"))

                    
        # (2) setup channels between the modules
        for channel_output, channel_input in module_setup["channels"].items():

            # select the module for the output
            output_module = self.ports[channel_output]
            if debugging:
                print "self.ports"
                print self.ports
            # select the module for the input
            input_module = getattr(self.ports[channel_input], "receive")
            
            # eliminate module-id in the channel - NEEDS TO BE IMPROVED
            out_prefix = channel_output.split("_")[0]
            out_portname = channel_output.split("_")[1].split(".")[1]

            in_prefix = channel_input.split("_")[0]
            in_portname = channel_input.split("_")[1].split(".")[1]

            # register output-handler
            output_module.register_output_handler(out_prefix + "_" + out_portname, in_prefix + "_" + in_portname, input_module)

        # printout current compound-module
        if debugging:
            print ws_recursion + "[+] Ports: "
            for port_name, mapping in self.ports.items():
                print ws_recursion + "    " + "[+] Port-Name: " + str(port_name) + " - " + str(mapping)

            print ws_recursion + "[+] External Ports of the Compound-Module: "
            for port_name, mapping in self.external_ports.items():
                print ws_recursion + "    " + "[+] Port-Name: " + str(port_name) + " - " + str(mapping)

            print ws_recursion + "[+] Input-Handlers of the Compound-Module: "
            for port_name, handler in self.input_handler.items():
                print ws_recursion + "    " + "[+] Input: " + str(port_name) + " - " + str(handler)

            print ws_recursion + "[+] Containing Modules"
            for module_name, module_reference in self.modules.items():
                print ws_recursion + ws_recursion + "-----------------------------"
                print ws_recursion + ws_recursion + "[+] " + module_name
                print ws_recursion + ws_recursion + "[+] Input-Handlers: " + str(module_reference.input_handler)
                print ws_recursion + ws_recursion + "[+] Output-Handlers: " + str(module_reference.output_handler)

            print ws_recursion + "+++++++++++++++++++++++++"
            
    def instantiate_simple_module(self, simple_module_name, simple_module_properties, debugging):
        """ Instantiation of each containing
        simple-module.
        """
        
        try:
            
            # (1) instantiate class + handing over config-dict
            mod_name = simple_module_properties["src"].split("/")
            mod_name = mod_name[-1][:-3]

            if self.debugging:
                print "load mod-name=%s src=%s" %(mod_name, simple_module_properties["src"])

            loaded_mod = imp.load_source(mod_name, simple_module_properties["src"])

            if self.debugging:
                print "loaded mod: " + str(loaded_mod)
            klass = getattr(loaded_mod, simple_module_properties["name"])

            if self.debugging:
                print "parameters: " + str(simple_module_properties["config"])
            
            simple_module_reference = klass(simple_module_properties["config"])

            # debug-flag
            simple_module_reference.set_debugging(debugging)
            
            # (2) register input-handlers
            for port_name, function_name in simple_module_properties["ports"].items():
                if port_name[:5] == "input":
                    simple_module_reference.register_input_handler(port_name, function_name)
                    
            # (3) put reference in self.modules
            self.modules[simple_module_name[4:]] = simple_module_reference

            # (4) store reference for each input
            for port_name, mapping in simple_module_properties["ports"].items():
                if self.debugging:
                    print "[+] Port of SimpleModule inserted:"
                    print "port_name=%s, port_reference=%s" %(port_name, simple_module_reference)

                port_name_new = port_name.split("_")[0] + "_" + simple_module_name[4:] + "." + port_name.split("_")[1]
                
                self.ports[port_name_new] = simple_module_reference
                    
        except ImportError:
            print "[!] Error importing module: %s" %(simple_module_name)
        

    def register_input_handler(self, port_name, mapping_name, function_reference):
        self.input_handler[port_name] = (function_reference, mapping_name)

    def register_output_handler(self, port_name, input_name, receiver_object):
        self.output_handler[port_name] = (receiver_object, input_name)
        
    def send(self, port, pbuf, **kwargs):

        if self.debugging:
            print "[!] send() in compound-module called with port=%s, pbuf=%s" %(port, pbuf)
            print "[!] output-handler: " + str(self.output_handler)
        
        self.output_handler[port][0](self.output_handler[port][1], pbuf, **kwargs)

    def receive(self, port, pbuf, **kwargs):
        # call input-handler function for specified channel

        if self.debugging:
            print "[!] receive() of compound-module called: port=%s, pbuf=%s" %(port, pbuf)
            print "[!] input-handler at this point: %s" %(str(self.input_handler))
        
        self.input_handler[port][0](self.input_handler[port][1], pbuf, **kwargs)
        
    def start(self):
        # call start-method on all modules
        for module_name, module_instance in self.modules.items():
            module_instance.start()

    def stop(self):
        # call stop-method on all modules
        for module_name, module_instance in self.modules.items():
            module_instance.stop()


class Proxy(CompoundModule):
    """ A proxy-module is basically a slightly extended compound module which the
    single difference of the XML-parsing-process before instantiation.
    """

    def __init__(self, configuration_file, current_folder, debugging):
        # parse XML-configuration
        cfgh = ConfigParser()
        module_setup = cfgh.parse_config(configuration_file, current_folder)
        
        # call parents constructor
        super(Proxy, self).__init__(module_setup, debugging)

    
def pf_starter():
    """ This is the console-hook starting point for pf-starter
    """

    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', required = True , help='specify the XML-config file for the proxy')
    parser.add_argument('--verbose', required = False, help='enable debugging printouts')
    args = parser.parse_args()
    
    try:
        prox = Proxy(args.config, str(os.getcwd()) + "/", args.verbose)
        prox.start()
        print "[+] Proxy-Configuration '%s' successfully started!" %(args.config)

    except KeyboardInterrupt:
        prox.stop()
    


