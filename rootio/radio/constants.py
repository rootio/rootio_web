# -*- coding: utf-8 -*-

# Hardcoded program types
#TODO, link these to program dynamics
DEFAULT = 0
NEWS = 1
HOT_HITS = 2
ROUNDTABLE = 3
STRING_LEN = 100

PROGRAM_TYPES = {
    DEFAULT: 'Default',
    NEWS: 'News',
    HOT_HITS: 'Hot Hits',
    ROUNDTABLE: 'Roundtable',
}

#enum for privacy types
PRIVATE = 0
SHARED = 1
PUBLIC = 2
PRIVACY_TYPE = {
    PRIVATE: u'Private',
    SHARED: u'Shared',
    PUBLIC: u'Public',
}

#should probably link to ACCEPT_LANGUAGES in config.py
LANGUAGE_CODES = {
    'en':'English',
    'lg':'Luganda',
    'luo':'Luo',
    'sw':'Swahili'
}