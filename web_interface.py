#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Web界面版本 - 支持手机访问的渗透测试平台
"""

from flask import Flask, render_template, request, jsonify, send_file
import threading
import subprocess
import os
import json
import time
from datetime import datetime
import socket
from tool_adapter import ToolAdapter

app = Flask(__name__)

# 工具执行状态
active_processes = {}
log_messages = []

# 工具适配器
adapter = ToolAdapter()

# 工具配置
TOOL_CONFIG = {
    "web_attack": {
        "name": "🌐 Web攻击平台",
        "command": "python automated_web_attack_platform.py",
        "description": "自动化Web应用安全测试和攻击",
        "category": "web"
    },
    "subdomain_scan": {
        "name": "🔍 子域名枚举",
        "command": "python subdomain_enumeration_tool.py",
        "description": "自动发现目标域名的所有子域名",
        "category": "recon"
    },
    "whois_query": {
        "name": "📋 WHOIS查询",
        "command": "python whois_information_tool.py",
        "description": "获取域名注册信息和所有者信息",
        "category": "recon"
    },
    "file_upload_exploit": {
        "name": "📁 文件上传漏洞",
        "command": "python file_upload_exploit_tool.py",
        "description": "文件上传功能漏洞利用和绕过",
        "category": "web"
    },
    "android_attack": {
        "name": "📱 Android攻击",
        "command": "python android_attack_toolkit.py",
        "description": "Android设备攻击工具包",
        "category": "mobile"
    },
    "ios_attack": {
        "name": "📱 iOS攻击",
        "command": "python ios_attack_toolkit.py",
        "description": "iOS设备攻击工具包",
        "category": "mobile"
    },
    "nmap_scan": {
        "name": "🔍 端口扫描",
        "command": "python nmap_scanner.py",
        "description": "专业端口扫描和服务识别",
        "category": "network"
    },
    "vulnerability_scan": {
        "name": "🛡️ 漏洞扫描",
        "command": "python vulnerability_scanner.py",
        "description": "系统漏洞扫描和安全评估",
        "category": "web"
    },
    "password_attack": {
        "name": "🔑 密码攻击",
        "command": "python password_attack_tool.py",
        "description": "密码破解和暴力攻击",
        "category": "web"
    },
    "wireless_attack": {
        "name": "📶 无线攻击",
        "command": "python wireless_attack_tool.py",
        "description": "无线网络攻击和破解",
        "category": "network"
    }
}

def get_local_ip():
    """获取本机IP地址"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def add_log(message, level="info"):
    """添加日志"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    log_entry = {
        "timestamp": timestamp,
        "message": message,
        "level": level
    }
    log_messages.append(log_entry)
    
    # 限制日志数量
    if len(log_messages) > 1000:
        log_messages.pop(0)

@app.route('/')
def index():
    """主页面"""
    local_ip = get_local_ip()
    return f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>渗透测试Web平台</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: #333;
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        .header {{
            background: rgba(255, 255, 255, 0.95);
            padding: 30px;
            border-radius: 15px;
            margin-bottom: 20px;
            text-align: center;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }}
        
        .header h1 {{
            color: #2c3e50;
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        .header p {{
            color: #7f8c8d;
            font-size: 1.1em;
        }}
        
        .main-content {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }}
        
        @media (max-width: 768px) {{
            .main-content {{
                grid-template-columns: 1fr;
            }}
        }}
        
        .panel {{
            background: rgba(255, 255, 255, 0.95);
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }}
        
        .panel h2 {{
            color: #2c3e50;
            margin-bottom: 20px;
            font-size: 1.5em;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
        }}
        
        .tool-category {{
            margin-bottom: 25px;
        }}
        
        .tool-category h3 {{
            color: #34495e;
            margin-bottom: 15px;
            font-size: 1.2em;
        }}
        
        .tool-item {{
            background: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 10px;
            cursor: pointer;
            transition: all 0.3s ease;
        }}
        
        .tool-item:hover {{
            background: #e3f2fd;
            border-color: #3498db;
            transform: translateY(-2px);
        }}
        
        .tool-item.active {{
            background: #d4edda;
            border-color: #28a745;
        }}
        
        .tool-name {{
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 5px;
        }}
        
        .tool-desc {{
            color: #6c757d;
            font-size: 0.9em;
        }}
        
        .input-group {{
            margin-bottom: 20px;
        }}
        
        .input-group label {{
            display: block;
            margin-bottom: 8px;
            font-weight: bold;
            color: #495057;
        }}
        
        .input-group input {{
            width: 100%;
            padding: 12px;
            border: 1px solid #ced4da;
            border-radius: 6px;
            font-size: 16px;
        }}
        
        .button-group {{
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }}
        
        .button {{
            padding: 12px 24px;
            border: none;
            border-radius: 6px;
            font-size: 16px;
            cursor: pointer;
            transition: all 0.3s ease;
            flex: 1;
            min-width: 120px;
        }}
        
        .button.primary {{
            background: #3498db;
            color: white;
        }}
        
        .button.primary:hover {{
            background: #2980b9;
        }}
        
        .button.danger {{
            background: #e74c3c;
            color: white;
        }}
        
        .button.danger:hover {{
            background: #c0392b;
        }}
        
        .button.secondary {{
            background: #95a5a6;
            color: white;
        }}
        
        .button.secondary:hover {{
            background: #7f8c8d;
        }}
        
        .log-container {{
            height: 300px;
            overflow-y: auto;
            background: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 6px;
            padding: 15px;
            margin-bottom: 15px;
            font-family: 'Courier New', monospace;
            font-size: 14px;
        }}
        
        .log-entry {{
            margin-bottom: 5px;
            padding: 3px 0;
        }}
        
        .log-success {{
            color: #28a745;
        }}
        
        .log-error {{
            color: #dc3545;
        }}
        
        .log-warning {{
            color: #ffc107;
        }}
        
        .log-info {{
            color: #17a2b8;
        }}
        
        .log-timestamp {{
            color: #888;
        }}
        
        .status-bar {{
            background: #34495e;
            color: white;
            padding: 10px;
            text-align: center;
            font-weight: bold;
        }}
        
        .progress-bar {{
            height: 4px;
            background: #2c3e50;
            border-radius: 2px;
            margin-top: 5px;
            overflow: hidden;
        }}
        
        .progress {{
            height: 100%;
            background: #3498db;
            width: 0%;
            transition: width 0.3s ease;
        }}
        
        .progress.active {{
            animation: progress 2s infinite;
        }}
        
        @keyframes progress {{
            0% {{ transform: translateX(-100%); }}
            100% {{ transform: translateX(400%); }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔧 渗透测试Web平台</h1>
            <p>手机友好界面 - 访问地址: http://{local_ip}:5000</p>
        </div>
        
        <div class="main-content">
            <!-- 左侧工具面板 -->
            <div class="panel">
                <h2>🛠️ 工具选择</h2>
                
                <div class="tool-category">
                    <h3>🌐 Web攻击</h3>
                    <div class="tool-item" onclick="selectTool('web_attack')">
                        <div class="tool-name">Web攻击平台</div>
                        <div class="tool-desc">自动化Web应用安全测试和攻击</div>
                    </div>
                    <div class="tool-item" onclick="selectTool('file_upload_exploit')">
                        <div class="tool-name">文件上传漏洞</div>
                        <div class="tool-desc">文件上传功能漏洞利用和绕过</div>
                    </div>
                </div>
                
                <div class="tool-category">
                    <h3>🔍 信息收集</h3>
                    <div class="tool-item" onclick="selectTool('subdomain_scan')">
                        <div class="tool-name">子域名枚举</div>
                        <div class="tool-desc">自动发现目标域名的所有子域名</div>
                    </div>
                    <div class="tool-item" onclick="selectTool('whois_query')">
                        <div class="tool-name">WHOIS查询</div>
                        <div class="tool-desc">获取域名注册信息和所有者信息</div>
                    </div>
                </div>
                
                <div class="tool-category">
                    <h3>📱 移动设备</h3>
                    <div class="tool-item" onclick="selectTool('android_attack')">
                        <div class="tool-name">Android攻击</div>
                        <div class="tool-desc">Android设备攻击工具包</div>
                    </div>
                    <div class="tool-item" onclick="selectTool('ios_attack')">
                        <div class="tool-name">iOS攻击</div>
                        <div class="tool-desc">iOS设备攻击工具包</div>
                    </div>
                </div>
                
                <div class="tool-category">
                    <h3>🔧 网络工具</h3>
                    <div class="tool-item" onclick="selectTool('nmap_scan')">
                        <div class="tool-name">端口扫描</div>
                        <div class="tool-desc">专业端口扫描和服务识别</div>
                    </div>
                    <div class="tool-item" onclick="selectTool('wireless_attack')">
                        <div class="tool-name">无线攻击</div>
                        <div class="tool-desc">无线网络攻击和破解</div>
                    </div>
                </div>
                
                <div class="input-group">
                    <label for="target">🎯 目标地址</label>
                    <input type="text" id="target" placeholder="例如: example.com 或 192.168.1.1">
                </div>
                
                <div class="button-group">
                    <button class="button primary" onclick="startAttack()">🚀 启动攻击</button>
                    <button class="button danger" onclick="stopAttack()">🛑 停止攻击</button>
                </div>
            </div>
            
            <!-- 右侧日志面板 -->
            <div class="panel">
                <h2>📊 执行日志</h2>
                <div class="log-container" id="logContainer">
                    <div class="log-entry">
                        <span class="log-timestamp">[系统]</span> 欢迎使用渗透测试Web平台
                    </div>
                </div>
                
                <div class="button-group">
                    <button class="button secondary" onclick="clearLog()">🧹 清空日志</button>
                    <button class="button secondary" onclick="exportLog()">💾 导出日志</button>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        let selectedTool = null;
        
        function selectTool(toolId) {{
            // 移除所有激活状态
            document.querySelectorAll('.tool-item').forEach(item => {{
                item.classList.remove('active');
            }});
            
            // 设置当前工具为激活状态
            event.currentTarget.classList.add('active');
            selectedTool = toolId;
            
            addLog(`已选择工具: ${{TOOL_CONFIG[toolId].name}}`, 'info');
        }}
        
        function startAttack() {{
            const target = document.getElementById('target').value.trim();
            
            if (!selectedTool) {{
                addLog('请先选择一个工具', 'error');
                return;
            }}
            
            if (!target) {{
                addLog('请输入目标地址', 'error');
                return;
            }}
            
            addLog(`开始攻击: ${{TOOL_CONFIG[selectedTool].name}} - 目标: ${{target}}`, 'info');
            
            fetch('/start_attack', {{
                method: 'POST',
                headers: {{
                    'Content-Type': 'application/json',
                }},
                body: JSON.stringify({{ tool: selectedTool, target: target }})
            }})
            .then(response => response.json())
            .then(data => {{
                if (data.status === 'started') {{
                    addLog('攻击已启动', 'success');
                }} else {{
                    addLog('启动失败: ' + data.error, 'error');
                }}
            }})
            .catch(error => {{
                addLog('请求失败: ' + error, 'error');
            }});
        }}
        
        function stopAttack() {{
            fetch('/stop_attack', {{
                method: 'POST'
            }})
            .then(response => response.json())
            .then(data => {{
                if (data.status === 'stopped') {{
                    addLog('攻击已停止', 'warning');
                }} else {{
                    addLog('停止失败', 'error');
                }}
            }});
        }}
        
        function clearLog() {{
            document.getElementById('logContainer').innerHTML = 
                '<div class="log-entry"><span class="log-timestamp">[系统]</span> 日志已清空</div>';
        }}
        
        function exportLog() {{
            const logContent = document.getElementById('logContainer').innerText;
            const blob = new Blob([logContent], {{ type: 'text/plain' }});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'penetration_log_' + new Date().toISOString().replace(/[:.]/g, '-') + '.txt';
            a.click();
            URL.revokeObjectURL(url);
        }}
        
        function addLog(message, level = 'info') {{
            const timestamp = new Date().toLocaleTimeString();
            const logEntry = document.createElement('div');
            logEntry.className = 'log-entry';
            logEntry.innerHTML = `
                <span class="log-timestamp">[${{timestamp}}]</span>
                <span class="log-${{level}}">${{message}}</span>
            `;
            
            const container = document.getElementById('logContainer');
            container.appendChild(logEntry);
            container.scrollTop = container.scrollHeight;
        }}
        
        // 定期获取最新日志
        function updateLogs() {{
            fetch('/get_logs')
                .then(response => response.json())
                .then(logs => {{
                    // 这里可以添加日志更新逻辑
                }});
        }}
        
        // 每5秒更新一次日志
        setInterval(updateLogs, 5000);
        
        // 工具配置对象
        const TOOL_CONFIG = {json.dumps(TOOL_CONFIG, ensure_ascii=False)};
    </script>
</body>
</html>
"""

@app.route('/start_attack', methods=['POST'])
def start_attack():
    """启动攻击"""
    data = request.json
    tool_id = data.get('tool')
    target = data.get('target')
    
    if tool_id not in TOOL_CONFIG:
        return jsonify({'error': '无效的工具ID'}), 400
    
    if not target:
        return jsonify({'error': '目标地址不能为空'}), 400
    
    # 在后台执行工具
    def execute_tool():
        tool = TOOL_CONFIG[tool_id]
        add_log(f"启动工具: {tool['name']}", "info")
        
        try:
            # 使用工具适配器执行，避免交互式输入问题
            success, result = adapter.execute_tool_with_config(tool_id, target)
            
            if success:
                # 处理成功结果
                lines = result.split('\n')
                for line in lines:
                    if line.strip():
                        add_log(f"{tool['name']}: {line.strip()}", "info")
                add_log(f"✅ {tool['name']} 执行完成", "success")
            else:
                # 处理错误
                add_log(f"❌ 执行失败: {result}", "error")
                
        except Exception as e:
            add_log(f"❌ 执行异常: {e}", "error")
        finally:
            if tool_id in active_processes:
                del active_processes[tool_id]
    
    thread = threading.Thread(target=execute_tool)
    thread.daemon = True
    thread.start()
    
    return jsonify({'status': 'started', 'tool': tool_id})

@app.route('/stop_attack', methods=['POST'])
def stop_attack():
    """停止攻击"""
    for tool_id, process in active_processes.items():
        try:
            process.terminate()
            add_log(f"已停止: {tool_id}", "warning")
        except Exception as e:
            add_log(f"停止失败: {tool_id} - {e}", "error")
    
    active_processes.clear()
    return jsonify({'status': 'stopped'})

@app.route('/get_logs', methods=['GET'])
def get_logs():
    """获取日志"""
    return jsonify(log_messages)

if __name__ == '__main__':
    local_ip = get_local_ip()
    print(f"🌐 Web界面已启动")
    print(f"📱 手机访问地址: http://{local_ip}:5000")
    print(f"💻 本地访问地址: http://127.0.0.1:5000")
    print("🛑 按 Ctrl+C 停止服务")
    
    app.run(host='0.0.0.0', port=5000, debug=False)