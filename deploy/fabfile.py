# -*- coding: utf-8 -*-

# http://docs.fabfile.org/en/1.5/tutorial.html
from __future__ import with_statement
from fabric.api import *
from contextlib import contextmanager as _contextmanager

@_contextmanager
def virtualenv():
    with prefix(env.virtualenv_activate):
        yield

env.hosts = ['176.58.125.166']
env.user = 'rootio'
env.project_root = '/home/rootio/public_python/rootio_web'
env.virtualenv_activate = 'source venv/bin/activate'
env.forward_agent = True

def git_update():
    stash_str = run("git stash")
    run("git pull origin master")
    if stash_str.strip() != 'No local changes to save':
    	run("git stash pop")


def restart_apache():
    sudo("/etc/init.d/apache2 graceful")


def restart_cache():
    sudo("/etc/init.d/memcached restart", pty=False)


def touch_wsgi():
    # Touching the deploy.wsgi file will cause apache's mod_wsgi to
    # reload all python modules having to restart apache.
    with cd(env.project_root):
        run("touch deploy/rootio_web.wsgi")


def update(full=False):
    with cd(env.project_root):
        git_update()
        with virtualenv():
            run("pip install -r requirements.txt")
            run("python manage.py migrate up")
            #todo: static files
    touch_wsgi()
    #restart_cache()
    #restart_apache()


def deploy():
    update()


def server_logs():
    with cd(env.project_root):
        run("tail -f error.log")

def initdb():
    local("python manage.py initdb")    


def reset():
    """
    Reset local debug env.
    """
    local("rm -rf /tmp/instance")
    local("mkdir /tmp/instance")


def runserver():
    """
    Run local server, for debugging only.
    Need to move up one directory, from deploy to see manage.py
    """
    with lcd('..'):
        with virtualenv():
            local("python manage.py runserver")
