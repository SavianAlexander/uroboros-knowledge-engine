Add-Type @"
  using System;
  using System.Runtime.InteropServices;
  public class Win32Helper {
    [DllImport("user32.dll")]
    public static extern bool SetForegroundWindow(IntPtr hWnd);
    [DllImport("user32.dll")]
    public static extern bool ShowWindowAsync(IntPtr hWnd, int nCmdShow);
  }
"@

$desktopProcs = Get-Process -Name "Docker Desktop" -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowHandle -ne [IntPtr]::Zero }
if ($desktopProcs) {
    foreach ($p in $desktopProcs) {
        [Win32Helper]::ShowWindowAsync($p.MainWindowHandle, 9) | Out-Null
        [Win32Helper]::SetForegroundWindow($p.MainWindowHandle) | Out-Null
    }
    Write-Host "Docker Desktop window restored to foreground."
} else {
    Start-Process "C:\Users\Administrator\AppData\Local\Programs\DockerDesktop\Docker Desktop.exe"
    Write-Host "Docker Desktop launched."
}

# Open the running Uroboros Knowledge Engine in the browser
Start-Process "http://localhost:80"
Write-Host "Opened Uroboros Knowledge Engine at http://localhost:80"
