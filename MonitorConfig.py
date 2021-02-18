# Format Micro Defined
FORMAT_LINE = "-"

# Panel Position Defined
MAIN_MENU = "main_menu"
SHOW_DISPOSABLE = "show_disposable"
SHOW_REALTIME = "show_realtime"

# Micro Variable
DEFAULT_CONGEALER = 30 * 60
DEFAULT_REMINDER_TEMPLATE = "【{}号监控任务】已命中"
DEFAULT_MONITOR_CONFIG_DICT = {
    # 当前监控项在配置文件中的label
    # Label : { 
    #     "KEY": 当前监控项在Panel中的名称
    #     "FUNCTION": 当前监控项使用的监控函数
    #     "CONGEALER": 当前监控项的提醒冷却间隔
    # }

    "[ LOG MONITOR IN ]": {
        "KEY": "log monitor", 
        "FUNCTION": "log_monitor_in", 
        "CONGEALER": ""
    },

    "[ PROCESS MONITOR EXIST ]": {
        "KEY": "process monitor", 
        "FUNCTION": "process_monitor_exist", 
        "CONGEALER": ""
    },

    "[ RUNNING MONITOR RANGE ]": {
        "KEY": "running monitor",
        "FUNCTION": "running_monitor_range", 
        "CONGEALER": ""
    }

}







