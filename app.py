import json
import os
import threading
from flask import Flask, request, send_from_directory

import logger
from jenkins_connector import Jenkins
from postgre_connector import PostgresSql
from settings import build_allowed_configs

log = logger.configure_logger()
app = Flask(__name__)
app.config["DEBUG"] = True
available_list = ['MDA']
configurations = build_allowed_configs(available_list)
log.warning(f"Creds: {configurations[0].config['Base']['Postgres_Address']}")


def post_to_db(runs_link, postgres, jenkins):
    run = jenkins.get_run_full(runs_link)
    postgres.insert_run(run)
    print("Message is done")


@app.route('/', methods=['GET'])
def api_main():
    return "Everything is fine"


@app.route('/run', methods=['POST'])
def api_upload_run():
    branch_name = None
    body = request.form
    config_name = body.get("Jenkins")
    for config in configurations:
        if config_name in config.name:
            jenkins = Jenkins(config.jenkins_url, config.jenkins_username, config.jenkins_password)
            postgres = PostgresSql(host=config.postgres_address, port=config.postgres_port,
                                   user=config.postgres_username, password=config.postgres_password,
                                   database=config.db_name)
            runs_link = jenkins.build_run_link(pipeline_name=body.get("pipeline_name"), branch_name=branch_name,
                                               run_id=body.get("run_id"))

            response = jenkins.get_response(runs_link)
            t1 = threading.Thread(target=post_to_db, args=(runs_link, postgres, jenkins,))
            t1.start()

            return json.loads(response.content.decode('utf-8')), response.status_code


@app.route('/duration_pause_nodes', methods=['GET'])
def api_duration_pause_nodes():
    config_name = 'MDA'
    for config in configurations:
        if config_name in config.name:
            postgres = PostgresSql(host=config.postgres_address, port=config.postgres_port,
                                   user=config.postgres_username, password=config.postgres_password,
                                   database=config.db_name)
            data = postgres.get_items('select_duration_pause_nodes.sql')
            return data


@app.route('/duration_pause_runs', methods=['GET'])
def api_duration_pause_runs():
    config_name = 'MDA'
    for config in configurations:
        if config_name in config.name:
            postgres = PostgresSql(host=config.postgres_address, port=config.postgres_port,
                                   user=config.postgres_username, password=config.postgres_password,
                                   database=config.db_name)
            data = postgres.get_items('select_duration_pause_runs.sql')
            return data


app.run(host='0.0.0.0', port=80)
