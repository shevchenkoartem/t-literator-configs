print(f'join-configs-into-single-file.py script execution:')

import json
import sys
import re
import random
import os
from os import walk

def get_minified_json_str(json_str):
    find_comments = re.compile(r'\/\*[\s\S]*?\*\/|([^\\:]|^)\/\/.*$', re.MULTILINE)
    find_wrong_spaces = re.compile(r'[\u202F\u00A0]')

    # Replacing comments and non-breaking spaces:
    valid_json_str = re.sub(find_comments, r'\1', json_str)
    valid_json_str = re.sub(find_wrong_spaces, ' ', valid_json_str)

    json_obj = json.loads(valid_json_str)

    code = json_obj['code'] if 'code' in json_obj else 'config' + str(random.randint(1000, 9999))
    json_minified_str = json.dumps(json_obj, separators=(',', ":"), ensure_ascii=False)

    return (code, json_minified_str)

# Path to 'configs' folder can be passed in the first script argument
configs_path = './configs/'
if len(sys.argv) > 1 and len(sys.argv[1]) > 0:
    configs_path = sys.argv[1]

print(f'\tThe [configs] folder is "{configs_path}"')

config_src_path = os.path.join(configs_path, 'src')
config_deploy_path = os.path.join(configs_path, 'deploy')

# Get all file names in 'src' folder
print(f'\tGetting files in "{config_src_path}"...')
conf_filenames = []
for (dirpath, dirnames, filenames) in walk(config_src_path):
    conf_filenames.extend(filenames)
    break

json_minified_configs = []
for conf_filename in conf_filenames:
    conf_filepath = os.path.join(config_src_path, conf_filename)
    json_str = open(conf_filepath, "r", 1).read()

    print(f'\tMinifying {conf_filename}...')
    (code, json_minified_str) = get_minified_json_str(json_str)
    json_minified_configs.append(f'"{code}": {json_minified_str}')

res_filename = 't-literator-configs.json'
res_prev_filename = 't-literator-configs.prev'
res_filepath = os.path.join(config_deploy_path, res_filename)
res_prev_filepath = os.path.join(config_deploy_path, res_prev_filename)

if os.path.exists(res_prev_filepath):
    os.remove(res_prev_filepath)

if os.path.exists(res_filepath):
    print(f'\tSaving previously done {res_filename} as {res_prev_filename}...')
    os.rename(res_filepath, res_prev_filepath)

print(f'\tCreating a new {res_filename} file...')
res_file = open(res_filepath, "a+", 1)
res_file.write('{\n')
res_file.write(',\n'.join(json_minified_configs))
res_file.write('\n}')

print(f'\t=====\n\tThe script is completed successfully!')