from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
import os
import urllib.request
import re
from urllib.parse import urlparse


class SitemapProcessor:
    def __init__(self, sitemap_url):
        self.sitemap_url = sitemap_url

    def fetch_sitemap(self):
        req = urllib.request.Request(
            self.sitemap_url,
            data=None,
            headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:101.0) Gecko/20100101 Firefox/101.0"
            },
        )
        response = urllib.request.urlopen(req)
        return response.read()

    def extract_urls(self, sitemap_xml):
        soup = BeautifulSoup(sitemap_xml, "lxml-xml")
        return [loc.get_text() for loc in soup.find_all("loc")]


class URLFilter:
    def __init__(self, filter_pattern=None):
        self.filter_pattern = re.compile(filter_pattern) if filter_pattern else None

    def filter_urls(self, urls):
        if not self.filter_pattern:
            return urls

        filtered_urls = []
        for url in urls:
            parsed_url = urlparse(url)
            path_query = f"{parsed_url.path}?{parsed_url.query}"
            if self.filter_pattern.search(path_query):
                filtered_urls.append(url)
        return filtered_urls


class WebDriverFactory:
    @staticmethod
    def create_driver(
        headless=False,
        disable_images=True,
        disable_stylesheets=True,
        disable_fonts=True,
    ):
        chrome_options = webdriver.ChromeOptions()
        if headless:
            chrome_options.add_argument("--headless")
        if disable_images or disable_stylesheets or disable_fonts:
            prefs = {}
            if disable_images:
                prefs["profile.managed_default_content_settings.images"] = 2
            if disable_stylesheets:
                prefs["profile.managed_default_content_settings.stylesheets"] = 2
            if disable_fonts:
                prefs["profile.managed_default_content_settings.fonts"] = 2
            chrome_options.add_experimental_option("prefs", prefs)
        return webdriver.Chrome(options=chrome_options)


class PageScraper:
    def __init__(self, driver, timeout=30):
        self.driver = driver
        self.timeout = timeout

    def scrape_url(self, url):
        try:
            self.driver.set_page_load_timeout(self.timeout)
            self.driver.get(url)
            return self.driver.page_source
        except TimeoutException:
            print(f"Timeout occurred while loading URL: {url}")
            return None


class HTMLSaver:
    @staticmethod
    def save_html(url, content, output_dir):
        parsed_url = urllib.parse.urlparse(url)
        path = parsed_url.path.lstrip("/")
        dirname = os.path.dirname(path)
        basename = os.path.basename(path)
        if not basename:
            basename = "index.html"
        elif not basename.endswith(".html"):
            basename = f"{os.path.splitext(basename)[0]}.html"
        filename = os.path.join(output_dir, dirname, basename)
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)


class GitbookScraper:
    def __init__(
        self, base_url, output_dir, filter_pattern=None, sitemap_filename="sitemap.xml"
    ):
        self.base_url = base_url
        self.sitemap_url = f"{base_url}{sitemap_filename}"
        self.output_dir = output_dir
        self.visited_links = set()
        self.filter_pattern = filter_pattern

    def scrape(self):
        self._create_output_directory()
        self._print_scraping_info()

        sitemap_processor = SitemapProcessor(self.sitemap_url)
        sitemap_xml = sitemap_processor.fetch_sitemap()
        urls = sitemap_processor.extract_urls(sitemap_xml)

        url_filter = URLFilter(self.filter_pattern)
        filtered_urls = url_filter.filter_urls(urls)

        driver = WebDriverFactory.create_driver()
        page_scraper = PageScraper(driver)

        try:
            for url in filtered_urls:
                if url not in self.visited_links:
                    self.visited_links.add(url)
                    page_content = page_scraper.scrape_url(url)
                    if page_content:
                        HTMLSaver.save_html(url, page_content, self.output_dir)
        finally:
            driver.quit()

        print("Scraping complete!")

    def _create_output_directory(self):
        os.makedirs(self.output_dir, exist_ok=True)

    def _print_scraping_info(self):
        print(f"Fetching URLs from {self.sitemap_url} to scrape to {self.output_dir}")


if __name__ == "__main__":
    base_url = "https://python.langchain.com/"
    output_dir = "./langchain-docs/"
    # remove version numbers to prevent getting old versions
    filter_pattern = r"^/(?!.*\d+\.\d+\.\d+/).*$"
    sitemap_filename = "sitemap.xml"

    scraper = GitbookScraper(base_url, output_dir, filter_pattern, sitemap_filename)
    scraper.scrape()
