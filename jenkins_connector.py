import logging
import threading
from datetime import datetime
from queue import Queue

import requests
import base64
import json
import uuid

logger = logging.getLogger('')


class Jenkins:
    __auth = None
    __basic_url = None
    build_name = None
    runs_link = None
    job_name = None

    def __init__(self, basic_url, user_name, password):
        self.__basic_url = f"{basic_url}/organizations/jenkins/pipelines"
        self.__auth = "Basic %s" % base64.b64encode(bytes('%s:%s' % (user_name, password), 'ascii')).decode('utf-8')

    def build_run_link(self, pipeline_name, branch_name=None, run_id=None):
        logger.info('Build link to Job')
        self.job_name = pipeline_name
        runs_link = f"{self.__basic_url}/{pipeline_name}/runs"
        if branch_name:
            runs_link = f"{self.__basic_url}/{pipeline_name}/branches/{branch_name}/runs"
            if run_id:
                runs_link = f"{runs_link}/{run_id}"
        elif not branch_name and run_id:
            runs_link = f"{runs_link}/{run_id}"

        self.runs_link = runs_link
        logger.info(f"For build will be used link {runs_link}")
        return runs_link

    def get_response(self, urn):
        logger.info(f"Get build {urn}")
        r = requests.get(f"{urn}", headers={'Authorization': self.__auth})
        logger.info(f"Request with status {r.status_code}")
        return r

    def get_run_full(self, runs_link):
        start = datetime.now()
        unique_name = str(uuid.uuid4())
        logger.info(f"{unique_name} - Get run from jenkins - {runs_link}")
        if runs_link:
            self.runs_link = runs_link
        run = self.__get_items(self.runs_link)

        nodes_link = f"{self.runs_link}/nodes"
        run_id = run['id']
        run['run_uuid'] = unique_name
        run['job_name'] = self.job_name
        if not nodes_link:
            nodes_link = f"{self.runs_link}/{run_id}/nodes"
        run['nodes'] = []
        run['nodes'].extend(self.__get_nodes(nodes_link, run['run_uuid']))

        end = datetime.now()
        logger.info(f"{unique_name} - Get run from jenkins duration - {end - start}")
        return run

    def get_runs_full(self, runs_link=None):
        start = datetime.now()
        logger.info(f"Get runs - start - {start}")
        if runs_link:
            self.runs_link = runs_link
        runs = self.__get_items(self.runs_link)
        nodes_link = None
        if type(runs) is not list:
            runs = [runs]
            nodes_link = f"{self.runs_link}/nodes"

        runs.reverse()
        for run in runs:
            unique_name = str(uuid.uuid4())
            logger.info(f"{unique_name} - Get run from jenkins - {runs_link}")
            run_id = run['id']
            run['run_uuid'] = unique_name
            run['job_name'] = self.job_name
            if not nodes_link:
                nodes_link = f"{self.runs_link}/{run_id}/nodes"
            run['nodes'] = []
            run['nodes'].extend(self.__get_nodes(nodes_link, run['run_uuid']))
            logger.info(f"{unique_name} - Run is built - {runs_link}")

        end = datetime.now()
        logger.info(f"Runs are built duration - {end - start}")
        return runs

    def __get_nodes(self, node_links, parent_run_uuid):
        start = datetime.now()
        logger.info(f"{parent_run_uuid} - Get nodes from jenkins - {node_links}")
        nodes = self.__get_items(node_links)
        for node in nodes:
            node_id = node['id']

            node['run_uuid'] = parent_run_uuid
            node['node_uuid'] = str(uuid.uuid4())
            steps_link = f"{node_links}/{node_id}/steps"
            node['steps'] = []
            node['steps'].extend(self.__get_steps(steps_link, node['node_uuid']))

        end = datetime.now()
        logger.info(f"{parent_run_uuid} - Get nodes from jenkins duration - {end - start}")
        return nodes

    def __get_nodes_parallel(self, node_links, parent_run_uuid):
        nodes = self.__get_items(node_links)
        queue = Queue()
        for node in nodes:
            queue.put(node)
        for i in range(0, 10):
            t1 = threading.Thread(target=self.__get_node, args=(queue, parent_run_uuid, node_links))
            t1.daemon = True
            t1.start()
        queue.join()
        return nodes

    def __get_node(self, queue, parent_run_uuid, node_links):
        while not queue.empty():
            node = queue.get()
            node_id = node['id']

            node['run_uuid'] = parent_run_uuid
            node['node_uuid'] = str(uuid.uuid4())
            steps_link = f"{node_links}/{node_id}/steps"
            node['steps'] = []
            node['steps'].extend(self.__get_steps(steps_link, node['node_uuid']))

    def __get_steps(self, steps_link, parent_node_uuid):
        steps = self.__get_items(steps_link)
        for step in steps:
            step['node_uuid'] = parent_node_uuid
            result = step['result']
            step['log'] = None
            if result != 'SUCCESS':
                logs_link = f"{steps_link}/{step['id']}/log"
                log = self.__get_response(logs_link)
                step['log'] = log

        return steps

    def __get_items(self, urn):
        return json.loads(self.__get_response(urn))

    def __get_response(self, urn):
        r = requests.get(f"{urn}", headers={'Authorization': self.__auth})
        if r.status_code != 200:
            print(r.text)
        return r.content.decode('utf-8')
