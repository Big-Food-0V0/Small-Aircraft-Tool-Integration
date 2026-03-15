#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
学校机房ARP欺骗可行性测试工具
⚠️ 仅用于教育和授权的安全测试
"""

import subprocess
import socket
import platform
import re
from scapy.all import ARP, Ether, srp, conf
import time

def check_network_environment():
    """检查网络环境特征"""
    print("=" * 60)
    print("          学校机房网络环境检测")
    print("=" * 60)
    
    results = {}
    
    # 1. 检查操作系统和权限
    print("\n[1] 系统环境检查:")
    print(f"   操作系统: {platform.system()} {platform.release()}")
    print(f"   主机名: {socket.gethostname()}")
    
    # 2. 检查网络配置
    print("\n[2] 网络配置检查:")
    try:
        # 获取本机IP和网关
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        print(f"   本机IP: {local_ip}")
        
        # 获取网关（Windows）
        if platform.system() == "Windows":
            result = subprocess.run(['route', 'print'], capture_output=True, text=True)
            gateway_match = re.search(r'0\.0\.0\.0\s+0\.0\.0\.0\s+(\d+\.\d+\.\d+\.\d+)', result.stdout)
            if gateway_match:
                gateway = gateway_match.group(1)
                print(f"   网关IP: {gateway}")
                results['gateway'] = gateway
        
        results['local_ip'] = local_ip
    except Exception as e:
        print(f"   网络配置检查失败: {e}")
    
    # 3. 检查网络连通性
    print("\n[3] 网络连通性测试:")
    
    # Ping网关
    if 'gateway' in results:
        try:
            if platform.system() == "Windows":
                result = subprocess.run(['ping', '-n', '2', results['gateway']], 
                                      capture_output=True, text=True)
            else:
                result = subprocess.run(['ping', '-c', '2', results['gateway']], 
                                      capture_output=True, text=True)
            
            if "TTL=" in result.stdout or "ttl=" in result.stdout:
                print(f"   ✓ 网关 {results['gateway']} 可达")
                results['gateway_reachable'] = True
            else:
                print(f"   ✗ 网关 {results['gateway']} 不可达")
                results['gateway_reachable'] = False
        except Exception as e:
            print(f"   Ping测试失败: {e}")
    
    # 4. 检查ARP表
    print("\n[4] ARP表检查:")
    try:
        if platform.system() == "Windows":
            result = subprocess.run(['arp', '-a'], capture_output=True, text=True)
            arp_entries = re.findall(r'(\d+\.\d+\.\d+\.\d+)\s+([a-fA-F0-9-]+)', result.stdout)
            
            print(f"   ARP表条目数: {len(arp_entries)}")
            if len(arp_entries) > 0:
                print("   前5个ARP条目:")
                for ip, mac in arp_entries[:5]:
                    print(f"     {ip} -> {mac}")
            
            results['arp_entries'] = len(arp_entries)
        
    except Exception as e:
        print(f"   ARP表检查失败: {e}")
    
    return results

def test_arp_spoofing_feasibility(results):
    """测试ARP欺骗可行性"""
    print("\n" + "=" * 60)
    print("          ARP欺骗可行性评估")
    print("=" * 60)
    
    feasibility_score = 0
    max_score = 10
    
    print("\n评估标准:")
    
    # 1. 网关可达性
    if results.get('gateway_reachable', False):
        print("   ✓ 网关可达 (+2分)")
        feasibility_score += 2
    else:
        print("   ✗ 网关不可达 (-2分)")
        feasibility_score -= 2
    
    # 2. ARP表条目数量
    arp_entries = results.get('arp_entries', 0)
    if arp_entries > 5:
        print(f"   ✓ ARP表丰富 ({arp_entries}个条目) (+3分)")
        feasibility_score += 3
    elif arp_entries > 0:
        print(f"   ⚠ ARP表有限 ({arp_entries}个条目) (+1分)")
        feasibility_score += 1
    else:
        print("   ✗ ARP表为空 (-3分)")
        feasibility_score -= 3
    
    # 3. 网络环境判断
    local_ip = results.get('local_ip', '')
    if local_ip.startswith('10.') or local_ip.startswith('192.168.'):
        print("   ✓ 私有IP地址 (+2分)")
        feasibility_score += 2
    else:
        print("   ⚠ 公网IP地址 (可能受限制) (+0分)")
    
    # 4. 操作系统权限
    if platform.system() == "Windows":
        try:
            # 尝试创建socket（需要管理员权限）
            s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_IP)
            s.close()
            print("   ✓ 可能有管理员权限 (+3分)")
            feasibility_score += 3
        except:
            print("   ✗ 权限不足 (-2分)")
            feasibility_score -= 2
    
    # 评估结果
    print(f"\n可行性评分: {feasibility_score}/{max_score}")
    
    if feasibility_score >= 7:
        print("   🟢 高可行性 - ARP欺骗可能成功")
        print("   建议: 在获得授权的情况下进行测试")
    elif feasibility_score >= 4:
        print("   🟡 中等可行性 - 可能遇到障碍")
        print("   建议: 需要进一步测试验证")
    else:
        print("   🔴 低可行性 - 很可能失败")
        print("   建议: 使用虚拟机环境学习")
    
    return feasibility_score

def simple_arp_discovery():
    """简单的ARP发现测试"""
    print("\n" + "=" * 60)
    print("          简单ARP发现测试")
    print("=" * 60)
    
    try:
        # 获取本机IP和子网
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        
        # 计算子网范围
        ip_parts = local_ip.split('.')
        subnet = f"{ip_parts[0]}.{ip_parts[1]}.{ip_parts[2]}.0/24"
        
        print(f"   扫描子网: {subnet}")
        print("   开始ARP发现... (可能需要几分钟)")
        
        # 创建ARP请求包
        arp_request = ARP(pdst=subnet)
        broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
        arp_request_broadcast = broadcast/arp_request
        
        # 发送ARP请求
        answered_list = srp(arp_request_broadcast, timeout=2, verbose=False)[0]
        
        print(f"   发现 {len(answered_list)} 个活跃设备:")
        
        devices_found = []
        for element in answered_list:
            device = {
                'ip': element[1].psrc,
                'mac': element[1].hwsrc
            }
            devices_found.append(device)
            print(f"     IP: {device['ip']} - MAC: {device['mac']}")
        
        return devices_found
        
    except Exception as e:
        print(f"   ARP发现失败: {e}")
        print("   可能原因: 权限不足、网络隔离、防火墙阻挡")
        return []

def main():
    """主函数"""
    print("⚠️  重要提醒: 此工具仅用于教育和授权的安全测试")
    print("⚠️  禁止在未经授权的情况下使用")
    
    confirm = input("\n确认继续测试? (y/N): ").strip().lower()
    if confirm != 'y':
        print("测试取消")
        return
    
    # 检查网络环境
    results = check_network_environment()
    
    # 评估ARP欺骗可行性
    feasibility_score = test_arp_spoofing_feasibility(results)
    
    # 如果可行性较高，进行ARP发现测试
    if feasibility_score >= 4:
        confirm = input("\n是否进行ARP发现测试? (y/N): ").strip().lower()
        if confirm == 'y':
            devices = simple_arp_discovery()
            
            if len(devices) > 0:
                print(f"\n🎯 发现 {len(devices)} 个设备，ARP欺骗可能有效")
            else:
                print("\n❌ 未发现任何设备，ARP欺骗很可能无效")
                print("   可能原因: 客户端隔离、网络限制、权限不足")
    
    print("\n" + "=" * 60)
    print("          测试完成")
    print("=" * 60)

if __name__ == "__main__":
    main()