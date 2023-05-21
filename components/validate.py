import re

def validateEmail(email):
        email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b' # regex do sprawdzania poprawności adresu email
        return (len(email) != 0 and re.fullmatch(email_regex, email))

def validatePassword(password):
        password_regex = r'[A-Za-z0-9@#$%^&+=]{8,}' # minimum 8 znaków, jedyne dozwolone znaki to litery, cyfry i znaki specjalne
        return (len(password) != 0 and re.fullmatch(password_regex, password))