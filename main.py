#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-
import datetime
import os
import tracemalloc

import logger
from jenkins_connector import Jenkins
from postgre_connector import PostgresSql
from settings import build_allowed_configs

log = logger.configure_logger()


def main():
    global_start_time = datetime.datetime.now()
    tracemalloc.start()
    available_list = ['MDA']
    configurations = build_allowed_configs(available_list)
    config = configurations[0]
    jenkins = Jenkins(config.jenkins_url, config.jenkins_username, config.jenkins_password)
    postgres = PostgresSql(host=config.postgres_address, port=config.postgres_port,
                           user=config.postgres_username, password=config.postgres_password,
                           database=config.db_name)

    pipeline_name = os.environ.get("BUILD_NAME")
    branch_name = None
    run_id = os.environ.get("BUILD_NUMBER")

    runs_link = jenkins.build_run_link(pipeline_name=pipeline_name, branch_name=branch_name, run_id=run_id)
    runs = jenkins.get_runs_full(runs_link)
    if runs:
        if type(runs) is not list:
            runs = [runs]

    for run in runs:
        postgres.insert_run(run)

    current, peak = tracemalloc.get_traced_memory()
    print(f"Current memory usage is {current / 10 ** 6}MB; Peak was {peak / 10 ** 6}MB")
    tracemalloc.stop()
    print(f"---- Finished script:                   {datetime.datetime.now()- global_start_time}")


if __name__ == "__main__":
    main()
