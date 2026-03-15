#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARP欺骗适配器 - 专门处理ARP欺骗工具的执行
"""

import subprocess
import json
import time
import os
from datetime import datetime

class ARPAdapter:
    """ARP欺骗适配器"""
    
    def __init__(self):
        self.default_config = {
            "target_ip": "192.168.1.100",
            "gateway_ip": "192.168.1.1", 
            "interface": "eth0",
            "duration": 300
        }
    
    def execute_arp_spoof(self, target_ip, gateway_ip, interface="eth0", duration=300, intensity="medium"):
        """执行ARP欺骗攻击"""
        
        # 验证参数
        if not target_ip or not gateway_ip:
            return False, "目标IP和网关IP不能为空"
        
        # 使用新的命令行参数模式
        command = f"python arp_spoof_simple.py --target {target_ip} --gateway {gateway_ip} --duration {duration} --intensity {intensity} --auto"
        
        try:
            # 执行命令
            process = subprocess.Popen(command, shell=True, 
                                     stdout=subprocess.PIPE, 
                                     stderr=subprocess.PIPE,
                                     text=True,
                                     stdin=subprocess.PIPE)
            
            # 实时读取输出
            output_lines = []
            start_time = time.time()
            
            # 发送预定义的输入
            inputs = [target_ip, gateway_ip, interface, str(duration)]
            
            for user_input in inputs:
                process.stdin.write(user_input + "\n")
                process.stdin.flush()
                time.sleep(0.5)  # 给程序时间处理输入
            
            # 读取输出
            while True:
                # 检查是否超时
                if time.time() - start_time > duration + 10:  # 额外10秒缓冲
                    process.terminate()
                    output_lines.append("⏰ ARP欺骗时间结束，自动停止")
                    break
                
                # 读取输出
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    output_lines.append(output.strip())
            
            # 检查错误
            stderr = process.stderr.read()
            
            result = "\n".join(output_lines)
            
            if stderr:
                return False, f"执行错误: {stderr}"
            
            return True, result
            
        except Exception as e:
            return False, f"执行异常: {e}"
    
    def create_config_file(self, config):
        """创建配置文件"""
        filename = f"arp_spoof_{int(time.time())}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        
        return filename
    
    def get_network_info(self):
        """获取网络信息（简化实现）"""
        try:
            # 获取本机IP和网关（简化实现）
            import socket
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            
            # 推测网关（通常是.1或.254）
            ip_parts = local_ip.split('.')
            gateway_candidates = [
                f"{ip_parts[0]}.{ip_parts[1]}.{ip_parts[2]}.1",
                f"{ip_parts[0]}.{ip_parts[1]}.{ip_parts[2]}.254"
            ]
            
            return {
                "local_ip": local_ip,
                "gateway_candidates": gateway_candidates,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        except:
            return {
                "local_ip": "未知",
                "gateway_candidates": ["192.168.1.1", "192.168.1.254"],
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

def test_arp_adapter():
    """测试ARP适配器"""
    adapter = ARPAdapter()
    
    # 测试ARP欺骗
    success, result = adapter.execute_arp_spoof(
        target_ip="192.168.1.100",
        gateway_ip="192.168.1.1",
        duration=30  # 测试30秒
    )
    
    print(f"ARP欺骗结果: {success}")
    print(f"输出: {result}")

if __name__ == "__main__":
    test_arp_adapter()