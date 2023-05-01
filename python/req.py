
from typing import NoReturn, Final, TypeVar, NewType
import threading
import sys
import requests
import logging
import os
import subprocess
# # this works now just move into the final file
# word = "cross spawn"
# print(word)
# w = word.replace(' ', '+')
# print(w)
# req = requests.get(f"https://api.npms.io/v2/search?q={w}")
# print(req.json()['results'])


# import aiohttp
# import asyncio


# async def test(url:str) -> str:
#     async with aiohttp.ClientSession() as session:
#         async with session.get(url) as r:
#             print( await r.json())

# loop = asyncio.get_event_loop()
# loop.run_until_complete(test("https://api.npms.io/v2/search?q=express"))


# class Test:
#     def __init__(self,user) -> None:
#         self.email = user.email
#         self.name = user.name

#     def __repr__(self):
#         return self.email
# class User:
#     def __init__(self,name:str,email:str,password:str) -> None:
#         self.name = name
#         self.password = password
#         self.email = email

# class User:
#     name:str
#     password: str
#     email: str

# test:User = "name" , "password", "email"

# print(test)
# user = User("test","test@gmail.com","password")


# test = Test(user)
# print(test)

# req = requests.get(f"https://api.npms.io/v2/search?q=fsdfassdfaf")
# print(req.json()['total'] == 0)
# RED = "\u001b[31m"
# RESET_COLOR= "\u001b[0m"
# def __custom_print(color:str,message:str)-> None:
#     if len(message) <= 0:
#         raise ValueError(f"invalid input for message :{message}")
#     # if not self.__color_check(color):
#     #     raise ValueError("invalid input for color")
#     sys.stdout.write(color + message + RESET_COLOR)
#     sys.stdout.flush()

# test = 10
# ET = TypeVar('ET',bound=BaseException)
# # __custom_print(RED,f"test of f strings {test}")
# def __custom_raise(exception_type:ET,exception_message:str) ->ET:
#     if not type(BaseException) == type(exception_type):
#         raise ValueError("invalid exception type passed!")
#     if type(exception_message) != str:
#         raise ValueError("excption_message must be a string")
#     if len(exception_message) <= 0:
#         raise ValueError("exception_message can not be empty!")
#     return exception_type(exception_message)

# e = __custom_raise(DeprecationWarning,"test of the fucntion")
# raise e
# print(type(BaseException) == type(Exception))
# args = sys.argv
# t = True if len(args) >=2 and (args[1] == "-d" or args[1] == "--default") else False
# print(t)
# path = os.getcwd()
# os.makedirs(os.path.join(path, "../test"))

# subprocess.run(['dir'])
# os.system("dir")

sys.stdout.write("\033[H\033[2J")
sys.stdout.flush()
