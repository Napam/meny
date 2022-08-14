import platform

def print_os():
    operating_system = platform.system()
    print(f"Your operating system is {operating_system}")
    return operating_system
