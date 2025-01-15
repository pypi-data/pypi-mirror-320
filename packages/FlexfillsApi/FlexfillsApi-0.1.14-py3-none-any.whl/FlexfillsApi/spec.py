import os
from flexfillsapi import initialize


def login_flexfills():
    flexfills_api = initialize(
        'flexfills_username', 'flexfills_password', True)

    print("Login Successful")


if __name__ == "__main__":
    login_flexfills()
