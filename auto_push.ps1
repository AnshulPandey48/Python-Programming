cd "D:\aiml\Python Programming"
while ($true) {
    git add .
    $time = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    git commit -m "Auto-update at $time" --allow-empty
    git push origin main
    Start-Sleep -Seconds 300   # wait 5 minutes
}
