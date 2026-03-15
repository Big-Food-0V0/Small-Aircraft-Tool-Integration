#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
远程控制交互式界面
提供完整的命令输入和输出功能
⚠️ 仅用于教育和授权的安全测试
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import socket
import threading
import json
import time
from datetime import datetime

class RemoteControlInteractive:
    """远程控制交互式界面"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("远程控制交互工具")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # 连接状态
        self.is_connected = False
        self.client_socket = None
        self.receive_thread = None
        
        # 创建界面
        self.create_interface()
    
    def create_interface(self):
        """创建交互式界面"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # 标题
        title_label = ttk.Label(main_frame, text="远程控制交互工具", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 10))
        
        # 安全警告
        warning_label = ttk.Label(main_frame, 
                                 text="⚠️ 重要提醒: 此工具仅用于教育和授权的安全测试",
                                 foreground="red", font=("Arial", 10, "bold"))
        warning_label.grid(row=1, column=0, columnspan=3, pady=(0, 10))
        
        # 连接设置区域
        connection_frame = ttk.LabelFrame(main_frame, text="连接设置", padding="10")
        connection_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        connection_frame.columnconfigure(1, weight=1)
        
        # 服务器地址
        ttk.Label(connection_frame, text="服务器地址:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.server_ip_var = tk.StringVar(value="127.0.0.1")
        self.server_ip_entry = ttk.Entry(connection_frame, textvariable=self.server_ip_var, width=15)
        self.server_ip_entry.grid(row=0, column=1, sticky=tk.W, pady=5, padx=(5, 0))
        
        # 端口
        ttk.Label(connection_frame, text="端口:").grid(row=0, column=2, sticky=tk.W, pady=5, padx=(20, 0))
        self.port_var = tk.StringVar(value="8888")
        self.port_entry = ttk.Entry(connection_frame, textvariable=self.port_var, width=10)
        self.port_entry.grid(row=0, column=3, sticky=tk.W, pady=5, padx=(5, 0))
        
        # 连接按钮
        self.connect_button = ttk.Button(connection_frame, text="连接服务器", 
                                        command=self.connect_server)
        self.connect_button.grid(row=0, column=4, sticky=tk.W, pady=5, padx=(20, 0))
        
        self.disconnect_button = ttk.Button(connection_frame, text="断开连接", 
                                           command=self.disconnect_server, state=tk.DISABLED)
        self.disconnect_button.grid(row=0, column=5, sticky=tk.W, pady=5, padx=(5, 0))
        
        # 命令输入区域
        command_frame = ttk.LabelFrame(main_frame, text="命令输入", padding="10")
        command_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        command_frame.columnconfigure(0, weight=1)
        
        # 命令输入框
        self.command_var = tk.StringVar()
        self.command_entry = ttk.Entry(command_frame, textvariable=self.command_var, width=50)
        self.command_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        self.command_entry.bind("<Return>", self.send_command)
        
        # 发送按钮
        self.send_button = ttk.Button(command_frame, text="发送命令", 
                                     command=self.send_command, state=tk.DISABLED)
        self.send_button.grid(row=0, column=1, sticky=tk.W, pady=5, padx=(5, 0))
        
        # 快速命令按钮
        quick_commands_frame = ttk.Frame(command_frame)
        quick_commands_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))
        
        quick_commands = [
            ("系统信息", "system_info"),
            ("网络信息", "network_info"),
            ("进程列表", "process_list"),
            ("文件列表", "file_list ."),
            ("Ping测试", "ping 8.8.8.8"),
            ("帮助", "help")
        ]
        
        for i, (label, command) in enumerate(quick_commands):
            btn = ttk.Button(quick_commands_frame, text=label, width=10,
                           command=lambda cmd=command: self.set_command(cmd))
            btn.grid(row=0, column=i, padx=2, pady=2)
        
        # 输出区域
        output_frame = ttk.LabelFrame(main_frame, text="命令输出", padding="10")
        output_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        self.output_text = scrolledtext.ScrolledText(output_frame, width=80, height=20)
        self.output_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 状态栏
        self.status_var = tk.StringVar(value="未连接 - 请输入服务器地址并连接")
        status_label = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_label.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
    
    def set_command(self, command):
        """设置命令到输入框"""
        self.command_var.set(command)
        self.command_entry.focus()
    
    def append_output(self, text):
        """添加输出文本"""
        self.output_text.insert(tk.END, text)
        self.output_text.see(tk.END)
        self.root.update()
    
    def connect_server(self):
        """连接服务器"""
        try:
            server_ip = self.server_ip_var.get().strip()
            port = int(self.port_var.get())
            
            if not server_ip:
                messagebox.showerror("错误", "请输入服务器地址")
                return
            
            if port <= 0 or port > 65535:
                messagebox.showerror("错误", "端口号应在1-65535之间")
                return
            
            # 创建socket连接
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.settimeout(5)  # 5秒超时
            
            self.append_output(f"[INFO] 正在连接服务器 {server_ip}:{port}...\n")
            
            # 连接服务器
            self.client_socket.connect((server_ip, port))
            
            self.is_connected = True
            self.connect_button.config(state=tk.DISABLED)
            self.disconnect_button.config(state=tk.NORMAL)
            self.send_button.config(state=tk.NORMAL)
            self.status_var.set(f"已连接 - {server_ip}:{port}")
            
            self.append_output("[SUCCESS] 服务器连接成功!\n")
            self.append_output("💡 可用命令: system_info, network_info, process_list, file_list [路径], ping [目标], help\n\n")
            
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
    app = RemoteControlInteractive(root)
    root.mainloop()

if __name__ == "__main__":
    main()