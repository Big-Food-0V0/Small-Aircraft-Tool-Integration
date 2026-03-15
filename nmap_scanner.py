#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高级网络扫描工具 - 自定义配置版本
支持自定义配置和Y/N确认执行
"""

import os
import sys
import time
import socket
import subprocess
import threading
import ipaddress
from datetime import datetime
from typing import List, Dict, Tuple, Optional

class NmapScanner:
    """高级网络扫描工具"""
    
    def __init__(self):
        self.scan_results = {}
        self.scan_options = {
            'target': '',
            'scan_type': 'quick',
            'ports': '1-1000',
            'threads': 10,
            'timeout': 3
        }
        
        # 常用端口列表
        self.common_ports = {
            'web': [80, 443, 8080, 8443],
            'ssh': [22],
            'ftp': [21],
            'telnet': [23],
            'smtp': [25, 587],
            'dns': [53],
            'http_proxy': [3128, 8080],
            'rdp': [3389],
            'mysql': [3306],
            'postgresql': [5432],
            'mongodb': [27017],
            'redis': [6379]
        }
        
        # 服务识别
        self.service_map = {
            21: 'FTP',
            22: 'SSH',
            23: 'Telnet',
            25: 'SMTP',
            53: 'DNS',
            80: 'HTTP',
            110: 'POP3',
            143: 'IMAP',
            443: 'HTTPS',
            993: 'IMAPS',
            995: 'POP3S',
            1433: 'MSSQL',
            1521: 'Oracle',
            3306: 'MySQL',
            3389: 'RDP',
            5432: 'PostgreSQL',
            5900: 'VNC',
            6379: 'Redis',
            27017: 'MongoDB'
        }
        
        # 统计信息
        self.stats = {
            'hosts_scanned': 0,
            'ports_found': 0,
            'services_identified': 0,
            'start_time': None
        }
    
    def get_configuration(self):
        """获取用户自定义配置"""
        print("=" * 60)
        print("          网络扫描工具 - 自定义配置")
        print("=" * 60)
        
        # 目标配置
        while True:
            target = input("请输入扫描目标 (IP/域名/网段) (例如: 192.168.1.1): ").strip()
            if target:
                self.scan_options['target'] = target
                break
            else:
                print("❌ 目标不能为空")
        
        # 扫描类型配置
        while True:
            scan_type = input("请输入扫描类型 (快速/全面/服务识别/操作系统识别) (默认快速): ").strip()
            if scan_type in ['快速', '全面', '服务识别', '操作系统识别']:
                self.scan_options['scan_type'] = scan_type
                break
            elif not scan_type:
                self.scan_options['scan_type'] = '快速'
                break
            else:
                print("❌ 请输入有效的扫描类型")
        
        # 端口范围配置
        while True:
            ports = input("请输入端口范围 (例如: 1-1000, 默认1-1000): ").strip()
            if ports:
                self.scan_options['ports'] = ports
                break
            elif not ports:
                self.scan_options['ports'] = '1-1000'
                break
            else:
                print("❌ 端口范围不能为空")
        
        # 线程数配置
        while True:
            try:
                threads = int(input("请输入线程数 (默认10): ").strip() or "10")
                if 1 <= threads <= 100:
                    self.scan_options['threads'] = threads
                    break
                else:
                    print("❌ 线程数必须在1-100之间")
            except ValueError:
                print("❌ 请输入有效的数字")
        
        # 超时时间配置
        while True:
            try:
                timeout = int(input("请输入超时时间(秒) (默认3): ").strip() or "3")
                if timeout > 0:
                    self.scan_options['timeout'] = timeout
                    break
                else:
                    print("❌ 超时时间必须大于0")
            except ValueError:
                print("❌ 请输入有效的数字")
        
        return self.show_configuration()
    
    def show_configuration(self):
        """显示配置信息并请求确认"""
        print("\n" + "=" * 60)
        print("          配置确认")
        print("=" * 60)
        print(f"扫描目标: {self.scan_options['target']}")
        print(f"扫描类型: {self.scan_options['scan_type']}")
        print(f"端口范围: {self.scan_options['ports']}")
        print(f"线程数: {self.scan_options['threads']}")
        print(f"超时时间: {self.scan_options['timeout']}秒")
        print("=" * 60)
        
        # 请求用户确认
        while True:
            confirm = input("\n确认执行网络扫描? (Y/N): ").strip().upper()
            if confirm == 'Y':
                return True
            elif confirm == 'N':
                print("❌ 扫描已取消")
                return False
            else:
                print("❌ 请输入 Y 或 N")
    
    def start_scan(self):
        """开始网络扫描"""
        print("=" * 60)
        print("          网络扫描开始")
        print("=" * 60)
        print(f"扫描目标: {self.scan_options['target']}")
        print(f"扫描类型: {self.scan_options['scan_type']}")
        print(f"端口范围: {self.scan_options['ports']}")
        print(f"线程数: {self.scan_options['threads']}")
        print(f"超时时间: {self.scan_options['timeout']}秒")
        print("=" * 60)
        
        self.stats['start_time'] = time.time()
        self.stats['hosts_scanned'] = 0
        self.stats['ports_found'] = 0
        self.stats['services_identified'] = 0
        
        try:
            # 根据扫描类型执行不同的扫描
            if self.scan_options['scan_type'] == '快速':
                self.quick_scan()
            elif self.scan_options['scan_type'] == '全面':
                self.comprehensive_scan()
            elif self.scan_options['scan_type'] == '服务识别':
                self.service_scan()
            elif self.scan_options['scan_type'] == '操作系统识别':
                self.os_scan()
            
        except KeyboardInterrupt:
            print("\n[!] 用户中断扫描")
        except Exception as e:
            print(f"[-] 扫描错误: {e}")
        finally:
            self.show_results()
    
    def quick_scan(self):
        """快速扫描"""
        print("[+] 开始快速扫描...")
        
        # 解析目标
        target = self.scan_options['target']
        
        # 检查目标类型
        if '/' in target:  # 网段扫描
            self.scan_network(target)
        else:  # 单个目标扫描
            self.scan_single_host(target)
    
    def scan_single_host(self, host):
        """扫描单个主机"""
        print(f"[+] 扫描主机: {host}")
        
        # 端口扫描
        ports = self.parse_port_range(self.scan_options['ports'])
        
        for port in ports:
            if self.check_port(host, port):
                service = self.identify_service(host, port)
                print(f"    [+] 端口 {port}/tcp 开放 - {service}")
                
                self.stats['ports_found'] += 1
                if service != '未知':
                    self.stats['services_identified'] += 1
        
        self.stats['hosts_scanned'] += 1
    
    def scan_network(self, network):
        """扫描整个网段"""
        print(f"[+] 扫描网段: {network}")
        
        try:
            # 生成IP地址列表
            network_obj = ipaddress.ip_network(network, strict=False)
            hosts = list(network_obj.hosts())
            
            print(f"[+] 发现 {len(hosts)} 个主机")
            
            for host in hosts:
                host_str = str(host)
                
                # 检查主机是否在线
                if self.ping_host(host_str):
                    print(f"[+] 主机在线: {host_str}")
                    self.scan_single_host(host_str)
                else:
                    print(f"[-] 主机离线: {host_str}")
                
        except Exception as e:
            print(f"[-] 网段扫描错误: {e}")
    
    def check_port(self, host, port):
        """检查端口是否开放"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.scan_options['timeout'])
            result = sock.connect_ex((host, port))
            sock.close()
            return result == 0
        except:
            return False
    
    def ping_host(self, host):
        """Ping主机检查是否在线"""
        try:
            # Windows系统使用ping命令
            if os.name == 'nt':
                response = subprocess.run(['ping', '-n', '1', '-w', '1000', host], 
                                        capture_output=True, text=True)
                return response.returncode == 0
            else:  # Linux/Unix系统
                response = subprocess.run(['ping', '-c', '1', '-W', '1', host], 
                                        capture_output=True, text=True)
                return response.returncode == 0
        except:
            return False
    
    def identify_service(self, host, port):
        """识别服务"""
        try:
            # 尝试连接并获取banner
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            sock.connect((host, port))
            
            # 发送探测数据
            if port == 80 or port == 443:
                sock.send(b"HEAD / HTTP/1.0\r\n\r\n")
            elif port == 21:
                sock.send(b"\r\n")
            elif port == 22:
                sock.send(b"SSH-2.0-OpenSSH_7.4\r\n")
            
            # 接收响应
            banner = sock.recv(1024).decode('utf-8', errors='ignore')
            sock.close()
            
            # 分析banner
            if 'HTTP' in banner:
                return 'HTTP服务'
            elif 'SSH' in banner:
                return 'SSH服务'
            elif 'FTP' in banner:
                return 'FTP服务'
            
        except:
            pass
        
        # 使用端口映射表
        return self.service_map.get(port, '未知')
    
    def parse_port_range(self, port_range):
        """解析端口范围"""
        ports = []
        
        try:
            if '-' in port_range:
                start, end = map(int, port_range.split('-'))
                ports = list(range(start, end + 1))
            elif ',' in port_range:
                ports = list(map(int, port_range.split(',')))
            else:
                ports = [int(port_range)]
        except:
            # 使用默认端口
            ports = list(range(1, 1001))
        
        return ports
    
    def comprehensive_scan(self):
        """全面扫描"""
        print("[+] 开始全面扫描...")
        # 这里可以添加更全面的扫描逻辑
        self.quick_scan()
    
    def service_scan(self):
        """服务识别扫描"""
        print("[+] 开始服务识别扫描...")
        # 这里可以添加服务识别逻辑
        self.quick_scan()
    
    def os_scan(self):
        """操作系统识别扫描"""
        print("[+] 开始操作系统识别扫描...")
        # 这里可以添加操作系统识别逻辑
        self.quick_scan()
    
    def show_results(self):
        """显示扫描结果"""
        elapsed = time.time() - self.stats['start_time']
        
        print("\n" + "=" * 60)
        print("          扫描结果")
        print("=" * 60)
        print(f"扫描主机数: {self.stats['hosts_scanned']}")
        print(f"发现端口数: {self.stats['ports_found']}")
        print(f"识别服务数: {self.stats['services_identified']}")
        print(f"扫描用时: {int(elapsed)}秒")
        print("=" * 60)

def main():
    """主函数"""
    try:
        scanner = NmapScanner()
        
        # 获取配置并确认
        if scanner.get_configuration():
            scanner.start_scan()
        
    except KeyboardInterrupt:
        print("\n[!] 程序被用户中断")
    except Exception as e:
        print(f"[-] 程序错误: {e}")

if __name__ == "__main__":
    main()