#!/usr/bin/env bash
# -*- coding: utf-8 -*-
#=========================================================
# File:        run.sh
# Author:      Vinith Balakrishnan Raj
# Created:     2025-10-05
# Description: Launcher script for SuperTerm application
#
# Usage:
#     bash run.sh
#
# Notes:
#     - Activates virtual environment
#     - Launches SuperTerm CLI
#
# License:
#     MIT License - Copyright (c) 2025 Vinith Balakrishnan Raj
#=========================================================

cd "$(dirname "$0")"
source .superterm_env/bin/activate
exec superterm
