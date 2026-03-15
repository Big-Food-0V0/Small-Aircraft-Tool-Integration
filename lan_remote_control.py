#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
局域网专用远程控制工具
针对同一局域网下的两台电脑优化
⚠️ 仅用于教育和授权的安全测试
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import socket
import threading
import json
import subprocess
import os
import platform
from datetime import datetime

class LANRemoteControl:
    """局域网专用远程控制工具"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("局域网远程控制工具")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        # 连接状态
        self.is_connected = False
        self.client_socket = None
        self.receive_thread = None
        self.server_thread = None
        self.server_socket = None
        self.is_server_running = False
        
        # 创建界面
        self.create_interface()
        
        # 自动获取本机IP
        self.auto_detect_ip()
    
    def auto_detect_ip(self):
        """自动获取本机IP地址"""
        try:
            # 获取本机IP
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            self.local_ip_var.set(local_ip)
            
            # 自动设置服务器IP
            self.server_ip_var.set(local_ip)
            
            # 扫描局域网设备
            self.scan_lan_devices()
            
        except Exception as e:
            self.append_output(f"[WARN] 自动获取IP失败: {e}\n")
    
    def scan_lan_devices(self):
        """扫描局域网设备"""
        try:
            # 获取本机IP段
            local_ip = self.local_ip_var.get()
            ip_parts = local_ip.split('.')
            subnet = f"{ip_parts[0]}.{ip_parts[1]}.{ip_parts[2]}."
            
            self.append_output(f"[INFO] 扫描局域网: {subnet}1-254\n")
            
            # 在后台线程中扫描
            scan_thread = threading.Thread(target=self._scan_lan_devices, args=(subnet,))
            scan_thread.daemon = True
            scan_thread.start()
            
        except Exception as e:
            self.append_output(f"[ERROR] 扫描失败: {e}\n")
    
    def _scan_lan_devices(self, subnet):
        """实际扫描局域网设备"""
        devices = []
        
        for i in range(1, 255):
            ip = subnet + str(i)
            try:
                # 使用ping检测设备是否在线
                param = "-n" if platform.system().lower() == "windows" else "-c"
                result = subprocess.run(["ping", param, "1", "-w", "1000", ip], 
                                      capture_output=True, text=True, timeout=2)
                
                if "TTL=" in result.stdout or "ttl=" in result.stdout:
                    devices.append(ip)
                    self.root.after(0, lambda ip=ip: self.append_output(f"  发现设备: {ip}\n"))
                    
            except:
                pass
        
        self.root.after(0, lambda: self.append_output(f"[INFO] 扫描完成，发现 {len(devices)} 个在线设备\n"))
    
    def create_interface(self):
        """创建界面"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # 标题
        title_label = ttk.Label(main_frame, text="局域网远程控制工具", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 10))
        
        # 安全警告
        warning_label = ttk.Label(main_frame, 
                                 text="⚠️ 重要提醒: 此工具仅用于教育和授权的安全测试",
                                 foreground="red", font=("Arial", 10, "bold"))
        warning_label.grid(row=1, column=0, columnspan=3, pady=(0, 10))
        
        # 本机信息区域
        local_info_frame = ttk.LabelFrame(main_frame, text="本机信息", padding="10")
        local_info_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        local_info_frame.columnconfigure(1, weight=1)
        
        # 本机IP
        ttk.Label(local_info_frame, text="本机IP:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.local_ip_var = tk.StringVar(value="正在检测...")
        local_ip_label = ttk.Label(local_info_frame, textvariable=self.local_ip_var,
                                 foreground="blue", font=("Arial", 10, "bold"))
        local_ip_label.grid(row=0, column=1, sticky=tk.W, pady=5, padx=(5, 0))
        
        # 主机名
        ttk.Label(local_info_frame, text="主机名:").grid(row=0, column=2, sticky=tk.W, pady=5, padx=(20, 0))
        self.hostname_var = tk.StringVar(value=socket.gethostname())
        hostname_label = ttk.Label(local_info_frame, textvariable=self.hostname_var,
                                 foreground="green")
        hostname_label.grid(row=0, column=3, sticky=tk.W, pady=5, padx=(5, 0))
        
        # 服务器控制区域
        server_frame = ttk.LabelFrame(main_frame, text="服务器控制", padding="10")
        server_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        server_frame.columnconfigure(1, weight=1)
        
        # 启动服务器按钮
        self.start_server_button = ttk.Button(server_frame, text="启动服务器", 
                                             command=self.start_server)
        self.start_server_button.grid(row=0, column=0, sticky=tk.W, pady=5)
        
        # 服务器状态
        self.server_status_var = tk.StringVar(value="服务器未启动")
        server_status_label = ttk.Label(server_frame, textvariable=self.server_status_var,
                                      foreground="red")
        server_status_label.grid(row=0, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # 客户端连接区域
        client_frame = ttk.LabelFrame(main_frame, text="客户端连接", padding="10")
        client_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        client_frame.columnconfigure(1, weight=1)
        
        # 服务器IP
        ttk.Label(client_frame, text="目标IP:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.server_ip_var = tk.StringVar()
        self.server_ip_entry = ttk.Entry(client_frame, textvariable=self.server_ip_var, width=15)
        self.server_ip_entry.grid(row=0, column=1, sticky=tk.W, pady=5, padx=(5, 0))
        
        # 端口
        ttk.Label(client_frame, text="端口:").grid(row=0, column=2, sticky=tk.W, pady=5, padx=(20, 0))
        self.port_var = tk.StringVar(value="8888")
        self.port_entry = ttk.Entry(client_frame, textvariable=self.port_var, width=10)
        self.port_entry.grid(row=0, column=3, sticky=tk.W, pady=5, padx=(5, 0))
        
        # 连接按钮
        self.connect_button = ttk.Button(client_frame, text="连接服务器", 
                                        command=self.connect_server)
        self.connect_button.grid(row=0, column=4, sticky=tk.W, pady=5, padx=(20, 0))
        
        self.disconnect_button = ttk.Button(client_frame, text="断开连接", 
                                           command=self.disconnect_server, state=tk.DISABLED)
        self.disconnect_button.grid(row=0, column=5, sticky=tk.W, pady=5, padx=(5, 0))
        
        # 命令输入区域
        command_frame = ttk.LabelFrame(main_frame, text="命令控制", padding="10")
        command_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        command_frame.columnconfigure(0, weight=1)
        
        # 快速命令按钮
        quick_commands_frame = ttk.Frame(command_frame)
        quick_commands_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 5))
        
        quick_commands = [
            ("系统信息", "system_info"),
            ("网络信息", "network_info"),
            ("进程列表", "process_list"),
            ("文件列表", "file_list ."),
            ("Ping测试", "ping 8.8.8.8"),
            ("网络扫描", "scan_network"),
            ("系统状态", "system_status")
        ]
        
        for i, (label, command) in enumerate(quick_commands):
            btn = ttk.Button(quick_commands_frame, text=label, width=10,
                           command=lambda cmd=command: self.set_command(cmd))
            btn.grid(row=0, column=i, padx=2, pady=2)
        
        # 命令输入框
        self.command_var = tk.StringVar()
        self.command_entry = ttk.Entry(command_frame, textvariable=self.command_var, width=50)
        self.command_entry.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        self.command_entry.bind("<Return>", self.send_command)
        
        # 发送按钮
        self.send_button = ttk.Button(command_frame, text="发送命令", 
                                     command=self.send_command, state=tk.DISABLED)
        self.send_button.grid(row=1, column=1, sticky=tk.W, pady=5, padx=(5, 0))
        
        # 输出区域
        output_frame = ttk.LabelFrame(main_frame, text="命令输出", padding="10")
        output_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(6, weight=1)
        
        self.output_text = scrolledtext.ScrolledText(output_frame, width=80, height=20)
        self.output_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 状态栏
        self.status_var = tk.StringVar(value="就绪 - 请启动服务器或连接服务器")
        status_label = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_label.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
    
    def set_command(self, command):
        """设置命令到输入框"""
        self.command_var.set(command)
        self.command_entry.focus()
    
    def append_output(self, text):
        """添加输出文本"""
        self.output_text.insert(tk.END, text)
        self.output_text.see(tk.END)
        self.root.update()
    
    def start_server(self):
        """启动服务器"""
        if self.is_server_running:
            messagebox.showinfo("提示", "服务器已在运行中")
            return
        
        try:
            port = int(self.port_var.get())
            
            # 启动服务器线程
            self.server_thread = threading.Thread(target=self.run_server)
            self.server_thread.daemon = True
            self.server_thread.start()
            
            self.is_server_running = True
            self.start_server_button.config(state=tk.DISABLED)
            self.server_status_var.set(f"服务器运行在端口 {port}")
            self.status_var.set("服务器已启动，等待连接...")
            
            self.append_output(f"[INFO] 服务器启动在端口 {port}\n")
            self.append_output("[INFO] 等待客户端连接...\n")
            
        except Exception as e:
            self.append_output(f"[ERROR] 启动服务器失败: {e}\n")
    
    def run_server(self):
        """运行服务器"""
        try:
            port = int(self.port_var.get())
            
            # 创建服务器socket
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind(('0.0.0.0', port))
            self.server_socket.listen(5)
            
            while self.is_server_running:
                try:
                    client_socket, client_address = self.server_socket.accept()
                    self.root.after(0, lambda: self.append_output(f"[INFO] 客户端连接: {client_address}\n"))
                    
                    # 处理客户端连接
                    client_thread = threading.Thread(target=self.handle_client, 
                                                   args=(client_socket, client_address))
                    client_thread.daemon = True
                    client_thread.start()
                    
                except Exception as e:
                    if self.is_server_running:
                        self.root.after(0, lambda: self.append_output(f"[ERROR] 接受连接失败: {e}\n"))
        
        except Exception as e:
            self.root.after(0, lambda: self.append_output(f"[ERROR] 服务器运行错误: {e}\n"))
        
        finally:
            if self.server_socket:
                self.server_socket.close()
    
    def handle_client(self, client_socket, client_address):
        """处理客户端请求"""
        try:
            while self.is_server_running:
                # 接收命令
                data = client_socket.recv(4096).decode('utf-8')
                if not data:
                    break
                
                # 解析命令
                try:
                    command_data = json.loads(data)
                    command = command_data.get('command', '')
                    args = command_data.get('args', [])
                    
                    self.root.after(0, lambda: self.append_output(f"[RECV] 来自 {client_address}: {command} {args}\n"))
                    
                    # 执行命令
                    result = self.execute_command(command, args)
                    
                    # 发送响应
                    response = {
                        'status': 'success',
                        'result': result,
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    client_socket.send(json.dumps(response).encode('utf-8'))
                    
                except json.JSONDecodeError:
                    error_response = {
                        'status': 'error',
                        'error': '无效的命令格式',
                        'timestamp': datetime.now().isoformat()
                    }
                    client_socket.send(json.dumps(error_response).encode('utf-8'))
        
        except Exception as e:
            self.root.after(0, lambda: self.append_output(f"[ERROR] 处理客户端错误: {e}\n"))
        
        finally:
            client_socket.close()
            self.root.after(0, lambda: self.append_output(f"[INFO] 客户端断开: {client_address}\n"))
    
    def execute_command(self, command, args):
        """执行命令"""
        try:
            if command == "system_info":
                return self.get_system_info()
            elif command == "network_info":
                return self.get_network_info()
            elif command == "process_list":
                return self.get_process_list()
            elif command == "file_list":
                path = args[0] if args else "."
                return self.list_files(path)
            elif command == "ping":
                target = args[0] if args else "8.8.8.8"
                return self.ping_test(target)
            elif command == "scan_network":
                return self.scan_network()
            elif command == "system_status":
                return self.get_system_status()
            else:
                return f"未知命令: {command}"
        
        except Exception as e:
            return f"命令执行错误: {e}"
    
    def get_system_info(self):
        """获取系统信息"""
        info = {
            'platform': platform.system(),
            'hostname': socket.gethostname(),
            'ip_address': socket.gethostbyname(socket.gethostname()),
            'current_dir': os.getcwd(),
            'timestamp': datetime.now().isoformat()
        }
        return info
    
    def get_network_info(self):
        """获取网络信息"""
        info = {
            'hostname': socket.gethostname(),
            'ip_address': socket.gethostbyname(socket.gethostname())
        }
        return info
    
    def get_process_list(self):
        """获取进程列表"""
        try:
            if platform.system() == "Windows":
                result = subprocess.run(['tasklist'], capture_output=True, text=True)
                processes = result.stdout.split('\n')[:10]  # 只显示前10个进程
                return {'processes': processes}
            else:
                result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
                processes = result.stdout.split('\n')[:10]
                return {'processes': processes}
        except Exception as e:
            return {'error': str(e)}
    
    def list_files(self, path):
        """列出文件"""
        try:
            files = []
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                files.append({
                    'name': item,
                    'is_dir': os.path.isdir(item_path),
                    'size': os.path.getsize(item_path) if os.path.isfile(item_path) else 0
                })
            
            return {
                'path': path,
                'files': files[:20]  # 限制数量
            }
        except Exception as e:
            return {'error': str(e)}
    
    def ping_test(self, target):
        """ping测试"""
        try:
            param = "-n" if platform.system().lower() == "windows" else "-c"
            result = subprocess.run(['ping', param, '3', target], capture_output=True, text=True)
            return {'ping_result': result.stdout}
        except Exception as e:
            return {'error': str(e)}
    
    def scan_network(self):
        """扫描网络"""
        return {'message': '网络扫描功能'}
    
    def get_system_status(self):
        """获取系统状态"""
        return {'message': '系统状态信息'}
    
    def connect_server(self):
        """连接服务器"""
        try:
            server_ip = self.server_ip_var.get().strip()
            port = int(self.port_var.get())
            
            if not server_ip:
                messagebox.showerror("错误", "请输入服务器地址")
                return
            
            # 创建socket连接
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.settimeout(5)
            
            self.append_output(f"[INFO] 正在连接服务器 {server_ip}:{port}...\n")
            
            # 连接服务器
            self.client_socket.connect((server_ip, port))
            
            self.is_connected = True
            self.connect_button.config(state=tk.DISABLED)
            self.disconnect_button.config(state=tk.NORMAL)
            self.send_button.config(state=tk.NORMAL)
            self.status_var.set(f"已连接 - {server_ip}:{port}")
            
            self.append_output("[SUCCESS] 服务器连接成功!\n")
            
            # 启动接收线程
            self.receive_thread = threading.Thread(target=self.receive_messages)
            self.receive_thread.daemon = True
            self.receive_thread.start()
            
        except Exception as e:
            self.append_output(f"[ERROR] 连接失败: {e}\n")
            if self.client_socket:
                self.client_socket.close()
                self.client_socket = None
    
    def disconnect_server(self):
        """断开连接"""
        self.is_connected = False
        
        if self.client_socket:
            try:
                self.client_socket.close()
            except:
                pass
            self.client_socket = None
        
        self.connect_button.config(state=tk.NORMAL)
        self.disconnect_button.config(state=tk.DISABLED)
        self.send_button.config(state=tk.DISABLED)
        self.status_var.set("已断开连接")
        
        self.append_output("[INFO] 已断开服务器连接\n")
    
    def send_command(self, event=None):
        """发送命令"""
        if not self.is_connected or not self.client_socket:
            messagebox.showerror("错误", "未连接到服务器")
            return
        
        command = self.command_var.get().strip()
        if not command:
            messagebox.showerror("错误", "请输入命令")
            return
        
        try:
            # 解析命令和参数
            parts = command.split()
            cmd = parts[0]
            args = parts[1:] if len(parts) > 1 else []
            
            # 构建命令数据
            command_data = {
                'command': cmd,
                'args': args,
                'timestamp': datetime.now().isoformat()
            }
            
            # 发送命令
            self.client_socket.send(json.dumps(command_data).encode('utf-8'))
            
            self.append_output(f"[SEND] {command}\n")
            self.command_var.set("")
            
        except Exception as e:
            self.append_output(f"[ERROR] 发送命令失败: {e}\n")
    
    def receive_messages(self):
        """接收服务器消息"""
        while self.is_connected and self.client_socket:
            try:
                # 接收数据
                data = self.client_socket.recv(4096).decode('utf-8')
                if not data:
                    break
                
                # 解析响应
                try:
                    response = json.loads(data)
                    status = response.get('status', '')
                    result = response.get('result', '')
                    timestamp = response.get('timestamp', '')
                    
                    if status == 'success':
                        self.append_output(f"[RESPONSE] 命令执行成功\n")
                        if isinstance(result, dict):
                            for key, value in result.items():
                                self.append_output(f"  {key}: {value}\n")
                        else:
                            self.append_output(f"  {result}\n")
                    else:
                        error = response.get('error', '未知错误')
                        self.append_output(f"[ERROR] 命令执行失败: {error}\n")
                    
                    self.append_output("\n")
                    
                except json.JSONDecodeError:
                    # 如果不是JSON格式，直接显示原始数据
                    self.append_output(f"[RAW] {data}\n")
                
            except socket.timeout:
                continue
            except Exception as e:
                if self.is_connected:
                    self.append_output(f"[ERROR] 接收数据失败: {e}\n")
                break
        
        # 连接断开
        if self.is_connected:
            self.root.after(0, self.disconnect_server)

def main():
    """主函数"""
    root = tk.Tk()
    app = LANRemoteControl(root)
    root.mainloop()

if __name__ == "__main__":
    main()