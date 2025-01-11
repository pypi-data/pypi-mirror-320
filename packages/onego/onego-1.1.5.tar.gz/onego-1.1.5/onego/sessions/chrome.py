import os
import cloudscraper
from urllib.parse import urlparse

from onego import files, utils, logger

class SessionChrome(cloudscraper.CloudScraper):

    def __init__(self, profile: str = 'Default', chrome_version: int = 131, cookies_path: str = '.onego-cookies', htmls_path: str = '.onego-htmls', logs_path: str = '.logs', *args, **kwargs):
        self.profile = profile
        self.cookies_path = os.path.join(cookies_path, f'{self.profile}.json')
        self.htmls_path = htmls_path
        self.chrome_version = chrome_version or 131

        self.logger = logger.Logger(self.profile, logs_path)

        os.makedirs(cookies_path, exist_ok=True)

        super().__init__(*args, **kwargs)

        user_agent = f'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{self.chrome_version}.0.0.0 Safari/537.36'

        self.headers.update({ 'User-Agent': user_agent })
        self.headers.update({ 'Sec-Ch-Ua': f'"Not_A Brand";v="8", "Chromium";v="{self.chrome_version}", "Google Chrome";v="{self.chrome_version}"' })
        self.headers.update({ 'Sec-Ch-Ua-Mobile': '?0' })
        self.headers.update({ 'Sec-Ch-Ua-Platform': '"Windows"' })

    def init(self):
        self.load_cookies()
        return self

    def save_cookies(self):
        cookies = self.export_cookies_dict()
        files.writeJSON(self.cookies_path, cookies)
        return cookies

    def load_cookies(self):
        cookies = files.readJSON(self.cookies_path)
        if not cookies: return []
        for c in cookies: self.cookies.set(c['name'], c['value'], domain=c['domain'], path=c['path'], secure=c['secure'], expires=c['expires'])
        return cookies

    def export_cookies_dict(self):
        return [{ 'name': c.name, 'value': c.value, 'domain': c.domain, 'path': c.path, 'secure': c.secure, 'expires': c.expires } for c in self.cookies]

    def export_cookies(self):
        return [c for c in self.cookies]

    def save_html(self, res: cloudscraper.requests.Response, filename: str = None):
        if type(filename) == str and not filename.endswith('.html'): filename = f'{filename}.html'
        path = files.join(self.htmls_path, filename or self.url_to_domain(res.url + '.html'))
        files.write(path, res.text)

    def parse(self, res: cloudscraper.requests.Response | str): return utils.parse(res)

    @staticmethod
    def url_to_domain(url: str): return urlparse(url).netloc

    def __info(self): return f'<Session profile={self.profile} />'

    def __str__(self): return self.__info()
    def __repr__(self): return self.__info()

def make_session(profile: str, *args, **kwargs): return SessionChrome(profile, *args, **kwargs)
