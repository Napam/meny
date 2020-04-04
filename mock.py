'''
Mock file
'''
from consoleclass import CLI
from consolecommon import list_local_cases

def test():
    '''
    Test case
    '''
    print('Test')

if __name__ == '__main__':
    print(test.__module__)
    CLI(list_local_cases(locals())).run()
    # import inspect
    # print(locals())
    # print(__name__)




