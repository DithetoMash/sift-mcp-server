import os

def get_registry_hives(mount_path: str) -> dict:
    """List available registry hives from a mounted Windows image."""
    hive_paths = {
        "SAM":      os.path.join(mount_path, "WINDOWS/system32/config/SAM"),
        "SYSTEM":   os.path.join(mount_path, "WINDOWS/system32/config/SYSTEM"),
        "SOFTWARE": os.path.join(mount_path, "WINDOWS/system32/config/SOFTWARE"),
        "SECURITY": os.path.join(mount_path, "WINDOWS/system32/config/SECURITY"),
    }
    found = {}
    for name, path in hive_paths.items():
        found[name] = {"path": path, "exists": os.path.exists(path)}
    return {"hives": found, "mount_path": mount_path}

def get_user_profiles(mount_path: str) -> dict:
    """List user profiles from Documents and Settings."""
    profiles_path = os.path.join(mount_path, "Documents and Settings")
    if not os.path.exists(profiles_path):
        return {"error": f"Path not found: {profiles_path}"}
    users = [d for d in os.listdir(profiles_path)
             if os.path.isdir(os.path.join(profiles_path, d))]
    return {"users": users, "profiles_path": profiles_path}
