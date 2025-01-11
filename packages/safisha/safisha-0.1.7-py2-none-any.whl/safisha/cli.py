# safisha/cli.py
import argparse
import subprocess
from safisha.cleaner import Safisha
import http.server
import socketserver
import os

def start_server():
    # Serve the static directory
    os.chdir("static")
    PORT = 8000
    Handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"Serving at http://127.0.0.1:{PORT}")
        httpd.serve_forever()

def main():
    parser = argparse.ArgumentParser(description="Safisha - Programu ya kusafisha Mac yako.")
    parser.add_argument(
        "--gui", action="store_true", help="Fungua kivinjari cha GUI."
    )
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

    args = parser.parse_args()

    if args.gui:
        # Launch the HTTP server
        start_server()
    else:
        safisha = Safisha()
        if args.downloads:
            safisha.safisha_downloads()
        elif args.desktop:
            safisha.safisha_desktop()
        elif args.cache:
            safisha.safisha_cache()
        elif args.zote:
            safisha.safisha_zote()
        else:
            print("Tafadhali tumia moja ya chaguo. Tumia --gui kwa menyu ya kivinjari.")

if __name__ == "__main__":
    main()