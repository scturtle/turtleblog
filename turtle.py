#!/usr/bin/env python
# coding: utf-8

import re
import os
import json
import shutil
import jinja2
import markdown
from os import path
from math import log
from datetime import datetime
from collections import defaultdict
try:
    import IPython
    import IPython.nbconvert as nb
except:
    pass


gconf = json.load(open('config.json'))
md = markdown.Markdown(extensions=gconf['markdown config'].split(),
                       output='html5')

env = jinja2.Environment(loader=jinja2.FileSystemLoader('template'),
                         autoescape=True, line_statement_prefix='#')

dateformat = lambda val, fmt='%B {}, %Y': val.strftime(fmt).format(val.day)
env.filters['dateformat'] = dateformat


class Blog:

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


def toMarkdown(filename):
    return md.convert(open(filename).read().decode('utf-8'))


def renderToFile(tofile, template, **params):
    open(tofile, 'w').write(env.get_template(template).render(
                            site_name=gconf['site name'],
                            site_url=gconf['site url'],
                            author=gconf['author'],
                            disqus_shortname=gconf['disqus shortname'],
                            **params).encode('utf-8'))


def copyImg(src_dir, dest_dir):
    img_dir = path.join(src_dir, 'img')
    if path.exists(img_dir):
        shutil.copytree(img_dir, path.join(dest_dir, 'img'))

#=================================================================


def walk(relpath=''):
    p = path.join('blog', relpath)
    to = path.join('html', relpath)
    try:
        os.mkdir(to)
    except:
        pass
    if path.exists(path.join(p, 'config.json')):
        return [per_blog(relpath)]
    else:
        dirs = filter(lambda d: path.isdir(path.join(p, d)), os.listdir(p))
        dirs = [path.join(relpath, d) for d in dirs]
        # gather infomation for analysis tags and pages
        return sum(map(walk, dirs), [])


def per_blog(relpath=''):
    p = path.join('blog', relpath)
    to = path.join('html', relpath)
    conf = json.load(open(path.join(p, 'config.json')))

    date = datetime.strptime(conf['date'], '%Y-%m-%d %H:%M')
    # fix url problem in Windows
    url = '/{}/'.format(relpath).replace('\\', '/')

    # render
    ipynb = os.path.exists(path.join(p, 'blog.ipynb'))
    if ipynb:
        config = IPython.Config(
            {'HTMLExporter': {'default_template': 'basic'}})
        html = nb.export_html(
            open(path.join(p, 'blog.ipynb')), config=config)[0]
        html = html.replace('\n</pre>', '</pre>')
        content = u'<div class="ipynb">\n{}\n</div>'.format(html)
    else:
        content = toMarkdown(path.join(p, 'blog.md'))

    # render template
    renderToFile(path.join(to, 'index.html'), 'blog.html',
                 title=conf['title'],
                 date=date,
                 tags=conf['tags'].split(),
                 enable_mathjax=conf.get('enable mathjax', False),
                 ipynb=ipynb,
                 content=content)
    copyImg(p, to)

    # return blog information
    return Blog(title=conf['title'],
                url=url,
                content=content,
                tags=conf['tags'].split(),
                date=date)


def blogs():
    shutil.rmtree('html', ignore_errors=True)
    infos = walk()
    shutil.copytree('static', 'html/static')
    return infos

#====================================================


def paging(infos):
    shutil.rmtree('html/page', ignore_errors=True)
    infos.sort(key=lambda d: d.date, reverse=True)

    # dividing list into groups of N
    N = gconf['number of blogs per page']
    pages = [infos[i:i + N] for i in range(0, len(infos), N)]
    if not pages:
        pages = [[]]

    # render per page
    os.mkdir('html/page')
    for idx, blogs in enumerate(pages):
        is_last = (idx == len(pages) - 1)
        renderToFile('html/page/{}.html'.format(idx + 1), 'pagination.html',
                     blogs=blogs, idx=idx, is_last=is_last)

    # generate index.html
    open('html/index.html', 'w').write(open('html/page/1.html').read())

#====================================================


def archive(infos):
    ar = defaultdict(list)
    for b in infos:
        ar[b.date.year].append(b)
    for y in ar:
        ar[y].sort(key=lambda b: b.date, reverse=True)
    renderToFile('html/archive.html', 'archive.html', ar=ar)

#====================================================


def tags(infos):
    shutil.rmtree('html/tags', ignore_errors=True)
    os.mkdir('html/tags')

    # invert index
    tags = defaultdict(lambda: {'count': 0, 'blogs': []})
    for b in infos:
        for t in b.tags:
            tags[t]['count'] += 1
            tags[t]['blogs'].append(b)

    # compute tags cloud
    cloud = [[k, 100.0 + 20 * log(tags[k]['count'])] for k in tags]
    cloud.sort(key=lambda t: t[0])

    renderToFile('html/tags/index.html', 'tagcloud.html', tags=cloud)

    # tag page
    for t in tags:
        tags[t]['blogs'].sort(key=lambda b: b.date, reverse=True)
        renderToFile('html/tags/{}.html'.format(t), 'tag.html',
                     tag=t, blogs=tags[t]['blogs'])

#=============================================================


def pages():
    dirs = filter(lambda d: path.isdir(path.join('page', d)),
                  os.listdir('page'))
    for d in dirs:
        p = path.join('page', d)
        conf = json.load(open(path.join(p, 'config.json')))
        to = path.join('html', d)
        os.mkdir(to)

        content = toMarkdown(path.join(p, 'page.md'))
        renderToFile(path.join(to, 'index.html'), 'page.html',
                     title=conf['title'], content=content)
        copyImg(p, to)


def feed(infos):
    blogs = infos[:10]
    for b in blogs:
        # black magic to fix url
        b.content = re.sub(r'(?<=src=.)(?!(https?:|/))', b.url, b.content)
    renderToFile('html/atom.xml', 'atom.xml', now=datetime.now(), blogs=blogs)

if __name__ == '__main__':
    infos = blogs()
    paging(infos)
    archive(infos)
    tags(infos)
    pages()
    feed(infos)
