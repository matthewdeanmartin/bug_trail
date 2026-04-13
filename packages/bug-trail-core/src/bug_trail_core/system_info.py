"""
System info for including with error logs
"""

from __future__ import annotations

import json
import os
import platform
from collections.abc import Sequence
from typing import Any

import psutil


def convert_bytes_to_gb(bytes_value: int) -> str:
    """
    Converts a byte value to gigabytes and formats it to two decimal places.
    """
    gb_value = bytes_value / (1024**3)
    return f"{gb_value:.2f} GB"


def convert_mhz_to_ghz(mhz_value: int | float) -> str:
    """
    Converts a frequency value from MHz to GHz and formats it to two decimal places.
    """
    ghz_value = mhz_value / 1000
    return f"{ghz_value:.2f} GHz"


def get_os_summary() -> dict[str, str | Sequence[str]]:
    """Collects and returns a summary of the operating system information."""
    os_version = platform.version()
    os_platform = platform.system()
    os_release = platform.release()
    os_architecture = platform.machine()

    # Build operating system summary
    os_summary: dict[str, str | Sequence[str]] = {
        "Platform (sysname)": os_platform,
        "Release": os_release,
        "Architecture": os_architecture,
        "Version": os_version,
        "Windows Info": platform.win32_ver(),
    }

    return os_summary


def get_system_info() -> dict[str, Any]:
    """
    Collects and returns system information including memory, CPU, disk space, and operating system details.
    """
    # Memory information
    mem = psutil.virtual_memory()
    total_memory = convert_bytes_to_gb(mem.total)
    available_memory = convert_bytes_to_gb(mem.available)

    # CPU information
    cpu_freq = psutil.cpu_freq()
    cpu_clock_speed = convert_mhz_to_ghz(cpu_freq.current)
    cpu_count = psutil.cpu_count(logical=False)

    # Disk information — use the system drive on Windows, root on Unix
    disk_root = (
        os.environ.get("SystemDrive", "C:\\") if platform.system() == "Windows" else "/"
    )
    disk_usage = psutil.disk_usage(disk_root)
    total_disk_space = convert_bytes_to_gb(disk_usage.total)
    available_disk_space = convert_bytes_to_gb(disk_usage.free)

    # Get the operating system summary
    os_summary = get_os_summary()

    # Build system information dictionary
    info = {
        "Total Memory": total_memory,
        "Available Memory": available_memory,
        "CPU Frequency": cpu_clock_speed,
        "CPU Cores": cpu_count,
        "Total Disk Space": total_disk_space,
        "Available Disk Space": available_disk_space,
        "Operating System Summary": os_summary,
    }

    return info


# Usage example
if __name__ == "__main__":
    system_info = get_system_info()
    for key, value in system_info.items():
        if key == "Operating System Summary" and isinstance(value, dict):
            print("Operating System Information:")
            for os_key, os_value in value.items():
                print(f"  {os_key}: {os_value}")
        else:
            print(f"{key}: {value}")


def create_system_info_table(conn):
    """Creates the system_info table in the database if it does not exist."""
    sql_create_table = """CREATE TABLE IF NOT EXISTS system_info (
                              id TEXT PRIMARY KEY,
                              snapshot_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                              total_memory TEXT,
                              available_memory TEXT,
                              cpu_frequency TEXT,
                              cpu_cores INTEGER,
                              total_disk_space TEXT,
                              available_disk_space TEXT,
                              os_platform TEXT,
                              os_release TEXT,
                              os_architecture TEXT,
                              os_version TEXT,
                              windows_info TEXT
                          );"""
    cursor = conn.cursor()
    cursor.execute(sql_create_table)


def insert_system_info(conn, info):
    """Inserts system information into the system_info table."""
    sql_insert_info = """INSERT INTO system_info 
                         (total_memory, available_memory, cpu_frequency, cpu_cores, 
                          total_disk_space, available_disk_space, os_platform, os_release, 
                          os_architecture, os_version, windows_info) 
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""

    cursor = conn.cursor()
    cursor.execute(
        sql_insert_info,
        (
            info["Total Memory"],
            info["Available Memory"],
            info["CPU Frequency"],
            info["CPU Cores"],
            info["Total Disk Space"],
            info["Available Disk Space"],
            info["Operating System Summary"]["Platform (sysname)"],
            info["Operating System Summary"]["Release"],
            info["Operating System Summary"]["Architecture"],
            info["Operating System Summary"]["Version"],
            json.dumps(
                info["Operating System Summary"]["Windows Info"]
            ),  # Store as JSON string
        ),
    )
    conn.commit()


def record_system_info(conn):
    """Records system information into the database."""
    system_info = get_system_info()
    insert_system_info(conn, system_info)
