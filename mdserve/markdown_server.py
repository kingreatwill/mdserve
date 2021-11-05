import mimetypes
import os
import posixpath
import shutil
import urllib
from http.server import BaseHTTPRequestHandler, HTTPServer
import markdown
import pymdownx.superfences
import pymdownx.arithmatex as arithmatex
from operator import itemgetter, attrgetter
__version__ = '1.4.0'


def extensions_icon_map_init():
    icon_map = {}
    rel_path = os.path.join(os.path.dirname(__file__), 'icons')
    for entry in os.listdir(rel_path):
        if entry.startswith('file_type_') or entry.startswith('folder_type_'):
            ext = '{}'.format(entry.replace('.svg', ''))
            icon_map[ext] = entry
    return icon_map


class MarkdownHTTPRequestHandler(BaseHTTPRequestHandler):
    content_type = 'text/html;charset=utf-8'
    encoding = 'utf8'
    favicon = 'favicon.ico'
    server_version = "MarkdownHTTP/" + __version__

    def do_GET(self):
        path = self.path[1:].split('?')[0].split('#')[0]
        path = urllib.parse.unquote(path)
        if path.startswith('css/') or path.startswith('icons/') or path == 'favicon.ico':
            return self.serve_file(path, True)
        # if path in ['css/markdown.css', 'favicon.ico', 'css/style.css']:
        #     return self.serve_file(path, True)

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
            return self.make_html([], full_path=full_path)
        # md file.
        if full_path.lower().endswith('.md'):
            self.markdown_file(full_path)
        else:
            self.serve_file(full_path)

    def make_sidebar(self, full_path: str):
        parent_directory = full_path
        if os.path.isfile(full_path):
            parent_directory = os.path.dirname(full_path)

        parent_directory = parent_directory.replace("\\", "/")
        path = parent_directory.replace(self.server.directory, "").strip("/")

        li_objs = []
        for entry in os.listdir(parent_directory):
            if entry.startswith(".") or entry.startswith("_"):
                continue
            entry_full = os.path.join(parent_directory, entry)
            entry_isfile = os.path.isfile(entry_full)
            a_href = '/{}'.format(entry)
            if path:
                a_href = '/{}/{}'.format(path, entry)

            li_class = 'folder'
            file_extension = entry
            if entry_isfile:
                li_class = 'page'
                file_extension = os.path.splitext(entry_full)[-1]
                if not file_extension:
                    file_extension = entry

            li_icon = self.file_icon(file_extension, entry_isfile)
            li_objs.append({'isfile': entry_isfile, 'href': a_href,
                           'name': entry, 'class': li_class, 'icon': li_icon})

        li_objs = sorted(li_objs, key=lambda kv: (kv['isfile'], kv['name']))
        # 首页Home;
        content = []
        content.extend(['<div class="path">',
                        '<a href="/"><img src="/icons/default_root_folder_opened.svg"/>Home</a>'])
        paths = path.split('/')
        if len(paths) > 1:
            content.append(
                '<a href="/{}">../</a>'.format('/'.join(paths[0:-1])))

        content.append('</div>')
        # 目录下的文件或者目录;
        content.append('<div><ul>')
        for li in li_objs:
            content.append(
                '<li class="{class}"><a href="{href}"><img src="/icons/{icon}"/>{name}</a></li>'.format(**li))
        content.append('</ul></div>')
        return content

    def make_html(self, content, full_path=None, last_modified=None):
        full_page = [
            "<!doctype html>",
            "<html><head>",
        ]
        full_page.extend(self.header_content())
        full_page.extend(["</head>", '<body>'])
        full_page.extend(
            ['<div class="layout">', '<div class="layout-sidebar">'])
        full_page.extend(self.make_sidebar(full_path))
        full_page.extend(['</div>', '<div class="layout-main markdown">'])
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
                                               'pymdownx.superfences',
                                               'pymdownx.tabbed',
                                               'pymdownx.tasklist',
                                               'pymdownx.highlight',
                                               'pymdownx.emoji',
                                               'pymdownx.magiclink',
                                               'markdown.extensions.footnotes',
                                               'markdown.extensions.attr_list',
                                               'markdown.extensions.def_list',
                                               'markdown.extensions.tables',
                                               'markdown.extensions.abbr',
                                               'markdown.extensions.md_in_html',
                                               ],
                                   extension_configs={
                                       'pymdownx.inlinehilite': {
                                           'custom_inline': [
                                               {
                                                   'name': 'math',
                                                   'class': 'arithmatex',
                                                   'format': arithmatex.arithmatex_inline_format(which="generic")
                                               }
                                           ]
                                       },
                                       "pymdownx.superfences": {
                                           "custom_fences": [
                                               {
                                                   "name": "math",
                                                   "class": "arithmatex",
                                                   'format': arithmatex.arithmatex_fenced_format(which="generic")
                                               },
                                               {
                                                   'name': 'mermaid',
                                                   'class': 'mermaid',
                                                   'format': pymdownx.superfences.fence_div_format
                                               }
                                           ]
                                       },
                                       'pymdownx.tasklist': {
                                           'custom_checkbox': True,
                                           'clickable_checkbox': False
                                       },
                                       # https://facelessuser.github.io/pymdown-extensions/extensions/highlight/#options
                                       'pymdownx.highlight': {
                                           'css_class': 'highlight',
                                           #    'guess_lang': True,
                                           # 'noclasses': True,
                                           # 'linenums': True,
                                       },
                                       'pymdownx.arithmatex': {
                                           'preview': False,
                                           'generic': True,
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
            '<script src="https://unpkg.com/mermaid@8.13.3/dist/mermaid.min.js"></script>',
            '<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.15.1/dist/katex.min.css" integrity="sha384-R4558gYOUz8mP9YWpZJjofhk+zx0AS11p36HnD2ZKj/6JR5z27gSSULCNHIRReVs" crossorigin="anonymous">',
            '<script defer src="https://cdn.jsdelivr.net/npm/katex@0.15.1/dist/katex.min.js" integrity="sha384-z1fJDqw8ZApjGO3/unPWUPsIymfsJmyrDVWC8Tv/a1HeOtGmkwNd/7xUS0Xcnvsx" crossorigin="anonymous"></script>',
            '<script defer src="https://cdn.jsdelivr.net/npm/katex@0.15.1/dist/contrib/auto-render.min.js" integrity="sha384-+XBljXPPiv+OzfbB3cVmLHf4hdUFHlWNZN5spNQ7rmHTXpd7WvJum6fIACpNNfIR" crossorigin="anonymous"></script>',
            r'''
            <script>
                document.addEventListener("DOMContentLoaded", function() {
                    renderMathInElement(document.body, {
                        strict: "ignore",
                        trust: ["\\htmlId"],
                        macros: {
                            "\\eqref": "\\href{###1}{(\\text{#1})}",
                            "\\ref": "\\href{###1}{\\text{#1}}",
                            "\\label": "\\htmlId{#1}{}",
                            "\\f": "#1f(#2)"
                        },
                        throwOnError: false,
                    });
                });
            </script>
            ''',
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
        if not os.path.exists(rel_path):
            self.send_response(404)
            return
        content_type = self.guess_type(filename)
        with open(rel_path, 'rb') as f:
            self.send_response(200)
            self.send_header("Content-type", content_type)
            fs = os.fstat(f.fileno())
            #self.send_header("Content-Length", str(fs[6]))
            self.send_header(
                "Last-Modified", self.date_time_string(fs.st_mtime))
            self.end_headers()

            shutil.copyfileobj(f, self.wfile)

    def file_icon(self, ext: str, isfile: bool):
        ext = ext.lower()
        if not isfile:
            ext = 'folder_type_{}'.format(ext)
        else:
            ext = 'file_type_{}'.format(ext.strip('.'))

        if ext in self.extensions_icon_map:
            return self.extensions_icon_map[ext]
        li_icon = 'default_folder.svg'
        if isfile:
            li_icon = 'default_file.svg'
        return li_icon

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
    extensions_icon_map = extensions_icon_map_init()
    # https://github.com/vscode-icons/vscode-icons/blob/master/src/iconsManifest/supportedFolders.ts
    # https://github.com/vscode-icons/vscode-icons/blob/master/src/iconsManifest/supportedExtensions.ts
    extensions_icon_map.update({
        'file_type_md': 'file_type_markdown.svg',
        'file_type_gemfile': 'file_type_bundler.svg',

        'file_type_gz': 'file_type_zip.svg',
        'file_type_7z': 'file_type_zip.svg',
        'file_type_tar': 'file_type_zip.svg',
        'file_type_tgz': 'file_type_zip.svg',
        'file_type_bz': 'file_type_zip.svg',

        'file_type_mod': 'file_type_go_package.svg',
        'file_type_sum': 'file_type_go_package.svg',

        'file_type_dockerfile': 'file_type_docker2.svg',

        'file_type_jpeg': 'file_type_image.svg',
        'file_type_jpg': 'file_type_image.svg',
        'file_type_gif': 'file_type_image.svg',
        'file_type_png': 'file_type_image.svg',
        'file_type_bmp': 'file_type_image.svg',
        'file_type_tiff': 'file_type_image.svg',
        'file_type_ico': 'file_type_image.svg',
        
        'folder_type_lang': 'folder_type_locale.svg',
        'folder_type_language': 'folder_type_locale.svg',
        'folder_type_languages': 'folder_type_locale.svg',
        'folder_type_locales': 'folder_type_locale.svg',
        'folder_type_internationalization': 'folder_type_locale.svg',
        'folder_type_i18n': 'folder_type_locale.svg',
        'folder_type_globalization': 'folder_type_locale.svg',
        'folder_type_g11n': 'folder_type_locale.svg',
        'folder_type_localization': 'folder_type_locale.svg',
        'folder_type_l10n': 'folder_type_locale.svg',
        'folder_type_logs': 'folder_type_log.svg',
        'folder_type_img': 'folder_type_images.svg',
        'folder_type_image': 'folder_type_images.svg',
        'folder_type_imgs': 'folder_type_images.svg',
        'folder_type_source': 'folder_type_src.svg',
        'folder_type_sources': 'folder_type_src.svg',

        'folder_type_tests': 'folder_type_test.svg',
        'folder_type_integration': 'folder_type_test.svg',
        'folder_type_specs': 'folder_type_test.svg',
        'folder_type_spec': 'folder_type_test.svg',
        'folder_type_win': 'folder_type_windows.svg',
    })


class MarkdownHTTPServer(HTTPServer):
    handler_class = MarkdownHTTPRequestHandler

    def __init__(self, server_address, directory: str, indexs: str):
        self.directory = directory.replace("\\", "/")
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


def run(host='', port=8080, directory=os.getcwd(), indexs=''):
    if not directory:
        directory = os.getcwd()
    if not indexs:
        indexs = 'index.html,index.md,README.md'

    server_address = (host, port)
    httpd = MarkdownHTTPServer(server_address, directory, indexs)
    print("Serving from http://{}:{}/".format(host, port))
    httpd.serve_forever()
