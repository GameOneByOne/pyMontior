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
from redis.connection import ConnectionPool
from redis.client import Redis
import threading

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
handler = TimedRotatingFileHandler('./Monitor.log', when = 'd', interval = 1, backupCount=10)
handler.setFormatter(logging.Formatter('[%(asctime)s] %(filename)s [%(levelname)s] :%(message)s'))
logger.addHandler(handler)


class MonitorWorker:
    def __init__(self, reminder, core, cfg_dict):
        # 初始化调度器
        self.sched = BackgroundScheduler()
        # 初始化配置字典
        self.worker_config = cfg_dict
        # 赋值监控提醒器
        self.reminder = reminder
        # 赋值监控核心
        self.core = core

    def log_monitor_in(self, item):
        key_words, file_name = cfg_list[2].split("|"), cfg_list[1]
        mark = False
        with open (file_name, "r") as f:
            for line in f.readlines():
                mark = [key_word in line for key_word in key_words].count(True) == len(key_words)

                if mark: 
                    break

        template = DEFAULT_REMINDER_TEMPLATE.format(cfg_list[-1])
        self.__result_handle(cfg_list[-1], mark, template)

    def process_monitor_exist(self, item):
        process_name = cfg_list[1].strip()
        mark = False
        for pid in psutil.pids():
            if process_name in psutil.Process(pid).name():
                mark = True
                break

        template = DEFAULT_REMINDER_TEMPLATE.format(cfg_list[-1])
        self.__result_handle(cfg_list[-1], mark, template)

    def running_monitor_range(self, item):
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
             
    def create_sched(self, item):      
        self.sched.add_job(self.__getattribute__(item.func),
                        'cron', minute=item.cron[0], hour=item.cron[1], 
                        day=item.cron[2], month=item.cron[3], day_of_week=item.cron[4], 
                        args=[item], id=str(item.job_num))

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


class MonitorItem:
    def __init__(self, monitor_func, cfg_str, job_num):
        # 监控函数
        self.func = monitor_func
        # 配置字符串
        self.cfg_str = cfg_str
        # 配置列表
        self.cfg_list = [x.strip() for x in cfg_str.split(",")]
        # 配置时间周期
        self.cron = [x.strip() for x in cfg_list[0].split(" ") if x != ""]
        # 任务编号
        self.job_num = str(job_num)
        # 上次检查结果
        self.pred_monitor_result = ""
        # 上次检查时间
        self.pred_monitor_datetime = ""


class MonitorManager:
    def __init__(self, reminder=MonitorReminder, worker=MonitorWorker, config_dict=dict()):
        logger.info("[ Manager INIT PROCESS ] Monitor Initialing ...")
        # 全局的监控项目管理变量
        self.monitor_list = list()
        # 读取配置
        self.config_dict = DEFAULT_MONITOR_CONFIG_DICT
        self.config_dict.update(config_dict)
        self.monitor_dict = {x.get("KEY", ""): list() for x in self.config_dict.values()}
        logger.info("[ Manager INIT PROCESS ] Config Init Success ...")

        # 初始化Core
        self.core = MonitorCore()
        logger.info("[ Manager INIT PROCESS ] Core Init Success ...")

        # 初始化Reminder
        self.reminder = MonitorReminder()
        logger.info("[ Manager INIT PROCESS ] Reminder Init Success ...")

        # 初始化Worker
        self.worker = MonitorWorker(self.reminder, self.core, self.config_dict)
        logger.info("[ Manager INIT PROCESS ] Worker Init Success ...")

        self.__write_pid()
        order_soldier = threading.Thread(target=self.__check_order)
        order_soldier.start()

    def begin_monitor(self):
        current_monitor_key, current_moniroe_func = "", ""
        # 查看当前配置文件是否存在
        if not os.path.exists("monitor.cfg"): 
            logger.warn("[ Manager INIT PROCESS ] We Can Not Find The Config File, So Good Bye...")
            exit(0)

        with open("monitor.cfg", "r") as f:
            for line_num, line in enumerate(f.readlines(), 1):
                line = line.strip()
                # 如果当前行是空行或者注释的话
                if self.__is_empty_or_comment(line): continue

                # 如果当前行是个标签的话
                if self.__is_label(line):
                    current_monitor_key = self.config_dict.get(line, {}).get("KEY", "")
                    current_moniroe_func = self.config_dict.get(line, {}).get("FUNCTION", "")
                    
                    if current_monitor_key == "" or current_moniroe_func == "": 
                        logger.warn("[ Manager INIT PROCESS ] {} Is Not In Config Dict Or Config Isn't Complete, Will Pass...".format(line))
                        current_monitor_key, current_moniroe_func = "", ""
                    
                    continue
                
                # 如果当前变量key是空的话
                if self.__is_empty_key(current_monitor_key): continue

                # 符合条件的行，将会被创建监控对象，并开启周期任务
                item = MonitorItem(current_moniroe_func, line, line_num)
                self.monitor_dict[current_monitor_key].append(item)
                self.worker.create_sched(item)

        logger.info("[ INIT PROCESS ] Complete Manager Init Success, The Current Jobs Is {}".format(sum([len(x) for x in self.monitor_dict.values()])))
        self.worker.start()  

    def stop_monitor(self):
        pass

    def __is_label(self, line):
        return True if line[0] == "[" and line[-1] == "]" else False

    def __is_empty_or_comment(self, line):
        return True if line == "" or line[0] == "#" else False

    def __is_empty_key(self, key):
        return True if key == "" else False

    def __write_pid(self):
        with open("./manager.pid", "w") as f:
            f.write(" ")
            f.write(str(os.getpid()))

    def __check_order(self):
        while True:
            time.sleep(1)
            if ".order_accept.tmp" in os.listdir():
                with open(".order_accept.tmp", "r") as f:
                    # 读取命令后开始分析命令
                    response = self.__parse_order(f.read())

                with open(".order_response.tmp", "w") as f:
                    # 将结果写到制定文件夹
                    f.write(response)

    def __parse_order(self, order):
        if order == "Show Monitor Schedule": return self.__show_monitor_schedule() 
        elif order == "": pass 
        elif order == "": pass
        else : return "Order Parse Error, Please Ensure Your Order Correctly"

    def __show_monitor_schedule(self):
        

            

            