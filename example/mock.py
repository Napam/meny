import meny
from meny import config as cng
import json
from itertools import chain
import sys

stack = [cng._ROOT, "func1"]
casefunc = "bingbong"
value = 666
returns = {}

temp: dict
temp = returns
for key in chain(stack[1:], casefunc):
    if key not in returns:
        returns[key] = {}
    temp


wanted = {"func1": {"return": 1, "bingbong": {"return": value}}}
print(json.dumps(wanted, indent=4))

curr = {}
curr = curr["lol"] = {}
print(curr)
