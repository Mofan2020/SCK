"""
The SCK Project
v2.0 Windows(x64)
By skyc8266
File: main.py (Consolidated Version)
"""

import os
import sys
import json
import platform
import itertools
import ast
import subprocess
import time
from datetime import datetime
from colorama import init, Fore, Back, Style

# Initialize colorama
init()

# Path
projectRoot = os.path.abspath(".")  # Its value is like "/Users/user/Documents/sck"
# Path-End

# Config
cfg_decode = {"err": "No data in cfg_decode"}  # Config file data
safetyRules = ["App", "Ctrl"]
# Config-End

# ==================== LOG MODULE ====================
def log_style_reset():
    print(Style.RESET_ALL, end="", sep="")

def log_info(text, model):
    print(Style.RESET_ALL + "[INFO] ", datetime.now(), " [", model, "] ", text, sep="", end="\n")
    log_style_reset()

def log_err(text, model, err_id="1"):
    print(Fore.RED + "[ERROR] ", datetime.now(), " [", model, "] ", "[ERROR CODE: ", err_id, "] ", text, sep="", end="\n")
    log_style_reset()

# ==================== TOOLS MODULE ====================
def tools_loading(text="Loading", duration=5):
    spinner = itertools.cycle(['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'])
    end_time = time.time() + duration
    while time.time() < end_time:
        sys.stdout.write(f'\r{text} {next(spinner)}')
        sys.stdout.flush()
        time.sleep(0.1)
    sys.stdout.write('\r' + ' ' * (len(text) + 2) + '\r')  # 清除行

# ==================== CMD MODULE ====================
def find_seewo_processes():
    """查找希沃课堂进程"""
    processes = []
    try:
        # 使用pslist获取进程列表
        result = subprocess.run([projectRoot + "/app/PsExec/Pslist.exe", "-e"],
                                capture_output=True, text=True, check=True)
        lines = result.stdout.split('\n')
        for line in lines:
            # 查找包含"seewo"或"classroom"的进程
            if 'seewo' in line.lower() or 'classroom' in line.lower():
                parts = line.split()
                if len(parts) >= 2:
                    try:
                        pid = int(parts[1])  # PID通常在第二列
                        processes.append(pid)
                    except ValueError:
                        continue
    except (subprocess.CalledProcessError, FileNotFoundError, IndexError, ValueError) as e:
        log_err(f"Failed to find seewo processes: {e}", "app/cmd find_seewo_processes", "SCK_PSLIST_FAILED")
    return processes

def inject_dll(pid, dll_name):
    """注入DLL到指定进程"""
    dll_path = projectRoot + f"/ctrl/DllInjector/{dll_name}"
    try:
        subprocess.run([projectRoot + "/app/PsExec/PsExec64.exe", "-s",
                        projectRoot + "/ctrl/DllInjector/Injector.exe",
                        dll_path, str(pid)], check=True, capture_output=True)
        log_info(f"Successfully injected {dll_name} to PID {pid}", "app/cmd inject_dll")
    except subprocess.CalledProcessError as e:
        log_err(f"DLL injection failed for PID {pid}: {e}", "app/cmd inject_dll", "SCK_INJECTION_FAILED")

def send_signal(pid, signal_name):
    """发送信号到指定进程"""
    try:
        subprocess.run([projectRoot + "/app/PsExec/PsExec64.exe", "-s",
                        projectRoot + "/ctrl/DllInjector/Sig.exe",
                        signal_name, str(pid)], check=True, capture_output=True)
        log_info(f"Successfully sent signal {signal_name} to PID {pid}", "app/cmd send_signal")
    except subprocess.CalledProcessError as e:
        log_err(f"Signal send failed for PID {pid}: {e}", "app/cmd send_signal", "SCK_SIGNAL_FAILED")

def start_jiyu_trainer():
    """启动极域_trainer"""
    try:
        subprocess.run([projectRoot + "/app/PsExec/PsExec64.exe", "-s",
                        projectRoot + "/ctrl/JT/JiYuTrainer.exe"], check=True, capture_output=True)
        log_info("Successfully started JiYuTrainer", "app/cmd start_jiyu_trainer")
    except subprocess.CalledProcessError as e:
        log_err(f"JiYuTrainer start failed: {e}", "app/cmd start_jiyu_trainer", "SCK_JIYU_START_FAILED")

class App:
    @staticmethod
    def Help(topic="All"):
        if topic == "All":
            # 从config.json读取所有帮助信息
            if "Help" in cfg_decode:
                print("Available SCK Commands:")
                for command, description in cfg_decode["Help"].items():
                    print(f"\n* {command}")
                    # 格式化显示帮助信息，将换行符转换为适当的格式
                    lines = description.split('\n')
                    for line in lines:
                        if line.strip():
                            print(f"  {line}")
            else:
                print("Available SCK Commands:")
                print("* App.Help(topic) - Show this help")
                print("  - topic: Specific command or 'All'")
        else:
            if topic in cfg_decode["Help"]:
                print(f"Command: {topic}")
                description = cfg_decode["Help"][topic]
                lines = description.split('\n')
                for line in lines:
                    if line.strip():
                        print(line)

# ==================== MAIN FUNCTIONS ====================
def pre_getConfig():  # Get config from file
    global cfg_decode
    cfg = open(projectRoot + "/config/config.json", "r")  # Read config file
    cfg_decode = json.load(cfg)

def pre_printHead():  # Print app head
    print("-----The SCK Project-----")
    print("|Seewo Classroom Killer |")
    print("|By skyc8266 Ver", cfg_decode["version"], "   |")
    print("-------------------------")
    print("\n", end="")
    print("For help, please type \"App.Help()\" in the SCK Terminal")

def pre_envCheck():  # Check environment
    osType = platform.system()
    if(osType == "Windows"):
        pass
    else:
        log_err("System is not Windows", "pre_envCheck", "SYS_IS_NOT_NT")
        sys.exit(1)

    dbgStatus = sys.gettrace()
    if(dbgStatus):
        log_err("A debugger has attached to SCK", "pre_envCheck", "APP_DEBUGGER_ATTACHED")
        sys.exit(1)
    else:
        pass

def run_cmd():  # Start command mode
    while True:
        usrCmd = str(input("SCK>"))
        # Basic command handling
        if usrCmd == "App.Help()":
            App.Help()
        elif usrCmd.startswith("App.Help("):
            # Extract topic from command
            try:
                topic = usrCmd.split('(')[1].split(')')[0].strip('"\'')
                App.Help(topic)
            except:
                App.Help()
        else:
            print(f"Unknown command: {usrCmd}")
            print("For help, please type \"App.Help()\"")

if __name__ == "__main__":
    pre_envCheck()
    pre_getConfig()
    pre_printHead()
    tools_loading("Preparing", 5)
    run_cmd()