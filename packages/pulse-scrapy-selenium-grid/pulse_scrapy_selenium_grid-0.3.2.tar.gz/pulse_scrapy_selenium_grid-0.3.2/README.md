# pulse-scrapy-selenium-grid: Selenium Grid middleware for Scrapy
Forked from https://github.com/dozymoe/scrapy-selenium-grid

A Scrapy Download Handler which performs requests using `Selenium Grid` (aiohttp). 
It can be used to handle pages that require JavaScript (among other things) concurrently, while adhering to the regular Scrapy workflow (i.e. without interfering with request scheduling, item processing, etc).

The development of this module is heavily inspired by `scrapy-playwright` and `asyncselenium`.

After the release of Scrapy v2, which includes `coroutine syntax
support <ScrapyCoroutineSyntax_>` and `asyncio support <ScrapyAsyncioSupport_>`,
Scrapy allows to integrate asyncio-based projects such as aiohttp.


#### Minimum required versions
- Python >= 3.12 
- Scrapy >= 2.0
- aiohttp

## Installation
`pulse-scrapy-selenium-grid` is available on PyPI and can be installed with `pip`:
```
pip install pulse-scrapy-selenium-grid
```


## Activation
Replace the default `http` and/or `https` Download Handlers through `DOWNLOAD_HANDLERS`:

```
from pulse_scrapy_selenium_grid.download_handler import ScrapyDownloadHandler

DOWNLOAD_HANDLERS = {
    'http': ScrapyDownloadHandler,
    'https': ScrapyDownloadHandler,
}
TWISTED_REACTOR = 'twisted.internet.asyncioreactor.AsyncioSelectorReactor'
```
Note that the `ScrapyDownloadHandler` class inherits from the default `http/https` handler. 
Unless explicitly marked (see `Basic Usage`), requests will be processed by the regular Scrapy download handler.

#### Basic Usage
===========

Set `DOWNLOAD_HANDLERS` and `TWISTED_REACTOR`.
```
class AwesomeSpider(Spider):
    name = "awesome"
    custom_settings = dict(
        DOWNLOAD_HANDLERS={
            "http": ScrapyDownloadHandler,
            "https": ScrapyDownloadHandler,
        },
        TWISTED_REACTOR="twisted.internet.asyncioreactor.AsyncioSelectorReactor",
        LOG_LEVEL="INFO",
    )

    def start_requests(self):
        yield Request("https://httpbin.org/get")

        yield FormRequest(
            url="https://httpbin.org/post",
            formdata={"foo": "bar"},
        )

    def parse(self, response, **kwargs):
        # 'response' contains the page html as seen by the browser
        self.logger.info(response.url)
        yield {"url": response.url}
```

## Supported Settings

#### SELENIUM_GRID_REMOTE_URL

Type `str`, default `http://127.0.0.1:4444`  

The Selenium Grid hub url.

#### SELENIUM_GRID_IMPLICIT_WAIT_IN_SEC
Type `int`, default `0`

Selenium has a built-in way to automatically wait for elements.

This is a global setting that applies to every element location call for the entire session. The default value is 0, which means that if the element is not found, it will immediately return an error. If an implicit wait is set, the driver will wait for the duration of the provided value before returning the error.  

Note that as soon as the element is located, the driver will return the element reference and the code will continue executing, so a larger implicit wait value won’t necessarily increase the duration of the session.
#### PROXY_ENABLED
Type `boolean`

#### PROXY_HOST
Type `str`

#### PROXY_PORT
Type `str`

#### PROXY_USERNAME
Type `str`

#### PROXY_PASSWORD
Type `str`


## Supported Request Meta

#### use_selenium_grid

Type `bool`, default `True`

If set to a value that evaluates to `True` the request will be processed by Selenium Grid.
```
return Request("https://example.org", meta={"use_selenium_grid": True})
```

#### selenium_grid_implicit_wait_in_sec
Wait time before parsing the request

#### selenium_grid_driver
Type `scrapy_selenium_grid.webdriver.WebDriver`

This will be returned with asynchronous Selenium Driver.

```
  from scrapy import Request
  from scrapy_selenium_grid.common.action_chains import ActionChains
  from selenium.webdriver.common.by import By
  from selenium.webdriver.common.keys import Keys

  def start_requests(self):
      yield Request(url="https://httpbin.org/get")
  
  async def parse(self, response, **kwargs):
      driver = response.meta["selenium_grid_driver"]

      await ActionChains(driver).key_down(Keys.F12).key_up(Keys.F12).perform()

      inp_userid = await driver.find_element(By.CSS_SELECTOR, 'input[name="userid"]')
      assert await inp_userid.is_displayed() == True
      await inp_userid.send_keys("Username")

      print(await driver.get_log('browser'))
```


## References
- _Scrapy: https://github.com/scrapy/scrapy
- _ScrapyAsyncioReactor: https://docs.scrapy.org/en/latest/topics/asyncio.html#installing-the-asyncio-reactor
- _ScrapyAsyncioSupport: https://docs.scrapy.org/en/2.0/topics/asyncio.html
- _ScrapyCoroutineSyntax: https://docs.scrapy.org/en/2.0/topics/coroutines.html
- _ScrapyRequestMeta: https://docs.scrapy.org/en/latest/topics/request-response.html#scrapy.http.Request.meta
- _ScrapySettings: https://docs.scrapy.org/en/latest/topics/settings.html
- _Scrapy_v2: https://docs.scrapy.org/en/latest/news.html#scrapy-2-0-0-2020-03-03
- _Selenium Grid: https://www.selenium.dev/documentation/grid/
- _SeleniumImplicitWaits: https://www.selenium.dev/documentation/webdriver/waits/#implicit-waits
- _aiohttp: https://github.com/aio-libs/aiohttp
- _scrapy-playwright: https://github.com/scrapy-plugins/scrapy-playwright
- _asyncselenium: https://github.com/Yyonging/asyncselenium
