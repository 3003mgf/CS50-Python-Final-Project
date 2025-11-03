import sys
import re
from pyfiglet import Figlet
from tabulate import tabulate
from classes.user import User
from classes.cart import Cart
from classes.order import Order
from utils import colored_text, read_csv, title_keys, speak

def main():
    speak(text="Welcome to Harvoffe!")
    print(banner(), "This is Harvoffe, the coffee shop of Harvard. In this application you'll be able to pythonically order your favorite coffee so you can be awake in class!", sep="\n", end="\n\n")
    print("You're:", colored_text("Online", "success"), end="\n\n") if User.obtain_session() else print("You're:", colored_text("Disconnected", "alert"), end="\n\n")
    print("\nAvailable Shortcuts:", display_table(file="shortcuts.csv"), sep="\n\n")
    prompt()
    
def banner(text:str="Harvoffe", font:str="catwalk"):
    f = Figlet()
    f.setFont(font=font)
    return f.renderText(text)

def display_table(file:str="") -> str:
    lines:list[dict] = read_csv(file)

    return tabulate(title_keys(lines), headers="keys", tablefmt="rounded_grid")

def prompt():
    while True:
        try:
            prompt = input("Type Here (CTRL + C to exit): ").strip()

            if prompt in ["-r", "--register"]:
                User.init_creation_process()
            elif prompt in ["-m", "--menu"]:
                print(display_table(file="menu.csv"))
            elif prompt in ["-o", "--order"]:
                Order.take()
            elif prompt in ["-auth", "--authenticate"]:
                User.create_session()
            elif prompt in ["-dis", "--disconnect"]:
                User.close_session()
            elif prompt in ["-c", "--cart"]:
                Cart.try_to_open()
            elif prompt in ["-sh", "--shortcuts"]:
                print("\nAvailable Shortcuts:", display_table(file="shortcuts.csv"), sep="\n\n")
            elif prompt in ["-oh", "--orderhistory"]:
                Order.display_user_orders()
            elif pattern := re.search(r"^(?:-t|--ticket) ([A-Z0-9]{6})$", prompt):
                Order.request_ticket(pattern.group(1))

        except (EOFError, KeyboardInterrupt):
            sys.exit(colored_text("\n\nSee you next time!"))

if __name__ == "__main__":
    main()