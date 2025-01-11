"""接口请求子线程"""

import time
import json
from json.decoder import JSONDecodeError
from PySide6.QtCore import QThread, Signal
from requests import request, Response
from requests.exceptions import MissingSchema, ReadTimeout, InvalidURL
from httpgogui.utils.enum.error import ErrorEnum


class WorkerThread(QThread):
    """子线程类"""

    progress = Signal(bool, Response)  # 定义一个信号，传递是否开启loading

    def __init__(
        self,
        method: str,
        url: str,
        body: str,
        params: dict,
        headers: dict,
        cookies: dict,
    ):
        super().__init__()
        self.method = method
        self.url = url
        self.body = body
        self.params = params
        self.headers = headers
        # 简化token的输入
        if token := self.headers.get("Authorization", None):
            if token.find("bearer") == -1:
                self.headers["Authorization"] = "bearer " + token
        self.cookies = cookies

    def run(self):
        """使用父类run函数，子线程发送接口请求"""
        self.progress.emit(True, None)  # 请求开始，发送loading信号
        try:
            method = self.method
            url = self.url
            body = self.body
            if body != "":
                body = json.loads(body)
        except JSONDecodeError:
            # 序列化失败时发送失败信号
            self.progress.emit(False, ErrorEnum.JSONDECODEERROR)
            return

        params = self.params
        headers = self.headers
        cookies = self.cookies
        print("开始接口请求...")
        start_time = time.time()
        try:
            response = request(
                method=method,
                url=url,
                json=body,
                headers=headers,
                params=params,
                cookies=cookies,
                timeout=15,
            )
            end_time = time.time()
            # 打印控制台输出
            print(f"status code: {response.status_code}", end="\n\n")
            print(f"response time: {end_time - start_time}s", end="\n\n")
            print(
                f"response header: \n {json.dumps(dict(response.headers.__dict__.get('_store',None)),indent=4)}",
                end="\n\n",
            )
            # print()
            try:
                print(
                    f"response body: \n {json.dumps(response.json(),indent=4)}",
                    end="\n\n",
                )
            except Exception:
                print(f"response body: \n {response.text}", end="\n\n")
            self.progress.emit(False, response)  # 请求结束，返回信号
        except MissingSchema:
            # 请求参数错误返回信号
            self.progress.emit(False, ErrorEnum.MISSINGSCHEMA)
        except InvalidURL:
            self.progress.emit(False, ErrorEnum.INVALIDURL)
        except ReadTimeout:
            self.progress.emit(False, ErrorEnum.READTIMEOUT)
