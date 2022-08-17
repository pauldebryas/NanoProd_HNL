import subprocess
import sys
import os
import yaml

def sh_call(cmd, shell=False, catch_stdout=False, decode=True, split=None, expected_return_codes = [ 0 ], verbose=0):
    cmd_str = []
    for s in cmd:
        if ' ' in s:
            s = f"'{s}'"
        cmd_str.append(s)
    cmd_str = ' '.join(cmd_str)
    if verbose > 0:
        print(f'>> {cmd_str}', file=sys.stderr)
    kwargs = {
        'shell': shell,
    }
    if catch_stdout:
        kwargs['stdout'] = subprocess.PIPE
    proc = subprocess.Popen(cmd, **kwargs)
    output, err = proc.communicate()
    if proc.returncode not in expected_return_codes:
        raise RuntimeError(f'Error while running "{cmd_str}". Error code: {proc.returncode}')
    if catch_stdout and decode:
        output_decoded = output.decode("utf-8")
        if split is None:
            output = output_decoded
        else:
            output = [ s for s in output_decoded.split(split) if len(s) > 0 ]
    return proc.returncode, output


input_file = sys.argv[1]
output_file = sys.argv[2]

skim_cfg_path = os.path.join(os.environ['CMSSW_BASE'], 'src', 'NanoProd', 'NanoProd', 'data', 'skim.yaml')
with open(skim_cfg_path, 'r') as f:
    skim_config = yaml.safe_load(f)

selection = skim_config['selection']
skim_tree_path = os.path.join(os.environ['CMSSW_BASE'], 'python', 'NanoProd', 'NanoProd', 'skim_tree.py')
cmd_line = ['python3', skim_tree_path, '--input', input_file, '--output', output_file, '--input-tree', 'Events',
         '--other-trees', 'LuminosityBlocks,Runs', '--include-all', '--sel', selection, '--verbose', '1']

for cond in ['exclude', 'include']:
    if cond + '_columns' in skim_config:
        columns = ','.join(skim_config[cond + '_columns'])
        cmd_line.extend([f'--{cond}-columns', columns])

sh_call(cmd_line, verbose=1)
