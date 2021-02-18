import platform
import os
import psutil


class MonitorData:
    def __init__(self):
        pass
    
    def ret_status(self):
        return [self.__getattribute__(x) for x in dir(self) if "data_monitor" in x]


class RunningData(MonitorData):
    def __init__(self):
        self.data_monitor_1 = ["CPU Use Percent", str(round(psutil.cpu_percent(), 2))]
        self.data_monitor_2 = ["MEM Use Percent", str(round(psutil.virtual_memory().percent, 2))]


class LogData(MonitorData):
    def __init__(self):
        pass
