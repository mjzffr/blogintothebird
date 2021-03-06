#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = u'Maja Frydrychowicz'
SITENAME = u'err &err'
#GITHUB_URL = 'http://github.com/mjzffr/'
#TWITTER_USERNAME = '@maja_zf'

TIMEZONE = 'America/New_York'
DEFAULT_DATE = 'fs'
DEFAULT_LANG = u'en'
DEFAULT_DATE_FORMAT = "%d %B %Y"

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None

# Blogroll
# LINKS =  (('Pelican', 'http://getpelican.com/'),
#           ('Python.org', 'http://python.org/'),
#           ('Jinja2', 'http://jinja.pocoo.org/'),
#           ('You can modify those links in your config file', '#'),)
LINKS = False
#MENUITEMS = (('Intro', 'http://www.erranderr.com/'),)

DISPLAY_CATEGORIES_ON_MENU = False
DISPLAY_PAGES_ON_MENU = True
PAGE_PATHS = ['pages']
AUTHORS_URL = False
AUTHORS_SAVE_AS = False

# Social widget
#SOCIAL = (('twitter', 'http://twitter.com/maja_zf'),)
TWITTER_BLUB = False
DEFAULT_PAGINATION = 0

# Uncomment following line if you want document-relative URLs when developing
RELATIVE_URLS = True

TYPOGRIFY = True

THEME = "pelican-themes/notmyidea-maja"

MARKDOWN = {
    'extension_configs': {
        'markdown.extensions.codehilite': {'css_class': 'highlight'},
        'markdown.extensions.extra': {},
    },
    'output_format': 'html5',
}


FAVICON = 'theme/images/icons/favicon.png'

MOBILE_CSS_FILE = 'mobile.css'

IGNORE_FILES = ['.#*', 'test_*.md', 'tmp_*.md',]
# presentations dir can contain pdfs, pandoc-generated speaker notes (ideally not just slides)
# Otherwise canonical location for presentations is presentations repo
STATIC_PATHS = ['images', 'presentations']
ARTICLE_EXCLUDES = ['presentations']
