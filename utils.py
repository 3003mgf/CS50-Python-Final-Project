import warnings
warnings.filterwarnings(action="ignore", module="pygame.pkgdata")
from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

import csv
import smtplib
from email.message import EmailMessage
import pygame
import pyttsx3 

def colored_text(text: str, color_key: str="") -> str:
    """Returns text wrapped in ANSI escape codes for color."""

    COLOR_MAP = {
        "success": "\033[92m",  # Bright Green
        "error": "\033[91m",    # Bright Red
        "gray": "\033[37m",     # Bright Gray
        "alert": "\033[93m",    # Bright Yellow
    }
    RESET = "\033[0m"

    # Use .get() with a default value to avoid a KeyError if color_key is bad
    ansi_color = COLOR_MAP.get(color_key, RESET) 

    return ansi_color + text + RESET

def read_csv(file:str) -> list:
    lines:list = []
    with open(file, "r", newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            # Replace all '\n' in the CSV for actual line breaks. If we don't do this, line breaks added in the CSV are not recognized as line breaks
            row = {key: value.replace("\\n", "\n") for key, value in row.items()}
            lines.append(row)

    return lines

def write_csv(file:str, rows:list[dict], headers:list[str]) -> bool:
    try:
        with open(file, "w") as file:
            writer = csv.DictWriter(file, fieldnames=headers)
            writer.writeheader()
            writer.writerows(rows)
    except Exception as error:
        print(f"Internal error: Could not write into '{file}'.\nSend this to developer: {error}")
        return False
    else:
        return True
    
def append_csv(file:str, row:list[dict], headers:list[str]) -> bool:
    try:
        with open(file, "a") as file:
            writer = csv.DictWriter(file, fieldnames=headers)
            writer.writerow(row)
    except Exception as error:
        print(f"Internal error: Could not append into '{file}'.\nSend this to developer: {error}")
        return False
    else:
        return True
    
def play_sound(file_path:str="") -> None:
    pygame.mixer.init()
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()

def speak(text:str=""):
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)  # Words per minute
    engine.say(text)
    engine.runAndWait()
    engine.stop()

def send_email(message) -> bool:
    
    credentials = {
        "SENDER_EMAIL": "[YOUR GMAIL ADDRESS]",
        "SENDER_PASSWORD": "[YOUR APP PASSWORD]"
    }
    
    e_message = EmailMessage()
    e_message["Subject"] = message["Subject"]
    e_message["To"] = message["To"]
    e_message.set_content(message["Body"])

    try:
        # Use GMail's SMTP server (port 587 for TLS)
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(credentials["SENDER_EMAIL"], credentials["SENDER_PASSWORD"])
            server.send_message(e_message)
            
    except Exception as error:
        print(colored_text(f"Internal error: Couldn't send email to user. Send this error to the developer: {error}", "error"))
        return False
    else:
        return True
    
def title_keys(data:list[dict]):
    titled_data = []

    for d in data:
        obj = {
            key.replace("_", " ").title(): value for key, value in d.items()
        }
        titled_data.append(obj)
        
    return titled_data

# To check if we need it
def is_init(obj, attr, alert) -> bool:
    """
    Used in setters. Checks if the attr trying to be modified exists already, meaning the class has been initialized. If so, returns False, so we can block the assignment. This is of course used in setters where we don't want the attr to be modified once created, such as in Orders.
    :return: boolean
    :rtype: bool
    """
    if hasattr(obj, attr):
        # Is not init
        print(alert)
        return False
    else:
        # Is init
        return True
