import socket


def is_physically_connected(host="8.8.8.8", port=53, timeout=2):
    """
    Checks if device has raw internet access (Ping Google DNS).
    """
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def is_internet_allowed(mode="casual"):
    """
    Policy Manager:
    - Casual: Allowed
    - Movie:  Allowed
    - Exam:   BLOCKED (Strict Offline)
    """
    # Exam Mode is ALWAYS Offline
    if mode == "exam":
        return False

    connected = is_physically_connected()

    if connected:
        print(f"🌍 [Network] Access Granted for '{mode}' mode.")
    else:
        print(f"⚠️ [Network] Physical Internet Unavailable.")

    return connected
