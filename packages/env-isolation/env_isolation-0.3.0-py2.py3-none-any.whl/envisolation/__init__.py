import logging
import subprocess
import threading
import requests
import time
import queue
import os
import shutil
import json
import tempfile
import socket
import hashlib

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__)).rstrip("/")


class EnvIsolatedModel:
    env_lock = {}

    def __init__(
        self,
        model_id: str,
        model_path: str,
        pip_requirements_path: str,
        model_arguments: dict = {},
        base_env_dir: str | None = None,
        readiness_probe_timeout_s: int = 300,
        host_port: int | None = None,
        python_executable="python",
    ):
        self.host_port = (
            host_port if host_port != None else self.__get_free_listenable_port()
        )
        self.model_id = model_id
        self.model_arguments = model_arguments
        self.python_executable = python_executable
        self.model_path = model_path
        self.pip_requirements_path = pip_requirements_path
        self.base_env_dir = base_env_dir
        self.readiness_probe_timeout_s = readiness_probe_timeout_s
        self.env_dir = self.__install_dependencies()
        self.model_url = self.__load_model()

    def execute(self, arguments: dict) -> dict:
        if not self.is_loaded:
            raise Exception(f"Model {self.model_id} is not loaded.")

        model_exec_url = f"{self.model_url}/execute"

        start_time_run = time.time()
        res = requests.post(model_exec_url, json=arguments).json()
        self.last_active_unix_s = time.time()
        return res, {
            "model_id": self.model_id,
            "duration": {
                "exec_s": time.time() - start_time_run,
            },
        }

    def unload(self, unload_env: bool = False):
        logging.info(f"Unloading model {self.model_id} on port {self.host_port}...")
        try:
            requests.post(f"{self.model_url}/exit")
        except Exception:
            pass

        if unload_env:
            # TODO: shared folders are also removed
            shutil.rmtree(self.env_dir)

        time.sleep(1)
        self.is_loaded = False
        logging.info(f"Model {self.model_id} on port {self.host_port} removed.")

    def __load_model(self) -> str:
        model_url = f"http://127.0.0.1:{self.host_port}"
        healthy_url = f"{model_url}/healthy"

        try:
            requests.get(healthy_url)
            return model_url
        except:
            logging.info(
                f"Loading model env-isolated {self.model_id} on port {self.host_port}..."
            )

            message_queue = queue.Queue()
            error_found = [False]

            def stream_output(pipe, message_queue):
                for line in iter(pipe.readline, b""):
                    decoded_line = line.decode().strip()
                    if len(decoded_line) > 0:
                        logging.info(
                            f"Model {self.model_id} (port {self.host_port}): {decoded_line}"
                        )
                        message_queue.put(decoded_line)
                pipe.close()

            def stream_output_stderr(pipe, message_queue, error_found):
                stream_output(pipe, message_queue)
                error_found[0] = True

            with tempfile.TemporaryDirectory() as tmpdirname:
                temp_arguments_path = os.path.join(tmpdirname, "arguments.json")

                with open(temp_arguments_path, "w") as f:
                    json.dump(self.model_arguments, f)

                process = subprocess.Popen(
                    f'bash -c "cd {self.model_path} && {self.env_dir}/.env/bin/{self.python_executable} {SCRIPT_DIR}/model_executor.py --port {int(self.host_port)} --model-id={self.model_id} --model-path={os.path.abspath(self.model_path)} --model-arguments-path={temp_arguments_path}"',
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )

                threading.Thread(
                    target=stream_output, args=(process.stdout, message_queue)
                ).start()
                threading.Thread(
                    target=stream_output_stderr,
                    args=(process.stderr, message_queue, error_found),
                ).start()

                for i in range(
                    int(float(self.readiness_probe_timeout_s - 1) / 2.0) + 5
                ):
                    try:
                        requests.get(healthy_url)
                        logging.debug(f"Model {self.model_id} is now available.")
                        self.is_loaded = True
                        return model_url
                    except:
                        time.sleep(0.2 if i < 5 else 3)
                        if error_found[0] == True:
                            self.is_loaded = False
                            raise Exception(
                                f"Model {self.model_id} failed: {self.__message_queue_to_str(message_queue)}"
                            )
                        continue

                self.is_loaded = False
                raise Exception(
                    f"Model {self.model_id} failed to start on port {self.host_port}: {self.__message_queue_to_str(message_queue)}"
                )

    def __install_dependencies(self):
        logging.debug(f"Installing dependencies for model {self.model_id}...")

        if not os.path.exists(self.pip_requirements_path):
            raise Exception(
                f"Requirements file {self.pip_requirements_path} not found."
            )

        env_dir = self.__get_model_env_dir(self.pip_requirements_path)

        if env_dir not in EnvIsolatedModel.env_lock:
            EnvIsolatedModel.env_lock[env_dir] = threading.Lock()

        with EnvIsolatedModel.env_lock[env_dir]:
            if os.path.exists(env_dir):
                return os.path.abspath(env_dir)

            os.makedirs(env_dir, exist_ok=True)
            tmp_requirements_path = f"{env_dir}/requirements.txt"

            with open(self.pip_requirements_path, "r") as f:
                required_content = f.read().strip()

            with open(tmp_requirements_path, "w") as f:
                f.write(required_content)

            if self.base_env_dir != None and self.base_env_dir != "":
                logging.debug(
                    f"Creating virtual environment for model {self.model_id} in dir {env_dir} by using base dir {self.base_env_dir}..."
                )
                os.system(
                    f"bash -c 'cp -r {self.base_env_dir} {env_dir}/.env && cd {env_dir} && {env_dir}/.env/bin/{self.python_executable} -m pip install -r {tmp_requirements_path}'"
                )
            else:
                logging.debug(
                    f"Creating virtual environment for model {self.model_id} in dir {env_dir}..."
                )
                os.system(
                    f"bash -c 'cd {env_dir} && {self.python_executable} -m venv .env && {env_dir}/.env/bin/{self.python_executable} -m pip install -r {tmp_requirements_path}'"
                )

            return os.path.abspath(env_dir)

    def __get_model_env_dir(self, required_file: str):
        with open(required_file, "r") as f:
            content = f.read().strip()

        dir_name = hashlib.sha256(content.encode("utf-8")).hexdigest()

        env_dir = os.path.join(tempfile.gettempdir(), dir_name)
        return os.path.abspath(env_dir)

    def __message_queue_to_str(self, message_queue: queue.Queue):
        messages = []
        while not message_queue.empty():
            messages.append(message_queue.get())

        return "\n".join(messages)

    def __get_free_listenable_port(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("", 0))  # Bind to a free port provided by the OS
            s.listen(1)  # Ensure the port can be listened to
            return s.getsockname()[1]
