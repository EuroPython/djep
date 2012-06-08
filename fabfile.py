# -*- coding: utf-8 -*-
from fabric.api import *
from os.path import join

if not env.get('branch'):
    abort("Please select a config file (staging.ini | live.ini)")
env.hosts = ['pyconde00.gocept.net', ]
env.srv_user = 'pyconde'
env.proj_name = 'pyconde'
env.www_root = join(env.root, 'htdocs')
env.proj_root = join(env.root, 'pycon_de_website')
env.pip_files = (
    join(env.proj_root, 'requirements.txt'),
)
env.manage_py = join(env.proj_root, env.proj_name, 'manage.py')


@task
def test_env():
    print env


@task
def test_id():
    srv_run('id')


def srv_run(cmd):
    return sudo(cmd, user=env.srv_user)


def srv_open_shellfa(cmd):
    return open_shell('sudo -u %s -s -- %s' % (env.srv_user, cmd))


def ve_python(cmd):
    return srv_run('%s %s' % (join(env.root, 'bin', 'python'), cmd))


def manage_py(cmd):
    return ve_python('%s %s' % (join(env.proj_root, env.proj_name, 'manage.py'), cmd))


def supervisorctl(cmd):
    return srv_run('%s %s' % (join(env.root, 'bin', 'supervisorctl'), cmd))


@task
def upgrade():
    update_proj()
    update_requirements()
    syncdb()
    migrate()
    build_static_files()
    restart_worker()


@task
def update():
    update_proj()
    syncdb()
    migrate()
    restart_worker()


@task
def syncdb():
    manage_py('syncdb --noinput')


@task
def migrate():
    manage_py('migrate')


@task
def update_requirements():
    pip = join(env.root, 'bin', 'pip')
    for reqfile in env.pip_files:
        srv_run('%s install --use-mirrors -E %s -r %s' % (pip, env.root, reqfile))


@task
def update_proj():
    with cd(env.proj_root):
        srv_run('git pull')
        srv_run('git checkout -f %s' % env.branch)
        srv_run('git submodule init')
        srv_run('git submodule update')


@task
def build_static_files():
    with path('/srv/pyconde/local/bin', behavior="prepend"):
        with cd(env.proj_root):
            srv_run('lessc -x pyconde/static_media/css/style.{less,css}')
        manage_py('collectstatic --noinput -v1 -i bootstrap -i \'*.less\'')
        manage_py('compress')


@task
def restart_worker():
    return supervisorctl('restart pyconde')


@task
def djshell():
    return srv_open_shell('%s %s shell' % (
        join(env.root, 'bin', 'python'),
        join(env.proj_root, env.proj_name, 'manage.py')))


@task
def loaddata(fixture):
    manage_py('loaddata {0}'.format(fixture))


@task
def build_statics():
    with lcd('pyconde'):
        local('lessc static_media/css/style.{less,css}')
        local('python manage.py collectstatic --noinput -v1 -i bootstrap -i \'.*.less\'')
        local('python manage.py compress -v0 --force')
