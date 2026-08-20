#!/usr/bin/env python3
"""Compatibility entry point for strict practice and interoperability validation."""
from check_interoperability import main as interoperability_main
from check_practice_system_strict import main as strict_main


def main():
    strict_main()
    interoperability_main()


if __name__ == "__main__":
    main()
