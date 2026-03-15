#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网络连通性测试工具 - 自定义配置版本
支持自定义配置和Y/N确认执行
"""

import os
import socket
import subprocess
import re
import threading
import time

class NetworkTest:
    def __init__(self):
        self.test_running = False
        
        # 配置参数
        self.config = {
            'target_ip': '',
            'test_type': 'basic',
            'ports': '80,443,22,53,3389',
            'ping_count': 3,
            'timeout': 2,
            'threads': 5
        }
        
        # 统计信息
        self.stats = {
            'hosts_tested': 0,
            'ports_found': 0,
            'start_time': None
        }
    
    def get_configuration(self):
        """获取用户自定义配置"""
        print("=" * 60)
        print("          网络测试工具 - 自定义配置")
        print("=" * 60)
        
        # 目标IP配置
        while True:
            target_ip = input("请输入目标IP地址 (例如: 10.30.58.185): ").strip()
            if self.validate_ip(target_ip):
                self.config['target_ip'] = target_ip
                break
            else:
                print("❌ IP地址格式不正确，请重新输入")
        
        # 测试类型配置
        while True:
            test_type = input("请输入测试类型 (basic/advanced/comprehensive) (默认basic): ").strip().lower()
            if test_type in ['basic', 'advanced', 'comprehensive']:
                self.config['test_type'] = test_type
                break
            elif not test_type:
                self.config['test_type'] = 'basic'
                break
            else:
                print("❌ 请输入 basic, advanced 或 comprehensive")
        
        # 端口列表配置
        while True:
            ports = input("请输入端口列表 (用逗号分隔，例如: 80,443,22) (默认80,443,22,53,3389): ").strip()
            if ports:
                self.config['ports'] = ports
                break
            elif not ports:
                self.config['ports'] = '80,443,22,53,3389'
                break
            else:
                print("❌ 端口列表不能为空")
        
        # Ping次数配置
        while True:
            try:
                ping_count = int(input("请输入Ping次数 (默认3): ").strip() or "3")
                if ping_count > 0:
                    self.config['ping_count'] = ping_count
                    break
                else:
                    print("❌ Ping次数必须大于0")
            except ValueError:
                print("❌ 请输入有效的数字")
        
        # 超时时间配置
        while True:
            try:
                timeout = int(input("请输入超时时间(秒) (默认2): ").strip() or "2")
                if timeout > 0:
                    self.config['timeout'] = timeout
                    break
                else:
                    print("❌ 超时时间必须大于0")
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
        print(f"测试类型: {self.config['test_type']}")
        print(f"端口列表: {self.config['ports']}")
        print(f"Ping次数: {self.config['ping_count']}")
        print(f"超时时间: {self.config['timeout']}秒")
        print(f"线程数: {self.config['threads']}")
        print("=" * 60)
        
        # 请求用户确认
        while True:
            confirm = input("\n确认执行网络测试? (Y/N): ").strip().upper()
            if confirm == 'Y':
                return True
            elif confirm == 'N':
                print("❌ 测试已取消")
                return False
            else:
                print("❌ 请输入 Y 或 N")
    
    def start_test(self):
        """开始网络测试"""
        print("=" * 60)
        print("          网络测试开始")
        print("=" * 60)
        print(f"目标IP: {self.config['target_ip']}")
        print(f"测试类型: {self.config['test_type']}")
        print(f"端口列表: {self.config['ports']}")
        print(f"Ping次数: {self.config['ping_count']}")
        print(f"超时时间: {self.config['timeout']}秒")
        print(f"线程数: {self.config['threads']}")
        print("=" * 60)
        
        self.test_running = True
        self.stats['start_time'] = time.time()
        self.stats['hosts_tested'] = 0
        self.stats['ports_found'] = 0
        
        # 解析端口列表
        ports_list = [int(port.strip()) for port in self.config['ports'].split(',')]
        
        try:
            # 根据测试类型执行不同的测试
            if self.config['test_type'] == 'basic':
                self.basic_test(ports_list)
            elif self.config['test_type'] == 'advanced':
                self.advanced_test(ports_list)
            elif self.config['test_type'] == 'comprehensive':
                self.comprehensive_test(ports_list)
            
        except KeyboardInterrupt:
            print("\n[!] 用户中断测试")
        except Exception as e:
            print(f"[-] 测试错误: {e}")
        finally:
            self.stop_test()
    
    def basic_test(self, ports_list):
        """基础网络测试"""
        print("\n[+] 开始基础网络测试...")
        
        # 1. Ping测试
        print("\n1. Ping测试:")
        try:
            if os.name == 'nt':  # Windows
                result = subprocess.run(['ping', '-n', str(self.config['ping_count']), self.config['target_ip']], 
                                      capture_output=True, text=True)
            else:  # Linux/Mac
                result = subprocess.run(['ping', '-c', str(self.config['ping_count']), self.config['target_ip']], 
                                      capture_output=True, text=True)
            
            if result.returncode == 0:
                print("   ✅ 目标设备可达")
                # 提取响应时间
                for line in result.stdout.split('\n'):
                    if '时间=' in line or 'time=' in line:
                        print(f"   📊 {line.strip()}")
            else:
                print("   ❌ 目标设备不可达")
                
        except Exception as e:
            print(f"   ❌ Ping测试失败: {e}")
        
        # 2. 端口扫描
        print("\n2. 端口扫描:")
        open_ports = []
        
        def scan_port(port):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(self.config['timeout'])
                result = sock.connect_ex((self.config['target_ip'], port))
                sock.close()
                
                if result == 0:
                    open_ports.append(port)
                    try:
                        service = socket.getservbyport(port)
                        print(f"   ✅ 端口 {port} 开放 ({service})")
                    except:
                        print(f"   ✅ 端口 {port} 开放 (未知服务)")
                else:
                    print(f"   ❌ 端口 {port} 关闭")
                    
            except Exception as e:
                print(f"   ❌ 端口 {port} 扫描失败: {e}")
        
        # 多线程端口扫描
        threads = []
        for port in ports_list:
            if not self.test_running:
                break
            
            t = threading.Thread(target=scan_port, args=(port,))
            threads.append(t)
            t.start()
            
            # 控制线程数量
            if len(threads) >= self.config['threads']:
                for t in threads:
                    t.join()
                threads = []
        
        # 等待剩余线程
        for t in threads:
            t.join()
        
        self.stats['ports_found'] += len(open_ports)
        self.stats['hosts_tested'] += 1
    
    def advanced_test(self, ports_list):
        """高级网络测试"""
        print("\n[+] 开始高级网络测试...")
        
        # 执行基础测试
        self.basic_test(ports_list)
        
        # 3. 路由追踪
        print("\n3. 路由追踪:")
        try:
            if os.name == 'nt':  # Windows
                result = subprocess.run(['tracert', '-d', self.config['target_ip']], 
                                      capture_output=True, text=True)
            else:  # Linux/Mac
                result = subprocess.run(['traceroute', '-n', self.config['target_ip']], 
                                      capture_output=True, text=True)
            
            print("   📊 路由追踪结果:")
            for line in result.stdout.split('\n')[:10]:  # 只显示前10行
                if line.strip():
                    print(f"      {line.strip()}")
                    
        except Exception as e:
            print(f"   ❌ 路由追踪失败: {e}")
        
        # 4. DNS解析测试
        print("\n4. DNS解析测试:")
        try:
            hostname = socket.gethostbyaddr(self.config['target_ip'])
            print(f"   ✅ 反向DNS解析: {hostname[0]}")
        except:
            print("   ❌ 反向DNS解析失败")
    
    def comprehensive_test(self, ports_list):
        """全面网络测试"""
        print("\n[+] 开始全面网络测试...")
        
        # 执行高级测试
        self.advanced_test(ports_list)
        
        # 5. 扩展端口扫描
        print("\n5. 扩展端口扫描 (1-1000):")
        extended_ports = list(range(1, 1001))
        
        def scan_extended_port(port):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex((self.config['target_ip'], port))
                sock.close()
                
                if result == 0:
                    try:
                        service = socket.getservbyport(port)
                        print(f"   ✅ 端口 {port} 开放 ({service})")
                    except:
                        print(f"   ✅ 端口 {port} 开放 (未知服务)")
                    
            except:
                pass
        
        # 多线程扩展端口扫描
        threads = []
        for port in extended_ports:
            if not self.test_running:
                break
            
            t = threading.Thread(target=scan_extended_port, args=(port,))
            threads.append(t)
            t.start()
            
            # 控制线程数量
            if len(threads) >= self.config['threads']:
                for t in threads:
                    t.join()
                threads = []
        
        # 等待剩余线程
        for t in threads:
            t.join()
        
        # 6. 网络服务检测
        print("\n6. 网络服务检测:")
        self.detect_services()
    
    def detect_services(self):
        """检测网络服务"""
        services = {
            80: "HTTP服务",
            443: "HTTPS服务", 
            22: "SSH服务",
            21: "FTP服务",
            25: "SMTP服务",
            53: "DNS服务",
            3389: "RDP服务"
        }
        
        for port, service_name in services.items():
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                result = sock.connect_ex((self.config['target_ip'], port))
                sock.close()
                
                if result == 0:
                    print(f"   ✅ {service_name} 运行中 (端口 {port})")
                else:
                    print(f"   ❌ {service_name} 未运行 (端口 {port})")
                    
            except Exception as e:
                print(f"   ❌ {service_name} 检测失败: {e}")
    
    def stop_test(self):
        """停止测试"""
        if self.test_running:
            print("\n[+] 停止网络测试...")
            self.test_running = False
            
            # 显示统计信息
            elapsed = time.time() - self.stats['start_time']
            print(f"\n[+] 测试统计:")
            print(f"    - 总运行时间: {int(elapsed)}秒")
            print(f"    - 测试主机数: {self.stats['hosts_tested']}")
            print(f"    - 发现端口数: {self.stats['ports_found']}")

def main():
    """主函数"""
    try:
        test = NetworkTest()
        
        # 获取配置并确认
        if test.get_configuration():
            test.start_test()
        
    except KeyboardInterrupt:
        print("\n[!] 程序被用户中断")
    except Exception as e:
        print(f"[-] 程序错误: {e}")

if __name__ == "__main__":
    main()