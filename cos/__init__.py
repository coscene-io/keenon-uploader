# -*- coding:utf-8 -*-
import argparse
import sys

from cos.api import ApiClient
from cos.config import ConfigManager
from cos.exception import CosException
from cos.kn import KNMod
from cos.tools import Unbuffered

sys.stdout = Unbuffered(sys.stdout)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--server-url', type=str)
    parser.add_argument('-p', '--project-slug', type=str)
    parser.add_argument('-t', '--title', type=str, default="Test Record")
    parser.add_argument('-d', '--description', type=str)
    parser.add_argument('--base-dir', type=str, default="")
    parser.add_argument('--api-key', type=str)
    parser.add_argument('-c', '--config', type=str, default=None)
    parser.add_argument('files', nargs='*', help='files or directory')
    parser.add_argument('--daemon', action="store_true")
    args = parser.parse_args()

    # 和配置合并
    cm = ConfigManager(config_file=args.config)
    args.server_url = args.server_url or cm.get("server_url")
    args.api_key = args.api_key or cm.get("api_key")
    args.project_slug = args.project_slug or cm.get("project_slug")
    args.base_dir = args.base_dir if args.base_dir else cm.get("base_dir") if cm.get("base_dir") else "."
    cm.set('base_dir', args.base_dir)

    if not args.server_url or not args.api_key or not args.project_slug:
        raise CosException("server_url, api_key or project_slugs must not be empty!")

    # 0. 初始化您的 API key, Warehouse ID 和 Project ID
    api_client = ApiClient(args.server_url, args.api_key, args.project_slug)

    if args.daemon:
        # do something in daemon.py
        print("Start KN daemon...")
        api_client.daemon(KNMod, cm)
    else:
        record = api_client.create_or_get_record(args.title, args.files)
        api_client.upload_files(args.files, record)


if __name__ == "__main__":
    main()
