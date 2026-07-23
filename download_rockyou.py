import requests
import os

urls = [
    "https://github.com/brannondorsey/naive-hashcat/releases/download/data/rockyou.txt",
    "https://objects.githubusercontent.com/github-production-release-asset-2e65be/97552267/d9a6dc00-5630-11e7-8e39-26b2f624f208",
]

for url in urls:
    print(f"Trying: {url[:70]}")
    try:
        r = requests.get(url, stream=True, timeout=60, allow_redirects=True)
        size_header = r.headers.get("content-length", "unknown")
        print(f"Status: {r.status_code}, Content-Length: {size_header}")
        if r.status_code == 200:
            with open("rockyou.txt", "wb") as f:
                downloaded = 0
                for chunk in r.iter_content(chunk_size=65536):
                    f.write(chunk)
                    downloaded += len(chunk)
                    if downloaded % (5 * 1024 * 1024) < 65536:
                        print(f"  Downloaded: {downloaded/1024/1024:.1f} MB")
            size = os.path.getsize("rockyou.txt")
            print(f"Saved rockyou.txt - {size/1024/1024:.1f} MB")
            break
        else:
            print(f"Failed with status {r.status_code}")
    except Exception as e:
        print(f"Error: {e}")
