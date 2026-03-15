#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网络侦查和信息收集工具
目标信息收集、指纹识别、拓扑发现
"""

import socket
import subprocess
import requests
from scapy.all import *

class ReconnaissanceTool:
    def __init__(self):
        self.collected_info = {}
    
    def dns_reconnaissance(self, target_domain):
        """DNS侦查"""
        print(f"🔍 DNS侦查: {target_domain}")
        
        try:
            # DNS记录查询
            dns_records = {}
            
            # A记录
            a_records = socket.getaddrinfo(target_domain, None)
            dns_records["A"] = [record[4][0] for record in a_records]
            
            print(f"   📍 A记录: {dns_records['A']}")
            
            # MX记录（邮件服务器）
            try:
                mx_records = socket.getaddrinfo(f"mail.{target_domain}", None)
                dns_records["MX"] = [record[4][0] for record in mx_records]
                print(f"   📧 MX记录: {dns_records['MX']}")
            except:
                print("   ❌ 未发现MX记录")
            
            self.collected_info["dns"] = dns_records
            
        except Exception as e:
            print(f"❌ DNS侦查失败: {e}")
    
    def whois_lookup(self, target_ip_or_domain):
        """WHOIS查询"""
        print(f"🔍 WHOIS查询: {target_ip_or_domain}")
        
        try:
            # 使用系统whois命令
            result = subprocess.run(['whois', target_ip_or_domain], 
                                  capture_output=True, text=True)
            
            # 提取关键信息
            whois_info = {}
            for line in result.stdout.split('\n'):
                if 'Organization:' in line or 'OrgName:' in line:
                    whois_info['organization'] = line.split(':', 1)[1].strip()
                elif 'Country:' in line or 'CountryCode:' in line:
                    whois_info['country'] = line.split(':', 1)[1].strip()
                elif 'NetRange:' in line:
                    whois_info['netrange'] = line.split(':', 1)[1].strip()
            
            if whois_info:
                for key, value in whois_info.items():
                    print(f"   📋 {key}: {value}")
            else:
                print("   ❌ 未找到WHOIS信息")
            
            self.collected_info["whois"] = whois_info
            
        except Exception as e:
            print(f"❌ WHOIS查询失败: {e}")
    
    def service_fingerprinting(self, target_ip, ports=None):
        """服务指纹识别"""
        print(f"🔍 服务指纹识别: {target_ip}")
        
        if ports is None:
            ports = [21, 22, 23, 25, 53, 80, 110, 443, 993, 995, 3389]
        
        services = {}
        
        for port in ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(3)
                result = sock.connect_ex((target_ip, port))
                
                if result == 0:
                    # 端口开放，尝试获取banner
                    try:
                        sock.send(b"\\r\\n")
                        banner = sock.recv(1024).decode('utf-8', errors='ignore')
                        
                        service_name = socket.getservbyport(port, 'tcp')
                        services[port] = {
                            'service': service_name,
                            'banner': banner.strip()
                        }
                        
                        print(f"   🔧 端口 {port} ({service_name}): {banner[:50]}...")
                        
                    except:
                        service_name = socket.getservbyport(port, 'tcp')
                        services[port] = {'service': service_name, 'banner': '未知'}
                        print(f"   🔧 端口 {port} ({service_name}): 无banner信息")
                
                sock.close()
                
            except:
                pass
        
        self.collected_info["services"] = services
    
    def network_topo_discovery(self, target_ip):
        """网络拓扑发现"""
        print(f"🔍 网络拓扑发现: {target_ip}")
        
        # 获取网络段
        ip_parts = target_ip.split('.')
        network_segment = f"{ip_parts[0]}.{ip_parts[1]}.{ip_parts[2]}"
        
        print(f"   🌐 网络段: {network_segment}.x")
        
        #  traceroute路径发现
        try:
            result = subprocess.run(['tracert', '-d', '-h', '5', target_ip], 
                                  capture_output=True, text=True)
            
            hops = []
            for line in result.stdout.split('\n'):
                if '*' not in line and len(line.strip()) > 0:
                    parts = line.split()
                    if len(parts) > 2 and parts[-1].replace('.', '').isdigit():
                        hop_ip = parts[-1]
                        if hop_ip != target_ip:
                            hops.append(hop_ip)
            
            if hops:
                print(f"   🛣️  网络路径: {' -> '.join(hops[:3])}...")
            
            self.collected_info["topology"] = {
                'network_segment': network_segment,
                'hops': hops
            }
            
        except Exception as e:
            print(f"❌ 拓扑发现失败: {e}")
    
    def web_tech_detection(self, target_url):
        """Web技术检测"""
        print(f"🔍 Web技术检测: {target_url}")
        
        try:
            response = requests.get(target_url, timeout=10)
            
            tech_info = {}
            
            # 服务器信息
            if 'Server' in response.headers:
                tech_info['server'] = response.headers['Server']
                print(f"   🖥️  服务器: {response.headers['Server']}")
            
            # 框架检测
            if 'X-Powered-By' in response.headers:
                tech_info['framework'] = response.headers['X-Powered-By']
                print(f"   ⚙️  框架: {response.headers['X-Powered-By']}")
            
            # 内容类型
            if 'Content-Type' in response.headers:
                tech_info['content_type'] = response.headers['Content-Type']
                print(f"   📄 内容类型: {response.headers['Content-Type']}")
            
            # 检查常见技术特征
            html_content = response.text.lower()
            
            if 'wordpress' in html_content:
                tech_info['cms'] = 'WordPress'
                print("   📝 CMS: WordPress")
            elif 'drupal' in html_content:
                tech_info['cms'] = 'Drupal'
                print("   📝 CMS: Drupal")
            elif 'joomla' in html_content:
                tech_info['cms'] = 'Joomla'
                print("   📝 CMS: Joomla")
            
            self.collected_info["web_tech"] = tech_info
            
        except Exception as e:
            print(f"❌ Web技术检测失败: {e}")
    
    def run_complete_recon(self, target):
        """运行完整侦查"""
        print("=" * 70)
        print("          网络侦查和信息收集工具")
        print("=" * 70)
        
        print(f"🎯 目标: {target}")
        
        # 判断目标是IP还是域名
        if target.replace('.', '').isdigit() and len(target.split('.')) == 4:
            target_ip = target
            target_domain = None
        else:
            target_domain = target
            try:
                target_ip = socket.gethostbyname(target_domain)
            except:
                target_ip = None
        
        if target_ip:
            print(f"📍 解析IP: {target_ip}")
            
            # 执行各种侦查
            self.whois_lookup(target_ip)
            self.service_fingerprinting(target_ip)
            self.network_topo_discovery(target_ip)
        
        if target_domain:
            self.dns_reconnaissance(target_domain)
            
            # 尝试Web技术检测
            for protocol in ['http', 'https']:
                url = f"{protocol}://{target_domain}"
                try:
                    self.web_tech_detection(url)
                    break
                except:
                    continue
        
        # 生成侦查报告
        print("\n📋 侦查报告:")
        for category, info in self.collected_info.items():
            print(f"   📁 {category.upper()}: {len(info)} 项信息")

def main():
    """主函数"""
    recon = ReconnaissanceTool()
    
    # 测试目标
    target = "example.com"  # 可以修改为实际目标
    
    print("💡 这是一个演示工具，请修改target为实际目标")
    print("💡 实际使用时请确保有授权")
    
    # recon.run_complete_recon(target)

if __name__ == "__main__":
    main()