Write-Output "$(Get-Date) Gitlab Clean Up Script"
Set-Location "c:\"
$curPath = Get-Location

#Delete .git config
Get-ChildItem -path "c:\gitlab" -Directory -Recurse -Filter ".git" -Hidden | Remove-Item -Force -Recurse
Get-ChildItem -path "c:\gitlab" -Recurse -Filter ".gitignore" | Remove-Item -Force -Recurse
Get-ChildItem -path "c:\gitlab" -Recurse -Filter "README.md" | Remove-Item -Force -Recurse


#$versionInfo = @"
#v0.21 
#HOL 2501 CMP vPod 
#2024/08/16 
#"@

#If (Test-Path -Path "c:\hol\version.txt" ) {
#    Remove-Item "c:\hol\version.txt" -Force
#    New-Item "c:\hol\version.txt" -ItemType File -Value $versionInfo
#}
