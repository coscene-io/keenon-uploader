# -*- coding:utf-8 -*-
import os
from ConfigParser import ConfigParser

try:
    # noinspection PyCompatibility
    from pathlib import Path
except ImportError:
    from pathlib2 import Path


class ConfigManager:
    # 以下目录 `~/.config/cos` 遵从 XDG Base Directory Specification
    # 参考: https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html
    _XDG_DIR = Path(os.getenv('XDG_CONFIG_HOME') or '~/.config').expanduser() / 'cos'
    DEFAULT_CONFIG_PATHS = [
        Path.cwd() / 'config.ini',          # ./config.ini
        Path('~/.cos.ini').expanduser(),    # ~/.cos.ini
        _XDG_DIR / 'config.ini',            # ~/.config/cos/config.ini
        Path('/etc/cos') / 'config.ini'     # /etc/cos/config.ini
    ]

    def __init__(self, config_file, profile='default'):
        self.config_file = self._find_conf_path(config_file)
        self.profile = profile
        self.parser = ConfigParser()
        self.load()

    def get(self, key):
        return self.parser.has_option(self.profile, key) and self.parser.get(self.profile, key) or None

    def set(self, key, value):
        if not self.parser.has_section(self.profile):
            self.parser.add_section(self.profile)
        self.parser.set(self.profile, key, value)

    def load(self):
        self.parser.read(str(self.config_file))

    def save(self):
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        with self.config_file.open() as f:
            self.parser.write(f)

    def _find_conf_path(self, conf_path=None):
        if conf_path and Path(conf_path).expanduser().exists():
            return conf_path

        print("==> No valid config file specified, try to find one")
        for default in self.DEFAULT_CONFIG_PATHS:
            print(default)
            if default.exists():
                print("==> Use config {default}".format(
                    conf_path=conf_path,
                    default=default
                ))
                return default

        # 强制使用 ./config.ini
        print("==> No config found".format(
            conf_path=conf_path
        ))
        return self.DEFAULT_CONFIG_PATHS[0]
