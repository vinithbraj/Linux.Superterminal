#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Shared LLM context state for last executed shell command/output."""

LAST_COMMAND_INPUT = None
LAST_COMMAND_OUTPUT = None


def set_last_context(cmd: str, output: str):
    """Update command context only when a real shell command is executed."""
    global LAST_COMMAND_INPUT, LAST_COMMAND_OUTPUT

    # Ignore empty commands or AI prompts (those starting with '!')
    if not cmd or cmd.strip().startswith("!"):
        return

    LAST_COMMAND_INPUT = cmd.strip()

    # Limit large outputs to last 8KB
    if output:
        trimmed_output = output.strip()
        if len(trimmed_output) > 8000:
            trimmed_output = trimmed_output[-8000:]
        LAST_COMMAND_OUTPUT = trimmed_output


def get_last_context():
    """Return the last command and output context."""
    return LAST_COMMAND_INPUT, LAST_COMMAND_OUTPUT
