#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
免费代理获取工具
从多个免费代理API获取可用的代理列表
"""

import requests
import time
import threading
from concurrent.futures import ThreadPoolExecutor

class FreeProxyFetcher:
    """免费代理获取器"""
    
    def __init__(self):
        self.working_proxies = []
        self.test_url = "http://httpbin.org/ip"  # 测试代理的URL
        
    def get_proxies_from_apis(self):
        """从多个免费代理API获取代理"""
        proxy_sources = [
            # 这些是常见的免费代理API
            "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all",
            "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
            "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt",
            "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/proxy.txt",
        ]
        
        all_proxies = []
        
        for url in proxy_sources:
            try:
                print(f"📡 正在从 {url} 获取代理...")
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    # 解析代理列表
                    proxies = response.text.strip().split('\n')
                    # 过滤空行和注释
                    proxies = [p.strip() for p in proxies if p.strip() and not p.startswith('#')]
                    
                    # 标准化格式
                    formatted_proxies = []
                    for proxy in proxies:
                        if ':' in proxy:
                            ip, port = proxy.split(':', 1)
                            formatted_proxies.append(f"http://{ip}:{port}")
                    
                    all_proxies.extend(formatted_proxies)
                    print(f"✅ 从 {url} 获取到 {len(formatted_proxies)} 个代理")
                else:
                    print(f"❌ 无法从 {url} 获取代理")
                    
            except Exception as e:
                print(f"❌ 获取 {url} 时出错: {e}")
        
        # 去重
        all_proxies = list(set(all_proxies))
        return all_proxies
    
    def test_proxy(self, proxy):
        """测试单个代理的可用性"""
        try:
            proxies = {
                'http': proxy,
                'https': proxy
            }
            
            # 设置较短的超时时间
            response = requests.get(self.test_url, proxies=proxies, timeout=5)
            
            if response.status_code == 200:
                print(f"✅ 代理可用: {proxy}")
                return proxy
            
        except Exception as e:
            # 代理不可用，静默失败
            pass
        
        return None
    
    def test_proxies(self, proxies, max_workers=20):
        """多线程测试代理可用性"""
        print(f"🧪 开始测试 {len(proxies)} 个代理的可用性...")
        
        working_proxies = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            results = executor.map(self.test_proxy, proxies)
            
            for result in results:
                if result:
                    working_proxies.append(result)
        
        print(f"🎯 测试完成！找到 {len(working_proxies)} 个可用代理")
        return working_proxies
    
    def save_proxies_to_file(self, proxies, filename="files/proxies/proxies.txt"):
        """将代理保存到文件"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("# 免费代理列表 - 自动获取\n")
                f.write("# 更新时间: " + time.strftime("%Y-%m-%d %H:%M:%S") + "\n\n")
                
                for proxy in proxies:
                    f.write(proxy + "\n")
            
            print(f"💾 已将 {len(proxies)} 个代理保存到 {filename}")
            return True
            
        except Exception as e:
            print(f"❌ 保存代理文件失败: {e}")
            return False
    
    def get_static_proxies(self):
        """获取一些已知的免费代理（备用方案）"""
        # 这些是一些相对稳定的免费代理（可能会变化）
        static_proxies = [
            "http://51.158.68.68:8811",
            "http://51.158.68.133:8811", 
            "http://51.158.68.26:8811",
            "http://51.158.68.148:8811",
            "http://188.165.141.114:3128",
            "http://188.165.141.115:3128",
            "http://188.165.141.116:3128",
            "http://188.165.141.117:3128",
            "http://51.91.212.159:3128",
            "http://51.91.212.160:3128",
            "http://51.91.212.161:3128",
            "http://51.91.212.162:3128",
            "http://138.68.161.14:3128",
            "http://138.68.161.60:3128",
            "http://138.68.161.61:3128",
            "http://167.99.123.158:3128",
            "http://167.99.123.159:3128",
            "http://167.99.123.160:3128",
            "http://167.99.123.161:3128",
            "http://51.89.166.149:3128"
        ]
        
        return static_proxies

def main():
    """主函数"""
    print("=" * 60)
    print("🔄 免费代理获取工具")
    print("=" * 60)
    
    fetcher = FreeProxyFetcher()
    
    # 方法1：尝试从在线API获取
    print("\n1. 尝试从在线API获取代理...")
    try:
        online_proxies = fetcher.get_proxies_from_apis()
        if online_proxies:
            print(f"✅ 从在线API获取到 {len(online_proxies)} 个代理")
            
            # 测试可用性
            working_proxies = fetcher.test_proxies(online_proxies[:50])  # 只测试前50个
            
            if working_proxies:
                fetcher.save_proxies_to_file(working_proxies)
                return
        else:
            print("❌ 无法从在线API获取代理")
    except Exception as e:
        print(f"❌ 在线获取失败: {e}")
    
    # 方法2：使用静态代理列表（备用方案）
    print("\n2. 使用备用静态代理列表...")
    static_proxies = fetcher.get_static_proxies()
    print(f"📋 获取到 {len(static_proxies)} 个静态代理")
    
    # 测试静态代理
    working_proxies = fetcher.test_proxies(static_proxies)
    
    if working_proxies:
        fetcher.save_proxies_to_file(working_proxies)
        print("\n🎉 代理获取完成！")
    else:
        print("\n⚠️ 警告：未找到可用代理，将创建示例文件")
        # 创建示例文件
        example_proxies = [
            "# 示例代理文件 - 需要替换为真实代理",
            "# 格式: http://IP:端口 或 socks5://IP:端口",
            "",
            "# 可以从以下网站获取免费代理:",
            "# - https://www.proxy-list.download/", 
            "# - https://free-proxy-list.net/",
            "# - https://spys.one/",
            "",
            "# 示例（需要替换）:",
            "http://127.0.0.1:8080",
            "socks5://127.0.0.1:1080"
        ]
        
        with open("files/proxies/proxies.txt", 'w', encoding='utf-8') as f:
            f.write('\n'.join(example_proxies))
        print("📝 已创建示例代理文件")

if __name__ == "__main__":
    main()