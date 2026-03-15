#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
交互式渗透测试GUI
支持用户配置和实时交互的完整工具平台
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog, simpledialog
import threading
import subprocess
import os
import sys
import json
from datetime import datetime
import socket

class InteractivePenetrationGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🔧 交互式渗透测试平台")
        self.root.geometry("1400x900")
        self.root.configure(bg='#1e1e1e')
        
        # 工具执行状态
        self.active_processes = {}
        self.tool_windows = {}
        
        # 工具配置
        self.tool_config = self.load_tool_config()
        
        # 创建界面
        self.create_main_interface()
    
    def load_tool_config(self):
        """加载完整的工具配置"""
        return {
            "ddos_attack": {
                "name": "💥 DDoS攻击",
                "description": "分布式拒绝服务攻击",
                "category": "network",
                "interactive": True,
                "params": [
                    {"name": "target", "type": "entry", "label": "目标地址", "default": ""},
                    {"name": "method", "type": "combobox", "label": "攻击方法", 
                     "values": ["GET", "POST", "TCP", "UDP", "SYN"], "default": "GET"},
                    {"name": "threads", "type": "spinbox", "label": "线程数", 
                     "from": 1, "to": 1000, "default": 100},
                    {"name": "duration", "type": "spinbox", "label": "持续时间(秒)", 
                     "from": 10, "to": 3600, "default": 60}
                ],
                "command": "python start.py {method} {target} {threads} {duration}"
            },
            "arp_spoof": {
                "name": "🔄 ARP欺骗",
                "description": "ARP缓存投毒攻击",
                "category": "network",
                "interactive": True,
                "params": [
                    {"name": "target_ip", "type": "entry", "label": "目标IP", "default": ""},
                    {"name": "gateway_ip", "type": "entry", "label": "网关IP", "default": ""},
                    {"name": "interface", "type": "entry", "label": "网络接口", "default": "eth0"},
                    {"name": "duration", "type": "spinbox", "label": "持续时间(秒)", 
                     "from": 10, "to": 3600, "default": 300}
                ],
                "command": "python arp_spoof_simple.py"
            },
            "dns_hijack": {
                "name": "🌐 DNS劫持",
                "description": "DNS查询劫持攻击",
                "category": "network",
                "interactive": True,
                "params": [
                    {"name": "target_domain", "type": "entry", "label": "目标域名", "default": ""},
                    {"name": "redirect_ip", "type": "entry", "label": "重定向IP", "default": ""},
                    {"name": "listen_port", "type": "spinbox", "label": "监听端口", 
                     "from": 1, "to": 65535, "default": 53}
                ],
                "command": "python dns_hijack_simple.py"
            },
            "web_attack": {
                "name": "🌐 Web攻击",
                "description": "自动化Web应用攻击",
                "category": "web",
                "interactive": True,
                "params": [
                    {"name": "target_url", "type": "entry", "label": "目标URL", "default": ""},
                    {"name": "attack_type", "type": "combobox", "label": "攻击类型",
                     "values": ["sql_injection", "xss", "directory_traversal", "brute_force"], "default": "sql_injection"}
                ],
                "command": "python automated_web_attack_platform.py"
            },
            "subdomain_scan": {
                "name": "🔍 子域名扫描",
                "description": "子域名枚举发现",
                "category": "recon",
                "interactive": True,
                "params": [
                    {"name": "domain", "type": "entry", "label": "目标域名", "default": ""},
                    {"name": "threads", "type": "spinbox", "label": "线程数", 
                     "from": 1, "to": 100, "default": 20}
                ],
                "command": "python subdomain_enumeration_tool.py"
            },
            "port_scan": {
                "name": "🔍 端口扫描",
                "description": "网络端口和服务扫描",
                "category": "recon",
                "interactive": True,
                "params": [
                    {"name": "target", "type": "entry", "label": "目标IP/网段", "default": ""},
                    {"name": "port_range", "type": "entry", "label": "端口范围", "default": "1-1000"},
                    {"name": "threads", "type": "spinbox", "label": "线程数", 
                     "from": 1, "to": 100, "default": 50}
                ],
                "command": "python nmap_scanner.py"
            },
            "whois_lookup": {
                "name": "🔍 WHOIS查询",
                "description": "域名WHOIS信息查询",
                "category": "recon",
                "interactive": True,
                "params": [
                    {"name": "domain", "type": "entry", "label": "目标域名", "default": ""}
                ],
                "command": "python whois_information_tool.py"
            },
            "file_upload_exploit": {
                "name": "📁 文件上传利用",
                "description": "文件上传漏洞利用",
                "category": "web",
                "interactive": True,
                "params": [
                    {"name": "target_url", "type": "entry", "label": "目标URL", "default": ""},
                    {"name": "upload_path", "type": "entry", "label": "上传路径", "default": "/upload"}
                ],
                "command": "python file_upload_exploit_tool.py"
            }
        }
    
    def create_main_interface(self):
        """创建主界面"""
        # 创建主菜单
        self.create_menu()
        
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建左侧工具面板
        self.create_tool_panel(main_frame)
        
        # 创建右侧控制面板
        self.create_control_panel(main_frame)
        
        # 创建底部日志面板
        self.create_log_panel(main_frame)
    
    def create_menu(self):
        """创建菜单栏"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="保存配置", command=self.save_config)
        file_menu.add_command(label="加载配置", command=self.load_config)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.root.quit)
        
        # 工具菜单
        tool_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="工具", menu=tool_menu)
        
        for category in ["network", "web", "recon"]:
            cat_menu = tk.Menu(tool_menu, tearoff=0)
            tool_menu.add_cascade(label=self.get_category_name(category), menu=cat_menu)
            
            for tool_id, tool_info in self.tool_config.items():
                if tool_info["category"] == category:
                    cat_menu.add_command(
                        label=tool_info["name"], 
                        command=lambda tid=tool_id: self.open_tool_window(tid)
                    )
        
        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="关于", command=self.show_about)
    
    def get_category_name(self, category):
        """获取分类名称"""
        names = {
            "network": "网络攻击",
            "web": "Web攻击", 
            "recon": "信息收集"
        }
        return names.get(category, category)
    
    def create_tool_panel(self, parent):
        """创建工具面板"""
        tool_frame = ttk.LabelFrame(parent, text="🛠️ 工具库", padding="10")
        tool_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # 创建工具分类标签
        notebook = ttk.Notebook(tool_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # 为每个分类创建标签页
        categories = {"network": "网络攻击", "web": "Web攻击", "recon": "信息收集"}
        
        for category_id, category_name in categories.items():
            category_frame = ttk.Frame(notebook, padding="5")
            notebook.add(category_frame, text=category_name)
            
            # 添加该分类的工具
            self.add_tools_to_category(category_frame, category_id)
    
    def add_tools_to_category(self, parent, category):
        """向分类添加工具"""
        tools = [tool for tool_id, tool in self.tool_config.items() 
                if tool["category"] == category]
        
        for i, tool in enumerate(tools):
            tool_frame = ttk.Frame(parent)
            tool_frame.pack(fill=tk.X, pady=2)
            
            # 工具按钮
            btn = ttk.Button(
                tool_frame, 
                text=tool["name"],
                command=lambda t=tool: self.open_tool_config(t),
                width=20
            )
            btn.pack(side=tk.LEFT, padx=(0, 5))
            
            # 工具描述
            desc_label = ttk.Label(tool_frame, text=tool["description"], 
                                 font=('Arial', 8), foreground='#666')
            desc_label.pack(side=tk.LEFT)
    
    def create_control_panel(self, parent):
        """创建控制面板"""
        control_frame = ttk.LabelFrame(parent, text="🎯 控制中心", padding="10")
        control_frame.pack(side=tk.TOP, fill=tk.X, pady=(0, 10))
        
        # 状态显示
        status_frame = ttk.Frame(control_frame)
        status_frame.pack(fill=tk.X, pady=5)
        
        self.status_var = tk.StringVar(value="就绪")
        status_label = ttk.Label(status_frame, textvariable=self.status_var, 
                               font=('Arial', 10, 'bold'))
        status_label.pack(side=tk.LEFT)
        
        # 进度条
        self.progress = ttk.Progressbar(status_frame, mode='indeterminate')
        self.progress.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(10, 0))
        
        # 控制按钮
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(button_frame, text="🚀 快速扫描", 
                  command=self.quick_scan).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="🔍 深度扫描", 
                  command=self.deep_scan).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="💥 综合攻击", 
                  command=self.comprehensive_attack).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="🛑 停止所有", 
                  command=self.stop_all).pack(side=tk.LEFT)
    
    def create_log_panel(self, parent):
        """创建日志面板"""
        log_frame = ttk.LabelFrame(parent, text="📊 实时日志", padding="10")
        log_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        
        # 日志文本框
        self.log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, 
                                                 font=('Consolas', 9))
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # 配置标签颜色
        self.log_text.tag_configure("success", foreground="green")
        self.log_text.tag_configure("error", foreground="red")
        self.log_text.tag_configure("warning", foreground="orange")
        self.log_text.tag_configure("info", foreground="blue")
        self.log_text.tag_configure("command", foreground="purple")
    
    def open_tool_config(self, tool_info):
        """打开工具配置窗口"""
        tool_id = [k for k, v in self.tool_config.items() if v == tool_info][0]
        
        if tool_id in self.tool_windows:
            self.tool_windows[tool_id].lift()
            return
        
        # 创建工具配置窗口
        config_window = tk.Toplevel(self.root)
        config_window.title(f"配置 - {tool_info['name']}")
        config_window.geometry("500x400")
        config_window.transient(self.root)
        config_window.grab_set()
        
        self.tool_windows[tool_id] = config_window
        
        # 创建参数输入表单
        self.create_parameter_form(config_window, tool_info, tool_id)
        
        config_window.protocol("WM_DELETE_WINDOW", 
                              lambda: self.close_tool_window(tool_id))
    
    def create_parameter_form(self, parent, tool_info, tool_id):
        """创建参数输入表单"""
        main_frame = ttk.Frame(parent, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 工具描述
        desc_label = ttk.Label(main_frame, text=tool_info['description'], 
                              font=('Arial', 10), wraplength=400)
        desc_label.pack(pady=(0, 20))
        
        # 参数输入框架
        param_frame = ttk.Frame(main_frame)
        param_frame.pack(fill=tk.BOTH, expand=True)
        
        self.param_vars = {}
        
        for i, param in enumerate(tool_info.get('params', [])):
            row_frame = ttk.Frame(param_frame)
            row_frame.pack(fill=tk.X, pady=5)
            
            ttk.Label(row_frame, text=param['label'] + ":").pack(side=tk.LEFT)
            
            if param['type'] == 'entry':
                var = tk.StringVar(value=param.get('default', ''))
                entry = ttk.Entry(row_frame, textvariable=var, width=30)
                entry.pack(side=tk.LEFT, padx=(10, 0), fill=tk.X, expand=True)
                self.param_vars[param['name']] = var
            
            elif param['type'] == 'combobox':
                var = tk.StringVar(value=param.get('default', ''))
                combo = ttk.Combobox(row_frame, textvariable=var, 
                                   values=param['values'], width=27)
                combo.pack(side=tk.LEFT, padx=(10, 0), fill=tk.X, expand=True)
                self.param_vars[param['name']] = var
            
            elif param['type'] == 'spinbox':
                var = tk.IntVar(value=param.get('default', 1))
                spin = tk.Spinbox(row_frame, from_=param['from'], to=param['to'], 
                                 textvariable=var, width=10)
                spin.pack(side=tk.LEFT, padx=(10, 0))
                self.param_vars[param['name']] = var
        
        # 按钮区域
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        ttk.Button(button_frame, text="🚀 执行", 
                  command=lambda: self.execute_tool(tool_info, tool_id)).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="💾 保存配置", 
                  command=lambda: self.save_tool_config(tool_id)).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="❌ 关闭", 
                  command=lambda: self.close_tool_window(tool_id)).pack(side=tk.LEFT)
    
    def execute_tool(self, tool_info, tool_id):
        """执行工具"""
        # 收集参数
        params = {}
        for param_name, var in self.param_vars.items():
            params[param_name] = var.get()
        
        # 构建命令
        command = tool_info['command'].format(**params)
        
        self.log(f"执行命令: {command}", "command")
        
        # 在后台执行
        thread = threading.Thread(target=self.run_tool_command, 
                                args=(tool_info['name'], command, tool_id))
        thread.daemon = True
        thread.start()
    
    def run_tool_command(self, tool_name, command, tool_id):
        """运行工具命令"""
        try:
            self.progress.start()
            self.status_var.set(f"执行中: {tool_name}")
            
            process = subprocess.Popen(command, shell=True, 
                                     stdout=subprocess.PIPE, 
                                     stderr=subprocess.PIPE,
                                     text=True)
            
            self.active_processes[tool_id] = process
            
            # 实时读取输出
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    self.log(f"{tool_name}: {output.strip()}", "info")
            
            # 检查错误
            stderr = process.stderr.read()
            if stderr:
                self.log(f"错误: {stderr}", "error")
            else:
                self.log(f"✅ {tool_name} 执行完成", "success")
                
        except Exception as e:
            self.log(f"❌ 执行失败: {e}", "error")
        finally:
            if tool_id in self.active_processes:
                del self.active_processes[tool_id]
            
            self.progress.stop()
            self.status_var.set("就绪")
    
    def save_tool_config(self, tool_id):
        """保存工具配置"""
        try:
            config_data = {}
            for param_name, var in self.param_vars.items():
                config_data[param_name] = var.get()
            
            filename = f"{tool_id}_config.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, ensure_ascii=False, indent=2)
            
            self.log(f"✅ 配置已保存到 {filename}", "success")
            messagebox.showinfo("保存成功", f"配置已保存到 {filename}")
            
        except Exception as e:
            self.log(f"❌ 保存配置失败: {e}", "error")
            messagebox.showerror("保存失败", f"保存配置时出错: {e}")
    
    def close_tool_window(self, tool_id):
        """关闭工具窗口"""
        if tool_id in self.tool_windows:
            self.tool_windows[tool_id].destroy()
            del self.tool_windows[tool_id]
    
    def open_tool_window(self, tool_id):
        """打开工具窗口"""
        if tool_id in self.tool_config:
            self.open_tool_config(self.tool_config[tool_id])
    
    def log(self, message, level="info"):
        """添加日志"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"
        
        self.log_text.insert(tk.END, formatted_message)
        self.log_text.tag_add(level, f"{self.log_text.index(tk.END)}-{len(formatted_message)}c", self.log_text.index(tk.END))
        self.log_text.see(tk.END)
    
    def save_config(self):
        """保存全局配置"""
        try:
            config_data = {
                "global_config": {
                    "last_used_tools": list(self.tool_windows.keys()),
                    "save_timestamp": datetime.now().isoformat()
                }
            }
            
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON 文件", "*.json"), ("所有文件", "*.*")]
            )
            
            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(config_data, f, ensure_ascii=False, indent=2)
                
                self.log(f"✅ 全局配置已保存到 {filename}", "success")
                messagebox.showinfo("保存成功", "全局配置已保存")
                
        except Exception as e:
            self.log(f"❌ 保存全局配置失败: {e}", "error")
            messagebox.showerror("保存失败", f"保存全局配置时出错: {e}")
    
    def load_config(self):
        """加载全局配置"""
        try:
            filename = filedialog.askopenfilename(
                filetypes=[("JSON 文件", "*.json"), ("所有文件", "*.*")]
            )
            
            if filename:
                with open(filename, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                
                # 应用配置
                if "global_config" in config_data:
                    self.log("✅ 全局配置已加载", "success")
                    messagebox.showinfo("加载成功", "全局配置已加载")
                
        except Exception as e:
            self.log(f"❌ 加载配置失败: {e}", "error")
            messagebox.showerror("加载失败", f"加载配置时出错: {e}")
    
    def quick_scan(self):
        """快速扫描"""
        target = simpledialog.askstring("快速扫描", "请输入目标IP或域名:")
        if target:
            self.log(f"🚀 开始快速扫描: {target}", "info")
            # 执行快速扫描逻辑
            self.execute_quick_scan(target)
    
    def deep_scan(self):
        """深度扫描"""
        target = simpledialog.askstring("深度扫描", "请输入目标IP或域名:")
        if target:
            self.log(f"🔍 开始深度扫描: {target}", "info")
            # 执行深度扫描逻辑
            self.execute_deep_scan(target)
    
    def comprehensive_attack(self):
        """综合攻击"""
        target = simpledialog.askstring("综合攻击", "请输入目标IP或域名:")
        if target:
            self.log(f"💥 开始综合攻击: {target}", "info")
            # 执行综合攻击逻辑
            self.execute_comprehensive_attack(target)
    
    def execute_quick_scan(self, target):
        """执行快速扫描"""
        commands = [
            f"python subdomain_enumeration_tool.py {target} --threads 10",
            f"python nmap_scanner.py {target} --ports 1-1000"
        ]
        
        for cmd in commands:
            thread = threading.Thread(target=self.run_tool_command, 
                                    args=("快速扫描", cmd, "quick_scan"))
            thread.daemon = True
            thread.start()
    
    def execute_deep_scan(self, target):
        """执行深度扫描"""
        commands = [
            f"python subdomain_enumeration_tool.py {target} --threads 50",
            f"python nmap_scanner.py {target} --ports 1-65535",
            f"python whois_information_tool.py {target}"
        ]
        
        for cmd in commands:
            thread = threading.Thread(target=self.run_tool_command, 
                                    args=("深度扫描", cmd, "deep_scan"))
            thread.daemon = True
            thread.start()
    
    def execute_comprehensive_attack(self, target):
        """执行综合攻击"""
        commands = [
            f"python start.py GET {target} 100 60",
            f"python arp_spoof_simple.py",
            f"python dns_hijack_simple.py"
        ]
        
        for cmd in commands:
            thread = threading.Thread(target=self.run_tool_command, 
                                    args=("综合攻击", cmd, "comprehensive_attack"))
            thread.daemon = True
            thread.start()
    
    def stop_all(self):
        """停止所有进程"""
        for tool_id, process in self.active_processes.items():
            try:
                process.terminate()
                self.log(f"🛑 已停止: {tool_id}", "warning")
            except Exception as e:
                self.log(f"❌ 停止失败: {tool_id} - {e}", "error")
        
        self.active_processes.clear()
        self.progress.stop()
        self.status_var.set("已停止所有进程")
    
    def show_about(self):
        """显示关于信息"""
        about_text = """交互式渗透测试平台

版本: 1.0
功能: 集成多种渗透测试工具
支持: ARP欺骗、DNS劫持、DDoS攻击、Web攻击等

作者: 渗透测试团队
日期: 2024年"""
        
        messagebox.showinfo("关于", about_text)

def main():
    """主函数"""
    root = tk.Tk()
    app = InteractivePenetrationGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()