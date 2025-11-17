import os
import shutil
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import hashlib

def download_file(url, save_dir):
    os.makedirs(save_dir, exist_ok=True)
    local_filename = url.split('/')[-1]
    local_path = os.path.join(save_dir, local_filename)
    with requests.get(url, stream=True, timeout=30) as r:
        r.raise_for_status()
        with open(local_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
    return local_path

def compute_md5(file_path):
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def crawl_arxiv_list_page(url, save_dir="downloads"):
    print(f"Crawling {url}")

    # ---------- FETCH PAGE SAFELY ----------
    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch list page: {e}")
        return [{"url": url, "status": f"error: {e}"}]

    # ---------- PARSE DOCUMENT ----------
    soup = BeautifulSoup(resp.text, "html.parser")
    pdf_links = []

    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.startswith("/pdf/"):
            pdf_links.append(urljoin("https://arxiv.org", href))
        elif href.startswith("https://arxiv.org/pdf/"):
            pdf_links.append(href)

    # Remove duplicates
    pdf_links = list(set(pdf_links))
    print(f"Found {len(pdf_links)} PDF links")

    results = []

    # ---------- DOWNLOAD PDFS SAFELY ----------
    for pdf_url in pdf_links:
        try:
            file_path = download_file(pdf_url, save_dir)
            md5 = compute_md5(file_path)

            results.append({
                "url": pdf_url,
                "file": file_path,
                "md5": md5,
                "status": "success"
            })

        except Exception as e:
            results.append({
                "url": pdf_url,
                "file": None,
                "md5": None,
                "status": f"error: {e}"
            })

    return results

def main(try_counter = 0):
    data = requests.get("http://orchestrator:8000/get_urls/worker1")
    urls = data.json()["urls"]
    results = []
    for url in urls:
        out = crawl_arxiv_list_page(url, save_dir="arxiv_pdfs")
        try:
            shutil.rmtree("arxiv_pdfs")
            print("Cleanup successful!")
        except Exception as ex:
            print("Error cleaning up!", str(ex))
        # Optionally: print out results or send back to server API
        results.extend(out)

    try:
        requests.post(
            "http://orchestrator:8000/post_results/data",
            json=results,
            timeout=30
        )
    except Exception as ex:
        if try_counter < 3:
            print("Error sending data back to server! Trying again!", str(ex))
            main(try_counter + 1)
        else:
            print("Error sending data back to server! Exiting!", str(ex))

if __name__ == "__main__":
    main()
