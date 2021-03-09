#!/usr/bin/env python3

"""
Integrated server and CMS startup
"""

import multiprocessing
import asyncio
# import yaml
import waitress

from cms.cms.wsgi import application as cms_app
from django.core.management import call_command as django_manage_call
from django.contrib.auth.models import User
from conf_manage import MainConfig

from server import start_server


def serve_cms(host, port):
    waitress.serve(cms_app, host=host, port=port)


if __name__ == '__main__':
    # test = MainConfig()
    # test.load()
    # test._data_path = "test.yaml"
    # test.save()
    # try:
    #     with open('config.yml') as f:
    #         user_config = yaml.safe_load(f)
    # except FileNotFoundError:
    #     with open('config.default.yml') as f:
    #         user_config = yaml.safe_load(f)
    # config = UserConfig()
    # config.load()
    # if not config.from_disk:
    #     config = DefaultConfig()
    #     config.load()
    config = MainConfig()
    config.load()
    if not config.from_disk:
        config.save()

    # if user_config['cms']['enabled']:
    if config.cms.enabled:
        # if not user_config['cms']['debug']:
        if not config.cms.debug:
            django_manage_call('collectstatic', interactive=False)
            django_manage_call('migrate', interactive=False)
            if User.objects.count() == 0:
                print('It looks like there are no users configured yet. Please create an account for your first '
                      'administrator:')
                django_manage_call('createsuperuser')
        cms_process = multiprocessing.Process(target=serve_cms, args=(
            # user_config['cms']['listen_host'],
            config.cms.listen_host,
            config.cms.listen_port
            # user_config['cms']['listen_port']
        ))
        cms_process.start()

    # servers = start_server.start(user_config)
    servers = start_server.start(config)

    loop = asyncio.get_event_loop()
    loop.run_forever()

    loop.close()
    # if user_config['cms']['enabled']:
    if config.cms.enabled:
        cms_process.join()
