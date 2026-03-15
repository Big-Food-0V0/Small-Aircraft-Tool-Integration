#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
目标MAC不可用诊断脚本
诊断为什么无法获取目标设备的MAC地址
"""

import sys
import os
import subprocess
import platform
import socket

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def check_target_connectivity(target_ip):
    """检查目标设备连通性"""
    print(f"🔍 检查目标设备 {target_ip} 的连通性...")
    
    # 方法1: Ping测试
    try:
        param = '-n' if platform.system().lower() == 'windows' else '-c'
        result = subprocess.run(['ping', param, '3', target_ip], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ Ping测试: 目标设备在线")
            return True
        else:
            print("❌ Ping测试: 目标设备无响应")
            return False
    except:
        print("❌ Ping测试失败")
        return False

def check_arp_table(target_ip):
    """检查系统ARP表"""
    print(f"\n🔍 检查系统ARP表中的 {target_ip}...")
    
    try:
        # Windows系统
        if platform.system().lower() == 'windows':
            result = subprocess.run(['arp', '-a'], capture_output=True, text=True)
            
            if target_ip in result.stdout:
                print("✅ 目标IP在系统ARP表中")
                # 提取MAC地址
                for line in result.stdout.split('\n'):
                    if target_ip in line:
                        parts = line.split()
                        if len(parts) >= 2:
                            mac = parts[1]
                            print(f"   当前MAC: {mac}")
                            return mac
            else:
                print("❌ 目标IP不在系统ARP表中")
        
        return None
        
    except Exception as e:
        print(f"❌ ARP表检查失败: {e}")
        return None

def check_network_segment(target_ip, local_ip):
    """检查网络段是否匹配"""
    print(f"\n🔍 检查网络段匹配性...")
    
    try:
        # 提取IP前两段
        target_segment = '.'.join(target_ip.split('.')[:2])
        local_segment = '.'.join(local_ip.split('.')[:2])
        
        if target_segment == local_segment:
            print(f"✅ 网络段匹配: {target_segment}.x.x")
            return True
        else:
            print(f"❌ 网络段不匹配: 目标({target_segment}) vs 本机({local_segment})")
            return False
            
    except Exception as e:
        print(f"❌ 网络段检查失败: {e}")
        return False

def check_scapy_arp_request(target_ip):
    """使用Scapy发送ARP请求"""
    print(f"\n🔍 使用Scapy发送ARP请求到 {target_ip}...")
    
    try:
        from scapy.all import ARP, Ether, srp
        
        # 发送ARP请求
        arp_request = Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst=target_ip)
        answered, unanswered = srp(arp_request, timeout=3, verbose=False)
        
        if answered:
            mac = answered[0][1].hwsrc
            print(f"✅ Scapy ARP请求成功: MAC = {mac}")
            return mac
        else:
            print("❌ Scapy ARP请求无响应")
            return None
            
    except ImportError:
        print("❌ Scapy库未安装")
        return None
    except Exception as e:
        print(f"❌ Scapy ARP请求失败: {e}")
        return None

def check_firewall_settings():
    """检查防火墙设置"""
    print(f"\n🔍 检查防火墙设置...")
    
    try:
        if platform.system().lower() == 'windows':
            # 检查Windows防火墙状态
            result = subprocess.run(['netsh', 'advfirewall', 'show', 'allprofiles'], 
                                  capture_output=True, text=True)
            
            if 'ON' in result.stdout:
                print("⚠️  Windows防火墙已启用")
            else:
                print("✅ Windows防火墙已禁用")
        
        print("💡 防火墙可能阻止ARP请求")
        
    except Exception as e:
        print(f"❌ 防火墙检查失败: {e}")

def diagnose_target_mac(target_ip):
    """主诊断函数"""
    print("=" * 60)
    print(f"          目标MAC不可用诊断报告")
    print("=" * 60)
    
    # 获取本机IP
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        print(f"本机IP: {local_ip}")
        print(f"目标IP: {target_ip}")
    except:
        local_ip = "未知"
    
    # 运行诊断测试
    tests = [
        ("网络连通性检查", lambda: check_target_connectivity(target_ip)),
        ("系统ARP表检查", lambda: check_arp_table(target_ip)),
        ("网络段匹配性", lambda: check_network_segment(target_ip, local_ip)),
        ("Scapy ARP请求", lambda: check_scapy_arp_request(target_ip)),
        ("防火墙设置检查", check_firewall_settings)
    ]
    
    results = {}
    for test_name, test_func in tests:
        results[test_name] = test_func()
    
    # 诊断总结
    print("\n" + "=" * 60)
    print("          诊断总结")
    print("=" * 60)
    
    if not results["网络连通性检查"]:
        print("❌ 主要问题: 目标设备不在线")
        print("💡 解决方案:")
        print("   1. 确保目标设备开机并联网")
        print("   2. 检查目标设备网络连接")
        print("   3. 确认目标IP地址正确")
    
    elif not results["网络段匹配性"]:
        print("❌ 主要问题: 网络段不匹配")
        print("💡 说明: 目标设备可能在不同子网")
        print("💡 解决方案:")
        print("   1. 确认目标设备在同一局域网")
        print("   2. 检查子网掩码设置")
    
    elif not results["Scapy ARP请求"]:
        print("❌ 主要问题: ARP请求被阻止")
        print("💡 可能原因:")
        print("   1. 目标设备防火墙阻止ARP")
        print("   2. 网络设备过滤ARP包")
        print("   3. 客户端隔离设置")
        print("💡 解决方案:")
        print("   1. 尝试使用广播模式ARP欺骗")
        print("   2. 检查网络设备设置")
    
    else:
        print("✅ 所有检查通过，但MAC仍不可用")
        print("💡 可能原因:")
        print("   1. 目标设备有特殊网络配置")
        print("   2. 网络环境有特殊限制")
        print("💡 解决方案:")
        print("   1. 使用增强版工具包的广播模式")
        print("   2. 尝试其他网络攻击方法")
    
    print("\n🔧 增强版工具包处理方式:")
    print("   1. 目标MAC不可用时自动切换到广播模式")
    print("   2. 广播模式仍可进行ARP欺骗，但效果可能受限")
    print("   3. 程序会提供详细的状态反馈")

def main():
    """主函数"""
    if len(sys.argv) > 1:
        target_ip = sys.argv[1]
    else:
        # 使用您提供的目标IP
        target_ip = "10.30.58.185"
    
    diagnose_target_mac(target_ip)

if __name__ == "__main__":
    main()