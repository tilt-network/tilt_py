import os
import sys


class TiltLog:
    debug_mode = os.environ.get("DEBUG") == "1"

    @staticmethod
    def success(msg: str):
        if TiltLog.debug_mode:
            print(f"[✓] {msg}", file=sys.stdout)

    @staticmethod
    def warning(msg: str):
        if TiltLog.debug_mode:
            print(f"[!] {msg}", file=sys.stdout)

    @staticmethod
    def info(msg: str):
        if TiltLog.debug_mode:
            print(f"[-] {msg}", file=sys.stdout)

    @staticmethod
    def error(msg: str):
        print(f"[x] {msg}", file=sys.stderr)
