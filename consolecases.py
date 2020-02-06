'''
File containing cases for console interface

Each case should be a function.
The ordering of the cases in the console interface
will be by the function names. So a() will be 
first then b() etc.

Name of cases in console interface will be first line of 
docstring

Feel free to import whatever
'''
from common import join_threads
from threading import Thread
from pandas import to_numeric 
from time import sleep
import scrapeconfig as scng
import numpy as np

def a_sample_case():
    '''
    Get a random number
    '''
    print(np.random.randint(10))
    sleep(1)

def case1():
    '''
    Update all data
    '''
    print('Omae wa shinderu')
    sleep(1)

def case2():
    '''
    Obtain Oslo Bors quotes and returns
    '''
    from get_osebx_html_files import get_htmlfile 
    print('Obtaining HTML files from Oslo Bors')
    args = (
        (scng.BORS_QUOTES_URL, scng.QUOTES_TARGET_FILE, scng.QUOTES_WAIT_TARGET_CLASS),
        (scng.BORS_RETURNS_URL, scng.RETURNS_TARGET_FILE, scng.RETURNS_WAIT_TARGET_CLASS)
    )

    threads = [Thread(target=get_htmlfile, args=a) for a in args]
    [th.start() for th in threads]
    join_threads(threads, verbose=False)
    print('Obtained HTML files')

def case3():
    '''
    Scrape Oslo bors HTML files
    '''

def case4():
    '''
    Scrape Yahoo Finance
    '''

def case5():
    '''
    Backup current data
    '''
