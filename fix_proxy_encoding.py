#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
代理文件编码修复工具
解决MHDDoS读取代理文件时的编码错误
"""

import os
import chardet

def detect_file_encoding(file_path):
    """检测文件编码"""
    with open(file_path, 'rb') as f:
        raw_data = f.read()
        result = chardet.detect(raw_data)
        return result['encoding'], result['confidence']

def fix_proxy_file_encoding(file_path):
    """修复代理文件编码"""
    print(f"🔧 修复文件编码: {file_path}")
    
    try:
        # 检测当前编码
        encoding, confidence = detect_file_encoding(file_path)
        print(f"📊 检测到编码: {encoding} (置信度: {confidence:.2f})")
        
        # 读取文件内容
        with open(file_path, 'r', encoding=encoding if encoding else 'utf-8') as f:
            content = f.read()
        
        # 清理内容：移除中文字符和注释
        lines = content.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            # 跳过空行和注释行
            if not line or line.startswith('#'):
                continue
            # 只保留有效的代理格式
            if '://' in line and ':' in line:
                cleaned_lines.append(line)
        
        # 重新写入为纯ASCII格式
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('# Clean proxy list\n')
            f.write('# Fixed encoding for MHDDoS\n\n')
            for line in cleaned_lines:
                f.write(line + '\n')
        
        print(f"✅ 文件修复完成，保留 {len(cleaned_lines)} 个代理")
        return True
        
    except Exception as e:
        print(f"❌ 修复失败: {e}")
        return False

def create_simple_proxy_file(file_path):
    """创建简单的代理文件（备用方案）"""
    print(f"📝 创建简单代理文件: {file_path}")
    
    # 使用已知可用的代理
    simple_proxies = [
        'http://51.158.68.68:8811',
        'http://51.158.68.133:8811',
        'http://138.68.161.14:3128',
        'http://167.99.123.158:3128',
        'http://8.130.37.235:1081',
        'socks5://47.252.18.37:5060',
        'socks5://192.111.137.37:18762',
        'socks5://47.251.87.199:8081',
        'http://103.48.71.194:83',
        'http://121.43.109.88:80'
    ]
    
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('# Simple proxy list for MHDDoS\n')
            f.write('# UTF-8 encoded, no Chinese characters\n\n')
            for proxy in simple_proxies:
                f.write(proxy + '\n')
        
        print(f"✅ 创建成功，包含 {len(simple_proxies)} 个代理")
        return True
        
    except Exception as e:
        print(f"❌ 创建失败: {e}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("🔧 MHDDoS代理文件编码修复工具")
    print("=" * 60)
    
    # 需要修复的代理文件
    proxy_files = [
        'files/proxies/proxies.txt',
        'files/proxies/http.txt',
        'files/proxies/files/proxies/http.txt'
    ]
    
    for file_path in proxy_files:
        if os.path.exists(file_path):
            print(f"\n📁 处理文件: {file_path}")
            
            # 先尝试修复
            if not fix_proxy_file_encoding(file_path):
                # 如果修复失败，创建新文件
                print("🔄 修复失败，尝试创建新文件...")
                create_simple_proxy_file(file_path)
        else:
            print(f"\n📁 文件不存在: {file_path}")
            print("🔄 创建新文件...")
            create_simple_proxy_file(file_path)
    
    print("\n" + "=" * 60)
    print("🎉 代理文件修复完成！")
    print("💡 现在可以正常使用代理进行DDoS攻击了")
    print("=" * 60)

if __name__ == "__main__":
    main()