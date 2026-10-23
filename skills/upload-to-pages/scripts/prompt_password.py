#!/usr/bin/env python3
"""Collect a user-chosen password through a masked local window."""

from __future__ import annotations

import getpass
import sys


def prompt_hidden_terminal() -> str:
    if not sys.stdin.isatty() or not sys.stderr.isatty():
        raise SystemExit("No private local password prompt is available.")
    return getpass.getpass("Enter your password: ")


def prompt_password() -> str:
    try:
        import tkinter as tk
        from tkinter import simpledialog
    except ImportError:
        password = prompt_hidden_terminal()
    else:
        try:
            root = tk.Tk()
        except tk.TclError:
            password = prompt_hidden_terminal()
        else:
            try:
                root.withdraw()
                root.attributes("-topmost", True)
                password = simpledialog.askstring(
                    "Upload to Pages",
                    "Enter the password for the protected HTML page:",
                    show="*",
                    parent=root,
                )
            except tk.TclError:
                password = prompt_hidden_terminal()
            finally:
                try:
                    root.destroy()
                except tk.TclError:
                    pass

            if password is None:
                raise SystemExit("Password entry was cancelled.")

    if not password:
        raise SystemExit("Password cannot be empty.")
    return password


if __name__ == "__main__":
    # Call through shell command substitution so the value goes straight into
    # StatiCrypt's environment and does not appear in terminal output.
    sys.stdout.write(prompt_password())
