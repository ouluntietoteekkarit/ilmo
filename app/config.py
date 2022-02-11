import os
from werkzeug.security import generate_password_hash, check_password_hash
from typing import Tuple, Dict

def load_auth_config() -> Tuple[Dict[str, str], Dict[str, str]]:
    users = {}
    roles = {}
    try:
        file = open("auth.conf", "r")
        for line in file.readlines():
            new_user = line.split(",", 6)
            users[new_user[0]] = new_user[1]
            roles[new_user[0]] = new_user[2:6]

        file.close()
    except FileNotFoundError as e:
        password = os.urandom(64).hex()
        users['admin'] = generate_password_hash(password)
        roles['admin'] = 'admin'
        
        print(e)
        print("auth.conf not found")
        print("For production, create auth.conf with proper users and hashed passwords")
        print("username: admin")
        print("password: " + password)

    return (users, roles)


def load_route_conf() -> bool:
    kapsi = False
    try:
        with open("routes.conf", "r") as file:
            lines = file.readlines()

            for line in lines:
                conf_line = line.split(":", 2)

                if "kapsi" in conf_line[0]:
                    kapsi = "true" in conf_line[1]

    except FileNotFoundError as e:
        print(e)
        print("routes.conf not found")

    return kapsi