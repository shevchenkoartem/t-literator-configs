from operator import itemgetter
from os import walk
import os
import random
import re
import sys
import json

def parse_json(json_str):
    find_comments = re.compile(
        r'\/\*[\s\S]*?\*\/|([^\\:]|^)\/\/.*$', re.MULTILINE)
    find_wrong_spaces = re.compile(r'[\u202F\u00A0]')

    # Replacing comments and non-breaking spaces:
    valid_json_str = re.sub(find_comments, r'\1', json_str)
    valid_json_str = re.sub(find_wrong_spaces, ' ', valid_json_str)

    json_obj = json.loads(valid_json_str)
    return json_obj


def get_file_fullnames(root_path, filetype):
    res = []
    for level in os.walk(root_path):
        (level_root, _, files) = level
        if 'ignore' in level_root:
            continue
        for f in files:
            if f.lower().endswith(filetype.lower()):
                res.append(os.path.join(level_root, f))
    return res


def get_config_jsons(conf_file_fullnames):
    res = []
    for conf_fullname in conf_file_fullnames:
        json_str = open(conf_fullname, "r", 1).read()
        print(f'\tMinifying {conf_fullname}...')
        json_obj = parse_json(json_str)

        sort_by_me = str(json_obj['year']) if json_obj['year'] is not None else ''
        sort_by_me += json_obj['name'] if json_obj['name'] is not None else ''
        sort_by_me += json_obj['code'] if json_obj['code'] is not None else ''
        json_obj['sortByMe'] = sort_by_me

        is_minor = 'minor' in conf_fullname
        is_unconventional = 'unconventional' in conf_fullname
        is_fun = 'fun' in conf_fullname
        json_obj['isEssential'] = not (is_minor or is_unconventional or is_fun)
        json_obj['isNotEssential_Unconventional'] = is_unconventional
        json_obj['isNotEssential_Fun'] = is_fun
        json_obj['isNotEssential_Minor'] = is_minor
        res.append(json_obj)
        
    res = sorted(res, key=itemgetter('sortByMe'))
    return res


print(f'join-configs-into-single-file.py script execution:')

# Path to 'configs' folder can be passed in the first script argument
configs_path = './'
if len(sys.argv) > 1 and len(sys.argv[1]) > 0:
    configs_path = sys.argv[1]

print(f'\tThe root [configs] folder is "{os.path.abspath(configs_path)}"')

config_src_path = os.path.join(configs_path, 'src')
config_deploy_path = os.path.join(configs_path, 'deploy', 'result')

# Get all file names in 'src' folder and its subfolders
print(f'\tGetting files in "{config_src_path}" and its subfolders...')
conf_file_fullnames = get_file_fullnames(config_src_path, 'config')

config_jsons = get_config_jsons(conf_file_fullnames)

json_minified_configs = []
for conf_json in config_jsons:
    json_minified_str = json.dumps(
        conf_json, separators=(',', ":"), ensure_ascii=False)
    code = conf_json['code'] if 'code' in conf_json else 'config' + \
        str(random.randint(1000, 9999))
    json_minified_configs.append(f'"{code}": {json_minified_str}')

res_filename = 't-literator-configs.json'
res_prev_filename = 't-literator-configs.back'
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
