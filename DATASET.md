# Dataset Documentation

## Case: NIST CFReDS Hacking Case

### Source
National Institute of Standards and Technology (NIST)  
Computer Forensics Reference Data Sets (CFReDS)  
https://cfreds-archive.nist.gov/images/

### Files
| File | Size | SHA256 |
|------|------|--------|
| 4Dell Latitude CPi.E01 | 640 MB | 96bebe80f00541bf28fbc2ef0b02b580082ee6ad58837e991852ae66f077ec31 |
| 4Dell Latitude CPi.E02 | 400 MB | 46bd09821dbb64675e5877d0ad7ec544a571fad5a3fd7fc3f0c3a16278887db5 |

### Device
- **Make/Model:** Dell Latitude CPi laptop
- **OS:** Windows XP
- **Image format:** Expert Witness Format (EWF), two-part split

### Case Background
A suspect known as "Mr. Evil" was suspected of war-driving and intercepting
network traffic at public WiFi locations. The disk image contains the suspect's
laptop filesystem with documented evidence of hacking tools and network activity.

### Known Ground Truth
Documented findings from NIST case documentation:

| Artifact | Finding |
|----------|---------|
| Registered owner | Greg Schardt |
| Alias | Mr. Evil |
| User profile | Mr. Evil (confirmed via Documents and Settings) |
| SAM hive | Present at WINDOWS/system32/config/SAM |
| SECURITY hive | Present at WINDOWS/system32/config/SECURITY |
| SYSTEM hive | Not found at expected path |
| SOFTWARE hive | Not found at expected path |

### How the Agent Was Tested
1. Image downloaded from NIST CFReDS archive
2. SHA256 hashes verified against published checksums
3. Image mounted read-only via ewfmount
4. Agent run against mounted image at /mnt/windows_mount
5. SHA256 hashes verified post-execution to confirm no spoliation

### Reproducing the Test Environment
```bash
mkdir -p /cases/hacking_case && cd /cases/hacking_case
wget "https://cfreds-archive.nist.gov/images/4Dell%20Latitude%20CPi.E01"
wget "https://cfreds-archive.nist.gov/images/4Dell%20Latitude%20CPi.E02"
sha256sum "4Dell Latitude CPi.E01" "4Dell Latitude CPi.E02"
sudo mkdir -p /mnt/ewf_mount /mnt/windows_mount
sudo ewfmount "/cases/hacking_case/4Dell Latitude CPi.E01" /mnt/ewf_mount
sudo mount -o ro,loop,show_sys_files,streams_interface=windows,offset=32256 \
    /mnt/ewf_mount/ewf1 /mnt/windows_mount
```
