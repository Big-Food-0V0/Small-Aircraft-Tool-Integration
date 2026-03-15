#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
渗透测试GUI界面
集成所有渗透测试工具的图形化界面
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import subprocess
import os
import sys
import json
from datetime import datetime

class PenetrationGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🔧 渗透测试工具平台")
        self.root.geometry("1200x800")
        self.root.configure(bg='#2c3e50')
        
        # 工具执行状态
        self.running_tools = {}
        self.log_text = None
        
        # 创建界面
        self.create_gui()
        
        # 工具配置
        self.tool_config = self.load_tool_config()
    
    def load_tool_config(self):
        """加载工具配置"""
        return {
            "web_attack": {
                "name": "🌐 Web攻击平台",
                "command": "python automated_web_attack_platform.py",
                "params": ["target_url"],
                "description": "自动化Web应用安全测试和攻击"
            },
            "subdomain_scan": {
                "name": "🔍 子域名枚举",
                "command": "python subdomain_enumeration_tool.py",
                "params": ["domain"],
                "description": "自动发现目标域名的所有子域名"
            },
            "whois_query": {
                "name": "📋 WHOIS查询",
                "command": "python whois_information_tool.py",
                "params": ["domain"],
                "description": "获取域名的注册信息和所有者信息"
            },
            "file_upload_exploit": {
                "name": "📁 文件上传漏洞",
                "command": "python file_upload_exploit_tool.py",
                "params": ["target_url"],
                "description": "文件上传功能漏洞利用和绕过"
            },
            "android_attack": {
                "name": "📱 Android攻击",
                "command": "python android_attack_toolkit.py",
                "params": ["target_ip"],
                "description": "Android设备攻击工具包"
            },
            "ios_attack": {
                "name": "📱 iOS攻击",
                "command": "python ios_attack_toolkit.py",
                "params": ["target_ip"],
                "description": "iOS设备攻击工具包"
            },
            "nmap_scan": {
                "name": "🔍 端口扫描",
                "command": "python nmap_scanner.py",
                "params": ["target"],
                "description": "专业端口扫描和服务识别"
            },
            "vulnerability_scan": {
                "name": "🛡️ 漏洞扫描",
                "command": "python vulnerability_scanner.py",
                "params": ["target"],
                "description": "系统漏洞扫描和安全评估"
            },
            "password_attack": {
                "name": "🔑 密码攻击",
                "command": "python password_attack_tool.py",
                "params": ["target"],
                "description": "密码破解和暴力攻击"
            },
            "wireless_attack": {
                "name": "📶 无线攻击",
                "command": "python wireless_attack_tool.py",
                "params": ["target"],
                "description": "无线网络攻击和破解"
            }
        }
    
    def create_gui(self):
        """创建GUI界面"""
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # 标题
        title_label = ttk.Label(main_frame, text="🔧 渗透测试工具平台", 
                               font=('Arial', 16, 'bold'), foreground='#3498db')
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # 左侧工具面板
        self.create_tool_panel(main_frame)
        
        # 右侧日志面板
        self.create_log_panel(main_frame)
        
        # 底部状态栏
        self.create_status_bar(main_frame)
    
    def create_tool_panel(self, parent):
        """创建工具选择面板"""
        tool_frame = ttk.LabelFrame(parent, text="🛠️ 工具选择", padding="10")
        tool_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        tool_frame.columnconfigure(0, weight=1)
        
        # 工具分类标签
        notebook = ttk.Notebook(tool_frame)
        notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Web攻击标签
        web_frame = ttk.Frame(notebook, padding="10")
        notebook.add(web_frame, text="🌐 Web攻击")
        self.create_web_tools(web_frame)
        
        # 信息收集标签
        recon_frame = ttk.Frame(notebook, padding="10")
        notebook.add(recon_frame, text="🔍 信息收集")
        self.create_recon_tools(recon_frame)
        
        # 移动攻击标签
        mobile_frame = ttk.Frame(notebook, padding="10")
        notebook.add(mobile_frame, text="📱 移动攻击")
        self.create_mobile_tools(mobile_frame)
        
        # 网络攻击标签
        network_frame = ttk.Frame(notebook, padding="10")
        notebook.add(network_frame, text="🌐 网络攻击")
        self.create_network_tools(network_frame)
        
        # 参数输入区域
        param_frame = ttk.LabelFrame(tool_frame, text="🎯 攻击参数", padding="10")
        param_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        param_frame.columnconfigure(1, weight=1)
        
        # 目标输入
        ttk.Label(param_frame, text="目标:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.target_entry = ttk.Entry(param_frame, width=30)
        self.target_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        
        # 额外参数
        ttk.Label(param_frame, text="参数:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.param_entry = ttk.Entry(param_frame, width=30)
        self.param_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        
        # 控制按钮
        button_frame = ttk.Frame(tool_frame)
        button_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        self.start_button = ttk.Button(button_frame, text="🚀 启动攻击", 
                                      command=self.start_attack)
        self.start_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.stop_button = ttk.Button(button_frame, text="🛑 停止攻击", 
                                     command=self.stop_attack, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(button_frame, text="🧹 清空日志", 
                  command=self.clear_log).pack(side=tk.LEFT)
    
    def create_web_tools(self, parent):
        """创建Web攻击工具"""
        tools = [
            ("web_attack", "🌐 Web攻击平台", "自动化Web应用安全测试"),
            ("file_upload_exploit", "📁 文件上传漏洞", "文件上传功能漏洞利用"),
            ("vulnerability_scan", "🛡️ 漏洞扫描", "系统漏洞扫描和安全评估"),
            ("password_attack", "🔑 密码攻击", "密码破解和暴力攻击")
        ]
        
        for i, (tool_id, name, desc) in enumerate(tools):
            frame = ttk.Frame(parent)
            frame.grid(row=i, column=0, sticky=(tk.W, tk.E), pady=2)
            
            var = tk.BooleanVar()
            cb = ttk.Checkbutton(frame, text=name, variable=var, 
                                command=lambda tid=tool_id: self.on_tool_select(tid))
            cb.pack(side=tk.LEFT)
            
            ttk.Label(frame, text=desc, font=('Arial', 8), foreground='#666').pack(side=tk.LEFT, padx=(10, 0))
            
            self.running_tools[tool_id] = {'var': var, 'name': name}
    
    def create_recon_tools(self, parent):
        """创建信息收集工具"""
        tools = [
            ("subdomain_scan", "🔍 子域名枚举", "自动发现目标域名的所有子域名"),
            ("whois_query", "📋 WHOIS查询", "获取域名注册信息和所有者信息"),
            ("nmap_scan", "🔍 端口扫描", "专业端口扫描和服务识别")
        ]
        
        for i, (tool_id, name, desc) in enumerate(tools):
            frame = ttk.Frame(parent)
            frame.grid(row=i, column=0, sticky=(tk.W, tk.E), pady=2)
            
            var = tk.BooleanVar()
            cb = ttk.Checkbutton(frame, text=name, variable=var,
                                command=lambda tid=tool_id: self.on_tool_select(tid))
            cb.pack(side=tk.LEFT)
            
            ttk.Label(frame, text=desc, font=('Arial', 8), foreground='#666').pack(side=tk.LEFT, padx=(10, 0))
            
            self.running_tools[tool_id] = {'var': var, 'name': name}
    
    def create_mobile_tools(self, parent):
        """创建移动攻击工具"""
        tools = [
            ("android_attack", "📱 Android攻击", "Android设备攻击工具包"),
            ("ios_attack", "📱 iOS攻击", "iOS设备攻击工具包")
        ]
        
        for i, (tool_id, name, desc) in enumerate(tools):
            frame = ttk.Frame(parent)
            frame.grid(row=i, column=0, sticky=(tk.W, tk.E), pady=2)
            
            var = tk.BooleanVar()
            cb = ttk.Checkbutton(frame, text=name, variable=var,
                                command=lambda tid=tool_id: self.on_tool_select(tid))
            cb.pack(side=tk.LEFT)
            
            ttk.Label(frame, text=desc, font=('Arial', 8), foreground='#666').pack(side=tk.LEFT, padx=(10, 0))
            
            self.running_tools[tool_id] = {'var': var, 'name': name}
    
    def create_network_tools(self, parent):
        """创建网络攻击工具"""
        tools = [
            ("wireless_attack", "📶 无线攻击", "无线网络攻击和破解")
        ]
        
        for i, (tool_id, name, desc) in enumerate(tools):
            frame = ttk.Frame(parent)
            frame.grid(row=i, column=0, sticky=(tk.W, tk.E), pady=2)
            
            var = tk.BooleanVar()
            cb = ttk.Checkbutton(frame, text=name, variable=var,
                                command=lambda tid=tool_id: self.on_tool_select(tid))
            cb.pack(side=tk.LEFT)
            
            ttk.Label(frame, text=desc, font=('Arial', 8), foreground='#666').pack(side=tk.LEFT, padx=(10, 0))
            
            self.running_tools[tool_id] = {'var': var, 'name': name}
    
    def create_log_panel(self, parent):
        """创建日志显示面板"""
        log_frame = ttk.LabelFrame(parent, text="📊 执行日志", padding="10")
        log_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        # 日志文本框
        self.log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, width=60, height=20)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置标签颜色
        self.log_text.tag_configure("success", foreground="green")
        self.log_text.tag_configure("error", foreground="red")
        self.log_text.tag_configure("warning", foreground="orange")
        self.log_text.tag_configure("info", foreground="blue")
    
    def create_status_bar(self, parent):
        """创建状态栏"""
        status_frame = ttk.Frame(parent)
        status_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        self.status_var = tk.StringVar(value="就绪")
        status_label = ttk.Label(status_frame, textvariable=self.status_var)
        status_label.pack(side=tk.LEFT)
        
        # 进度条
        self.progress = ttk.Progressbar(status_frame, mode='indeterminate')
        self.progress.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(10, 0))
    
    def on_tool_select(self, tool_id):
        """工具选择事件"""
        tool = self.running_tools[tool_id]
        if tool['var'].get():
            self.log(f"✅ 选择工具: {tool['name']}", "success")
        else:
            self.log(f"❌ 取消选择: {tool['name']}", "warning")
    
    def log(self, message, tag="info"):
        """添加日志"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        
        self.log_text.insert(tk.END, log_message, tag)
        self.log_text.see(tk.END)
        
        # 更新状态栏
        self.status_var.set(message)
    
    def start_attack(self):
        """启动攻击"""
        target = self.target_entry.get().strip()
        if not target:
            messagebox.showerror("错误", "请输入目标地址")
            return
        
        # 获取选中的工具
        selected_tools = []
        for tool_id, tool_info in self.running_tools.items():
            if tool_info['var'].get():
                selected_tools.append(tool_id)
        
        if not selected_tools:
            messagebox.showerror("错误", "请至少选择一个工具")
            return
        
        # 更新界面状态
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.progress.start()
        
        # 启动攻击线程
        attack_thread = threading.Thread(target=self.execute_attack, 
                                        args=(selected_tools, target))
        attack_thread.daemon = True
        attack_thread.start()
    
    def execute_attack(self, tool_ids, target):
        """执行攻击"""
        self.log(f"🚀 开始攻击目标: {target}", "success")
        
        for tool_id in tool_ids:
            if tool_id in self.tool_config:
                tool = self.tool_config[tool_id]
                self.log(f"🔧 执行工具: {tool['name']}", "info")
                
                try:
                    # 构建命令
                    command = f"{tool['command']} {target}"
                    
                    # 执行命令
                    process = subprocess.Popen(command, shell=True, 
                                             stdout=subprocess.PIPE, 
                                             stderr=subprocess.PIPE,
                                             text=True)
                    
                    # 实时读取输出
                    while True:
                        output = process.stdout.readline()
                        if output == '' and process.poll() is not None:
                            break
                        if output:
                            self.log(f"{tool['name']}: {output.strip()}", "info")
                    
                    # 检查错误输出
                    stderr = process.stderr.read()
                    if stderr:
                        self.log(f"❌ {tool['name']} 错误: {stderr}", "error")
                    else:
                        self.log(f"✅ {tool['name']} 执行完成", "success")
                        
                except Exception as e:
                    self.log(f"❌ {tool['name']} 执行失败: {e}", "error")
        
        # 攻击完成
        self.attack_complete()
    
    def stop_attack(self):
        """停止攻击"""
        self.log("🛑 用户停止攻击", "warning")
        self.attack_complete()
    
    def attack_complete(self):
        """攻击完成处理"""
        # 更新界面状态
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.progress.stop()
        
        self.log("📊 攻击执行完成", "success")
        self.status_var.set("攻击完成")
    
    def clear_log(self):
        """清空日志"""
        self.log_text.delete(1.0, tk.END)
        self.log("🧹 日志已清空", "info")

def main():
    """主函数"""
    try:
        root = tk.Tk()
        app = PenetrationGUI(root)
        root.mainloop()
    except Exception as e:
        print(f"GUI启动错误: {e}")
        messagebox.showerror("错误", f"GUI启动失败: {e}")

if __name__ == "__main__":
    main()