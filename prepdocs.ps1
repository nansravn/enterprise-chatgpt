Write-Host ""
Write-Host "Loading .env file from current python-dotenv environment"
Write-Host ""

$envFile = "./.env"

if (-not (Test-Path $envFile)) {
  Write-Host "ERROR: .env file not found. Please create one."
  exit
}

# Load env variables from .env file
$output = Get-Content $envFile

foreach ($line in $output) {
  $name, $value = $line.Split("=")
  $value = $value -replace '^\"|\"$'
  [Environment]::SetEnvironmentVariable($name, $value)
}

Write-Host "Environment variables set."

$venvPythonPath = "./.venv/bin/python"

$cwd = (Get-Location)
Start-Process -FilePath $venvPythonPath -ArgumentList "$cwd/prepdocs.py $cwd/data/* --storageaccount $env:AZURE_STORAGE_ACCOUNT --storagekey $env:AZURE_STORAGE_KEY --container $env:AZURE_STORAGE_CONTAINER --searchservice $env:AZURE_SEARCH_SERVICE --searchkey $env:AZURE_SEARCH_KEY --index $env:AZURE_SEARCH_INDEX --formrecognizerservice $env:AZURE_FORMRECOGNIZER_SERVICE --tenantid $env:AZURE_TENANT_ID -v" -Wait -NoNewWindow
