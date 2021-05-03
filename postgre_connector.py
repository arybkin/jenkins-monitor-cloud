import logging
from datetime import datetime

import psycopg2

logger = logging.getLogger('')
DEC2FLOAT = psycopg2.extensions.new_type(
    psycopg2.extensions.DECIMAL.values,
    'DEC2FLOAT',
    lambda value, curs: float(value) if value is not None else None)
psycopg2.extensions.register_type(DEC2FLOAT)


class PostgresSql:
    __conn = None
    __user = None
    __password = None
    __database = None
    __host = None
    __port = None
    exclude_list = ['actions', 'artifactsZipFile', '_class', '_links', 'causes', 'changeSet', 'causeOfBlockage',
                    # common
                    'branch', 'pullRequest',  # from runs
                    'edges',  # from nodes
                    'nodes', 'steps']
    RUNS_TABLE_NAME = "runs"
    NODES_TABLE_NAME = "nodes"
    STEPS_TABLE_NAME = "steps"

    def __init__(self, host, port, user, password, database):
        self.__user = user
        self.__password = password
        self.__host = host
        self.__port = port
        self.__database = database

    def insert_run(self, run):
        start = datetime.now()
        logger.info(f"{run['run_uuid']} - Insert run - {run['job_name']}")
        self.insert_item(run, self.RUNS_TABLE_NAME)
        nodes = run['nodes']
        steps = []
        if nodes:
            if type(nodes) is not list:
                nodes = [nodes]

            self.insert_items(nodes, self.NODES_TABLE_NAME)
            for node in nodes:
                steps.extend(node['steps'])

        if steps:
            self.insert_items(steps, self.STEPS_TABLE_NAME)
        end = datetime.now()
        logger.info(f"{run['run_uuid']} - Run is pasted - {run['job_name']}")
        logger.info(f"{run['run_uuid']} - Run is pasted duration - {end - start}")

    def insert_item(self, item, table_name):
        start = datetime.now()
        logger.info(f"Insert {table_name}")
        command, values = self.__build_command(item, table_name)
        conn = psycopg2.connect(host=self.__host, port=self.__port, user=self.__user, password=self.__password,
                                database=self.__database)
        cursor = conn.cursor()
        cursor.execute(command, values)
        conn.commit()  # <- We MUST commit to reflect the inserted data
        cursor.close()
        conn.close()

        end = datetime.now()
        logger.info(f"Inserted {table_name} - duration - {end - start}")

    def insert_items(self, items, table_name):
        start = datetime.now()
        logger.info(f"Insert {table_name}")

        command, values = self.__build_command_many(items, table_name)
        conn = psycopg2.connect(host=self.__host, port=self.__port, user=self.__user, password=self.__password,
                                database=self.__database)
        cursor = conn.cursor()
        cursor.executemany(command, values)
        conn.commit()  # <- We MUST commit to reflect the inserted data
        cursor.close()
        conn.close()

        end = datetime.now()
        logger.info(f"Inserted {table_name} - duration - {end - start}")

    def get_items(self, file_name):
        file_path = f"requests/{file_name}"
        data = self.__select_request_from_file(file_path)
        return self.__convert_response_to_dict(data)

    @staticmethod
    def __convert_response_to_dict(data):
        out_dict = {}
        for line in data:
            out_dict[line[0]] = list()
            for i in range(1, len(line)):
                out_dict[line[0]].append(line[i])
        return out_dict

    def __select_request_from_file(self, filePath):
        with open(filePath, 'r') as file:
            request = file.read()

        if request:
            logger.info(f"Run request: \n {request}")
            conn = psycopg2.connect(host=self.__host, port=self.__port, user=self.__user, password=self.__password,
                                    database=self.__database)
            cursor = conn.cursor()

            cursor.execute(request)
            output = cursor.fetchall()

            cursor.close()
            conn.close()
            logger.info(f"Output first line: \n {output[0]}")
            return output

        return None

    def __build_command(self, item, table_name):
        columns = []
        values = []
        values_space = []
        for key in item:
            if key not in self.exclude_list:
                columns.append(key)
                values.append(item[key])
                values_space.append('%s')

        column_str = ','.join(map(str, columns))
        values_spaces_str = ','.join(map(str, values_space))
        command = "INSERT INTO {0} ({1}) VALUES({2})".format(table_name, column_str, values_spaces_str)
        return command, values

    def __build_command_many(self, items, table_name):
        columns = []
        values = []
        values_space = []
        for key in items[0]:
            if key not in self.exclude_list:
                columns.append(key)
                values_space.append('%s')

        for item in items:
            temp_list = []
            for column in columns:
                temp_list.append(item[column])
            values.append(temp_list)

        column_str = ','.join(map(str, columns))
        values_spaces_str = ','.join(map(str, values_space))
        command = "INSERT INTO {0} ({1}) VALUES({2})".format(table_name, column_str, values_spaces_str)
        return command, values
