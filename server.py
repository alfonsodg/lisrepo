#!/usr/bin/env python

import os
from tornado import ioloop, web
from pymongo import MongoClient
import json
from bson import json_util
import logging

with open('config.json') as json_data_file:
    data = json.load(json_data_file)

db_data = data['database']
db_indexes = data['indexes']
app_config = data['application']
keys = data["keys"]
log_file = data['log_file_base']

MONGODB_DB_URL = 'mongodb://{}:{}/'.format(db_data['host'], db_data['port'])
MONGODB_DB_NAME = db_data['name']
client = MongoClient(MONGODB_DB_URL)
db = client[MONGODB_DB_NAME]

rotation = logging.handlers.RotatingFileHandler(
    log_file, maxBytes=20, backupCount=5)
formatter = logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s',
                              datefmt='%Y-%m-%d %H:%M:%S')

handler = logging.handlers.RotatingFileHandler(
    log_file, maxBytes=10 * 1024 * 1024, backupCount=5)
handler.setFormatter(formatter)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)

for index in db_indexes:
    db.lab.create_index(index)


class IndexHandler(web.RequestHandler):
    def get(self):
        self.render("main.html")


class RepositoryHandler(web.RequestHandler):
    def get(self):
        validate = self.request.headers.get('X-Api-Key')
        status = {'status': 'Error'}
        if validate not in keys:
            self.write(status)
            return
        stories = db.lab.find()
        self.set_header("Content-Type", "application/json")
        self.write(json.dumps(list(stories), default=json_util.default))

    def post(self):
        validate = self.request.headers.get('X-Api-Key')
        status = {'status': 'Error'}
        if validate not in keys:
            self.write(status)
            return
        story_data = json.loads(self.request.body)
        story_id = db.lab.insert(story_data)
        self.set_header("Content-Type", "application/json")
        status = {'status': 'Ok'}
        self.set_status(201)
        self.write(status)


class WorkOrderHandler(web.RequestHandler):
    def get(self, work_order_number):
        validate = self.request.headers.get('X-Api-Key')
        work_order_number = '{}'.format(work_order_number)
        status = {'status': 'Error'}
        if validate not in keys:
            self.write(status)
            return
        order = db.lab.find_one({"id": work_order_number})
        try:
            user_agent = self.request.headers['User-Agent']
        except:
            user_agent = 'Unknown'
        remote_ip = self.request.remote_ip
        logger.info('{} : {} _ {} - {}'.format('Work Order', work_order_number, user_agent, remote_ip))
        self.set_header("Content-Type", "application/json")
        self.write(json.dumps(order, default=json_util.default))


class PatientAlternateIDHandler(web.RequestHandler):
    def get(self, patient_alternate_id):
        validate = self.request.headers.get('X-Api-Key')
        patient_alternate_id = '{}'.format(patient_alternate_id)
        status = {'status': 'Error'}
        if validate not in keys:
            self.write(status)
            return
        order = db.lab.find({"subject.reference_alternate": patient_alternate_id})
        try:
            user_agent = self.request.headers['User-Agent']
        except:
            user_agent = 'Unknown'
        remote_ip = self.request.remote_ip
        logger.info('{} : {} _ {} - {}'.format('Patient ID Alternate', patient_alternate_id, user_agent, remote_ip))
        self.set_header("Content-Type", "application/json")
        self.write(json.dumps(list(order), default=json_util.default))


class PatientIDHandler(web.RequestHandler):
    def get(self, patient_id):
        validate = self.request.headers.get('X-Api-Key')
        patient_id = '{}'.format(patient_id)
        status = {'status': 'Error'}
        if validate not in keys:
            self.write(status)
            return
        order = db.lab.find({"subject.reference": patient_id})
        try:
            user_agent = self.request.headers['User-Agent']
        except:
            user_agent = 'Unknown'
        remote_ip = self.request.remote_ip
        logger.info('{} : {} _ {} - {}'.format('Patient ID', patient_id, user_agent, remote_ip))
        self.set_header("Content-Type", "application/json")
        self.write(json.dumps(list(order), default=json_util.default))


class ProviderIDHandler(web.RequestHandler):
    def get(self, provider_id):
        validate = self.request.headers.get('X-Api-Key')
        provider_id = '{}'.format(provider_id)
        status = {'status': 'Error'}
        if validate not in keys:
            self.write(status)
            return
        order = db.lab.find({"reportNumber.providerId": provider_id})
        try:
            user_agent = self.request.headers['User-Agent']
        except:
            user_agent = 'Unknown'
        remote_ip = self.request.remote_ip
        logger.info('{} : {} _ {} - {}'.format('Provider ID', provider_id, user_agent, remote_ip))
        self.set_header("Content-Type", "application/json")
        self.write(json.dumps(list(order), default=json_util.default))


settings = {
    "template_path": os.path.join(os.path.dirname(__file__), "templates"),
    "static_path": os.path.join(os.path.dirname(__file__), "static"),
    "debug": True
}

application = web.Application([
    (r'/', IndexHandler),
    (r'/index', IndexHandler),
    (r'/api/v1/result', RepositoryHandler),
    (r'/api/v1/work_order/(.*)', WorkOrderHandler),
    (r'/api/v1/patient/(.*)', PatientIDHandler),
    (r'/api/v1/patient_alternate/(.*)', PatientAlternateIDHandler),
    (r'/api/v1/provider/(.*)', ProviderIDHandler)
], **settings)

if __name__ == "__main__":
    application.listen(app_config['port'])
    logger.info('Listening on http://localhost:%d' % app_config['port'])
    ioloop.IOLoop.instance().start()
