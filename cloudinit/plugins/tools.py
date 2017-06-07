import sys
import subprocess

import shlex
from collections import namedtuple

# python 3.5 version
# def run(cmd, stdin=None, fail=False, suppress_output=False):
    ## res = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True) # , encoding='utf-8'
    # if isinstance(stdin, str):
    #     stdin = stdin.encode()
    # res = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, input=stdin)
    # if res.stdout and not suppress_output:
    ##     print(res.stdout)
    #     print(res.stdout.decode('utf-8'))
    # if res.stderr:
    #     print(res.stderr.decode('utf-8'), file=sys.stderr)
    # if res.returncode and fail:
    #     sys.exit(1)
    # return res


def run(cmd, stdin=None, fail=False, suppress_output=False):
    if isinstance(stdin, str):
        stdin = stdin.encode()
    cmd = shlex.split(cmd)
    popen = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = popen.communicate(input=stdin)

    if stdout and not suppress_output:
        # print(res.stdout)
        print(stdout.decode('utf-8'))
    if stderr:
        print(stderr.decode('utf-8'), file=sys.stderr)
    if popen.returncode and fail:
        sys.exit(1)
    CompletedProcess = namedtuple('CompletedProcess', 'stdout stderr returncode')
    return CompletedProcess(stdout, stderr, popen.returncode)