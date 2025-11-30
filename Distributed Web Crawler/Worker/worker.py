"""
CSCI-651 Project: Distributed Web Crawler

Implementing a Distributed Web Crawler to crawl different
websites, download all related files, calculate MD5 hash
and send it back to the server.
Uses Docker Containers to host workers.
"""

import os
import shutil
import requests
import time
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import hashlib
import config

WORKER_ID = os.environ.get("WORKER_ID", "undefined")  # default to undefined if not set
DOWNLOAD_DELAY = 5

def download_file(url, save_dir):
    """
    Method to download the file and save it

    :param url: URL of file to be downloaded
    :param save_dir: Directory name where to store it
    :return: Full file path where file has been stored
    """
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
    """
    Method to compute MD5 of the downloaded file

    :param file_path: Path of downloaded file to calculate its MD5 hash
    :return: MD5 Hash of the file
    """
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def _get_user_bookmarks(login_response, auth_kw):
    auth_token = dict()
    for k, v in login_response.cookies.items():
        if auth_kw in k:
            auth_token = {k: v}

    try:
        time.sleep(DOWNLOAD_DELAY)
        response = requests.get(
            config.bookmark_url, timeout=30, cookies=auth_token, headers=config.bookmark_headers)
        response.raise_for_status()
        print(f"Status Code: {response.status_code}")
    except requests.exceptions.HTTPError as err:
        print(f"HTTP error occurred: {err}")
    except Exception as err:
        print(f"An unexpected error occurred: {err}")

    return response

def _extract_article_content(article_response):
    article_content_css = '.post__content__section'
    article_soup = BeautifulSoup(article_response.text, "html.parser")
    article_text_selectors = article_soup.select(article_content_css)

    all_article_text = []

    for sel in article_text_selectors:
        txt = sel.get_text(strip=True)
        all_article_text.append(txt)

    article_content = '\n\n'.join(all_article_text)

    return article_content

def download_article_content(url, save_dir):
    """
    Method to download the file and save it

    :param url: URL of file to be downloaded
    :param save_dir: Directory name where to store it
    :return: Full file path where file has been stored
    """
    os.makedirs(save_dir, exist_ok=True)
    local_filename = [u for u in url.split('/') if u][-1]
    local_path = os.path.join(save_dir, f'{local_filename}.txt')
    with requests.get(url, stream=True, timeout=30, headers=config.article_headers) as r:
        r.raise_for_status()
        time.sleep(DOWNLOAD_DELAY)

        with open(local_path, 'wb') as f:
            chunk = _extract_article_content(r).encode('utf-8')
            if chunk:
                f.write(chunk)

    return local_path

def crawl_arxiv_list_page(url, save_dir="downloads"):
    """
    Method to crawl the arXiv website and download all PDFs

    :param url: URL of the website to crawl
    :param save_dir: Directory name to download files and store them
    :return: JSON dictionary of {url, file, md5, status} of all downloaded files
    """
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

def crawl_mit_list_page(url, save_dir="downloads"):
    """
    Method to crawl the MIT website and download all PDFs

    :param url: URL of the website to crawl
    :param save_dir: Directory name to download files and store them
    :return: JSON dictionary of {url, file, md5, status} of all downloaded files
    """
    print(f"Crawling MIT base page: {url}")

    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
    except Exception as e:
        print(f"Failed to fetch MIT base page: {e}")
        return [{"url": url, "status": f"error: {e}"}]

    soup = BeautifulSoup(resp.text, "html.parser")
    resource_links = []

    # ---------- Step 1: collect all resource pages ----------
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.startswith("/courses/") and "/resources/" in href:
            resource_links.append(urljoin("https://ocw.mit.edu", href))

    resource_links = list(set(resource_links))
    print(f"Found {len(resource_links)} MIT resource pages")

    # ---------- Step 2: crawl each resource page for actual PDFs ----------
    pdf_links = []

    for res_url in resource_links:
        try:
            res_resp = requests.get(res_url, timeout=30)
            res_resp.raise_for_status()
        except Exception as e:
            print(f"Failed to fetch resource page {res_url}: {e}")
            continue

        res_soup = BeautifulSoup(res_resp.text, "html.parser")
        for a in res_soup.find_all("a", href=True, class_="download-file"):
            href = a["href"]
            if href.endswith(".pdf"):
                pdf_links.append(urljoin("https://ocw.mit.edu", href))

    pdf_links = list(set(pdf_links))
    print(f"Found {len(pdf_links)} MIT PDF files")

    # ---------- Step 3: download PDFs ----------
    results = []
    for pdf_url in pdf_links:
        try:
            file_path = download_file(pdf_url, save_dir)
            md5 = compute_md5(file_path)
            results.append({"url": pdf_url, "file": file_path, "md5": md5, "status": "success"})
        except Exception as e:
            results.append({"url": pdf_url, "file": None, "md5": None, "status": f"error: {e}"})

    return results

def crawl_quanta_page(url, save_dir="downloads"):
    try:
        time.sleep(DOWNLOAD_DELAY)
        response = requests.post(url, timeout=30, headers=config.login_headers, data=config.login_body)
        response.raise_for_status()
        print(f"Status Code: {response.status_code}")
    except requests.exceptions.HTTPError as err:
        print(f"HTTP error occurred: {err}")
    except Exception as err:
        print(f"An unexpected error occurred: {err}")

    bookmarks_response = _get_user_bookmarks(response, 'logged_in')
    soup = BeautifulSoup(bookmarks_response.text, 'html.parser')
    saved_articles_css = '.card__content > a[data-toggle-hover="card"]'
    hrefs_selectors = soup.select(saved_articles_css)

    saved_article_urls = []
    for link_tag in hrefs_selectors:
        url = link_tag.get('href')
        if url:
            saved_article_urls.append(url)

    print(
        f"Downloading the following {len(saved_article_urls)} bookmarked articles for user {config.username}:")
    for url in saved_article_urls:
        print(f"- {url}")

    results = []

    for article_url in saved_article_urls:
        try:
            file_path = download_article_content(
                article_url, save_dir)
            md5 = compute_md5(file_path)

            results.append({
                "url": article_url,
                "file": file_path,
                "md5": md5,
                "status": "success"
            })
        except Exception as e:
            results.append({
                "url": article_url,
                "file": None,
                "md5": None,
                "status": f"error: {e}"
            })

    return results

def main(try_counter=0):
    """
    Main method to trigger crawling based on worker ids. Retries 3 times
    on failures.

    :param try_counter: Current attempt of running main function
    :return: None
    """
    # Get URLs dynamically based on worker ID
    try:
        resp = requests.get(f"http://orchestrator:8000/get_urls/{WORKER_ID}")
        resp.raise_for_status()
        urls = resp.json().get("urls", [])
    except Exception as ex:
        print("Failed to fetch URLs from orchestrator!", str(ex))
        return

    results = []

    for url in urls:
        if WORKER_ID == "worker1":
            out = crawl_arxiv_list_page(url, save_dir="arxiv_pdfs")
            cleanup_dir = "arxiv_pdfs"
        elif WORKER_ID == "worker2":
            out = crawl_mit_list_page(url, save_dir="mit_pdfs")
            cleanup_dir = "mit_pdfs"
        elif WORKER_ID == "worker3":
            out = crawl_quanta_page(url, save_dir="quanta_pdfs")
            cleanup_dir = "quanta_pdfs"
        else:
            print("Unknown WORKER_ID", WORKER_ID)
            continue

        # Cleanup downloaded files
        if os.path.exists(cleanup_dir):
            shutil.rmtree(cleanup_dir)
            print("Cleanup successful!")

        results.extend(out)

    # POST results back
    try:
        requests.post(f"http://orchestrator:8000/post_results/data", json=results, timeout=30)
    except Exception as ex:
        if try_counter < 3:
            print("Error sending data back! Retrying...", str(ex))
            main(try_counter + 1)
        else:
            print("Failed to send data after retries.", str(ex))

if __name__ == "__main__":
    main()
