# HARVOFFE: Command-Line Coffee Shop Management System

#### Video Demo: <URL HERE>

#### Description:

Harvoffe is a fully functional, command-line interface (CLI) application designed to simulate the user experience and core functionalities of a modern coffee shop's digital ordering system. The application manages user accounts, handles secure authentication via email verification, facilitates in-app cart modification, processes payments using an internal balance system, and stores transaction history for ticket retrieval. The entire application is built using a Python Object-Oriented Programming (OOP) model, ensuring clear separation of concerns between user management, cart logistics, and order processing.

The user interacts with the system through a persistent command prompt, leveraging short, intuitive shortcuts (e.g., `-m` for menu, `-c` for cart) to navigate and execute functions, making the ordering process quick and Pythonic.

### File Structure and Functionality

The project adheres to a clean, modular structure utilizing three primary classes (`User`, `Cart`, `Order`) nested within a `classes` directory, supported by a central `utils.py` helper file.

* **`project.py`:** This is the application's entry point. It initializes the terminal banner (`banner`), checks the user's session status, and runs the perpetual `prompt()` loop. The `prompt` function acts as the **command router**, using conditional logic and regular expressions to parse user input and dispatch the correct method call (e.g., calling `Order.request_ticket` when the pattern `-t [ORDER_ID]` is matched).

* **`classes/user.py`:** Contains the **`User`** and base **`Person`** classes, managing account creation, authentication flow, and balance updates. It handles complex input validation (names, email formats) and orchestrates the two-step secure registration process by interacting with the `Auth` class. User data, including the hashed password and balance, is stored in `users.csv`.

* **`classes/auth.py`:** A stateless utility class dedicated to security. It leverages the **`bcrypt`** library for robust password hashing and verification. Crucially, it manages the **email verification workflow** during registration, sending a temporary, unique code to the user's email via the `utils.send_email` function.

* **`classes/cart.py`:** Manages the user's current order state. It allows the user to open the cart (`try_to_open`), display the contents in a readable table, and enter a sub-prompt (`open`) to modify item quantities (`-a`, `-d`). The centerpiece is the `pay` method, which handles the final checkout, checks the user's balance, calls the `User.update_balance` method, generates a unique order ID, and finally calls the `Order.create` method before trashing the cart data.

* **`classes/order.py`:** Handles all transaction-related history. The `take` method manages the item selection process (inputting `Coffee -q N`). The `display_user_orders` method retrieves, formats, and displays the user's order history, and the `request_ticket` method generates and sends the fully formatted receipt via email.

* **`utils.py`:** A comprehensive collection of helper functions. This file handles all **I/O and external interactions**, including reading/writing CSV data (`read_csv`, `write_csv`), formatting text with ANSI colors (`colored_text`), playing sound effects (`play_sound` using `pygame`), and managing external communication (`send_email` using `smtplib`). It also includes critical initial logic to **suppress non-fatal `pygame` warnings** upon initialization for a clean terminal experience.

### Design Choices and Trade-offs

A significant design decision was the heavy reliance on a **Command-Line Interface (CLI)** and the use of the perpetual `prompt()` loop. This structure made it easy to map user input directly to class methods, providing a fast and efficient workflow.

Another critical choice was utilizing **CSV files** (`users.csv`, `orders.csv`, `carts.csv`) for data persistence instead of a true database. While adequate for this project's scope, a proper database would offer better performance and integrity, especially for concurrent access.

Finally, the design implemented **circular import workarounds** by using local imports (e.g., importing `User` inside `Cart.pay`). This was necessary because the `Cart` needs `User` methods (to check balance/update), and the `Order` needs `User` and `Cart` methods (to process/trash). This solution maintains the clean OOP separation without violating Python's module loading constraints.

### Testing Strategy

Testing was primarily focused on the functional correctness of the stateless utility functions in `project.py`. Due to the constraint of using only `assert` statements instead of the full `unittest` framework, testing of interactive and I/O heavy functions like `prompt()` was limited to basic type checking and error raising, focusing on what could be statically verified without complex mocking of user input and external dependencies. A future improvement would involve using the `unittest.mock` library for robust verification of all input/output commands.