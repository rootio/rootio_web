# -*- coding: utf-8 -*-

# User role
ADMIN = 0 #edit all
NETWORK_ADMIN = 1
STAFF = 2 #edit own stations only
USER = 3 #view only
USER_ROLE = {
    ADMIN: 'admin',
    NETWORK_ADMIN: 'network admin',
    STAFF: 'staff',
    USER: 'user',
}

# User status
INACTIVE = 0
NEW = 1
ACTIVE = 2
USER_STATUS = {
    INACTIVE: 'inactive',
    NEW: 'new',
    ACTIVE: 'active',
}

DEFAULT_USER_AVATAR = 'default.jpg'
