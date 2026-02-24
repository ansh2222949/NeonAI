import socket
import requests


ALLOWED_ONLINE_MODES = {"casual", "movie", "coding"}
BLOCKED_MODES = {"exam"}


def is_physically_connected(host="8.8.8.8", port=53, timeout=2):
    """
    Checks low-level internet connectivity using DNS socket.
    """
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def _http_check(timeout=2):
    """
    Secondary HTTP check to confirm actual internet access.
    """
    try:
        requests.get("https://www.google.com", timeout=timeout)
        return True
    except requests.RequestException:
        return False


def is_internet_allowed(mode="casual", silent=False):
    """
    Network Policy Manager.

    Rules:
    - Exam mode: Always offline.
    - Casual, Movie, Coding: Allowed if physically connected.
    - Unknown modes: Blocked by default.
    """

    mode = (mode or "").lower().strip()

    # -----------------------------
    # Strict Offline Mode
    # -----------------------------
    if mode in BLOCKED_MODES:
        if not silent:
            print(f"[Network] Internet blocked for '{mode}' mode (policy restriction).")
        return False

    # -----------------------------
    # Unknown Mode Protection
    # -----------------------------
    if mode not in ALLOWED_ONLINE_MODES:
        if not silent:
            print(f"[Network] Unknown mode '{mode}'. Internet blocked by default.")
        return False

    # -----------------------------
    # Physical Connectivity Check
    # -----------------------------
    if not is_physically_connected():
        if not silent:
            print("[Network] Physical internet unavailable.")
        return False

    # Optional deeper HTTP validation
    if not _http_check():
        if not silent:
            print("[Network] HTTP validation failed.")
        return False

    if not silent:
        print(f"[Network] Internet access granted for '{mode}' mode.")

    return True
