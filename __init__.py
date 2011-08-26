"""
Inspired in Django-Tagging.

Copyright 2011, Harrington Joseph
http://www.hjoseph.com
hello@hjoseph.com

Licensed under the MIT

Permission is hereby granted, free of charge, to any
person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the
Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the
Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice
shall be included in all copies or substantial portions of
the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY
KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS
OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR
OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

from blah.models import CommentDescriptor

STATUS = "dev"
VERSION = "0.0.1"

def get_version():
	return "%s.%s" % (STATUS, VERSION)

__version__ = get_version()

_registry = []


def register(model, attr_name = "comments"):
	if model not in _registry:
		if hasattr(model, attr_name):
			raise AttributeError ('The model %s already has the attribute %s' % (model._meta.object_name, attr_name))
		setattr(model, attr_name, CommentDescriptor())
		_registry.append(model)