import logging
import time
import io

from ..connections.redis import get_connection_info

logger = logging.getLogger("device_command_handler")


class DeviceCommandHandler:
    def __init__(self, client, timeout: float = 2):

        config = get_connection_info()
        self.mode = config.get("mode", "adb")
        self.host = config.get("host")
        self.port = config.get("port", 5555)

        self.timeout = timeout

        self.client = client
        self.device = None
        self.session_pool = {}

        if self.mode == "adb":
            self.device = client.device(f"{self.host}:{self.port}")

    def initialize_session(self, command):
        if self.mode == "adb":
            self.session_pool[command] = self.create_connection()
            if self.session_pool[command] is None:
                raise Exception("ADB Invalid IP or Port")

    def create_connection(self) -> any:
        start_time = time.time()
        # time out을 설정하고, create_connection에 성공할 때 까지 계속 시도
        while True:
            try:
                time.sleep(0.1)
                return self.device.create_connection(timeout=self.timeout)
            except Exception as e:
                if time.time() - start_time >= self.timeout:
                    logger.error(f"Create session error: {e}")
                    return None

    def is_session_valid(self, command):
        if command not in self.session_pool:
            return False

        try:
            session = self.session_pool[command]
            if not session or not session.socket:
                return False

            if session.socket.fileno() == -1:
                return False

            return True
        except Exception as e:
            logger.error(f"is_session_valid error: {e}")
            return False

    def ensure_valid_session(self, command):
        try:
            if not self.is_session_valid(command):
                if command in self.session_pool:
                    try:
                        self.session_pool[command].close()
                    except Exception:
                        pass

                self.initialize_session(command)
            else:
                logger.info("used prev session")

        except Exception as e:
            raise Exception(f"Session validation error: {e}")

    def preprocess_stdout_stream(self, stdout: io.TextIOWrapper, command):
        retry_count = 0
        max_retries = 10
        try:
            while True:
                try:
                    line = stdout.readline()
                    if line == "":  # EOF 도달
                        break
                    retry_count = 0
                    yield line

                except Exception as e:
                    if retry_count >= max_retries:
                        break
                    logger.error(f"Stream read error: {e}")
                    retry_count += 1

                    line = ""

                    while True:
                        try:
                            if self.mode == "adb":
                                x = stdout.read(1).encode()
                            else:
                                x = stdout.read(1)

                            if not x:  # EOF 체크
                                return

                            line += x.decode()
                            if x == b"\n":
                                yield line
                                break

                        except Exception as e:
                            if retry_count >= max_retries:
                                break
                            retry_count += 1
                            logger.error(f"Byte read error: {e}")
                            time.sleep(0.1)
        except Exception as e:
            raise Exception(f"Error processing stdout: {e}")
        finally:
            # 리소스 정리
            self.close_client(stdout, command)

    def close_client(self, stdout: io.TextIOWrapper, command):
        if self.mode == "ssh":
            self.client.close()
        elif self.mode == "adb":
            stdout.close()
            if self.session_pool[command]:
                self.session_pool[command].close()
        del stdout

    def exec_command(self, command: str):
        if self.mode == "ssh":
            stdin, stdout, stderr = self.client.exec_command(command)
        elif self.mode == "adb":
            self.ensure_valid_session(command)
            cmd = "shell:{}".format(command)
            self.session_pool[command].send(cmd)
            socket = self.session_pool[command].socket
            socket.settimeout(self.timeout)
            stdout = socket.makefile()
        return self.preprocess_stdout_stream(stdout, command)
