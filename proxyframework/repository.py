# -*- coding: utf-8 -*-

import shutil
import os
from lxml import etree
import argparse, importlib
import logging, os

class Repository(object):
    """ Class representing the repository and offering all possible operations
    """
    
    def __init__(self):
        # TODO -  user should be able to specify the repo-path within installation
        self.repo_path = "/root/.proxy-framework/"
        self.repo_register_path = self.repo_path + "repo.xml"
        
        # holds the root-node (the whole XML-tree)
        self.repo_element = etree.parse(self.repo_path + "repo.xml").getroot()
        self.repo_modules = self.repo_element.xpath("//module")
        
    def list_all_modules(self):
        """ List all modules stored in the repository
        """

        for module in self.repo_modules:
            repo_path = module.xpath("repo")[0].text.split("/")
            
            print "\n" + repo_path[0] + "/" + repo_path[1] + ": " +  '\033[1m' + module.xpath("name")[0].text + '\033[0m'
            print "  %s" %(module.find("desc").text)

        print "\n"
            
    def search_repo_module(self, search_string):
        """ Search for a module in the repo using a given search-string
        """

        # simple search operation using xpath-methods
        modules = self.repo_element.xpath("/repository/module/name[contains(text(),'" + search_string + "')]/.. | /repository/module/desc[contains(text(), '" + search_string + "')]/..")

        if len(modules) != 0:
            print "[+] Results for query: '%s'" %(search_string)
            
            for module in modules:
                print "   - " + '\033[1m' + module.xpath("name")[0].text + '\033[0m'
                print "     " + module.xpath("desc")[0].text

            return True

        else:
            return False
            
    def get_instantiation(self, module_name):
        """ Printout a XML-instantiation of a given module identified by an unique module name
        """

        module = self.repo_element.xpath("/repository/module/name[text()='" + module_name + "']/..")
                
        if module is None:
            print "[!] Error: No module found named %s" %(module_name)

        else:
            # load and parse description file
            module_path = module[0].find("repo").text
            module_name = module_path.split("/")[-1]            
            det_module = etree.parse(self.repo_path + module_path + "/" + module_name + ".xml").getroot()
            
            print "    " + '<module type="simple" repo="' + module[0].find("repo").text + '" id="###">'

            # insert configuration block
            if det_module.xpath("module/config") is not None:
                print "    " + '  <config>'
                conf_params = det_module.xpath("/module/config/param")

                for param in conf_params:
                    if param.attrib.has_key("value"):
                        print "    " + "    " + '<param id="' + param.attrib["id"] + '" value="' + param.attrib["value"] + '"/>'

                    else:
                        print "    " + "    " + '<param id="' + param.attrib["id"] + '" value="###"/>'
                        
            print "    " + '  </config>'
            print "    " + '</module>'

            
    def show_detailled_information(self, module_name):
        """ Printout detailed information about a module specified by an unique module name
        """

        module = self.repo_element.xpath("/repository/module/name[text()='" + module_name + "']/..")

        if module is None:
            print "[!] Error: No module found named %s" %(module_name)

        else:
            print "Module: " + '\033[1m' + module[0].find("name").text + '\033[0m'

            # load and parse description file
            module_path = module[0].find("repo").text
            module_name = module_path.split("/")[-1]            
            det_module = etree.parse(self.repo_path + module_path + "/" + module_name + ".xml").getroot()


            # print description (optional)
            if det_module.xpath("module/desc") is not None:
                print "   " + det_module.xpath("/module/desc")[0].text
            
            # print ports (optional)
            if det_module.xpath("module/ports") is not None:
            
                print '\033[1m' + "\nPorts of the Module:" + '\033[0m'
                output_ports = det_module.xpath("/module/ports/output")
                input_ports = det_module.xpath("/module/ports/input")

                if output_ports is not None:
                    for port in output_ports:
                        print "   output-port: %s (type=%s)" %(port.attrib["id"], port.attrib["type"])

                if input_ports is not None:
                    for port in input_ports:
                        print "   input-port: %s (type=%s, mapped to function=%s)" %(port.attrib["id"], port.attrib["type"], port.attrib["function"])

            # print configuration-parameters (optional)
            if len(det_module.xpath("//module/config")) != 0:
                print '\033[1m' + "\nConfiguration Parameters:" + '\033[0m'
                conf_params = det_module.xpath("/module/config/param")

                for param in conf_params:
                    print "   " + "param-id: " + param.attrib["id"]

                    if param.attrib.has_key("value"):
                        print "      " + "default-value: " + param.attrib["value"] + " (optional)"

                    else:
                        print "      " + "(required)"

                    if param.attrib.has_key("desc"):
                        print "      " + "description: " + param.attrib["desc"]

            print '\n\033[1m' + "Instantiation:" + '\033[0m'
            self.get_instantiation(module_name)


    def insert_module(self, source_dir, repo_path):
        """ Insert a given module into the repo
        """
        
        # TODO - better model of internal representation of module names and paths
        module_name = source_dir.split("/")[-2]
        
        # check if module with same name exists
        if self.search_repo_module(module_name) is True:
            print "Module with same name exists!"

        else:
            # load module-description
            det_module = etree.parse(source_dir + module_name +  ".xml").getroot()

            # insert values in repository-register
            repository_root = self.repo_element

            module_root = etree.SubElement(repository_root, "module")
            # TODO compound-modules should be supported as well
            module_root.set("type","simple")

            # name of the module
            mod_name = etree.SubElement(module_root, "name")
            mod_name.text = module_name

            mod_author = etree.SubElement(module_root, "author")
            mod_author.text = det_module.xpath("/module/author")[0].text

            mod_desc = etree.SubElement(module_root, "desc")
            mod_desc.text = det_module.xpath("/module/desc")[0].text

            mod_repo = etree.SubElement(module_root, "repo")
            mod_repo.text = repo_path + "/" + module_name

            et = etree.ElementTree(repository_root)       
            et.write(self.repo_register_path)

            destination_dir = self.repo_path + repo_path + "/" + module_name + "/"

            print "source_dir=%s" %(source_dir)
            print "destination_dir=%s" %(destination_dir)
            
            # copy relevant files into correct path
            shutil.copytree(source_dir, destination_dir)

            print "Module '" + module_name + "' inserted!"


def pf_repo():
    """ This is the console-hook starting point for pf-starter
    """

    repo = Repository()

    # Parse arguments
    parser = argparse.ArgumentParser(
        description='Helper script to access the repository of the proxy-framework. Use one of the available operations as specified beyond.')
    
    parser.add_argument('--list', action='store_true', help='list all modules of the repository')
    parser.add_argument('--search', help='search for a module by specifying a search-string')
    parser.add_argument('--display', help='show a particular module')
    parser.add_argument('--insert', nargs = '*', help='insert a new module into the repository')
    parser.add_argument('--delete', help='delete a module from the repository')
    
    args = parser.parse_args()

    if args.list:
        repo.list_all_modules()

    elif args.search:
        repo.search_repo_module(args.search)

    elif args.display:
        repo.show_detailled_information(args.display)

    elif args.insert:
        repo.insert_module(os.getcwd() + "/" + args.insert[0], args.insert[1])
                        
if __name__ == '__main__':
    rp = Repository()
    rp.list_all_modules()
    rp.show_detailled_information("ArpSpoofer")
    rp.get_instantiation("ArpSpoofer")

