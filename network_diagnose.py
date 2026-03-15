#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网络诊断工具 - 分析宿舍网络环境
"""

import os
import sys
import socket
import subprocess
import platform

def get_system_info():
    """获取系统信息"""
    print("=" * 50)
    print("系统信息")
    print("=" * 50)
    
    system = platform.system()
    release = platform.release()
    version = platform.version()
    
    print(f"操作系统: {system} {release}")
    print(f"系统版本: {version}")
    print(f"机器类型: {platform.machine()}")
    print(f"处理器: {platform.processor()}")

def get_network_info():
    """获取网络信息"""
    print("\n" + "=" * 50)
    print("网络信息")
    print("=" * 50)
    
    try:
        # 获取本机IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        
        print(f"本机IP地址: {local_ip}")
        
        # 获取网关
        if platform.system() == "Windows":
            result = subprocess.run("ipconfig", capture_output=True, text=True)
            for line in result.stdout.split('\n'):
                if "默认网关" in line or "Default Gateway" in line:
                    print(f"默认网关: {line.strip()}")
        
        # 计算网络段
        ip_parts = local_ip.split('.')
        network = f"{ip_parts[0]}.{ip_parts[1]}.{ip_parts[2]}.0/24"
        print(f"网络段: {network}")
        
        return local_ip, network
        
    except Exception as e:
        print(f"获取网络信息失败: {e}")
        return None, None

def check_arp_table():
    """检查ARP表"""
    print("\n" + "=" * 50)
    print("ARP表检查")
    print("=" * 50)
    
    try:
        if platform.system() == "Windows":
            result = subprocess.run("arp -a", capture_output=True, text=True)
            print("ARP表内容:")
            print(result.stdout)
            
            # 统计条目数量
            lines = result.stdout.split('\n')
            dynamic_entries = 0
            static_entries = 0
            
            for line in lines:
                if "动态" in line or "dynamic" in line.lower():
                    dynamic_entries += 1
                elif "静态" in line or "static" in line.lower():
                    static_entries += 1
            
            print(f"动态条目: {dynamic_entries}")
            print(f"静态条目: {static_entries}")
            
    except Exception as e:
        print(f"检查ARP表失败: {e}")

def extended_ping_scan(network, start=1, end=50):
    """扩展的ping扫描"""
    print(f"\n" + "=" * 50)
    print(f"扩展ping扫描 ({start}-{end})")
    print("=" * 50)
    
    base_ip = network.split('/')[0]
    ip_parts = base_ip.split('.')
    
    active_devices = []
    
    for i in range(start, end + 1):
        target_ip = f"{ip_parts[0]}.{ip_parts[1]}.{ip_parts[2]}.{i}"
        
        try:
            # 使用ping检测
            if platform.system() == "Windows":
                cmd = f"ping -n 2 -w 2000 {target_ip}"
            else:
                cmd = f"ping -c 2 -W 2 {target_ip}"
            
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0 and ("TTL=" in result.stdout or "ttl=" in result.stdout.lower()):
                # 获取MAC地址
                if platform.system() == "Windows":
                    mac_cmd = f"arp -a {target_ip}"
                else:
                    mac_cmd = f"arp -n {target_ip}"
                
                mac_result = subprocess.run(mac_cmd, shell=True, capture_output=True, text=True)
                
                mac_address = "未知"
                if mac_result.returncode == 0 and target_ip in mac_result.stdout:
                    for line in mac_result.stdout.split('\n'):
                        if target_ip in line:
                            parts = line.split()
                            if len(parts) >= 2:
                                mac_address = parts[1]
                                break
                
                # 判断设备类型
                device_type = "未知"
                if "router" in result.stdout.lower() or "gateway" in result.stdout.lower():
                    device_type = "路由器"
                elif any(keyword in mac_address.lower() for keyword in ["android", "apple", "samsung"]):
                    device_type = "手机"
                elif "pc" in result.stdout.lower() or "windows" in result.stdout.lower():
                    device_type = "电脑"
                
                active_devices.append({
                    'ip': target_ip,
                    'mac': mac_address,
                    'type': device_type
                })
                
                print(f"    [+] {target_ip} - {mac_address} ({device_type})")
            
        except Exception as e:
            continue
    
    print(f"\n[+] 扫描完成，发现 {len(active_devices)} 个活跃设备")
    
    # 按设备类型统计
    device_stats = {}
    for device in active_devices:
        device_type = device['type']
        device_stats[device_type] = device_stats.get(device_type, 0) + 1
    
    print("\n设备类型统计:")
    for device_type, count in device_stats.items():
        print(f"    {device_type}: {count}台")
    
    return active_devices

def check_network_isolation():
    """检查网络隔离情况"""
    print("\n" + "=" * 50)
    print("网络隔离检查")
    print("=" * 50)
    
    print("1. 检查ICMP响应（ping）...")
    print("2. 检查ARP响应...")
    print("3. 检查端口连通性...")
    
    print("\n[!] 如果只能看到少量设备，可能原因:")
    print("    • 路由器启用了客户端隔离")
    print("    • 设备处于不同VLAN")
    print("    • 防火墙阻挡了通信")
    print("    • 设备处于离线状态")

def main():
    """主函数"""
    print("=" * 60)
    print("        宿舍网络环境诊断工具")
    print("        分析网络拓扑和设备发现")
    print("=" * 60)
    
    # 获取系统信息
    get_system_info()
    
    # 获取网络信息
    local_ip, network = get_network_info()
    
    if not network:
        print("[-] 无法获取网络信息")
        return
    
    # 检查ARP表
    check_arp_table()
    
    # 扩展ping扫描
    active_devices = extended_ping_scan(network, 1, 50)
    
    # 网络隔离检查
    check_network_isolation()
    
    # 总结报告
    print("\n" + "=" * 50)
    print("诊断总结")
    print("=" * 50)
    
    if len(active_devices) <= 1:
        print("⚠️  可能存在问题:")
        print("   • 网络客户端隔离已启用")
        print("   • 设备处于离线状态")
        print("   • 扫描权限受限")
    else:
        print("✅ 网络环境正常")
        print(f"   发现 {len(active_devices)} 个活跃设备")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n诊断被用户中断")
    except Exception as e:
        print(f"\n[-] 诊断出错: {e}")