# -*- coding: utf-8 -*-
from fabric.api import *
from os.path import join


env.hosts = ['pyconde00.gocept.net',]
env.srv_user = 'pyconde'
env.root = '/srv/pyconde/env_pyconde_2012'

env.proj_name = 'pyconde'
env.www_root = join(env.root, 'htdocs')
env.proj_root = join(env.root, 'pycon_de_website')
env.pip_files = (
    join(env.proj_root, 'requirements.txt'),
)
env.manage_py = join(env.proj_root, env.proj_name, 'manage.py')


def test_id():
    srv_run('id')

def srv_run(cmd):
    return sudo(cmd, user=env.srv_user)

def srv_open_shell(cmd):
    return open_shell('sudo -u %s -s -- %s' % (env.srv_user, cmd))

def ve_python(cmd):
    return srv_run('%s %s' % (join(env.root, 'bin', 'python'), cmd))

def manage_py(cmd):
    return ve_python('%s %s' % (join(env.proj_root, env.proj_name, 'manage.py'), cmd))

def supervisorctl(cmd):
    return srv_run('%s %s' % (join(env.root, 'bin', 'supervisorctl'), cmd))

def upgrade():
    update_proj()

    update_requirements()

    syncdb()
    migrate()

    build_static_files()

    restart_worker()

def update():
    update_proj()

    syncdb()
    migrate()

    restart_worker()

def syncdb():
    manage_py('syncdb --noinput')

def migrate():
    manage_py('migrate')

def update_requirements():
    pip = join(env.root, 'bin', 'pip')
    for reqfile in env.pip_files:
        srv_run('%s install --use-mirrors -E %s -r %s' % (pip, env.root, reqfile))

def update_proj():
    srv_run('cd %s; git pull' % env.proj_root)

def build_static_files():
    manage_py('collectstatic --noinput -v1')

def restart_worker():
    return supervisorctl('restart pyconde')

def djshell():
    return srv_open_shell('%s %s shell' % (
        join(env.root, 'bin', 'python'),
        join(env.proj_root, env.proj_name, 'manage.py')))
