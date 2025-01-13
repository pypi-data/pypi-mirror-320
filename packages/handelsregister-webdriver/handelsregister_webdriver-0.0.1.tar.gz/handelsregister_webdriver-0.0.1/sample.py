import os
import time
from tempfile import mkdtemp

from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary

from handelsregister_webdriver import query_docs

# Instructions for use:

# Run with geckodriver in path and create ./tmp and export it:
# $ export TMPDIR=$(pwd)"/tmp/"
# python sample.py

FIREFOX_BIN='/snap/bin/firefox' # need to customize this

# whoop whoop! let's go!

cur_dir = os.getcwd()
download_dir = mkdtemp(prefix='download-', dir=cur_dir)

opts = Options()
#opts.set_headless()
opts.binary_location = FIREFOX_BIN
#assert opts.headless  # Operating in headless mode
opts.add_argument('--ignore-certificate-errors')
opts.add_argument('--incognito')
opts.set_preference("browser.download.folderList", 2)
opts.set_preference("browser.download.manager.showWhenStarting", False)
opts.set_preference("browser.download.dir", download_dir)
opts.set_preference('browser.download.useDownloadDir', True)
opts.set_preference('browser.helperApps.alwaysAsk.force', False)
opts.set_preference('browser.download.manager.useWindow', False)
opts.set_preference('browser.helperApps.neverAsk.saveToDisk', 'application/octet-stream')
opts.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/x-gzip")
#opts.add_argument('--headless')
browser = Firefox(options=opts)

print("Ready!")

try:
	# And here is our query!
	query_docs(browser, 'HRB', 'Chemnitz', '26992')
except Exception as e:
	browser.save_screenshot(f'error.png')
	raise e

print("Sleeping!")
time.sleep(30)

browser.quit()
