#!/usr/bin/env python
# coding: utf-8

import os
import sys
import bottle
from os import path


@bottle.route('/:p#.*#')
def serve(p):
    if path.isdir(path.join('html', p)):
        p = path.join(p, 'index.html')
    return bottle.static_file(p, root='html')

if __name__ == '__main__':
    bottle.debug(True)
    if sys.platform.startswith('darwin'):
        os.system('open -g ' + 'http://localhost:8080')
    elif sys.platform.startswith('win'):
        os.system('start ' + 'http://localhost:8080')
    bottle.run(reloader=True)
