# -*- coding: utf-8 -*-

from lxml import etree
import pprint, os

class ConfigParser(object):
    """ Parses a given proxy-framework configuration
    written in XML
    """
    
    def __init__(self, ):
        
        self.pf_repo = "/root/.proxy-framework/"
        self.pf_current = ""


    def parse_configuration_block(self, module):
        """ Parses a configuration block consisting of
        <param id="##" value="##"/> nodes
        """
        
        cfg_dict = {}
        config_nodes = module.iterfind("config/param")

        # iterate over each param-node
        for param in config_nodes:
            cfg_dict[param.attrib["id"]] = param.attrib["value"]

        return cfg_dict

    def parse_port_block(self, simple_module):
        """ Parses a port block consisting of
        <input id="##" function="##" type="##"/> or
        <output id="##" type="##"/> nodes
        """
        
        port_dict = {}

        inputs = simple_module.iterfind("ports/input")
        outputs = simple_module.iterfind("ports/output")

        if inputs is not None:
            for port in inputs:
                port_dict["input_" + port.attrib["id"]] = port.attrib["function"]

        if outputs is not None:
            for port in outputs:
                port_dict["output_" + port.attrib["id"]] = None    

        return port_dict

    def parse_simple_module(self, simple_module, current_folder = ""):
        """ Parses a Simple Module instantiation into the internal
        dictionary structure for handling within the proxy-framework
        """

        module_dict = {}

        # unique ID of the current simple module
        module_id = simple_module.attrib["id"]
        module_attribs = simple_module.attrib

        # the default configuration needs to be loaded from the
        # corresponding module description

        # (1) module description specified via src-attribute
        if module_attribs.has_key("src"):

            # check, if config-node existent
            config_node = simple_module.find("config")

            if config_node is not None:
                module_dict.setdefault("config", self.parse_configuration_block(simple_module))
                simple_module = etree.parse(module_attribs["src"]).getroot()

            # if no config-node existent: use all config-data from referenced module-file
            else:

                simple_module = etree.parse(module_attribs["src"]).getroot()
                module_dict.setdefault("config", self.parse_configuration_block(simple_module))

            # source of current module
            module_src = simple_module.find("src").text

            # absolute path
            if module_src[:1] == "/":
                module_dict["src"] = module_src

            # relative path to current
            else:
                module_dict["src"] =  current_folder + module_src

        # module from REPO
        elif module_attribs.has_key("repo"):

            # read config-section
            module_dict.setdefault("config", self.parse_configuration_block(simple_module))

            # TODO - improve handling of module-names in config-parser + core
            module_name = module_attribs["repo"].split("/")[-1]
            
            # build repo-path out from <repo location> + <repo string> + <module name> + xml-extension
            module_src = self.pf_repo + module_attribs["repo"] + "/" + module_name + ".xml"

            print "[+] repo src: %s" %(module_src)
            
            simple_module = etree.parse(module_src).getroot()

            # source as specified in repo XML-file "module.py"
            simple_module_src = simple_module.find("src").text

            module_path = module_src.split("/")[:-1]
            code_path = ""
            for path_str in module_path:
                code_path += path_str + "/"

            module_dict["src"] = code_path + simple_module_src
                        
            # load module from repo
            simple_module = etree.parse(module_src).getroot()
            
        # module defined INPLACE
        else:
            module_dict.setdefault("config", self.parse_configuration_block(simple_module))

            # source of current module
            module_dict["src"] = current_folder + simple_module.find("src").text
                        
            # source of current module
            module_src = current_folder + simple_module.find("src").text

            # absolute path
            if module_src[:1] == "/":
                module_dict["src"] = module_src

            # relative path to current
            else:
                module_dict["src"] = current_folder + module_src


        module_dict["name"] = simple_module.find("name").text
        
        # port-section
        module_dict.setdefault("ports", self.parse_port_block(simple_module))

        # should return the module dictionary
        return module_id, module_dict


    def parse_compound_module(self, compound_module, current_folder):
        """ Parses a XML-compound-module description
        """

        module_dict = {}
        module_dict.setdefault("modules", {})
        module_attribs = compound_module.attrib

        if module_attribs["type"] != "proxy":
            module_id = module_attribs["id"]

        else:
            module_id = None

        # repo
        if module_attribs.has_key("repo"):
            print "repo-module"

        # src
        elif module_attribs.has_key("src"):
            compound_module = etree.parse(module_attribs["src"]).getroot()

        if module_attribs["type"] == "proxy":
            module_dict["name"] = compound_module.find("name").text

        module_name = compound_module.find("name").text
        module_dict["type"] = module_attribs["type"]

        # (1) parse simple-modules
        simple_modules = compound_module.iterfind("module[@type='simple']")

        for simple_module in simple_modules:
            simple_module_id, simple_module_dict = self.parse_simple_module(simple_module, current_folder)
            module_dict["modules"]["sim_" + simple_module_id] = simple_module_dict

        # (2) parse compound-modules
        compound_modules = compound_module.iterfind("module[@type='compound']")

        for comp_module in compound_modules:
            # recursively parses all compound-modules
            comp_module_id, comp_module_dict = self.parse_compound_module(comp_module, current_folder)
            module_dict["modules"]["comp_" + comp_module_id] = comp_module_dict

        # (3) parse channels
        channels = compound_module.iterfind("channel")
        channel_dict = self.parse_channels(channels)

        module_dict["channels"] = channel_dict
        module_dict["name"] = module_name

        # (4) parse ports
        # Different to simple-module, as ports have only an id

        # only parse ports ifnot proxy-compound-module
        if compound_module.attrib["type"] == "compound":
            port_dict = {}

            inputs = compound_module.iterfind("ports/input")
            outputs = compound_module.iterfind("ports/output")

            if inputs is not None:
                for port in inputs:
                    port_dict["input_" + port.attrib["id"]] = None

            if outputs is not None:
                for port in outputs:
                    port_dict["output_" + port.attrib["id"]] = None    
        
            module_dict.setdefault("ports", port_dict)

        # (4) set-up mappings
        mapping_dict = {}
        mapping_node = compound_module.find("mapping")
    
        if mapping_node is not None:

            # parse port-mappings
            port_map_nodes = compound_module.iterfind("mapping/portmap")

            if port_map_nodes is not None:
                for port_map_node in port_map_nodes:
                    mapping_dict[port_map_node.attrib["dir"] + "_" + port_map_node.attrib["port"]] = port_map_node.attrib["dir"] + "_" + port_map_node.attrib["to"]

            # parse config-mappings
            conf_map_nodes = compound_module.iterfind("mapping/confmap")

            if conf_map_nodes is not None:
                for conf_map_node in conf_map_nodes:
                    mapping_dict[conf_map_node.attrib["id"]] = conf_map_node.attrib["to"]
                
            module_dict["mapping"] = mapping_dict

        return module_id, module_dict

    def parse_channels(self,channels):
        """ Parse all channels of a given configuration
        """

        channel_dict = {}

        for channel in channels:
            ch_output, ch_input = self.parse_channel(channel)
            channel_dict.setdefault(ch_output, {})
            channel_dict[ch_output] = ch_input

        return channel_dict

    def parse_channel(self, channel):
        """ Parse a single channel node
        """

        ch_output = "output_" + channel.attrib["source"]
        ch_input = "input_" + channel.attrib["sink"]

        return ch_output, ch_input

    def parse_config(self, filename, current_folder):
        """ Parse complete configuration
        """
        
        # initialize empty dictionary for config
        module_config = {}

        # holds the root-node (the whole XML-tree)
        proxy_element = etree.parse(filename).getroot()
        module_name, module_config = self.parse_compound_module(proxy_element, current_folder)

        return module_config
        
# debug configuration - show internal representation of parsed configuration
if __name__ == '__main__':

    cfgh = ConfigParser()
    cfg = cfgh.parse_config("ProxyInstantiation.xml", str(os.getcwd()) + "/")

    pp = pprint.PrettyPrinter()
    pp.pprint(cfg)
