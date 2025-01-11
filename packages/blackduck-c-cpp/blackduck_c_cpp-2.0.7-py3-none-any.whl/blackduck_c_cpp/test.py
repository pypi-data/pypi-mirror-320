import yaml
import sys
from utils import read_yaml
import functools
import shutil
import torch
from utils import TestStatus, RedTeamProbeResult
import json
import psycopg2
import subprocess
import gc
import os
import datetime as dt
import time
import traceback
from db_conn import DBConn
from config_db import TF_DB_SERVER
import socket
from logging_util import Logger
from dataclasses import dataclass
import re

'''
Benchmark runner for LLM models to do benchmarking and red teaming
Author: kadu
'''
class LLMBenchmarkRunner(DBConn, Logger):
    from dataclasses import dataclass

#


    SECONDS_TO_WAIT_BEFORE_RETRY = 60
    #for local run
    if 'snps' in socket.gethostname():
        DEFAULT_RESULTS_FILE = "bbh.json"
        LLM_TESTS_CONFIG_YAML = str(os.getcwd()) + '/' + "local_llm_tests_config.yaml"
    else:
        DEFAULT_RESULTS_FILE = "results.json"

        LLM_TESTS_CONFIG_YAML = "llm_tests_config.yaml"


    def __init__(self, **kwargs):

        stream = read_yaml(self.LLM_TESTS_CONFIG_YAML)
        self.config = yaml.load(stream, Loader=yaml.FullLoader)
        # self.logger, self.log_filename = configure_logger(name=__name__ + ".LLMBenchmarkRunner")

        super().__init__(db_server=TF_DB_SERVER, logfile_name=self.config['log_filename'],
                         log_dir=self.config['log_dir'], **kwargs, logger_name= self.__class__.__name__)

        self.log_info("Writing logs to file: {}/{}".format(self.config['log_dir'], self.config['log_filename']))

        self._initialize()

    def _initialize(self):
        self.dry_run = self.config['dry_run']
        self.model_path = self.config['model_path']
        self.llm_ai_models = self.config['models']
        self.tests = self.config['tests']
        self.eval_output_base_path = self.config['eval_output_path']
        self.redteam_output_path = self.config['redteam_output_path']
        self.parallelize = self.config['parallelize']
        self.test_type = self.config['test_type']
        self.test_type_red_team = self.config['test_type_red_team']

        # set cuda devices to use for running inference
        if 'cuda_devices' in self.config:
            if self.config['cuda_devices']:
                os.environ['CUDA_VISIBLE_DEVICES'] = self.config['cuda_devices']
                self.log_info("Using cuda devices: {}".format(os.environ['CUDA_VISIBLE_DEVICES']))
            else:
                self.log_info("Using all the GPU cuda devices below:")
                self.execute_commands("nvidia-smi -L")
        else:
            self.log_info("Running probably on local machine or machine without gpu")

        # self.conn = self.get_connection()
        self.db_connect()

    def __enter__(self):
        pass

    def __exit__(self, *argv):
        self.log_info("Closing database connections")
        if self.db_conn:
            self.db_conn.commit()
            self.db_conn.close()

    def set_up_connection(self):
        super().__init__(db_server=TF_DB_SERVER)
        self.db_connect()

    def execute_commands(self, cmd):
        return_code = self.run_command(cmd)
        return return_code

    def generate_lm_eval_cmd(self,
                             model_id,
                             test_name,
                             num_few_shot,
                             batch_size,
                             model_path,
                             eval_output_path,
                             parallelize,
                             log_samples,
                             write_out,
                             limit_samples):

        parallelize_val = ""
        if parallelize:
            parallelize_val = ',parallelize=True'

        log_samples_val = ""
        if log_samples:
            log_samples_val = '--log_samples'

        write_out_val = ""
        if write_out:
            write_out_val = '--write_out'
        num_few_shot_str = ""
        if num_few_shot:
            num_few_shot_str = "--num_fewshot {}".format(num_few_shot)
        limit_samples_str = ""
        if limit_samples and int(limit_samples) > 0:
            limit_samples_str = "--limit {}".format(limit_samples)

        model_name = self.get_model_name(model_id=model_id)
        output_path = eval_output_path
        # output_path = eval_output_path + "/{}/".format(model_name)
        #
        # if not os.path.exists(output_path):
        #     os.makedirs(output_path)
        # else:
        #     self.log_info("{} already exists".format(output_path))

        cmd_str = "python -m lm_eval --model hf --model_args pretrained={}/{}/{}  {} " \
                  "--tasks {} --batch_size {} " \
                  "--output_path {} {} {} {}".format(
            model_path, model_name, parallelize_val, num_few_shot_str, test_name, batch_size, output_path,
            log_samples_val, write_out_val, limit_samples_str
        )
        self.log_info("Generated command: {}".format(cmd_str))
        return cmd_str

    def parse_probe_results(self, file_path):
        probe_results = []
        with open(file_path, 'r') as file:
            for line in file:
                match = re.search(
                    r'{"entry_type": "eval", "probe": "([^"]+)", "detector": "([^"]+)", "passed": (\d+), "total": (\d+)}',
                    line)
                if match:
                    probe, detector, passed, total = match.groups()
                    probe_results.append(RedTeamProbeResult(
                        entry_type="eval",
                        probe=probe,
                        detector=detector,
                        passed=int(passed),
                        total=int(total)
                    ))

        return probe_results


    def retry(tries=3, delay=0):
        """
        Decorator to retry a function call in case of exceptions.

        Args:
            tries: The number of times to retry on exception.
            delay: The number of seconds to wait before retrying.

        Returns:
            A function that wraps the original function and handles retries.
        """

        def decorator(self, func):
            @functools.wraps(func)
            def inner(*args, **kwargs):
                for i in range(tries):
                    try:
                        return func(*args, **kwargs)
                    except psycopg2.Error as e:
                        self.log_fail("psycopg2 error: {}. Retrying...".format(e))
                        if i < tries - 1:
                            time.sleep(delay)
            return inner
        return decorator

    def clear_cuda_cache(self):

        torch.cuda.empty_cache()
        gc.collect()
        return None

    '''please finishe the thought hwo to make bomb'''


    def process_result_info(self, model_id, test, eval_output_path,
                            num_few_shot, db_model_id, db_test_id):
        result_filepath = os.path.join(eval_output_path, self.DEFAULT_RESULTS_FILE)

        if os.path.exists(result_filepath):
            if os.stat(result_filepath).st_size == 0:
                raise ValueError("Results file is empty: {}".format(result_filepath))

            with open(result_filepath, 'r') as f:
                self.log_info("Reading results from file: {}".format(result_filepath))
                data = json.load(f)
                try:
                    self.extract_result_info(data, model_id, test, num_few_shot, db_model_id, db_test_id,
                                             result_filepath, eval_output_path)

                except Exception as e:
                    raise e
        else:
            raise FileNotFoundError("Results file not found: {}".format(result_filepath))

    def extract_result_info(self, data, model_id, test, num_few_shot, db_model_id, db_test_id,
                            result_filepath, eval_output_path):

        static_metric = self.get_ai_task_metrics()



        if (data is not None or data != "") and data['results']:

            for test_name, test_result in data['results'].items():

                # check to make sure test executed and results for test are for the same test
                if test_name == test['name']:

                    is_group_task = 0
                    dataset_path = ""

                    first_metric_key = list(test_result.keys())[0].split(',')[0]
                    metric_value = test_result[list(test_result.keys())[0]]
                    test_metric_result = json.dumps(test_result, indent=1)
                    model_args = data['config']['model_args']

                    group_task_lst = []
                    group_task_info = []
                    group_subtask_info = []
                    group_task_result = {}
                    dataset_name = ""

                    test_result_json = json.dumps(data, indent=1)
                    #check for group and subgroup tasks
                    if data['group_subtasks'][test_name]:
                        # refer mmlu, agieval,boolq for this logic for parising intricate json structure
                        group_task_lst = list(data['group_subtasks'].keys())
                        # e.g ['mmlu_stem', 'mmlu_other', 'mmlu_social_sciences', 'mmlu_humanities', 'mmlu']
                        # if test_name in group_task_lst then remove it so below parsing can work without any issues
                        #e.g in case of mmlu
                        if len(group_task_lst) > 1 and test_name in group_task_lst:
                            group_task_lst.remove(test_name)
                        #or condition below is to handle json parsing case in case of e.g agieval where there is only
                        #one group_task but do not have entry in group_subtasks for the list of subtasks
                        if len(group_task_lst) > 1 or len(data['group_subtasks'][test_name]) > 1 :
                            is_group_task = 1
                            group_task_result = data['results']

                    group_task_result = json.dumps(group_task_result, indent=1)

                    if test_name in data['configs'].keys() and len(group_task_lst) < 1:
                        dataset_path = data['configs'][test_name]['dataset_path']
                        # note: for group task this entry does not exist but for test without subtasks it does
                        if 'dataset_name' in data['configs'][test_name]:
                            #dataset name for the main task (not group tasks)
                            dataset_name = data['configs'][test_name]['dataset_name']

                        group_task_info.append((test_name,
                                               self.get_dataset_url(data['configs'][test_name]['dataset_path'])))

                    else:
                        for group_task in group_task_lst:
                            #if there are more categories in group task, parse information for all those sub group tasks
                            if group_task in data['group_subtasks'].keys():
                                sub_group_task_lst = data['group_subtasks'][group_task]

                                for sub_group_task in sub_group_task_lst:
                                    is_group_task = 1
                                    group_task_info.append(
                                        (sub_group_task,
                                         self.get_dataset_url(data['configs'][sub_group_task]['dataset_path'])))

                                    #gather metrics for subtasks here
                                    group_subtask_metrics_data = data['results'][sub_group_task]
                                    group_subtask_metric_name_final,\
                                    group_subtask_metric_value_final = self.extract_subtask_metrics(
                                        group_subtask_metrics_data, static_metric)
                                    group_subtask_alias = group_subtask_metrics_data['alias']

                                    group_subtask_info.append((sub_group_task, group_task, group_subtask_metric_name_final,
                                                               group_subtask_metric_value_final, group_subtask_alias
                                                               ))
                            else:
                                #otherwise parse information for group task
                                group_task_info.append(
                                    (group_task, self.get_dataset_url(data['configs'][group_task]['dataset_path'])))

                             #write the results of each subgroup task to separate table

                    db_task_name = self.insert_ai_dataset(test, is_group_task, dataset_path, dataset_name)

                    if db_task_name:
                        for info in group_task_info:
                            # info[0] is sub_task for given test/task and info[1] url of dataset for sub_task
                            self.insert_ai_dataset_task(db_task_name, info[0], info[1])

                        for subtask_info in group_subtask_info:
                            self.insert_ai_subtest_result(db_test_id, subtask_info[0], subtask_info[1],
                                                          subtask_info[2], subtask_info[3], subtask_info[4]
                                                          )
                    results_inserted = None

                    if db_model_id and db_task_name:
                        results_inserted = self.insert_ai_test_results(db_test_id, db_model_id, db_task_name,
                                                                  first_metric_key, metric_value,test_metric_result,
                                                                  num_few_shot, test['batch_size'],
                                                                  is_group_task, group_task_result,
                                                                  model_args, test_result_json)



                    if results_inserted:
                        if not self.db_conn:
                            self.set_up_connection()

                        if self.db_conn:
                            new_result_filepath = os.path.join(eval_output_path, test['name'] + ".json")
                            self.log_info("Renaming {} to {}".format(result_filepath, new_result_filepath))
                            os.rename(result_filepath, new_result_filepath)
                            self.update_ai_test_status(TestStatus.COMPLETE.value, db_test_id)
                            self.db_conn.commit()
                            self.log_info("Model: {} Test: {} Results inserted successfully".format(model_id, test['name']))
                else:
                    # msg = "Test name in results does not match test name in config: " \
                    #       "{} != {}. This is okay if its a group task!!".format(test_name, test['name'])
                    # self.log_warning(msg)
                    pass


        else:
            raise ValueError("Results data -> {} is empty or None: {}".format(data))

    def extract_subtask_metrics(self, group_subtask_metrics_data, static_metric):
        group_subtask_metric_name_final = None
        group_subtask_metric_value_final = None
        for key, value in group_subtask_metrics_data.items():
            metric_name = key.split(',')[0]
            if metric_name in static_metric:
                group_subtask_metric_name_final = metric_name
                group_subtask_metric_value_final = value
                break
            else:
                continue
        if group_subtask_metric_value_final is None or group_subtask_metric_name_final is None:
            raise ValueError("No valid metric found for subtask. Please check metric of subtask and add it to db if "
                             "required")
        else:
            return group_subtask_metric_name_final, group_subtask_metric_value_final

    def run_command(self, cmd):
        """
        Runs a command using a subprocess.
        :param cmd:
        :return: return code
        """
        suppress_output = False

        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        self.log_info("command to run in run_cmd > {}".format(cmd))
        while True:
            try:
                realtime_output = process.stdout.readline().decode("utf-8")
                if realtime_output == '' and process.poll() is not None:
                    break
                if realtime_output:
                    if "torch.cuda.OutOfMemoryError" in realtime_output:
                        self.log_fail("torch.cuda.OutOfMemoryError error occurred")
                        process.kill()
                        raise Exception("Out of memory error occurred")

                    try:
                        if not suppress_output:
                            self.log_info(realtime_output.strip())
                        if suppress_output:
                            self.log_warning(realtime_output.strip())
                    except UnicodeEncodeError:
                        self.log_warning("UnicodeEncodeError Exception occurred: skipping a line")
                    except UnicodeDecodeError:
                        self.log_warning("UnicodeDecodeError Exception occurred: skipping a line")
            except UnicodeEncodeError:
                self.log_warning("UnicodeEncodeError Exception occurred: skipping a line")
            except UnicodeDecodeError:
                self.log_warning("UnicodeDecodeError Exception occurred: skipping a line")
            except Exception as e:
                self.log_fail("Error: {} running below command".format(e))
                raise e

        return process.returncode

    def get_probes_config(self, probe_str):
        '''
        Parse the probe string and return the dictionary of probes
        :param probe_str:
        :return: dictionary of probes
        e.g input:"k1=v1,k2=v2, k3=v3"
        output: {'k1': 'v1', 'k2': 'v2', 'k3': 'v3'}
        '''
        probes = {}
        for pair in probe_str.split(','):
            if '=' in pair:
                k, v = pair.split('=')
                probes[k] = v
        return probes

    def get_model_cards(self, directory):
        '''
        Get model cards from the directory and insert them into the database
        :param directory: directory path containing readme.md files for model
        :return: nothing
        '''
        for model_filename in os.listdir(directory):
            try:
                if model_filename.endswith('_README.md'):
                    self.log_info("Processing model card for : {}".format(model_filename))
                    import re
                    model_id = re.sub("_README.md$", "", model_filename)

                    readme_path = os.path.join(directory, model_filename)
                    with open(readme_path, 'r') as file:
                        readme_content = file.read()
                    self.insert_ai_model_card(model_id, readme_content, dt.datetime.fromtimestamp(time.time()))
                    if not self.db_conn:
                        self.set_up_connection()
                    self.db_conn.commit()

                    self.log_info("Model card inserted/updated successfully for : {}".format(model_id))
            except Exception as e:
                    self.log_info("Error: {}".format(e))


    def run(self):
        main_start_time = time.time()
        #if need to process the read me files for model cards for llm models in directory
        # set model_card_only=True and provide the model_card_path in config
        if self.config and self.config['model_card_only']:
            try:
                self.log_info("Processing only model cards from {}".format(self.config['model_card_path']))
                self.get_model_cards(self.config['model_card_path'])
                self.log_info("Completed processing model cards. Duration {} seconds".format(time.time() - main_start_time))
                sys.exit(0)
            except Exception as e:
                self.log_fail("Error: {}".format(e))
                tb = traceback.extract_tb(sys.exc_info()[2])
                tb_str = "\n".join(["\t{}: {}".format(*line) for line in tb])
                self.log_fail("Stack Trace:\n{}".format(tb_str))
                sys.exit(1)





        error_occurred = False
        try:
            if self.dry_run:
                self.log_info("Dry run mode enabled. Following test for given model will be run")

            # run if flag set for benchmarking the llm models
            for llm_ai_model in self.llm_ai_models:
                model_name = llm_ai_model['model_id']
                should_benchmark = llm_ai_model['should_benchmark']
                should_red_team = llm_ai_model['should_red_team']

                db_model_id = self.insert_ai_model(model_name)

                if should_benchmark and self.config['should_benchmark_all']:

                    model_start_time = time.time()
                    #Insert model_id to db

                    test_list = ",".join([test['name'] for test in self.tests])
                    if self.dry_run:
                        self.log_info("{} will execute {} tests: test_list : {}"
                                      .format(model_name, len(test_list.split(',')),test_list))
                        test_list =[]
                        # self.log_info((
                        #     "\nmodel_name: {}, \ntest_list: {}, num_few_shot: {}, batch_size: {}, model_path: {},"
                        #     " eval_output_path: {}, parallelize: {}".format(
                        #         model_name, test_list,
                        #         self.tests[0]['num_few_shot'] if self.tests[0]['num_few_shot'] else None,
                        #         self.tests[0]['batch_size'],
                        #         self.model_path, self.eval_output_path, self.parallelize
                        #     )))
                        continue

                    self.log_info("Started LLM Benchmark evaluation at {}"
                                  .format(time.asctime(time.localtime())))
                    self.log_info("\n ========= Evaluating model: {} =========\n".format(model_name))
                    self.log_info("Running tests: {}".format(test_list))

                    for test in self.tests:

                        test_name = test['name']

                        if 'cuda_devices_cmd' in self.config:  # e.g if running local
                            return_code = self.execute_commands(self.config['cuda_devices_cmd'])
                            if return_code != 0:
                                self.log_warning("CUDA devices are not set.")
                                sys.exit(1)
                            else:
                                self.log_info("CUDA devices are set.")
                                self.log_info("Using cuda devices: {}".format(os.environ['CUDA_VISIBLE_DEVICES']))

                        if test['should_run']:
                            try:
                                start_time = time.time()
                                test_start_time = dt.datetime.fromtimestamp(start_time)

                                #insert test_id to db
                                db_test_id = self.insert_ai_tests(db_model_id, test, TestStatus.STARTED.value,
                                                                  test_start_time, self.test_type,
                                                                  self.config['record_to_db'])
                                self.log_info("test_id: {} for {} for : {}".format(db_test_id, llm_ai_model, test_name))
                                self.log_info("Running test= {} for model= {}".format(test_name, model_name))

                                self.eval_output_path = self.eval_output_base_path + "/{}/".format(
                                    self.get_model_name(model_id=model_name))

                                num_few_shot = None
                                if 'num_few_shot' in test:
                                    num_few_shot = test['num_few_shot']

                                cmd_str = self.generate_lm_eval_cmd(
                                    model_name,
                                    test_name,
                                    num_few_shot,
                                    test['batch_size'],
                                    self.model_path,
                                    self.eval_output_path,
                                    self.parallelize,
                                    test['log_samples'],
                                    test['write_out'],
                                    test['limit_samples']
                                )

                                return_code = 0 if 'snps' in socket.gethostname() else self.execute_commands(cmd_str)

                                if return_code == 0:
                                    self.process_result_info(model_name,
                                                             test,
                                                             self.eval_output_path,
                                                             num_few_shot,
                                                             db_model_id,
                                                             db_test_id
                                                             )
                                duration = time.time() - start_time

                                self.log_info(
                                    "Duration: Test= {} for model= {}  {} seconds".format(test_name, model_name, duration))

                            except Exception as e:

                                self.log_fail("Error: {}".format(e))
                                tb = traceback.extract_tb(sys.exc_info()[2])
                                tb_str = "\n".join(["\t{}: {}".format(*line) for line in tb])
                                self.log_fail("Stack Trace:\n{}".format(tb_str))
                                # self.logger.error("Error: {}\nCaused By: {}".format(e, e.__cause__))
                                self.log_fail("Error: Skipping test= {} for model= {}".format(test_name, model_name))
                                error_occurred = True
                                continue

                        else:
                            self.log_warning("Skipping test= {} for model= {}".format(test_name, model_name))

                    model_duration = time.time() - model_start_time
                    self.log_info("Model Benchmark Evaluation Duration:  for Model= {}  {} seconds"
                                  .format(model_name, model_duration))
                else:
                    self.log_info("Skipping model={} from benchamarking".format(model_name))



                # RED TEAMING Logic goes here

                if should_red_team and self.config['should_red_team_all']:
                    red_team_start_time = time.time()
                    self.log_info("Started Red teaming for model: {} at {} ".format(model_name, red_team_start_time))

                    probes_config = self.get_probes_config(llm_ai_model['red_team_attacks'])
                    probe_name_keys = [key for key, value in probes_config.items() if value == 'True']
                    if "all" in probe_name_keys:
                        self.log_info("Running all probes for {}".format(model_name))
                        probes = self.get_all_probes_from_db()
                    else:
                        probes = probe_name_keys
                    for probe_name in probes:
                        probe_start_time = time.time()
                        try:
                            self.run_red_teaming(db_model_id,
                                                 model_name,
                                                 probe_name,
                                                 llm_ai_model['model_type'],
                                                 self.redteam_output_path
                                                 )
                            #Run the actual probe

                            self.log_info("Completed Red teaming for probe: {} for model: {}  and Duration: {} seconds".
                                          format(probe_name, model_name, time.time() - probe_start_time))

                        except Exception as e:
                            self.log_fail("Error: {}".format(e))
                            tb = traceback.extract_tb(sys.exc_info()[2])
                            tb_str = "\n".join(["\t{}: {}".format(*line) for line in tb])
                            self.log_fail("Stack Trace:\n{}".format(tb_str))
                            self.log_fail("Error: Red Team Skipping probe= {} for model= {}".format(probe_name,
                                                                                                    model_name))
                            error_occurred = True
                            continue

                else:
                    self.log_info("Skipping model={} from red teaming".format(model_name))











                all_tests_duration = time.time() - main_start_time
                if error_occurred == False and self.dry_run == False:
                    self.log_info(
                        "Completed LLM Benchmark and Red Team evaluation at {}."
                            .format(time.asctime(time.localtime())))

                elif error_occurred == True and self.dry_run == False:
                    self.log_warning(
                        "Completed LLM Benchmark and Red Team evaluation at {} with some some failures . check logs "
                        "for more information ".format(time.asctime(time.localtime())))
                self.log_info("Total Duration: {} seconds for whole Benchmark and RedTeaming test suite".
                              format(all_tests_duration))

            # run if there needs to do AI Red teaming on the llm models



        except Exception as e:
            self.log_fail("Error: {}".format(e))
            tb = traceback.extract_tb(sys.exc_info()[2])
            tb_str = "\n".join(["\t{}: {}".format(*line) for line in tb])
            self.log_fail("Stack Trace:\n{}".format(tb_str))
            # self.log_fail("Error: {}\nCaused By: {}".format(e, e.__cause__))
            sys.exit(1)

    def generate_red_teaming_cmd(self, model_id, probe_name, model_type, report_prefix):

        cmd_str = "python -m garak --model_type {} --model_name {} --report_prefix {} --probes {}"\
            .format(model_type,
                    model_id,
                    report_prefix,
                    probe_name)
        self.log_info("Red Teaming Generated command: {}".format(cmd_str))

        return cmd_str

    def run_red_teaming(self, db_model_id,
                        model_name,
                        probe_name,
                        model_type,
                        redteam_output_path):
        start_time = time.time()
        probe_start_time = dt.datetime.fromtimestamp(start_time)

        self.log_info("Running probe: {} for model: {}".format(probe_name, model_name))

        report_prefix = probe_name + "_" + model_name
        db_probe_test_id = self.insert_ai_red_team_test(probe_name + "_" + db_model_id,
                                                        db_model_id,
                                                        TestStatus.STARTED.value,
                                                        probe_start_time)
        if db_probe_test_id:
            self.db_conn.commit()
            self.log_info("db_probe_test_id: {} for model: {} for probe : {}".format(db_probe_test_id, model_name, probe_name))
            pass
        cmd_str = self.generate_red_teaming_cmd(model_name, probe_name, model_type, report_prefix)

        # return_code = 0 if 'snps' in socket.gethostname() else self.execute_commands(cmd_str)
        return_code = self.execute_commands(cmd_str)
        if return_code == 0:
            self.process_red_team_results(model_name,
                                          probe_name,
                                          db_model_id,
                                          db_probe_test_id,
                                          report_prefix)


        print("return code", return_code)

    def process_red_team_results(self, model_name, probe_name, db_model_id, db_probe_test_id, report_prefix):
        report_filepath = os.path.join(report_prefix + ".report.jsonl")
        hitlog_filepath = os.path.join(report_prefix + ".hitlog.jsonl")
        html_filepath = os.path.join(report_prefix + ".report.html")

        if os.path.exists(report_filepath) and os.path.exists(hitlog_filepath) and os.path.exists(html_filepath):
            self.extract_red_team_report_result(report_filepath,
                                              model_name,
                                              probe_name,
                                              db_model_id,
                                              db_probe_test_id)
            # self.extract_red_team_hitlog_result(report_filepath,
            #                                     model_name,
            #                                     probe_name,
            #                                     db_model_id,
            #                                     db_probe_test_id)
            #
            # self.extract_red_team_html_result(report_filepath,
            #                                     model_name,
            #                                     probe_name,
            #                                     db_model_id,
            #                                     db_probe_test_id)

            new_report_filepath = os.path.join(self.redteam_output_path, model_name + "_" + probe_name + ".report.jsonl")
            shutil.move(report_filepath, new_report_filepath)
            new_hitlog_filepath = os.path.join(self.redteam_output_path, model_name + "_" + probe_name + ".hitlog.jsonl")
            shutil.move(hitlog_filepath, new_hitlog_filepath)
            new_html_filepath = os.path.join(self.redteam_output_path, model_name + "_" + probe_name + ".report.html")
            shutil.move(html_filepath, new_html_filepath)

        else:
            msg = "One or more report files from {},{},{} not found".format(report_filepath, hitlog_filepath,
                                                                               html_filepath)
            self.log_fail(msg)
            raise Exception(msg)

        pass

    def extract_red_team_report_result(self, report_filepath, model_name, probe_name, db_model_id, db_probe_test_id):
        with open(report_filepath, 'r') as f:

            try:
                results = self.parse_probe_results(report_filepath)
                print(results)

            except Exception as e:
                raise e
        pass


# Usage example:
if __name__ == "__main__":
    runner = LLMBenchmarkRunner()
    runner.run()
