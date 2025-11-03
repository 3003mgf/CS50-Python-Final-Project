import uuid
from utils import send_email, colored_text, read_csv
import bcrypt

class Auth:
    @staticmethod
    def send_verification_code(send_to:str) -> int:
        code = uuid.uuid4().hex[:6].upper()
        message = {}
        message["Subject"] = "Harvoffe Registration Code"
        message["To"] = send_to

        body = f"""
        Thank you for registering with Harvoffe!
        
        Your verification code is: {code}
        
        Please enter this code in the terminal to complete your registration.
        """
        
        message["Body"] = body
        if code_sent := send_email(message):
            print(colored_text("A verification code has been sent to your email, please retrieve it and type it below!", "alert"))
            return code
    
    @staticmethod
    def verify_verification_code(code_sent:str) -> bool:
        tries = 2
        while tries > 0:
            user_code = input("Verification Code: ")
            if user_code != code_sent:
                if tries == 2:
                    print(colored_text("Incorrect code. You have one more attempt available.", "error"))
                tries -= 1
            else:
                print(colored_text("Your email has been verified!", "success"))
                break

        if tries == 0:
            return False
        
        return True
    
    @staticmethod
    def check_if_email_is_in_use(email:str) -> bool:
        """
        Searchs for existing accounts linked to the email received
        """
        users = read_csv("users.csv")
        return True if not [user for user in users if user["email"] == email] else False

    @staticmethod
    def hash_password(password:str) -> str:
        password_bytes = password.encode('utf-8')
        # 1. Generate salt and hash
        salt = bcrypt.gensalt()
        hashed_password_bytes = bcrypt.hashpw(password_bytes, salt)
        # 2. Decode the bytes object into a string for storage
        return hashed_password_bytes.decode('utf-8')

    @staticmethod
    def check_password(password:str, hashed_password:str) -> bool:
        """
        Check if the pass received is equal to the hashed pass received
        """
        try:
            # 1. Convert both the attempt and the stored hash to bytes (bcrypt requires bytes)
            password_bytes = password.encode('utf-8')
            hashed_password_bytes = hashed_password.encode('utf-8')
            
            # 2. Perform the check
            return bcrypt.checkpw(password_bytes, hashed_password_bytes)
        except Exception as error:
            print(f"Internal error: Couldn't validate if your password matches the one stored.\nSend this error to the developer ('/user.py/check_password'): {error}")
            return False