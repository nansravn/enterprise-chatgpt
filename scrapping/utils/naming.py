import hashlib
import re
from urllib.parse import urlparse

def create_name(url):
    # Parse the URL to get the domain name
    domain = urlparse(url).netloc
    
    # Remove "www." from the domain name if it exists
    domain = re.sub(r'^www\.', '', domain)

    # Remove the TLD from the domain name
    domain = domain.split(".")[0]

    # Remove any non-alphanumeric characters from the domain name
    domain = re.sub(r'\W+', '', domain)
    
    # Hash the URL to get a unique identifier
    hash = hashlib.sha256(url.encode('utf-8')).hexdigest()[:12]
    
    # Combine the domain name and hash to create the final name
    name = f"{domain}-{hash}"
    
    # Truncate the name to 24 characters
    name = name[:24]
    
    return name


if __name__ == "__main__":
    urls = ["https://www.vale.com/pt/", "https://www.eyp.org/", "https://www.microsoft.com/"]
    name = create_name(urls[2])
    print(name)