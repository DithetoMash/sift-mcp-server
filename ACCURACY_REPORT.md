# Accuracy Report

## Test Case
**Dataset:** NIST CFReDS Hacking Case — Dell Latitude CPi  
**Ground Truth Source:** NIST published case documentation  
**Agent Version:** SIFT MCP Server v1.0  

---

## 1. Findings Accuracy

### User Profile Enumeration
| Finding | Expected | Agent Result | Classification |
|---------|----------|--------------|----------------|
| Mr. Evil user profile exists | YES | YES | True Positive |
| LocalService account present | YES | YES | True Positive |
| NetworkService account present | YES | YES | True Positive |
| Default User profile present | YES | YES | True Positive |

### Registry Hive Availability
| Finding | Expected | Agent Result | Classification |
|---------|----------|--------------|----------------|
| SAM hive present | YES | YES | True Positive |
| SECURITY hive present | YES | YES | True Positive |
| SYSTEM hive at expected path | NO | NO | True Negative |
| SOFTWARE hive at expected path | NO | NO | True Negative |

### Summary
- True Positives: 6
- False Positives: 0
- False Negatives: 0
- True Negatives: 2
- **Precision: 100%**
- **Recall: 100%**

*Note: MFT timeline analysis was not completed due to API access constraints
during testing. Results above reflect registry and user profile tools only.*

---

## 2. Evidence Integrity

### Architectural Enforcement
Original disk images are mounted read-only via `ewfmount` at the MCP server
layer. The agent has zero write access to case data by design — not by
instruction.

The MCP server exposes no write tools. The complete tool surface is:
- `get_mft_timeline()` — read only
- `get_registry_hives()` — read only
- `get_user_profiles()` — read only
- `get_ewf_info()` — read only

An agent that attempted to modify evidence would receive:
`{"error": "Unknown tool: write_file"}` — the tool does not exist on the server.

### Mount Verification
```bash
$ sudo ewfmount "/cases/hacking_case/4Dell Latitude CPi.E01" /mnt/ewf_mount
$ sudo mount -o ro,...  /mnt/ewf_mount/ewf1 /mnt/windows_mount
$ mount | grep windows_mount
# Output confirms: (ro,loop,...)
```

### SHA256 Integrity Check
PRE-EXECUTION:
96bebe80f00541bf28fbc2ef0b02b580082ee6ad58837e991852ae66f077ec31  4Dell Latitude CPi.E01
46bd09821dbb64675e5877d0ad7ec544a571fad5a3fd7fc3f0c3a16278887db5  4Dell Latitude CPi.E02
POST-EXECUTION: Identical — no spoliation occurred.
