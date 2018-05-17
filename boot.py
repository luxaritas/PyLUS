import multiprocessing
import asyncio
import yaml

import gunicorn.app.base
from gunicorn.six import iteritems

from cms.cms.wsgi import application as cms_app
from server import start_server

class GunicornCMS(gunicorn.app.base.BaseApplication):

    def __init__(self, config):
        if config['cms']['workers'] == 'default':
            workers = (multiprocessing.cpu_count() * 2) + 1
        else:
            workers = config['cms']['workers']

        host = config["cms"]["listen_host"]
        port = config["cms"]["listen_port"]

        options = {
            'bind': f'{host}:{port}',
            'workers': workers
        }
        
        self.options = options
        self.application = cms_app
        super().__init__()

    def load_config(self):
        config = dict([(key, value) for key, value in iteritems(self.options)
                       if key in self.cfg.settings and value is not None])
        for key, value in iteritems(config):
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application
    
if __name__ == '__main__':
    try:
        with open('config.yml') as f:
            config = yaml.load(f)
    except FileNotFoundError:
        with open('config.default.yml') as f:
            config = yaml.load(f)
    
    cms_process = multiprocessing.Process(target=GunicornCMS(config).run)
    cms_process.start()
    servers = start_server.start(config)
    
    loop = asyncio.get_event_loop()
    loop.run_forever()
    
    loop.close()
    cms_process.join()