'''
Run this file to run console 
'''
if __name__ == '__main__':
    import consolecases
    import consoleconfig as ccng
    from consoleobject import CLI
    import consolestrings as strings

    if ccng.DEFAULT_DECORATE:
        from consoledecorator import case_decorator
        CLI(consolecases, title=strings.LOGO_TITLE, blank_proceedure='exit', decorator=case_decorator).run()
    else:
        CLI(consolecases, title=strings.LOGO_TITLE, blank_proceedure='exit', decorator=None).run()