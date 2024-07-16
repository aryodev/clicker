import time
import json
import requests
import threading
import datetime
from datetime import timezone
import random
from colorama import Fore

correct_requests = 0
wrong_requests = 0
lock = threading.Lock()
list_of_operations = []

with open('data.json', 'r') as f:
    data = json.load(f)


def calculate_request_body(data):
    body = {}
    # saved data
    last_request_time = data.get('lastRequestTime', 1717771516)
    last_max_taps = data.get('MaxTaps', 5500)
    last_taps_recover_per_sec = data.get('tapsRecoverPerSec', 10)
    last_earn_per_tap = data.get('earnPerTap', 10)
    last_available_taps = data.get('availableTaps', last_max_taps)

    # calculate request time
    dt = datetime.datetime.now(timezone.utc)
    utc_time = dt.replace(tzinfo=timezone.utc)
    utc_timestamp = utc_time.timestamp()
    body['timestamp'] = utc_timestamp

    # calculate available taps
    time_difference = utc_timestamp - last_request_time
    money_saved = last_available_taps + \
        (time_difference * last_taps_recover_per_sec)
    available_taps = int(
        money_saved) if money_saved < last_max_taps else last_max_taps
    body['availableTaps'] = available_taps

    # calculate count of taps
    count = available_taps // last_earn_per_tap
    # body['count'] = count
    # body['count'] = random.randint(1, 10)
    body['count'] = 1

    return body


def bot(index):
    global correct_requests, wrong_requests
    
    while True:
        
        print(f"{index}: Start to request at {datetime.datetime.now().strftime('%H:%M')}")
        
        body = calculate_request_body(data[index])
        api_key = data[index].get('key', None)
        last_taps_recover_per_sec = data[index].get('tapsRecoverPerSec', 10)
        last_max_taps = data[index].get('MaxTaps', 5500)
        last_earn_per_tap = data[index].get('earnPerTap', 10)
        last_available_taps = data.get('availableTaps', last_max_taps)

        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }

        response = requests.post('https://api.hamsterkombatgame.io/clicker/sync',
                                #  data=json.dumps(body),
                                headers=headers)

        
        result = response.ok

        with lock:
            if result:
                correct_requests += 1
                response_result = json.loads(response.content.decode('utf-8'))
                response_data = response_result.get('clickerUser')

                # Update new data
                updated_last_request_time = body.get('timestamp')
                updated_taps_recover_per_sec = response_data.get(
                    'tapsRecoverPerSec', last_taps_recover_per_sec)
                updated_max_taps = response_data.get('maxTaps', last_max_taps)
                updated_earn_per_tap = response_data.get(
                    'earnPerTap', last_earn_per_tap)
                updated_available_taps = response_data.get(
                    'availableTaps', last_available_taps)

                newbalanceCoins = int(response_data.get('balanceCoins'))

                data[index]['lastRequestTime'] = updated_last_request_time
                data[index]['tapsRecoverPerSec'] = updated_taps_recover_per_sec
                data[index]['MaxTaps'] = updated_max_taps
                data[index]['earnPerTap'] = updated_earn_per_tap
                data[index]['availableTaps'] = updated_available_taps
                data[index]['balanceCoins'] = newbalanceCoins

                # Save updated data to data.json
                with open('data.json', 'w') as f:
                    json.dump(data, f, indent=4)
            else:
                wrong_requests += 1
                print(f'Wrong request with {index} account ; status code {response.status_code}!')
                if response.status_code == 401:
                    break


        sleep_time = random.randint(3600, 10800)
        str_sleep_time = (datetime.datetime.now() + datetime.timedelta(seconds=sleep_time)).strftime('%H:%M')
        operation_text = f'{Fore.GREEN + index}: {datetime.datetime.now().strftime("%H:%M")} , status: {response.status_code}, NewCoins: {Fore.YELLOW}{newbalanceCoins:,}, {Fore.BLUE}{str_sleep_time}'

        print(operation_text)
        list_of_operations.append(operation_text)

        time.sleep(sleep_time)


for item in data:
    threading.Thread(target=bot, args=(item,)).start() 



