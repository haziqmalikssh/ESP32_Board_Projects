import sys
import os

print("--- Python Version ---")
print(sys.version)

print("\n--- Python Path (sys.path) ---")
for path in sys.path:
    print(path)

print("\n--- Contents of site-packages ---")
site_packages_path = next((p for p in sys.path if "site-packages" in p), None)
if site_packages_path and os.path.exists(site_packages_path):
    print(f"Checking directory: {site_packages_path}")
    contents = os.listdir(site_packages_path)
    contents.sort()
    for item in contents:
        print(f"- {item}")
else:
    print("Could not find the site-packages directory.")

print("\n--- Diagnostic Complete ---")
