import mimetypes
import os
import posixpath
import shutil
import urllib
from http.server import BaseHTTPRequestHandler, HTTPServer
import markdown
import pymdownx.superfences
import pymdownx.arithmatex as arithmatex

__version__ = '1.3.0'


class MarkdownHTTPRequestHandler(BaseHTTPRequestHandler):
    content_type = 'text/html;charset=utf-8'
    encoding = 'utf8'
    favicon = 'favicon.ico'
    server_version = "MarkdownHTTP/" + __version__

    def do_GET(self):
        path = self.path[1:].split('?')[0].split('#')[0]
        path = urllib.parse.unquote(path)
        print(path)
        if path in ['css/markdown.css','favicon.ico','css/style.css']:
            return self.serve_file(path, True)

        if not os.path.isdir(self.server.directory):
            return self.resp_file(self.server.directory)

        full_path = os.path.join(self.server.directory, path)

        if not os.path.exists(full_path):
            self.send_error(404, "File not found")
        # file.
        return self.resp_file(full_path)

    def resp_file(self, full_path: str):
        # directory.
        if os.path.isdir(full_path):
            # index;
            for index in self.server.indexs:
                index_file = os.path.join(full_path, index)
                if os.path.exists(index_file):
                    return self.resp_file(index_file)
            return self.make_html([],full_path = full_path)
        # md file.
        if full_path.lower().endswith('.md'):
            self.markdown_file(full_path)
        else:
            self.serve_file(full_path)

    def make_sidebar(self, full_path: str):
        parent_directory = full_path
        if os.path.isfile(full_path):
            parent_directory = os.path.dirname(full_path)
        
        parent_directory = parent_directory.replace("\\","/")
        path = parent_directory.lower().replace(self.server.directory.lower(),"").strip("/")

        pages = []
        folders = []        
        for entry in os.listdir(parent_directory):
            a_tag = '<a href="/{}">{}</a>'.format(entry, entry)
            if path:
                a_tag = '<a href="/{}/{}">{}</a>'.format(path, entry, entry)
            
            entry_full = os.path.join(parent_directory, entry)
            if os.path.isfile(entry_full):
                pages.append('<li class="page"><i class="fa fa-file" aria-hidden="true"></i>{}</li>'.format(a_tag))
            else:
                folders.append('<li class="folder"><i class="fa fa-folder" aria-hidden="true"></i>{}</li>'.format(a_tag))
        
        content = []
        content.extend(['<div class="path">', 
        '<i class="fa fa-home fa-fw" aria-hidden="true"></i><a href="/">Home</a>'])
        paths = path.split('/')
        if len(paths)>1:          
            content.append('<a href="/{}"><i class="fa fa-ellipsis-h fa-fw" aria-hidden="true"></i>/</a>'.format('/'.join(paths[0:-1])))
        
        content.append('</div>')

        content.append('<div><ul>')
        content.extend(folders)
        content.extend(pages)
        content.append('</ul></div>')
        return content

    def make_html(self, content, full_path=None,last_modified=None):
        full_page = [
            "<!doctype html>",
            "<html><head>",
        ]
        full_page.extend(self.header_content())
        full_page.extend(["</head>", '<body>'])
        full_page.extend(['<div class="layout">', '<div class="layout-sidebar">'])
        full_page.extend(self.make_sidebar(full_path))
        full_page.extend(['</div>','<div class="layout-main markdown">'])
        full_page.extend(content)
        full_page.extend(["</div>", '</div>'])
        full_page.append("</body></html>")

        text = "\n".join(full_page)
        self.send_response(200)
        self.send_header("Content-type", self.content_type)

        if last_modified is not None:
            self.send_header(
                "Last-Modified", self.date_time_string(last_modified))

        #self.send_header("Content-Length", len(text.encode(self.encoding)))
        self.end_headers()
        self.wfile.write(text.encode(self.encoding))

    def markdown_file(self, full_path):
        with open(full_path, 'r', encoding='UTF-8') as f:
            fs = os.fstat(f.fileno())
            return self.make_html(
                [markdown.markdown(f.read(),
                                   extensions=['toc', 'meta',
                                               'pymdownx.betterem',  # pip install pymdown-extensions
                                               'pymdownx.superfences',
                                               'pymdownx.arithmatex',
                                               'pymdownx.inlinehilite',
                                               'pymdownx.tabbed',
                                               'pymdownx.tasklist',
                                               'markdown.extensions.footnotes',
                                               'markdown.extensions.attr_list',
                                               'markdown.extensions.def_list',
                                               'markdown.extensions.tables',
                                               'markdown.extensions.abbr',
                                               'markdown.extensions.md_in_html',
                                               ],
                                   extension_configs={
                                       'pymdownx.superfences': {
                                           'custom_fences': [
                                               {
                                                   'name': 'mermaid',
                                                   'class': 'mermaid',
                                                   'format': pymdownx.superfences.fence_div_format
                                               }
                                           ]
                                       },
                                       'pymdownx.inlinehilite': {
                                           'custom_inline': [
                                               {
                                                   'name': 'math',
                                                   'class': 'arithmatex',
                                                   'format': arithmatex.inline_mathjax_format
                                               }
                                           ]
                                       },
                                       'pymdownx.tasklist': {
                                           'custom_checkbox': True,
                                           'clickable_checkbox': False
                                       }
                },
                )],
                full_path=full_path,
                last_modified=fs.st_mtime
            )

    def header_content(self):
        return [
            '<link rel="stylesheet" href="/css/markdown.css"></link>',
            '<link rel="stylesheet" href="/css/style.css"></link>',
            '<link rel="stylesheet" href="https://cdn.bootcdn.net/ajax/libs/font-awesome/5.15.3/css/all.min.css"></link>',
            '<script src="https://unpkg.com/mermaid@8.6.4/dist/mermaid.min.js"></script>',
            '<script src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.0/MathJax.js"></script>',
            '''
            <script>
            MathJax.Hub.Config({
              config: ["MMLorHTML.js"],
              jax: ["input/TeX", "output/HTML-CSS", "output/NativeMML"],
              extensions: ["MathMenu.js", "MathZoom.js"]
            });
            </script>''',
        ]


    def redirect(self, location, code=302):
        text = '''<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">
        <title>Redirecting...</title>
        <h1>Redirecting...</h1>
        <p>You should be redirected automatically to target URL: 
        <a href="{}">{}</a>.  If not click the link.
        '''.format(location, location)
        self.send_response(code)
        self.send_header("Content-type", self.content_type)
        self.send_header("Content-Length", len(text))
        self.send_header("Location", location)
        self.end_headers()
        self.wfile.write(text.encode(self.encoding))

    def serve_file(self, filename, local_file: bool = False):
        """
        Returns a 200 response with the content of the filename (which is
        relative to this file), and the given content type.
        """
        rel_path = filename
        if local_file:
            rel_path = os.path.join(os.path.dirname(__file__), filename)
        content_type = self.guess_type(filename)
        with open(rel_path, 'rb') as f:
            self.send_response(200)
            self.send_header("Content-type", content_type)
            fs = os.fstat(f.fileno())
            #self.send_header("Content-Length", str(fs[6]))
            self.send_header("Last-Modified", self.date_time_string(fs.st_mtime))
            self.end_headers()

            shutil.copyfileobj(f, self.wfile)

    def guess_type(self, path):
        base, ext = posixpath.splitext(path)
        if ext in self.extensions_map:
            return self.extensions_map[ext]
        ext = ext.lower()
        if ext in self.extensions_map:
            return self.extensions_map[ext]
        else:
            return self.extensions_map['']

    if not mimetypes.inited:
        mimetypes.init()  # try to read system mime.types
    extensions_map = mimetypes.types_map.copy()
    extensions_map.update({
        '': 'application/octet-stream',  # Default
        '.py': 'text/plain',
        '.c': 'text/plain',
        '.h': 'text/plain',
    })


class MarkdownHTTPServer(HTTPServer):
    handler_class = MarkdownHTTPRequestHandler

    def __init__(self, server_address, directory: str, indexs: str):
        self.directory = directory.replace("\\","/")
        self.indexs = indexs.split(',')
        try:
            super().__init__(
                server_address, self.handler_class
            )
        except TypeError:
            # Python 2.7 will cause a type error, and in addition
            # HTTPServer is an old-school class object, so use the old
            # inheritance way here.
            HTTPServer.__init__(self, server_address, self.handler_class)


def directory_html(directory: str):
    html = '''
    <!--fa fa-folder-open    file:fa-file  fa-markdown  <i class="fa fa fa-bars" aria-hidden="true"></i> https://fontawesome.com/icons?d=gallery&q=markdown-->
    <div id="directory">
        <div id="path">
            <i class="fa fa-home fa-fw" aria-hidden="true"></i>
            <a href="/">Home</a>&nbsp;&nbsp;»&nbsp;&nbsp;<a href="/Misc">Misc</a> 
        </div>
        <div id="menu">
            <ul>		
                <li class="folder">
                    <i class="fa fa-folder" aria-hidden="true"></i>
                    <a href="/Misc">Misc</a>
                </li>		 
                <li class="page">
                    <i class="fa fa-file" aria-hidden="true"></i>
                    <a href="/Structure">Structure</a>
                </li>
            </ul>
        </div>
	</div>
    '''


def run(host='', port=8080, directory=os.getcwd(), indexs='index.html,index.md,readme.md'):
    if not directory:
        directory = os.getcwd()
    if not indexs:
        indexs = 'index.html,index.md,readme.md'

    server_address = (host, port)
    httpd = MarkdownHTTPServer(server_address, directory, indexs)
    print("Serving from http://{}:{}/".format(host, port))
    httpd.serve_forever()
