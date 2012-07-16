#!/usr/bin/env python
# coding: utf-8

import jinja2
import os, shutil, json
from markdown import markdown
from os import path
from datetime import datetime
from pprint import pprint
from collections import defaultdict
from math import log
import re

env = jinja2.Environment(loader = jinja2.FileSystemLoader('template'),
                         autoescape = True,
                         line_statement_prefix = '#',
                         #line_comment_prefix = '##'
                         )

def dateformat(value, format_str='%B %d, %Y'):
    return value.strftime(format_str)

env.filters['dateformat'] = dateformat

gconf = json.load(file('config.json'))

class Blog:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

##################################################################

def walk(relpath=''):
    p = path.join('blog', relpath)
    to = path.join('html', relpath)
    os.mkdir(to)
    if path.exists(path.join(p, 'config.json')):
        return [per_blog(relpath)]
    else:
        dirs = filter(lambda d: path.isdir(path.join(p,d)),
                os.listdir(p))
        dirs = [ path.join(relpath, d) for d in dirs ]
        # gather infomation for analysis tags and pages
        return sum(map(walk, dirs), [])

def per_blog(relpath=''):
    # config
    p = os.path.join('blog', relpath)
    conf = json.load(file(path.join(p,'config.json')))
    to = os.path.join('html', relpath)

    date = datetime.strptime(conf['date'], '%Y-%m-%d %H:%M')
    # fix url problem in Windows
    url = '/{0}/'.format(relpath).replace('\\','/')

    # render markdown
    md = file(path.join(p,'blog.md')).read().decode('utf-8')
    content = markdown(md, gconf['markdown config'].split())

    # render template
    tofile = path.join(to, 'index.html')
    with file(tofile,'w') as f:
        f.write(env.get_template('blog.html').render(
            site_name = gconf['site name'],
            disqus_shortname = gconf['disqus shortname'],
            title = conf['title'],
            date = date,
            enable_mathjax = 'enable mathjax' in conf and
                               conf['enable mathjax'],
            content = content
            ).encode('utf-8'))

    # copy img
    img_dir = path.join(p, 'img')
    if path.exists(img_dir):
        shutil.copytree(img_dir, path.join(to, 'img'))

    # return blog information
    return Blog(title = conf['title'],
                url = url,
                content = content,
                tags = conf['tags'].split(),
                date = date)

def blogs():
    shutil.rmtree('html', ignore_errors=True)
    infos = walk()
    shutil.copytree('static', 'html/static')
    return infos

#====================================================

def paging(infos):
    shutil.rmtree('html/page',ignore_errors=True)
    infos.sort(key = lambda d: d.date, reverse = True)
    # dividing list into groups of N
    N = gconf['number of blogs per page']
    pages = [infos[i:i+N] for i in range(0, len(infos), N)]
    if not pages:
        pages = [[]]
    # render per page
    os.mkdir('html/page')
    for idx, blogs in enumerate(pages):
        is_last = (idx == len(pages)-1)
        url = path.join('html/page', str(idx+1))
        os.mkdir(url)
        fn = path.join(url, 'index.html')
        with file(fn, 'w') as f:
            f.write( env.get_template('pagination.html').render(
            site_name = gconf['site name'],
            blogs = blogs, idx = idx, is_last = is_last
            ).encode('utf-8'))

    # generate index.html
    with file('html/index.html', 'w') as f:
        f.write(file('html/page/1/index.html').read())

#====================================================

def tags(infos):
    shutil.rmtree('html/tags',ignore_errors=True)
    os.mkdir('html/tags')

    # invert index
    tags = defaultdict(lambda:{'count':0,'blogs':[]})
    for b in infos:
        for t in b.tags:
            tags[t]['count']+=1
            tags[t]['blogs'].append(b)

    # compute tags cloud
    cloud = [[k, 100.0+20*log(tags[k]['count'])] for k in tags]
    cloud.sort(key = lambda t: t[0])

    with file('html/tags/index.html', 'w') as f:
        f.write( env.get_template('tagcloud.html').render(
            site_name = gconf['site name'],
            tags = cloud
            ).encode('utf-8'))

    # tag page
    for t in tags:
        d = 'html/tags/{0}'.format(t)
        os.mkdir(d)
        f = file(path.join(d,'index.html'), 'w')
        tags[t]['blogs'].sort(key = lambda b: b.date, reverse = True)

        f.write( env.get_template('tag.html').render(
            site_name = gconf['site name'],
            tag = t, blogs = tags[t]['blogs']
            ).encode('utf-8'))

        f.close()

#=============================================================

def pages():
    dirs = filter(lambda d: path.isdir(path.join('page',d)),
            os.listdir('page'))
    for d in dirs:
        p = path.join('page', d)
        conf = json.load(file(path.join(p,'config.json')))
        to = path.join('html', d)
        os.mkdir(to)

        md = file(path.join(p,'page.md')).read().decode('utf-8')
        content = markdown(md, gconf['markdown config'].split())

        with file(path.join(to, 'index.html'), 'w') as f:
            f.write( env.get_template('page.html').render(
                site_name = gconf['site name'],
                title = conf['title'],
                content = content
                ).encode('utf-8'))
        # copy img
        img_dir = path.join(p, 'img')
        if path.exists(img_dir):
            shutil.copytree(img_dir, path.join(to, 'img'))

def feed(infos):
    blogs = infos[:10]
    for b in blogs:
        # black magic to fix url
        b.content = re.sub(r'(?<=src=.)(?=[^/])', b.url, b.content)
    with file('html/atom.xml', 'w') as f:
        f.write( env.get_template("atom.xml").render(
            site_name = gconf['site name'],
            site_url = gconf['site url'],
            author = gconf['author'],
            now = datetime.now(),
            blogs = blogs
            ).encode('utf-8'))

if __name__=='__main__':
    infos = blogs()
    paging(infos)
    tags(infos)
    pages()
    feed(infos)
