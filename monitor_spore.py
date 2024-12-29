import requests
import time
import json
from datetime import datetime
from urllib.parse import urlencode

def send_to_discord(webhook_url, message):
    try:
        payload = {
            "content": message,
            "username": "Spore Monitor",
            "avatar_url": "https://www.spore.fun/favicon.ico"
        }
        requests.post(webhook_url, json=payload)
    except Exception as e:
        print(f"Error sending to Discord: {e}")

def fetch_spore_data():
    url = 'https://www.spore.fun/api/trpc/status,listAgent'
    headers = {
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        'content-type': 'application/json',
        'priority': 'u=1, i',
        'referer': 'https://www.spore.fun/',
        'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'trpc-accept': 'application/jsonl',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'x-trpc-source': 'nextjs-react'
    }
    
    params = {
        'batch': '1',
        'input': '{"0":{"json":null,"meta":{"values":["undefined"]}},"1":{"json":null,"meta":{"values":["undefined"]}}}'
    }
    
    try:
        full_url = f"{url}?{urlencode(params)}"
        response = requests.get(full_url, headers=headers)
        response.raise_for_status()
        data = [json.loads(line) for line in response.text.strip().split('\n') if line.strip()]
        return data
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

def find_agent_6(data):
    try:
        for item in data:
            if 'json' in item and isinstance(item['json'], list):
                if len(item['json']) > 2 and isinstance(item['json'][2], list):
                    for sublist in item['json'][2]:
                        if isinstance(sublist, list) and len(sublist) > 0:
                            for agent_list in sublist:
                                if isinstance(agent_list, list):
                                    for agent in agent_list:
                                        if isinstance(agent, dict) and agent.get('id') == 6:
                                            return agent
                                elif isinstance(agent_list, dict) and agent_list.get('id') == 6:
                                    return agent_list
    except Exception as e:
        print(f"Error parsing data: {e}")
    return None

def monitor_token_address(webhook_url, check_interval=5): 
    last_token_address = None
    check_count = 0
    
    print("Starting monitoring of Agent 6's token address...")
    print(f"Checking every {check_interval} seconds...")
    
    send_to_discord(webhook_url, "🟢 Spore Monitor started - watching Agent 6's token address")
    
    while True:
        check_count += 1
        current_time = datetime.now().strftime('%H:%M:%S')
        print(f"[{current_time}] Check #{check_count} - ", end='', flush=True)
        
        data = fetch_spore_data()
        if data:
            agent = find_agent_6(data)
            if agent:
                current_token_address = agent.get('tokenAddress', '')
                print(f"Current token address: {current_token_address or 'empty'}")
                
                if last_token_address is None:
                    message = f"📡 Initial token address: {current_token_address or 'empty'}"
                    send_to_discord(webhook_url, message)
                elif current_token_address != last_token_address:
                    message = (
                        f"🔔 **Token Address Change Detected!**\n"
                        f"Time: {current_time}\n"
                        f"Old: {last_token_address or 'empty'}\n"
                        f"New: {current_token_address or 'empty'}"
                    )
                    print(f"\n{'='*50}")
                    print(message)
                    print(f"{'='*50}\n")
                    send_to_discord(webhook_url, message)
                
                last_token_address = current_token_address
            else:
                print("Could not find Agent 6 in the response")
        else:
            print("Error fetching data")
        
        time.sleep(check_interval)

if __name__ == "__main__":
    DISCORD_WEBHOOK_URL = ""
    
    try:
        monitor_token_address(DISCORD_WEBHOOK_URL)
    except KeyboardInterrupt:
        print("\nMonitoring stopped by user")
        send_to_discord(DISCORD_WEBHOOK_URL, "🔴 Spore Monitor stopped") 