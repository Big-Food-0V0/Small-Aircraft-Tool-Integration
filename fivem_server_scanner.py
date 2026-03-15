#!/usr/bin/env python3
"""
FiveM服务器信息扫描工具
获取服务器IP、端口、状态等信息
"""

import socket
import requests
import json
import re
from urllib.parse import urlparse

def scan_fivem_server_info(server_address):
    """扫描FiveM服务器信息"""
    print(f"🔍 扫描FiveM服务器: {server_address}")
    
    # 解析输入（支持域名和IP）
    if ':' in server_address:
        parts = server_address.split(':')
        server_ip = parts[0]
        server_port = int(parts[1])
    else:
        server_ip = server_address
        server_port = 30120  # FiveM默认端口
    
    server_info = {
        'ip': server_ip,
        'port': server_port,
        'status': '未知',
        'players': 0,
        'max_players': 0,
        'hostname': '未知',
        'game': '未知'
    }
    
    # 1. 测试服务器连通性
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((server_ip, server_port))
        sock.close()
        
        if result == 0:
            server_info['status'] = '在线'
            print(f"✅ 服务器在线: {server_ip}:{server_port}")
        else:
            server_info['status'] = '离线'
            print(f"❌ 服务器离线")
            return server_info
    except:
        server_info['status'] = '连接失败'
        print(f"❌ 连接测试失败")
        return server_info
    
    # 2. 尝试获取服务器信息（通过HTTP API）
    try:
        # FiveM服务器可能有信息接口
        info_urls = [
            f'http://{server_ip}:{server_port}/info.json',
            f'http://{server_ip}:{server_port}/dynamic.json',
            f'http://{server_ip}:{server_port}/players.json'
        ]
        
        for url in info_urls:
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    
                    if 'hostname' in data:
                        server_info['hostname'] = data['hostname']
                    if 'clients' in data:
                        server_info['players'] = data['clients']
                    if 'sv_maxclients' in data:
                        server_info['max_players'] = data['sv_maxclients']
                    if 'gamename' in data:
                        server_info['game'] = data['gamename']
                    
                    print(f"📊 获取到服务器信息")
                    break
            except:
                pass
    except:
        print("⚠️ 无法获取详细信息")
    
    # 3. 端口扫描（检查其他服务）
    common_ports = [80, 443, 8080, 8443, 22, 21, 3306]
    open_ports = []
    
    for port in common_ports:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex((server_ip, port))
            sock.close()
            
            if result == 0:
                open_ports.append(port)
        except:
            pass
    
    server_info['open_ports'] = open_ports
    
    return server_info

def resolve_domain_to_ip(domain):
    """解析域名到IP"""
    try:
        ip = socket.gethostbyname(domain)
        print(f"🌐 域名解析: {domain} -> {ip}")
        return ip
    except:
        print(f"❌ 域名解析失败: {domain}")
        return None

def scan_fivem_server_list():
    """扫描FiveM服务器列表"""
    print("🔍 扫描在线FiveM服务器...")
    
    # FiveM服务器列表API（示例）
    server_list_urls = [
        'https://servers.fivem.net/servers/',
        'https://runtime.fivem.net/servers/',
    ]
    
    found_servers = []
    
    for url in server_list_urls:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                # 解析服务器列表（简化版）
                # 实际需要解析具体的API响应格式
                print(f"✅ 获取到服务器列表: {url}")
        except:
            print(f"❌ 无法访问: {url}")
    
    # 返回一些已知的测试服务器（示例）
    test_servers = [
        '51.91.100.222:30120',  # 示例服务器
        '145.239.200.123:30120', # 示例服务器
        '51.89.100.111:30120'   # 示例服务器
    ]
    
    return test_servers

def main():
    print("="*60)
    print("🎮 FiveM服务器信息扫描工具")
    print("="*60)
    
    print("\n🔧 选择扫描方式:")
    print("1. 扫描特定服务器")
    print("2. 扫描服务器列表")
    print("3. 域名解析")
    
    choice = input("请选择 (1/2/3): ").strip()
    
    if choice == "1":
        # 扫描特定服务器
        server_input = input("请输入服务器地址 (IP:端口 或 域名): ").strip()
        
        if not server_input:
            print("❌ 请输入有效的服务器地址")
            return
        
        # 扫描服务器信息
        server_info = scan_fivem_server_info(server_input)
        
        # 显示结果
        print("\n" + "="*60)
        print("📊 服务器信息扫描结果")
        print("="*60)
        print(f"🌐 IP地址: {server_info['ip']}")
        print(f"🔌 端口: {server_info['port']}")
        print(f"📡 状态: {server_info['status']}")
        print(f"👥 玩家: {server_info['players']}/{server_info['max_players']}")
        print(f"🏷️ 主机名: {server_info['hostname']}")
        print(f"🎮 游戏: {server_info['game']}")
        print(f"🔓 开放端口: {server_info.get('open_ports', [])}")
        print("="*60)
        
    elif choice == "2":
        # 扫描服务器列表
        servers = scan_fivem_server_list()
        
        print("\n📋 发现的服务器:")
        for i, server in enumerate(servers, 1):
            print(f"{i}. {server}")
            
        # 扫描发现的服务器
        if servers:
            scan_choice = input("\n是否扫描这些服务器? (y/n): ")
            if scan_choice.lower() == 'y':
                for server in servers:
                    print(f"\n扫描: {server}")
                    scan_fivem_server_info(server)
    
    elif choice == "3":
        # 域名解析
        domain = input("请输入域名: ").strip()
        if domain:
            ip = resolve_domain_to_ip(domain)
            if ip:
                print(f"✅ 解析结果: {domain} -> {ip}")
                
                # 扫描该服务器
                scan_choice = input("是否扫描该服务器? (y/n): ")
                if scan_choice.lower() == 'y':
                    scan_fivem_server_info(f"{ip}:30120")
    
    else:
        print("❌ 无效选择")

if __name__ == "__main__":
    main()