#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通用工具适配器 - 解决所有交互式工具的输入问题
"""

import subprocess
import json
import time
import os
import re
from datetime import datetime
from io import StringIO
import sys

class UniversalToolAdapter:
    """通用工具适配器"""
    
    def __init__(self):
        self.tool_configs = self.load_tool_configs()
    
    def load_tool_configs(self):
        """加载所有工具的配置"""
        return {
            "arp_spoof": {
                "name": "ARP欺骗",
                "interactive_inputs": [
                    {"prompt": "请输入目标IP地址", "param_name": "target_ip", "type": "ip"},
                    {"prompt": "请输入网关IP地址", "param_name": "gateway_ip", "type": "ip"},
                    {"prompt": "请输入网络接口", "param_name": "interface", "default": "eth0", "type": "str"},
                    {"prompt": "请输入攻击时长(秒)", "param_name": "duration", "default": "300", "type": "int"},
                    {"prompt": "确认执行? (Y/N)", "param_name": "confirm", "default": "Y", "type": "confirm"}
                ],
                "command": "python arp_spoof_simple.py"
            },
            "dns_hijack": {
                "name": "DNS劫持", 
                "interactive_inputs": [
                    {"prompt": "请输入目标IP地址", "param_name": "target_ip", "type": "ip"},
                    {"prompt": "请输入网关IP地址", "param_name": "gateway_ip", "type": "ip"},
                    {"prompt": "请输入要劫持的域名", "param_name": "domain", "type": "str"},
                    {"prompt": "请输入重定向IP", "param_name": "redirect_ip", "type": "ip"},
                    {"prompt": "请输入攻击时长(秒)", "param_name": "duration", "default": "300", "type": "int"},
                    {"prompt": "确认执行? (Y/N)", "param_name": "confirm", "default": "Y", "type": "confirm"}
                ],
                "command": "python dns_hijack_simple.py"
            },
            "subdomain_scan": {
                "name": "子域名扫描",
                "interactive_inputs": [
                    {"prompt": "请输入目标域名", "param_name": "domain", "type": "str"},
                    {"prompt": "请输入线程数", "param_name": "threads", "default": "20", "type": "int"},
                    {"prompt": "确认执行? (Y/N)", "param_name": "confirm", "default": "Y", "type": "confirm"}
                ],
                "command": "python subdomain_enumeration_tool.py"
            },
            "whois_query": {
                "name": "WHOIS查询",
                "interactive_inputs": [
                    {"prompt": "请输入要查询的域名", "param_name": "domain", "type": "str"},
                    {"prompt": "确认执行? (Y/N)", "param_name": "confirm", "default": "Y", "type": "confirm"}
                ],
                "command": "python whois_information_tool.py"
            },
            "file_upload_exploit": {
                "name": "文件上传漏洞利用",
                "interactive_inputs": [
                    {"prompt": "请输入目标URL", "param_name": "target_url", "type": "str"},
                    {"prompt": "请输入上传路径", "param_name": "upload_path", "default": "/upload", "type": "str"},
                    {"prompt": "确认执行? (Y/N)", "param_name": "confirm", "default": "Y", "type": "confirm"}
                ],
                "command": "python file_upload_exploit_tool.py"
            },
            "web_attack": {
                "name": "Web攻击平台",
                "interactive_inputs": [
                    {"prompt": "请输入目标URL", "param_name": "target_url", "type": "str"},
                    {"prompt": "选择攻击类型(1-SQL注入 2-XSS 3-目录遍历)", "param_name": "attack_type", "default": "1", "type": "int"},
                    {"prompt": "请输入线程数", "param_name": "threads", "default": "10", "type": "int"},
                    {"prompt": "确认执行? (Y/N)", "param_name": "confirm", "default": "Y", "type": "confirm"}
                ],
                "command": "python automated_web_attack_platform.py"
            }
        }
    
    def execute_tool(self, tool_id, params=None):
        """执行工具"""
        if tool_id not in self.tool_configs:
            return False, f"未知的工具ID: {tool_id}"
        
        tool_config = self.tool_configs[tool_id]
        
        # 构建自动输入脚本
        input_script = self.build_input_script(tool_config, params)
        
        # 执行命令
        command = tool_config["command"]
        
        try:
            # 使用echo命令自动输入所有参数
            full_command = f"echo '{input_script}' | {command}"
            
            process = subprocess.Popen(full_command, shell=True, 
                                     stdout=subprocess.PIPE, 
                                     stderr=subprocess.PIPE,
                                     text=True)
            
            # 实时读取输出
            output_lines = []
            start_time = time.time()
            
            while True:
                # 检查是否超时（最长10分钟）
                if time.time() - start_time > 600:
                    process.terminate()
                    output_lines.append("⏰ 执行超时，自动停止")
                    break
                
                # 读取输出
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    output_lines.append(output.strip())
            
            # 检查错误
            stderr = process.stderr.read()
            
            # 过滤掉警告信息
            filtered_output = []
            for line in output_lines:
                if "DeprecationWarning" not in line and "RequestsDependencyWarning" not in line:
                    filtered_output.append(line)
            
            result = "\n".join(filtered_output)
            
            if stderr and "DeprecationWarning" not in stderr and "RequestsDependencyWarning" not in stderr:
                return False, f"执行错误: {stderr}"
            
            return True, result
            
        except Exception as e:
            return False, f"执行异常: {e}"
    
    def build_input_script(self, tool_config, params):
        """构建自动输入脚本"""
        inputs = []
        
        for input_config in tool_config["interactive_inputs"]:
            prompt = input_config["prompt"]
            param_name = input_config["param_name"]
            input_type = input_config["type"]
            default_value = input_config.get("default", "")
            
            # 如果提供了参数，使用参数值
            if params and param_name in params:
                value = str(params[param_name])
            else:
                # 否则使用默认值
                value = default_value
            
            # 对于确认类型，总是使用Y
            if input_type == "confirm":
                value = "Y"
            
            inputs.append(value)
        
        # 将输入用换行符连接
        return "\n".join(inputs)
    
    def get_tool_parameters(self, tool_id):
        """获取工具参数配置"""
        if tool_id in self.tool_configs:
            return self.tool_configs[tool_id]["interactive_inputs"]
        return []
    
    def validate_parameters(self, tool_id, params):
        """验证参数"""
        if tool_id not in self.tool_configs:
            return False, "未知的工具ID"
        
        tool_config = self.tool_configs[tool_id]
        
        for input_config in tool_config["interactive_inputs"]:
            param_name = input_config["param_name"]
            input_type = input_config["type"]
            
            # 跳过确认参数
            if input_type == "confirm":
                continue
            
            # 检查必要参数
            if param_name not in params and not input_config.get("default"):
                return False, f"缺少必要参数: {param_name}"
            
            # 验证参数类型
            if param_name in params:
                value = params[param_name]
                
                if input_type == "ip":
                    if not self.validate_ip(str(value)):
                        return False, f"参数 {param_name} 不是有效的IP地址"
                elif input_type == "int":
                    try:
                        int(value)
                    except ValueError:
                        return False, f"参数 {param_name} 必须是整数"
        
        return True, "参数验证通过"
    
    def validate_ip(self, ip):
        """验证IP地址格式"""
        ip_pattern = re.compile(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$')
        if not ip_pattern.match(ip):
            return False
        
        # 验证每个部分在0-255之间
        parts = ip.split('.')
        for part in parts:
            if not 0 <= int(part) <= 255:
                return False
        
        return True
    
    def create_config_file(self, tool_id, params):
        """创建配置文件"""
        if tool_id not in self.tool_configs:
            return None
        
        config = {
            "tool_id": tool_id,
            "tool_name": self.tool_configs[tool_id]["name"],
            "parameters": params,
            "timestamp": datetime.now().isoformat()
        }
        
        filename = f"{tool_id}_config_{int(time.time())}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        
        return filename

def test_universal_adapter():
    """测试通用适配器"""
    adapter = UniversalToolAdapter()
    
    # 测试ARP欺骗
    params = {
        "target_ip": "192.168.1.100",
        "gateway_ip": "192.168.1.1",
        "interface": "eth0",
        "duration": 30
    }
    
    success, result = adapter.execute_tool("arp_spoof", params)
    print(f"ARP欺骗结果: {success}")
    print(f"输出: {result}")

if __name__ == "__main__":
    test_universal_adapter()