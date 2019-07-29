
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait  # available since 2.4.0
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium import webdriver
import smtplib
import time
import datetime
import calendar
import schedule
import yagmail
from dateutil import relativedelta


week_time=[8, 8, 8, 8, 8, 0, 0]

def getWeekTimeframe():
    ct=datetime.datetime.now()
    start = ct - datetime.timedelta((ct.weekday()) % 7)
    end = ct - datetime.timedelta((ct.weekday()+1) % 7 - 7)
    return (start, end)

def formatDateForEmail(timeframe):
    start, end=timeframe
    return "{:%m/%d} - {:%m/%d}".format(start,end)
    
def formatDateForScreenshot(timeframe):
    start, end=timeframe
    return "{:%m-%d} - {:%m-%d}".format(start,end)

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

        save = browser.find_element_by_xpath("//button[contains(.,'Submit')]")
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
        browser.save_screenshot("Timesheet Wilk, Ryan "+formatDateForScreenshot(getWeekTimeframe())+".png")
    else:
        exit(1)
    browser.close()

def sendEmailViaGmail():
    send_from='wilk.ryan14@gmail.com'
    send_to=['rjw1428@gmail.com']
    subject = "Timesheet - "+formatDateForEmail(getWeekTimeframe())+" - Wilk"
    body='Hi Dan,\n\nAttached is my timesheet for the week.\n\nRegards,\nRyan'
    email_text="""\From: %s To: %s Subject: %s %s """%(send_from, ', '.join(send_to), subject, body)
    try:
        print("Sending Message with Gmail")
        yag=yagmail.SMTP(user='wilk.ryan14@gmail.com', password="Bball@1428")
        # # server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        # server.ehlo()
        # server.starttls()
        # print("  - Logging in")
        # server.login('wilk.ryan14@gmail.com', 'Bball@1428')
        # print("  - Login Successful")
        yag.send(send_to, subject, email_text)
        # server.sendmail(send_from, send_to, email_text)
        print("  - Mail Send")
        # server.close()
        print("  - Server Closed")
    except:
        print('Something went wrong...')

def sendEmailViaOutlook():
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
            time.sleep(1)
            to[0].send_keys(Keys.TAB)
        else:
            exit(1)
        
        to[0].send_keys(Keys.TAB)
        time.sleep(1)
        browser.switch_to_active_element().send_keys(Keys.TAB)
        time.sleep(1)
        # browser.switch_to_active_element().send_keys(Keys.TAB)
        # time.sleep(1)
        browser.switch_to_active_element().send_keys("cmcnelly@teksystems.com")
        to[1].send_keys(Keys.TAB)
        time.sleep(1)
        browser.switch_to_active_element().send_keys(Keys.TAB)
        time.sleep(1)
        browser.switch_to_active_element().send_keys("Timesheet - "+formatDateForEmail(getWeekTimeframe())+" - Wilk")

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
    
    time.sleep(120)
    # browser.close()

def main():
    # doWebStuff()
    # sendEmailViaOutlook()
    sendEmailViaGmail()

main()
# schedule.every().friday.at('11:00').do(lambda: main())

# alert=True

# while True:
#     if datetime.datetime.now().weekday()==4 and alert:
#         print("TASK SCHEDULED FOR TODAY AT 11:00")
#         alert=False
#     elif datetime.datetime.now().weekday()!=4:
#         alert=True
#     schedule.run_pending()

