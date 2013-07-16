# -*- coding: utf-8 -*-
import functools
from os.path import join, splitext

from fabric.api import *

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
env.manage_py = join(env.proj_root, 'manage.py')
env.use_ssh_config = True

def srv_run(cmd):
    return sudo(cmd, user=env.srv_user)


def srv_open_shellfa(cmd):
    return open_shell('sudo -u %s -s -- %s' % (env.srv_user, cmd))


def ve_python(cmd):
    return srv_run('%s %s' % (join(env.root, 'bin', 'python'), cmd))


def manage_py(cmd):
    return ve_python('%s %s' % (join(env.proj_root, 'manage.py'), cmd))


def supervisorctl(cmd):
    return srv_run('%s %s' % (join(env.root, 'bin', 'supervisorctl'), cmd))


@task
def compilemessages():
    """Compile the i18n messages."""
    with cd(join(env.proj_root, env.proj_name)):
        manage_py('compilemessages')


@task
def upgrade():
    """
    Upgrades the server to the latest codebase.
    """
    update_proj()
    update_requirements()
    syncdb()
    migrate()
    build_static_files()
    compilemessages()
    restart_worker()
    build_docs()


@task
def syncdb():
    """
    Executes python manage.py syncdb on the server.
    """
    manage_py('syncdb --noinput')


@task
def migrate():
    """
    Executes python manage.py migrate on the server.
    """
    manage_py('migrate')


@task
def update_requirements():
    """
    Updates the project's requirements based on the requirements.txt file.
    """
    pip = join(env.root, 'bin', 'pip')
    for reqfile in env.pip_files:
        srv_run('%s install --use-mirrors -r %s' % (pip, reqfile))


@task
def update_proj():
    """
    Fetches changes from the repository.
    """
    with cd(env.proj_root):
        srv_run('git pull')
        srv_run('git checkout -f %s' % env.branch)
        srv_run('git submodule init')
        srv_run('git submodule update')


def _find_style_less(cmd):
    """Helper that returns the path to style.less suitable for lessc.

    cmd is either functools.partial(local, capture=True), sudo or run.
    """
    output = cmd('{0}/bin/python manage.py findstatic css/style.less'.format(env.root))
    fname = output.splitlines()[1].strip()  # first line contains header
    return '%s.{less,css}' % splitext(fname)[0]


@task
def build_static_files():
    """
    Compiles less files into css, runs collectstatic and compress.
    """
    with path('/srv/pyconde/local/bin', behavior="prepend"):
        manage_py('collectstatic --noinput -v1')
        with cd(env.root + '/htdocs/static_media/css'):
            srv_run('/srv/pyconde/local/bin/lessc -x {0}'.format('style.{less,css}'))
        manage_py('compress')


@task
def build_statics():
    """
    Compiles files locally.
    """
    less = _find_style_less(functools.partial(local, capture=True))
    local('lessc -x %s' % less)
    local('python manage.py collectstatic --noinput -v1 -i bootstrap -i \'*.less\'')
    local('python manage.py compress --force')


@task
def restart_worker():
    """
    Restarts the gunicorn workers managed by supervisord.
    """
    return supervisorctl('restart pyconde')


@task
def djshell():
    """
    Starts a Django shell on the server.
    """
    return srv_open_shell('%s %s shell' % (
        join(env.root, 'bin', 'python'),
        join(env.proj_root, 'manage.py')))


@task
def loaddata(fixture):
    """
    Loads a given fixture name.
    """
    manage_py('loaddata {0}'.format(fixture))


@task
def build_docs():
    """
    Rebuilds the sphinx documentation on the server.
    """
    with cd(join(env.proj_root, 'docs')):
        srv_run("source ../../bin/activate && make html")
