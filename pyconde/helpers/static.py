# -*- coding: utf8 -*-
from django.contrib.staticfiles.finders import AppDirectoriesFinder
from django.contrib.staticfiles.storage import AppStaticStorage


class AppMediaStorage(AppStaticStorage):
    source_dir = 'media'

class AppMediaDirectoriesFinder(AppDirectoriesFinder):
    storage_class = AppMediaStorage
