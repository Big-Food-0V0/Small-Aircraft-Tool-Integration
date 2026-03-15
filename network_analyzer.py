#!/usr/bin/env python3
"""
网络分析工具 - 捕获和分析FiveM网络流量
"""

import socket
import struct
import threading
import time
from scapy.all import *
import subprocess

def capture_fivem_traffic(interface=None, duration=30):
    """捕获FiveM网络流量"""
    print("📡 开始捕获FiveM网络流量...")
    
    # FiveM相关端口
    fivem_ports = [30120, 30121, 30122, 30123]
    
    def packet_handler(packet):
        if packet.haslayer(IP):
            src_ip = packet[IP].src
            dst_ip = packet[IP].dst
            
            if packet.haslayer(TCP):
                src_port = packet[TCP].sport
                dst_port = packet[TCP].dport
                
                if src_port in fivem_ports or dst_port in fivem_ports:
                    print(f"🔍 FiveM流量: {src_ip}:{src_port} -> {dst_ip}:{dst_port}")
            
            elif packet.haslayer(UDP):
                src_port = packet[UDP].sport
                dst_port = packet[UDP].dport
                
                if src_port in fivem_ports or dst_port in fivem_ports:
                    print(f"🔍 FiveM UDP流量: {src_ip}:{src_port} -> {dst_ip}:{dst_port}")
    
    try:
        # 使用scapy捕获流量
        sniff(filter="tcp or udp", prn=packet_handler, timeout=duration)
    except Exception as e:
        print(f"❌ 流量捕获失败: {e}")

def get_local_fivem_connections():
    """获取本地FiveM连接信息"""
    print("🔗 检查本地FiveM连接...")
    
    try:
        # 使用netstat命令
        result = subprocess.run(['netstat', '-an'], capture_output=True, text=True)
        
        fivem_connections = []
        for line in result.stdout.split('\n'):
            if '30120' in line or '30121' in line or '30122' in line or '30123' in line:
                fivem_connections.append(line.strip())
        
        if fivem_connections:
            print("📊 发现的FiveM连接:")
            for conn in fivem_connections:
                print(f"   {conn}")
        else:
            print("ℹ️ 未发现FiveM连接")
            
    except Exception as e:
        print(f"❌ 连接检查失败: {e}")

def scan_network_for_fivem(subnet="192.168.1.0/24"):
    """扫描网络中的FiveM服务器"""
    print(f"🔍 扫描网络 {subnet} 中的FiveM服务器...")
    
    found_servers = []
    
    # 扫描30120端口
    for i in range(1, 255):
        ip = f"192.168.1.{i}"  # 修改为您的网络段
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((ip, 30120))
            sock.close()
            
            if result == 0:
                print(f"✅ 发现FiveM服务器: {ip}:30120")
                found_servers.append(f"{ip}:30120")
        except:
            pass
    
    return found_servers

def main():
    print("="*60)
    print("🌐 网络分析工具")
    print("="*60)
    
    print("\n🔧 选择分析方式:")
    print("1. 捕获FiveM网络流量")
    print("2. 检查本地FiveM连接")
    print("3. 扫描网络中的FiveM服务器")
    print("4. 使用FiveM服务器扫描器")
    
    choice = input("请选择 (1/2/3/4): ").strip()
    
    if choice == "1":
        # 流量捕获
        duration = input("捕获时长(秒，默认30): ").strip()
        duration = int(duration) if duration.isdigit() else 30
        
        capture_fivem_traffic(duration=duration)
        
    elif choice == "2":
        # 本地连接检查
        get_local_fivem_connections()
        
    elif choice == "3":
        # 网络扫描
        subnet = input("输入网络段 (如 192.168.1.0/24): ").strip()
        if not subnet:
            subnet = "192.168.1.0/24"
        
        servers = scan_network_for_fivem(subnet)
        
        if servers:
            print(f"\n📋 发现的服务器 ({len(servers)} 个):")
            for server in servers:
                print(f"   • {server}")
        else:
            print("❌ 未发现FiveM服务器")
    
    elif choice == "4":
        # 使用专门的扫描器
        subprocess.run(['python', 'fivem_server_scanner.py'])
    
    else:
        print("❌ 无效选择")

if __name__ == "__main__":
    main()