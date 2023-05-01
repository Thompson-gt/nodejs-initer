import time
import os
import sys
# import this way so i get autocomplete with the class
from Generator import Generator


def main() -> None:
    app = Generator()
    try:
        app.build()
    except KeyboardInterrupt:
        c = input("you stopped the app, wanna start again? (y/n)\n").lower()
        if c[0] == 'y':
            if os.path.exists(app.project_path):
                os.rmdir(app.project_path)
            app.build()
        else:
            print("you cancled the build of the node project")
            sys.exit(0)


if __name__ == "__main__":
    main()
