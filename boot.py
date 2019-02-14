#!/usr/bin/python3.6

"""
Integrated server and CMS startup
"""

import multiprocessing
import asyncio
import yaml
import waitress
from django.core.management import call_command as django_manage_call

from cms.cms.wsgi import application as cms_app
from server import start_server

def serve_cms(host, port):
    waitress.serve(cms_app, host=host, port=port)

if __name__ == '__main__':
    try:
        with open('config.yml') as f:
            user_config = yaml.load(f)
    except FileNotFoundError:
        with open('config.default.yml') as f:
            user_config = yaml.load(f)

    if user_config['cms']['enabled']:
        if not user_config['cms']['debug']:
            django_manage_call('collectstatic', interactive=False)
        cms_process = multiprocessing.Process(target=serve_cms, args=(
            user_config['cms']['listen_host'],
            user_config['cms']['listen_port']
        ))
        cms_process.start()
    servers = start_server.start(user_config)

    loop = asyncio.get_event_loop()
    loop.run_forever()

    loop.close()
    if user_config['cms']['enabled']:
        cms_process.join()
