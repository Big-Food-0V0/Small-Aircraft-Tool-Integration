#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
跨局域网公网目标扫描工具
专门针对不同网络环境的远程目标扫描
"""

import socket
import subprocess
import time
import requests
from concurrent.futures import ThreadPoolExecutor

def run_command(cmd):
    """运行系统命令"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return -1, "", str(e)

def check_public_connectivity():
    """检查公网连通性"""
    print("[+] 检查公网连通性...")
    
    test_targets = [
        ("8.8.8.8", "Google DNS"),
        ("1.1.1.1", "Cloudflare DNS"),
        ("114.114.114.114", "国内DNS")
    ]
    
    for ip, description in test_targets:
        code, stdout, stderr = run_command(f"ping -n 2 -w 2000 {ip}")
        if code == 0 and "TTL=" in stdout:
            print(f"    ✅ {description} ({ip}): 可达")
        else:
            print(f"    ❌ {description} ({ip}): 不可达")

def public_port_scan(target_ip, ports=None):
    """公网端口扫描"""
    if ports is None:
        ports = [
            21,    # FTP
            22,    # SSH
            23,    # Telnet
            53,    # DNS
            80,    # HTTP
            443,   # HTTPS
            8080,  # HTTP-alt
            8443,  # HTTPS-alt
            3389,  # RDP
            5900,  # VNC
        ]
    
    print(f"[+] 开始公网端口扫描: {target_ip}")
    
    open_ports = []
    
    def scan_port(port):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            result = sock.connect_ex((target_ip, port))
            sock.close()
            
            if result == 0:
                open_ports.append(port)
                return port, "开放"
            else:
                return port, "关闭"
        except:
            return port, "错误"
    
    # 多线程扫描
    with ThreadPoolExecutor(max_workers=20) as executor:
        results = list(executor.map(scan_port, ports))
    
    # 显示结果
    print(f"    扫描完成，发现 {len(open_ports)} 个开放端口:")
    for port in open_ports:
        # 获取服务名称
        service_name = get_service_name(port)
        print(f"        {port}/tcp - {service_name}")
    
    return open_ports

def get_service_name(port):
    """获取端口对应的服务名称"""
    services = {
        21: "FTP",
        22: "SSH",
        23: "Telnet",
        25: "SMTP",
        53: "DNS",
        80: "HTTP",
        110: "POP3",
        143: "IMAP",
        443: "HTTPS",
        993: "IMAPS",
        995: "POP3S",
        1433: "MSSQL",
        1521: "Oracle",
        3306: "MySQL",
        3389: "RDP",
        5432: "PostgreSQL",
        5900: "VNC",
        8080: "HTTP-Proxy",
        8443: "HTTPS-Alt"
    }
    return services.get(port, "未知")

def http_service_discovery(target_ip, ports=[80, 443, 8080, 8443]):
    """HTTP服务发现"""
    print(f"[+] HTTP服务发现: {target_ip}")
    
    discovered_services = []
    
    for port in ports:
        for scheme in ["http", "https"]:
            if (scheme == "http" and port in [80, 8080]) or (scheme == "https" and port in [443, 8443]):
                url = f"{scheme}://{target_ip}:{port}"
                
                try:
                    response = requests.get(url, timeout=5, verify=False)
                    
                    service_info = {
                        'url': url,
                        'status_code': response.status_code,
                        'server': response.headers.get('Server', '未知'),
                        'title': extract_page_title(response.text)
                    }
                    
                    discovered_services.append(service_info)
                    print(f"    ✅ {url} - 状态: {response.status_code}")
                    print(f"        服务器: {service_info['server']}")
                    if service_info['title']:
                        print(f"        标题: {service_info['title']}")
                    
                except requests.exceptions.RequestException as e:
                    # 连接失败，端口可能关闭
                    pass
                except Exception as e:
                    print(f"    ❌ {url} - 错误: {e}")
    
    return discovered_services

def extract_page_title(html):
    """提取HTML页面标题"""
    try:
        import re
        title_match = re.search(r'<title[^>]*>(.*?)</title>', html, re.IGNORECASE)
        if title_match:
            return title_match.group(1).strip()
    except:
        pass
    return ""

def dns_enumeration(target_domain):
    """DNS枚举"""
    print(f"[+] DNS枚举: {target_domain}")
    
    record_types = ['A', 'AAAA', 'MX', 'TXT', 'NS', 'CNAME']
    
    try:
        import dns.resolver
        
        for record_type in record_types:
            try:
                answers = dns.resolver.resolve(target_domain, record_type)
                print(f"    {record_type} 记录:")
                for rdata in answers:
                    print(f"        {rdata}")
            except:
                pass
                
    except ImportError:
        print("    [!] 需要安装dnspython库: pip install dnspython")

def network_traceroute(target_ip):
    """网络路由追踪"""
    print(f"[+] 路由追踪: {target_ip}")
    
    try:
        code, stdout, stderr = run_command(f"tracert -d -h 15 {target_ip}")
        
        if code == 0:
            lines = stdout.split('\n')
            hop_count = 0
            
            print("    路由路径:")
            for line in lines:
                if line.strip() and line[0].isdigit():
                    hop_count += 1
                    parts = line.split()
                    if len(parts) >= 3:
                        hop_ip = parts[-1]
                        print(f"        {hop_count}. {hop_ip}")
                        
                        # 如果是最后一跳，显示目标
                        if hop_ip == target_ip:
                            print(f"        ✅ 到达目标: {target_ip}")
                            break
            
            return hop_count
        else:
            print("    ❌ 路由追踪失败")
            
    except Exception as e:
        print(f"    ❌ 路由追踪错误: {e}")
    
    return 0

def comprehensive_public_scan(target_ip):
    """综合公网扫描"""
    print("=" * 70)
    print("        跨局域网公网目标扫描")
    print("        针对不同网络环境的远程目标")
    print("=" * 70)
    
    # 1. 检查公网连通性
    check_public_connectivity()
    
    # 2. 路由追踪
    hop_count = network_traceroute(target_ip)
    
    if hop_count == 0:
        print("\n❌ 目标不可达，扫描终止")
        return
    
    print(f"\n[+] 目标 {target_ip} 可达，跳数: {hop_count}")
    
    # 3. 端口扫描
    open_ports = public_port_scan(target_ip)
    
    # 4. HTTP服务发现
    if open_ports:
        http_services = http_service_discovery(target_ip, open_ports)
    else:
        # 即使没有常见开放端口，也尝试标准端口
        http_services = http_service_discovery(target_ip)
    
    # 5. 结果汇总
    print("\n" + "=" * 70)
    print("扫描结果汇总")
    print("=" * 70)
    
    if open_ports:
        print(f"✅ 发现 {len(open_ports)} 个开放端口")
        for port in open_ports:
            service = get_service_name(port)
            print(f"    {port}/tcp - {service}")
    else:
        print("❌ 未发现开放端口")
    
    if http_services:
        print(f"\n✅ 发现 {len(http_services)} 个HTTP服务")
        for service in http_services:
            print(f"    URL: {service['url']}")
            print(f"    状态: {service['status_code']}")
            print(f"    服务器: {service['server']}")
            if service['title']:
                print(f"    标题: {service['title']}")
            print()
    
    # 风险评估
    print("\n" + "=" * 70)
    print("安全风险评估")
    print("=" * 70)
    
    if open_ports:
        risk_ports = [port for port in open_ports if port in [21, 22, 23, 3389, 5900]]
        if risk_ports:
            print("⚠️  发现高风险端口:")
            for port in risk_ports:
                print(f"    {port} - {get_service_name(port)} (可能暴露敏感服务)")
        else:
            print("✅ 未发现明显高风险端口")
    else:
        print("✅ 目标看起来相对安全（无开放端口）")

def main():
    """主函数"""
    print("⚠️  重要提醒：此工具仅用于授权的安全测试")
    print("   未经授权扫描他人网络属于违法行为！\n")
    
    target_ip = input("输入要扫描的公网IP地址 (例如: 26.0.0.1): ").strip()
    
    if not target_ip:
        print("[-] IP地址不能为空")
        return
    
    # 验证IP格式
    try:
        socket.inet_aton(target_ip)
    except socket.error:
        print("[-] 无效的IP地址格式")
        return
    
    # 检查是否为私有IP
    if target_ip.startswith(('10.', '172.', '192.168.')):
        print("[-] 这是私有IP地址，请使用公网IP")
        return
    
    confirm = input(f"确认扫描 {target_ip}？(y/N): ").lower()
    if confirm != 'y':
        print("扫描已取消")
        return
    
    start_time = time.time()
    comprehensive_public_scan(target_ip)
    end_time = time.time()
    
    print(f"\n[+] 扫描完成，耗时: {end_time - start_time:.2f} 秒")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n扫描被用户中断")
    except Exception as e:
        print(f"\n[-] 扫描出错: {e}")