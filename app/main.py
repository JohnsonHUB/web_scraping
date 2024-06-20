import html2text
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

app = FastAPI()

class URLList(BaseModel):
    urls: List[str]

def get_main_content_from_url(url):
    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    try:
        response = session.get(url, verify=False)
        response.raise_for_status()  # 检查请求是否成功
    except requests.exceptions.RequestException as e:
        return f"Request failed: {e}"

    # 解析网页内容
    soup = BeautifulSoup(response.text, 'html.parser')

    # 剔除顶部导航栏和底部导航栏
    def remove_elements(soup, selectors):
        for selector in selectors:
            for element in soup.select(selector):
                element.decompose()

    # 示例选择器，请根据实际网页的 HTML 结构调整
    selectors_to_remove = [
        'header',             # 顶部导航栏的选择器
        'nav',                # 另一种顶部导航栏的选择器
        'footer',             # 底部导航栏的选择器
        '.top-nav',           # 顶部导航栏的类名
        '.bottom-nav',        # 底部导航栏的类名
    ]

    remove_elements(soup, selectors_to_remove)

    # 查找并移除符合 CSS 选择器的元素
    elements_to_remove = soup.select('.__pf .pf-lg-hide')

    for element in elements_to_remove:
        element.decompose()  # 移除元素

    # 获取主内容
    main_content = soup.find('main', id='MainContent')

    if main_content:
        html_text = str(main_content)

        # 带有配置选项的示例
        h = html2text.HTML2Text()
        h.ignore_images = True
        h.ignore_links = False
        return h.handle(html_text)
    else:
        return "No main content found."

def process_links_concurrently(links):
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(get_main_content_from_url, links))
    return results

@app.post("/process_urls")
def process_urls(url_list: URLList):
    results = process_links_concurrently(url_list.urls)
    return {"results": results}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
