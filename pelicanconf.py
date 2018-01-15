#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = u'Bykov Anthony'
SITENAME = u'Blog of Ankarion'
SITEURL = ''

PATH = 'content'
THEME = "notmyidea"

TIMEZONE = 'Europe/Paris'

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

# Blogroll
LINKS = (('Pelican', 'http://getpelican.com/'),
         ('Python.org', 'http://python.org/'),
         ('Jinja2', 'http://jinja.pocoo.org/'),
         ('You can modify those links in your config file', '#'),)

# Social widget
SOCIAL = (
		('Github','https://github.com/ankarion'),
		('Few words about myself','https://ankarion.github.io'),
		('Telegram', 'https://t.me/Ankarion'),
		  )

DEFAULT_PAGINATION = 10
DEFAULT_METADATA = {
		'status': 'draft',
		}


# PLUGINS
PLUGIN_PATHS = ['../pelican-plugins']
PLUGINS = ['assets', 'sitemap', 'gravatar', 'neighbors']

# PLUGINS VARIABLES
SITEMAP = {
		'format':'xml',
		}

# Uncomment following line if you want document-relative URLs when developing
#RELATIVE_URLS = True
