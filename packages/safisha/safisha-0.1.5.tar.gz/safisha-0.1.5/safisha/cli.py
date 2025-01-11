# safisha/cli.py
from __future__ import print_function  # Ensure Python 3-style print in Python 2.7
import argparse
from .cleaner import Safisha

def onyesha_menu():
    """Onyesha menyu ya Swahili."""
    print("\n--- Menyu ya Safisha ---")
    print("1. Safisha Folda ya Downloads")
    print("2. Safisha Folda ya Desktop")
    print("3. Safisha Folda ya Cache")
    print("5. Ondoka")

def kuwa_na_safisha():
    """Washa programu ya Safisha."""
    safisha = Safisha()

    while True:
        onyesha_menu()
        try:
            # Use input() for Python 3.x and raw_input() for Python 2.7
            chaguo = input("Chagua nambari ya shughuli: ")
        except NameError:
            # Fallback to raw_input() for Python 2.7
            chaguo = raw_input("Chagua nambari ya shughuli: ")

        if chaguo == "1":
            safisha.safisha_downloads()
        elif chaguo == "2":
            safisha.safisha_desktop()
        elif chaguo == "3":
            safisha.safisha_cache()
        elif chaguo == "5":
            print("Kwaheri!")
            break
        else:
            print("Chaguo si sahihi. Tafadhali chagua tena.")

def main():
    parser = argparse.ArgumentParser(description="Safisha - Programu ya kusafisha Mac yako.")
    parser.add_argument(
        "--downloads", action="store_true", help="Safisha folda ya Downloads."
    )
    parser.add_argument(
        "--desktop", action="store_true", help="Safisha folda ya Desktop."
    )
    parser.add_argument(
        "--cache", action="store_true", help="Safisha folda ya Cache."
    )
    parser.add_argument(
        "--zote", action="store_true", help="Safisha folda zote."
    )
    parser.add_argument(
        "--menyu", action="store_true", help="Fungua menyu ya Safisha."
    )

    args = parser.parse_args()

    safisha = Safisha()

    # Display the menu by default if no arguments are provided
    if not any(vars(args).values()):
        kuwa_na_safisha()
    elif args.menyu:
        kuwa_na_safisha()
    elif args.downloads:
        safisha.safisha_downloads()
    elif args.desktop:
        safisha.safisha_desktop()
    elif args.cache:
        safisha.safisha_cache()
    
    else:
        print("Tafadhali tumia moja ya chaguo. Tumia --menyu kwa menyu.")

if __name__ == "__main__":
    main()