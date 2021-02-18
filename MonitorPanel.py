import psutil
import os

class MonitorPanel:
    def __init__(self):
        self.print_queue = list()
        self.panel_Position = MAIN_MENU

        if not self.__manager_is_alive():
            print("Your Monitor Manager Is Not Running, Please Run It Firstly")

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
        pass

    def show_menu(self):
        self.panel_Position = MAIN_MENU
        self.print_queue.extend([
            ["MonitorPanel 0.1"],
            [FORMAT_LINE],
            ["1. Show RealTime Status"],
            ["2. Show Disposable Status"],
            [FORMAT_LINE]
        ])

        self.__print_format()

    def __manager_is_alive(self):
        manger_pid = self.__find_manage_pid()
        return psutil.Process(manger_pid).is_running() if manger_pid != "" else False
            
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
        with open("manager.pid", "a+") as f: 
            return f.content

        return ""


panel = MonitorPanel()

while True:
    if panel.panel_Position == MAIN_MENU: panel.show_menu()

    user_input = input("Monitor Panel command > ")
    if panel.panel_Position == MAIN_MENU:
        if user_input.lower() == "q": exit(0)
        elif user_input == "2": panel.show_disposable_status()
        
    elif panel.panel_Position == SHOW_DISPOSABLE: 
        if user_input.lower() == "q": panel.panel_Position = MAIN_MENU
        elif user_input.lower() == "rf": panel.show_disposable_status()