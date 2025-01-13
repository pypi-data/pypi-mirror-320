import time
import threading

from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, ElementNotVisibleException, ElementNotSelectableException, StaleElementReferenceException
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains


def fill_tokens(browser=None, tokens_per_increment=3, increment_seconds=9):
    while True:
        if browser.token_value < tokens_per_increment:
            browser.token_inc(tokens_per_increment)
        time.sleep(increment_seconds)


class TokenBucket:
    """A token bucket impl based on an atomic, thread-safe counter"""

    def __init__(self, initial=0):
        super().__init__()
        """Initialize a new atomic counter to given initial value"""
        self._value = initial
        self._lock = threading.Lock()

        self.filler = threading.Thread(target=fill_tokens, kwargs={"browser": self}, daemon=True)
        self.filler.start()

    def token_inc(self, num=1):
        """Atomically increment the counter by num and return the new value"""
        with self._lock:
            self._value += num
            return self._value

    @property
    def token_value(self):
        return self._value

    def wait(self):
        """Atomically decrement the counter by num and return the new value"""
        while self._value <= 0:
            time.sleep(0.5) # this probably needs adjustment if you change the token refiller 
        with self._lock:
            if self._value > 0:
                self._value -= 1
                return self._value


class Breadcrumbs:
    def __init__(self):
        lis = []

    def run(self):
        for el in lis:
            el.fetch_safe()


class Throttled:
    def __init__(self, tokens=None, wait=None, driver=None):
        if tokens:
            self.token_bucket = tokens
        else:
            self.token_bucket = TokenBucket()

        if wait:
            self.wait = wait
        else:
            self.wait = WebDriverWait(driver, timeout=10, poll_frequency=2,
                                         ignored_exceptions=[NoSuchElementException,
                                         ElementNotVisibleException,
                                         ElementNotSelectableException])


    def fetch(self):
        raise NotImplementedError()

    def fetch_safe(self, restart=None):
        while True:
            try:
                self.fetch()
            except ScrapingError:
                if restart:
                    restart.run()
            else:
                break


class SearchResults(Throttled):
    def __init__(self, register_type, register_loc, register_number, driver=None, tokens=None):
        super().__init__(tokens, driver=driver)
        self.driver = driver

        self.register_loc = register_loc
        self.register_type = register_type
        self.register_number = register_number

    # depth-first search
    def fetch(self):
        res = self.driver.get('https://www.handelsregister.de/rp_web/welcome.xhtml')

        self.driver.find_element(By.ID,'naviForm:erweiterteSucheLink').click()

        #search_form = self.driver.find_element(By.ID, 'form:schlagwoerter')
        #search_form.send_keys('Saxony Minerals Exploration SME AG')


        reg_typ = self.wait.until(
            EC.presence_of_element_located((By.ID, "form:registerArt"))
        )
        reg_typ.click()

        reg_item = self.driver.find_element(By.XPATH, f"//ul[@id='form:registerArt_items']/li[contains(text(), '{self.register_type}')]")
        ActionChains(self.driver) \
            .move_to_element(reg_item) \
            .pause(0.1) \
            .click(reg_item) \
            .perform()

        reg_loc = self.wait.until(
            EC.presence_of_element_located((By.ID, "form:registergericht"))
        )
        self.driver.execute_script("arguments[0].scrollIntoView()", reg_loc)
        reg_loc.click()

        reg_item = self.driver.find_element(By.ID, "form:registergericht_filter")
        self.driver.execute_script("arguments[0].scrollIntoView()", reg_item)
        ActionChains(self.driver) \
            .move_to_element(reg_item) \
            .pause(0.1) \
            .send_keys(self.register_loc) \
            .send_keys(Keys.ENTER) \
            .perform()

        reg_num = self.driver.find_element(By.ID, 'form:registerNummer')
        self.driver.execute_script("arguments[0].scrollIntoView()", reg_num)
        reg_num.send_keys(self.register_number)


        all_keywords = self.driver.find_element(By.XPATH, "//label[@for='form:schlagwortOptionen:0']")
        self.driver.execute_script("arguments[0].scrollIntoView()", all_keywords)
        all_keywords.click()

        deleted = self.driver.find_element(By.ID, "form:auchGeloeschte")
        self.driver.execute_script("arguments[0].scrollIntoView()", deleted)
        deleted.click()

        submit = self.driver.find_element(By.ID, "form:btnSuche")
        self.driver.execute_script("arguments[0].scrollIntoView()", submit)
        submit.click()

        structured = self.wait.until(
            EC.presence_of_element_located((By.ID, "ergebnissForm:selectedSuchErgebnisFormTable_data"))
        )


class ScrapingError(Exception):
    pass


def error_check(driver):
    err = driver.find_element(By.XPATH, "/html/body/div[1]/div[3]")
    if err.get_attribute("aria-hidden") != "true":
        raise ScrapingError()


# Document view iterator
class DKGenerator(Throttled):
    def __init__(self, driver, tokens=None, wait=None):
        super().__init__(tokens, driver=driver)
        self.cache = set()
        self.driver = driver

        self.wait = wait

        self.root_expr = '//*[@id="dk_form:dktree:0_0"]'
        self.root_clickable = '/span/span[3]'

        self.child_expr = '//ul/li' # this should have class ui-treenode-parent
        self.clickable_child_expr = './/*[contains(@class, "ui-treenode-label")]' # this should have ui-treenode-label

    def _is_leaf(self, path):
        element = self.driver.find_element(By.XPATH, path)
        return 'ui-treenode-leaf' in element.get_attribute('class')

    def _get_res(self, path):
        element = self.driver.find_element(By.XPATH, path)
        return (element, element.find_element(By.XPATH, self.clickable_child_expr))

    def get_xpath(self, elm):
        e = elm
        xpath = elm.tag_name
        i=0 # Счетчик финального элемента
        while e.tag_name != "html":
            if i==0: # Сохраняем родительский элемент финального-искомого (только в первый цикл)
                parent_elm=e.find_element(By.XPATH, "..")
                i+=1
            e = e.find_element(By.XPATH, "..")
            neighbours = e.find_elements(By.XPATH, "../" + e.tag_name)
            level = e.tag_name
            if len(neighbours) > 1:
                level += "[" + str(neighbours.index(e) + 1) + "]"
            xpath = level + "/" + xpath
    
        elm_count=1
        other_elements=parent_elm.find_elements('xpath', elm.tag_name)
        for other_element in other_elements:
            if other_element==elm:
                final_element_count=elm_count
            else:
                elm_count+=1
        if final_element_count>1:
            final_xpath="/" + xpath+f'[{str(final_element_count)}]'
        else:
            final_xpath="/" + xpath
        return final_xpath

    def all(self):
        self.wait.until(EC.presence_of_element_located((By.XPATH, self.root_expr)))

        root_el = self.driver.find_element(By.XPATH, self.root_expr)
        root_click = self.driver.find_element(By.XPATH, self.root_expr + self.root_clickable)

        #yield (root_el, root_click)

        ActionChains(self.driver) \
                .move_to_element(root_click) \
                .pause(0.1) \
                .click(root_click) \
                .pause(0.7) \
                .perform()

        yield from self._get_inc(self.root_expr)

    def _get_inc(self, path):
        print(f"PATH: {path}")
        error_check(self.driver)
        children = [self.get_xpath(el) for el in self.driver.find_elements(By.XPATH, path + self.child_expr)]

        print(f"CHILDS: {len(children)}")

        for path in children:
            if path in self.cache:
                continue
            if self._is_leaf(path):
                self.token_bucket.wait()
                error_check(self.driver)
                yield self._get_res(path)
                self.cache.add(path)
            else:
                element = self.driver.find_element(By.XPATH, path)
                print(f"ELE: {element.get_attribute('innerHTML')}")
                click = element.find_element(By.XPATH, self.clickable_child_expr)
                self.driver.execute_script("arguments[0].scrollIntoView()", click)
                ActionChains(self.driver) \
                    .move_to_element(click) \
                    .pause(0.1) \
                    .click(click) \
                    .pause(0.7) \
                    .perform()
                print("DESCENDING")

                yield from self._get_inc(path)
                self.cache.add(path)

class DKFetcher(Throttled):
    def __init__(self, driver=None, tokens=None):
        super().__init__(tokens, driver=driver)
        self.driver = driver
        self.dk = DKGenerator(driver, wait=self.wait)


    # depth-first search
    def fetch(self):
        button_path = "/html/body/div[1]/div[1]/div[2]/div/div[2]/div/div/div[2]/div/div/div/div[2]/div/form/div/div/div/div[2]/div/table/tbody/tr[9]/td/div/button"
        
        for element, clickable in self.dk.all():
            def click_it(element, clickable):
                print(f"Element: {element.get_attribute('innerHTML')}")
                print(f"Clickable: {clickable.get_attribute('innerHTML')}")

                old_button = self.driver.find_element(By.XPATH, button_path)
                
                self.driver.execute_script("arguments[0].scrollIntoView()", clickable)
                clickable.click()

                self.wait.until(EC.staleness_of(old_button));

                button = self.driver.find_element(By.XPATH, button_path)
                self.driver.execute_script("arguments[0].scrollIntoView()", button)
                button.click()

                self.token_bucket.wait()
            try:
                click_it(element, clickable)
            except (StaleElementReferenceException, NoSuchElementException):
                click_it(element, clickable)


class StructuredData(Throttled):
    def __init__(self, driver=None, tokens=None):
        super().__init__(tokens, driver=driver)
        self.driver = driver

    def fetch(self, tokens=None):
        struc = self.driver.find_element(By.CLASS_NAME, "linksPanel")
        struc.find_element(By.XPATH, "//a[6]").click()

class DKFromResult(Throttled):
    def __init__(self, driver=None, tokens=None):
        super().__init__(tokens, driver=driver)
        self.driver = driver

    def fetch(self):
        struc = self.driver.find_element(By.CLASS_NAME, "linksPanel")
        struc.find_elements(By.XPATH, "//a[contains(@class, 'dokumentList')]")[2].click()

def query_structured(driver, register_type, register_loc, register_number):
    tokens = TokenBucket()
    s1 = SearchResults(register_type, register_loc, register_number, driver=driver, tokens=tokens)
    s2 = StructuredData(driver=driver, tokens=tokens)
    s1.fetch_safe()
    s2.fetch_safe()


def query_docs(driver, register_type, register_loc, register_number):
    tokens = TokenBucket()
    s1 = SearchResults(register_type, register_loc, register_number, driver=driver, tokens=tokens)
    s2 = StructuredData(driver=driver, tokens=tokens)
    s3 = DKFromResult(driver=driver, tokens=tokens)
    s4 = DKFetcher(driver=driver, tokens=tokens)

    s1.fetch_safe()
    s2.fetch_safe()
    s3.fetch_safe()

    crumbs = Breadcrumbs()
    crumbs.lis = [s1, s3]

    s4.fetch_safe(crumbs)

