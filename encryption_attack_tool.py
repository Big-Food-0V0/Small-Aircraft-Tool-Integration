#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
加密通信攻击工具
SSL剥离、中间人TLS、证书伪造
"""

import socket
import ssl
from datetime import datetime, timedelta

class EncryptionAttackTool:
    def __init__(self):
        self.attacks = {}
    
    def ssl_stripping_detection(self, target_url):
        """SSL剥离攻击检测"""
        print(f"🔍 SSL剥离检测: {target_url}")
        
        try:
            # 检查HTTP到HTTPS的重定向
            if not target_url.startswith('http'):
                target_url = 'http://' + target_url
            
            # 尝试HTTP连接
            http_url = target_url.replace('https://', 'http://')
            
            print(f"   🔄 检查HTTP重定向: {http_url}")
            
            # 模拟检查（实际需要更复杂的实现）
            print("   💡 SSL剥离攻击原理:")
            print("     1. 拦截HTTP到HTTPS的重定向")
            print("     2. 强制用户使用不加密的HTTP")
            print("     3. 中间人可读取所有通信内容")
            
            # 检测可能的SSL剥离漏洞
            vulnerabilities = []
            
            if 'http://' in target_url and 'login' in target_url.lower():
                vulnerabilities.append("登录页面使用HTTP，存在SSL剥离风险")
            
            if len(vulnerabilities) > 0:
                print("   ⚠️  发现SSL剥离风险:")
                for vuln in vulnerabilities:
                    print(f"      • {vuln}")
            else:
                print("   ✅ 未发现明显SSL剥离风险")
            
            return vulnerabilities
            
        except Exception as e:
            print(f"❌ SSL剥离检测失败: {e}")
            return []
    
    def tls_mitm_simulation(self, target_host, target_port=443):
        """TLS中间人攻击模拟"""
        print(f"🔐 TLS中间人攻击模拟: {target_host}:{target_port}")
        
        try:
            # 创建SSL上下文
            context = ssl.create_default_context()
            
            # 连接到目标服务器
            with socket.create_connection((target_host, target_port)) as sock:
                with context.wrap_socket(sock, server_hostname=target_host) as ssock:
                    # 获取证书信息
                    cert = ssock.getpeercert()
                    
                    print("   📜 目标服务器证书信息:")
                    if cert:
                        print(f"      主题: {cert.get('subject', '未知')}")
                        print(f"      颁发者: {cert.get('issuer', '未知')}")
                        
                        # 检查证书有效期
                        not_after = cert.get('notAfter', '')
                        if not_after:
                            print(f"      有效期至: {not_after}")
            
            print("\n   💡 TLS中间人攻击方法:")
            print("     1. 伪造证书颁发机构(CA)")
            print("     2. 生成目标网站的伪造证书")
            print("     3. 在中间人位置解密和重新加密流量")
            print("     4. 用户浏览器信任伪造证书")
            
            return True
            
        except Exception as e:
            print(f"❌ TLS中间人模拟失败: {e}")
            return False
    
    def certificate_analysis(self, target_host):
        """证书分析"""
        print(f"🔍 证书分析: {target_host}")
        
        try:
            context = ssl.create_default_context()
            
            with socket.create_connection((target_host, 443)) as sock:
                with context.wrap_socket(sock, server_hostname=target_host) as ssock:
                    cert = ssock.getpeercert()
                    
                    if cert:
                        print("   📋 证书详细信息:")
                        
                        # 解析主题
                        subject = cert.get('subject', [])
                        for item in subject:
                            for key, value in item:
                                if key == 'commonName':
                                    print(f"      域名: {value}")
                                elif key == 'organizationName':
                                    print(f"      组织: {value}")
                        
                        # 解析颁发者
                        issuer = cert.get('issuer', [])
                        for item in issuer:
                            for key, value in item:
                                if key == 'commonName':
                                    print(f"      颁发者: {value}")
                                elif key == 'organizationName':
                                    print(f"      颁发组织: {value}")
                        
                        # 有效期检查
                        not_before = cert.get('notBefore', '')
                        not_after = cert.get('notAfter', '')
                        
                        if not_before and not_after:
                            print(f"      有效期: {not_before} 至 {not_after}")
                            
                            # 检查是否过期
                            expiry_date = datetime.strptime(not_after, '%b %d %H:%M:%S %Y %Z')
                            if expiry_date < datetime.now():
                                print("      ⚠️  证书已过期")
                            elif expiry_date < datetime.now() + timedelta(days=30):
                                print("      ⚠️  证书即将过期")
                            else:
                                print("      ✅ 证书有效")
                        
                        # 检查扩展字段
                        extensions = cert.get('subjectAltName', [])
                        if extensions:
                            print("      备用名称:")
                            for ext_type, ext_value in extensions:
                                print(f"        • {ext_value}")
            
            return True
            
        except Exception as e:
            print(f"❌ 证书分析失败: {e}")
            return False
    
    def https_interception_test(self, target_url):
        """HTTPS拦截测试"""
        print(f"🔒 HTTPS拦截测试: {target_url}")
        
        try:
            # 简单的HTTPS请求测试
            import requests
            
            response = requests.get(target_url, timeout=10, verify=True)
            
            print("   🔄 HTTPS连接测试:")
            print(f"      状态码: {response.status_code}")
            print(f"      服务器: {response.headers.get('Server', '未知')}")
            
            # 检查安全头
            security_headers = ['Strict-Transport-Security', 'Content-Security-Policy']
            for header in security_headers:
                if header in response.headers:
                    print(f"      ✅ {header}: {response.headers[header]}")
                else:
                    print(f"      ⚠️  {header}: 缺失")
            
            print("\n   💡 HTTPS拦截攻击方法:")
            print("     1. 在网关位置安装伪造证书")
            print("     2. 解密HTTPS流量")
            print("     3. 分析或修改通信内容")
            print("     4. 重新加密发送给目标")
            
            return True
            
        except Exception as e:
            print(f"❌ HTTPS拦截测试失败: {e}")
            return False
    
    def run_encryption_attack_analysis(self):
        """运行加密攻击分析"""
        print("=" * 70)
        print("          加密通信攻击工具")
        print("=" * 70)
        
        target = input("请输入目标域名或URL: ").strip()
        
        if not target:
            target = "example.com"
            print(f"💡 使用示例目标: {target}")
        
        # 提取主机名
        if '://' in target:
            target_host = target.split('://')[1].split('/')[0]
        else:
            target_host = target.split('/')[0]
        
        print(f"🎯 分析目标: {target_host}")
        
        # 执行各种加密攻击分析
        print("\n1. 🔍 SSL剥离攻击检测")
        self.ssl_stripping_detection(target)
        
        print("\n2. 🔐 TLS中间人攻击分析")
        self.tls_mitm_simulation(target_host)
        
        print("\n3. 📜 证书安全性分析")
        self.certificate_analysis(target_host)
        
        print("\n4. 🔒 HTTPS拦截可行性测试")
        self.https_interception_test(f"https://{target_host}" if not target.startswith('http') else target)
        
        # 生成安全报告
        print("\n📋 加密安全报告:")
        print("   💡 攻击防御建议:")
        print("      • 强制使用HSTS头防止SSL剥离")
        print("      • 使用证书钉扎防止伪造证书")
        print("      • 定期检查证书有效性")
        print("      • 启用完整的HTTPS加密")

def main():
    """主函数"""
    encrypt_tool = EncryptionAttackTool()
    
    try:
        encrypt_tool.run_encryption_attack_analysis()
    except Exception as e:
        print(f"❌ 分析失败: {e}")

if __name__ == "__main__":
    main()