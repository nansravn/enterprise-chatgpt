# Project Name
Enterprise ChatGPT

## Description

Fork of this project: [ChatGPT + Enterprise data with Azure OpenAI and Cognitive Search](https://github.com/Azure-Samples/azure-search-openai-demo/)

## Installations

```bash
pip install -r requirements.txt
```

Optional (for MacOS users):
```bash
playwright install
brew install libmagic
```
## Usage

```bash
# Run the following commands in the root directory of the project

# Phase 1: Crawling websites and writing the knowledge base locally
pwsh ./scrapping-pipeline.ps1

# Phase 2: Creating the Cognitive Search Index and uploading
# the knowledge base to Cognitive Search
pwsh ./prepdocs.ps1
```

**Note:** If the Cognitive Search index already exists, delete the index before running the `./prepdocs.ps1` script. The script will create a new index with the same name and upload the knowledge base to that new index.
## Contributing

[Insert contribution guidelines here]

## License

[Insert license information here]