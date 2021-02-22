import sys
sys.path.append("../")

import psutil
import os
import time
from config.MonitorConfig import *


class MonitorPanel:
    def __init__(self):
        self.print_queue = list()
        self.panel_Position = MAIN_MENU

        if not self.__manager_is_alive():
            print("Your Monitor Manager Is Not Running, Please Run It Firstly")
            exit(0)

    def show_realtime_status(self):
        self.panel_Position = SHOW_REALTIME

    def show_disposable_status(self):
        self.panel_Position = SHOW_DISPOSABLE
        self.print_queue.extend([
            ["Disposable Performance Show"],
            [FORMAT_LINE],
        ])

        self.print_queue.extend(self.pf_core.get_sys_status())
        self.__print_format()

    def show_monitor_item(self):
        self.panel_Position = SEND_ORDER
        responses = self.__send_order("Show Monitor Schedule")

        self.print_queue = [FORMAT_LINE]
        self.print_queue.extend([x.replace("\n", "").split("|") for x in responses])
        self.print_queue.extend([FORMAT_LINE])
        # print(self.print_queue)
        self.__print_format()

    def show_menu(self):
        self.panel_Position = MAIN_MENU
        self.print_queue.extend([
            ["MonitorPanel 0.1"],
            [FORMAT_LINE],
            ["1. Show RealTime Status"],
            ["2. Show Disposable Status"],
            ["3. Show Monitor Status"],
            [FORMAT_LINE]
        ])

        self.__print_format()

    def __send_order(self, order):
        with open(".order_to_monitor.tmp", "w") as f:
            # 读取命令后开始分析命令
            f.write(order)

        while True:
            time.sleep(0.2)
            if ".response_to_panel.tmp" in os.listdir():
                with open(".response_to_panel.tmp", "r") as f:
                    # 将结果写到制定文件夹
                    responses = f.readlines()

                os.remove(".response_to_panel.tmp")
                break

        return responses
        
    def __manager_is_alive(self):
        manger_pid = int(self.__find_manage_pid().strip())
        if manger_pid in psutil.pids():
            return psutil.Process(manger_pid).is_running() if manger_pid != "" else False
        return False
            
    def __print_format(self):
        max_line_len = max([len(x) for x in self.print_queue])
        max_phrase_len = [max([len(x[i])+3 for x in self.print_queue if i < len(x)]) for i in range(max_line_len)]

        for line in self.print_queue:
            for index in range(len(line)):
                if line[index] == FORMAT_LINE: print("-"*sum(max_phrase_len), end="")
                else: print("{str:<{len}}".format(str=line[index], len=max_phrase_len[index]), end="")
            print("")

        self.print_queue.clear()

    def __find_manage_pid(self):
        if "manager.pid" in os.listdir():
            with open("manager.pid", "r") as f: 
                return f.read()

        return ""

    def show(self):
        while True:
            if self.panel_Position == MAIN_MENU: self.show_menu()

            user_input = input("Monitor Panel command > ")
            if self.panel_Position == MAIN_MENU:
                if user_input.lower() == "q": exit(0)
                elif user_input == "2": self.show_disposable_status()
                elif user_input == "3": self.show_monitor_item()
                
            elif self.panel_Position == SHOW_DISPOSABLE: 
                if user_input.lower() == "q": self.panel_Position = MAIN_MENU
                elif user_input.lower() == "rf": self.show_disposable_status()

            elif self.panel_Position == SEND_ORDER:
                if user_input.lower() == "q": self.panel_Position = MAIN_MENU
