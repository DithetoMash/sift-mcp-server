from .common import safe_run

def get_mft_timeline(image_path: str, filter_path: str = None) -> dict:
    """Extract MFT timeline using fls from Sleuth Kit."""
    # Step 1: get partition offset
    mmls_result = safe_run(["mmls", image_path])
    if "error" in mmls_result:
        return mmls_result
    offset = _parse_ntfs_offset(mmls_result["stdout"])
    if not offset:
        return {"error": "Could not find NTFS partition offset from mmls output"}

    # Step 2: run fls to list files with timestamps
    fls_cmd = ["fls", "-r", "-m", "/", "-o", str(offset), image_path]
    fls_result = safe_run(fls_cmd, timeout=120)
    if "error" in fls_result:
        return fls_result

    # Step 3: filter by path if requested
    lines = fls_result["stdout"].splitlines()
    if filter_path:
        lines = [l for l in lines if filter_path.lower() in l.lower()]

    return {
        "tool": "fls",
        "offset": offset,
        "filter_path": filter_path,
        "entry_count": len(lines),
        "entries": lines[:500]
    }

def _parse_ntfs_offset(mmls_output: str) -> int:
    """Parse sector offset of NTFS partition from mmls output."""
    for line in mmls_output.splitlines():
        if "NTFS" in line or "0x07" in line:
            parts = line.split()
            for part in parts:
                if part.isdigit() and int(part) > 0:
                    return int(part) * 512
    return None
