#!/usr/bin/env python
# coding: utf-8

import os
import sys
import webbrowser

if sys.version_info.major == 2:
    import SocketServer
    import SimpleHTTPServer
else:
    import socketserver
    import http.server
    SocketServer = socketserver
    SimpleHTTPServer = http.server

os.chdir('html')
Handler = SimpleHTTPServer.SimpleHTTPRequestHandler
SocketServer.TCPServer.allow_reuse_address = True
httpd = SocketServer.TCPServer(("", 8080), Handler)
webbrowser.open('http://localhost:8080')
try:
    httpd.serve_forever()
except KeyboardInterrupt:  # no use
    httpd.server_close()
