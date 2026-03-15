#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多运营商网络环境扫描工具
验证不同运营商用户在同一局域网的发现可能性
"""

import socket
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor

def run_command(cmd):
    """运行系统命令"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return -1, "", str(e)

def traceroute_analysis(target_ip):
    """路由追踪分析"""
    print(f"[+] 分析到 {target_ip} 的路由路径...")
    
    try:
        if target_ip.startswith('10.30.'):
            # 内部IP，使用tracert
            code, stdout, stderr = run_command(f"tracert -d -h 5 {target_ip}")
            
            if code == 0:
                lines = stdout.split('\n')
                hop_count = 0
                
                for line in lines:
                    if line.strip() and line[0].isdigit():
                        hop_count += 1
                        parts = line.split()
                        if len(parts) >= 3:
                            hop_ip = parts[-1]
                            print(f"    跳数 {hop_count}: {hop_ip}")
                
                return hop_count
        
    except Exception as e:
        print(f"    [-] 路由分析失败: {e}")
    
    return 0

def check_connectivity_variants(target_ip):
    """检查多种连通性"""
    results = {}
    
    # 1. ICMP (ping)
    print(f"    [ICMP] 检查ping连通性...")
    code, stdout, stderr = run_command(f"ping -n 2 -w 2000 {target_ip}")
    results['icmp'] = code == 0 and "TTL=" in stdout
    
    # 2. TCP端口扫描（常见端口）
    common_ports = [80, 443, 22, 23, 53, 21, 135, 139, 445, 3389]
    open_ports = []
    
    for port in common_ports[:3]:  # 只测试前3个端口以节省时间
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex((target_ip, port))
            sock.close()
            
            if result == 0:
                open_ports.append(port)
        except:
            pass
    
    results['tcp'] = len(open_ports) > 0
    results['open_ports'] = open_ports
    
    # 3. UDP端口扫描
    udp_ports = [53, 123, 161, 162, 514]
    udp_results = []
    
    for port in udp_ports[:2]:  # 只测试前2个UDP端口
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(2)
            
            # 发送测试数据
            if port == 53:  # DNS
                message = b'\x00\x00\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x07version\x04bind\x00\x00\x10\x00\x03'
            else:
                message = b'TEST'
            
            sock.sendto(message, (target_ip, port))
            
            try:
                data, addr = sock.recvfrom(1024)
                udp_results.append(port)
            except socket.timeout:
                pass
            
            sock.close()
        except:
            pass
    
    results['udp'] = len(udp_results) > 0
    results['udp_ports'] = udp_results
    
    return results

def isp_identification(ip):
    """运营商识别（基于IP段模式）"""
    # 简单的IP段模式识别（实际需要更复杂的数据库）
    ip_parts = ip.split('.')
    
    if len(ip_parts) >= 2:
        second_octet = int(ip_parts[1])
        
        # 基于常见的运营商IP段模式（简化版）
        if 0 <= second_octet <= 50:
            return "移动/内部网络"
        elif 51 <= second_octet <= 100:
            return "电信"
        elif 101 <= second_octet <= 150:
            return "联通"
        elif 151 <= second_octet <= 200:
            return "教育网"
        else:
            return "其他/未知"
    
    return "未知"

def multi_isp_scan():
    """多运营商环境扫描"""
    print("=" * 70)
    print("        多运营商网络环境扫描分析")
    print("        验证不同运营商用户的发现可能性")
    print("=" * 70)
    
    # 生成测试IP列表（覆盖不同运营商段）
    test_ips = []
    base_network = "10.30"
    
    # 测试不同运营商段的IP
    isp_segments = [
        ("移动/内部", [1, 10, 20, 30, 40, 50]),
        ("电信", [60, 70, 80, 90, 100]),
        ("联通", [110, 120, 130, 140, 150]),
        ("教育网", [160, 170, 180, 190, 200]),
        ("其他", [210, 220, 230, 240, 250])
    ]
    
    for isp_name, segments in isp_segments:
        for segment in segments:
            for host in [1, 50, 100, 150, 200, 254]:  # 测试每个段的几个主机
                test_ips.append((f"{base_network}.{segment}.{host}", isp_name))
    
    print(f"[+] 生成 {len(test_ips)} 个测试IP，覆盖5种运营商类型")
    print("[+] 开始连通性测试（可能需要几分钟）...\n")
    
    results = {}
    
    def test_single_ip(ip_isp):
        ip, expected_isp = ip_isp
        
        # 跳过本机IP
        if ip == "10.30.77.84":
            return None
        
        print(f"测试 IP: {ip} (预期运营商: {expected_isp})")
        
        # 路由分析
        hop_count = traceroute_analysis(ip)
        
        # 连通性测试
        connectivity = check_connectivity_variants(ip)
        
        # 实际运营商识别
        actual_isp = isp_identification(ip)
        
        result = {
            'ip': ip,
            'expected_isp': expected_isp,
            'actual_isp': actual_isp,
            'hop_count': hop_count,
            'connectivity': connectivity,
            'reachable': connectivity['icmp'] or connectivity['tcp'] or connectivity['udp']
        }
        
        # 显示结果
        status = "✅ 可达" if result['reachable'] else "❌ 不可达"
        print(f"    {status} | 跳数: {hop_count} | 运营商: {actual_isp}")
        
        if result['reachable']:
            if connectivity['icmp']:
                print("        ICMP: 可达")
            if connectivity['tcp'] and connectivity['open_ports']:
                print(f"        TCP开放端口: {connectivity['open_ports']}")
            if connectivity['udp'] and connectivity['udp_ports']:
                print(f"        UDP响应端口: {connectivity['udp_ports']}")
        
        print()
        time.sleep(0.1)  # 避免过于频繁
        
        return result
    
    # 多线程测试
    with ThreadPoolExecutor(max_workers=10) as executor:
        test_results = list(executor.map(test_single_ip, test_ips))
    
    # 统计结果
    reachable_by_isp = {}
    total_reachable = 0
    
    for result in test_results:
        if result and result['reachable']:
            total_reachable += 1
            isp = result['actual_isp']
            reachable_by_isp[isp] = reachable_by_isp.get(isp, 0) + 1
    
    # 显示汇总结果
    print("\n" + "=" * 70)
    print("扫描结果汇总")
    print("=" * 70)
    
    print(f"总测试IP数: {len(test_ips)}")
    print(f"可达IP数: {total_reachable}")
    print(f"发现率: {total_reachable/len(test_ips)*100:.1f}%")
    
    print("\n按运营商统计:")
    for isp, count in reachable_by_isp.items():
        percentage = count / total_reachable * 100 if total_reachable > 0 else 0
        print(f"    {isp}: {count} 个IP ({percentage:.1f}%)")
    
    # 技术分析
    print("\n" + "=" * 70)
    print("技术分析结论")
    print("=" * 70)
    
    if total_reachable > len(test_ips) * 0.1:  # 如果发现率超过10%
        print("✅ 多运营商环境扫描可行性: 高")
        print("   不同运营商的用户在同一局域网中可以相互发现")
        print("   网络隔离策略相对宽松")
    elif total_reachable > 0:
        print("⚠️  多运营商环境扫描可行性: 中等")
        print("   部分运营商用户可能被发现")
        print("   网络存在一定程度的隔离")
    else:
        print("❌ 多运营商环境扫描可行性: 低")
        print("   严格的客户端隔离策略")
        print("   不同运营商用户间无法直接通信")

def main():
    """主函数"""
    print("⚠️  此工具用于分析多运营商网络环境的扫描可能性")
    print("   仅供技术研究和网络管理使用\n")
    
    confirm = input("是否开始扫描分析？(y/N): ").lower()
    if confirm != 'y':
        print("扫描已取消")
        return
    
    start_time = time.time()
    multi_isp_scan()
    end_time = time.time()
    
    print(f"\n[+] 分析完成，耗时: {end_time - start_time:.2f} 秒")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n扫描被用户中断")
    except Exception as e:
        print(f"\n[-] 扫描出错: {e}")