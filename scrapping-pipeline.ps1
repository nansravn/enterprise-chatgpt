$venvPythonPath = "./.venv/bin/python"

$customerUrl = "https://www.vale.com.br/"
$nJobs = 16
$modelName = "text-davinci-003"
$chunkSize = 1600
$chunkOverlap = 100

$cwd = (Get-Location)

Write-Host "[STEP 1] Crawling '$customerUrl'"
Start-Process -FilePath $venvPythonPath -ArgumentList "$cwd/scrapping/s01_find_urls.py $customerUrl" -Wait -NoNewWindow

Write-Host "[STEP 2] Downloading crawled webpages ($nJobs parallel jobs)"
Start-Process -FilePath $venvPythonPath -ArgumentList "$cwd/scrapping/s02_scrap_content.py $customerUrl --n-jobs $nJobs" -Wait -NoNewWindow

Write-Host "[STEP 3] SKIPPED"
#Start-Process -FilePath $venvPythonPath -ArgumentList "$cwd/scrapping/s03_cleanse_dictionary.py $customerUrl" -Wait -NoNewWindow

Write-Host "[STEP 4] Pairwise comparison of the scrapped websites"
Start-Process -FilePath $venvPythonPath -ArgumentList "$cwd/scrapping/s04_pairwise_diff.py $customerUrl" -Wait -NoNewWindow

Write-Host "[STEP 5] Computing line frequency statistics"
Start-Process -FilePath $venvPythonPath -ArgumentList "$cwd/scrapping/s05_frequency_stats.py $customerUrl" -Wait -NoNewWindow

Write-Host "[STEP 6] Cleasing the webpages based on the frequency statistics"
Start-Process -FilePath $venvPythonPath -ArgumentList "$cwd/scrapping/s06_cleanse_frequent_lines.py $customerUrl" -Wait -NoNewWindow

Write-Host "[STEP 7] Computing webpage tokenization statistics"
Start-Process -FilePath $venvPythonPath -ArgumentList "$cwd/scrapping/s07_tokenize_webpages.py $customerUrl --model-name $modelName" -Wait -NoNewWindow

Write-Host "[STEP 8] Splitting webpage in chunks of $chunkSize tokens (with an overlap of $chunkOverlap tokens)"
Start-Process -FilePath $venvPythonPath -ArgumentList "$cwd/scrapping/s08_zoning.py $customerUrl --chunk-size $chunkSize --chunk-overlap $chunkOverlap" -Wait -NoNewWindow
