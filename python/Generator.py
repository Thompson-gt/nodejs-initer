# NOTE explaniation how to use callable because its my first time
# callable syntax is a type hint that defines the return value and the inputs
# takes a array as input callable can be anything that gets called, in my case i used it with exceptions
#                       example:Callable[[1...n number of arguments to callable]return value from callable]
from typing import NoReturn, Final, TypeVar, Callable, Optional
import os
import json
import sys
import time
import aiohttp
# was used for the __new__query method
# import asyncio
import requests
import threading
# inherit the threading class to allow methods in the class to be multithreaded

# enum for all of the colors
from .colors import Color, RESET_COLOR


class Generator(threading.Thread):
    # this will be the max time out for the threads when joining
    __THREAD_TIMEOUT: Final[float] = 5.0
    # genric for custom raise function to so it can be genertic for all of the exceptions that inherit from base
    ET = TypeVar('ET', bound=BaseException)
    # on versions 3.10 they added a type hint for aliasing but im on 3.9 so cant hint but the
    # linker pickes up on it
    # alias for the funcion to build exceptions more info where the alias is used
    ExceptionType = Callable[[str], ET]

    def __init__(self) -> None:
        # have to pass a referance of self to the thread construction
        # for some reason because it makes it threading work in the methods
        threading.Thread.__init__(self)
        self.args = sys.argv
        self.path: str = ""
        self.name: str = ""
        self.desc: str = ""
        self.author: str = ""
        self.js_type: str = ""
        self.dependecies: list[str] = []
        self.error_depens: list[str] = []
        # lock to protect the package object
        self.package_lock: threading.Lock = threading.Lock()
        # the lock to protect the error array
        self.error_lock: threading.Lock = threading.Lock()
        self.start_time = time.time()
        self.ts = False

    def __clear_screen(self) -> None:
        # escape codes that are used to clear the screen
        sys.stdout.write("\033[H\033[2J")
        sys.stdout.flush()
        # move the screen down
        # print("\n" * 10)
        return

    def __check_for_flags(self,) -> bool:
        return len(self.args) >= 2 and (self.args[1] == "-d" or self.args[1] == "--default")

    def __get_project_home(self) -> str:
        printable = ""
        choice = ""
        io = ""
        try:
            choice = input(
                "relative or absolute path for the project?\n").lower()
            printable = "relative" if choice[0] == 'r' else "absolute"
            io = input(
                f"where do you want the project to live:({printable})\n")
            if not self.__valid_user_input(choice, printable, io):
                raise ValueError
        except ValueError:
            i = input(
                Color.get_color(Color.YELLOW)+"there was an error when the inputed value! would you like to re-enter the value?\n"+RESET_COLOR).lower()
            if i[0] == "y":
                choice = input(
                    "relative or absolute path for the project?\n").lower()
                printable = "relative" if choice[0] == 'r' else "absolute"
                io = input(
                    f"where do you want the project to live:({printable})\n")
            else:
                self.__handle_exit()
        finally:
            path = os.getcwd() + io
            return os.path.join(path, "src") if printable == 'relative' else os.path.join(io, "src")

    def __get_module_type(self) -> str:
        io = ""
        try:
            io = input(
                "what type of javascript:\n Module(m):\n Commonjs(c):\n").lower()
            if not self.__valid_user_input(io):
                raise ValueError
        except ValueError:
            io = self.__handle_value_erorr()
        finally:
            self.__clear_screen()
            self.__custom_print(Color.CYAN, "module type", begining_tab=True,
                                seperator="->", ending_newline=True, post_seperator=io)
            return "module" if io[0] == 'm' else "commonjs"

    def __js_or_ts(self,) -> None:
        io = ""
        try:
            io = input(
                "would you like to use typescript or javascript\n").lower()
            if not self.__valid_user_input(io):
                raise ValueError
            if len(io) > 0 and io[0] == "t":
                self.ts = True
                self.__build_tsconfig()
                self.__build_dst_dir()
                self.__clear_screen()
                self.__custom_print(Color.CYAN, "js or ts -> typescript", begining_tab=True,
                                    seperator="->", ending_newline=True, post_seperator=io)
            else:
                self.__clear_screen()
                self.__custom_print(Color.CYAN, "js or ts -> javascript", begining_tab=True,
                                    seperator="->", ending_newline=True, post_seperator=io)
        except ValueError:
            self.__custom_print(Color.YELLOW,
                                "invalid input, will default to javascript")

    def create_git_ignore(self) -> None:
        self.__custom_print(Color.GREEN, "creating the .git file...")
        try:
            with open(os.path.join(self.path, ".gitignore"), 'w') as f:
                if self.ts:
                    f.write("./tsconfig.json\n")
                f.write("./package.json\n")
                f.write("./env\n")
        except FileExistsError:
            i = input(
                Color.get_color(Color.YELLOW)+"the gitignore file already exists!\n would you like to overwrite the file?"+RESET_COLOR).lower()
            if not self.__valid_user_input(i):
                self.__custom_raise(ValueError, "invalid user input")
            if i == "y" or i == "yes":
                os.remove(os.path.join(self.path, ".gitignore"))
                with open(os.path.join(self.path, ".gitignore"), 'w') as f:
                    f.write(".package.json\n")
                    f.write(".env")
            else:
                self.__handle_exit()

    def create_env_file(self) -> None:
        self.__custom_print(Color.GREEN, "creating the .env file...")
        try:
            with open(os.path.join(self.path, ".env"), 'w') as f:
                f.write("DB_URI=? \n")
                f.write("PORT=8080")
        except FileExistsError:
            i = input(
                Color.get_color(Color.YELLOW)+"the env file already exists!\n would you like to overwrite the file?"+RESET_COLOR).lower()
            if not self.__valid_user_input(i):
                self.__custom_raise(ValueError, "invalid user input")
            if i == "y" or i == "yes":
                os.remove(os.path.join(self.path, ".gitignore"))
                with open(os.path.join(self.path, ".env"), 'w') as f:
                    f.write("DB_URI=? \n")
                    f.write("PORT=8080")
            else:
                self.__handle_exit()

    def create_index_file(self) -> None:
        ending = ".ts" if self.ts else ".js"
        self.__custom_print(
            Color.GREEN, f"creating the index{ending} file ...")
        try:
            with open(os.path.join(self.path, f"index{ending}"), 'w') as f:
                if self.js_type == "commonjs":
                    f.write("const dotenv = require('dotenv').config();\n")
                    f.write("const express = require('express');\n\n\n")
                else:
                    f.write("import * as dotenv from 'dotenv';\n")
                    f.write("import express from 'express';\n\n\n ")
                f.write("const app = express()\n\n")
                f.write("app.use(json())\n\n")
                f.write(
                    "app.listen(process.env.PORT || 5000,()=> console.log('sever is running'))")
        except FileExistsError:
            i = input(
                Color.get_color(Color.YELLOW)+"the index.js file already exists!\n would you like to overwrite the file?"+RESET_COLOR).lower()
            if not self.__valid_user_input(i):
                self.__custom_raise(ValueError, "invalid user input")
            if i == "y" or i == "yes":
                os.remove(os.path.join(self.path, ".gitignore"))
                with open(os.path.join(self.path, f"index{ending}"), 'w') as f:
                    if self.js_type == "commonjs":
                        f.write("const dotenv = require('dotenv').config();\n")
                        f.write("const express = require('express');\n\n\n")
                    else:
                        f.write("import * as dotenv from 'dotenv';\n")
                        f.write("import express from 'express';\n\n\n ")
                f.write("const app = express()\n\n")
                f.write("app.use(json())\n\n")
                f.write(
                    "app.listen(process.env.PORT || 5000,()=> console.log('sever is running'))")
            else:
                self.__handle_exit()

    def __build_tsconfig(self,) -> None:
        self.__custom_print(Color.GREEN, "building the typescript config")
        config = {}
        # set configurations for the tsc compiler
        config["compilerOptions"] = {}
        config["compilerOptions"]["target"] = "es2021"
        config["compilerOptions"]["module"] = "ES6" if self.js_type == "module" else "CommonJS"
        config["compilerOptions"]["strict"] = True
        config["compilerOptions"]["removeComments"] = True
        config["compilerOptions"]["preserveConstEnums"] = True
        config["compilerOptions"]["outDir"] = "dist"
        config["compilerOptions"]["noImplicitAny"] = True
        # specities the dir for the compiled js
        config["include"] = ["src/**/*"]
        try:
            with open(os.path.join(self.path, "../tsconfig.json"), 'w') as f:
                json.dump(config, f)
        except FileExistsError:
            raise self.__custom_raise(
                FileExistsError, "package.json already exits!")
        except json.JSONDecodeError:
            raise self.__custom_raise(
                BaseException, "unexpected error when serializing the package object")

    def create_package_json(self) -> None:
        self.__custom_print(Color.GREEN, "creating the package.json...")
        package = {}
        package["name"] = self.name
        package["version"] = "1.0.0"
        package["description"] = self.desc
        package["main"] = "index.js"
        package["type"] = self.js_type
        package["scripts"] = {
            "test": "echo "
        }
        if "nodemon" in self.dependecies:
            package["scripts"]["start"] = "nodemon index.js"
        if self.ts:
            package["scripts"]["build"] = "tsc build "
            package["scripts"]["run"] = "node dist/index.js"

        package["author"] = self.author
        package["license"] = "ISC"
        package["dependencies"] = {}
        # this is the loop for the async code
        # loop = asyncio.get_event_loop()
        # loop.run_until_complete(self.__new_query_npm(package))
        threads = self.__get__threads(package)
        self.__handle_threads(threads)
        try:
            with open(os.path.join(self.path, "package.json"), 'w') as f:
                json.dump(package, f)
        except FileExistsError:
            raise self.__custom_raise(
                FileExistsError, "package.json already exits!")
        except json.JSONDecodeError:
            raise self.__custom_raise(
                BaseException, "unexpected error when serializing the package object")

    def __get__threads(self, package: dict) -> list[threading.Thread]:
        threads = []
        try:
            for d in self.dependecies:
                t = threading.Thread(
                    target=self.__threaded_query_npm, args=(package, d))
                threads.append(t)
                t.start()
            return threads
        except:
            raise self.__custom_raise(
                threading.ThreadError, "error when creating the thread")

    def __handle_threads(self, threads: list[threading.Thread]) -> None:
        try:
            for thread in threads:
                thread.join(timeout=self.__THREAD_TIMEOUT)
        except:
            raise self.__custom_raise(
                threading.ThreadError, "error when joining the thread")

    def display_final_message(self) -> None:
        self.__clear_screen()
        n = len(self.error_depens)
        __error = f"WARNING:\n {n} of your entered dependices were not found when creating project!\n "
        __success = "Project has been generated!\nHAVE FUN CODING!"
        if n == 0:
            self.__custom_print(Color.GREEN, __success)
            self.__custom_print(Color.YELLOW,
                                f"took: {time.time() - self.start_time}s")
        else:
            self.__custom_print(Color.YELLOW, __error)
            self.__display_error_depens()

    def __display_error_depens(self) -> None:
        for d in self.error_depens:
            self.__custom_print(
                Color.YELLOW, f"{d} not found!\n please check npm site to see if that dependice exists")

    @property
    def project_path(self) -> str:
        return self.path

    def __build_dst_dir(self,) -> None:
        try:
            os.makedirs(os.path.join(self.path, "../dst"), exist_ok=False)
        except:
            raise self.__custom_raise(
                FileExistsError, "a project already exists in this directory")

    def __create_dir(self) -> None:
        try:
            os.makedirs(self.path, exist_ok=False)
        except:
            raise self.__custom_raise(
                FileExistsError, "a project already exists in this directory")

    def create_routes(self) -> None:
        try:
            os.makedirs(os.path.join(self.path, "routes"), exist_ok=False)
        except:
            raise self.__custom_raise(
                FileExistsError, "routes directiory already exists!")

    async def __new_query_npm(self, package: dict,) -> None:
        async with aiohttp.ClientSession() as session:
            for depen in self.dependecies:
                print(f"downloading {depen}...\n ")
                async with session.get(f"https://api.npms.io/v2/search?q={depen}") as r:
                    version = await r.json()
                    if version['total'] == 0:
                        self.error_depens.append(depen)
                    else:
                        package["dependencies"][depen] = version['results'][0]['package']['version']

    def __query_npm(self, dep: str) -> str:
        d = dep.replace(' ', '+')
        r = requests.get(f"https://api.npms.io/v2/search?q={d}") .json()
        return "not found" if r['total'] == 0 else r['results'][0]['package']['version']

    def __threaded_query_npm(self, package: dict, dep: str) -> None:
        if len(dep) <= 0:
            return
        r = requests.get(f"https://api.npms.io/v2/search?q={dep}").json()
        if r['total'] == 0 or r == []:
            self.error_lock.acquire()
            self.error_depens.append(dep)
            self.error_lock.release()
            return
        else:
            self.package_lock.acquire()
            package["dependencies"][dep] = r['results'][0]['package']['version']
            self.package_lock.release()
            return

    def __create_controllers(self) -> None:
        try:
            os.makedirs(os.path.join(self.path, "controllers"), exist_ok=False)
        except:
            raise self.__custom_raise(
                FileExistsError, "directory controllers already exits")

    def __handle_value_erorr(self) -> str:
        c = input(Color.get_color(Color.YELLOW) +
                  "erorr with the value that was entered! would you like to re-enter the value?\n "+RESET_COLOR).lower()
        if not self.__valid_user_input(c):
            raise self.__custom_raise(ValueError, "invalid user input")
        if c[0] == 'n':
            self.__handle_exit()
        else:
            io = input("please re-enter the value\n")
            if not self.__valid_user_input(io):
                raise self.__custom_raise(ValueError, "invalid user input")
        return io

    def __get_name(self) -> str:
        i = ""
        try:
            i = input("what is the name of the project\n")
            if not self.__valid_user_input(i):
                raise ValueError
        except ValueError:
            i = self.__handle_value_erorr()
        finally:
            self.__clear_screen()
            self.__custom_print(Color.CYAN, "name of project", begining_tab=True,
                                seperator="->", ending_newline=True, post_seperator=i)
            return i

    def __get_desc(self) -> str:
        i = ""
        try:
            i = input("what is the description of the project\n")
            if not self.__valid_user_input(i):
                raise ValueError
        except ValueError:
            i = self.__handle_value_erorr()
        finally:
            self.__clear_screen()
            self.__custom_print(Color.CYAN, "desc of project", begining_tab=True,
                                seperator="->", ending_newline=True, post_seperator=i)
            return i

    def __get_author(self) -> str:
        i = ""
        try:
            i = input(
                "who is the author of this project(Your name)\n")
            if not self.__valid_user_input(i):
                raise ValueError
        except ValueError:
            i = self.__handle_value_erorr()
        finally:
            self.__clear_screen()
            self.__custom_print(Color.CYAN, "author of project", begining_tab=True,
                                seperator="->", ending_newline=True, post_seperator=i)
            return i

    def __get_depens(self) -> list[str]:
        i = input(
            "aditional dependices(Express and dotenv are already included)\n").split(' ')
        return ["express", "dotenv", *i]

    def __handle_exit(self,) -> NoReturn:
        self.__custom_print(Color.GREEN, "the project was safely exited ",
                            ending_newline=True, begining_tab=True)
        sys.exit(0)

    # force the optional inputs to be keword arguments
    # seperator is the trailing char that is used to seperate from the added value when custom print is called
    def __custom_print(
        self,
        color: Color,
        message: str,
        *,
        begining_tab: Optional[bool] = False,
        ending_newline: Optional[bool] = False,
        seperator: str = "",
        post_seperator: str = ""
    ) -> None:
        if type(message) != str:
            raise ValueError("the message needs to be of type str")
        if len(message) <= 0:
            raise ValueError(f"invalid input for message :{message}")
        if type(color) != Color:
            raise ValueError("color must be of type color")
        base_message = Color.get_color(
            color) + message + seperator + post_seperator + RESET_COLOR
        out = ""
        if begining_tab and ending_newline:
            out = "\t" + base_message + "\n"
        elif begining_tab and not ending_newline:
            out = "\t" + base_message
        elif ending_newline and not begining_tab:
            out = base_message + "\n"
        if len(out) <= 0:
            raise ValueError("error when building the message")
        sys.stdout.write(out)
        sys.stdout.flush()

    # the exception type is a alias for callable str that returns a generic bound by exception class
    # then the function will return this generic meaning the return will be any exception that
    # derives from base exception class
    def __custom_raise(self, exception_type: ExceptionType[ET], exception_message: str) -> ET:
        if len(exception_message) <= 0:
            raise ValueError("exception_message can not be empty!")
        if not type(BaseException) == type(exception_type):
            raise ValueError("execption type must inherit from BaseException")
        if not type(exception_message) == str:
            raise ValueError("excption_message must be a string")

        # return the built error instead of raising it here
        # if raised here the dispalyed raise line will be this funcion instead of when this function is called
        # (not the funcionality i want )
        return exception_type(Color.get_color(Color.RED) + exception_message + RESET_COLOR)

    # by passing args i can just iterate through any number of user_inputs to check
    # and if any are invalid return false to be handled later
    def __valid_user_input(self, *args: str) -> bool:
        for user_input in args:
            if not type(user_input) == str:
                return False
            if user_input == " ":
                return False
            if len(user_input) <= 0:
                return False

        return True

    def __handle_commands_install(self,) -> None:
        try:
            # make sure to change to the generated project path
            # or the tsc depencies will not install in the correct place
            os.chdir(self.path)
            if self.ts:
                os.system("npm install typescript --save-dev")
                # make sure to install the types for express
                os.system("npm install --save @types/express")
            os.system("npm install")
            self.__clear_screen()
        except:
            raise self.__custom_raise(OSError,
                                      "error when running install commands")

    def __default_info(self,) -> None:
        self.path = os.path.join(os.getcwd(), "express-app")
        self.__create_dir()
        self.name = "user"
        self.desc = "default express build"
        self.author = "user"
        self.js_type = "module"
        self.dependecies = ["express", "dotenv"]
        self.__create_project()
        self.display_final_message()
        return

    def __user_info(self,) -> None:
        self.path = self.__get_project_home()
        self.__clear_screen()
        self.__custom_print(Color.CYAN, "project home", begining_tab=True,
                            seperator="->", ending_newline=True, post_seperator=self.path)
        self.__create_dir()
        self.name = self.__get_name()
        self.desc = self.__get_desc()
        self.author = self.__get_author()
        self.js_type = self.__get_module_type()
        self.__js_or_ts()
        self.dependecies = self.__get_depens()
        self.__clear_screen()
        self.__create_project()
        self.display_final_message()
        return

    def __create_project(self) -> None:
        self.create_env_file()
        self.create_git_ignore()
        self.create_index_file()
        self.create_package_json()
        self.__create_controllers()
        self.create_routes()
        self.__handle_commands_install()

    def build(self) -> None:
        if self.__check_for_flags():
            self.__default_info()
        else:
            self.__user_info()
        return
