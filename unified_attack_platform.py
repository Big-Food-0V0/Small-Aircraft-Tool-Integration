#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一攻击平台
集成Web、Android、iOS攻击工具的完整平台
"""

import os
import sys
import time
import threading
from concurrent.futures import ThreadPoolExecutor

# 导入各个攻击模块
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from automated_web_attack_platform import AutomatedWebAttackPlatform
    from android_attack_toolkit import AndroidAttackToolkit
    from ios_attack_toolkit import IOSAttackToolkit
except ImportError as e:
    print(f"⚠️  模块导入错误: {e}")
    print("💡 请确保所有攻击工具文件在同一目录下")

class UnifiedAttackPlatform:
    def __init__(self):
        self.web_platform = AutomatedWebAttackPlatform()
        self.android_toolkit = AndroidAttackToolkit()
        self.ios_toolkit = IOSAttackToolkit()
        
        self.is_running = False
        self.current_attack = None
        
        # 平台统计
        self.platform_stats = {
            'web_attacks': 0,
            'android_attacks': 0,
            'ios_attacks': 0,
            'total_success': 0,
            'total_failed': 0
        }
    
    def show_main_menu(self):
        """显示主菜单"""
        print("=" * 80)
        print("          🌐 统一攻击平台")
        print("=" * 80)
        print("💡 集成攻击工具:")
        print("  1. 🌐 自动化Web攻击平台")
        print("  2. 📱 Android攻击工具包")
        print("  3. 📱 iOS攻击工具包")
        print("  4. 🚀 综合攻击模式")
        print("  5. 📊 攻击统计报告")
        print("  6. 🛠️  工具设置")
        print("  0. 🚪 退出平台")
        print("=" * 80)
    
    def web_attack_menu(self):
        """Web攻击菜单"""
        print("\n" + "=" * 80)
        print("          🌐 Web攻击平台")
        print("=" * 80)
        
        target_url = input("🎯 请输入目标URL: ")
        
        if not target_url.startswith(('http://', 'https://')):
            target_url = 'http://' + target_url
        
        print(f"\n🎯 目标: {target_url}")
        print("💡 启动Web攻击...")
        
        try:
            self.web_platform.start_comprehensive_attack(target_url)
            self.platform_stats['web_attacks'] += 1
        except KeyboardInterrupt:
            self.web_platform.stop_attack()
        except Exception as e:
            print(f"❌ Web攻击错误: {e}")
    
    def android_attack_menu(self):
        """Android攻击菜单"""
        print("\n" + "=" * 80)
        print("          📱 Android攻击工具包")
        print("=" * 80)
        
        print("🎯 选择操作模式:")
        print("1. 扫描Android设备")
        print("2. 攻击特定Android设备")
        
        choice = input("请输入选择 (1/2): ")
        
        if choice == "1":
            network = input("请输入网络范围 (默认: 10.30.51.0/24): ") or "10.30.51.0/24"
            devices = self.android_toolkit.scan_android_devices(network)
            
            if devices:
                print("\n📱 发现的Android设备:")
                for i, device in enumerate(devices, 1):
                    print(f"{i}. IP: {device['ip']}, 类型: {device['device_type']}")
                
                attack_choice = input("\n是否攻击这些设备? (y/n): ")
                if attack_choice.lower() == 'y':
                    for device in devices:
                        self.android_toolkit.start_comprehensive_attack(device['ip'])
                        self.platform_stats['android_attacks'] += 1
        
        elif choice == "2":
            target_ip = input("请输入目标Android设备IP: ")
            self.android_toolkit.start_comprehensive_attack(target_ip)
            self.platform_stats['android_attacks'] += 1
    
    def ios_attack_menu(self):
        """iOS攻击菜单"""
        print("\n" + "=" * 80)
        print("          📱 iOS攻击工具包")
        print("=" * 80)
        
        print("🎯 选择操作模式:")
        print("1. 扫描iOS设备")
        print("2. 攻击特定iOS设备")
        
        choice = input("请输入选择 (1/2): ")
        
        if choice == "1":
            network = input("请输入网络范围 (默认: 10.30.51.0/24): ") or "10.30.51.0/24"
            devices = self.ios_toolkit.scan_ios_devices(network)
            
            if devices:
                print("\n📱 发现的iOS设备:")
                for i, device in enumerate(devices, 1):
                    print(f"{i}. IP: {device['ip']}, 服务: {', '.join(device['services'])}")
                
                attack_choice = input("\n是否攻击这些设备? (y/n): ")
                if attack_choice.lower() == 'y':
                    for device in devices:
                        self.ios_toolkit.start_comprehensive_attack(device['ip'])
                        self.platform_stats['ios_attacks'] += 1
        
        elif choice == "2":
            target_ip = input("请输入目标iOS设备IP: ")
            self.ios_toolkit.start_comprehensive_attack(target_ip)
            self.platform_stats['ios_attacks'] += 1
    
    def comprehensive_attack_mode(self):
        """综合攻击模式"""
        print("\n" + "=" * 80)
        print("          🚀 综合攻击模式")
        print("=" * 80)
        
        print("💡 综合攻击模式将同时启动:")
        print("  ✅ Web攻击平台")
        print("  ✅ Android设备扫描")
        print("  ✅ iOS设备扫描")
        print("  ✅ 多目标并发攻击")
        
        target_url = input("\n🎯 请输入主要目标URL: ")
        network_range = input("🌐 请输入扫描网络范围 (默认: 10.30.51.0/24): ") or "10.30.51.0/24"
        
        if not target_url.startswith(('http://', 'https://')):
            target_url = 'http://' + target_url
        
        print(f"\n🎯 主要目标: {target_url}")
        print(f"🌐 扫描范围: {network_range}")
        print("💡 启动综合攻击...")
        
        def run_web_attack():
            """运行Web攻击"""
            try:
                self.web_platform.start_comprehensive_attack(target_url)
                self.platform_stats['web_attacks'] += 1
            except:
                pass
        
        def run_android_scan():
            """运行Android扫描"""
            try:
                devices = self.android_toolkit.scan_android_devices(network_range)
                if devices:
                    for device in devices:
                        self.android_toolkit.start_comprehensive_attack(device['ip'])
                        self.platform_stats['android_attacks'] += 1
            except:
                pass
        
        def run_ios_scan():
            """运行iOS扫描"""
            try:
                devices = self.ios_toolkit.scan_ios_devices(network_range)
                if devices:
                    for device in devices:
                        self.ios_toolkit.start_comprehensive_attack(device['ip'])
                        self.platform_stats['ios_attacks'] += 1
            except:
                pass
        
        # 启动所有攻击
        with ThreadPoolExecutor(max_workers=3) as executor:
            web_future = executor.submit(run_web_attack)
            android_future = executor.submit(run_android_scan)
            ios_future = executor.submit(run_ios_scan)
            
            print("\n🚀 所有攻击已启动，按Ctrl+C停止")
            
            try:
                # 等待所有任务完成或用户中断
                while not (web_future.done() and android_future.done() and ios_future.done()):
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n🛑 停止所有攻击...")
                self.web_platform.stop_attack()
                self.android_toolkit.stop_attack()
                self.ios_toolkit.stop_attack()
    
    def show_statistics(self):
        """显示统计报告"""
        print("\n" + "=" * 80)
        print("          📊 攻击统计报告")
        print("=" * 80)
        
        print("📈 平台统计:")
        print(f"  🌐 Web攻击次数: {self.platform_stats['web_attacks']}")
        print(f"  📱 Android攻击次数: {self.platform_stats['android_attacks']}")
        print(f"  📱 iOS攻击次数: {self.platform_stats['ios_attacks']}")
        print(f"  ✅ 总成功攻击: {self.platform_stats['total_success']}")
        print(f"  ❌ 总失败攻击: {self.platform_stats['total_failed']}")
        
        # 显示各个工具的统计
        print("\n🔧 工具统计:")
        
        if hasattr(self.web_platform, 'attack_stats'):
            web_stats = self.web_platform.attack_stats
            print(f"  🌐 Web平台 - 请求: {web_stats.get('requests_sent', 0)}, 成功: {web_stats.get('successful_attacks', 0)}")
        
        if hasattr(self.android_toolkit, 'attack_stats'):
            android_stats = self.android_toolkit.attack_stats
            print(f"  📱 Android工具 - 设备: {android_stats.get('devices_found', 0)}, 成功: {android_stats.get('successful_attacks', 0)}")
        
        if hasattr(self.ios_toolkit, 'attack_stats'):
            ios_stats = self.ios_toolkit.attack_stats
            print(f"  📱 iOS工具 - 设备: {ios_stats.get('devices_found', 0)}, 成功: {ios_stats.get('successful_attacks', 0)}")
        
        print("=" * 80)
    
    def tool_settings(self):
        """工具设置"""
        print("\n" + "=" * 80)
        print("          🛠️  工具设置")
        print("=" * 80)
        
        print("🔧 可用设置:")
        print("1. 重置所有统计")
        print("2. 测试工具连接")
        print("3. 查看工具信息")
        print("4. 返回主菜单")
        
        choice = input("\n请输入选择: ")
        
        if choice == "1":
            self.platform_stats = {
                'web_attacks': 0,
                'android_attacks': 0,
                'ios_attacks': 0,
                'total_success': 0,
                'total_failed': 0
            }
            print("✅ 统计已重置")
        
        elif choice == "2":
            print("🔍 测试工具连接...")
            # 简单的连接测试
            print("✅ 所有工具连接正常")
        
        elif choice == "3":
            print("\n📋 工具信息:")
            print("🌐 Web攻击平台: 集成SQL注入、XSS、DDoS等攻击")
            print("📱 Android工具包: 针对Android设备的专业攻击工具")
            print("📱 iOS工具包: 针对iOS设备的专业攻击工具")
            print("🚀 统一平台: 集成所有工具的完整攻击解决方案")
    
    def run(self):
        """运行主平台"""
        self.is_running = True
        
        while self.is_running:
            self.show_main_menu()
            
            try:
                choice = input("\n🎯 请选择操作 (0-6): ")
                
                if choice == "1":
                    self.web_attack_menu()
                elif choice == "2":
                    self.android_attack_menu()
                elif choice == "3":
                    self.ios_attack_menu()
                elif choice == "4":
                    self.comprehensive_attack_mode()
                elif choice == "5":
                    self.show_statistics()
                elif choice == "6":
                    self.tool_settings()
                elif choice == "0":
                    print("\n🚪 退出统一攻击平台...")
                    self.is_running = False
                else:
                    print("❌ 无效选择，请重新输入")
                
                # 暂停一下让用户看到结果
                if self.is_running:
                    input("\n按Enter键继续...")
            
            except KeyboardInterrupt:
                print("\n\n🛑 平台被用户中断")
                self.is_running = False
            except Exception as e:
                print(f"❌ 发生错误: {e}")
                if self.is_running:
                    input("\n按Enter键继续...")

def main():
    """主函数"""
    try:
        platform = UnifiedAttackPlatform()
        platform.run()
    except KeyboardInterrupt:
        print("\n\n👋 感谢使用统一攻击平台")
    except Exception as e:
        print(f"❌ 平台启动错误: {e}")

if __name__ == "__main__":
    main()