import argparse
import os
import os.path as p
import re

from cos.api import ApiClient

API_BASE = 'https://openapi.staging.coscene.cn'
API_KEY = 'YmI1Y---------------------------------------------------------------------------------=='
PROJECT = 'default/123e'

WANTED_FILE_SUFFIXES = [
    '.bag',
    '.bag.active'
]

RECORD_TITLE_REGEX = re.compile(r'(\b202\d(-\d\d){5}.*)\.bag')

client = ApiClient(API_BASE, API_KEY, PROJECT)

def process_file(dirname, basename, record_prefix):
    mat = RECORD_TITLE_REGEX.search(basename)
    if not mat:
        print('Skipping file {} because it does not match expected pattern'.format(basename))
        return

    record_title = '{}-{}'.format(record_prefix, mat.group(1))

    upload_list = [p.join(dirname, basename)]
    rec = client.create_or_get_record(record_title, upload_list)
    client.upload_files(upload_list, rec)


def upload_batch(directory, config_file, tag, start, limit):
    prefixes = {}
    with open(config_file) as f:
        for line in f:
            if not line.strip():
                continue
            s = line.strip().split('----')
            prefixes[s[0]] = s[1]

    groups = { name: prefixes[name] for name in os.listdir(directory) if p.isdir(p.join(directory, name)) }
    files_to_upload = []
    for name, prefix in groups.items():
        for dir_path, _, filenames in os.walk(p.join(directory, name)):
            for f in filenames:
                if not any(f.endswith(s) for s in WANTED_FILE_SUFFIXES):
                    continue

                files_to_upload.append((dir_path, f, prefix))

    files_with_index = list(enumerate(sorted(files_to_upload)))
    to_process = files_with_index[start:]
    if limit > 0:
        to_process = to_process[:limit]

    for index, (path, name, prefix) in to_process:
        print('Starting to process file: ' + str(index))
        process_file(path, name, prefix)
        print('Finished processing file: ' + str(index))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--tag', type=str)
    parser.add_argument('--directory', type=str, required=True)
    parser.add_argument('--config', type=str, required=True)
    parser.add_argument('--start', type=int, default=0)
    parser.add_argument('--limit', type=int, default=-1)
    args = parser.parse_args()

    upload_batch(args.directory, args.config, args.tag, args.start, args.limit)

