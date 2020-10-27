import argparse
import os

from mdserve import markdown_server

"""
from wsgiref.simple_server import make_server
with make_server(host=host, port=port, app=app) as httpd:   
    httpd.serve_forever()
"""
parser = argparse.ArgumentParser(description='Render markdown files and serve them with an http server.')
parser.add_argument('-d', '--directory', type=str, help='directory[default:current directory].')
parser.add_argument('--host', type=str, default='0.0.0.0', help='host.')
parser.add_argument('-p', '--port', type=int, default=8080, help='port.')
parser.add_argument('--level', action='store_true', help='log level.')

args = parser.parse_args()
if not args.directory: args.directory = os.getcwd()  # = os.path.split(os.path.abspath(sys.argv[0]))[0]


def main():
    print(args)
    markdown_server.run(host=args.host, port=args.port, directory=args.directory)


if __name__ == '__main__':
    main()
