import os
import argparse
import glob
import html
import io
import re
import time
from azure.identity import AzureDeveloperCliCredential
from azure.identity import DefaultAzureCredential
from azure.core.credentials import AzureKeyCredential
from azure.storage.blob import BlobServiceClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import *
from azure.search.documents import SearchClient
from azure.ai.formrecognizer import DocumentAnalysisClient
from typing import List

MAX_SECTION_LENGTH = 1000
SENTENCE_SEARCH_LIMIT = 100
SECTION_OVERLAP = 100

parser = argparse.ArgumentParser(
    description="Prepare documents by extracting content from PDFs, splitting content into sections, uploading to blob storage, and indexing in a search index.",
    epilog="Example: prepdocs.py '..\data\*' --storageaccount myaccount --container mycontainer --searchservice mysearch --index myindex -v"
    )
parser.add_argument("files", help="Files to be processed")
parser.add_argument("--category", help="Value for the category field in the search index for all sections indexed in this run")
parser.add_argument("--skipblobs", action="store_true", help="Skip uploading individual pages to Azure Blob Storage")
parser.add_argument("--storageaccount", help="Azure Blob Storage account name")
parser.add_argument("--container", help="Azure Blob Storage container name")
parser.add_argument("--storagekey", required=False, help="Optional. Use this Azure Blob Storage account key instead of the current user identity to login (use az login to set current user for Azure)")
parser.add_argument("--tenantid", required=False, help="Optional. Use this to define the Azure directory where to authenticate)")
parser.add_argument("--searchservice", help="Name of the Azure Cognitive Search service where content should be indexed (must exist already)")
parser.add_argument("--index", help="Name of the Azure Cognitive Search index where content should be indexed (will be created if it doesn't exist)")
parser.add_argument("--searchkey", required=False, help="Optional. Use this Azure Cognitive Search account key instead of the current user identity to login (use az login to set current user for Azure)")
parser.add_argument("--remove", action="store_true", help="Remove references to this document from blob storage and the search index")
parser.add_argument("--removeall", action="store_true", help="Remove all blobs from blob storage and documents from the search index")
parser.add_argument("--localpdfparser", action="store_true", help="Use PyPdf local PDF parser (supports only digital PDFs) instead of Azure Form Recognizer service to extract text, tables and layout from the documents")
parser.add_argument("--formrecognizerservice", required=False, help="Optional. Name of the Azure Form Recognizer service which will be used to extract text, tables and layout from the documents (must exist already)")
parser.add_argument("--formrecognizerkey", required=False, help="Optional. Use this Azure Form Recognizer account key instead of the current user identity to login (use az login to set current user for Azure)")
parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
args = parser.parse_args()

# Use the current user identity to connect to Azure services unless a key is explicitly set for any of them
credential = DefaultAzureCredential()
azd_credential = AzureDeveloperCliCredential() if args.tenantid == None else AzureDeveloperCliCredential(tenant_id=args.tenantid)
default_creds = azd_credential if args.searchkey == None or args.storagekey == None else None
search_creds = default_creds if args.searchkey == None else AzureKeyCredential(args.searchkey)
if not args.skipblobs:
    storage_creds = default_creds if args.storagekey == None else args.storagekey

print(args)

def blob_name_from_file_page(filename, page = 0):
    if os.path.splitext(filename)[1].lower() == ".pdf":
        return os.path.splitext(os.path.basename(filename))[0] + f"-{page}" + ".pdf"
    else:
        return os.path.basename(filename)

def upload_blobs(filename):
    blob_service = BlobServiceClient(account_url=f"https://{args.storageaccount}.blob.core.windows.net", credential=credential)
    blob_container = blob_service.get_container_client(args.container)
    if not blob_container.exists():
        blob_container.create_container()

    blob_name = blob_name_from_file_page(filename)
    with open(filename,"rb") as data:
        blob_container.upload_blob(blob_name, data, overwrite=True)

def remove_blobs(filename):
    if args.verbose: print(f"Removing blobs for '{filename or '<all>'}'")
    blob_service = BlobServiceClient(account_url=f"https://{args.storageaccount}.blob.core.windows.net", credential=storage_creds)
    blob_container = blob_service.get_container_client(args.container)
    if blob_container.exists():
        if filename == None:
            blobs = blob_container.list_blob_names()
        else:
            prefix = os.path.splitext(os.path.basename(filename))[0]
            blobs = filter(lambda b: re.match(f"{prefix}-\d+\.pdf", b), blob_container.list_blob_names(name_starts_with=os.path.splitext(os.path.basename(prefix))[0]))
        for b in blobs:
            if args.verbose: print(f"\tRemoving blob {b}")
            blob_container.delete_blob(b)

def create_document(file_path, text):
    return {
        "id": re.sub("[^0-9a-zA-Z_-]","_", os.path.basename(file_path)),
        "content": text,
        "category": "Company Webpage",
        "sourcepage": os.path.basename(file_path),
        "sourcefile": os.path.basename(file_path).split("-")[0] + ".txt"
    }
        

# def create_search_index():
#     if args.verbose: print(f"Ensuring search index {args.index} exists")
#     index_client = SearchIndexClient(endpoint=f"https://{args.searchservice}.search.windows.net/",
#                                      credential=search_creds)
#     if args.index not in index_client.list_index_names():
#         index = SearchIndex(
#             name=args.index,
#             fields=[
#                 SimpleField(name="id", type="Edm.String", key=True),
#                 SearchableField(name="content", type="Edm.String", analyzer_name="en.microsoft"),
#                 SimpleField(name="category", type="Edm.String", filterable=True, facetable=True),
#                 SimpleField(name="sourcepage", type="Edm.String", filterable=True, facetable=True),
#                 SimpleField(name="sourcefile", type="Edm.String", filterable=True, facetable=True)
#             ],
#             semantic_settings=SemanticSettings(
#                 configurations=[SemanticConfiguration(
#                     name='default',
#                     prioritized_fields=PrioritizedFields(
#                         title_field=None, prioritized_content_fields=[SemanticField(field_name='content')]))])
#         )
#         if args.verbose: print(f"Creating {args.index} search index")
#         index_client.create_index(index)
#     else:
#         if args.verbose: print(f"Search index {args.index} already exists")

def create_search_index():
    if args.verbose: print(f"Ensuring search index {args.index} exists")
    index_client = SearchIndexClient(endpoint=f"https://{args.searchservice}.search.windows.net/",
                                     credential=credential)
    if args.index not in index_client.list_index_names():
        index = SearchIndex(
            name=args.index,
            fields=[
                SimpleField(name="id", type="Edm.String", key=True),
                SearchableField(name="content", type="Edm.String", analyzer_name="pt-Br.microsoft"),
                SimpleField(name="category", type="Edm.String", filterable=True, facetable=True),
                SimpleField(name="sourcepage", type="Edm.String", filterable=True, facetable=True),
                SimpleField(name="sourcefile", type="Edm.String", filterable=True, facetable=True)
            ],
            semantic_settings=SemanticSettings(
                configurations=[SemanticConfiguration(
                    name='default',
                    prioritized_fields=PrioritizedFields(
                        title_field=None, prioritized_content_fields=[SemanticField(field_name='content')]))])
        )
        if args.verbose: print(f"Creating {args.index} search index")
        index_client.create_index(index)
    else:
        if args.verbose: print(f"Search index {args.index} already exists")

def index_documents(documents: List[dict]):
    if args.verbose: print(f"Indexing list of documents into search index '{args.index}'")
    search_client = SearchClient(endpoint=f"https://{args.searchservice}.search.windows.net/",
                                    index_name=args.index,
                                    credential=credential)
    i = 0
    batch = []
    for s in documents:
        batch.append(s)
        i += 1
        if i % 100 == 0 or i == len(documents):
            results = search_client.upload_documents(documents=batch)
            succeeded = sum([1 for r in results if r.succeeded])
            if args.verbose: print(f"\tIndexed {len(results)} sections, {succeeded} succeeded")
            batch = []


def remove_from_index(filename):
    if args.verbose: print(f"Removing sections from '{filename or '<all>'}' from search index '{args.index}'")
    search_client = SearchClient(endpoint=f"https://{args.searchservice}.search.windows.net/",
                                    index_name=args.index,
                                    credential=search_creds)
    while True:
        filter = None if filename == None else f"sourcefile eq '{os.path.basename(filename)}'"
        r = search_client.search("", filter=filter, top=1000, include_total_count=True)
        if r.get_count() == 0:
            break
        r = search_client.delete_documents(documents=[{ "id": d["id"] } for d in r])
        if args.verbose: print(f"\tRemoved {len(r)} sections from index")
        # It can take a few seconds for search results to reflect changes, so wait a bit
        time.sleep(2)

if args.removeall:
    remove_blobs(None)
    remove_from_index(None)
else:
    if not args.remove:
        create_search_index()
    
    print(f"Processing files...")
    documents_queue = []
    for txt_path in glob.glob("data/embratel-14db19e9f974/content-stage4/*.txt"):
        if not args.skipblobs:
            print(f"Uploading blob for '{txt_path}'")
            upload_blobs(txt_path)
            with open(txt_path, "r") as f:
                text = f.read()
            documents_queue.append(create_document(txt_path, text))
            print(f"Indexing document '{txt_path}'")
    index_documents(documents_queue)
