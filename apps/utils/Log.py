import os
import logging
from datetime import datetime
import threading



class Log:
    def __init__(self, log_name=None, log_batch=None, log_type=None):
        global resultPath, proDir
        self.log_batch = log_batch
        self.log_type = log_type
        if log_name is None:
            self.log_name = 'output.log'
        else:
            self.log_name = log_name

        proDir = os.path.abspath(os.curdir)
        resultPath = os.path.join(proDir, "result")
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        if not os.path.exists(resultPath):
            os.mkdir(resultPath)
        if log_batch is None:
            self.logPath = os.path.join(resultPath, str(datetime.now().strftime("%Y%m%d%H%M%S")))
        else:
            self.logPath = os.path.join(resultPath, log_batch)

        if not os.path.exists(self.logPath):
            os.mkdir(self.logPath)
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)

        # defined handler
        if self.log_type == 'run_opt':
            self.handler_run_opt = logging.FileHandler(os.path.join(self.logPath, log_name))
            self.handler_run_opt.setFormatter(formatter)
            self.logger.addHandler(self.handler_run_opt)

        elif self.log_type == 'init_gp':
            self.handler_init_gp = logging.FileHandler(os.path.join(self.logPath, log_name))
            self.handler_init_gp.setFormatter(formatter)
            self.logger.addHandler(self.handler_init_gp)

        elif self.log_type == 'run_single_case':
            self.handler_run_single_case = logging.FileHandler(os.path.join(self.logPath, log_name))
            self.handler_run_single_case.setFormatter(formatter)
            self.logger.addHandler(self.handler_run_single_case)

        elif self.log_type == 'run_all_case':
            self.handler_run_all_case = logging.FileHandler(os.path.join(self.logPath, log_name))
            self.handler_run_all_case.setFormatter(formatter)
            self.logger.addHandler(self.handler_run_all_case)

        else:
            self.handler = logging.FileHandler(os.path.join(self.logPath, log_name))
            self.handler.setFormatter(formatter)
            self.logger.addHandler(self.handler)

    def get_logger(self):
        """
        get logger
        :return:
        """
        return self.logger

    # def get_result_path(self):
    #     """
    #     get test result path
    #     :return:
    #     """
    #     return self.logPath
    #
    # def write_result(self, result):
    #     """
    #
    #     :param result:
    #     :return:
    #     """
    #     result_path = os.path.join(self.logPath, "report.txt")
    #     fb = open(result_path, "wb")
    #     try:
    #         fb.write(result)
    #     except FileNotFoundError as ex:
    #         self.logger.error(str(ex))

    # 清除文件内容
    def clear_logContent(self):
        result_path = os.path.join(self.logPath, self.log_name)
        with open(result_path, 'r+') as file:
            try:
                file.truncate(0)
            except FileNotFoundError as ex:
                self.logger.error(str(ex))

    # 获取文件内容
    def get_logContent(self):
        result_path = os.path.join(self.logPath, self.log_name)
        fb = open(result_path, "r+")
        try:
            lines = fb.read()
            fb.close()
            return lines
        except FileNotFoundError as ex:
            return self.logger.error(str(ex))

    # 获取文件内容
    def remove_handler(self):
        if self.log_type == 'run_opt':
            self.logger.removeHandler(self.handler_run_opt)

        elif self.log_type == 'init_gp':
            self.logger.removeHandler(self.handler_init_gp)

        elif self.log_type == 'run_single_case':
            self.logger.removeHandler(self.handler_run_single_case)

        elif self.log_type == 'run_all_case':
            self.logger.removeHandler(self.handler_run_all_case)

        else:
            self.logger.removeHandler(self.handler)


class MyLog:
    log = None
    mutex = threading.Lock()

    def __init__(self):
        pass

    @staticmethod
    def get_log(log_name=None, log_batch=None, log_type=None):

        # if MyLog.log is None:
        MyLog.mutex.acquire()
        MyLog.log = Log(log_name, log_batch, log_type)
        MyLog.mutex.release()
        return MyLog.log