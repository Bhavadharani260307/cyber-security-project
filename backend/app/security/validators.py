"""
Input Validation and File Sanitization Helpers
"""

import os
import re
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {"csv"}
IP_REGEX = re.compile(
    r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
)


def validate_ip(ip_str: str) -> bool:
    """Validates IPv4 string format"""
    if not ip_str or not isinstance(ip_str, str):
        return False
    return bool(IP_REGEX.match(ip_str.strip()))


def validate_allowed_file(filename: str) -> bool:
    """Checks if file extension is safe (CSV only)"""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def sanitize_filename(filename: str) -> str:
    """Returns secure filename free of directory traversal sequences"""
    return secure_filename(filename)


def validate_predict_payload(data: dict) -> tuple[bool, str | None]:
    """Validates input JSON for single packet prediction"""
    required_numeric_fields = [
        "destination_port",
        "flow_duration",
        "total_fwd_packets",
        "total_backward_packets",
        "fwd_packet_length_max",
        "bwd_packet_length_mean",
        "flow_bytes_s",
        "flow_packets_s",
    ]

    for field in required_numeric_fields:
        if field not in data:
            return False, f"Missing required feature field: '{field}'"
        try:
            val = float(data[field])
            if val < 0:
                return False, f"Feature '{field}' must be a non-negative number."
        except (ValueError, TypeError):
            return False, f"Feature '{field}' must be a valid numeric value."

    return True, None
