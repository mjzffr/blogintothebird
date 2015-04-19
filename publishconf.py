#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

# This file is only used if you use `make publish` or
# explicitly specify it as your config file.

import os
import sys
sys.path.append(os.curdir)
from pelicanconf import *

SITEURL = 'http://www.erranderr.com/blog'
HOMEURL = 'http://www.erranderr.com'
#RELATIVE_URLS = False

FEED_ALL_ATOM = 'feeds/all.atom.xml'
CATEGORY_FEED_ATOM = 'feeds/cat-%s.atom.xml'
TAG_FEED_ATOM = 'feeds/%s.atom.xml'
FEED_DOMAIN = SITEURL

DELETE_OUTPUT_DIRECTORY = True

IGNORE_FILES = ['.#*', 'test_*.md', 'tmp_*.md',]

# Following items are often useful when publishing

#DISQUS_SITENAME = ""
GOOGLE_ANALYTICS = "UA-45941192-1"
TWITTER_USERNAME = "@impossibus"
TWITTER_WIDGET_ID = 493058448800497664
