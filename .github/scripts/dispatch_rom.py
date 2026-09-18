#!/usr/bin/env python3
import os
import json
import urllib.request
import urllib.error

git_token = os.environ.get("GIT_TOKEN")
payload = {
    "stock_device": "SM-P613",
    "target_device": "SM-P620",
    "target_csc": "EUX",
    "output_fs": "erofs",
    "vendor_repo": "tui2019/vendor_samsung_gta4xlve",
    "kernel_repo": "tui2019/android_kernel_samsung_sm7125",
    "publish_release": "False"
}

event_payload_str = os.environ.get("EVENT_PAYLOAD", "")
if event_payload_str and event_payload_str != "null":
    try:
        incoming = json.loads(event_payload_str)
        if isinstance(incoming, dict):
            payload.update(incoming)
    except Exception as e:
        print(f"Notice: {e}")

input_pub = os.environ.get("INPUT_PUBLISH_RELEASE")
if input_pub:
    payload["publish_release"] = input_pub

# Enforce GitHub API limit of at most 10 top-level properties
allowed_top = {
    "trigger_rom", "stock_device", "target_device", "target_csc",
    "output_fs", "vendor_repo", "kernel_repo", "publish_release", "rom_config"
}
rom_config = payload.get("rom_config", {})
if not isinstance(rom_config, dict):
    rom_config = {}

compact_payload = {}
for k, v in payload.items():
    if k in allowed_top and k != "rom_config":
        compact_payload[k] = v
    elif k != "rom_config":
        rom_config[k] = v

compact_payload["rom_config"] = rom_config

body = json.dumps({
    "event_type": "kernel-build-completed",
    "client_payload": compact_payload
}).encode('utf-8')

req = urllib.request.Request(
    "https://api.github.com/repos/tui2019/QuantumROM/dispatches",
    data=body,
    headers={
        "Accept": "application/vnd.github+json",
        "Authorization": f"token {git_token}",
        "Content-Type": "application/json"
    }
)
try:
    with urllib.request.urlopen(req) as resp:
        print(f"✅ Successfully dispatched build to QuantumROM! HTTP Code: {resp.status}")
except urllib.error.HTTPError as e:
    print(f"❌ Failed to dispatch to QuantumROM. HTTP Error: {e.code} - {e.read().decode('utf-8', errors='ignore')}")
    exit(1)
