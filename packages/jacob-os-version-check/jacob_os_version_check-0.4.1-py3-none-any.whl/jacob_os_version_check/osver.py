import sys
import platform

def os_check_j() -> str:
    if platform.system().lower() == "windows":
        return win_os_ver()
    elif "linux" in platform.system().lower() or "ubuntu" in platform.system().lower():
        return get_os_pretty_name()
    else:
        return "Unknown OS"

def win_os_ver():
    return f"{platform.system()} {platform.release()}  {platform.version()}"



def get_os_pretty_name():
          with open('/etc/os-release','r') as file:
                  for line in file:
                          if line.startswith('PRETTY_NAME'):
                                  return line.split("=")[1].strip().strip('"')
          return None


