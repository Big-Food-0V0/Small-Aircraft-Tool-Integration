#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工具适配器 - 解决GUI无法处理交互式输入的问题
"""

import subprocess
import threading
import json
import os
from datetime import datetime
from ddos_adapter import DDoSAdapter
from arp_adapter import ARPAdapter
from universal_tool_adapter import UniversalToolAdapter

class ToolAdapter:
    """工具适配器类"""
    
    def __init__(self):
        self.tool_configs = self.load_tool_configs()
        self.ddos_adapter = DDoSAdapter()
        self.arp_adapter = ARPAdapter()
        self.universal_adapter = UniversalToolAdapter()
    
    def load_tool_configs(self):
        """加载工具配置"""
        return {
            "web_attack": {
                "name": "Web攻击平台",
                "interactive_params": [
                    {"name": "target_url", "prompt": "请输入目标URL", "type": "str"},
                    {"name": "attack_type", "prompt": "选择攻击类型(1-SQL注入 2-XSS 3-目录遍历)", "type": "int"},
                    {"name": "threads", "prompt": "线程数", "default": 10, "type": "int"}
                ],
                "auto_yes": True,
                "config_file": "web_attack_config.json"
            },
            "subdomain_scan": {
                "name": "子域名枚举",
                "interactive_params": [
                    {"name": "domain", "prompt": "请输入目标域名", "type": "str"},
                    {"name": "threads", "prompt": "线程数", "default": 20, "type": "int"}
                ],
                "auto_yes": True,
                "config_file": "subdomain_config.json"
            },
            "whois_query": {
                "name": "WHOIS查询",
                "interactive_params": [
                    {"name": "domain", "prompt": "请输入域名", "type": "str"}
                ],
                "auto_yes": True,
                "config_file": "whois_config.json"
            },
            "file_upload_exploit": {
                "name": "文件上传漏洞",
                "interactive_params": [
                    {"name": "target_url", "prompt": "请输入目标URL", "type": "str"},
                    {"name": "upload_path", "prompt": "上传路径", "default": "/upload", "type": "str"}
                ],
                "auto_yes": True,
                "config_file": "file_upload_config.json"
            }
        }
    
    def create_config_file(self, tool_id, params):
        """创建配置文件"""
        if tool_id in self.tool_configs:
            config_file = self.tool_configs[tool_id]["config_file"]
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(params, f, ensure_ascii=False, indent=2)
            return config_file
        return None
    
    def execute_tool_with_config(self, tool_id, target, additional_params=None):
        """使用配置文件执行工具"""
        if tool_id not in self.tool_configs:
            return False, "未知的工具ID"
        
        # 如果是DDoS攻击，使用专门的适配器
        if tool_id == "ddos_attack":
            return self.execute_ddos_attack(target, additional_params)
        
        # 如果是ARP欺骗，使用专门的适配器
        if tool_id == "arp_spoof":
            return self.execute_arp_spoof(target, additional_params)
        
        # 使用通用适配器处理其他所有工具
        return self.execute_with_universal_adapter(tool_id, target, additional_params)
    
    def execute_with_universal_adapter(self, tool_id, target, additional_params=None):
        """使用通用适配器执行工具"""
        try:
            # 构建参数
            params = {}
            
            # 如果target是IP地址或域名，添加到参数中
            if target:
                # 检查target类型
                import re
                ip_pattern = re.compile(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$')
                
                if ip_pattern.match(target):
                    # 如果是IP地址，添加到相关参数
                    params["target_ip"] = target
                    params["gateway_ip"] = self.infer_gateway(target)
                else:
                    # 如果是域名，添加到域名相关参数
                    params["domain"] = target
                    params["target_url"] = f"https://{target}"
            
            # 添加额外参数
            if additional_params:
                params.update(additional_params)
            
            # 验证参数
            valid, message = self.universal_adapter.validate_parameters(tool_id, params)
            if not valid:
                return False, f"参数验证失败: {message}"
            
            # 执行工具
            success, result = self.universal_adapter.execute_tool(tool_id, params)
            
            return success, result
            
        except Exception as e:
            return False, f"通用适配器执行异常: {e}"
    
    def infer_gateway(self, target_ip):
        """推测网关地址"""
        try:
            # 简单的网关推测逻辑
            ip_parts = target_ip.split('.')
            
            # 常见的网关地址
            gateway_candidates = [
                f"{ip_parts[0]}.{ip_parts[1]}.{ip_parts[2]}.1",
                f"{ip_parts[0]}.{ip_parts[1]}.{ip_parts[2]}.254",
                f"{ip_parts[0]}.{ip_parts[1]}.{ip_parts[2]}.2"
            ]
            
            return gateway_candidates[0]  # 返回第一个候选
            
        except:
            return "192.168.1.1"  # 默认网关
    
    def execute_ddos_attack(self, target, params=None):
        """执行DDoS攻击"""
        try:
            # 解析参数
            method = params.get("method", "GET") if params else "GET"
            threads = params.get("threads", 100) if params else 100
            duration = params.get("duration", 60) if params else 60
            
            # 使用DDoS适配器执行攻击
            success, result = self.ddos_adapter.execute_ddos_attack(
                method=method,
                target=target,
                threads=threads,
                duration=duration
            )
            
            return success, result
            
        except Exception as e:
            return False, f"DDoS攻击执行异常: {e}"
    
    def execute_arp_spoof(self, target, params=None):
        """执行ARP欺骗攻击"""
        try:
            # 解析参数
            target_ip = params.get("target_ip", "") if params else ""
            gateway_ip = params.get("gateway_ip", "") if params else ""
            interface = params.get("interface", "eth0") if params else "eth0"
            duration = params.get("duration", 300) if params else 300
            
            # 如果target参数是IP地址，使用它作为目标IP
            if not target_ip and target:
                # 检查target是否是IP地址
                import re
                ip_pattern = re.compile(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$')
                if ip_pattern.match(target):
                    target_ip = target
            
            # 验证必要参数
            if not target_ip:
                return False, "目标IP不能为空"
            if not gateway_ip:
                return False, "网关IP不能为空"
            
            # 使用ARP适配器执行攻击
            success, result = self.arp_adapter.execute_arp_spoof(
                target_ip=target_ip,
                gateway_ip=gateway_ip,
                interface=interface,
                duration=duration
            )
            
            return success, result
            
        except Exception as e:
            return False, f"ARP欺骗执行异常: {e}"
    
    def get_tool_params(self, tool_id):
        """获取工具参数配置"""
        if tool_id in self.tool_configs:
            return self.tool_configs[tool_id]["interactive_params"]
        return []

# 创建适配器实例
adapter = ToolAdapter()

def test_adapter():
    """测试适配器"""
    # 测试子域名扫描
    success, result = adapter.execute_tool_with_config("subdomain_scan", "example.com")
    print(f"子域名扫描结果: {success}, {result}")
    
    # 测试WHOIS查询
    success, result = adapter.execute_tool_with_config("whois_query", "google.com")
    print(f"WHOIS查询结果: {success}, {result}")

if __name__ == "__main__":
    test_adapter()