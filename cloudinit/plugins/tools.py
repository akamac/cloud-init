import sys
import subprocess


def run(cmd, stdin=None, fail=False, suppress_output=False):
    # res = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True) # , encoding='utf-8'
    if isinstance(stdin, str):
        stdin = stdin.encode()
    res = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, input=stdin)
    if res.stdout and not suppress_output:
        # print(res.stdout)
        print(res.stdout.decode('utf-8'))
    if res.stderr:
        print(res.stderr.decode('utf-8'), file=sys.stderr)
    if res.returncode and fail:
        sys.exit(1)
    return res
