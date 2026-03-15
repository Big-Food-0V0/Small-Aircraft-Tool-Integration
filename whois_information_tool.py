#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WHOIS信息查询工具
获取域名的注册信息和所有者信息
"""

import socket
import whois
import json
import requests
from datetime import datetime

class WhoisInformationTool:
    def __init__(self):
        self.whois_servers = {
            'com': 'whois.verisign-grs.com',
            'net': 'whois.verisign-grs.com',
            'org': 'whois.pir.org',
            'edu': 'whois.educause.edu',
            'gov': 'whois.dotgov.gov',
            'cn': 'whois.cnnic.cn',
            'uk': 'whois.nic.uk',
            'de': 'whois.denic.de',
            'fr': 'whois.nic.fr',
            'jp': 'whois.jprs.jp',
            'ru': 'whois.tcinet.ru'
        }
    
    def python_whois_query(self, domain):
        """使用python-whois库查询"""
        try:
            w = whois.whois(domain)
            return w
        except Exception as e:
            return f"错误: {e}"
    
    def socket_whois_query(self, domain, server=None):
        """使用socket直接查询WHOIS服务器"""
        if not server:
            # 自动选择WHOIS服务器
            tld = domain.split('.')[-1]
            server = self.whois_servers.get(tld, 'whois.iana.org')
        
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((server, 43))
            s.send((domain + '\r\n').encode())
            
            response = b''
            while True:
                data = s.recv(4096)
                if not data:
                    break
                response += data
            
            s.close()
            return response.decode('utf-8', errors='ignore')
        except Exception as e:
            return f"错误: {e}"
    
    def parse_whois_data(self, whois_data):
        """解析WHOIS数据"""
        parsed_info = {}
        
        if isinstance(whois_data, dict):
            # python-whois返回的字典格式
            for key, value in whois_data.items():
                if value and str(value) != '[]':
                    parsed_info[key] = value
        elif isinstance(whois_data, str):
            # 原始WHOIS文本格式
            lines = whois_data.split('\n')
            for line in lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip()
                    if value:
                        parsed_info[key] = value
        
        return parsed_info
    
    def get_domain_info_summary(self, domain):
        """获取域名信息摘要"""
        print(f"🔍 查询域名: {domain}")
        
        # 使用python-whois查询
        whois_result = self.python_whois_query(domain)
        
        if isinstance(whois_result, str) and '错误' in whois_result:
            # 如果python-whois失败，使用socket查询
            print("⚠️  python-whois查询失败，尝试socket查询...")
            raw_data = self.socket_whois_query(domain)
            parsed_info = self.parse_whois_data(raw_data)
        else:
            parsed_info = self.parse_whois_data(whois_result)
        
        return parsed_info
    
    def display_whois_info(self, domain, info):
        """显示WHOIS信息"""
        print(f"\n{'='*80}")
        print(f"          📋 {domain} WHOIS信息")
        print(f"{'='*80}")
        
        # 关键信息字段映射
        key_fields = {
            'domain_name': '域名',
            'registrar': '注册商',
            'whois_server': 'WHOIS服务器',
            'referral_url': '参考URL',
            'updated_date': '更新日期',
            'creation_date': '创建日期',
            'expiration_date': '过期日期',
            'name_servers': '名称服务器',
            'status': '状态',
            'emails': '邮箱',
            'dnssec': 'DNSSEC',
            'name': '注册人姓名',
            'org': '组织',
            'address': '地址',
            'city': '城市',
            'state': '州/省',
            'zipcode': '邮编',
            'country': '国家'
        }
        
        for eng_key, chn_key in key_fields.items():
            if eng_key in info:
                value = info[eng_key]
                if value:
                    print(f"{chn_key}: {value}")
        
        # 显示原始WHOIS数据中的其他重要信息
        print(f"\n{'='*80}")
        print("          其他信息")
        print(f"{'='*80}")
        
        for key, value in info.items():
            if key not in key_fields and value:
                print(f"{key}: {value}")
    
    def check_domain_availability(self, domain):
        """检查域名可用性"""
        print(f"\n🔍 检查域名可用性: {domain}")
        
        try:
            # 尝试解析域名
            socket.gethostbyname(domain)
            print("❌ 域名已被注册")
            return False
        except:
            print("✅ 域名可用")
            return True
    
    def get_ip_geolocation(self, domain):
        """获取IP地理位置信息"""
        try:
            ip = socket.gethostbyname(domain)
            print(f"\n🌐 IP地址: {ip}")
            
            # 使用ipapi.co获取地理位置（免费服务）
            url = f"http://ipapi.co/{ip}/json/"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                geo_data = response.json()
                print("📍 地理位置信息:")
                print(f"   国家: {geo_data.get('country_name', '未知')}")
                print(f"   城市: {geo_data.get('city', '未知')}")
                print(f"   运营商: {geo_data.get('org', '未知')}")
                print(f"   时区: {geo_data.get('timezone', '未知')}")
        except Exception as e:
            print(f"❌ 获取地理位置失败: {e}")
    
    def comprehensive_domain_analysis(self, domain):
        """综合域名分析"""
        print(f"🚀 开始综合域名分析: {domain}")
        
        # 1. WHOIS信息查询
        whois_info = self.get_domain_info_summary(domain)
        self.display_whois_info(domain, whois_info)
        
        # 2. 域名可用性检查
        self.check_domain_availability(domain)
        
        # 3. IP地理位置信息
        self.get_ip_geolocation(domain)
        
        # 4. 安全评估
        print(f"\n{'='*80}")
        print("          🔒 安全评估")
        print(f"{'='*80}")
        
        # 检查域名年龄
        if 'creation_date' in whois_info:
            creation_date = whois_info['creation_date']
            if isinstance(creation_date, list):
                creation_date = creation_date[0]
            
            if isinstance(creation_date, datetime):
                domain_age = (datetime.now() - creation_date).days
                print(f"域名年龄: {domain_age} 天")
                
                if domain_age < 365:
                    print("⚠️  域名较新，可能存在风险")
                else:
                    print("✅ 域名较老，相对可信")
        
        # 检查名称服务器
        if 'name_servers' in whois_info:
            ns_count = len(whois_info['name_servers']) if isinstance(whois_info['name_servers'], list) else 1
            print(f"名称服务器数量: {ns_count}")
            if ns_count >= 2:
                print("✅ 名称服务器配置良好")
            else:
                print("⚠️  名称服务器配置单一")

def main():
    """主函数"""
    tool = WhoisInformationTool()
    
    print("=" * 80)
    print("          🔍 WHOIS信息查询工具")
    print("=" * 80)
    
    domain = input("🎯 请输入目标域名 (例如: example.com): ")
    
    if domain:
        tool.comprehensive_domain_analysis(domain)

if __name__ == "__main__":
    main()