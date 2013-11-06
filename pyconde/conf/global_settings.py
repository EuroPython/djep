# -*- encoding: UTF-8 -*-
import os
from django.conf.global_settings import (TEMPLATE_CONTEXT_PROCESSORS,
    STATICFILES_FINDERS)

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
PROJECT_NAME = os.path.split(PROJECT_ROOT)[-1]

DEBUG = TEMPLATE_DEBUG = False
INTERNAL_IPS = ('127.0.0.1',)
DEBUG_TOOLBAR_CONFIG = {'INTERCEPT_REDIRECTS': False}

ADMINS = ()
MANAGERS = ADMINS

EMAIL_SUBJECT_PREFIX = '[%s] ' % PROJECT_NAME

DEFAULT_FROM_EMAIL = 'noreply@ep14.org'
SERVER_EMAIL = 'noreply@ep14.org'

TIME_ZONE = 'Europe/Berlin'
LANGUAGE_CODE = 'de'

USE_I18N = True
USE_L10N = True

SITE_ID = 1

ugettext = lambda s: s
LANGUAGES = (
    ('de', ugettext('German')),
    ('en', ugettext('English')),
)

MEDIA_URL = '/site_media/'
STATIC_URL = '/static_media/'

STATICFILES_DIRS = (
    os.path.join(PROJECT_ROOT, 'static_media'),
)

FIXTURE_DIRS = (
    os.path.join(PROJECT_ROOT, 'fixtures'),
)

STATICFILES_FINDERS += (
    'pyconde.helpers.static.AppMediaDirectoriesFinder',
    'compressor.finders.CompressorFinder',
)

COMPRESS_CSS_FILTERS = (
    'compressor.filters.css_default.CssAbsoluteFilter',
    'compressor.filters.cssmin.CSSMinFilter',
)

COMPRESS_PRECOMPILERS = (
   ('text/less', 'lessc -x {infile} {outfile}'),
)

ROOT_URLCONF = '%s.urls' % PROJECT_NAME

INSTALLED_APPS = (
    # Skins
    'pyconde.skins.ep14',
    'pyconde.skins.default',

    'djangocms_admin_style',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.staticfiles',
    'django.contrib.markup',
    'crispy_forms',
    'south',
    'easy_thumbnails',
    'filer',
    'compressor',
    'djangocms_text_ckeditor',  # must be before 'cms'!
    'cms',
    'cms.stacks',
    'mptt',
    'menus',
    'sekizai',
    'userprofiles',
    'userprofiles.contrib.accountverification',
    'userprofiles.contrib.emailverification',
    'userprofiles.contrib.profiles',
    'taggit',
    'haystack',
    #'tinymce', # If you want tinymce, add it in the settings.py file.
    'django_gravatar',
    'social_auth',

    'cms.plugins.inherit',
    'cms.plugins.googlemap',
    'cms.plugins.link',
    'cms.plugins.snippet',
    #'cms.plugins.twitter',
    #'cms.plugins.text',
    'cmsplugin_filer_image',
    #'cmsplugin_news',

    # Symposion apps
    'pyconde.conference',
    'pyconde.speakers',
    'pyconde.proposals',
    'pyconde.sponsorship',

    # Custom apps
    'pyconde.accounts',
    'pyconde.attendees',
    'pyconde.events',
    'pyconde.reviews',
    'pyconde.schedule',
    'pyconde.search',
    'pyconde.helpers',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'cms.middleware.page.CurrentPageMiddleware',
    'cms.middleware.user.CurrentUserMiddleware',
    'cms.middleware.toolbar.ToolbarMiddleware',
    'cms.middleware.language.LanguageCookieMiddleware',
    'social_auth.middleware.SocialAuthExceptionMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS += (
    'django.core.context_processors.debug',
    'django.core.context_processors.request',
    'sekizai.context_processors.sekizai',
    'pyconde.conference.context_processors.current_conference',
    'pyconde.reviews.context_processors.review_roles',
    'pyconde.context_processors.less_settings',
    'social_auth.context_processors.social_auth_backends',
)

TEMPLATE_DIRS = (
    os.path.join(PROJECT_ROOT, 'skins', 'default'),
    os.path.join(PROJECT_ROOT, 'skins', 'ep14'),
)

USERPROFILES_CHECK_UNIQUE_EMAIL = True
USERPROFILES_DOUBLE_CHECK_EMAIL = False
USERPROFILES_DOUBLE_CHECK_PASSWORD = True
USERPROFILES_REGISTRATION_FULLNAME = True
USERPROFILES_USE_ACCOUNT_VERIFICATION = True
USERPROFILES_USE_EMAIL_VERIFICATION = True
USERPROFILES_USE_PROFILE = True
USERPROFILES_INLINE_PROFILE_ADMIN = True
USERPROFILES_USE_PROFILE_VIEW = False
USERPROFILES_REGISTRATION_FORM = 'pyconde.accounts.forms.ProfileRegistrationForm'
USERPROFILES_PROFILE_FORM = 'pyconde.accounts.forms.ProfileForm'
USERPROFILES_EMAIL_VERIFICATION_DONE_URL = 'userprofiles_profile_change'

AUTH_PROFILE_MODULE = 'accounts.Profile'

LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

CMS_TEMPLATES = (
    ('cms/default.html', 'Default template'),
    ('cms/frontpage.html', 'Frontpage template'),
    ('cms/page_templates/fullpage.html', 'Full page width (schedule, ...)'),
)

# Docs at https://django-cms.readthedocs.org/en/develop/getting_started/configuration.html#cms-languages
CMS_LANGUAGES = {
    1: [
        {
            'code': 'en',
            'name': ugettext('English'),
            'public': True,
            'hide_untranslated': True,
        },
        {
            'code': 'de',
            'name': ugettext('German'),
            'public': True,
        },
    ],
    'default': {
        'fallbacks': ['en', 'de'],
        'hide_untranslated': False,
    }
}

THUMBNAIL_PROCESSORS = (
    'easy_thumbnails.processors.colorspace',
    'easy_thumbnails.processors.autocrop',
    'filer.thumbnail_processors.scale_and_crop_with_subject_location',
    'easy_thumbnails.processors.filters',
)
THUMBNAIL_SIZE = 100

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

CMSPLUGIN_NEWS_FEED_TITLE = u'PyCon DE 2013-News'
CMSPLUGIN_NEWS_FEED_DESCRIPTION = u'Neuigkeiten rund um die PyCon DE 2013 in Köln'
CONFERENCE_ID = 1

ATTENDEES_CUSTOMER_NUMBER_START = 20000
ATTENDEES_PRODUCT_NUMBER_START = 1000

PROPOSALS_SUPPORT_ADDITIONAL_SPEAKERS = True
PROPOSALS_TYPED_SUBMISSION_FORMS = {
    'tutorial': 'pyconde.proposals.forms.TutorialSubmissionForm',
    'talk': 'pyconde.proposals.forms.TalkSubmissionForm',
}
PROPOSAL_LANGUAGES = (
    ('de', ugettext('German')),
    ('en', ugettext('English')),
)

LESS_USE_DYNAMIC_IN_DEBUG = True

SCHEDULE_CACHE_SCHEDULE = True

# Search configuration
#    If no other search backend is specified, Whoosh is used to make the setup
#    as simple as possible. In production we will be using a Lucene-based
#    backend like SOLR or ElasticSearch.
HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.whoosh_backend.WhooshEngine',
        'PATH': os.path.join(PROJECT_ROOT, 'whoosh_index'),
        'STORAGE': 'file',
        'INCLUDE_SPELLING': True,
        'BATCH_SIZE': 100,
    }
}

# Disable south migrations during unittests
SOUTH_TESTS_MIGRATE = False

TINYMCE_DEFAULT_CONFIG = {
    'theme': 'advanced',
    'relative_urls': False,
    'theme_advanced_resizing': True,
    'theme_advanced_buttons1_add': 'forecolor,backcolor',
    'style_formats': [
        {'title': u'Heading 2 (alternative)', 'block': 'h2', 'classes': 'alt'},
        {'title': u'Heading 3 (alternative)', 'block': 'h3', 'classes': 'alt'},
    ]
}

ACCOUNTS_FALLBACK_TO_GRAVATAR = True

# For Elasticsearch you can use for instance following configuration in your
# settings.py.
# HAYSTACK_CONNECTIONS = {
#     'default': {
#         'ENGINE': 'pyconde.search.backends.elasticsearch.Engine',
#         'URL': 'http://127.0.0.1:9200/',
#         'INDEX_NAME': 'pyconde2013',
#     }
# }

SOCIAL_AUTH_PIPELINE = (
    'social_auth.backends.pipeline.social.social_auth_user',
    'social_auth.backends.pipeline.user.get_username',
    'social_auth.backends.pipeline.user.create_user',
    'social_auth.backends.pipeline.social.associate_user',
    'social_auth.backends.pipeline.social.load_extra_data',
    'social_auth.backends.pipeline.user.update_user_details',
    'social_auth.backends.pipeline.misc.save_status_to_session',
    'pyconde.accounts.pipeline.show_request_email_form',
    'pyconde.accounts.pipeline.create_profile',
)

LOGIN_ERROR_URL = '/accounts/login/'

GITHUB_APP_ID = os.environ.get('GITHUB_APP_ID')
GITHUB_API_SECRET = os.environ.get('GITHUB_API_SECRET')
GITHUB_EXTENDED_PERMISSIONS = ['user:email']
TWITTER_CONSUMER_KEY = os.environ.get('TWITTER_CONSUMER_KEY')
TWITTER_CONSUMER_SECRET = os.environ.get('TWITTER_CONSUMER_SECRET')
GOOGLE_OAUTH2_CLIENT_ID = os.environ.get('GOOGLE_OAUTH2_CLIENT_ID')
GOOGLE_OAUTH2_CLIENT_SECRET = os.environ.get('GOOGLE_OAUTH2_CLIENT_SECRET')
FACEBOOK_APP_ID = os.environ.get('FACEBOOK_APP_ID')
FACEBOOK_API_SECRET = os.environ.get('FACEBOOK_API_SECRET')

AUTHENTICATION_BACKENDS = ['django.contrib.auth.backends.ModelBackend']
if GITHUB_APP_ID and GITHUB_API_SECRET:
    AUTHENTICATION_BACKENDS.insert(-1, 'social_auth.backends.contrib.github.GithubBackend')
if TWITTER_CONSUMER_KEY and TWITTER_CONSUMER_SECRET:
    AUTHENTICATION_BACKENDS.insert(-1, 'social_auth.backends.twitter.TwitterBackend')
if FACEBOOK_API_SECRET and FACEBOOK_APP_ID:
    AUTHENTICATION_BACKENDS.insert(-1, 'social_auth.backends.facebook.FacebookBackend')
if GOOGLE_OAUTH2_CLIENT_SECRET and GOOGLE_OAUTH2_CLIENT_ID:
    AUTHENTICATION_BACKENDS.insert(-1, 'social_auth.backends.google.GoogleOAuth2Backend')

PAYMILL_PRIVATE_KEY = os.environ.get('PAYMILL_PRIVATE_KEY')
PAYMILL_PUBLIC_KEY = os.environ.get('PAYMILL_PUBLIC_KEY')

PAYMILL_TRANSACTION_DESCRIPTION = 'EuroPython 2014: Invoice {purchase_pk}'

PAYMENT_METHODS = set(['invoice', 'creditcard'])

PURCHASE_NUMBER_FORMAT = 'EP14-{0:05d}'
PURCHASE_EXPORT_RECIPIENTS = []
PURCHASE_EXPORT_SUBJECT = 'Purchase-export: {purchase_number}'
PURCHASE_TERMS_OF_USE_URL = "https://ep14.org/participate/register/terms/"

EXPORT_SECRET_KEY = os.environ.get('EXPORT_SECRET_KEY', '')  # Set this for production


CHILDREN_DATA_DISABLED = True
