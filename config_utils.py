#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通用配置工具库
为所有工具提供自定义配置和Y/N确认功能
"""

import re

def validate_ip(ip):
    """验证IP地址格式"""
    pattern = r'^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
    return re.match(pattern, ip) is not None

def validate_port(port):
    """验证端口号格式"""
    try:
        port = int(port)
        return 1 <= port <= 65535
    except ValueError:
        return False

def get_input_with_default(prompt, default="", validator=None, error_msg="❌ 输入无效"):
    """获取用户输入，支持默认值和验证"""
    while True:
        user_input = input(f"{prompt} (默认{default}): ").strip()
        
        # 如果用户输入为空，使用默认值
        if not user_input and default:
            return default
        
        # 如果有验证器，验证输入
        if validator:
            if validator(user_input):
                return user_input
            else:
                print(error_msg)
        else:
            return user_input

def get_int_input(prompt, default=0, min_val=None, max_val=None):
    """获取整数输入"""
    while True:
        try:
            user_input = input(f"{prompt} (默认{default}): ").strip()
            
            # 如果用户输入为空，使用默认值
            if not user_input:
                return default
            
            value = int(user_input)
            
            # 检查最小值
            if min_val is not None and value < min_val:
                print(f"❌ 值不能小于 {min_val}")
                continue
            
            # 检查最大值
            if max_val is not None and value > max_val:
                print(f"❌ 值不能大于 {max_val}")
                continue
            
            return value
            
        except ValueError:
            print("❌ 请输入有效的数字")

def get_choice_input(prompt, choices, default=None):
    """获取选择输入"""
    while True:
        print(f"{prompt}")
        for i, choice in enumerate(choices, 1):
            print(f"  {i}. {choice}")
        
        if default:
            user_input = input(f"请选择 (1-{len(choices)}, 默认{default}): ").strip()
        else:
            user_input = input(f"请选择 (1-{len(choices)}): ").strip()
        
        # 如果用户输入为空且有默认值，使用默认值
        if not user_input and default:
            return default
        
        try:
            choice_index = int(user_input) - 1
            if 0 <= choice_index < len(choices):
                return choices[choice_index]
            else:
                print(f"❌ 请选择 1-{len(choices)}")
        except ValueError:
            print("❌ 请输入有效的数字")

def confirm_execution(config_info):
    """显示配置信息并请求确认执行"""
    print("\n" + "=" * 60)
    print("          配置确认")
    print("=" * 60)
    
    for key, value in config_info.items():
        print(f"{key}: {value}")
    
    print("=" * 60)
    
    # 请求用户确认
    while True:
        confirm = input("\n确认执行? (Y/N): ").strip().upper()
        if confirm == 'Y':
            return True
        elif confirm == 'N':
            print("❌ 操作已取消")
            return False
        else:
            print("❌ 请输入 Y 或 N")

def show_section_header(title):
    """显示章节标题"""
    print("=" * 60)
    print(f"          {title}")
    print("=" * 60)

def show_attack_start(config_info):
    """显示攻击开始信息"""
    print("=" * 60)
    print("          攻击开始")
    print("=" * 60)
    
    for key, value in config_info.items():
        print(f"{key}: {value}")
    
    print("=" * 60)

def show_statistics(stats):
    """显示统计信息"""
    print("\n" + "=" * 60)
    print("          统计信息")
    print("=" * 60)
    
    for key, value in stats.items():
        print(f"{key}: {value}")
    
    print("=" * 60)

class BaseToolConfig:
    """基础工具配置类"""
    
    def __init__(self, tool_name):
        self.tool_name = tool_name
        self.config_info = {}
        self.stats = {}
    
    def get_basic_config(self):
        """获取基础配置"""
        show_section_header(f"{self.tool_name} - 自定义配置")
        
        # 目标IP配置
        while True:
            target_ip = input("请输入目标IP地址: ").strip()
            if validate_ip(target_ip):
                self.config_info['目标IP'] = target_ip
                break
            else:
                print("❌ IP地址格式不正确，请重新输入")
        
        # 攻击时长配置
        duration = get_int_input("请输入攻击时长(秒)", 300, min_val=1)
        self.config_info['攻击时长'] = f"{duration}秒"
        
        return self.config_info
    
    def get_advanced_config(self):
        """获取高级配置（子类可重写）"""
        return self.config_info
    
    def get_full_config(self):
        """获取完整配置"""
        self.get_basic_config()
        self.get_advanced_config()
        return self.config_info
    
    def confirm_and_execute(self, execute_function):
        """确认配置并执行"""
        if confirm_execution(self.config_info):
            show_attack_start(self.config_info)
            execute_function()
            show_statistics(self.stats)
        else:
            print("❌ 操作已取消")

# 工具特定的配置类
class DDoSConfig(BaseToolConfig):
    """DDoS工具配置"""
    
    def __init__(self):
        super().__init__("DDoS攻击工具")
    
    def get_advanced_config(self):
        """获取DDoS特定配置"""
        # 线程数配置
        threads = get_int_input("请输入线程数", 100, min_val=1, max_val=1000)
        self.config_info['线程数'] = threads
        
        # 攻击方法选择
        methods = ['GET', 'POST', 'TCP', 'UDP', 'SYN']
        method = get_choice_input("请选择攻击方法", methods, 'GET')
        self.config_info['攻击方法'] = method
        
        return self.config_info

class NetworkScanConfig(BaseToolConfig):
    """网络扫描工具配置"""
    
    def __init__(self):
        super().__init__("网络扫描工具")
    
    def get_advanced_config(self):
        """获取网络扫描特定配置"""
        # 端口范围配置
        port_range = input("请输入端口范围 (例如: 1-1000, 默认1-1000): ").strip() or "1-1000"
        self.config_info['端口范围'] = port_range
        
        # 扫描类型选择
        scan_types = ['快速扫描', '全面扫描', '服务识别', '操作系统识别']
        scan_type = get_choice_input("请选择扫描类型", scan_types, '快速扫描')
        self.config_info['扫描类型'] = scan_type
        
        return self.config_info

class VulnerabilityScanConfig(BaseToolConfig):
    """漏洞扫描工具配置"""
    
    def __init__(self):
        super().__init__("漏洞扫描工具")
    
    def get_advanced_config(self):
        """获取漏洞扫描特定配置"""
        # 扫描深度选择
        depths = ['快速扫描', '标准扫描', '深度扫描']
        depth = get_choice_input("请选择扫描深度", depths, '标准扫描')
        self.config_info['扫描深度'] = depth
        
        # 漏洞类型选择
        vuln_types = ['Web漏洞', '系统漏洞', '网络服务漏洞', '全部漏洞']
        vuln_type = get_choice_input("请选择漏洞类型", vuln_types, '全部漏洞')
        self.config_info['漏洞类型'] = vuln_type
        
        return self.config_info