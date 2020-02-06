# PyPat-Console
Simple but sexy framework for console interface 

# Why
Sometimes you want to have a simple console interface so you can do things step by step. 
For example here is an application.

```
------------- Mulababy420 --------------
1. Update all data
2. Obtain Oslo Bors quotes and returns
3. Scrape Oslo bors HTML files
4. Scrape Yahoo Finance
5. Backup current data
6. Exit program
Enter choice: 
```
Sometimes I don't want to run everything at once. Maybe I just want to backup data instead of doing all the things. This framework will enable a very quick implementation of a console. 
Without the console I would need to find the right file to run (and maybe comment things out first as well). The console organizes everything into one place. 

# What to run
```
python .\console.py
```

# How to implement
Simply implement the cases (as functions) in consolecases.py. You can import whatever you want in there. You will need to implement docstrings to every case. The first line of of text in the docstring will be used as the description in the console interface. 

The order of the cases is alphabetically sorted by the function name. 

The rest of the code will automatically integrate the function to the console interface without you needing to worry about anything.

