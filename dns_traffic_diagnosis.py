#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DNS流量诊断工具 - 分析ARP欺骗成功但DNS劫持失败的原因
"""

import time
import socket
import subprocess
from scapy.all import *
from scapy.layers.dns import DNS, DNSQR
from scapy.layers.inet import IP, UDP

def check_dns_configuration(target_ip):
    """检查目标设备的DNS配置"""
    print("🔍 目标设备DNS配置分析")
    print("-" * 50)
    
    # 方法1: 通过nslookup检查DNS服务器
    print("1. 检查DNS服务器配置:")
    try:
        # 在本地执行nslookup，观察目标设备的DNS查询
        result = subprocess.run(['nslookup', 'www.google.com'], 
                              capture_output=True, text=True)
        
        for line in result.stdout.split('\n'):
            if 'Server' in line or 'Address' in line:
                print(f"   {line.strip()}")
    except:
        pass
    
    # 方法2: 检查常见DNS端口
    print("\n2. 检查DNS端口使用:")
    dns_ports = [53, 853, 443]  # 标准DNS, DoT, DoH
    
    for port in dns_ports:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(1)
            
            # 发送测试DNS查询
            test_query = b'\x00\x00\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x03www\x06google\x03com\x00\x00\x01\x00\x01'
            sock.sendto(test_query, (target_ip, port))
            
            try:
                data, addr = sock.recvfrom(1024)
                print(f"   ✅ 端口 {port}: 检测到DNS活动")
            except socket.timeout:
                print(f"   ❌ 端口 {port}: 无响应")
            
            sock.close()
            
        except Exception as e:
            print(f"   ❌ 端口 {port}: 测试失败")

def monitor_all_dns_traffic(target_ip, duration=60):
    """监控所有DNS相关流量"""
    print(f"\n🔍 全面DNS流量监控 ({duration}秒)")
    print("-" * 50)
    
    dns_queries = []
    start_time = time.time()
    
    def packet_handler(pkt):
        current_time = time.time() - start_time
        
        # 检查DNS over UDP (标准DNS)
        if pkt.haslayer(DNS) and pkt.haslayer(UDP):
            dns = pkt[DNS]
            udp = pkt[UDP]
            ip = pkt[IP]
            
            if dns.qr == 0:  # DNS查询
                query_name = dns.qd.qname.decode('utf-8').rstrip('.')
                
                if ip.src == target_ip:
                    dns_queries.append({
                        'time': current_time,
                        'type': 'UDP',
                        'port': udp.dport,
                        'query': query_name,
                        'src': ip.src,
                        'dst': ip.dst
                    })
                    
                    print(f"   [{current_time:.1f}s] UDP DNS查询: {query_name} -> {ip.dst}:{udp.dport}")
        
        # 检查DNS over TCP (可能用于大型查询或DoT)
        elif pkt.haslayer(TCP) and pkt.haslayer(Raw):
            tcp = pkt[TCP]
            ip = pkt[IP]
            
            # 检查常见DNS over TLS端口
            if tcp.dport in [853, 443] and ip.src == target_ip:
                print(f"   [{current_time:.1f}s] 可能DoT/DoH: {ip.src} -> {ip.dst}:{tcp.dport}")
    
    print("   开始监听所有网络流量...")
    print("   💡 请在目标设备上访问多个网站")
    print("   💡 包括: http网站、https网站、视频网站等")
    
    try:
        # 监听所有流量，不限制端口
        sniff(
            filter=f"host {target_ip}",
            prn=packet_handler,
            store=0,
            timeout=duration
        )
        
        # 分析结果
        print(f"\n📊 监控结果分析:")
        print(f"   总时长: {duration}秒")
        print(f"   检测到DNS查询: {len(dns_queries)} 个")
        
        if dns_queries:
            # 按类型统计
            udp_queries = [q for q in dns_queries if q['type'] == 'UDP']
            tcp_queries = [q for q in dns_queries if q['type'] == 'TCP']
            
            print(f"   UDP DNS查询: {len(udp_queries)} 个")
            print(f"   TCP DNS查询: {len(tcp_queries)} 个")
            
            # 显示查询详情
            print("\n   📋 查询详情:")
            for query in dns_queries[:10]:  # 显示前10个
                print(f"      {query['time']:.1f}s: {query['query']} ({query['type']}:{query['port']})")
        else:
            print("\n   ❌ 未检测到任何DNS查询")
            print("   💡 可能原因:")
            print("      • 目标设备使用加密DNS (DoH/DoT)")
            print("      • DNS查询被缓存，无新查询")
            print("      • 网络设备过滤DNS流量")
            print("      • 目标设备未进行网络访问")
    
    except Exception as e:
        print(f"   ❌ 流量监控失败: {e}")

def test_dns_hijack_effectiveness(target_ip, gateway_ip):
    """测试DNS劫持程序的有效性"""
    print("\n🔍 DNS劫持程序有效性测试")
    print("-" * 50)
    
    # 测试1: 检查过滤器设置
    print("1. 检查DNS劫持过滤器:")
    filter_str = f"udp port 53 and host {target_ip}"
    print(f"   当前过滤器: {filter_str}")
    
    # 测试2: 模拟DNS查询
    print("\n2. 模拟DNS查询测试:")
    
    def send_test_dns_query():
        """发送测试DNS查询"""
        try:
            # 创建DNS查询包
            dns_query = IP(dst="8.8.8.8")/UDP(dport=53)/DNS(
                rd=1,  # 递归查询
                qd=DNSQR(qname="www.test.com")
            )
            
            send(dns_query, verbose=False)
            print("   ✅ 测试DNS查询已发送")
            
        except Exception as e:
            print(f"   ❌ 发送测试查询失败: {e}")
    
    # 测试3: 检查ARP欺骗状态
    print("\n3. 检查ARP欺骗状态:")
    try:
        # 检查目标设备的ARP表
        result = subprocess.run(['arp', '-a', target_ip], capture_output=True, text=True)
        
        gateway_in_arp = False
        for line in result.stdout.split('\n'):
            if gateway_ip in line:
                gateway_in_arp = True
                print(f"   ✅ 网关在目标ARP表中: {line.strip()}")
                break
        
        if not gateway_in_arp:
            print("   ❌ 网关不在目标ARP表中")
            print("   💡 ARP欺骗可能未完全生效")
    
    except Exception as e:
        print(f"   ❌ ARP表检查失败: {e}")

def check_modern_dns_usage(target_ip):
    """检查现代DNS使用情况"""
    print("\n🔍 现代DNS使用情况检查")
    print("-" * 50)
    
    print("1. 检查加密DNS使用:")
    
    # 常见DoH提供商
    doh_providers = [
        "cloudflare-dns.com",
        "dns.google",
        "doh.opendns.com",
        "dns.quad9.net"
    ]
    
    print("   💡 现代浏览器/系统可能使用以下DoH服务:")
    for provider in doh_providers:
        print(f"      • {provider}")
    
    print("\n2. 检查DNS缓存:")
    print("   💡 目标设备可能有DNS缓存，需要清除:")
    print("      Windows: ipconfig /flushdns")
    print("      Linux: systemd-resolve --flush-caches")
    print("      Mac: sudo killall -HUP mDNSResponder")

def main():
    """主函数"""
    print("=" * 70)
    print("           DNS流量诊断工具")
    print("     分析ARP欺骗成功但DNS劫持失败的原因")
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
    
    # 执行诊断
    check_dns_configuration(target_ip)
    test_dns_hijack_effectiveness(target_ip, gateway_ip)
    check_modern_dns_usage(target_ip)
    
    # 询问是否进行流量监控
    choice = input("\n🔍 是否进行详细DNS流量监控? (y/N): ").strip().lower()
    if choice == 'y':
        duration = input("请输入监控时长(秒，默认60): ").strip() or "60"
        try:
            monitor_all_dns_traffic(target_ip, int(duration))
        except:
            monitor_all_dns_traffic(target_ip, 60)
    
    print("\n" + "=" * 70)
    print("            诊断完成")
    print("=" * 70)
    
    print("\n💡 根据诊断结果，建议:")
    print("1. 如果检测到DNS查询: 检查DNS劫持程序代码")
    print("2. 如果未检测到DNS查询: 目标可能使用加密DNS")
    print("3. 如果ARP欺骗不完全: 需要增强ARP欺骗")
    print("4. 考虑使用替代DNS攻击方案")

if __name__ == "__main__":
    main()