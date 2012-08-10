#!/usr/bin/env python
#-*- coding: ISO-8859-1 -*-

"""
JSON wrapper around different JSON python implementations.
We use simplejson (json), cjson and yajl JSON implementation.
"""

__author__ = "Valentin Kuznetsov <vkuznet@gmail.com>"

MODULE = None
try:
    import yajl
    MODULE = "yajl"
except:
    pass

try:
    import cjson
    MODULE = "cjson"
except:
    pass

import json
if not MODULE: # use default JSON module
    MODULE = "json"

# stick so far with cjson, until yajl will be fully tested
#MODULE = "cjson"
MODULE = "yajl"

def loads(idict, **kwargs):
    """
    Based on default MODULE invoke appropriate JSON decoding API call
    """
    if MODULE == 'json':
        return json.loads(idict, **kwargs)
    elif MODULE == 'cjson':
        return cjson.decode(idict)
    elif MODULE == 'yajl':
        try: # yajl.loads("123") will fail
            res = yajl.loads(idict)
        except: # fall back into default python JSON
            res = json.loads(idict, **kwargs)
        return res
    else:
        raise Exception("Not support JSON module: %s" % MODULE)

def load(source):
    """
    Use json.load for back-ward compatibility, since cjson doesn't
    provide this method. The load method works on file-descriptor
    objects.
    """
    if MODULE == 'json':
        return json.load(source)
    elif MODULE == 'cjson':
        data = source.read()
        return cjson.decode(data)
    elif MODULE == 'yajl':
        return yajl.load(source)
    else:
        raise Exception("Not support JSON module: %s" % MODULE)

def dumps(idict, **kwargs):
    """
    Based on default MODULE invoke appropriate JSON encoding API call
    """
    if MODULE == 'json':
        return json.dumps(idict, **kwargs)
    elif MODULE == 'cjson':
        return cjson.encode(idict)
    elif MODULE == 'yajl':
        return yajl.dumps(idict)
    else:
        raise Exception("JSON module %s is not supported" % MODULE)

def dump(doc, source):
    """
    Use json.dump for back-ward compatibility, since cjson doesn't
    provide this method. The dump method works on file-descriptor
    objects.
    """
    if MODULE == 'json':
        return json.dump(doc, source)
    elif MODULE == 'cjson':
        stj = cjson.encode(doc)
        return source.write(stj)
    elif MODULE == 'yajl':
        return yajl.dump(doc, source)
    else:
        raise Exception("JSON module %s is not supported" % MODULE)

class JSONEncoder(object):
    """
    JSONEncoder wrapper
    """
    def __init__(self, **kwargs):
        self.encoder = json.JSONEncoder(**kwargs)
        if kwargs and kwargs.has_key('sort_keys'):
            self.module = 'default'
        else:
            self.module = MODULE

    def encode(self, idict):
        """Decode JSON method"""
        if self.module == 'cjson':
            return cjson.encode(idict)
        elif self.module == 'yajl':
            return yajl.Encoder().encode(idict)
        return self.encoder.encode(idict)

    def iterencode(self, idict):
        "Encode input dict"
        return self.encoder.iterencode(idict)

class JSONDecoder(object):
    """
    JSONDecoder wrapper
    """
    def __init__(self, **kwargs):
        self.decoder = json.JSONDecoder(**kwargs)
        if kwargs:
            self.module = 'default'
        else:
            self.module = MODULE

    def decode(self, istring):
        """Decode JSON method"""
        if MODULE == 'cjson':
            return cjson.decode(istring)
        elif MODULE == 'yajl':
            return yajl.Decoder().decode(istring)
        return self.decoder.decode(istring)

    def raw_decode(self, istring):
        "Decode given string"
        return self.decoder.raw_decode(istring)
