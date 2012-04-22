import os
import sys
import subprocess
import argparse
from paste.deploy import loadwsgi
from . import monitor

def restart_with_reloader():
    print('restart with monitor')
    new_environ = os.environ.copy()
    new_environ['PYTHON_RELOADER_SHOULD_RUN'] = 'true'
    args = [sys.executable] + sys.argv
    while True:
        proc = subprocess.Popen(args, env=new_environ)
        exit_code = proc.wait()
        print("subprocess exit %d" % exit_code)
        if exit_code != 3:
            return exit_code

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('config')
    parser.add_argument('--reload', action="store_true")

    args = parser.parse_args()
    if args.reload:
        if os.environ.get('PYTHON_RELOADER_SHOULD_RUN'):
            monitor.install_monitor()
            print('subprocess')
        else:
            return restart_with_reloader()
    app = loadwsgi.loadapp("config:" + args.config, relative_to=os.getcwd())
    server = loadwsgi.loadserver("config:" + args.config, relative_to=os.getcwd())
    server(app)
