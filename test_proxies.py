#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
代理可用性测试工具
测试现有代理文件的代理是否可用
"""

import requests
import concurrent.futures
import time

def test_single_proxy(proxy, test_url="http://httpbin.org/ip", timeout=5):
    """测试单个代理的可用性"""
    try:
        proxies = {
            'http': proxy,
            'https': proxy
        }
        
        start_time = time.time()
        response = requests.get(test_url, proxies=proxies, timeout=timeout)
        response_time = time.time() - start_time
        
        if response.status_code == 200:
            return {
                'proxy': proxy,
                'status': '可用',
                'response_time': round(response_time, 2),
                'ip': response.json().get('origin', '未知')
            }
    except Exception as e:
        pass
    
    return {
        'proxy': proxy,
        'status': '不可用',
        'response_time': None,
        'ip': None
    }

def load_proxies_from_file(filename="files/proxies/files/proxies/http.txt"):
    """从文件加载代理列表"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            proxies = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        return proxies
    except Exception as e:
        print(f"❌ 加载代理文件失败: {e}")
        return []

def main():
    """主函数"""
    print("=" * 60)
    print("🔍 代理可用性测试")
    print("=" * 60)
    
    # 加载代理
    proxies = load_proxies_from_file()
    print(f"📋 从文件加载到 {len(proxies)} 个代理")
    
    if not proxies:
        print("❌ 未找到代理，无法测试")
        return
    
    # 多线程测试代理
    print("🧪 开始测试代理可用性...")
    
    working_proxies = []
    failed_proxies = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        results = list(executor.map(test_single_proxy, proxies))
    
    for result in results:
        if result['status'] == '可用':
            working_proxies.append(result)
        else:
            failed_proxies.append(result['proxy'])
    
    # 显示结果
    print(f"\n📊 测试结果:")
    print(f"✅ 可用代理: {len(working_proxies)} 个")
    print(f"❌ 不可用代理: {len(failed_proxies)} 个")
    print(f"📈 可用率: {len(working_proxies)/len(proxies)*100:.1f}%")
    
    if working_proxies:
        print(f"\n🏆 最快的5个代理:")
        working_proxies.sort(key=lambda x: x['response_time'])
        for i, proxy_info in enumerate(working_proxies[:5]):
            print(f"{i+1}. {proxy_info['proxy']} - {proxy_info['response_time']}秒 - IP: {proxy_info['ip']}")
    
    # 保存可用代理
    if working_proxies:
        with open("files/proxies/working_proxies.txt", 'w', encoding='utf-8') as f:
            f.write("# 可用代理列表\n")
            f.write(f"# 测试时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"# 总代理数: {len(proxies)}, 可用数: {len(working_proxies)}\n\n")
            
            for proxy_info in working_proxies:
                f.write(f"{proxy_info['proxy']} # 响应时间: {proxy_info['response_time']}秒\n")
        
        print(f"\n💾 已将可用代理保存到: files/proxies/working_proxies.txt")
    
    # 攻击效果预测
    if working_proxies:
        print(f"\n🎯 攻击效果预测:")
        print(f"• 可用代理数: {len(working_proxies)}")
        print(f"• 建议线程数: {min(len(working_proxies) * 2, 500)}")
        print(f"• 预期攻击效果: {'高' if len(working_proxies) > 20 else '中'}")
        print(f"• 对博客网站的瘫痪概率: {min(80 + len(working_proxies), 95)}%")

if __name__ == "__main__":
    main()