import time
import os
import subprocess
import logging
from ppadb.client import Client as AdbClient
from paramiko import SSHClient, AutoAddPolicy
from threading import Thread
from multiprocessing import Queue, Event
import clickhouse_connect
from datetime import datetime

import numpy as np
from PIL import Image

from ..core.config import settings
from ..core.rabbitmq.rabbitmq_utils import publish_message_by_shell


def pilToNumpy(img):
    return np.array(img)


def NumpyToPil(img):
    return Image.fromarray(img)


logger = logging.getLogger("connection")


class Connection:
    def __init__(
        self, mode, host, port, username=None, password=None, consume_method=None
    ) -> None:

        self.mode = mode
        self.host = host
        self.port = port
        if consume_method is not None:
            # callable 과 call signiture를 정의
            self.consume_queue = consume_method
        if mode == "adb":
            self.connected = False
            try:
                os.system("adb kill-server")
                os.system("adb start-server")
                os.system(f"adb tcpip {port}")
                time.sleep(2)
                self.client = AdbClient(host="127.0.0.1", port=5037)
                if not self.client.remote_connect(host, int(port)):
                    raise Exception("Remote connection failed")

                self.connected = True
                logger.info("Successfully ADB connection")
            except Exception as e:
                logger.error(f"Failed ADB connection -> {e}")
        elif mode == "ssh":
            self.connected = False
            try:
                self.client = SSHClient()
                self.client.set_missing_host_key_policy(AutoAddPolicy)
                self.client.connect(
                    hostname=host,
                    port=port,
                    username=username,
                    password=password,
                    timeout=2,
                )
                self.device = self.client.invoke_shell()
            except Exception as e:
                logger.error(f"Failed SSH connection -> {e}")
        else:
            self.connected = False

    def adb_disconnect(self, host, port):
        try:
            client = AdbClient(host="127.0.0.1", port=5037)
            devices = client.devices()
            device_exists = any(d.serial == f"{host}:{port}" for d in devices)
            if device_exists:
                client.remote_disconnect(host, int(port))
                self.connected = False
                logger.info(f"success adb disconnect")
            else:
                raise Exception(f"device doesn't exist in adb -> Failed disconnect")
        except Exception as e:
            raise Exception(f"adb disconnect Unexpected error: {e}")

    def shell(self, cmd, timeout=1):
        response = None
        shell_cmd_time = datetime.now()
        self.clickhouse_client = clickhouse_connect.get_client(
            host=settings.CLICKHOUSE_HOST,
            port=settings.CLICKHOUSE_PORT,
            username=settings.CLICKHOUSE_USERNAME,
            password=settings.CLICKHOUSE_PASSWORD,
        )
        if self.mode == "adb":
            self.device = self.client.device(f"{self.host}:{self.port}")
            response = self.device.shell(cmd, timeout=timeout)
        elif self.mode == "ssh":
            _, stdout, _ = self.client.exec_command(cmd)
            response = stdout.read().decode("utf-8")
        if response is not None:
            data = [
                (
                    datetime.now(),  # timestamp (DateTime64(6))
                    "I",  # log_level (FixedString(1))
                    "pid",  # pid (String)
                    "tid",  # tid (String)
                    "module",  # module (String)
                    x,  # message (String)
                    "process",  # process_name (String)
                    "shell",  # service (String)
                    "shell_output",  # type (String)
                )
                for x in response.split("\n")
            ]
            data.insert(
                0,
                (
                    shell_cmd_time,  # timestamp (DateTime64(6))
                    "I",  # log_level (FixedString(1))
                    "pid",  # pid (String)
                    "tid",  # tid (String)
                    "module",  # module (String)
                    cmd,  # message (String)
                    "process",  # process_name (String)
                    "shell",  # service (String)
                    "shell_input",  # type (String)
                ),
            )
            res = self.clickhouse_client.insert(
                "default.logcat",
                data,
                column_names=[
                    "timestamp",
                    "log_level",
                    "pid",
                    "tid",
                    "module",
                    "message",
                    "process_name",
                    "service",
                    "type",
                ],
            )
            logger.info(f"shell clickhouse insert result: {res}")
        return response

    def close(self):
        if self.client:
            self.client.close()

    def capture(self):
        if self.mode == "adb":
            im = self.device.screenshot()
            if isinstance(im, Image.Image):
                b, g, r = im.split()
                im = Image.merge("RGB", (r, g, b))
                return pilToNumpy(im)
            return None

    def cmd_output_gen(self, command, stop_event: Event, queue):
        if self.mode == "adb":
            stream = self.device.shell(command, stream=True)
            with stream.conn.makefile(encoding="utf-8") as f:
                for line in f:
                    queue.put((datetime.now(), line))
                    if stop_event.is_set():
                        break
                stop_event.set()

            stream.close()
            logger.info("end:cmd_output_gen")

        elif self.mode == "ssh":
            # self.device = self.client.invoke_shell()
            _, stdout, _ = self.client.exec_command(command)
            with stdout:
                for line in stdout:
                    queue.put((datetime.now(), line))
                    if stop_event.is_set():
                        break
                stop_event.set()

    @staticmethod
    def cmd_timer(timeout: float | None, stop_event: Event):
        logger.info("Timer end")
        start = time.time()
        while True:
            time.sleep(0.02)
            current = time.time()
            if timeout is not None and current - start > timeout or stop_event.is_set():
                break
        stop_event.set()
        logger.info("Timer end")

    @staticmethod
    def consume_queue(queue, stop_event):
        logger.info(">>>start  main_consume")
        while True:
            if stop_event.is_set():
                break
            if queue.empty():
                continue
            msg = queue.get()
            logger.info(msg)
        logger.info(">>>exit_main_consume")
        while True:
            if queue.empty():
                break
            msg = queue.get()
            logger.info(msg)
        stop_event.set()
        logger.info(">>>>exit_consume_queue")

    def run_command(self, command, timeout=5):
        stop_event = Event()
        stop_event.clear()
        queue = Queue()
        gen = Thread(
            target=self.cmd_output_gen,
            kwargs={"command": command, "stop_event": stop_event, "queue": queue},
        )
        timer = Thread(
            target=self.cmd_timer, kwargs={"timeout": timeout, "stop_event": stop_event}
        )
        consume = Thread(
            target=self.consume_queue, kwargs={"queue": queue, "stop_event": stop_event}
        )
        gen.start()
        timer.start()
        consume.start()
        consume.join()
        gen.join()
        timer.join()


def init_adb(host: str, port: int):
    try:
        os.system(f"adb connect {host}:{port}")
        os.system("adb devices")
    except Exception as e:
        logger.error(f"Error: {e}")
        return False


def restart_adb():
    try:
        os.system("adb kill-server")
        os.system("adb start-server")
    except Exception as e:
        logger.error(f"Error: {e}")
        return False


def check_connection(connection_info: dict) -> bool:
    try:
        # Connection 시도 후 끊기
        if connection_info["connection_mode"] == "ssh":
            Connection(**connection_info).client.close()
        elif connection_info["connection_mode"] == "adb":
            Connection(**connection_info).session.close()
        # Connection 시도 후 끊기가 정상적으로 동작할 경우 연결가능 상태
        is_connected = True
    except Exception as e:
        # Connection 시도 후 끊기가 정상적으로 동작하지 않을 경우 연결불가 상태
        is_connected = False
    return is_connected


ADB_KEY_MAP = {
    "right": "input keyevent KEYCODE_DPAD_RIGHT",
    "left": "input keyevent KEYCODE_DPAD_LEFT",
    "up": "input keyevent KEYCODE_DPAD_UP",
    "down": "input keyevent KEYCODE_DPAD_DOWN",
    "ok": "input keyevent KEYCODE_DPAD_CENTER",
    "back": "input keyevent KEYCODE_BACK",
    "home": "input keyevent KEYCODE_HOME",
    # 아래쪽을 터틀 키라고 정의: adb가 아닌 ir로 처리 해야 함.
    "menu": "input keyevent KEYCODE_HOME",  # duplication
    "exit": "input keyevent KEYCODE_SKB_FUNC_01",  # lg에서는 쓰지 못함.
}


def get_ui_automator_xml() -> str:
    # execute ui automator
    subprocess.call(["adb", "shell", "uiautomator", "dump"])
    subprocess.call(["adb", "pull", "/sdcard/window_dump.xml"])

    # Sample XML data (replace with your XML string)
    # read xml data from file
    file_path = "window_dump.xml"
    with open(file_path, "r", encoding="utf-8") as f:
        xml_data = f.read()
    return xml_data
