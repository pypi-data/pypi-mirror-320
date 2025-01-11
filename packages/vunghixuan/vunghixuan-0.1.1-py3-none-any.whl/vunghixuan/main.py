# src/vunghixuan/main.py
import sys
from .api_and_otp import APIKey, Otp
from .create_project import Project

def main():
    args = sys.argv[1:]
    if '-h' in args or '--help' in args:
        print("Help message")
    else:
        key = args[1] if len(args) > 1 else None
        if key:
            if '-api' in args:
                obj = APIKey(key)
                obj.get_api()
            if '-otp' in args or '-totp' in args:
                obj = Otp(key)
                obj.get_otp()
            if '-create_project' in args :
                obj = Project(key)
                obj.create_project()
            if '-create_app' in args :
                obj = Project(key)
                obj.create_app()
        else:
            print("Missing API key")
    

if __name__ == '__main__':
    main()