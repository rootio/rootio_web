# -*- coding: utf-8 -*-

# User role
ADMIN = 0 #edit all
NETWORK_ADMIN = 1
NETWORK_USER = 2 #edit own stations only
CONTENT_ADMIN = 3 #view only
CONTENT_USER = 4

USER_ROLE = {
    ADMIN: 'admin',
    NETWORK_ADMIN: 'network admin',
    NETWORK_USER: 'network user',
    CONTENT_ADMIN: 'content admin',
    CONTENT_USER: 'content user',
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

#Network Invitation status
# User status
PENDING = 0
ACCEPTED = 1
REJECTED = 2
INVITATION_STATUS = {
    PENDING: 'pending',
    ACCEPTED: 'accepted',
    REJECTED: 'rejected',
}


DEFAULT_USER_AVATAR = 'default.jpg'
