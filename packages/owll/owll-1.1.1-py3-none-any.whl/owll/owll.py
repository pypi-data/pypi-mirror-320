import os
import xml.etree.ElementTree as ET

# ANSI color codes
RESET_COLOR = "\033[0m"
GREEN_COLOR = "\033[92m"
RED_COLOR = "\033[91m"
YELLOW_COLOR = "\033[93m"
ORANGE_COLOR = "\033[38;5;208m"
PURPLE_COLOR = "\033[95m"  # Purple text
RED_BLINK_COLOR = "\033[5;31m"  # Red blinking text

# Define dangerous permissions
DANGEROUS_PERMISSIONS = {
    "android.permission.READ_CALENDAR",
    "android.permission.WRITE_CALENDAR",
    "android.permission.CAMERA",
    "android.permission.READ_CONTACTS",
    "android.permission.WRITE_CONTACTS",
    "android.permission.GET_ACCOUNTS",
    "android.permission.ACCESS_FINE_LOCATION",
    "android.permission.ACCESS_COARSE_LOCATION",
    "android.permission.RECORD_AUDIO",
    "android.permission.READ_PHONE_STATE",
    "android.permission.CALL_PHONE",
    "android.permission.READ_CALL_LOG",
    "android.permission.WRITE_CALL_LOG",
    "android.permission.ADD_VOICEMAIL",
    "android.permission.USE_SIP",
    "android.permission.PROCESS_OUTGOING_CALLS",
    "android.permission.BODY_SENSORS",
    "android.permission.SEND_SMS",
    "android.permission.RECEIVE_SMS",
    "android.permission.READ_SMS",
    "android.permission.RECEIVE_WAP_PUSH",
    "android.permission.RECEIVE_MMS",
    "android.permission.READ_EXTERNAL_STORAGE",
    "android.permission.WRITE_EXTERNAL_STORAGE",
}

# Define XML namespace
NAMESPACE = "{http://schemas.android.com/apk/res/android}"


def display_banner():
    """
    Display the script's banner at startup.
    """
    banner = f"""
    {GREEN_COLOR}#      (o,o)  OWLL: Android Defender
    #      {{ " }}  Checking permissions like a boss!
    #      -"-"-  Author: Jina{RESET_COLOR}
    """
    print(banner)


def parse_permissions(manifest_path):
    """
    Parse all permissions from the AndroidManifest.xml file.
    """
    try:
        tree = ET.parse(manifest_path)
        root = tree.getroot()

        permissions = []
        for elem in root.findall(".//uses-permission"):
            perm_name = elem.attrib.get(f'{NAMESPACE}name')
            max_sdk_version = elem.attrib.get(f'{NAMESPACE}maxSdkVersion')
            if perm_name:  # Only add permissions with a valid name
                permissions.append({
                    "name": perm_name,
                    "maxSdkVersion": max_sdk_version
                })
        return permissions
    except ET.ParseError as e:
        print(f"{RED_COLOR}Error parsing XML: {e}{RESET_COLOR}")
        return []


def get_dangerous_permissions(permissions):
    """
    Filter and return dangerous permissions from the list of permissions.
    """
    return [perm for perm in permissions if perm["name"] in DANGEROUS_PERMISSIONS]


def check_attribute(manifest_path, attribute_name):
    """
    Check the value of specific attributes in the application tag.
    """
    tree = ET.parse(manifest_path)
    root = tree.getroot()

    application_tag = root.find("application")
    if application_tag is not None:
        return application_tag.attrib.get(f"{NAMESPACE}{attribute_name}")
    return None


def get_target_sdk_version(manifest_path):
    """
    Get the targetSdkVersion from the manifest.
    """
    tree = ET.parse(manifest_path)
    root = tree.getroot()

    uses_sdk_tag = root.find("uses-sdk")
    if uses_sdk_tag is not None:
        return uses_sdk_tag.attrib.get(f"{NAMESPACE}targetSdkVersion")
    return None


def get_min_sdk_version(manifest_path):
    """
    Get the minSdkVersion from the manifest.
    """
    tree = ET.parse(manifest_path)
    root = tree.getroot()

    uses_sdk_tag = root.find("uses-sdk")
    if uses_sdk_tag is not None:
        return uses_sdk_tag.attrib.get(f"{NAMESPACE}minSdkVersion")
    return None


def check_exported_components(manifest_path):
    """
    Identify exported components in the AndroidManifest.xml file.
    """
    tree = ET.parse(manifest_path)
    root = tree.getroot()

    exported_components = ["activity", "service", "receiver", "provider"]
    warnings = []
    for component in exported_components:
        for elem in root.findall(f".//{component}"):
            exported = elem.attrib.get(f"{NAMESPACE}exported")
            component_name = elem.attrib.get(f"{NAMESPACE}name")
            if exported == "true":
                warnings.append(f"Exported {component}: {component_name}")
    return warnings


def get_package_name(manifest_path):
    """
    Extract the package name from the manifest tag.
    """
    tree = ET.parse(manifest_path)
    root = tree.getroot()

    return root.attrib.get("package")  # 'package' is an attribute of the <manifest> tag


def main():
    display_banner()  # Display banner at the start

    manifest_path = input("Please enter the full path to your AndroidManifest.xml: ")

    if not os.path.exists(manifest_path):
        print(f"{RED_COLOR}File not found: {manifest_path}{RESET_COLOR}")
        return

    # Extract package name
    package_name = get_package_name(manifest_path)

    # Parse permissions
    permissions = parse_permissions(manifest_path)

    # Check attributes
    attributes = ["allowBackup", "usesCleartextTraffic", "debuggable"]
    attribute_values = {attr: check_attribute(manifest_path, attr) for attr in attributes}

    # Dangerous permissions
    dangerous_permissions = get_dangerous_permissions(permissions)

    # Target SDK version
    target_sdk_version = get_target_sdk_version(manifest_path)

    # Min SDK version
    min_sdk_version = get_min_sdk_version(manifest_path)

    # Exported components
    exported_warnings = check_exported_components(manifest_path)

    # Display all permissions
    print(f"\n{GREEN_COLOR}All Permissions:{RESET_COLOR}")
    if permissions:
        for perm in permissions:
            if perm["maxSdkVersion"]:
                print(f"{YELLOW_COLOR}{perm['name']} (maxSdkVersion: {perm['maxSdkVersion']}){RESET_COLOR}")
            else:
                print(f"{YELLOW_COLOR}{perm['name']}{RESET_COLOR}")
    else:
        print(f"{RED_COLOR}No permissions found.{RESET_COLOR}")

    # Display key attributes
    print(f"\n{GREEN_COLOR}Key Attributes:{RESET_COLOR}")
    for attribute, value in attribute_values.items():
        if value is not None:
            color = RED_COLOR if value == "true" else YELLOW_COLOR
            print(f"{color}{attribute}: {value}{RESET_COLOR}", end=" ")
            if value == "true":
                print(f"{PURPLE_COLOR}[VULNERABLE]{RESET_COLOR}")
            else:
                print()
        else:
            print(f"{YELLOW_COLOR}{attribute}: Not specified{RESET_COLOR}")

    # Dangerous Permissions (without [VULNERABLE] tag)
    print(f"\n{GREEN_COLOR}Dangerous Permissions:{RESET_COLOR}")
    for perm in dangerous_permissions:
        print(f"{RED_COLOR}{perm['name']}{RESET_COLOR}")

    # Target SDK version
    print(f"\n{YELLOW_COLOR}Target SDK Version: {target_sdk_version if target_sdk_version else 'Not specified'}{RESET_COLOR}")
    if target_sdk_version is not None:
        if int(target_sdk_version) >= 28:
            print(f"{YELLOW_COLOR}Default value of android:usesCleartextTraffic: false (cleartext traffic is blocked by default){RESET_COLOR}")
        else:
            print(f"{YELLOW_COLOR}Default value of android:usesCleartextTraffic: true (cleartext traffic is allowed by default) {PURPLE_COLOR}[VULNERABLE]{RESET_COLOR}")

    # Min SDK version
    print(f"\n{YELLOW_COLOR}Min SDK Version: {min_sdk_version if min_sdk_version else 'Not specified'}{RESET_COLOR}")
    if min_sdk_version is not None and int(min_sdk_version) < 26:
        print(f"{YELLOW_COLOR}If minSdkVersion is lesser than 26 Report{RESET_COLOR}")
        print(f"{RED_BLINK_COLOR}Note: It will change in future :) {RESET_COLOR}")

    # Exported components
    print(f"\n{GREEN_COLOR}Exported Components:{RESET_COLOR}")
    if exported_warnings:
        for warning in exported_warnings:
            print(f"{RED_COLOR}{warning} {PURPLE_COLOR}[VULNERABLE]{RESET_COLOR}")
    else:
        print(f"{YELLOW_COLOR}No exported components detected.{RESET_COLOR}")

    # Added separator line before Detailed Summary
    print(f"\n{'-'*100}")  # Separator line

    # Detailed Summary Box
    print(f"\n{GREEN_COLOR}Detailed Summary:{RESET_COLOR}")
    print(f"{YELLOW_COLOR}Package Name: {package_name if package_name else 'Not specified'}{RESET_COLOR}")
    print(f"{YELLOW_COLOR}Total Permissions: {len(permissions)}{RESET_COLOR}")
    print(f"{YELLOW_COLOR}Total Dangerous Permissions: {len(dangerous_permissions)}{RESET_COLOR}")
    print(f"{YELLOW_COLOR}Exported Components Found: {len(exported_warnings)}{RESET_COLOR}")
    print(f"{YELLOW_COLOR}Target SDK Version: {target_sdk_version if target_sdk_version else 'Not specified'}{RESET_COLOR}")
    print(f"{YELLOW_COLOR}Min SDK Version: {min_sdk_version if min_sdk_version else 'Not specified'}{RESET_COLOR}")

    # Summary of important attributes
    for attribute, value in attribute_values.items():
        if value is not None:
            print(f"{YELLOW_COLOR}{attribute} is set to {value}{RESET_COLOR}")
        else:
            print(f"{YELLOW_COLOR}{attribute} is not specified{RESET_COLOR}")


if __name__ == "__main__":
    main()
