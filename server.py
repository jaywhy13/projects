import os

from fabric.api import *
from fabric.operations import *

PROJECTS_TEST = 'root@50.56.205.38'
#env.hosts = [PROJECTS_TEST]
#env.passwords[PROJECTS_TEST] = '4Dfw03IQoprojects-test'

PACKAGES = (
    'apache2',
    'php5',
    'php5-dev',
    'git',
    'subversion',
    'python-setuptools',
    'python-pip',
    'git-core',
    'libapache2-mod-wsgi',
    'g++',
    'opendk-7-jdk',
    'make',
    'build-essential',
    'libxerces-c2-dev',
    'libxqilla-dev',
    'libdb4.8',
    'libdb4.8-dev',
    'python-virtualenv',
    )

PIP_PACKAGES = (

)

def setup():
    """ main setup function that will bring a server from 
    scratch and bring up to the level it needs to be to run
    1map, django apps, drupal and other installations.
    """
    setup_apt()
    setup_packages()
    setup_dbxml()


def setup_apt():
    # replaces rackspace's sources.list coz their mirrors are slow
    put('setup/sources.list','/etc/apt/sources.list', use_sudo=True)
    sudo('apt-get update')

def setup_packages():
    install_package(" ".join(PACKAGES))
    
def setup_dbxml():
    #put('setup/dbxml-2.5.16.tar.gz','/tmp/', use_sudo=True)
    with cd('/tmp/'):
        #sudo('tar xvf dbxml-2.5.16.tar.gz')
        # patch bug 
        sudo("sed -i '27i#include <cstddef>' dbxml-2.5.16/xqilla/include/xqilla/framework/XPath2MemoryManager.hpp")
        with cd('dbxml*'):
            sudo('./buildall.sh --enable-java')

def configure_dbxml():
    """ configures dbxml, MUST be run after setup_dbxml
    """
    with cd('/tmp/dbxml*'):
        with cd('db-*/php_db4'):
            sudo('phpize')
            sudo('./configure --with-db4=$PWD/../../install')
            sudo('make')
            sudo('make install')
        with cd('dbxml/src/php'):
            sudo('phpize')
            sudo('./configure --with-dbxml=$PWD/../../install')
            sudo('make')
            sudo('make install')
            
def install_package(package):
    sudo('apt-get install -y %s' % package)


#### other stuff
def add_user(user=None, psw=None):
    if not user:
        user = 'gisadmin'
    if not psw:
        psw = 't1abns4MGI'
        
    sudo('useradd %s', user)
    sudo('echo "%s ALL=(ALL) ALL" >> /etc/sudoers' % user)
    sudo('echo "%s:%s" | chpasswd' % (user, psw))

#### scripts for automating deployment of our apps
def deploy_django_project(local_dir, overwrite=False):
    """ the idea now is that we will give it a local directory
    and the script will automatically deploy it 
    """
    pass

def deploy_1map_app(local_dir, overwrite=False):
    pass

def download_1map_app(app):
    """ Used to download a 1map app from projects
    """
    with cd('/var/www/html/'):
        sudo('tar zcvf %s.tar.gz %s' % (app,app))
        if not os.path.exists("1map"):
            os.mkdir("1map")
        get('%s.tar.gz' % app, '1map/')
        sudo('rm %s.tar.gz' % app)

def deploy_1map_app(app):
    """ Given the name of the folder that the 1map app lies in it will download 
    a copy of the app then push it to a server. This assumes that the project
    has already been downloaded from 1map.
    """
    tar = "1map/%s.tar.gz" % app
    if not os.path.exists(tar):
        download_1map_app(app)
    if os.path.exists(tar):
        put(tar, '/var/www/', use_sudo=True)
        with cd('/var/www/'):
            sudo('tar xvf %s.tar.gz' % app)
            restart_services()

def restart_services():
    sudo('service apache2 restart')
    sudo('service postgresql restart')
