from core.MonitorManager import MonitorManager
import time


my_monitor = MonitorManager()
my_monitor.begin_monitor()

while True:
    time.sleep(5)