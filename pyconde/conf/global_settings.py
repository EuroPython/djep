import os
from django.conf.global_settings import (TEMPLATE_CONTEXT_PROCESSORS,
    STATICFILES_FINDERS)

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
PROJECT_NAME = os.path.split(PROJECT_ROOT)[-1]

DEBUG = TEMPLATE_DEBUG = False

ADMINS = (
    ('Markus Zapke-Gruendemann', 'markus@de.pycon.org'),
    ('Stephan Jaekel', 'steph@rdev.info')
)
MANAGERS = ADMINS

EMAIL_SUBJECT_PREFIX = '[%s] ' % PROJECT_NAME

DEFAULT_FROM_EMAIL = 'info@de.pycon.org'
SERVER_EMAIL = 'info@de.pycon.org'

TIME_ZONE = 'Europe/Berlin'
LANGUAGE_CODE = 'de'

USE_I18N = True
USE_L10N = True

SITE_ID = 1

gettext_noop = lambda s: s
LANGUAGES = (
    ('de', gettext_noop('German')),
    #('en', gettext_noop('English')),
)

MEDIA_URL = '/site_media/'
STATIC_URL = '/static_media/'
ADMIN_MEDIA_PREFIX = '/static_media/admin/'

STATIC_ROOT = os.path.join(PROJECT_ROOT, 'deployed_static_media')

STATICFILES_DIRS = (
    os.path.join(PROJECT_ROOT, 'static_media'),
)

STATICFILES_FINDERS += (
    'pyconde.helpers.static.AppMediaDirectoriesFinder',
    'compressor.finders.CompressorFinder',
)

COMPRESS_CSS_FILTERS = (
    'compressor.filters.css_default.CssAbsoluteFilter',
    'compressor.filters.cssmin.CSSMinFilter',
)

ROOT_URLCONF = '%s.urls' % PROJECT_NAME

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.staticfiles',
    'south',
    'easy_thumbnails',
    'filer',
    'compressor',
    'cms',
    'mptt',
    'menus',
    'sekizai',
    'userprofiles',
    'userprofiles.contrib.accountverification',
    'userprofiles.contrib.emailverification',
    'userprofiles.contrib.profiles',

    'cms.plugins.inherit',
    'cms.plugins.googlemap',
    'cms.plugins.link',
    'cms.plugins.snippet',
    'cms.plugins.twitter',
    'cms.plugins.text',
    'cmsplugin_filer_image',
    'cmsplugin_news',

    'pyconde.accounts',
)

MIDDLEWARE_CLASSES = (
    'pyconde.helpers.middleware.CorrectDomainMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'cms.middleware.page.CurrentPageMiddleware',
    'cms.middleware.user.CurrentUserMiddleware',
    'cms.middleware.toolbar.ToolbarMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS += (
    'django.core.context_processors.request',
    'sekizai.context_processors.sekizai',
)

TEMPLATE_DIRS = (
    os.path.join(PROJECT_ROOT, 'templates'),
)

USERPROFILES_CHECK_UNIQUE_EMAIL = True
USERPROFILES_DOUBLE_CHECK_EMAIL = False
USERPROFILES_DOUBLE_CHECK_PASSWORD = True
USERPROFILES_REGISTRATION_FULLNAME = True
USERPROFILES_USE_ACCOUNT_VERIFICATION = True
USERPROFILES_USE_PROFILE = True
USERPROFILES_INLINE_PROFILE_ADMIN = True
USERPROFILES_USE_PROFILE_VIEW = False
USERPROFILES_REGISTRATION_FORM = 'pyconde.accounts.forms.ProfileRegistrationForm'
USERPROFILES_EMAIL_VERIFICATION_DONE_URL = 'userprofiles_profile_change'

AUTH_PROFILE_MODULE = 'accounts.Profile'

LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

CMS_TEMPLATES = (
    ('cms/default.html', 'Default template'),
)

CMS_LANGUAGE_FALLBACK = False
CMS_MENU_TITLE_OVERWRITE = True
CMS_REDIRECTS = True
CMS_SHOW_START_DATE = False
CMS_SHOW_END_DATE = False
CMS_MODERATOR = False
CMS_SEO_FIELDS = True

THUMBNAIL_PROCESSORS = (
    'easy_thumbnails.processors.colorspace',
    'easy_thumbnails.processors.autocrop',
    'filer.thumbnail_processors.scale_and_crop_with_subject_location',
    'easy_thumbnails.processors.filters',
)


WYM_TOOLS = ",\n".join([
    "{'name': 'Bold', 'title': 'Strong', 'css': 'wym_tools_strong'}",
    "{'name': 'Italic', 'title': 'Emphasis', 'css': 'wym_tools_emphasis'}",
    "{'name': 'Superscript', 'title': 'Superscript', 'css': 'wym_tools_superscript'}",
    "{'name': 'Subscript', 'title': 'Subscript', 'css': 'wym_tools_subscript'}",
    "{'name': 'InsertOrderedList', 'title': 'Ordered_List', 'css': 'wym_tools_ordered_list'}",
    "{'name': 'InsertUnorderedList', 'title': 'Unordered_List', 'css': 'wym_tools_unordered_list'}",
    "{'name': 'Indent', 'title': 'Indent', 'css': 'wym_tools_indent'}",
    "{'name': 'Outdent', 'title': 'Outdent', 'css': 'wym_tools_outdent'}",
    "{'name': 'Undo', 'title': 'Undo', 'css': 'wym_tools_undo'}",
    "{'name': 'Redo', 'title': 'Redo', 'css': 'wym_tools_redo'}",
    "{'name': 'Paste', 'title': 'Paste_From_Word', 'css': 'wym_tools_paste'}",
    "{'name': 'ToggleHtml', 'title': 'HTML', 'css': 'wym_tools_html'}",
    "{'name': 'CreateLink', 'title': 'Link', 'css': 'wym_tools_link'}",
    "{'name': 'Unlink', 'title': 'Unlink', 'css': 'wym_tools_unlink'}",
    "{'name': 'InsertImage', 'title': 'Image', 'css': 'wym_tools_image'}",
    "{'name': 'InsertTable', 'title': 'Table', 'css': 'wym_tools_table'}",
    "{'name': 'Preview', 'title': 'Preview', 'css': 'wym_tools_preview'}",
])

CMSPLUGIN_NEWS_FEED_TITLE = u'PyCon DE 2012-News'
CMSPLUGIN_NEWS_FEED_DESCRIPTION = u'Neuigkeiten rund um die PyCon DE 2012 in Leipzig'
