#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
授权内部网络扫描工具 - 基于合作和授权
只有在获得授权的情况下才能有效使用
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

def check_authorization():
    """检查授权状态"""
    print("=" * 70)
    print("        授权内部网络扫描工具")
    print("        仅在获得授权的情况下使用")
    print("=" * 70)
    
    print("\n⚠️  重要法律声明：")
    print("1. 未经授权扫描他人网络属于违法行为")
    print("2. 可能导致法律后果和纪律处分")
    print("3. 仅限授权测试环境使用")
    
    print("\n✅ 合法使用场景：")
    print("1. 获得网络管理员书面授权")
    print("2. 获得目标设备所有者明确同意") 
    print("3. 在授权的测试环境中")
    print("4. 用于网络管理和安全评估")
    
    authorization = input("\n您是否已获得正式授权？(yes/NO): ").lower().strip()
    
    if authorization != 'yes':
        print("\n❌ 扫描终止：未获得授权")
        print("请先获得正式授权后再使用此工具")
        return False
    
    target_owner = input("请输入授权人姓名/部门: ").strip()
    authorization_id = input("请输入授权编号(如有): ").strip()
    
    print(f"\n✅ 授权确认：{target_owner}")
    if authorization_id:
        print(f"   授权编号：{authorization_id}")
    
    return True

def cooperative_scan_scenarios():
    """合作扫描场景指南"""
    print("\n" + "=" * 70)
    print("合作扫描技术方案")
    print("=" * 70)
    
    print("\n📋 方案1：获得楼上同事合作")
    print("   1. 与楼上同事沟通，获得扫描授权")
    print("   2. 在他们的设备上运行内部扫描工具")
    print("   3. 从网络内部发现其他设备")
    
    print("\n📋 方案2：网络管理员协助")
    print("   1. 获得网络管理部门的正式授权")
    print("   2. 使用网络管理权限进行扫描")
    print("   3. 从核心交换机获取设备信息")
    
    print("\n📋 方案3：物理接入合作")
    print("   1. 获得物理接入楼上网络的权限")
    print("   2. 直接连接到楼上网络交换机")
    print("   3. 从内部进行网络发现")
    
    choice = input("\n请选择合作方案 (1/2/3): ").strip()
    return choice

def internal_scan_from_cooperative_device():
    """从合作设备进行内部扫描"""
    print("\n" + "=" * 70)
    print("内部网络扫描（从合作设备）")
    print("=" * 70)
    
    # 获取网络信息
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        
        print(f"[+] 合作设备IP: {local_ip}")
        
        # 分析当前网络段
        ip_parts = local_ip.split('.')
        network_base = f"{ip_parts[0]}.{ip_parts[1]}.{ip_parts[2]}"
        
        print(f"[+] 网络段: {network_base}.0/24")
        
        # 内部ARP扫描
        print("[+] 执行内部ARP发现...")
        code, stdout, stderr = run_command("arp -a")
        
        if code == 0:
            devices_found = 0
            for line in stdout.split('\n'):
                if "动态" in line or "dynamic" in line.lower():
                    parts = line.split()
                    if len(parts) >= 2 and parts[0].count('.') == 3:
                        devices_found += 1
                        print(f"    📱 {parts[0]} - {parts[1]}")
            
            print(f"[+] 发现 {devices_found} 个本地网络设备")
        
        # 内部端口扫描
        print("\n[+] 执行内部服务发现...")
        common_services = [21, 22, 23, 53, 80, 135, 139, 443, 445, 3389]
        
        def scan_local_service(port):
            try:
                # 扫描本地网络常见服务
                for i in range(1, 255):
                    target_ip = f"{network_base}.{i}"
                    
                    # 跳过本机和广播地址
                    if i == int(ip_parts[3]) or i in [0, 255]:
                        continue
                    
                    try:
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.settimeout(1)
                        result = sock.connect_ex((target_ip, port))
                        sock.close()
                        
                        if result == 0:
                            service_name = get_service_name(port)
                            print(f"    🔍 {target_ip}:{port} - {service_name}")
                            return target_ip, port
                    except:
                        pass
            except:
                pass
            return None
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            list(executor.map(scan_local_service, common_services))
        
        return True
        
    except Exception as e:
        print(f"[-] 内部扫描失败: {e}")
        return False

def get_service_name(port):
    """获取服务名称"""
    services = {
        21: "FTP", 22: "SSH", 23: "Telnet", 53: "DNS",
        80: "HTTP", 135: "RPC", 139: "NetBIOS", 443: "HTTPS",
        445: "SMB", 3389: "RDP"
    }
    return services.get(port, "未知")

def network_admin_scan():
    """网络管理员级别扫描"""
    print("\n" + "=" * 70)
    print("网络管理员级别扫描")
    print("=" * 70)
    
    print("📋 管理员可用的高级技术：")
    print("1. 交换机MAC地址表查询")
    print("2. DHCP服务器租约信息")
    print("3. 网络流量监控分析")
    print("4. 防火墙日志分析")
    print("5. 无线控制器客户端列表")
    
    print("\n⚠️  需要网络设备管理权限")
    print("⚠️  需要专业网络管理知识")
    
    return True

def generate_cooperation_agreement():
    """生成合作授权协议模板"""
    print("\n" + "=" * 70)
    print("合作授权协议模板")
    print("=" * 70)
    
    agreement = """
网络扫描合作授权协议

授权方：___________________（部门/个人）
被授权方：___________________（部门/个人）
授权日期：___________________
授权期限：___________________

授权范围：
□ 内部网络设备发现
□ 网络服务扫描  
□ 安全漏洞评估
□ 网络性能测试

授权条件：
1. 仅限于授权范围内的测试活动
2. 不得对业务系统造成影响
3. 测试结果仅用于安全改进
4. 遵守相关法律法规

双方签字：
授权方：______________    被授权方：______________
"""
    
    print(agreement)

def main():
    """主函数"""
    
    # 1. 检查授权
    if not check_authorization():
        return
    
    # 2. 选择合作方案
    scenario = cooperative_scan_scenarios()
    
    if scenario == '1':
        # 同事合作方案
        print("\n🎯 执行同事合作扫描方案")
        success = internal_scan_from_cooperative_device()
        
        if success:
            print("\n✅ 合作扫描完成")
            generate_cooperation_agreement()
        else:
            print("\n❌ 扫描遇到问题")
    
    elif scenario == '2':
        # 管理员协助方案
        print("\n🎯 执行管理员协助方案")
        network_admin_scan()
        print("\n📞 请联系网络管理部门获得进一步支持")
    
    elif scenario == '3':
        # 物理接入方案
        print("\n🎯 执行物理接入方案")
        print("📋 需要以下准备工作：")
        print("1. 获得楼上网络机房的访问权限")
        print("2. 准备网络测试设备")
        print("3. 获得相关部门的批准")
        print("\n🔧 技术实施需要专业网络工程师")
    
    else:
        print("\n❌ 无效的选择")
    
    print("\n" + "=" * 70)
    print("扫描工具使用完成")
    print("=" * 70)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n操作被用户中断")
    except Exception as e:
        print(f"\n[-] 程序出错: {e}")