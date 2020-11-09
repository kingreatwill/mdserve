import argparse
import os

from mdserve import markdown_server
from mdserve.schedule_server import ScheduleServer

"""
from wsgiref.simple_server import make_server
with make_server(host=host, port=port, app=app) as httpd:   
    httpd.serve_forever()
"""
parser = argparse.ArgumentParser(description='Render markdown files and serve them with an http server.')
parser.add_argument('-d', '--directory', default=r'F:\github\openjw\open', type=str, help='directory[default:current directory].')
parser.add_argument('--host', type=str, default='0.0.0.0', help='host.')
parser.add_argument('-p', '--port', type=int, default=8080, help='port.')
parser.add_argument('--level', action='store_true', help='log level.')
parser.add_argument('-c', '--crontab', type=str, default='0 */1 * * *', help='默认整点执行一次.')

args = parser.parse_args()
if not args.directory: args.directory = os.getcwd()  # = os.path.split(os.path.abspath(sys.argv[0]))[0]


def main():
    ScheduleServer(args.directory, args.crontab).run()
    markdown_server.run(host=args.host, port=args.port, directory=args.directory)


if __name__ == '__main__':
    main()
