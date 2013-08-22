# -*- coding: utf-8 -*-

# Hardcoded program types
#TODO, link these to program dynamics
DEFAULT = 0
NEWS = 1
HOT_HITS = 2
ROUNDTABLE = 3

PROGRAM_TYPES = {
    DEFAULT: 'default',
    NEWS: 'news',
    HOT_HITS: 'hot hits',
    ROUNDTABLE: 'round table',
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