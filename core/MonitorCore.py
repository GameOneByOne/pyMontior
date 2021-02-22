import sys
sys.path.append("../")

import platform 
import psutil
import time
import os
from .MonitorData import *
from config.MonitorConfig import *

LOCALS = locals()

class MonitorCore:
    def __init__(self):
        self.performance_list = [LOCALS[x]() for x in LOCALS.keys() if isinstance(LOCALS[x], type) and issubclass(LOCALS[x], MonitorData)]
        self.status_list = list()

    def get_sys_status(self):
        self.status_list = list()
        for pf in self.performance_list:
            self.status_list.extend(pf.ret_status())
            self.status_list.extend([FORMAT_LINE])
        return self.status_list
