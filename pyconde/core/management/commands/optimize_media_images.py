import json
import os
import re
import subprocess

from optparse import make_option

from django.conf import settings
from django.core.management import BaseCommand

from easy_thumbnails.conf import settings as thumbnail_settings


thumb_re = re.compile(
    r'^%s(.*)\.\d{1,}x\d{1,}_[-\w]*q([1-9]\d?|100)(_crop)?\.(jpg|png)' %
    thumbnail_settings.THUMBNAIL_PREFIX)


def is_thumbnail(path):
    return thumb_re.match(path) is not None


class Command(BaseCommand):
    help = "Optimizes PNGs and JPEGs stored in the media folder"

    valid_suffixes = ('.png', '.PNG', '.jpeg', '.JPEG', '.jpg', '.JPG')

    option_list = BaseCommand.option_list + (
        make_option(
            '--thumbnails',
            action='store_true',
            dest='only_thumbnails',
            default=False,
            help='Only operate on generated thumbnails'
        ),
        make_option(
            '--state-file',
            action='store',
            dest='state_filepath',
            default=None,
            help='File to (re)store list of already converted files'
        ),
    )

    def handle(self, *args, **options):
        quiet = int(options['verbosity']) == 0
        already_processed = self._load_state(options['state_filepath'])
        save_necessary = False
        for dirpath, dirnames, filenames in os.walk(settings.MEDIA_ROOT):
            for filename in filenames:
                if filename.endswith(self.valid_suffixes):
                    filepath = os.path.join(dirpath, filename)
                    if filepath in already_processed:
                        continue
                    if options['only_thumbnails'] and\
                            thumb_re.match(filename) is None:
                        continue
                    self._optimize(filepath, quiet)
                    already_processed.add(filepath)
                    save_necessary = True
        if save_necessary:
            self._save_state(already_processed, options['state_filepath'])

    def _optimize(self, path, quiet):
        if path.endswith(('.jpg', '.JPG', '.jpeg', '.JPEG')):
            cmd = ['jpegoptim', '--strip-all', path]
            if quiet:
                cmd.insert(1, '--quiet')
        else:
            cmd = ['optipng', path]
            if quiet:
                cmd.insert(1, '-quiet')
        subprocess.check_call(cmd)

    def _load_state(self, state_path):
        result = set()
        if state_path is not None and os.path.exists(state_path):
            with open(state_path) as fp:
                result = set(json.load(fp))
        return result

    def _save_state(self, state, state_path):
        if state_path is not None:
            with open(state_path, 'w+') as fp:
                json.dump(list(state), fp, indent=4)
