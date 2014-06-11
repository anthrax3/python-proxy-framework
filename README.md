python-proxy-framework
======================
*Proof-of-concept* implementation of a framework for building flexible and powerful network-proxy configurations in the context of security audits or penetration tests. Users are able to write individual proxy-configurations as XML descriptions by inserting modules which can either be self-implemented or imported from a included repository. Valid proxy-configurations can be executed by using a provided console script.

Additional ressources:
* [Slides - Bachelor Thesis Defense](http://www.fhauser.de/pub/140224_Slides_Thesis.pdf)

## Requirements

* python 2.6 / 2.7
* lxml

## Install

Install the python-proxy-framework by useing python-setuputils as:
    
    $ python2 setup.py install

# Documentation
## Execute a proxy-configuration
An existing and valid proxy-configuration (available as XML-file) can be executed by useing a provided console-script:

    $ pf-starter --config SampleProxyConfiguration.xml

## Interact with the repository
All interactions with the repository can be performed with the corresponding console-script:

* Printout a list of all present modules within the repository
  $ pf-repo --list$

* Search for a module by giving a search-string
  $ pf-repo --search "UserAgent"

* Show detailled information about a specific module
  $ pf-repo --display "UserAgentChanger"


# Information

## Improvements
As mentioned in the introduction, the current implementation should be considered as project in a *Proof-of-concept* state. Improvements as well as error-corrections will take place within the future. The *Issue* functionality for this repository can be used to report errors / problems or improvement proposals. 

## Contributing

I would be happy for every contribution regarding this particular implementation. For reasons of simplicity, please follow the instructions below:

1. Fork the project to your own Github account
1. Create a named topic branch to contain your change
1. Change whatever you're up to.
1. If you are adding new functionality, document it in the Readme.md (Sphinx-Documentation will be available soon).
1. Push the branch up to GitHub and send a pull request for your branch

## License
python-proxy-framework is free software and released under the terms of the GNU General Public License v3 (http://www.gnu.org/licenses/gpl-3.0.html), as specified in LICENSE.