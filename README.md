python-proxy-framework
======================
*Proof-of-concept* implementation of a framework for building flexible and powerful network-proxy configurations in the context of security audits or penetration tests. Users are able to write individual proxy-configurations as XML descriptions by inserting modules which can either be self-implemented or imported from a included repository. Valid proxy-configurations can be executed by using a provided console script.

## Requirements

* python 2.6 / 2.7
* lxml

## Install

Install the python-proxy-framework by useing python-setuputils as:
    
    $ python2 setup.py install

## Contributing

I would be happy for every contribution regarding this particular implementation. For reasons of simplicity, please follow the instructions below:

1. Fork the project to your own Github account
1. Create a named topic branch to contain your change
1. Change whatever you're up to.
1. If you are adding new functionality, document it in the Readme.md (Sphinx-Documentation will be available soon).
1. Push the branch up to GitHub and send a pull request for your branch

## License
python-proxy-framework is free software and released under the terms of the GNU General Public License v2 (http://www.gnu.org/licenses/gpl-3.0.html), as specified in LICENSE.