import time
import urllib.request
import re
import webbrowser
from typing import Tuple, Optional, List, Dict, Any
from urllib.parse import quote_plus
from config.config_manager import get_config
from utils.logger import get_logger

logger = get_logger("BrowserController")

class BrowserController:
    """
    Manages browser navigation, web searches, and YouTube video playback.
    Uses Selenium with Selenium Manager auto-driver management as primary engine,
    and direct YouTube video URL resolution + system browser as reliable fallback.
    """
    def __init__(self):
        self.config = get_config()
        self._driver = None

    def _get_selenium_driver(self):
        """Lazy initialization of Selenium webdriver using Selenium Manager."""
        if self._driver is not None:
            return self._driver

        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            
            options = Options()
            options.add_argument("--start-maximized")
            options.add_argument("--disable-notifications")
            
            logger.info("Initializing Selenium WebDriver using standard Selenium Manager...")
            self._driver = webdriver.Chrome(options=options)
            return self._driver
        except Exception as e:
            logger.warning(f"Selenium WebDriver initialization failed: {e}. Falling back to default system browser.")
            self._driver = None
            return None

    def open_website(self, url: str) -> Tuple[bool, str]:
        """Opens a website URL in browser."""
        if not url.startswith("http://") and not url.startswith("https://"):
            url = f"https://{url}"

        try:
            driver = self._get_selenium_driver()
            if driver:
                driver.get(url)
                return True, f"Opened {url} in automated browser."
            else:
                webbrowser.open_new_tab(url)
                return True, f"Opened {url} in system browser."
        except Exception as e:
            logger.error(f"Failed to open URL '{url}': {e}")
            webbrowser.open_new_tab(url)
            return True, f"Opened {url} via fallback browser."

    def search_google(self, query: str) -> Tuple[bool, str]:
        """Performs Google search for the specified query."""
        search_url = f"https://www.google.com/search?q={quote_plus(query)}"
        return self.open_website(search_url)

    def search_youtube(self, query: str) -> Tuple[bool, str]:
        """Performs YouTube search for the specified query."""
        search_url = f"https://www.youtube.com/results?search_query={quote_plus(query)}"
        return self.open_website(search_url)

    def play_youtube_video(self, query: str) -> Tuple[bool, str]:
        """
        Searches YouTube and plays the top video result directly.
        """
        logger.info(f"Attempting to play YouTube video for query: '{query}'")
        search_url = f"https://www.youtube.com/results?search_query={quote_plus(query)}"
        
        # 1. Attempt using Selenium if available
        driver = self._get_selenium_driver()
        if driver:
            try:
                driver.get(search_url)
                time.sleep(2)
                from selenium.webdriver.common.by import By
                videos = driver.find_elements(By.CSS_SELECTOR, "ytd-video-renderer #video-title, a#video-title")
                if videos:
                    video_title = videos[0].get_attribute("title") or query
                    videos[0].click()
                    return True, f"Playing top video '{video_title}' on YouTube."
            except Exception as se:
                logger.warning(f"Selenium video click failed: {se}")

        # 2. Extract top video ID directly from YouTube HTML
        try:
            html_content = urllib.request.urlopen(search_url, timeout=4).read().decode('utf-8')
            video_ids = re.findall(r"watch\?v=(\S{11})", html_content)
            if video_ids:
                video_url = f"https://www.youtube.com/watch?v={video_ids[0]}"
                webbrowser.open_new_tab(video_url)
                return True, f"Playing YouTube video: '{query}'"
        except Exception as e:
            logger.warning(f"Direct video ID extraction failed: {e}")

        # 3. Fallback to search results page
        webbrowser.open_new_tab(search_url)
        return True, f"Opened YouTube search results for '{query}'"

    def close_browser(self):
        """Closes automated browser instance if open."""
        if self._driver:
            try:
                self._driver.quit()
            except Exception:
                pass
            self._driver = None
