import time
import datetime
import os
import psutil
from apscheduler.schedulers.background import BackgroundScheduler
from MonitorCore import MonitorCore
from MonitorReminder import MonitorReminder
from MonitorConfig import *
import logging
from logging.handlers import TimedRotatingFileHandler

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
handler = TimedRotatingFileHandler('./Monitor-out.log', when = 'd', interval = 1, backupCount=10)
handler.setFormatter(logging.Formatter('[%(asctime)s] %(filename)s [%(levelname)s] :%(message)s'))
logger.addHandler(handler)

logger = logging.getLogger("error")
logger.setLevel(logging.DEBUG)
handler = TimedRotatingFileHandler('./Monitor-error.log', when = 'd', interval = 1, backupCount=10)
handler.setFormatter(logging.Formatter('[%(asctime)s] %(filename)s [%(levelname)s] :%(message)s'))
logger.addHandler(handler)

logger = logging.getLogger()


class MonitorWorker:
    def __init__(self, reminder, core, cfg_dict):
        # 初始化调度库
        self.sched = BackgroundScheduler()
        # 记录配置字段
        self.worker_config = cfg_dict
        # 赋值reminder
        self.reminder = reminder
        # 赋值core
        self.core = core

    def log_monitor_in(self, cfg_list):
        key_words, file_name = cfg_list[2].split("|"), cfg_list[1]
        mark = False
        with open (file_name, "r") as f:
            for line in f.readlines():
                mark = [key_word in line for key_word in key_words].count(True) == len(key_words)

                if mark: 
                    break

        template = DEFAULT_REMINDER_TEMPLATE.format(cfg_list[-1])
        self.__result_handle(cfg_list[-1], mark, template)

    def process_monitor_exist(self, cfg_list):
        process_name = cfg_list[1].strip()
        mark = False
        for pid in psutil.pids():
            if process_name in psutil.Process(pid).name():
                mark = True
                break

        template = DEFAULT_REMINDER_TEMPLATE.format(cfg_list[-1])
        self.__result_handle(cfg_list[-1], mark, template)

    def running_monitor_range(self, cfg_list):
        item_name = cfg_list[1]
        up_threshold = float(cfg_list[2])
        down_threshold = float(cfg_list[3])
        mark = False

        for item in self.core.get_sys_status():
            if item[0] == item_name and (float(item[1]) >= up_threshold or float(item[1]) < down_threshold):
                mark = True
                break

        template = DEFAULT_REMINDER_TEMPLATE.format(cfg_list[-1])
        self.__result_handle(cfg_list[-1], mark, template)
             
    def create_sched(self, func, cfg_str, job_num):
        cfg_list = [x.strip() for x in cfg_str.split(",")]
        cfg_list.append(str(job_num))
        cron_setting = [x.strip() for x in cfg_list[0].split(" ") if x != ""]
        
        self.sched.add_job(func, 'cron', minute=cron_setting[0], 
                                    hour=cron_setting[1], 
                                    day=cron_setting[2], 
                                    month=cron_setting[3], 
                                    day_of_week=cron_setting[4], 
                                    args=[cfg_list], id=str(job_num))

    def start(self):
        self.sched.start()

    def __pause_job(self, sched_id):
        self.sched.pause_job(sched_id)

    def __resume_job(self, sched_id):
        self.sched.resume_job(sched_id)

    def __result_handle(self, line, mark, template=DEFAULT_REMINDER_TEMPLATE):
        if mark:
            # 进行消息通知
            self.reminder.send_message(template)
            # 暂停当前任务
            self.__pause_job(line)
            # 进入冷静期
            time.sleep(DEFAULT_CONGEALER if self.worker_config.get("CONGEALER", "") == "" else self.worker_config.get["CONGEALER"])
            # 恢复任务
            self.__resume_job(line)


class MonitorManager:
    def __init__(self, reminder=MonitorReminder, worker=MonitorWorker, config_dict=dict()):
        logger.info("[ Manager INIT PROCESS ] Monitor Online...")
        # 读取配置
        self.config_dict = DEFAULT_MONITOR_CONFIG_DICT
        self.config_dict.update(config_dict)
        self.monitor_dict = {x.get("KEY", ""): list() for x in self.config_dict.values()}

        logger.info("[ Manager INIT PROCESS ] Complete Config Init Success ...")
        # 初始化Core
        self.core = MonitorCore()
        logger.info("[ Manager INIT PROCESS ] Complete Core Init Success ...")
        # 初始化Reminder
        self.reminder = MonitorReminder()
        logger.info("[ Manager INIT PROCESS ] Complete Reminder Init Success ...")
        # 初始化Worker
        self.worker = MonitorWorker(self.reminder, self.core, self.config_dict)
        logger.info("[ Manager INIT PROCESS ] Complete Worker Init Success ...")
        # 开始监控
        self.__write_pid()
        self.begin_monitor()
        
    def begin_monitor(self):
        current_monitor_key = ""
        current_moniroe_func = ""

        # 查看当前配置文件是否存在
        if not os.path.exists("monitor.cfg"): 
            logger.warn("[ Manager INIT PROCESS ] We Can Not Find The Config File, So Good Bye...")
            exit(0)

        with open("monitor.cfg", "r") as f:
            for line_num, line in enumerate(f.readlines(), 1):
                line = line.strip()
                if self.__is_empty_or_comment(line):
                    continue

                if self.__is_label(line):
                    current_monitor_key = self.config_dict.get(line, {}).get("KEY", "")
                    current_moniroe_func = self.config_dict.get(line, {}).get("FUNCTION", "")
                    
                    if current_monitor_key == "" or current_moniroe_func == "": 
                        logger.warn("[ Manager INIT PROCESS ] {} Is Not In Config Dict, Will Pass...".format(line))
                    
                    continue
                
                if current_monitor_key == "": 
                    continue
                else:
                    # 符合条件的监控行，将会被创建定时任务
                    self.monitor_dict[current_monitor_key].append(line)
                    self.worker.create_sched(self.worker.__getattribute__(current_moniroe_func), line, line_num)

        logger.info("[ INIT PROCESS ] Complete Manager Init Success, The Current Jobs Is {}".format(sum([len(x) for x in self.monitor_dict.values()])))
        self.worker.start()  

    def __is_label(self, line):
        return True if line[0] == "[" and line[-1] == "]" else False

    def __is_empty_or_comment(self, line):
        return True if line == "" or line[0] == "#" else False

    def __write_pid(self):
        with open("./manager.pid", "a+") as f:
            f.write(" ")
            f.write(str(os.getpid()))


# a = MonitorManager(config_dict = monitor_config_dict)

# while True:
#     time.sleep(5)
