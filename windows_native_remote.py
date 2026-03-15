#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Windows原生远程控制工具 - 无需对方安装任何软件
利用Windows内置功能实现远程控制
仅用于教育和授权的安全测试
"""

import subprocess
import socket
import platform
import os
import sys
import json
import threading
import time
from datetime import datetime

def check_windows_native_tools():
    """检查Windows原生工具可用性"""
    tools = {
        'WMI': 'wmic',
        'PowerShell': 'powershell',
        'net': 'net',
        'sc': 'sc',
        'tasklist': 'tasklist',
        'ipconfig': 'ipconfig',
        'systeminfo': 'systeminfo'
    }
    
    available_tools = {}
    
    for name, cmd in tools.items():
        try:
            result = subprocess.run([cmd, '/?'], capture_output=True, timeout=5)
            available_tools[name] = True
        except:
            available_tools[name] = False
    
    return available_tools

class WindowsNativeRemote:
    """Windows原生远程控制工具"""
    
    def __init__(self):
        self.available_tools = check_windows_native_tools()
        
    def execute_wmi_command(self, target_ip, username, password, wmi_query):
        """通过WMI执行远程命令"""
        try:
            # 构建WMI命令
            cmd = f'wmic /node:"{target_ip}" /user:"{username}" /password:"{password}" {wmi_query}'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
            return result
        except Exception as e:
            return subprocess.CompletedProcess(args=cmd, returncode=1, 
                                             stdout='', stderr=str(e))
    
    def execute_powershell_remote(self, target_ip, script_content):
        """通过PowerShell远程执行脚本"""
        try:
            # 创建临时脚本文件
            script_file = 'temp_script.ps1'
            with open(script_file, 'w', encoding='utf-8') as f:
                f.write(script_content)
            
            # 执行远程PowerShell
            cmd = f'powershell -ExecutionPolicy Bypass -File {script_file}'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
            
            # 清理临时文件
            if os.path.exists(script_file):
                os.remove(script_file)
                
            return result
        except Exception as e:
            return subprocess.CompletedProcess(args=cmd, returncode=1, 
                                             stdout='', stderr=str(e))
    
    def get_system_info_remote(self, target_ip, username, password):
        """获取远程系统信息"""
        # 使用WMI获取系统信息
        wmi_queries = {
            'os_info': 'os get Caption,Version,BuildNumber,OSArchitecture',
            'computer_info': 'computersystem get Name,Domain,Manufacturer,Model',
            'cpu_info': 'cpu get Name,NumberOfCores,MaxClockSpeed',
            'memory_info': 'memorychip get Capacity,Speed',
            'disk_info': 'logicaldisk get DeviceID,Size,FreeSpace',
            'network_info': 'nicconfig get IPAddress,MACAddress,DefaultIPGateway'
        }
        
        results = {}
        
        for key, query in wmi_queries.items():
            result = self.execute_wmi_command(target_ip, username, password, query)
            if result.returncode == 0:
                results[key] = result.stdout
            else:
                results[key] = f"Error: {result.stderr}"
        
        return results
    
    def execute_remote_command(self, target_ip, username, password, command):
        """执行远程命令"""
        # 使用WMI创建进程
        wmi_query = f'process call create "{command}"'
        result = self.execute_wmi_command(target_ip, username, password, wmi_query)
        return result
    
    def get_process_list_remote(self, target_ip, username, password):
        """获取远程进程列表"""
        wmi_query = 'process get Name,ProcessId,WorkingSetSize'
        result = self.execute_wmi_command(target_ip, username, password, wmi_query)
        return result
    
    def create_remote_service(self, target_ip, username, password, service_name, service_path):
        """创建远程服务"""
        try:
            # 使用sc命令创建服务
            cmd = f'sc \\{target_ip} create {service_name} binPath= "{service_path}"'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
            return result
        except Exception as e:
            return subprocess.CompletedProcess(args=cmd, returncode=1, 
                                             stdout='', stderr=str(e))
    
    def scan_network_devices(self, network_range):
        """扫描网络设备"""
        devices = []
        
        def ping_device(ip):
            try:
                result = subprocess.run(['ping', '-n', '1', '-w', '1000', ip], 
                                      capture_output=True, text=True, timeout=2)
                return result.returncode == 0
            except:
                return False
        
        # 扫描指定网段
        for i in range(1, 255):
            ip = f"{network_range}.{i}"
            if ping_device(ip):
                devices.append(ip)
        
        return devices
    
    def check_rdp_access(self, target_ip):
        """检查RDP访问权限"""
        try:
            # 检查RDP端口3389是否开放
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            result = sock.connect_ex((target_ip, 3389))
            sock.close()
            
            return result == 0
        except:
            return False
    
    def get_available_methods(self):
        """获取可用的远程控制方法"""
        methods = []
        
        if self.available_tools['WMI']:
            methods.append({
                'name': 'WMI远程管理',
                'description': '使用Windows Management Instrumentation进行远程管理',
                'requirements': '需要管理员权限和有效凭据'
            })
        
        if self.available_tools['PowerShell']:
            methods.append({
                'name': 'PowerShell远程',
                'description': '使用PowerShell远程执行命令',
                'requirements': '需要启用PowerShell远程功能'
            })
        
        methods.append({
            'name': '网络扫描',
            'description': '扫描网络中的设备',
            'requirements': '需要网络连接'
        })
        
        methods.append({
            'name': 'RDP访问检查',
            'description': '检查远程桌面服务是否可用',
            'requirements': '需要网络连接'
        })
        
        return methods

def main():
    """主函数"""
    print("=" * 60)
    print("       Windows原生远程控制工具")
    print("=" * 60)
    print("💡 特点: 无需对方安装任何软件")
    print("🎯 利用Windows内置功能实现远程控制")
    print("=" * 60)
    
    # 检查系统平台
    if platform.system() != 'Windows':
        print("❌ 此工具仅支持Windows系统")
        return
    
    # 创建远程控制实例
    remote = WindowsNativeRemote()
    
    # 显示可用工具
    print("\n🔧 检测到的Windows原生工具:")
    for tool, available in remote.available_tools.items():
        status = "✅ 可用" if available else "❌ 不可用"
        print(f"   {tool}: {status}")
    
    # 显示可用方法
    print("\n🎯 可用的远程控制方法:")
    methods = remote.get_available_methods()
    for i, method in enumerate(methods, 1):
        print(f"{i}. {method['name']}")
        print(f"   描述: {method['description']}")
        print(f"   要求: {method['requirements']}")
        print()
    
    # 演示网络扫描
    print("\n🌐 网络扫描演示:")
    local_ip = socket.gethostbyname(socket.gethostname())
    network_prefix = '.'.join(local_ip.split('.')[:3])
    
    print(f"扫描网络: {network_prefix}.1-254")
    devices = remote.scan_network_devices(network_prefix)
    
    if devices:
        print(f"发现 {len(devices)} 个在线设备:")
        for device in devices[:10]:  # 只显示前10个
            rdp_status = "(RDP可用)" if remote.check_rdp_access(device) else ""
            print(f"  • {device} {rdp_status}")
        if len(devices) > 10:
            print(f"  ... 还有 {len(devices) - 10} 个设备")
    else:
        print("未发现在线设备")
    
    print("\n" + "=" * 60)
    print("💡 使用说明:")
    print("=" * 60)
    print("1. WMI远程管理:")
    print("   命令示例: python windows_native_remote.py")
    print("   目标IP: 192.168.1.100")
    print("   用户名: administrator")
    print("   密码: [密码]")
    print()
    print("2. PowerShell远程:")
    print("   需要目标启用PowerShell远程功能")
    print("   使用Enter-PSSession或Invoke-Command")
    print()
    print("3. 网络扫描:")
    print("   自动扫描局域网设备")
    print("   检查RDP服务可用性")
    print()
    print("⚠️  重要提醒:")
    print("   • 仅用于教育和授权的安全测试")
    print("   • 需要合法的管理员凭据")
    print("   • 遵守相关法律法规")
    
    print("=" * 60)

if __name__ == "__main__":
    main()