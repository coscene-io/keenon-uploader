# -*- coding:utf-8 -*-
import json
import os
import signal
import sys
import time
import traceback

import scandir
from strictyaml import load, YAMLError

import cos

try:
    # noinspection PyCompatibility
    from pathlib import Path
except ImportError:
    from pathlib2 import Path


class KNMod:
    def __init__(self, api, cm):
        self.api = api
        self.base_dir = cm.get('base_dir')

        _XDG_DIR = Path(os.getenv('XDG_CONFIG_HOME') or '~/.config').expanduser() / 'cos'
        self.code_limit_file = str(Path(_XDG_DIR, "code_limit.json").absolute())

        self.code_limit = str(cm.get('code_limit')).lower() == 'true'
        if self.code_limit:
            self.code_white_list = json.loads(cm.get('code_white_list'))

        def signal_handler(sig, _):
            print("\nProgram exiting gracefully by {sig}".format(sig=sig))
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)

    def _find_error_json(self):
        Path(self.base_dir).mkdir(parents=True, exist_ok=True)
        for entry in scandir.scandir(self.base_dir):
            if entry.name.endswith('.json') and entry.is_file():
                yield os.path.join(self.base_dir, entry.name)

    def _convert_record_title(self, error_json_path):
        """Converts an error JSON file path to a record title.

        Args:
            error_json_path (str): The path to the error JSON file.

        Returns:
            str: The error message, or the basename of the error directory
                if the error message cannot be found.
        """
        error_dir, _ = error_json_path.rsplit('.', 1)
        with open(error_json_path, 'r') as fp:
            error_json = json.load(fp)

        code = str(error_json.get('code', ''))
        time_tuple = time.localtime(time.time())
        default_name = time.strftime("%Y-%m-%d-%H-%M-%S", time_tuple)

        if not str(code):
            return default_name
        return "{code}-{default_name}".format(code=code, default_name=default_name)

    def _create_or_get_device(self, error_json_path):
        """Creates a new device or gets an existing device.

        Args:
            error_json_path (str): The path to the error JSON file.

        Returns:
            dict: The device information.
        """
        with open(error_json_path, 'r') as fp:
            error_json = json.load(fp)

        device_yaml_path = error_json.get('deviceMsgYaml', '')
        if not device_yaml_path or not Path(device_yaml_path).exists() or not Path(device_yaml_path).is_file():
            return {}

        with open(str(Path(device_yaml_path).absolute()), "r") as y:
            try:
                device_yaml = load(y.read()).data
            except YAMLError as exc:
                raise cos.CosException("Failed to load device yaml: {exc}".format(exc=exc))

        sn = device_yaml.get('product_id', '')
        device = self.api.get_device_by_sn(sn)
        if device:
            print ("==> Found an existing device {sn}".format(sn=sn))
            return device

        labels = {
            'deviceModel': device_yaml.get('model_type', ''),
            'deviceSensorType': device_yaml.get('sensor_type', ''),
            'deviceCid': device_yaml.get('cid', ''),
            'deviceSessionId': device_yaml.get('session_id', ''),
            'deviceKey': device_yaml.get('key', ''),
            'deviceType': device_yaml.get('type', ''),
        }
        device = self.api.create_device(sn, labels=labels)
        if device:
            print("==> Created a new device {sn}".format(sn=sn.encode('utf-8')))
            return device
        print("==> Failed to create a new device")
        return {}

    def _create_event(self, error_json_path, record, device=None):
        if not record:
            return None
        if not device:
            device = {}
        record_name = record.get('name', '')
        if not record_name:
            return None

        with open(error_json_path, 'r') as fp:
            error_json = json.load(fp)
        title = self._convert_record_title(error_json_path)
        event = {
            "display_name": title,
            "description": title,
            "customized_fields": {
                "code": str(error_json.get('code', '')),
            },
            "trigger_time": {
                "seconds": int(time.time()),
            },
        }
        if device:
            event['device'] = {
                "name": device.get('name', ''),
            }
        self.api.create_event(record_name, event)

    def _handle(self, error_json_path):
        print("==> Find an error json {error_json_path}".format(
            error_json_path=error_json_path
        ))
        if not os.path.exists(error_json_path):
            print ("==> Error json {error_json_path} not exists".format(
                error_json_path=error_json_path
            ))
            return

        with open(error_json_path, 'r') as fp:
            error_json = json.load(fp)
        bags = error_json.get('bag', [])
        logs = error_json.get('log', [])
        files = []
        for f in bags + logs:
            if not os.path.exists(f):
                print("==> File {file} not exists".format(file=f))
                continue
            files.append(f)
        print("==> Files to upload: \n\t{files}".format(
            files="\n\t".join(files)
        ))
        if len(files) == 0:
            print("==> No files to upload")
            return

        with open(error_json_path, 'r') as fp:
            error_json = json.load(fp)
        record_name = error_json.get('recordName', None)
        device = self._create_or_get_device(error_json_path)
        title = self._convert_record_title(error_json_path)
        record = self.api.create_or_get_record(title, files,
                                               device=device.get('name', None),
                                               record_name=record_name)
        if not record_name:
            error_json['recordName'] = record.get('name', '') if record else ''
            with open(error_json_path, 'w') as fp:
                json.dump(error_json, fp, indent=4)

        self.api.upload_files(files, record)
        self._create_event(error_json_path, record, device)

        if self.code_limit:
            with open(self.code_limit_file, 'r+') as fp:
                code_limit_json = json.load(fp)

                code_request = int(code_limit_json.get(str(error_json.get('code')), 0)) + 1
                code_limit_json[str(error_json.get('code'))] = code_request

                fp.seek(0)
                json.dump(code_limit_json, fp, indent=4)

    def _check_code_limit(self, code):
        if not self.code_limit:
            return False
        if not code:
            print ("==> No code found, skip handle err file")
            return True
        if not Path(self.code_limit_file).exists():
            Path(self.code_limit_file).parent.mkdir(parents=True, exist_ok=True)
            with open(self.code_limit_file, 'w') as fp:
                json.dump({"timestamp": int(time.time())}, fp, indent=4)
        else:
            with open(self.code_limit_file, 'r') as fp:
                code_limit_json = json.load(fp)
            timestamp = int(code_limit_json.get('timestamp', 0))
            if abs(int(time.time()) - timestamp) > 24 * 60 * 60:
                with open(self.code_limit_file, 'w') as fp:
                    json.dump({"timestamp": int(time.time())}, fp, indent=4)
        with open(self.code_limit_file, 'r') as fp:
            code_limit_json = json.load(fp)
        request_count = code_limit_json.get(str(code), 0)
        limit_count = self.code_white_list.get(str(code), 0)
        return request_count >= limit_count

    def handle_error_json(self, error_json_path):
        with open(error_json_path, 'r') as fp:
            error_json = json.load(fp)

        # 如果 flag（文件已经找齐）为 True 并且还未 uploaded.
        if "uploaded" not in error_json and "skipped" not in error_json:
            limit = self._check_code_limit(error_json.get("code", ""))
            if limit:
                print("==> Reached code limit, skip handle err file: {path}".format(path=error_json_path))
                # 把跳过标记写回到json
                error_json['skipped'] = True
                with open(error_json_path, 'w') as fp:
                    json.dump(error_json, fp, indent=4)
                return

            self._handle(error_json_path)

            # 把上传状态写回json
            error_json['uploaded'] = True
            with open(error_json_path, 'w') as fp:
                json.dump(error_json, fp, indent=4)
            print ("==> Handle err file done: {path}".format(path=error_json_path))
        else:
            print ("==> Skip handle err file: {path}".format(path=error_json_path))

    def run(self):
        print("==> Search for new error json")
        for error_json_path in self._find_error_json():
            # noinspection PyBroadException
            try:
                self.handle_error_json(error_json_path)
            except Exception as _:
                # 打印错误，但保证循环不被打断
                traceback.print_exc()
