import datetime
from urllib import response
import requests
import traceback
from logging import info, error, basicConfig, ERROR, INFO
from datetime import date
import time
import pathlib

from seleniumwire import webdriver
from selenium.webdriver.common.by import By

import logging
logger = logging.getLogger('seleniumwire')
logger.setLevel(logging.ERROR)


chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('log-level=3')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--single-process')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument("--incognito")
chrome_options.add_argument('ignore-certificate-errors')
chrome_options.add_argument('--disable-blink-features=AutomationControlled')
chrome_options.add_argument('--disable-blink-features=AutomationControlled')
chrome_options.add_experimental_option('useAutomationExtension', False)
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
#chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
#wll crash somehow chrome
chrome_options.add_argument("disable-infobars")   
chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36')

#works!
#chrome_options.add_argument("--headless")

driver = webdriver.Chrome('chromedriver.exe', options=chrome_options)


class RevGen:
    
    def __init__(self) -> None:

        self.smsverification = True
        self.gennumb = ""
        self.baseurl = "https://business.revolut.com/api/"
        self.CURRENT_USER = self.baseurl + "user/current"
        self.cardnumb = 0
        self.mode = input("What do you want to do?\n> Generate Cards (1)\n> Get all card Details (2)\n")
        if self.mode == "1":
            self.gennumb = input("How many cards do you want to generate? > ")
            print("Running Gen Mode")
        elif self.mode == "2":
            self.gennumb = input("Where do you want to start? (use 0) > ")
            print("Running Detail Mode")
        else:
            print("Invalid.")
            driver.quit()

        self.email = input("Revolut Email: ")
        self.password = input("Revolut Password: ")
        print("Running...")
        



        self.cookienew = ""
        self.deviceid = ""
        self.ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36"
        
        self.headers_post =  {
            'pragma': 'no-cache',
            'cache-control': 'no-cache',
            'sec-ch-ua': '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
            'accept': 'application/json, text/plain, /',
            'sec-ch-ua-mobile': '?0',
            'user-agent': self.ua,
            'x-device-id': self.deviceid,
            'content-type': 'application/json;charset=UTF-8',
            'origin': 'https://business.revolut.com/',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': 'https://business.revolut.com/',
            'accept-language': 'en-US;q=0.9',
            'cookie': f'token={self.cookienew}',
        }
        
        self.headers_get = {
            'pragma': 'no-cache',
            'cache-control': 'no-cache',
            'sec-ch-ua': '"Google Chrome";v="93", " Not;A Brand";v="99", "Chromium";v="93"',
            'accept': 'application/json, text/plain, */*',
            'sec-ch-ua-mobile': '?0',
            'user-agent': self.ua,
            'x-device-id': self.deviceid,
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': 'https://business.revolut.com/',
            'accept-language': 'en-US;q=0.9',
            'cookie': f'token={self.cookienew}',        
        }

        
        
        self.s = requests.Session()
        self.csv_location = f'{pathlib.Path(__file__).parent.resolve()}\\cards.csv'
        

        
        self.get_newcookie()

        self.business_id = self.get_business()
        if not self.business_id:
            raise RuntimeError("Cannot Get Business API")
        if self.kyc_status != "PASSED":
            raise RuntimeError("Account Unverified")
        
        self.BASE_URL = self.baseurl + f"business/{self.business_id}"
        
        self.get_members()
        self.getcardid()
        
        if self.mode == "1":
            for n in range(0, int(self.gennumb)):
                self.cardnumb = n
                self.log_info("Generating Card ")
                self.gen_cards()
                self.log_info("Generated Card ")
                labeled = self.label_cards(n+int(self.gennumb),self.card_id)
                if labeled:
                    self.log_info(f"Labeled Card {n+int(self.gennumb)}")
                    if self.smsverification:
                        self.get_card_details(self.card_id)
        
        elif self.mode == "2":
            for n in range(int(self.gennumb), len(self.json)):
            # only get card details. NO CARD GEN!
                self.cardnumb = n
                if self.smsverification:
                    self.get_card_details(self.json[n]["payload"]["id"])
                    
        

    def update(self):
        self.headers_post =  {
            'pragma': 'no-cache',
            'cache-control': 'no-cache',
            'sec-ch-ua': '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
            'accept': 'application/json, text/plain, /',
            'sec-ch-ua-mobile': '?0',
            'user-agent': self.ua,
            'x-device-id': self.deviceid,
            'content-type': 'application/json;charset=UTF-8',
            'origin': 'https://business.revolut.com/',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': 'https://business.revolut.com/',
            'accept-language': 'en-US;q=0.9',
            'cookie': f'token={self.cookienew}',
        }
        
        self.headers_get = {
            'pragma': 'no-cache',
            'cache-control': 'no-cache',
            'sec-ch-ua': '"Google Chrome";v="93", " Not;A Brand";v="99", "Chromium";v="93"',
            'accept': 'application/json, text/plain, */*',
            'sec-ch-ua-mobile': '?0',
            'user-agent': self.ua,
            'x-device-id': self.deviceid,
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': 'https://business.revolut.com/',
            'accept-language': 'en-US;q=0.9',
            'cookie': f'token={self.cookienew}',        
        }
                
    @staticmethod
    def log_info(*args, **kwargs):
        
        timestamp = datetime.datetime.now().strftime('%H:%M:%S.%f')[:-3]
        st,en = '\033[92m','\033[0m'
        output =  f"{st}[{str(timestamp)}] {args[0]}{en}"
        basicConfig(format="%(message)s", level=INFO)
        info(output)  
        
        
    @staticmethod
    def log_error(*args, **kwargs):
        st,en = '\033[91m','\033[0m'
        timestamp = datetime.datetime.now().strftime('%H:%M:%S.%f')[:-3]
        output =  f"{st}[{str(timestamp)}] {args[0]}{en}"
        basicConfig(format="%(message)s", level=ERROR)
        error(output)  


    def get_newcookie(self):
        
        driver.get('https://business.revolut.com/overview')
        
        time.sleep(5)
        try:
            aktion = driver.find_element(By.NAME,'username')
            aktion.send_keys(self.email)
            button = driver.find_elements(By.XPATH,"//*[contains(text(), 'Continue with email')]")
            button[0].click()
        except:
            print("No Login required")
    
        time.sleep(5)
    
        try:
            pw = driver.find_element(By.NAME,'password')
            pw.send_keys(self.password)
            button = driver.find_elements(By.XPATH,"//*[contains(text(), 'Log in')]")
            button[0].click()
            print("Mobile App Confirmation")
            time.sleep(15)

        except:
            print("No Login required")

        time.sleep(5)
        cookies = driver.get_cookies()
        for cookie in cookies:
            if "token" in str(cookie):
                print("Token found in Cookies")
                self.cookienew = cookie["value"]
                break
        time.sleep(2)
        for request in driver.requests:  
            if request.response:  
                if str(request.url).endswith("/verifications"):
                    print("Your Device id: "+str(request.headers.get("x-device-id")))
                    self.deviceid = request.headers.get("x-device-id")
                    break
                
        print("Your session token "+self.cookienew)
        self.update()

    def get_business(self):
        
        self.log_info("Getting Business")
        print(self.headers_get)
        response = self.s.get(
            self.CURRENT_USER,
            headers=self.headers_get
            )
        
        if "This action is forbidden" in response.text:
            self.get_newcookie()
            self.get_business()
            print("Token expired. Getting a new one")
            return
        
        try:
            parsed = response.json()

            self.kyc_status = parsed["kyc"]
            business_id = parsed["businessId"]
            return business_id
        except:
            self.log_error(f"Error Parsing API: {response.status_code} - {response.text} - {traceback.format_exc()}")
            
    
    def get_members(self):

        self.log_info("Getting Team Members")
        
        response = self.s.get(
            f"{self.BASE_URL}/team/members",
            headers=self.headers_get
        )
        
        if "This action is forbidden" in response.text:
            self.get_newcookie()
            self.get_members()
            print("Token expired. Getting a new one")
            return
        
        try:
            parsed = response.json()
            self.current_member = [m for m in parsed if m["email"] == self.email][0]
            try:
                self.employee_id = self.current_member["employee"]["id"]
            except:
                self.employee_id = ""
                
            self.user_id = self.current_member["user"]["id"]
        except:
            self.log_error(f"Error Parsing API: {response.status_code} - {response.text} - {traceback.format_exc()}")   
            
    
    def send_sms(self, x):
        resp_code = 'resp'
        print(f' Sending SMS...')
        while not '"Verification required","code":9014,"factor":"SMS"' in resp_code:
            response = self.s.get(
                f"{self.BASE_URL}/card/{x}/image/unmasked?encrypt=false",
                headers=self.headers_get
            )
            resp_code = response.text
            if "This action is forbidden" in response.text:
                self.get_newcookie()
                self.get_business()
                print("Token expired. Getting a new one")
                return

            if '"Cannot create a new verification code at that moment","code":9015' in resp_code:
                print(f' Error sending SMS waiting 5 seconds and requesting new cookie...')
                self.get_newcookie()
                time.sleep(5)

        print('SMS code sent')


    def get_card_details(self,x):
        self.send_sms(x)
        Resend = True
        while Resend:
            self.sms_code = input(f'Card {str(self.card_num)}: Enter sms code (type "1" to send sms again): ') 
            if self.sms_code == "1":
                self.send_sms(x)  
            else:
                Resend = False

        self.verify_headers = {
            'pragma': 'no-cache',
            'cache-control': 'no-cache',
            'sec-ch-ua': '"Google Chrome";v="93", " Not;A Brand";v="99", "Chromium";v="93"',
            'accept': 'application/json, text/plain, */*',
            'sec-ch-ua-mobile': '?0',
            'user-agent': self.ua,
            'x-device-id': self.deviceid,
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': 'https://business.revolut.com/',
            'accept-language': 'en-US;q=0.9',
            'cookie': f'token={self.cookienew}', 
            'x-verify-code': f'{self.sms_code}',
        }
        response = self.s.get(
            f"{self.BASE_URL}/card/{x}/image/unmasked?encrypt=false",
            headers=self.verify_headers
        )

        if "This action is forbidden" in response.text:
            self.get_newcookie()
            self.get_business()
            print("Token expired. Getting a new one")
            return
        try:
            self.card_num = response.json()["pan"]
            self.card_cvv = response.json()["cvv"]
            self.card_exp_month = f'0{str(date.today().month)}'
            self.card_exp_year = str(date.today().year + 5)
            self.write_card_details()
        except:
            choice = input(f' Wrong sms code wanna try again? y/n: ')
            if choice == "y":
                print("getting a new cookie. Please wait!")
                self.get_newcookie()
                self.get_card_details(x)
            else:
                return
        


    def getcardid(self):

        self.verify_headers = {
            'pragma': 'no-cache',
            'cache-control': 'no-cache',
            'sec-ch-ua': '"Google Chrome";v="93", " Not;A Brand";v="99", "Chromium";v="93"',
            'accept': 'application/json, text/plain, */*',
            'sec-ch-ua-mobile': '?0',
            'user-agent': self.ua,
            'x-device-id': self.deviceid,
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': 'https://business.revolut.com/',
            'accept-language': 'en-US;q=0.9',
            'cookie': f'token={self.cookienew}',        
        }
        response = self.s.get(
            f"{self.BASE_URL}/team/members/current-member/cards",
            headers=self.verify_headers
        )

        if "This action is forbidden" in response.text:
            self.get_newcookie()
            self.get_business()
            print("Token expired. Getting a new one")
            return
        
        try:
            self.json = response.json()
            
        except:
            print("error")

    def write_card_details(self):
        with open(self.csv_location, 'a') as fd:
            fd.write(f'\ncard,{self.card_num},{self.card_exp_month},{self.card_exp_year},{self.card_cvv}')


    # functions for card gen
    def gen_cards(self):
        
        payload = {
            "includedToExpenseManagement":True,
            "linkAllAccounts":True,
            "email": self.email,
            "employeeId": self.employee_id,
            "userId": self.user_id,
            "personal":True
        }
        
        response = self.s.post(
            f'{self.BASE_URL}/card/virtual/order',
            headers=self.headers_post,
            json=payload
        )
        
        if "This action is forbidden" in response.text:
            self.get_newcookie()
            self.gen_cards()
            print("Token expired. Getting a new one")
            return
        
          
        try:
            self.card_id = response.json()["id"]
        except:
            self.log_error(f"Error Parsing API: {response.status_code} - {response.text} - {traceback.format_exc()}")   
        
    
    def label_cards(self, prefix, x):
        
        self.log_info("Labeling Card")   
        
        payload = {"label": f"Card {prefix}"} 

        self.card_name = f"Card {prefix}"

        response = self.s.patch(
            f'{self.BASE_URL}/card/{x}/label',
            headers=self.headers_post,
            json=payload
            )
        
        try:
            return response.json()["state"] == "ACTIVE"
        except:
            self.log_error(f"Error Parsing API: {response.status_code} - {response.text} - {traceback.format_exc()}") 

if __name__ == "__main__":
    pass

RevGen()
        
            
                 
        
        
        
            