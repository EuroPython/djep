import os
from fabric.api import *

def update():
    localroot = os.path.dirname(__file__)
    local('cd %s; pwd' % localroot)
    local('cd %s;epio upload' % localroot)
    local('cd %s;epio django -- syncdb' % localroot)
    local('cd %s;epio django -- migrate' % localroot)

def upgrade():
    localroot = os.path.dirname(__file__)
    update()
    local('cd %s; epio django -- collectstatic --noinput' % localroot)
