import json
import re
import uuid
from tabulate import tabulate
from datetime import datetime
from utils import read_csv, colored_text, write_csv, append_csv, play_sound, title_keys

class Cart:
    def __init__(self, card_id, cart):
        self.card_id = card_id
        self.cart = cart
    
    @property
    def card_id(self):
        return self._card_id
    
    @card_id.setter
    def card_id(self, card_id):
        if hasattr(self, "_card_id"):
            print(colored_text("Field 'card_id' can't be modified!", "error"))
        else:
            self._card_id = card_id
    
    @property
    def cart(self):
        return self._cart
    
    @cart.setter
    def cart(self, cart):
        self._cart = cart

    def open(self):
        while True:
            prompt = input("Modify Cart ('-e' to exit): ")

            # Exit
            if prompt in ["-e", "--exit"]: 
                break

            # Pay
            elif prompt in ["-p", "--pay"]: 
                self.pay()

            # Help
            elif prompt in ["-h", "--help"]: 
                print(colored_text("\nThis is your cart. You can update your items quantity with these shortcuts:\n\n  - To ADD an item: Use '-a' or '--add' (Macchiato -a 3)\n  - To DELETE an item: Use '-d' or '--delete' (Americano -d 1)\n  - To pay: Use '-p' or '--pay' (-p)\n", "gray"))
            
            # Validate user command
            elif matches := re.search(r"^([a-zA-Z]+(?: [a-zA-Z]+)?) (-a|--add|-d|--delete) ([1-9]\d*)$", prompt):
                coffee = matches.group(1).title()
                is_addition = True if matches.group(2) in ["-a", "--add"] else False
                quantity = int(matches.group(3))

                found = [index for index, item in enumerate(self.cart) if item["coffee"] == coffee]
                if found != []:
                    found_index = found[0]
                    self.update_quantity(index=found_index, quantity=quantity, is_addition=is_addition)
                    continue
                else:
                    # Item is not in the cart
                    print(colored_text(f"\nError: Could not find '{coffee}' in your cart!\n", "error"))
                    continue
            elif not matches:
                print(colored_text("\nInvalid command. Expected format: 'Macchiato (-a|--add|-d|--delete) \\d'\n", "error"))
                continue
    
    def update_quantity(self, index:int, quantity:int, is_addition:bool):
        # Update the cart and also update 'carts.csv'
        carts:list = read_csv("carts.csv")
        plural = "s" if quantity > 1 else ""
        coffee_targeted = self.cart[index]["coffee"]

        if is_addition:
            self.cart[index]["quantity"] += quantity
            
            success_txt = f"\n{quantity} {coffee_targeted + plural} has been added successfully! Currently in order: {self.cart[index]["quantity"]}\n"
            print(colored_text(success_txt, "gray"))
        elif is_addition is False:
            # Not enough coffees to delete
            if quantity > self.cart[index]["quantity"]:
                error_txt = f"\nCould not delete {quantity} {coffee_targeted + plural} from your cart, you only have {self.cart[index]["quantity"]}\n"
                print(colored_text(error_txt, "alert"))
            else:
                
                if self.cart[index]["quantity"] - quantity == 0:
                    # If substraction consequence is quantity being 0, update quantity and delete object from cart:
                    self.cart = [obj for obj in self.cart if obj["coffee"] != coffee_targeted]
                    
                    success_txt = f"\n{quantity} {coffee_targeted + plural} has been deleted successfully! Currently in order: None\n"
                    print(colored_text(success_txt, "gray"))
                else:
                    # If substraction consequence is not quantity being 0, just update quantity:
                    self.cart[index]["quantity"] -= quantity
                    success_txt = f"\n{quantity} {coffee_targeted + plural} has been deleted successfully! Currently in order: {self.cart[index]["quantity"]}\n"
                    print(colored_text(success_txt, "gray"))
                    
 
        # Update the cart in 'carts' with the updated version
        for cart in carts:
            if cart["card_id"] == self.card_id:
                cart["cart"] = json.dumps(self.cart) # This is because 'cart' in 'carts.csv' expect a str in JSON format

        # Rewrite entire 'carts.csv' to keep the user cart updated and persistant
        write_csv(file="carts.csv", rows=carts, headers=["card_id", "cart"])

    def get_total(self):
        total = 0
        for item in self.cart:
            total += (item["price"] * item["quantity"])
        
        return round(total, 2)

    def pay(self):
        # Break the circular import
        from .user import User
        from .order import Order

        if user_session := User.obtain_session():
            print(colored_text("\n*** Checkout Section ***\n", "gray"))
            print(colored_text(f"Hey {user_session["first"]}! Ready for your coffee? Check everything is correct and if so, just type 'Y' to pay!\n", "gray"))
            total = self.get_total()
            user_balance = User.get_balance(user_session["card_id"])
            enough_balance = True if user_balance >= total else False

            # Client
            print("Client:", user_session["first"])
            # Order Total
            print("Order Total:", colored_text(f"{total:.2f}", "success"))
            # User Balance
            print("Your Balance:", colored_text(f"{user_balance:.2f}", "alert"), end="\n\n")

            # Confirmation
            proceed = input("Pay? (Y/N) ").strip().upper()
            if proceed ==  "Y":
                if enough_balance:
                    try:
                        # Modify user balance in 'users.csv' (Put inside User class 'update_balance')
                        User.update_balance(user_session["card_id"], total)

                        # Create order ID
                        order_id = uuid.uuid4().hex[:6].upper()
                        # Create order using 'Order' class
                        Order.create(
                            id=order_id,
                            card_id=user_session["card_id"], 
                            client=user_session["first"] + " " + user_session["last"],
                            date=datetime.now().strftime("%b %d, %Y %H:%M:%S"),
                            total=total,
                            items=json.dumps(self.cart)
                        )
                        
                        # Tell the user his purchase succeeded :)
                        play_sound("sounds/cash_register.mp3")
                        print(colored_text("\nYour order has been successfully processed!\n", "success"))
                        print(colored_text(f"You can pick up your items at the Harvoffe store whenever you're ready.", "gray"))
                        print(colored_text(f"Your order ID is:", "gray"), order_id, colored_text("(You will need this ID to claim your order)\n", "gray"))

                        # Trash the cart
                        self.trash()

                        # Ask the user if he needs a ticket
                        asked_for_ticket = input("Do you need a ticket? (Y/N) ").strip().upper()
                        if asked_for_ticket == "Y":
                            Order.request_ticket(order_id)

                    except Exception as error:
                        print(colored_text(str(error), "error"))
                else:
                    print(colored_text("\nYou don't have enough balance!\n", "error"))
    
    def trash(self):
        carts = read_csv("carts.csv")
        deleted = [cart for cart in carts if cart["card_id"] != self.card_id]
        write_csv("carts.csv", deleted, ["card_id", "cart"])
        self.cart = []
    
    @classmethod
    def try_to_open(cls):
        # Break the circular import
        from .user import User

        if user_session := User.obtain_session(alert_user=True):
            user_cart = cls.get_user_cart(user_session["card_id"])
            # print("\n", banner("Cart"))

            if user_cart == []:
                print(colored_text("You cart is currently empty. To add items into it, type '-o|--order'.", "gray"))
            else:
                CART_HELP_TEXT = "\n*** Your Cart ***\n\nThis is your cart. You can update your items quantity with these shortcuts:\n\n  - To ADD an item: Use '-a' or '--add' (Macchiato -a 3)\n  - To DELETE an item: Use '-d' or '--delete' (Americano -d 1)\n  - To pay: Use '-p' or '--pay' (-p)\n"
                print(colored_text(CART_HELP_TEXT, "gray"))
                
                # Build the cart to be displayed
                cart = []
                cart_total = 0

                # Calculate unit_price, total, etc.
                for index, item in enumerate(user_cart):
                    cart_total += (item["price"] * item["quantity"])

                    obj = {}
                    obj["item"] = item["coffee"]
                    obj["unit_price"] = item["price"]
                    obj["quantity"] = item["quantity"]
                    obj["total"] = f"{item["price"] * item["quantity"]:.2f}"

                    cart.append(obj)

                    # If we're in the last item, we need to add the row that will display the total (last row of the table)
                    if index + 1 == len(user_cart):
                        # To Pay (USD)                  [N]
                        last_obj = {}
                        last_obj["item"] = colored_text("To Pay (USD)", "success")
                        last_obj["unit_price"] = None
                        last_obj["quantity"] = None
                        last_obj["total"] = colored_text(f"{cart_total:.2f}", "success")

                        cart.append(last_obj)
                
                cart_table = tabulate(title_keys(cart), headers="keys", tablefmt="rounded_grid")
                print(cart_table)

                cart = cls(user_session["card_id"], user_cart)
                cart.open()

    @classmethod
    def update_user_cart(cls, card_id:str, cart:list) -> None:
        carts = read_csv("carts.csv")
        cart_found_index = None

        json_cart = json.dumps(cart)
        headers = ["card_id", "cart"]

        if len(carts) > 0:
            for index, obj in enumerate(carts):
                if obj["card_id"] == card_id:
                    cart_found_index = index

        if cart_found_index is None:
            # Cart didn't exist in 'carts.csv' (or 'carts.csv' didn't exist), so we add the cart to the CSV
            append_csv(file="carts.csv", row={"card_id": card_id, "cart": json_cart}, headers=headers)
        else:
            # Cart already existed in 'carts.csv', so we update user cart, and rewrite the entire 'carts.csv'
            carts[cart_found_index]["cart"] = json_cart
            write_csv(file="carts.csv", rows=carts, headers=headers)

    @classmethod
    def get_user_cart(cls, card_id=None):
        carts = read_csv(file="carts.csv")
        user_cart = []

        for cart in carts:
            if cart["card_id"] == card_id:
                user_cart = json.loads(cart["cart"])

        return user_cart
    