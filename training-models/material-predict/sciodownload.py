import argparse, time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import selenium.webdriver.support.ui as ui

parser = argparse.ArgumentParser(description='Downloading and processing data from the SCiO sensor.')
parser.add_argument('-u', '--username', help='Username', required=True)
parser.add_argument('-p', '--password', help='Password', required=True)
parser.add_argument('-c', '--collection_name', help='Collection Name', required=True)
args = parser.parse_args()

driver = webdriver.Chrome()
wait = ui.WebDriverWait(driver, 10)

# Login to SCiO Lab
driver.get('https://sciolab.consumerphysics.com/#/login')
driver.switch_to.frame(driver.find_element_by_id('login-iframe'))

username = driver.find_element_by_id('username')
wait.until(lambda driver: driver.find_element_by_id('username').is_displayed())
username.send_keys(args.username)
password = driver.find_element_by_id('password')
password.send_keys(args.password)
password.send_keys(Keys.ENTER)

# Wait for SCiO webpage to load
wait.until(lambda driver: driver.find_element_by_id('collection-name-0').is_displayed())

# Get the collection id
time.sleep(0.5)
collection_id = driver.find_element_by_xpath("//*[contains(text(), '%s')]" % args.collection_name).find_element_by_xpath('..').find_element_by_xpath('..').find_element_by_xpath('..').get_attribute('col_id')
# driver.find_element_by_xpath("//*[contains(text(), 'Lakshmi')]").find_element_by_xpath('..').click()

# Open up specific collection
# driver.get('https://sciolab.consumerphysics.com/#/collections/f596a03f-5c67-47a9-83f3-51a7e2b6fc54/samples')
driver.get('https://sciolab.consumerphysics.com/#/collections/%s/samples' % collection_id)

# Get rid of "New features" dialog if it pops up
wait.until(lambda driver: (driver.find_element_by_id('confirm-modal-close').is_displayed() and driver.find_element_by_id('confirm-modal-close').is_enabled()) or driver.find_element_by_css_selector('header.title.clearfix').find_element_by_css_selector('button.app.btn-ok.action.pull-right.ng-binding.ng-scope').is_displayed())
time.sleep(0.5)
if driver.find_element_by_id('confirm-modal-close').is_displayed() and driver.find_element_by_id('confirm-modal-close').is_enabled():
    driver.find_element_by_id('confirm-modal-close').click()

# Open the download data dialog
time.sleep(0.5)
header = driver.find_element_by_css_selector('header.title.clearfix')
header.find_element_by_css_selector('button.app.btn-ok.action.pull-right.ng-binding.ng-scope').click()

# Click on the download button
popup = driver.find_element_by_css_selector('div.popup-content.download-collection-panel.ng-scope')
popup.find_element_by_css_selector('button.btn.app.btn-ok.ng-binding').click()

# driver.quit()


