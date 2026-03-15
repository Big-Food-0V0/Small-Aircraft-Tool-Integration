#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
子域名枚举工具 - 支持配置文件模式
自动发现目标域名的所有子域名
"""

import requests
import threading
import time
import socket
import json
import argparse
import sys
from concurrent.futures import ThreadPoolExecutor
import dns.resolver

class SubdomainEnumerationTool:
    def __init__(self, config_file=None):
        self.found_subdomains = []
        self.threads = 20
        self.domain = ""
        
        # 如果提供了配置文件，加载配置
        if config_file:
            self.load_config(config_file)
        
        # 常见子域名字典
        self.common_subdomains = [
            'www', 'mail', 'ftp', 'localhost', 'webmail', 'smtp', 'pop', 'ns1', 'webdisk',
            'ns2', 'cpanel', 'whm', 'autodiscover', 'autoconfig', 'ns3', 'test', 'staging',
            'dev', 'admin', 'blog', 'forum', 'shop', 'api', 'app', 'cdn', 'static', 'media',
            'support', 'help', 'docs', 'wiki', 'git', 'svn', 'backup', 'db', 'mysql', 'mongo',
            'redis', 'elasticsearch', 'jenkins', 'docker', 'kubernetes', 'vpn', 'remote',
            'portal', 'auth', 'login', 'oauth', 'sso', 'dashboard', 'monitor', 'status',
            'analytics', 'tracking', 'payment', 'billing', 'invoice', 'store', 'shop',
            'market', 'trade', 'exchange', 'wallet', 'bank', 'finance', 'insurance',
            'health', 'medical', 'patient', 'doctor', 'hospital', 'clinic', 'pharmacy',
            'school', 'university', 'college', 'student', 'teacher', 'library', 'lab',
            'research', 'science', 'tech', 'technology', 'it', 'info', 'news', 'press',
            'media', 'tv', 'radio', 'video', 'audio', 'image', 'photo', 'gallery',
            'music', 'movie', 'film', 'game', 'play', 'fun', 'entertainment', 'sport',
            'travel', 'tour', 'hotel', 'restaurant', 'food', 'drink', 'coffee', 'tea',
            'car', 'auto', 'motor', 'bike', 'cycle', 'flight', 'air', 'sea', 'land',
            'home', 'house', 'property', 'realestate', 'rent', 'buy', 'sell', 'trade',
            'job', 'career', 'work', 'office', 'business', 'company', 'corp', 'inc',
            'llc', 'ltd', 'group', 'global', 'world', 'international', 'national',
            'regional', 'local', 'city', 'state', 'country', 'asia', 'europe', 'america',
            'africa', 'australia', 'china', 'usa', 'uk', 'japan', 'korea', 'india',
            'russia', 'germany', 'france', 'italy', 'spain', 'brazil', 'mexico', 'canada'
        ]
    
    def load_config(self, config_file):
        """加载配置文件"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            self.domain = config.get('target', '')
            self.threads = config.get('threads', 20)
            
            print(f"✅ 配置加载成功: 目标={self.domain}, 线程数={self.threads}")
            
        except Exception as e:
            print(f"❌ 配置加载失败: {e}")
            sys.exit(1)
    
    def interactive_setup(self):
        """交互式设置"""
        print("🔍 子域名枚举工具")
        print("=" * 50)
        
        if not self.domain:
            self.domain = input("请输入目标域名: ").strip()
        
        if not self.domain:
            print("❌ 域名不能为空")
            sys.exit(1)
        
        threads_input = input(f"线程数 (默认 {self.threads}): ").strip()
        if threads_input:
            try:
                self.threads = int(threads_input)
            except ValueError:
                print("❌ 线程数必须是数字，使用默认值")
    
    def dns_enumeration(self):
        """DNS枚举子域名"""
        print(f"[DNS枚举] 扫描域名: {self.domain}")
        
        def check_subdomain(subdomain):
            full_domain = f"{subdomain}.{self.domain}"
            try:
                answers = dns.resolver.resolve(full_domain, 'A')
                for answer in answers:
                    ip = answer.address
                    print(f"✅ 发现: {full_domain} -> {ip}")
                    self.found_subdomains.append((full_domain, ip))
                    return True
            except:
                pass
            return False
        
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            results = executor.map(check_subdomain, self.common_subdomains)
            found_count = sum(1 for result in results if result)
        
        print(f"📊 DNS枚举完成: 发现 {found_count} 个子域名")
    
    def http_enumeration(self):
        """HTTP枚举子域名"""
        print(f"[HTTP枚举] 扫描域名: {self.domain}")
        
        def check_http(subdomain):
            full_domain = f"{subdomain}.{self.domain}"
            for protocol in ['http', 'https']:
                url = f"{protocol}://{full_domain}"
                try:
                    response = requests.get(url, timeout=5, verify=False)
                    if response.status_code == 200:
                        print(f"✅ HTTP发现: {url} (状态: {response.status_code})")
                        self.found_subdomains.append((full_domain, url))
                        return True
                except:
                    pass
            return False
        
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            results = executor.map(check_http, self.common_subdomains)
            found_count = sum(1 for result in results if result)
        
        print(f"📊 HTTP枚举完成: 发现 {found_count} 个可访问子域名")
    
    def certificate_enumeration(self):
        """SSL证书枚举子域名"""
        print(f"[证书枚举] 扫描域名: {self.domain}")
        
        # 使用证书透明度日志查询（简化实现）
        ct_urls = [
            f"https://crt.sh/?q=%.{self.domain}&output=json",
            f"https://api.certspotter.com/v1/issuances?domain={self.domain}&include_subdomains=true&expand=dns_names"
        ]
        
        for url in ct_urls:
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    # 解析返回的域名数据
                    data = response.json()
                    for item in data:
                        if 'name_value' in item:
                            subdomain = item['name_value']
                            if self.domain in subdomain:
                                print(f"✅ 证书发现: {subdomain}")
                                self.found_subdomains.append((subdomain, '证书发现'))
            except:
                pass
    
    def search_engine_enumeration(self):
        """搜索引擎枚举子域名"""
        print(f"[搜索引擎] 扫描域名: {self.domain}")
        
        search_queries = [
            f"site:*.{self.domain}",
            f"inurl:{self.domain}",
            f"-site:www.{self.domain} site:*.{self.domain}"
        ]
        
        # 模拟搜索引擎查询（简化实现）
        for query in search_queries:
            try:
                # 这里可以集成真实的搜索引擎API
                print(f"🔍 搜索: {query}")
                # 实际实现需要搜索引擎API密钥
            except:
                pass
    
    def comprehensive_scan(self):
        """综合扫描"""
        print(f"🚀 开始综合子域名枚举: {self.domain}")
        
        methods = [
            self.dns_enumeration,
            self.http_enumeration,
            self.certificate_enumeration,
            self.search_engine_enumeration
        ]
        
        for method in methods:
            try:
                method()
            except Exception as e:
                print(f"⚠️ 方法执行失败: {e}")
        
        # 去重
        unique_subdomains = list(set(self.found_subdomains))
        
        print(f"\n🎯 扫描完成!")
        print(f"📊 总共发现 {len(unique_subdomains)} 个唯一子域名")
        
        # 输出结果
        print("\n📋 发现的子域名:")
        for subdomain, info in unique_subdomains:
            print(f"   • {subdomain} -> {info}")
        
        # 保存结果到文件
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"subdomains_{self.domain}_{timestamp}.txt"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"子域名扫描结果 - {self.domain}\n")
            f.write(f"扫描时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"发现数量: {len(unique_subdomains)}\n\n")
            for subdomain, info in unique_subdomains:
                f.write(f"{subdomain} -> {info}\n")
        
        print(f"💾 结果已保存到: {filename}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='子域名枚举工具')
    parser.add_argument('--config', help='配置文件路径')
    parser.add_argument('domain', nargs='?', help='目标域名')
    
    args = parser.parse_args()
    
    # 创建工具实例
    tool = SubdomainEnumerationTool(config_file=args.config)
    
    # 如果通过命令行参数指定了域名
    if args.domain:
        tool.domain = args.domain
    
    # 如果没有配置文件且没有域名参数，进入交互模式
    if not args.config and not args.domain:
        tool.interactive_setup()
    
    # 执行扫描
    tool.comprehensive_scan()

if __name__ == "__main__":
    main()