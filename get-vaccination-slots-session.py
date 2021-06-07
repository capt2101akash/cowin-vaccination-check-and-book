import json
import requests
import time
import telebot
import sched
import re
import traceback
import hashlib
from http_request_randomizer.requests.proxy.requestProxy import RequestProxy
# import Chrome
from time import sleep
from datetime import datetime, timedelta
from telethon.sync import TelegramClient
from telethon import TelegramClient
from seleniumwire import webdriver
from ipaddress import IPv4Address
from pyairmore.request import AirmoreSession
from webdriver_manager.chrome import ChromeDriverManager
from pyairmore.services.messaging import MessagingService
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver import DesiredCapabilities
from svg_parser import *

# 
sleep_time = 5

def get_centers(url, headers):
    response = requests.get(url, headers=headers)
    try:
        response = json.loads(response.text)
    # print(response["centers"])
        return response["centers"]
    except Exception as e:
        print(response.text)
        return []

def get_slots(centers, age):
    center_name = centers.get('name', 'N/A')
    center_id = centers.get('center_id')
    pincode = centers.get('pincode')
    slots = dict()
    slots[center_name] = {'fee_type': centers.get('fee_type')}
    for session in centers['sessions']:
        session_date = session.get('date')
        vaccine = session.get('vaccine')
        slots_time = session.get('slots')
        if len(slots_time) > 0:
            preffered_slot = slots_time[-1]
        else:
            preffered_slot = 'N/A' 
        session_id = session.get('session_id')
        slots_available = session.get("available_capacity", "N/A")
        dose_1 = session.get("available_capacity_dose1", "N/A")
        dose_2 = session.get("available_capacity_dose2", "N/A")
        age_limit = session.get("min_age_limit", "N/A")
        slots[center_name][session_date] = {'pincode': pincode, 'center_id': center_id, 'session_id': session_id, 'preffered_slot':preffered_slot, 'vaccine': vaccine, age_limit:{"total_slots":slots_available, "dose1": dose_1, "dose2": dose_2}}
    return slots

def get_auth_code(smsService, txn_id, otp_verify_url, headers):
    messages = smsService.fetch_message_history()
    
    otp = re.search('(\d)\w+', messages[0].content)
    otp = str(otp[0])
    sha_otp = hashlib.sha256(otp.encode()).hexdigest()
    otp_verify = {"otp": sha_otp, "txnId": txn_id}
    otp_verify = json.dumps(otp_verify)
    otp_verify_response = requests.post(otp_verify_url, headers=headers, data=otp_verify)
    otp_verify_response = json.loads(otp_verify_response.text)
    auth_code = otp_verify_response["token"]
    return auth_code

def main():
    androidIP = IPv4Address('Ip of phone')
    androidSession = AirmoreSession(androidIP)
    smsService = MessagingService(androidSession)
    capabilities = DesiredCapabilities.CHROME
    current_date = datetime.now().strftime('%d-%m-%Y')
    capabilities["loggingPrefs"] = {"performance": "ALL"} 
    age = '18+'
    api_id = # telegram api id
    api_hash = #telegram api hash
    phone = #phone number
    client = TelegramClient('anon', api_id, api_hash)
    otp_url = "https://cdn-api.co-vin.in/api/v2/auth/public/generateOTP"
    login_url = "https://selfregistration.cowin.gov.in/"
    schedule_url = "https://cdn-api.co-vin.in/api/v2/appointment/schedule"
    captcha_url = "https://cdn-api.co-vin.in/api/v2/auth/getRecaptcha"
    otp_verify_url = "https://cdn-api.co-vin.in/api/v2/auth/validateMobileOtp"
    client.connect()
    
    try:
        headers = {'accept': '*/*', 'referer': 'https://selfregistration.cowin.gov.in/','access-control-request-method': 'GET','access-control-request-headers': 'authorization', 'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36', 'accept': 'application/json', 'origin': 'https://selfregistration.cowin.gov.in'}
        response = requests.post('https://cdn-api.co-vin.in/api/v2/auth/generateMobileOTP', headers=headers, data=get_otp)
        response = json.loads(response.text)
        txn_id = response["txnId"]
        sleep(15)
        try:
            auth_code = get_auth_code(smsService, txn_id, otp_verify_url, headers)
        except Exception as e:
            print(e)
            sleep(20)
            auth_code = get_auth_code(smsService, txn_id, otp_verify_url, headers)
            
        # driver.quit()
        print(auth_code)
        headers = {'accept': '*/*', 'referer': 'https://selfregistration.cowin.gov.in/','access-control-request-method': 'GET','access-control-request-headers': 'authorization', 'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36', 'accept': 'application/json', 'origin': 'https://selfregistration.cowin.gov.in', "Authorization": f"Bearer {auth_code}"} # This is chrome, you can set whatever browser you like
        
        if not client.is_user_authorized():
        
            client.send_code_request(phone)
                
                # signing in the client
            client.sign_in(phone, input('Enter the code: '))
        receivers = {
                        'User':['pincodes']
                    }
        start = time.time()
        stop = time.time()
        pincodes = [
            ]
        while 1:
            for pincode in pincodes:
                availability_url = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/calendarByPin?"
                availability_url = f"{availability_url}pincode={pincode}&date={current_date}"
                centers = get_centers(availability_url, headers)
                if centers is not None:
                    all_slots = dict()
                    for center in centers:
                        all_slots = get_slots(center, age)
                        slot_45 = 0
                        slot_18 = 0
                        for users in receivers.keys():
                            globals()[f'{users}_otp_count'] = 0
                        total_slots = 0
                        for center_name, v1 in all_slots.items():
                            fee_type = v1['fee_type']
                            for date, age_group in v1.items():
                                if date != 'fee_type':
                                    center_id = age_group.get('center_id')
                                    vaccine = age_group.get('vaccine')
                                    session_id = age_group.get('session_id')
                                    preffered_slot = age_group.get('preffered_slot')
                                    slot_45 = age_group.get(45, {'total_slots': 0, 'dose1': 0, 'dose2': 0})
                                    slot_18 = age_group.get(18, {'total_slots': 0, 'dose1': 0, 'dose2': 0})
                                    total_slots += slot_45['total_slots'] + slot_18['total_slots']
                                    # print(pincode, center_name, date, total_slots, slot_18['dose1'])
                                    if slot_45['dose1'] > 0:
                                        
                                        for user, pin in receivers.items():
                                            dose1_45 = slot_45["dose1"]
                                            dose2_45 = slot_45["dose2"]
                                            total_slots_45 = slot_45['total_slots']
                                            message = f'Hey! @{user} {total_slots_45} Vaccination slot available for {vaccine} at {center_name} in {pincode} for 45+ age group for {fee_type} on {date}. There are "{dose1_45}" DOSE-1 and "{dose2_45}" DOSE-2 slots available. Login here - https://selfregistration.cowin.gov.in/'
                                            if pincode in pin[:-1] and user in []:
                                                print(f"Sending notification to {user} for pincode {pincode} for 45+")
                                                otp_obj = {"mobile": pin[-1]}
                                                otp_obj = json.dumps(otp_obj)
                                                if globals()[f'{user}_otp_count'] == 0:
                                                    x = requests.post(otp_url, data=otp_obj, headers=headers)
                                                client.send_message(user, message, parse_mode='html') 
                                                globals()[f'{user}_otp_count']+=1
                                    elif slot_18['dose1'] > 0:
                                        for user, pin in receivers.items():
                                            dose1_18 = slot_18["dose1"]
                                            dose2_18 = slot_18["dose2"]
                                            total_slots_18 = slot_18['total_slots']
                                            message = f'Hey! @{user} {total_slots_18} Vaccination slot available for {vaccine} at {center_name} in {pincode} for 18+ age group for {fee_type} on {date}. There are "{dose1_18}" DOSE-1 and "{dose2_18}" DOSE-2 slots available. Login here - https://selfregistration.cowin.gov.in/'
                                            if pincode in pin[:-1]:
                                                print(f"Sending notification to '{user}' - '{dose1_18}' doses available in pincode '{pincode}' for '{vaccine}' on '{date}' for 18+")
                                                if user == '' and ('COVISHIELD', 'SPUTNIK') in vaccine:
                                                    captcha_data = {}
                                                    # print(headers)
                                                    # captcha_dict = requests.post(captcha_url, data=captcha_data, headers=headers)
                                                    # print(captcha_dict.text)
                                                    # captcha_svg = json.loads(captcha_dict.text)["captcha"]
                                                    # # print(captcha_svg)
                                                    # captcha = parse_svg(captcha_svg)
                                                    booking_data = {}
                                                    booking_data = json.dumps(booking_data)
                                                    schedule_result = requests.post(schedule_url, data=booking_data, headers=headers)
                                                    
                                                client.send_message(user, message, parse_mode='html')
                                                globals()[f'{user}_otp_count']+=1
                        if total_slots == 0:
                            name_of_center = center.get('name', 'N/A')
                            message = f"<b>No<b> Vaccination slots available at {name_of_center}"
                else:
                    pass  
                sleep(5)
            stop = time.time()
            if (stop - start) >= 100:
                client.disconnect()
                break
    except Exception as e:
        traceback.print_exc()
        print(e)
        client.disconnect()
        

while True:
    main()
    

