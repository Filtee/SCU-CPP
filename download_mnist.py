#!/usr/bin/env python3
import os
import urllib.request
import gzip
import shutil

def download_and_extract(url, filename):
    # Always download the file to ensure it's complete
    print(f"Downloading {filename}...")
    urllib.request.urlretrieve(url, filename)
    print(f"Downloaded {filename}")
    
    # Extract the file
    extract_path = filename.replace('.gz', '')
    print(f"Extracting {filename}...")
    with gzip.open(filename, 'rb') as f_in:
        with open(extract_path, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
    print(f"Extracted to {extract_path}")

def main():
    # Create data directory if it doesn't exist
    data_dir = "data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    # MNIST dataset URLs (updated)
    urls = [
        "https://ossci-datasets.s3.amazonaws.com/mnist/train-images-idx3-ubyte.gz",
        "https://ossci-datasets.s3.amazonaws.com/mnist/train-labels-idx1-ubyte.gz",
        "https://ossci-datasets.s3.amazonaws.com/mnist/t10k-images-idx3-ubyte.gz",
        "https://ossci-datasets.s3.amazonaws.com/mnist/t10k-labels-idx1-ubyte.gz"
    ]
    
    # Download and extract all files
    for url in urls:
        filename = os.path.join(data_dir, os.path.basename(url))
        download_and_extract(url, filename)
    
    print("All files downloaded and extracted successfully!")

if __name__ == "__main__":
    main()