from setuptools import setup
import os
import sys
from distutils.core import setup
from distutils.command.install import install as _install
import shutil

with open('README.md') as file:
    long_description = file.read()

def _post_install(dir):
    from subprocess import call
    current_dir =  os.getcwd()
    call([sys.executable, 'modules/insert_repo.py'],
         cwd=os.path.join(current_dir, 'proxyframework'))

def init_repo():
    """ Copy repository-contents to a local repo located at ~/.proxy-framework
    """
    home_folder = os.getenv('USERPROFILE') or os.getenv('HOME')
    destination_dir = home_folder + "/.proxy-framework/"
    source_dir = "proxyframework/repository/"

    shutil.copytree(source_dir, destination_dir)

def init_documentation():
    pass
    
class install(_install):
    def run(self):
        _install.run(self)
        init_repo()
setup(
    name = "python-proxy-framework",
    version = "0.0.1",
    author = "Frederik Hauser",
    author_email = "frederik@fhauser.de",
    description = ("Framework for creating network-proxy-configuration in the context of security audits"),
    license = "GPLv2",
    keywords = "network, security, audit, pentest, proxy",
    url = "https://github.com/fhauser/python-proxy-framework",
    packages = ['proxyframework'],
    include_package_data = True,
    entry_points = {
        'console_scripts': [
            'pf-repo = proxyframework.repository:pf_repo',
            'pf-starter = proxyframework.core:pf_starter',
        ],
    },
    cmdclass = { 'install' : install},
    package_data = {'proxy-framework': ['README.md', 'LICENSE.txt']},
    long_description = long_description,
    classifiers = [
        "Development Status :: 1 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: GPLv2 License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Topic :: Utilities",
    ],
)
