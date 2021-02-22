import sys
sys.path.append("../")

import datetime
from config.MonitorConfig import *

class MonitorItem:
    def __init__(self, monitor_key, monitor_func, cfg_str, job_num):
        # 监控函数
        self.func = monitor_func
        # 配置字符串
        self.cfg_str = cfg_str
        # 配置列表
        self.cfg_list = [x.strip() for x in cfg_str.split(",")]
        # 配置时间周期
        self.cron = [x.strip() for x in self.cfg_list[0].split(" ") if x != ""]
        # 任务编号
        self.job_num = str(job_num)
        # 上次检查结果
        self.cur_monitor_result = False
        self.pred_monitor_result = False
        # 上次检查时间
        self.pred_monitor_datetime = ""
        # 当前所处状态
        self.status = ItemStatus.PENDING
        # 当前所属的Key
        self.monitor_key = monitor_key


    def set_result(self, result: bool):
        if result: self.pred_monitor_datetime = datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')
        
        self.cur_monitor_result = result
        self.pred_monitor_result = result

    def is_monitor_aim(self):
        return self.cur_monitor_result

    def reset_result(self):
        self.cur_monitor_result = False

    def set_status(self, status: ItemStatus):
        self.status = status

    def description(self):
        return "{}|Line [{}] Job|{}|{}|{}|{}\n".format(self.monitor_key, self.job_num, self.cfg_list[0], self.status,
                        "Aimed" if self.pred_monitor_result else "Not Aimed", self.pred_monitor_datetime)


