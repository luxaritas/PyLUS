#!/usr/bin/python3.6

"""
Integrated server and CMS startup
"""

import multiprocessing
import asyncio
import yaml

import gunicorn.app.base
from gunicorn.six import iteritems

from cms.cms.wsgi import application as cms_app
from server import start_server

#pylint: disable=abstract-method
class GunicornCMS(gunicorn.app.base.BaseApplication):
    """
    Gunicorn application for PyLUS CMS
    """
    def __init__(self, config):
        self.config = config
        self.application = cms_app
        super().__init__()

    def load_config(self):
        if self.config['cms']['workers'] == 'default':
            workers = (multiprocessing.cpu_count() * 2) + 1
        else:
            workers = self.config['cms']['workers']

        host = self.config["cms"]["listen_host"]
        port = self.config["cms"]["listen_port"]

        options = {
            'bind': f'{host}:{port}',
            'workers': workers
        }

        for key, value in iteritems(options):
            self.cfg.set(key, value)

    def load(self):
        return self.application

if __name__ == '__main__':
    try:
        with open('config.yml') as f:
            user_config = yaml.load(f)
    except FileNotFoundError:
        with open('config.default.yml') as f:
            user_config = yaml.load(f)

    if user_config['cms']['enabled']:
        cms_process = multiprocessing.Process(target=GunicornCMS(user_config).run)
        cms_process.start()
    servers = start_server.start(user_config)

    loop = asyncio.get_event_loop()
    loop.run_forever()

    loop.close()
    if user_config['cms']['enabled']:
        cms_process.join()
