#!/usr/bin/env python3
"""
Configuration Validation CLI

Run this script before tests or deployment to catch configuration errors.

Usage:
    python validate_config.py
"""
from validation.configuration_validator import main

if __name__ == '__main__':
    exit(main())
