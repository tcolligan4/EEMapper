# ===============================================================================
# Copyright 2018 dgketchum
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ===============================================================================
import csv
import os
from subprocess import Popen, PIPE, check_call

home = os.path.expanduser('~')
EXEC = os.path.join(home, 'miniconda2', 'envs', 'ee', 'bin', 'earthengine')


def delete_assets(ee_asset_path):
    reader = None
    for year in range(2008, 2014):
        _dir = os.path.join(ee_asset_path, str(year))
        reader = list_assets(_dir)

    for r in reader:
        command = 'rm'
        cmd = ['{}'.format(EXEC), '{}'.format(command), '{}'.format(r['name'])]
        check_call(cmd)


def list_assets(location):
    command = 'ls'
    cmd = ['{}'.format(EXEC), '{}'.format(command), '{}'.format(location)]
    asset_list = Popen(cmd, stdout=PIPE)
    stdout, stderr = asset_list.communicate()
    reader = csv.DictReader(stdout.decode('ascii').splitlines(),
                            delimiter=' ', skipinitialspace=True,
                            fieldnames=['name'])
    assets = [x['name'] for x in reader]
    return assets


if __name__ == '__main__':
    loc = os.path.join('users', 'dgketchum', 'classy')
    _list = list_assets(loc)
    years = ['1986', '1996', '2006', '2016']
    dct = {'1986': [], '1996': [], '2006': [], '2016': []}
    for l in _list:
        e = l[-4:]
        dct[e].append(l)
    for key, val in dct.items():
        print(val)
# ========================= EOF ====================================================================
