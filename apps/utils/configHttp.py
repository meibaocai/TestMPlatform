# _*_ encoding:utf-8 _*_
import requests
from utils.Log import MyLog as Log
import json, os
proDir = os.path.split(os.path.realpath(__file__))[0]

class ConfigHttp:

    def __init__(self):
        global timeout
        timeout = 60.0
        # self.log = Log.get_log()
        # self.logger = self.log.get_logger()
        self.headers = {}
        self.cookies = {}
        self.params = {}
        self.data = {}
        self.url = None
        self.files = {}
        self.state = 0

    def set_url(self, url):
        """
        set url
        :param: interface url
        :return:
        """
        self.url = url

    def set_headers(self, header):
        """
        set headers
        :param header:
        :return:
        """
        self.headers = header

    def set_cookies(self, cookies):
        """
        set cookies
        :param cookies:
        :return:
        """
        self.cookies = cookies

    def set_params(self, param):
        """
        set params
        :param param:
        :return:
        """
        self.params = param

    def set_data(self, data):
        """
        set data
        :param data:
        :return:
        """
        self.data = data

    def set_files(self, filename):
        """
        set upload files
        :param filename:
        :return:
        """
        if filename != '':
            file_path = proDir+'/' + filename
            self.files = {'file': open(file_path, 'rb')}

        if filename == '' or filename is None:
            self.state = 1

    # defined http get method
    def get(self):
        """
        defined get method
        :return:
        """
        try:
            response = requests.get(self.url, headers=self.headers, cookies=self.cookies, params=self.params, timeout=float(timeout))
            # response.raise_for_status()
            return response
        except TimeoutError:
            # self.logger.error("Time out!")
            return None

    # defined http post method
    # include get params and post data
    # uninclude upload file
    def post(self):
        """
        defined post method
        :return:
        """
        response = requests.post(self.url, headers=self.headers, cookies=self.cookies, params=self.params, data=self.data, timeout=5.0)

        try:
            # response.raise_for_status()
            return response
        except TimeoutError:
            # self.logger.error("Time out!")
            return None

    # defined http post method
    # include upload file
    def postWithFile(self):
        """
        defined post method
        :return:
        """
        try:
            response = requests.post(self.url, headers=self.headers, cookies=self.cookies, data=self.data, files=self.files, timeout=float(timeout))
            return response
        except TimeoutError:
            # self.logger.error("Time out!")
            return None

    # defined http post method
    # for json
    def postWithJson(self):
        """
        defined post method
        :return:
        """
        try:
            response = requests.post(self.url, headers=self.headers, cookies=self.cookies, json=self.data, timeout=float(timeout))
            return response
        except TimeoutError:
            # self.logger.error("Time out!")
            return None

# if __name__ == "__main__":
#     print("ConfigHTTP")
