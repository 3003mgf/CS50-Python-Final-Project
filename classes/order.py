import re
import json
from utils import append_csv, colored_text, read_csv, send_email, play_sound, title_keys
from tabulate import tabulate
from operator import itemgetter

class Order:
    
    @classmethod
    def take(cls):
        # Break circular import
        from .user import User
        from .cart import Cart

        if user_session := User.obtain_session(alert_user=True):
            # print("\n", banner("Order"))
            print(colored_text("\n*** Place Order ***\n\nTips to place your order:\n1. You can add items to your order with this command 'COFFEE [-q \\d]'\n2. To open your cart and modify it, just type '-c|--cart'\n", "gray"))
            
            menu:list[dict] = read_csv(file="menu.csv")
            cart = Cart.get_user_cart(card_id=user_session["card_id"])
            cart_updated:bool = False

            # Take user order
            while True:
                command = input("Add to Order ('-e' to exit): ").strip()
                if command in ["-e", "--exit"]: break

                if valid := re.search(r"^([a-zA-Z]+(?: [a-zA-Z]+)?)( -q [1-9]\d*)?$", command):
                    coffee, quantity = valid.groups()

                    if found := [item for item in menu if item["coffee"] == coffee.title()]:
                        cart_updated = True
                        quantity:int = 1 if quantity is None else int(quantity.split(" ")[-1])

                        if already_in_cart := [(index, item) for index, item in enumerate(cart) if item["coffee"] == coffee.title()]:
                            # If item was already in the cart, update the quantity
                            index = already_in_cart[0][0]
                            item = already_in_cart[0][1]

                            cart[index]["quantity"] += quantity
                            print(colored_text(f"{item['coffee']} added! In order: {cart[index]["quantity"]}", "gray"))
                        elif not already_in_cart:
                            # If items was not in the cart already, insert the entire item obj (found[0])
                            cart.append({"coffee": found[0]["coffee"], "price": float(found[0]["price"]), "quantity": quantity})
                            print(colored_text(f"{found[0]['coffee']} added! In order: {quantity}", "gray"))
                    elif not found:
                        # If coffe not found, i.e: 'Apple Juice -q 3'
                        print(colored_text("Could not find that Coffee in our menu.", "error"))
                elif not valid:
                    # If invalid format, i,e: 'Macchiato -q three'
                    print(colored_text("Invalid command. Expected format: 'Macchiato [-q \\d]'", "error"))

            # Add user cart to 'carts.csv'
            if cart_updated:
                Cart.update_user_cart(card_id=user_session["card_id"], cart=cart)

    @classmethod
    def request_ticket(cls, order_id:str):
        # Break circular import
        from .user import User

        if user_session := User.obtain_session(alert_user=True):
            confirm = input(colored_text(f"\nRequest ticket for order {order_id}? (Y/N) ", "gray")).strip().upper()
            if confirm == "Y":
                orders = read_csv("orders.csv")
                if order_found := [order for order in orders if order["id"] == order_id]:
                    if ticket_sent := cls.send_ticket(user_session["email"], order_found[0]):
                        # Success
                        print(colored_text("\nDone!", "success"))
                        print(colored_text("\nYour ticket has been successfully sent to your email!\n", "gray"))
                        
                        # Play sound
                        play_sound("sounds/receipt.mp3")
                else:
                    # No order found, meaning the ID provided was incorrect
                    print(colored_text("\nCouldn't find an order associated to that ID.\n", "error"))

    @classmethod
    def create(cls, id, card_id, client, date, total, items):
        try:
            order = {
                "id": id,
                "card_id": card_id,
                "client": client,
                "date": date,
                "total": total,
                "items": items
            }
            
            headers = ["id", "card_id", "client", "date", "total", "items"]

            append_csv("orders.csv", order, headers)
        except Exception:
            raise Exception("Internal Error: Could not place your order. Send this error to developer: An error occurred while trying to append order into 'orders.csv' (order/create)")
    
    @classmethod
    def display_user_orders(cls):
        # Break circular import
        from .user import User

        if user_session := User.obtain_session(alert_user=True):
            if orders := cls.get_user_orders(card_id=user_session["card_id"]):

                table = tabulate(title_keys(orders), headers="keys", tablefmt="rounded_grid")
                print(colored_text("\n*** Order History ***\n\nThis section displays a list of all your past orders, sorted from the latest to the oldest.\nYou can request a printable PDF ticket for any order using its ID and the shortcut '-t' or '--ticket':\n\n- Usecase: '--ticket [ORDER_ID]'\n", "gray"))
                print(table)

            else:
                # User doesn't have any orders placed
                print(colored_text("You don't have any orders yet. To place an order type '-o|--order'!", "gray"))
    
    @staticmethod
    def get_user_orders(card_id:str) -> list:
        orders = read_csv("orders.csv")
        user_orders = []

        for order in orders:
            if order["card_id"] == card_id:
                str = "" # Items in str format, i.e: 'Macchiato (2), Americano (3), ...

                for index, item in enumerate(json.loads(order["items"])):
                    # If is not the first item, add a ", " to the str
                    separator = "" if index == 0 else ", "
                    str += f"{separator}{item["coffee"]} ({item["quantity"]})"

                order["items"] = str
                
                # Delete 'card_id' since is not needed and is a bit long, affecting the visualization of the orders
                del order["card_id"]

                # Insert order into 'user_orders'
                user_orders.append(order)

        # Return user orders sorted by date, in descending order (latest to oldest)
        return sorted(user_orders, key=itemgetter("date"), reverse=True)
    
    @staticmethod
    def send_ticket(send_to:str, order:dict) -> bool:
        message = {}
        message["Subject"] = f"Your Harvoffe Order Receipt – #{order["id"]}"
        message["To"] = send_to
        
        body = f"======================================\n           Harvoffe Coffee         \n======================================\nORDER RECEIPT\n\nOrder ID: {order['id']}\nDate: {order['date']}\nCustomer ID: {order['card_id']}\nClient: {order['client']}\n--------------------------------------\nITEMS PURCHASED:\n--------------------------------------\n{"".join(f"{item['coffee']} ({item['quantity']})\n" for item in json.loads(order['items']))}--------------------------------------\nSUBTOTAL: {order['total']}\nTAX: 0\nTOTAL PAID: {order['total']}\n\nThank You for Your Order!\nPickup ID: {order['id']}\n======================================\n"

        message["Body"] = body

        if ticket_sent := send_email(message):
            return True
        
        return False


