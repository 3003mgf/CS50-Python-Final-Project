import os
import json
import uuid
import re
from utils import colored_text, read_csv, write_csv, append_csv
from .auth import Auth


class Person():
    """
    Person class, in case we'd like to add teachers to the application
    """
    def __init__(self, first, last):
        self.first = first
        self.last = last
    
    @property
    def first(self):
        return self._first
    
    @first.setter
    def first(self, first):
        if not re.search(r"^[A-Z]+(?: [A-Z]+)*$", first, re.IGNORECASE):
            raise ValueError("Please provide a valid first, i.e: 'David'")
       
        self._first = first
        
    @property
    def last(self):
        return self._last
    
    @last.setter
    def last(self, last):
        if not re.search(r"^[A-Z]+(?: [A-Z]+)*$", last, re.IGNORECASE):
            raise ValueError("Please provide a valid last, i.e: 'Malan'")

        self._last = last


class User(Person):
    def __init__(self, first, last, email, password):
        super().__init__(first, last)
        self.email = email
        self.password = password
    
    def __str__(self):
        return "Hello " + self.first
    
    # This should use an append_csv from utils
    def create(self) -> None:
        card = self.create_card()
        headers = [
            "first", "last", "email", "password", "card_id", "balance"
        ]
        user = {
            "first": self.first,
            "last": self.last,
            "email": self.email,
            "password": self.password,
            "card_id": card["id"],
            "balance": card["balance"]
        }
        
        if success := append_csv("users.csv", user, headers):
            print(colored_text("\nYour user has been successfully created!\n", "success"))
    
    @classmethod
    def init_creation_process(cls):
        if user_session := cls.obtain_session():
            alert = colored_text(
                "You can't initiate a new registration process while you have an active session.\n"
                "Also, if you already have an account, please do not create another just to obtain more balance.\n"
                "We cannot strictly validate this in this version of the app, but like Python, we rely on the honor system :)", 
                "alert"
            )
            print(alert)
        else:
            first = cls.obtain_name("First ('-e' to exit): ")
            if first is None:
                return print(colored_text("Account creation cancelled", "error"))

            last = cls.obtain_name("Last ('-e' to exit): ")
            if last is None:
                return print(colored_text("Account creation cancelled", "error"))

            email = cls.obtain_email()
            if email is None:
                return print(colored_text("Account creation cancelled", "error"))
        
            password = cls.obtain_password()
            if password is None:
                return print(colored_text("Account creation cancelled", "error"))
            
            user = cls(first, last, email, password)
            
            # Add User to 'users.csv' file (Required)
            return user.create()

    @classmethod
    def get_balance(cls, card_id):
        users = read_csv("users.csv")
        user_balance = None
        for user in users:
            if user["card_id"] == card_id:
                user_balance = user["balance"]
        
        return float(user_balance)

    @classmethod
    def update_balance(cls, card_id, paid):
        try:
            users = read_csv("users.csv")
            for user in users:
                if user["card_id"] == card_id:
                    user["balance"] = float(user["balance"]) - paid

            headers = [
                "first", "last", "email", "password", "card_id", "balance"
            ]
            write_csv('users.csv', users, headers)
        except Exception as error:
            print(error)
            raise Exception("Internal Error: Could not place your order. Send this error to developer: An error occurred while trying to update user's balance (user/update_balance)")

    @classmethod
    def obtain_email(cls) -> str:
        while True:
            email = input("Email ('-e' to exit): ").strip()
            # User exits
            if email in ["-e", "--exit"]: break

            # Validate email format
            if valid := re.search(r"^[a-zA-Z0-9.!#$%&'*+\/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$", email, re.IGNORECASE):
                # Validate if email is not already in use
                if not_used := Auth.check_if_email_is_in_use(email):
                    # Send code and return the code sent
                    if code_sent := Auth.send_verification_code(email):
                        # Ask user for the code, if valid, True is received
                        if verified := Auth.verify_verification_code(code_sent):
                            return email
                        else:
                            # Ask for user email again
                            print(colored_text("Your email couldn't be verified :(", "error"))
                    else:
                        # Couldn't send the code to user's email, due to an internal error probably
                        print(colored_text("Internal error: Couldn't send code to user's email.", "error"))

                else:
                    print(colored_text("It seems you already have an account! (Email is already in use)", "error"))
            else:
                print(colored_text("Invalid email format!", "error"))
                continue

    @classmethod
    def obtain_password(cls) -> str:
        GUIDE = [
            "At least 8 characters in length.",
            "At least one uppercase letter (A-Z).",
            "At least one lowercase letter (a-z).",
            "At least one digit (0-9).",
            "At least one special character (@, $, !, %, *, ?, &)."
        ]
        
        while True:
            password = input("Password ('-e' to exit): ").strip()
            if password in ["-e", "--exit"]: break
            
            if valid := re.search(r"(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}", password):
                return Auth.hash_password(password)
            else:
                # Print error and guide
                print(colored_text("Invalid password. Expected:\n", "error"))
                for i, str in enumerate(GUIDE, start=1):
                    print(i, str, sep=". ")

    @classmethod
    def obtain_name(cls, prompt:str) -> str:
        while True:
            name = input(prompt).strip()
            if name in ["-e", "--exit"]: break

            if not name:
                print(colored_text("Name cannot be empty.", "error"))
                continue
            elif not re.search(r"^[A-Z]+(?: [A-Z]+)*$", name, re.IGNORECASE):
                print(colored_text("Invalid name. Please use letters only.", "error"))
                continue
            else:
                return name

    @classmethod
    def create_session(cls):
        users:list[dict] = read_csv("users.csv")
        user_found = None

        # Prompt for email:
        while True:
            email = input("Email ('-e' to exit): ").strip()
            if email in ["-e", "--exit"]: return False

            found = [user for user in users if user["email"] == email]
            if found != []:
                user_found = found[0]
                break
            else:
                print(colored_text("Could not find any user associated to your email", "error"))
                continue
        
        # Prompt for password:
        while True:
            password = input("Password ('-e' to exit): ").strip()
            if password in ["-e", "--exit"]: return False

            if valid_password := Auth.check_password(password, user_found["password"]):            
                # Create user session
                try:
                    with open("session.json", "w") as file:
                        json.dump({**user_found}, file)
                    break
                except Exception as error:
                    print(f"Internal Error: Couldn't create user session in 'session.json' file.\nSend this error to the developer: {error}")
            else:
                print(colored_text("Invalid password.", "error"))
                continue
        
        # If success:
        success_text = f"Hello {user_found["first"]}! You authenticated successfully, now you're available to add items to your cart and place an order!"
        print(colored_text(success_text, "success"))
        return user_found

    @staticmethod
    def close_session():
        if os.path.exists("session.json"):
            confirm = input("Close your current session? (y/n)").strip().upper()
            if confirm == "Y":
                    os.remove("session.json")
                    print(colored_text("\nSession closed!\n", "success"))

    @staticmethod
    def obtain_session(alert_user=False):
        if os.path.exists("session.json"):
            with open("session.json", "r") as file:
                session_data = json.load(file)
                return session_data
        else:
            if alert_user:
                print(colored_text("Please authenticate (-auth) in order to continue.", "alert"))
            return None

    @staticmethod
    def create_card():
        unique_id = uuid.uuid4()
        INITIAL_BALANCE = 300
        return {"id": unique_id, "balance": INITIAL_BALANCE}
