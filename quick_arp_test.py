#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速ARP测试脚本
快速诊断ARP欺骗为什么无效
"""

import subprocess
import platform
import socket
from scapy.all import ARP, Ether, srp, sendp

def quick_test():
    """快速测试函数"""
    target_ip = "10.30.58.185"
    gateway_ip = "10.30.255.254"
    
    print("🔍 快速ARP欺骗诊断")
    print("=" * 50)
    
    # 1. 检查目标可达性
    print("1. 检查目标设备可达性...")
    try:
        param = '-n' if platform.system().lower() == 'windows' else '-c'
        result = subprocess.run(['ping', param, '2', target_ip], 
                              capture_output=True, text=True, timeout=5)
        
        if result.returncode == 0:
            print("   ✅ 目标设备在线")
        else:
            print("   ❌ 目标设备无响应")
            print("   输出:", result.stdout)
    except Exception as e:
        print(f"   ❌ Ping测试失败: {e}")
    
    # 2. 检查ARP表
    print("\n2. 检查ARP表...")
    try:
        result = subprocess.run(['arp', '-a'], capture_output=True, text=True)
        if target_ip in result.stdout:
            print("   ✅ 目标IP在ARP表中")
            for line in result.stdout.split('\n'):
                if target_ip in line:
                    print(f"      {line.strip()}")
        else:
            print("   ❌ 目标IP不在ARP表中")
            
        if gateway_ip in result.stdout:
            print("   ✅ 网关IP在ARP表中")
            for line in result.stdout.split('\n'):
                if gateway_ip in line:
                    print(f"      {line.strip()}")
    except Exception as e:
        print(f"   ❌ ARP表检查失败: {e}")
    
    # 3. 测试直接ARP通信
    print("\n3. 测试直接ARP通信...")
    try:
        arp_request = Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst=target_ip)
        answered, unanswered = srp(arp_request, timeout=3, verbose=False)
        
        if answered:
            target_mac = answered[0][1].hwsrc
            print(f"   ✅ 直接ARP通信成功")
            print(f"      目标MAC: {target_mac}")
        else:
            print("   ❌ 直接ARP通信失败")
            print("   💡 强烈怀疑存在客户端隔离")
    except Exception as e:
        print(f"   ❌ ARP通信测试失败: {e}")
    
    # 4. 网络环境分析
    print("\n4. 网络环境分析...")
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    
    target_segment = '.'.join(target_ip.split('.')[:3])
    local_segment = '.'.join(local_ip.split('.')[:3])
    
    print(f"   本机IP: {local_ip}")
    print(f"   目标IP: {target_ip}")
    print(f"   网关IP: {gateway_ip}")
    
    if target_segment == local_segment:
        print("   ✅ 网络段匹配")
    else:
        print("   ❌ 网络段不匹配")
    
    print("\n" + "=" * 50)
    print("💡 诊断结论:")
    print("   如果直接ARP通信失败，说明存在客户端隔离")
    print("   客户端隔离是常见的企业/学校网络设置")
    print("   在这种环境下，传统ARP欺骗无效")
    print("\n🔧 解决方案:")
    print("   1. 使用网关级ARP欺骗")
    print("   2. 尝试DNS劫持等其他攻击方式")
    print("   3. 使用ICMP重定向攻击")

if __name__ == "__main__":
    quick_test()