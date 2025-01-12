import re
import ipaddress
from .exceptions import InvalidParameterError

class Validator:
    USERNAME_REGEX = re.compile(r'^[A-Za-z0-9]+$')
    PASSWORD_REGEX = re.compile(r'^[A-Za-z0-9]+$')

    @staticmethod
    def validate_username(username: str, plan_type: str):
        if not Validator.USERNAME_REGEX.match(username):
            raise InvalidParameterError("Username must contain only alphanumeric characters (a-z, A-Z, 0-9).")
        if plan_type == 'residential' and len(username) < 8:
            raise InvalidParameterError("Username must be at least 8 characters long for residential plans.")

    @staticmethod
    def validate_password(password: str, plan_type: str):
        if not Validator.PASSWORD_REGEX.match(password):
            raise InvalidParameterError("Password must contain only alphanumeric characters (a-z, A-Z, 0-9).")
        if plan_type == 'residential' and len(password) < 8:
            raise InvalidParameterError("Password must be at least 8 characters long for residential plans.")

    @staticmethod
    def validate_ip(ip: str):
        try:
            ipaddress.ip_address(ip)
        except ValueError:
            raise InvalidParameterError("IP address must be valid.")

    @staticmethod
    def validate_plan_type(plan_type: str):
        if plan_type not in ['residential', 'isp']:
            raise ValueError("Plan type must be either 'residential' or 'isp'.")