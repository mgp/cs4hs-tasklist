#!/usr/bin/python2.7

__author__ = 'michael.g.parker@gmail.com (Michael Parker)'

import sys

from google3.apphosting.api import apiproxy_stub
from google3.apphosting.api import apiproxy_stub_map
from google3.apphosting.api import datastore
from google3.apphosting.api import datastore_file_stub
from google3.apphosting.api import users
from google3.apphosting.ext import db
from google3.apphosting.runtime import apiproxy_errors


def AliasModule(orig_name, new_name):
  """Make the given module importable at the new name."""
  orig_bits = orig_name.split('.')
  new_bits = new_name.split('.')
  assert len(orig_bits) == len(new_bits)
  for i in range(1, len(orig_bits) + 1):
    orig_name = '.'.join(orig_bits[0:i])
    new_name = '.'.join(new_bits[0:i])
    sys.modules[new_name] = sys.modules[orig_name]


# We must alias the modules at import time before any project code attempts to
# import the google.appengine modules.
AliasModule('google3.apphosting.api.datastore',
            'google.appengine.api.datastore')
AliasModule('google3.apphosting.ext.db',
            'google.appengine.ext.db')
AliasModule('google3.apphosting.api.users',
            'google.appengine.api.users')
AliasModule('google3.apphosting.runtime.apiproxy_errors',
            'google.appengine.runtime.apiproxy_errors')

