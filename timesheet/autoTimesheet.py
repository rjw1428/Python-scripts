
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait  # available since 2.4.0
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium import webdriver
import smtplib
import time

week_time=[8, 8, 8, 8, 8, 0, 0]

def doWebStuff():
    browser = webdriver.Chrome()
    browser.get(
        "https://budget.lightning.force.com/lightning/n/My_Capitalization_Form_LC")
    browser.implicitly_wait(10)
    element = browser.find_element_by_class_name('customhyperlink')
    if element.is_displayed():
        element.click()
        inputBox = browser.find_elements_by_class_name('uiInputNumber')
        for i in range(0, len(week_time)):
            if inputBox[i].is_displayed():
                inputBox[i].clear()
                inputBox[i].send_keys(str(week_time[i]))

        save = browser.find_element_by_xpath("//button[contains(.,'Save')]")
        if save.is_displayed():
            save.click()
        else:
            exit(1)
    else:
        exit(1)

    # GET START & END OF WEEK DATE
    time.sleep(5)
    element = browser.find_element_by_class_name('customhyperlink')
    if element.is_displayed():
        element.click()
    else:
        exit(1)

    inputBox = browser.find_elements_by_class_name('uiInputNumber')
    if inputBox[0].is_displayed():
        browser.save_screenshot("Timesheet Wilk, Ryan.png")
    else:
        exit(1)
    browser.close()


def sendEmail():
    browser = webdriver.Chrome()
    browser.get(
        "https://webmail.comcast.com")

    browser.implicitly_wait(10)
    new_button = browser.find_element_by_id('_ariaId_26')
    if new_button.is_displayed():
        new_button.click()
        to = browser.find_elements_by_class_name('_fp_G')
        if to[0].is_displayed():
            to[0].send_keys("dmadden@teksystems.com")
        else:
            exit(1)
        
        to[0].send_keys(Keys.TAB)
        time.sleep(1)
        browser.switch_to_active_element().send_keys(Keys.TAB)
        browser.switch_to_active_element().send_keys("cmcnelly@teksystems.com")
        to[1].send_keys(Keys.TAB) #browser.switch_to_active_element().send_keys(Keys.ENTER).send_keys(Keys.TAB)
        time.sleep(1)
        browser.switch_to_active_element().send_keys(Keys.TAB)
        browser.switch_to_active_element().send_keys("Timesheet - <<DATE>> - Wilk")

    # subject_line = browser.find_element_by_class_name('_mcp_o1').find_element_by_class_name('_mcp_82').find_element_by_id('_mcp_c')
    # if subject_line.is_displayed():
    #     subject_line.send_keys("Timesheet - <<DATE>> - Wilk")
    # else:
    #     exit(1)

    time.sleep(1)
    message = browser.find_element_by_class_name('_mcp_32')
    if message.is_displayed():
        message.send_keys("Hi Dan,")
        message.send_keys(Keys.ENTER)
        message.send_keys(Keys.ENTER)
        message.send_keys("Attached is my timesheet for the week.")
        message.send_keys(Keys.ENTER)
        message.send_keys(Keys.ENTER)
        message.send_keys('Regards,')
        message.send_keys(Keys.ENTER)
        message.send_keys('Ryan')
    else:
        exit(1) 
    
    time.sleep(1)
    attach_button=browser.find_element_by_class_name('_mcp_72')
    if attach_button.is_displayed():
        attach_button.click()
        el=browser.switch_to_active_element()
        # print(el)
        # time.sleep(1)
        # actions=ActionChains(browser)
        # actions.send_keys(Keys.TAB)
        # actions.send_keys("Timesheet")
        # actions.perform()
    else:
        exit(1)
    
    time.sleep(20)
    # browser.close()


sendEmail()
