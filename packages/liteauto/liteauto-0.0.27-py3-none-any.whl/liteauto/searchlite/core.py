import asyncio
import re
from concurrent.futures import ThreadPoolExecutor
from dataclasses import field
from multiprocessing import cpu_count
from urllib.parse import quote_plus

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pydantic import BaseModel
from typing import List
import time


class SearchResult(BaseModel):
    query: str
    urls: list = field(default_factory=list)
    search_provider: str = ""
    page_source: str = ""


class OptimizedMultiQuerySearcher:
    def __init__(self, chromedriver_path="/usr/local/bin/chromedriver", max_workers=None,
                 animation=False):
        self.chromedriver_path = chromedriver_path
        self.max_workers = max_workers or min(32, cpu_count() - 2)
        self.animation = animation
        self.driver_pool = []
        self.params = {
            "bing": {"search": "b_results", "find_element": ".b_algo", "head_selector": "h2"},
            "google": {"search": "search", "find_element": "div.g", "head_selector": "h3"}
        }

    def _setup_driver(self):
        chrome_options = Options()
        if not self.animation:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-images")
        chrome_options.add_argument("--blink-settings=imagesEnabled=false")
        chrome_options.add_argument("--start-maximized")
        chrome_options.page_load_strategy = 'none'
        chrome_options.add_argument("--disable-javascript")  # If you don't need JS

        service = Service(self.chromedriver_path)
        return webdriver.Chrome(service=service, options=chrome_options)

    def _get_driver(self):
        if not self.driver_pool:
            return self._setup_driver()
        return self.driver_pool.pop()

    def _return_driver(self, driver):
        self.driver_pool.append(driver)

    def cleanup(self):
        if hasattr(self, 'driver'):
            self.driver.quit()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()

    def search_single_query(self, query, num_results=10,
                            search_provider="google",
                            min_waiting_time: int = 2
                            ):
        driver = self._get_driver()
        try:
            encoded_query = quote_plus(query)
            search_url = f"https://www.{search_provider}.com/search?q={encoded_query}"
            driver.get(search_url)
            time.sleep(min_waiting_time)
            # Wait for initial search results container
            WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.ID, self.params[search_provider]["search"]))
            )

            # Wait for search result links to be present and visible
            if search_provider == "google":
                WebDriverWait(driver, 3).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.g a[href^='https://']"))
                )
            else:  # bing
                WebDriverWait(driver, 3).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".b_algo a[href^='https://']"))
                )

            driver.execute_script("return document.readyState") == "complete"

            soup = BeautifulSoup(driver.page_source, 'html.parser')
            atags = soup.find_all('a',
                                  attrs={'href': re.compile("^https://"),
                                         # 'aria-label': True
                                         })

            urls = self.extract_urls(atags)

            return SearchResult(
                query=query,
                urls=urls,
                search_provider=search_provider,
                page_source=driver.page_source
            )
        except Exception as e:
            print(f'exception as {e}')
            return SearchResult(query=query)
        finally:
            self._return_driver(driver)

    async def search_multiple_queries(self, queries: List[str], num_results=10,
                                      search_provider=None, return_only_urls=False,
                                      min_waiting_time: int = 2
                                      ) -> List[SearchResult]:
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            providers_list = self.params.keys() if search_provider is None else [search_provider]
            tasks = [
                loop.run_in_executor(
                    executor,
                    self.search_single_query,
                    query,
                    num_results,
                    provider,
                    min_waiting_time
                )
                for query in queries for provider in providers_list
            ]
            result = await asyncio.gather(*tasks)
            if return_only_urls:
                all_urls = [url.urls for url in result]
                filtered_urls = [y for x in zip(*all_urls) for y in x]
                return filtered_urls
            return result


    def extract_urls(self, atags):
        all_urls = [u.get("href") for u in atags if u.get("href")]

        filtered_urls = []
        for url in all_urls:
            if 'google' not in url:
                filtered_urls.append(url)

        yt_urls = []
        non_yt_urls = []
        for url in filtered_urls:
            if 'youtube' in url:
                yt_urls.append(url)
            else:
                non_yt_urls.append(url)

        final_urls = non_yt_urls + yt_urls

        return final_urls


class RealTimeGoogleSearchProvider:
    def __init__(
        self,
        search_provider="google",
        chromedriver_path="/usr/local/bin/chromedriver",
        max_workers=None,
        animation=False
    ):
        self.search_provider = search_provider
        self.chromedriver_path = chromedriver_path
        self.max_workers = max_workers
        self.animation = animation

    def search(self, query: str, max_urls=50) -> List[str]:
        with OptimizedMultiQuerySearcher(chromedriver_path=self.chromedriver_path,
                                         max_workers=self.max_workers,
                                         animation=self.animation) as searcher:
            res = searcher.search_single_query(query, search_provider=self.search_provider)
            # print("@@@@@")
            # Path('goolge_page_source.txt').write_text(res.page_source)
            return res.urls[:max_urls]

    async def _async_batch_search(self, batch_queries, max_urls=50) -> List[str]:
        with OptimizedMultiQuerySearcher(chromedriver_path=self.chromedriver_path,
                                         max_workers=self.max_workers,
                                         animation=self.animation) as searcher:
            all_urls = await searcher.search_multiple_queries(
                queries=batch_queries,
                search_provider=self.search_provider
            )
            all_urls = [url.urls for url in all_urls]
            filtered_urls = [y for x in zip(*all_urls) for y in x]
            filtered_urls = [self._extract_until_hash(x) if self._is_hash(x) else x for x in filtered_urls]
            filtered_urls = [_ for _ in filtered_urls if _]
            duplicate_removed_urls = self._remove_duplicate_urls(filtered_urls)
            return duplicate_removed_urls[:max_urls]

    def search_batch(self, batch_queries, max_urls=50) -> List[str]:
        return asyncio.run(self._async_batch_search(batch_queries, max_urls=max_urls))

    def __call__(self, query: str | list, *args, **kwargs):
        if isinstance(query, str):
            return self.search(query, *args, **kwargs)
        return self.search_batch(query, *args, **kwargs)

    def _is_hash(self, x):
        return '#' in x

    def _extract_until_hash(self, x):
        results = re.findall(r'(.*)#', x)
        if results:
            return results[0]
        return ""

    def _remove_duplicate_urls(self, filtered_urls):
        """Remove duplicates  by maintaining order"""
        seen = set()
        seen_add = seen.add
        return [x for x in filtered_urls if not (x in seen or seen_add(x))]


