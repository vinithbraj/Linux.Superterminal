#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=========================================================
 File:        executer.py
 Author:      Vinith Balakrishnan Raj
 Created:     2025-10-05
 Description: Shell command execution with live output streaming

 Usage:
     from superterm.executer import run_command

 Notes:
     - Handles both interactive and non-interactive commands
     - Streams output in real-time
     - Captures output for LLM context

 License:
     MIT License - Copyright (c) 2025 Vinith Balakrishnan Raj
=========================================================
"""

import subprocess
import os
import sys
import pty
import select
from superterm.llm_client import set_last_context

def run_command(command: str):
    """Run shell command with live streaming output (like real terminal)."""
    try:
        interactive_keywords = [
            # --- Editors ---
            "nano", "vi", "vim", "nvim", "emacs",

            # --- File viewers / pagers ---
            "less", "more", "man",

            # --- System monitors / dashboards ---
            "top", "htop", "btop", "glances", "atop", "iotop", "iftop",

            # --- Disk / partition tools (prompt-heavy) ---
            "fdisk", "cfdisk", "parted", "gdisk", "sgdisk",

            # --- Package managers (confirmation or progress UI) ---
            "apt", "apt-get", "aptitude", "dpkg-reconfigure", "yum", "dnf", "zypper", "snap", "flatpak",

            # --- Network / remote shells ---
            "ssh", "telnet", "ftp", "sftp",

            # --- Continuous or streaming output ---
            "tail -f", "journalctl -f", "dmesg -w", "watch",

            # --- Shells and REPLs ---
            "bash", "sh", "zsh", "python", "python3", "ipython", "node", "mysql", "psql", "mongo",

            # --- System management & configuration ---
            "nmcli", "systemctl", "service", "ufw", "passwd", "adduser", "deluser", "usermod",

            # --- Misc interactive utilities ---
            "crontab -e", "visudo", "alsamixer", "amixer",
        ]


        # --- Handle truly interactive tools (no capture, direct terminal) ---
        if any(command.strip().startswith(k) for k in interactive_keywords):
            print(f"Launching interactive session: {command}\n")
            exit_code = os.system(command)
            # Record minimal context so !ref still knows what ran
            set_last_context(command, f"[Exited interactive command with code {exit_code}]")
            return "\n[Exited interactive command]"


        # --- Stream output live (non-interactive commands) ---
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True,
            cwd=os.getcwd(),
        )

        captured_output = []

        for line in process.stdout:
            sys.stdout.write(f"\033[0m{line}\033[0m")
            sys.stdout.flush()
            captured_output.append(line)

        for line in process.stderr:
            sys.stdout.write(f"\033[91m{line}\033[0m")
            sys.stdout.flush()
            captured_output.append(line)

        process.wait()

        full_output = "".join(captured_output)
        if len(full_output) > 10000:
            full_output = full_output[-10000:]

        set_last_context(command, full_output)

    except Exception as e:
        set_last_context(command, f"[Error running command: {e}]")
        return f"\033[91m[Error running command: {e}]\033[0m"
