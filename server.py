#!/usr/bin/env python
# coding: utf-8

import os
import webbrowser
import SocketServer
import SimpleHTTPServer

os.chdir('html')
Handler = SimpleHTTPServer.SimpleHTTPRequestHandler
httpd = SocketServer.TCPServer(("", 8080), Handler)
webbrowser.open('http://localhost:8080')
httpd.serve_forever()
