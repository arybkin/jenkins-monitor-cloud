import datetime
from dateutil.parser import parse


class ErrorObject:
    def __init__(self):
        self.runId = ""
        self.nodeIds = []
        self.error_message = dict()
        self.branch_name = ""
        self.is_stable = False
        self.run = dict()


def define_instability(i, runs):
    run = runs[i]

    if 'stable' in run:
        return
    if i != 0:
        is_restart = True
        for cause in runs[i]['causes']:
            if 'Branch event' in cause['shortDescription']:
                is_restart = False
        if "SUCCESS" in runs[i - 1]['result'] and is_restart:  # Out of Range
            runs[i]['stable'] = False
            return

    # if last build then it is stable
    if i == len(runs) - 1:
        runs[i]['stable'] = True
        return

    result = runs[i]['result']
    if "SUCCESS" in result:
        runs[i]['stable'] = True
        return
    elif "ABORTED" in result:
        define_instability(i + 1, runs)
        runs[i]['stable'] = runs[i + 1]['stable']
        return
    elif 'FAILURE' in result:
        is_restart = True
        for cause in runs[i + 1]['causes']:
            if 'Branch event' in cause['shortDescription']:
                is_restart = False
        if is_restart:
            if "SUCCESS" in runs[i + 1]['result']:  # Out of Range
                runs[i]['stable'] = False
                return
            elif "FAILURE" in runs[i + 1]['result']:  # Out of Range
                if len(runs[i]['nodes']) < len(runs[i + 1]['nodes']):
                    runs[i]['stable'] = False
                    return
                else:
                    define_instability(i + 1, runs)
                    runs[i]['stable'] = runs[i + 1]['stable']
                    return
        else:
            runs[i]['stable'] = True
            return


def collect_runs_statistics(runs):
    pass_number = 0
    aborted_number = 0
    fail_number = 0
    unstable_rerun = 0
    errors = []
    result = runs[0]['result']
    if "SUCCESS" in result:
        pass_number = pass_number + 1
    elif 'FAILURE' in result:
        fail_number = fail_number + 1
    elif 'ABORTED' in result:
        aborted_number += 1

    if len(runs) > 1:
        for i in range(1, len(runs)):
            result = runs[i]['result']
            is_restart = False
            for cause in runs[i]['causes']:
                if 'Branch event' in cause['shortDescription']:
                    is_restart = True

            if "SUCCESS" in result:
                pass_number = pass_number + 1
                if "SUCCESS" not in runs[i - 1]['result'] \
                    and runs[i]['commitId'] == runs[i - 1]['commitId'] \
                        and is_restart:
                    unstable_rerun += 1
            elif 'FAILURE' in result:
                nodes = runs[i]['nodes']
                errors_node = set()
                for node in nodes:
                    if node['result'] and "SUCCESS" not in node['result']:
                        steps = node['steps']
                        for step in steps:
                            if step['result'] and "SUCCESS" not in step['result']:
                                log_error = step['log']
                                errors_node.add(
                                    f"PR: {runs[i]['pipeline']} run: {runs[i]['id']} node: {node['id']} {log_error}")

                errors.extend(errors_node)

                fail_number = fail_number + 1
            elif 'ABORTED' in result:
                aborted_number += 1

    return pass_number, fail_number, unstable_rerun, errors


def collect_errors(runs):
    errors = []
    for run in runs:
        if 'FAILURE' in run['result']:
            nodes = run['nodes']
            errors_node = set()

            error = ErrorObject()
            error.branch_name = run['pipeline']
            error.is_stable = run['stable']
            error.runId = run['id']
            error.run = run
            for node in nodes:
                if node['result'] and "SUCCESS" not in node['result']:
                    steps = node['steps']
                    for step in steps:
                        if step['result'] and "SUCCESS" not in step['result']:
                            log_error = step['log']
                            error.error_message[node['id']] = [step['id'], log_error]
                            errors_node.add(
                                f"PR: {run['pipeline']} run: {run['id']} step: {step['id']} {log_error}")
                    error.error_message[node['id']] = errors_node
            errors.append(error)
    return errors


def get_max_min_avg_runs(runs):
    sum_num = 0
    values = []
    for run in runs:
        values.append(run['durationInMillis'])
        sum_num = sum_num + run['durationInMillis']

    avg = sum_num / len(runs)
    return datetime.timedelta(milliseconds=max(values)), datetime.timedelta(
        milliseconds=min(values)), datetime.timedelta(milliseconds=avg)


def get_max_min_avg_runs_in_queue(runs):
    sum_num = 0
    values = []
    for run in runs:
        elapsed_time = (parse(run['startTime']) - parse(run['enQueueTime'])).total_seconds()
        values.append(elapsed_time)
        sum_num = sum_num + elapsed_time

    avg = sum_num / len(runs)
    return datetime.timedelta(seconds=max(values)), datetime.timedelta(seconds=min(values)), datetime.timedelta(
        seconds=avg)


def get_max_min_avg_runs_in_sleep(runs):
    sum_num = 0
    sum_num_node = 0
    values = []
    values_node = []
    for run in runs:
        pause = 0
        for node in run['nodes']:
            pause_node = 0
            for step in node['steps']:
                if "Sleep" in step['displayName']:
                    pause = pause + 1
                    pause_node = pause_node + 1
            values_node.append(pause_node)
            sum_num_node += pause_node
        values.append(pause)
        sum_num = sum_num + pause

    avg = sum_num / len(runs)
    avg_node = sum_num_node / len(values_node)
    a, b, c = datetime.timedelta(minutes=max(values_node)), datetime.timedelta(
        minutes=min(values_node)), datetime.timedelta(
        minutes=avg_node)
    print("Time in nodes")
    print(f"Max: {a}, Min: {b}, Avg: {c}")
    return datetime.timedelta(minutes=max(values)), datetime.timedelta(minutes=min(values)), datetime.timedelta(
        minutes=avg)


def get_pass_rate(runs):
    pass_number = 0
    fail_number = 0
    for run in runs:
        if "SUCCESS" in run['result']:
            pass_number = pass_number + 1
        else:
            fail_number = fail_number + 1

    if pass_number is 0:
        return 0
    return (fail_number + pass_number) / pass_number
