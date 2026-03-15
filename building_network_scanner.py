#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
建筑内部跨楼层网络扫描工具
针对同一建筑不同楼层的网络发现
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

def analyze_network_topology():
    """分析网络拓扑"""
    print("[+] 分析建筑内部网络拓扑...")
    
    # 获取本机网络信息
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        
        print(f"    本机IP: {local_ip}")
        print(f"    网络类型: {'私有地址' if local_ip.startswith(('10.', '172.', '192.168.')) else '公网地址'}")
        
        # 获取默认网关
        code, stdout, stderr = run_command("ipconfig")
        if code == 0:
            for line in stdout.split('\n'):
                if "默认网关" in line or "Default Gateway" in line:
                    print(f"    默认网关: {line.strip()}")
        
        return local_ip
    except Exception as e:
        print(f"    [-] 网络分析失败: {e}")
        return None

def check_internal_routing(target_network):
    """检查内部路由连通性"""
    print(f"[+] 检查到 {target_network} 的内部路由...")
    
    # 测试路由是否存在
    code, stdout, stderr = run_command(f"route print")
    
    if code == 0 and target_network.split('.')[0] in stdout:
        print("    ✅ 发现内部路由条目")
        return True
    else:
        print("    ❌ 未发现直接路由")
        return False

def building_icmp_discovery(target_base):
    """建筑内部ICMP发现"""
    print(f"[+] 建筑内部ICMP发现: {target_base}.x")
    
    discovered = []
    
    # 扫描建筑内部常见IP段
    common_building_ips = []
    
    # 生成测试IP（建筑内部常见分配）
    for third_octet in [1, 10, 20, 30, 40, 50, 100, 200]:
        for host in [1, 10, 50, 100, 150, 200, 254]:  # 常见服务器/设备IP
            ip = f"{target_base}.{third_octet}.{host}"
            common_building_ips.append(ip)
    
    # 添加网关测试
    common_building_ips.append(f"{target_base}.255.254")  # 类似您的网关模式
    common_building_ips.append(f"{target_base}.0.1")      # 常见网关
    common_building_ips.append(f"{target_base}.1.1")      # 常见网关
    
    def ping_test(ip):
        try:
            code, stdout, stderr = run_command(f"ping -n 1 -w 1000 {ip}")
            if code == 0 and "TTL=" in stdout:
                # 获取设备类型信息
                device_type = identify_device_type(ip, stdout)
                discovered.append({'ip': ip, 'type': device_type})
                return ip, "活跃"
            return ip, "无响应"
        except:
            return ip, "错误"
    
    print(f"    测试 {len(common_building_ips)} 个建筑内部常见IP...")
    
    with ThreadPoolExecutor(max_workers=20) as executor:
        results = list(executor.map(ping_test, common_building_ips))
    
    print(f"    发现 {len(discovered)} 个活跃设备")
    return discovered

def identify_device_type(ip, ping_output):
    """识别设备类型"""
    # 基于TTL值和IP模式识别设备类型
    if "TTL=128" in ping_output:
        return "Windows设备"
    elif "TTL=64" in ping_output:
        return "Linux/网络设备"
    elif "TTL=255" in ping_output:
        return "路由器/交换机"
    
    # 基于IP地址模式
    if ip.endswith('.1') or ip.endswith('.254'):
        return "网络设备"
    elif ip.split('.')[2] in ['1', '10', '100']:
        return "服务器"
    else:
        return "用户设备"

def internal_service_scan(target_network):
    """内部服务扫描"""
    print(f"[+] 内部服务扫描: {target_network}")
    
    # 建筑内部常见服务端口
    building_services = {
        21: "FTP",
        22: "SSH",
        23: "Telnet", 
        53: "DNS",
        80: "HTTP",
        443: "HTTPS",
        135: "RPC",
        139: "NetBIOS",
        445: "SMB",
        1433: "MSSQL",
        1521: "Oracle",
        3306: "MySQL",
        3389: "RDP",
        5432: "PostgreSQL",
        5900: "VNC",
        8080: "HTTP代理",
        8443: "HTTPS代理"
    }
    
    discovered_services = []
    
    # 生成测试IP（建筑内部服务器常见IP）
    test_ips = []
    base = target_network.split('.')[0]  # 获取网络基础
    
    for server_ip in [f"{base}.1.10", f"{base}.10.1", f"{base}.100.1", f"{base}.200.1"]:
        test_ips.append(server_ip)
    
    def scan_service(ip_port):
        ip, port = ip_port
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex((ip, port))
            sock.close()
            
            if result == 0:
                service_name = building_services.get(port, "未知")
                discovered_services.append({'ip': ip, 'port': port, 'service': service_name})
                return ip, port, "开放"
            return ip, port, "关闭"
        except:
            return ip, port, "错误"
    
    # 生成IP-端口组合
    ip_port_combinations = []
    for ip in test_ips:
        for port in building_services.keys():
            ip_port_combinations.append((ip, port))
    
    print(f"    扫描 {len(test_ips)} 个内部服务器IP的 {len(building_services)} 个服务端口...")
    
    with ThreadPoolExecutor(max_workers=15) as executor:
        list(executor.map(scan_service, ip_port_combinations))
    
    print(f"    发现 {len(discovered_services)} 个内部服务")
    return discovered_services

def building_network_scan():
    """建筑内部网络扫描"""
    print("=" * 70)
    print("        建筑内部跨楼层网络扫描")
    print("        同一建筑不同楼层的网络发现")
    print("=" * 70)
    
    # 1. 分析本机网络
    local_ip = analyze_network_topology()
    
    if not local_ip:
        print("[-] 无法获取网络信息")
        return
    
    # 提取网络基础（第一个字节）
    network_base = local_ip.split('.')[0]
    
    # 2. 用户输入目标网络
    target_base = input(f"输入目标网络基础 (默认使用 {network_base}): ").strip()
    if not target_base:
        target_base = network_base
    
    target_network = f"{target_base}.0.0/8"  # 假设建筑使用A类私有地址
    
    print(f"\n[+] 扫描目标: {target_network}")
    print(f"[+] 本机网络: {local_ip}")
    
    # 3. 检查内部路由
    has_route = check_internal_routing(target_network)
    
    if not has_route:
        print("[!] 警告: 未发现直接路由，扫描可能受限")
    
    # 4. ICMP发现
    icmp_devices = building_icmp_discovery(target_base)
    
    # 5. 内部服务扫描
    internal_services = internal_service_scan(target_network)
    
    # 6. 结果显示
    print("\n" + "=" * 70)
    print("扫描结果汇总")
    print("=" * 70)
    
    if icmp_devices:
        print(f"✅ ICMP发现 {len(icmp_devices)} 个活跃设备:")
        for device in icmp_devices:
            print(f"    {device['ip']} - {device['type']}")
    else:
        print("❌ 未发现ICMP活跃设备")
    
    if internal_services:
        print(f"\n✅ 发现 {len(internal_services)} 个内部服务:")
        for service in internal_services:
            print(f"    {service['ip']}:{service['port']} - {service['service']}")
    
    # 7. 建筑网络分析
    print("\n" + "=" * 70)
    print("建筑网络分析")
    print("=" * 70)
    
    if icmp_devices or internal_services:
        print("✅ 建筑内部网络连通性: 存在")
        print("   不同楼层/部门间可能存在内部路由")
        print("   建筑内部服务可能对内部网络开放")
        
        # 识别网络设备
        network_devices = [d for d in icmp_devices if '路由器' in d['type'] or '交换机' in d['type']]
        if network_devices:
            print(f"   发现 {len(network_devices)} 个网络设备")
    else:
        print("❌ 建筑内部网络连通性: 严格隔离")
        print("   不同楼层/部门间网络完全隔离")
        print("   需要其他方法进行跨楼层扫描")

def main():
    """主函数"""
    print("⚠️  此工具用于建筑内部网络管理和安全测试")
    print("   请在授权范围内使用！\n")
    
    confirm = input("是否开始建筑内部网络扫描？(y/N): ").lower()
    if confirm != 'y':
        print("扫描已取消")
        return
    
    start_time = time.time()
    building_network_scan()
    end_time = time.time()
    
    print(f"\n[+] 扫描完成，耗时: {end_time - start_time:.2f} 秒")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n扫描被用户中断")
    except Exception as e:
        print(f"\n[-] 扫描出错: {e}")