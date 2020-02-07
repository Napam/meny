'''
Common stuff for console stuff
'''

import os 

__CLEAR_COMMAND = 'cls' if os.name == 'nt' else 'clear'
def clear_screen():
    '''Obvious'''
    os.system(__CLEAR_COMMAND)

