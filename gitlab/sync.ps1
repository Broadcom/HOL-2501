Write-Output "$(Get-Date) Creating GitLab repos"
Set-Location "c:\"
$curPath = Get-Location

Get-ChildItem -path ".\gitlab" -Directory -Force | ForEach-Object {
	Write-Output "Update git repo $($_.Name)"
	$repo_path = $curPath | Join-Path -ChildPath "gitlab" | Join-Path -ChildPath $_.Name
	Set-Location $repo_path
	If (-Not (Test-Path -Path ".git" -PathType Container)) {
		Invoke-Command -ScriptBlock { git init -b main }
		Invoke-Command -ScriptBlock { git remote add origin https://holadmin:{REPLACE_WITH_PASSWORD}@gitlab.vcf.sddc.lab/holadmin/$($_.Name) }
	}
	Invoke-Command -ScriptBlock { git add . }
	Invoke-Command -ScriptBlock { git commit -m "$(Get-Date) Refresh" }
	Invoke-Command -ScriptBlock { git push -f -u origin main }
}

