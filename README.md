<style>
  :root {
    --primary-color: #3498db;
    --secondary-color: #2ecc71;
    --background-color: #f5f5f5;
    --text-color: #333;
    --card-bg: #ffffff;
    --card-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    --border-radius: 8px;
  }
  
  * {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
  }
  
  body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    line-height: 1.6;
    color: var(--text-color);
    background-color: var(--background-color);
    padding: 20px;
  }
  
  .container {
    max-width: 1200px;
    margin: 0 auto;
  }
  
  header {
    text-align: center;
    margin-bottom: 40px;
    padding: 30px;
    background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
    color: white;
    border-radius: var(--border-radius);
    box-shadow: var(--card-shadow);
  }
  
  h1 {
    font-size: 2.5rem;
    margin-bottom: 10px;
  }
  
  h2 {
    font-size: 1.8rem;
    margin: 30px 0 20px;
    color: var(--primary-color);
    border-bottom: 2px solid var(--primary-color);
    padding-bottom: 10px;
  }
  
  h3 {
    font-size: 1.4rem;
    margin: 20px 0 15px;
    color: var(--secondary-color);
  }
  
  .card {
    background-color: var(--card-bg);
    border-radius: var(--border-radius);
    padding: 20px;
    margin-bottom: 20px;
    box-shadow: var(--card-shadow);
  }
  
  .feature-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 20px;
    margin: 30px 0;
  }
  
  .feature-card {
    background-color: var(--card-bg);
    border-radius: var(--border-radius);
    padding: 20px;
    box-shadow: var(--card-shadow);
    transition: transform 0.3s ease;
  }
  
  .feature-card:hover {
    transform: translateY(-5px);
  }
  
  .feature-card h4 {
    color: var(--primary-color);
    margin-bottom: 10px;
  }
  
  code {
    background-color: #f1f1f1;
    padding: 2px 6px;
    border-radius: 4px;
    font-family: 'Courier New', Courier, monospace;
  }
  
  pre {
    background-color: #f1f1f1;
    padding: 15px;
    border-radius: var(--border-radius);
    overflow-x: auto;
    margin: 20px 0;
  }
  
  pre code {
    background: none;
    padding: 0;
  }
  
  ul {
    margin-left: 20px;
    margin-bottom: 20px;
  }
  
  li {
    margin-bottom: 8px;
  }
  
  .warning {
    background-color: #fff3cd;
    border: 1px solid #ffeaa7;
    border-radius: var(--border-radius);
    padding: 15px;
    margin: 20px 0;
    color: #856404;
  }
  
  .footer {
    text-align: center;
    margin-top: 50px;
    padding: 20px;
    background-color: var(--card-bg);
    border-radius: var(--border-radius);
    box-shadow: var(--card-shadow);
  }
  
  .social-links {
    display: flex;
    justify-content: center;
    gap: 20px;
    margin: 20px 0;
  }
  
  .social-links a {
    color: var(--primary-color);
    text-decoration: none;
    font-weight: bold;
  }
  
  .social-links a:hover {
    color: var(--secondary-color);
  }
</style>

<div class="container">
  <header>
    <h1>Small Aircraft Tool Integration</h1>
    <p>多功能网络安全工具集成平台</p>
  </header>

  <div class="card">
    <h2>项目简介</h2>
    <p>Small Aircraft Tool Integration 是一个综合性的网络安全工具集成平台，包含多种网络攻击、诊断和安全测试工具。该项目旨在为网络安全专业人员提供一套完整的工具集，用于网络安全测试、漏洞评估和网络诊断。</p>
  </div>

  <h2>功能特点</h2>
  <div class="feature-grid">
    <div class="feature-card">
      <h4>网络攻击工具</h4>
      <ul>
        <li>ARP欺骗攻击</li>
        <li>DNS劫持</li>
        <li>DDoS攻击</li>
        <li>MITM攻击</li>
        <li>密码攻击</li>
      </ul>
    </div>
    <div class="feature-card">
      <h4>网络诊断工具</h4>
      <ul>
        <li>网络扫描</li>
        <li>流量分析</li>
        <li>漏洞扫描</li>
        <li>子域名枚举</li>
        <li>Whois信息查询</li>
      </ul>
    </div>
    <div class="feature-card">
      <h4>远程控制工具</h4>
      <ul>
        <li>远程命令执行</li>
        <li>后门持久化</li>
        <li>数据渗透</li>
        <li>隐身通信</li>
        <li>LAN远程控制</li>
      </ul>
    </div>
  </div>

  <div class="card">
    <h2>支持的工具列表</h2>
    <h3>攻击工具</h3>
    <ul>
      <li><code>arp_spoof_advanced.py</code> - 高级ARP欺骗工具</li>
      <li><code>dns_hijack_simple.py</code> - DNS劫持工具</li>
      <li><code>ddos_adapter.py</code> - DDoS攻击适配器</li>
      <li><code>advanced_mitm_attack.py</code> - 高级中间人攻击工具</li>
      <li><code>password_attack_tool.py</code> - 密码攻击工具</li>
    </ul>

    <h3>诊断工具</h3>
    <ul>
      <li><code>network_analyzer.py</code> - 网络分析工具</li>
      <li><code>vulnerability_scanner.py</code> - 漏洞扫描工具</li>
      <li><code>subdomain_enumeration_tool.py</code> - 子域名枚举工具</li>
      <li><code>whois_information_tool.py</code> - Whois信息查询工具</li>
      <li><code>nmap_scanner.py</code> - Nmap扫描工具</li>
    </ul>

    <h3>远程控制工具</h3>
    <ul>
      <li><code>remote_control.py</code> - 远程控制工具</li>
      <li><code>backdoor_persistence_tool.py</code> - 后门持久化工具</li>
      <li><code>data_exfiltration.py</code> - 数据渗透工具</li>
      <li><code>stealth_remote_control.py</code> - 隐身远程控制工具</li>
      <li><code>lan_remote_control.py</code> - LAN远程控制工具</li>
    </ul>
  </div>

  <div class="card">
    <h2>安装和使用</h2>
    <h3>安装依赖</h3>
    <pre><code>pip install -r requirements.txt</code></pre>

    <h3>基本使用</h3>
    <p>运行主程序：</p>
    <pre><code>python start.py</code></pre>

    <p>运行特定工具：</p>
    <pre><code>python tool_name.py</code></pre>
  </div>

  <div class="card">
    <h2>依赖项</h2>
    <ul>
      <li>cloudscraper==1.2.71</li>
      <li>certifi==2024.7.4</li>
      <li>dnspython==2.6.1</li>
      <li>requests==2.32.4</li>
      <li>impacket==0.10.0</li>
      <li>psutil>=5.9.3</li>
      <li>icmplib>=2.1.1</li>
      <li>pyasn1==0.4.8</li>
      <li>pyroxy @ git+https://github.com/MatrixTM/PyRoxy.git</li>
      <li>yarl>=1.7.2</li>
    </ul>
  </div>

  <div class="warning">
    <h3>⚠️ 注意事项</h3>
    <p>本工具仅用于网络安全测试和教育目的。使用本工具进行任何未授权的网络攻击都是违法的。请在使用前获得目标网络的明确授权。</p>
  </div>

  <div class="card">
    <h2>许可证</h2>
    <p>本项目采用 MIT 许可证。</p>
  </div>

  <div class="footer">
    <h3>联系方式</h3>
    <div class="social-links">
      <a href="https://github.com/Big-Food-0V0/Small-Aircraft-Tool-Integration" target="_blank">GitHub</a>
    </div>
    <p>© 2026 Small Aircraft Tool Integration</p>
  </div>
</div>
