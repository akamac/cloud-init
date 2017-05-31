# cloud_config = {}
from tools import run

import os
import glob


if cloud_config.get('Cleanup'):
    print('Cleaning up bash history and temp files')
    os.remove('/root/.bash_history')
    map(os.remove, glob.glob('/root/.ssh/*'))
    map(os.remove, glob.glob('/tmp/*'))
    map(os.remove, glob.glob('/vat/tmp/*'))