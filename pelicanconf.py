#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = u'Bykov Anthony'
SITENAME = u'Blog of Ankarion'
SITEURL = ''

PATH = 'content'
STATIC_PATHS = ['extras', 'images']
EXTRA_PATH_METADATA = {
    'extras/android-chrome-192x192.png': {'path': 'android-chrome-192x192.png'},
    'extras/android-chrome-512x512.png': {'path': 'android-chrome-512x512.png'},
    'extras/apple-touch-icon.png': {'path': 'apple-touch-icon.png'},
    'extras/browserconfig.xml': {'path': 'browserconfig.xml'},
    'extras/favicon-16x16.png': {'path': 'favicon-16x16.png'},
    'extras/favicon-32x32.png': {'path': 'favicon-32x32.png'},
    'extras/favicon.ico': {'path': 'favicon.ico'},
    'extras/manifest.json': {'path': 'manifest.json'},
    'extras/mstile-150x150.png': {'path': 'mstile-150x150.png'},
    'extras/safari-pinned-tab.svg': {'path': 'safari-pinned-tab.svg'},
}

THEME = "alchemy"

TIMEZONE = 'Europe/Moscow'

DEFAULT_LANG = u'en'
LOCALE = (
		'usa',   # On Windows
		'en_US.utf8', # On Linux
		)

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None
DISQUS_SITENAME = 'ankarion-blog'

IGNORE_FILES = ['*tags*']

# Blogroll
LINKS = (
		('Github','https://github.com/ankarion'),
		('Telegram', 'https://t.me/Ankarion'),
        ('Python.org', 'http://python.org/'),
		)

# Social widget

SITESUBTITLE = 'A blog about applied SQL/C/C++'
SITEIMAGE = '/images/profile.jpg width=200 height=200'
DESCRIPTION = 'some random text'
ICONS = (
    ('github', 'https://github.com/ankarion'),
)

PYGMENTS_STYLE = 'monokai'
RFG_FAVICONS = True

DEFAULT_PAGINATION = 10
DEFAULT_METADATA = {
		'status': 'draft',
		}


# PLUGINS
PLUGIN_PATHS = ['../pelican-plugins']
PLUGINS = [
		'assets', 'sitemap', 'gravatar', 'neighbors',
		]

# PLUGINS VARIABLES
SITEMAP = {
		'format':'xml',
		}

# Uncomment following line if you want document-relative URLs when developing
#RELATIVE_URLS = True
