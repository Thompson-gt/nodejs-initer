import os
import json
import subprocess
import sys


# create git ignore,return bool for if file was created
def create_git_ignore(path: str) -> bool:
    print("creating the gitignore file")

    try:
        with open(path + "\.gitignore", 'w') as f:
            f.write(".package.json\n")
            f.write(".env")
    except FileExistsError:
        print("file already exists")

        return False
    return True

# create a env file,return bool for if the file was created


def create_env_file(path: str) -> bool:

    print("creating the env file")
    try:
        with open(path + "\.env", 'w') as f:
            f.write("DB_URI=? \n")
            f.write("PORT=8080")

    except FileExistsError:
        print("file already exists")

        return False
    return True


def create_index_file(path: str, js_type: str) -> bool:

    print("creating the index.js")
    try:
        with open(path + "\index.js", 'w') as f:
            if js_type == "Commonjs":
                f.write("dotenv = require('dotenv').config();\n")
                f.write("express = require('express');\n\n\n")
            else:
                f.write("import * as dotenv from 'dotenv';\n")
                f.write("import express from 'express';\n\n\n ")
            f.write("app = express()\n\n")
            f.write("app.use(json())\n\n")
            f.write(
                "app.listen(process.env.PORT || 5000,()=> console.log('sever is running'))")
    except FileExistsError:
        print("file already exists")

        return False
    return True


def create_package_json(
    path: str,
    project_name: str,
    desc: str,
    js_type: str,
    dependcies: list,
    author: str
) -> bool:

    print("creating the package.json file")
    package = {}
    package["name"] = project_name
    package["version"] = "1.0.0"
    package["description"] = desc
    package["main"] = "index.js"
    package["type"] = js_type
    package["scripts"] = {
        "test": "echo "
    }
    if "nodemon" in dependcies:
        package["scripts"]["start"] = "nodemon index.js"
    package["author"] = author
    package["license"] = "ISC"
    package["dependencies"] = {
        "express": "^4.18.6",
        "dotenv": "16.0.3"
    }
    for depen in dependcies:
        # just give all of the dependices the versions greater than 1.0 becuase i cant find the versions
        # the carrort character will allow any version after 1.0
        package["dependencies"][depen] = "^1.0"
    try:
        with open(path + "\package.json", 'w') as f:
            json.dump(package, f)
    except FileExistsError:
        print("file already exists")
        return False
    return True


def create_routes(self) ->bool:
        if os.path.exists(os.path.join(self.path,"routes")):
            return False
        os.mkdir(os.path.join(self.path,"routes"))
        return True



def create_controllers(self) ->bool:
        if os.path.exists(os.path.join(self.path,"controllers")):
            return False
        os.mkdir(os.path.join(self.path,"controllers"))
        return True
# wrap all functionality into a main funcion so we can handle the keyboard interrupt
# exception


def main() -> None:
    try:
        # get the path for the project(will  start with the current dir)
        path = os.getcwd() + input(
            "where do you want the project to live\n")
        # create the directory
        os.mkdir(path)
        # make the files
        create_env_file(path)
        create_git_ignore(path)
        # get the name for the project
        name = input("what is the name of the project\n")
        # get the desc for the project
        description = input("what is the description of the project\n")
        # get the type of javascript
        js_type = input(
            "what type of javascript:\n Module:\n Commonjs:\n").lower()
        # populate the index file
        create_index_file(path, js_type)
        # get the author for the project
        author = input("who is the author of this project(Your name)\n")
        # get the dependcies for the project
        dependencies = input(
            "aditional dependices(Express is already included)").split(' ')
        # populate the package json file
        create_package_json(path, name, description,
                            js_type, dependencies, author)
        create_controllers()
        create_routes()
        # handle the keyboard interrupt event
    except KeyboardInterrupt:
        choice = input("you stopped the app, wanna start again? (y/n)\n")
        if choice == 'y' or choice == "yes":
            if os.path.exists(path): os.rmdir(path)
            subprocess.run(["python3 class.py"])
        else:
            sys.exit(0)

# run the whole project
main()
