from time import sleep
import consoleconfig as ccng

def case_decorator(func):
    '''Decorator to enforce commmon behavior for cases'''
    def case_wrapper(*args, **kwargs):
        '''Enter function'''
        retobj = func(*args, **kwargs)
        sleep(ccng.CASE_EXIT_WAIT_TIME) 
        return retobj

    # "Inherit" docstring (not really neccessary, but kinda nice to have)
    case_wrapper.__doc__ = func.__doc__
    return case_wrapper
