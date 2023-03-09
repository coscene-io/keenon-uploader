import argparse
import json
import os
import random
import time
from contextlib import closing
from datetime import datetime

import rosbag

ERROR_CODES = [{'code': 1234}, {'code': 1111}]


def generate_bag(input_bag_file, output_bag_file):
    with closing(rosbag.Bag(input_bag_file)) as input_bag:
        topics_to_pare = set()
        _, topics = tuple(input_bag.get_type_and_topic_info())

        for topic, (msg_type, msg_count, connections, freq) in topics.items():
            if msg_type != 'tf2_msgs/TFMessage' and msg_count > 100 and freq > 5:
                topics_to_pare.add(topic)

        with closing(rosbag.Bag(output_bag_file, 'w', 'lz4')) as output_bag:
            for topic, msg, ts in input_bag:
                if topic not in topics_to_pare or random.random() > 0.1:
                    output_bag.write(topic, msg, ts)
    print("generated {output_bag_file}".format(output_bag_file=output_bag_file))


def make_new_error_data(input_bag_file, output_dir):
    code = ERROR_CODES[random.randint(0, len(ERROR_CODES))]['code']
    start_time = int(time.time())
    start_time_string = datetime.fromtimestamp(start_time).strftime("%Y-%m-%y-%H-%M-%S")
    error_dir = "{output_dir}/{code}-{datetime}".format(
        output_dir=output_dir,
        code=code,
        datetime=start_time_string
    )
    json_file = "{error_dir}.json".format(error_dir=error_dir)
    bag_file = "{error_dir}/main.bag".format(error_dir=error_dir)

    os.makedirs(error_dir)
    generate_bag(input_bag_file, bag_file)

    error_id_json = {
        "code": code,
        "log": [],
        "bag": [bag_file],
    }
    with open(json_file, 'w') as fp:
        json.dump(error_id_json, fp)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', type=str, help='the input rosbag')
    parser.add_argument('-o', '--output', type=str, help='the directory for the output bag')
    parser.add_argument('--daemon', action="store_true")
    args = parser.parse_args()

    count = -1 if args.daemon else 1
    i = 0
    while count < 0 or i < count:
        make_new_error_data(args.input, args.output)
        i += 1
        if count < 0 or i < count:
            time.sleep(60)


if __name__ == '__main__':
    main()
