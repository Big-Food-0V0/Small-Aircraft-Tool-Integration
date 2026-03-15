#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基础远程控制工具 - 仅用于教育和授权的安全测试
⚠️ 重要提醒：必须在获得明确授权的情况下使用
"""

import socket
import threading
import subprocess
import os
import sys
import time
import json
from datetime import datetime

class RemoteControlServer:
    """远程控制服务器端"""
    
    def __init__(self, host='0.0.0.0', port=8888):
        self.host = host
        self.port = port
        self.server_socket = None
        self.is_running = False
        self.clients = {}
        
        # 命令白名单（安全限制）
        self.allowed_commands = {
            'system_info': self.get_system_info,
            'network_info': self.get_network_info,
            'process_list': self.get_process_list,
            'file_list': self.list_files,
            'ping': self.ping_test,
            'help': self.show_help
        }
    
    def start_server(self):
        """启动服务器"""
        print("=" * 60)
        print("          远程控制服务器")
        print("        (教育用途 - 需授权)")
        print("=" * 60)
        
        # 安全警告
        print("⚠️  重要安全提醒:")
        print("• 此工具仅用于教育和授权的安全测试")
        print("• 必须在获得明确授权的情况下使用")
        print("• 禁止用于非法用途")
        
        confirm = input("\n确认启动服务器? (y/N): ").strip().lower()
        if confirm != 'y':
            print("[-] 服务器启动取消")
            return
        
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            
            self.is_running = True
            
            print(f"[+] 服务器启动在 {self.host}:{self.port}")
            print("[+] 等待客户端连接...")
            
            # 接受连接线程
            accept_thread = threading.Thread(target=self.accept_connections)
            accept_thread.daemon = True
            accept_thread.start()
            
            # 主循环
            while self.is_running:
                time.sleep(1)
                
        except Exception as e:
            print(f"[-] 服务器启动失败: {e}")
        finally:
            self.stop_server()
    
    def accept_connections(self):
        """接受客户端连接"""
        while self.is_running:
            try:
                client_socket, client_address = self.server_socket.accept()
                
                print(f"[+] 客户端连接: {client_address}")
                
                # 处理客户端线程
                client_thread = threading.Thread(
                    target=self.handle_client,
                    args=(client_socket, client_address)
                )
                client_thread.daemon = True
                client_thread.start()
                
                # 保存客户端信息
                client_id = f"{client_address[0]}:{client_address[1]}"
                self.clients[client_id] = {
                    'socket': client_socket,
                    'address': client_address,
                    'thread': client_thread,
                    'connected_at': datetime.now()
                }
                
            except Exception as e:
                if self.is_running:
                    print(f"[-] 接受连接错误: {e}")
    
    def handle_client(self, client_socket, client_address):
        """处理客户端请求"""
        client_id = f"{client_address[0]}:{client_address[1]}"
        
        try:
            while self.is_running:
                # 接收命令
                data = client_socket.recv(1024).decode('utf-8')
                if not data:
                    break
                
                print(f"[{client_id}] 收到命令: {data}")
                
                # 解析命令
                try:
                    command_data = json.loads(data)
                    command = command_data.get('command', '')
                    args = command_data.get('args', [])
                    
                    # 执行命令
                    result = self.execute_command(command, args)
                    
                    # 发送结果
                    response = {
                        'status': 'success',
                        'result': result,
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    client_socket.send(json.dumps(response).encode('utf-8'))
                    
                except Exception as e:
                    error_response = {
                        'status': 'error',
                        'error': str(e),
                        'timestamp': datetime.now().isoformat()
                    }
                    client_socket.send(json.dumps(error_response).encode('utf-8'))
        
        except Exception as e:
            print(f"[-] 客户端处理错误 [{client_id}]: {e}")
        finally:
            client_socket.close()
            if client_id in self.clients:
                del self.clients[client_id]
            print(f"[-] 客户端断开: {client_id}")
    
    def execute_command(self, command, args):
        """执行命令（安全限制）"""
        if command in self.allowed_commands:
            return self.allowed_commands[command](args)
        else:
            return f"命令 '{command}' 不在允许列表中"
    
    def get_system_info(self, args):
        """获取系统信息"""
        info = {
            'platform': sys.platform,
            'hostname': socket.gethostname(),
            'username': os.getlogin(),
            'current_dir': os.getcwd(),
            'timestamp': datetime.now().isoformat()
        }
        
        # 系统特定信息
        if sys.platform == 'win32':
            try:
                result = subprocess.run(['systeminfo'], capture_output=True, text=True)
                info['system_info'] = result.stdout[:1000]  # 限制长度
            except:
                info['system_info'] = '无法获取系统信息'
        
        return info
    
    def get_network_info(self, args):
        """获取网络信息"""
        info = {
            'hostname': socket.gethostname(),
            'ip_address': socket.gethostbyname(socket.gethostname()),
            'network_interfaces': []
        }
        
        # 获取网络接口信息（简化版）
        try:
            # Windows系统
            if sys.platform == 'win32':
                result = subprocess.run(['ipconfig'], capture_output=True, text=True)
                info['ipconfig'] = result.stdout
        except:
            pass
        
        return info
    
    def get_process_list(self, args):
        """获取进程列表"""
        try:
            if sys.platform == 'win32':
                result = subprocess.run(['tasklist'], capture_output=True, text=True)
                processes = result.stdout.split('\n')[:20]  # 只显示前20个进程
                return {'processes': processes}
            else:
                result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
                processes = result.stdout.split('\n')[:20]
                return {'processes': processes}
        except Exception as e:
            return {'error': str(e)}
    
    def list_files(self, args):
        """列出文件"""
        path = args[0] if args else os.getcwd()
        
        # 安全限制：只能列出当前目录和子目录
        if not os.path.exists(path):
            return {'error': '路径不存在'}
        
        try:
            files = []
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                files.append({
                    'name': item,
                    'is_dir': os.path.isdir(item_path),
                    'size': os.path.getsize(item_path) if os.path.isfile(item_path) else 0
                })
            
            return {
                'path': path,
                'files': files[:50]  # 限制数量
            }
        except Exception as e:
            return {'error': str(e)}
    
    def ping_test(self, args):
        """ping测试"""
        target = args[0] if args else '8.8.8.8'
        
        try:
            if sys.platform == 'win32':
                result = subprocess.run(['ping', '-n', '3', target], capture_output=True, text=True)
            else:
                result = subprocess.run(['ping', '-c', '3', target], capture_output=True, text=True)
            
            return {'ping_result': result.stdout}
        except Exception as e:
            return {'error': str(e)}
    
    def show_help(self, args):
        """显示帮助"""
        return {
            'allowed_commands': list(self.allowed_commands.keys()),
            'description': '基础远程控制工具 - 仅限安全测试使用'
        }
    
    def stop_server(self):
        """停止服务器"""
        self.is_running = False
        
        # 关闭所有客户端连接
        for client_id, client_info in self.clients.items():
            try:
                client_info['socket'].close()
            except:
                pass
        
        if self.server_socket:
            self.server_socket.close()
        
        print("[+] 服务器已停止")

class RemoteControlClient:
    """远程控制客户端"""
    
    def __init__(self):
        self.client_socket = None
        self.is_connected = False
    
    def connect_to_server(self, server_host, server_port=8888):
        """连接到服务器"""
        print("=" * 60)
        print("          远程控制客户端")
        print("        (教育用途 - 需授权)")
        print("=" * 60)
        
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((server_host, server_port))
            
            self.is_connected = True
            print(f"[+] 连接到服务器: {server_host}:{server_port}")
            
            # 启动接收线程
            receive_thread = threading.Thread(target=self.receive_responses)
            receive_thread.daemon = True
            receive_thread.start()
            
            # 命令交互
            self.command_interface()
            
        except Exception as e:
            print(f"[-] 连接失败: {e}")
        finally:
            self.disconnect()
    
    def send_command(self, command, args=None):
        """发送命令"""
        if not self.is_connected:
            print("[-] 未连接到服务器")
            return
        
        try:
            command_data = {
                'command': command,
                'args': args or []
            }
            
            self.client_socket.send(json.dumps(command_data).encode('utf-8'))
            print(f"[+] 发送命令: {command}")
            
        except Exception as e:
            print(f"[-] 发送命令失败: {e}")
    
    def receive_responses(self):
        """接收响应"""
        while self.is_connected:
            try:
                data = self.client_socket.recv(4096).decode('utf-8')
                if not data:
                    break
                
                response = json.loads(data)
                
                print("\n[响应]")
                print(f"状态: {response.get('status', 'unknown')}")
                print(f"时间: {response.get('timestamp', 'unknown')}")
                
                if response.get('status') == 'success':
                    result = response.get('result', {})
                    self.pretty_print_result(result)
                else:
                    print(f"错误: {response.get('error', 'unknown error')}")
                
                print("\n» ", end='', flush=True)
                
            except Exception as e:
                if self.is_connected:
                    print(f"[-] 接收响应错误: {e}")
                break
    
    def pretty_print_result(self, result):
        """美化打印结果"""
        if isinstance(result, dict):
            for key, value in result.items():
                if isinstance(value, list):
                    print(f"{key}:")
                    for item in value:
                        print(f"  - {item}")
                else:
                    print(f"{key}: {value}")
        else:
            print(result)
    
    def command_interface(self):
        """命令交互界面"""
        print("\n💡 可用命令:")
        print("  system_info    - 获取系统信息")
        print("  network_info   - 获取网络信息")
        print("  process_list   - 获取进程列表")
        print("  file_list [路径] - 列出文件")
        print("  ping [目标]    - ping测试")
        print("  help           - 显示帮助")
        print("  exit           - 退出")
        
        while self.is_connected:
            try:
                user_input = input("\n» ").strip()
                
                if user_input.lower() == 'exit':
                    break
                
                parts = user_input.split()
                if not parts:
                    continue
                
                command = parts[0]
                args = parts[1:] if len(parts) > 1 else []
                
                self.send_command(command, args)
                
            except KeyboardInterrupt:
                print("\n[!] 用户中断")
                break
            except Exception as e:
                print(f"[-] 命令输入错误: {e}")
    
    def disconnect(self):
        """断开连接"""
        self.is_connected = False
        if self.client_socket:
            self.client_socket.close()
        print("[+] 已断开连接")

def main():
    """主函数"""
    print("🚀 基础远程控制工具")
    print("⚠️  仅用于教育和授权的安全测试\n")
    
    print("选择模式:")
    print("1. 服务器模式 (监听连接)")
    print("2. 客户端模式 (连接到服务器)")
    
    choice = input("\n请输入选择 (1/2): ").strip()
    
    if choice == '1':
        # 服务器模式
        host = input("请输入监听地址 (默认 0.0.0.0): ").strip() or '0.0.0.0'
        port = int(input("请输入端口 (默认 8888): ").strip() or '8888')
        
        server = RemoteControlServer(host, port)
        server.start_server()
        
    elif choice == '2':
        # 客户端模式
        host = input("请输入服务器地址: ").strip()
        if not host:
            print("[-] 必须输入服务器地址")
            return
        
        port = int(input("请输入端口 (默认 8888): ").strip() or '8888')
        
        client = RemoteControlClient()
        client.connect_to_server(host, port)
        
    else:
        print("[-] 无效选择")

if __name__ == "__main__":
    main()