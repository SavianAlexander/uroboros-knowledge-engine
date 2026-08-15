# Windows Audio Diagnostic and Unmute Test Script
$wscript = New-Object -ComObject Wscript.Shell

# Unmute and turn volume up by sending Volume Up keystroke 25 times
for ($i = 0; $i -lt 25; $i++) {
    $wscript.SendKeys([char]175)
}

# Play system chime
[System.Media.SystemSounds]::Asterisk.Play()
[System.Media.SystemSounds]::Exclamation.Play()

# Play WAV file via Media.SoundPlayer
$wavPath = "$PSScriptRoot\..\vault\audio_showcase\1_AURA_SHIP_AI.wav"
if (Test-Path $wavPath) {
    $player = New-Object System.Media.SoundPlayer($wavPath)
    $player.PlaySync()
}

# Launch in Windows Media Player explicitly
Start-Process "wmplayer.exe" -ArgumentList "/play `"$wavPath`""
