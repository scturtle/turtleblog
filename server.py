#!/usr/bin/env python
# coding: utf-8

import bottle
from os import path


@bottle.route('/:p#.*#')
def serve(p):
    if path.isdir(path.join('html', p)):
        p = path.join(p, 'index.html')
    return bottle.static_file(p, root='html')

if __name__ == '__main__':
    bottle.debug(True)
    bottle.run(reloader=True)
