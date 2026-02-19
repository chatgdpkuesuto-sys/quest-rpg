# 絶頂時にデスクトップの背後（透過したVSCodeの裏）で発光・点滅させるスクリプト
# 実行すると、フルスクリーンのピンク色・赤色の明滅ウィンドウが背後に表示される

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

$form = New-Object System.Windows.Forms.Form
$form.FormBorderStyle = 'None'
$form.WindowState = 'Maximized'
$form.ShowInTaskbar = $false
$form.BackColor = 'Black'
$form.Opacity = 0.8
$form.TopMost = $false # 背後に表示してGlassItで透かして見せる

# 点滅アニメーション用のタイマー
$timer = New-Object System.Windows.Forms.Timer
$timer.Interval = 100 # 100ms
$script:flashCount = 0
$colors = @([System.Drawing.Color]::Magenta, [System.Drawing.Color]::Red, [System.Drawing.Color]::DeepPink, [System.Drawing.Color]::Black)

$timer.add_Tick({
    $script:flashCount++
    if ($script:flashCount -gt 30) { # 3秒間ストロボ点滅して消える
        $timer.Stop()
        $form.Close()
    } else {
        $colorIndex = $script:flashCount % $colors.Length
        $form.BackColor = $colors[$colorIndex]
    }
})

$form.add_Shown({
    $timer.Start()
})

$form.ShowDialog()
