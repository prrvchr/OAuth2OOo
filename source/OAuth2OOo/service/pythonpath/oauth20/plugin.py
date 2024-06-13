#!
# -*- coding: utf-8 -*-

"""
╔════════════════════════════════════════════════════════════════════════════════════╗
║                                                                                    ║
║   Copyright (c) 2020 https://prrvchr.github.io                                     ║
║                                                                                    ║
║   Permission is hereby granted, free of charge, to any person obtaining            ║
║   a copy of this software and associated documentation files (the "Software"),     ║
║   to deal in the Software without restriction, including without limitation        ║
║   the rights to use, copy, modify, merge, publish, distribute, sublicense,         ║
║   and/or sell copies of the Software, and to permit persons to whom the Software   ║
║   is furnished to do so, subject to the following conditions:                      ║
║                                                                                    ║
║   The above copyright notice and this permission notice shall be included in       ║
║   all copies or substantial portions of the Software.                              ║
║                                                                                    ║
║   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,                  ║
║   EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES                  ║
║   OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.        ║
║   IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY             ║
║   CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,             ║
║   TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE       ║
║   OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.                                    ║
║                                                                                    ║
╚════════════════════════════════════════════════════════════════════════════════════╝
"""

# FIXME: Some Python package try to log message on stderr who is no available on Windows
import os
import sys
if sys.stderr is None:
    sys.stderr = open(os.devnull, 'w')
# FIXME: We need to force the creation of tab files using the utf8 codec to workaround issues with
# FIXME: the ply package, for systems like Windows that do not have utf8 configured as the default codec.
from calmjs.parse.parsers.optimize import reoptimize_all
reoptimize_all(True)

import js2xml
from js2xml.utils.objects import make
from parsel import Selector
from lxml import etree
from jsonpath_ng import parse
import extruct
from w3lib.html import get_base_url
#from rdflib.plugin import register, Serializer
#register('json-ld', Serializer, 'rdflib_jsonld.serializer', 'JsonLDSerializer')

import json
from six import string_types, text_type
from collections import OrderedDict
import traceback


def parseJson(data, path):
    try:
        result = [m.value for m in parse(path).find(data)]
    except Exception as e:
        results = ((), )
        print("OAuth2Plugin.parseJson() Error: %s" % traceback.format_exc())
    else:
        results = (tuple(result), )
    return results

def javaScript2Xml(data, path, default):
    try:
        tree = js2xml.parse(data)
        result = [js2xml.pretty_print(t) for t in tree.xpath(_getPath(path, default))]
    except Exception as e:
        results = ((), )
        print("OAuth2Plugin.javaScript2Xml() Error: %s" % traceback.format_exc())
    else:
        results = (tuple(result), )
    return results

def xml2Json(data, path, default):
    try:
        tree = etree.XML(data)
        result = [json.dumps(make(t), indent=2) for t in tree.xpath(_getPath(path, default))]
    except Exception as e:
        results = ((), )
        print("OAuth2Plugin.xml2Json() Error: %s" % traceback.format_exc())
    else:
        results = (tuple(result), )
    return results

def javaScript2Json(data, path, default):
    try:
        tree = js2xml.parse(data)
        result = [json.dumps(make(t), indent=2) for t in tree.xpath(_getPath(path, default))]
    except Exception as e:
        results = ((), )
        print("OAuth2Plugin.javaScript2Json() Error: %s" % traceback.format_exc())
    else:
        results = (tuple(result), )
    return results

def splitJson(data, typename, path, separator, default):
    try:
        item = _loadJson(data, path)
        values = _getSplitJson(item, typename, _getSeparator(separator, default))
        if values:
            results = tuple([(k, ) + tuple(v) for k, v in values.items()])
        else:
            result = ((), )
    except Exception as e:
        print("OAuth2Plugin.splitJson() Error: %s" % traceback.format_exc())
        return ((), )
    return results

def flattenJson(data, typename, path, separator, default):
    try:
        item = _loadJson(data, path)
        results = _getFlattenJson(item, typename, _getSeparator(separator, default))
    except Exception as e:
        print("OAuth2Plugin.flattenJson() Error: %s" % traceback.format_exc())
        return ((), )
    return results

def parseData(data, path, baseurl, dtype, default):
    url = _getBaseUrl(baseurl)
    try:
        result = Selector(text=data, type=dtype, base_url=url).xpath(_getPath(path, default)).getall()
    except Exception as e:
        results = ((), )
        print("OAuth2Plugin.parseData() Error: %s" % traceback.format_exc())
    else:
        results = (tuple(result), )
    return results

def extract2Json(data, baseurl, dtype):
    try:
        url = _getBaseUrl(baseurl)
        url = get_base_url(data, url) if url else None
        microdata = extruct.extract(data, base_url=url)
        result = [json.dumps(t, indent=2) for t in microdata.get(dtype, ())]
    except Exception as e:
        results = ((), )
        print("OAuth2Plugin.extract2Json() Error: %s" % traceback.format_exc())
    else:
        results = (tuple(result), )
    return results

# Private method
def _getPath(path, default):
    return text_type(path) if path else default

def _getBaseUrl(baseurl):
    return baseurl if baseurl and isinstance(baseurl, string_types) else None

def _getSeparator(separator, default):
    return default if separator is None else separator

def _loadJson(data, path):
    item = None
    find = True if path and isinstance(path, string_types) else False
    if find:
        for m in parse(path).find(data):
            item = json.loads(m.value)
            break
    if not item:
        item = json.loads(data)
    return item

def _getSplitJson(item, tn, sep, *headers):
    results = OrderedDict()
    if isinstance(item, dict):
        _getSplitDict(item, results, tn, sep, *headers)
    elif isinstance(item, (list, tuple)):
        _getSplitList(item, results, tn, sep, *headers)
    return results

def _getSplitDict(item, results, tn, sep, *headers):
    update, headers = _getHeaders(item, tn, headers)
    for key, value in item.items():
        if not update and key == tn:
            continue
        elif isinstance(value, dict):
            _getSplitDict(value, results, tn, sep, *_updateHeaders(update, key, headers))
        elif isinstance(value, (list, tuple)):
            _getSplitList(value, results, tn, sep, *_updateHeaders(True, key, headers))
        else:
            label = _getLabel(key, sep, headers)
            _addResult(results, label, value)

def _getSplitList(item, results, tn, sep, *headers):
    for value in item:
        if isinstance(value, dict):
            _getSplitDict(value, results, tn, sep, *headers)
        elif isinstance(value, (list, tuple)):
            _getSplitList(value, results, tn, sep, *headers)
        elif headers:
            label = sep.join(headers)
            _addResult(results, label, value)

def _addResult(results, label, value):
    if label not in results:
        results[label] = []
    results[label].append(value)

def _getFlattenJson(item, tn, sep, *headers):
    results = []
    if isinstance(item, dict):
        _getFlattenDict(item, results, tn, sep, *headers)
    elif isinstance(item, (list, tuple)):
        _getFlattenList(item, results, tn, sep, *headers)
    else:
        results.append((sep.join(headers), item))
    return tuple(results)

def _getFlattenDict(item, results, tn, sep, *headers):
    update, headers = _getHeaders(item, tn, headers)
    for key, value in item.items():
        if not update and key == tn:
            continue
        elif isinstance(value, dict):
            _getFlattenDict(value, results, tn, sep, *_updateHeaders(update, key, headers))
        elif isinstance(value, (list, tuple)):
            _getFlattenList(value, results, tn, sep, *_updateHeaders(True, key, headers))
        else:
            results.append((_getLabel(key, sep, headers), value))

def _getFlattenList(item, results, tn, sep, *headers):
    for i, value in enumerate(item):
        key = '[{}]'.format(i +1)
        if isinstance(value, dict):
            _getFlattenDict(value, results, tn, sep, *_updateHeaders(True, key, headers))
        elif isinstance(value, (list, tuple)):
            _getFlattenList(value, results, tn, sep, *_updateHeaders(True, key, headers))
        else:
            results.append((_getLabel(key, sep, headers), value))

def _getHeaders(item, tn, headers):
    update = True
    if tn:
        header = item.get(tn, None)
        update = header is None
        if not update:
            headers = _updateHeaders(True, header, headers)
    return update, headers

def _getLabel(key, sep, headers):
    headers = _updateHeaders(True, key, headers)
    return sep.join(headers) 

def _updateHeaders(update, key, headers):
    if update:
        headers = list(headers)
        headers.append(key)
        headers = tuple(headers) 
    return headers

