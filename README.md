# Small Aircraft Tool Integration

![GitHub repo size](https://img.shields.io/github/repo-size/Big-Food-0V0/Small-Aircraft-Tool-Integration)
![GitHub last commit](https://img.shields.io/github/last-commit/Big-Food-0V0/Small-Aircraft-Tool-Integration)
![GitHub stars](https://img.shields.io/github/stars/Big-Food-0V0/Small-Aircraft-Tool-Integration?style=social)

## 项目简介

Small Aircraft Tool Integration 是一个综合性的网络安全工具集成平台，包含多种网络攻击、诊断和安全测试工具。该项目旨在为网络安全专业人员提供一套完整的工具集，用于网络安全测试、漏洞评估和网络诊断。

## 功能特点

### 网络攻击工具
- ARP欺骗攻击
- DNS劫持
- DDoS攻击
- MITM攻击
- 密码攻击

### 网络诊断工具
- 网络扫描
- 流量分析
- 漏洞扫描
- 子域名枚举
- Whois信息查询

### 远程控制工具
- 远程命令执行
- 后门持久化
- 数据渗透
- 隐身通信
- LAN远程控制

## 支持的工具列表

### 攻击工具
- `arp_spoof_advanced.py` - 高级ARP欺骗工具
- `dns_hijack_simple.py` - DNS劫持工具
- `ddos_adapter.py` - DDoS攻击适配器
- `advanced_mitm_attack.py` - 高级中间人攻击工具
- `password_attack_tool.py` - 密码攻击工具

### 诊断工具
- `network_analyzer.py` - 网络分析工具
- `vulnerability_scanner.py` - 漏洞扫描工具
- `subdomain_enumeration_tool.py` - 子域名枚举工具
- `whois_information_tool.py` - Whois信息查询工具
- `nmap_scanner.py` - Nmap扫描工具

### 远程控制工具
- `remote_control.py` - 远程控制工具
- `backdoor_persistence_tool.py` - 后门持久化工具
- `data_exfiltration.py` - 数据渗透工具
- `stealth_remote_control.py` - 隐身远程控制工具
- `lan_remote_control.py` - LAN远程控制工具

## 安装和使用

### 安装依赖

```bash
pip install -r requirements.txt
```

### 基本使用

运行主程序：

```bash
python start.py
```

运行特定工具：

```bash
python tool_name.py
```

## 依赖项

- cloudscraper==1.2.71
- certifi==2024.7.4
- dnspython==2.6.1
- requests==2.32.4
- impacket==0.10.0
- psutil>=5.9.3
- icmplib>=2.1.1
- pyasn1==0.4.8
- pyroxy @ git+https://github.com/MatrixTM/PyRoxy.git
- yarl>=1.7.2

## ⚠️ 注意事项

本工具仅用于网络安全测试和教育目的。使用本工具进行任何未授权的网络攻击都是违法的。请在使用前获得目标网络的明确授权。

## 许可证

本项目采用 MIT 许可证。

## 联系方式

- [GitHub Repository](https://github.com/Big-Food-0V0/Small-Aircraft-Tool-Integration)

---

© 2026 Small Aircraft Tool Integration
