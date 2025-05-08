import json
import copy

my_default_json = {
    "Car Detail": {
        "basicInfo": {
            "bodyColor": "",
            "carModel": "",
            "carName": "",
            "company": ""
        },
        "techSpecs": {
            "assembly": "",
            "condition": "",
            "engineCapacity": "",
            "fuelType": "",
            "kmsDriven": "",
            "variant": ""
        },
        "bodyParts": {
            "Car Body (Outer)": {
                "Front Right Fender": {
                    "Paint": {"Original": 0, "Repainted": 0},
                    "Seals": {"Ok": 0, "Damaged": 0, "Repaired": 0},
                    "Dents": {"None": 0, "Minor": 0, "Major": 0},
                },
                "Front Left Fender": {
                    "Paint": {"Original": 0, "Repainted": 0},
                    "Seals": {"Ok": 0, "Damaged": 0, "Repaired": 0},
                    "Dents": {"None": 0, "Minor": 0, "Major": 0},
                },
                "Bonnet": {
                    "Paint": {"Original": 0, "Repainted": 0},
                    "Seals": {"Ok": 0, "Damaged": 0, "Repaired": 0},
                    "img_urls": [""],
                },
                "Front Driver Door": {
                    "Paint": {"Original": 0, "Repainted": 0},
                    "Seals": {"Ok": 0, "Damaged": 0, "Repaired": 0},
                    "img_urls": [""],
                },
                "Front Passenger Door": {
                    "Paint": {"Original": 0, "Repainted": 0},
                    "Seals": {"Ok": 0, "Damaged": 0, "Repaired": 0},
                    "img_urls": [""],
                },
                "Rear Right Door": {
                    "Paint": {"Original": 0, "Repainted": 0},
                    "Seals": {"Ok": 0, "Damaged": 0, "Repaired": 0},
                    "img_urls": [""],
                },
                "Rear Right Fender": {
                    "Paint": {"Original": 0, "Repainted": 0},
                    "Seals": {"Ok": 0, "Damaged": 0, "Repaired": 0},
                    "img_urls": [""],
                },
                "Rear Left Fender": {
                    "Paint": {"Original": 0, "Repainted": 0},
                    "Seals": {"Ok": 0, "Damaged": 0, "Repaired": 0},
                    "img_urls": [""],
                },
            },
            #   BODY FRAME
            "Body Frame": {
                "Radiator Core Support": {
                    "Condition": {"Ok": 0, "Damaged": 0, "Repaired": 0},
                    "img_urls": [""],
                },
                "Right Strut Tower Appron": {
                    "Condition": {"Ok": 0, "Damaged": 0, "Repaired": 0},
                    "img_urls": [""],
                },
                "Left Strut Tower Appron": {
                    "Condition": {"Ok": 0, "Damaged": 0, "Repaired": 0},
                    "img_urls": [""],
                },
                "Right Front Rail": {
                    "Condition": {"Ok": 0, "Damaged": 0, "Repaired": 0},
                    "img_urls": [""],
                },
                "Left Front Rail": {
                    "Condition": {"Ok": 0, "Damaged": 0, "Repaired": 0},
                    "img_urls": [""],
                },
                "Cowl Panel Firewall": {
                    "Condition": {"Ok": 0, "Damaged": 0, "Repaired": 0},
                    "img_urls": [""],
                },
                "Right Pilar Front": {
                    "Condition": {"Ok": 0, "Damaged": 0, "Repaired": 0},
                    "img_urls": [""],
                },
                "Right Pilar Back": {
                    "Condition": {"Ok": 0, "Damaged": 0, "Repaired": 0},
                    "img_urls": [""],
                },
                "Left Pilar Front": {
                    "Condition": {"Ok": 0, "Damaged": 0, "Repaired": 0},
                    "img_urls": [""],
                },
                "Left Pilar Back": {
                    "Condition": {"Ok": 0, "Damaged": 0, "Repaired": 0},
                    "img_urls": [""],
                },
                "Right Front Side Panel": {
                    "Condition": {"Ok": 0, "Damaged": 0, "Repaired": 0},
                    "img_urls": [""],
                },
                "Right Rear Side Panel": {
                    "Condition": {"Ok": 0, "Damaged": 0, "Repaired": 0},
                    "img_urls": [""],
                },
                "Left Front Side Panel": {
                    "Condition": {"Ok": 0, "Damaged": 0, "Repaired": 0},
                    "img_urls": [""],
                },
                "Left Rear Side Panel": {
                    "Condition": {"Ok": 0, "Damaged": 0, "Repaired": 0},
                    "img_urls": [""],
                },
            },
            #   TEST DRIVE REMARKS
            "Test Drive Remarks": {
                "Engine Starts Properly": {
                    "Status": {"Yes": 0, "No": 0, "With Difficulty": 0}
                },
                "Engine Health": {"Condition": {"Good": 0, "Average": 0, "Poor": 0}},
                "Gear Shifting": {
                    "Smoothness": {
                        "Smooth": 0,
                        "Rough": 0,
                        "Stuck": 0,
                        "Jerk": 0,
                        "late": 0,
                    }
                },
                "Turning": {"Condition": {"Normal": 0, "Abnormal": 0}},
                "Suspention Check": {"Condition": {"Normal": 0, "Abnormal": 0}},
                "Exhaust": {"Condition": {"Normal": 0, "Abnormal": 0}},
                "Cruise Control": {
                    "Condition": {"Not Available": 0, "Working": 0, "Not Working": 0}
                },
                "Stearing Controls": {
                    "Condition": {"Not Available": 0, "Working": 0, "Not Working": 0}
                },
                "Horn": {
                    "Condition": {"Not Available": 0, "Working": 0, "Not Working": 0}
                },
                "Cameras": {
                    "Condition": {"Not Available": 0, "Working": 0, "Not Working": 0}
                },
                "Sensors": {
                    "Condition": {"Not Available": 0, "Working": 0, "Not Working": 0}
                },
                "Warning Lights": {"Present": {"Yes": 0, "No": 0}},
            },
            #   DOORS CHECK
            "Doors Check": {
                "Front Right Door": {
                    "Paint": {"Original": 0, "Repainted": 0},
                    "Seals": {"Ok": 0, "Damaged": 0, "Repaired": 0},
                },
                "Front Left Door": {
                    "Paint": {"Original": 0, "Repainted": 0},
                    "Seals": {"Ok": 0, "Damaged": 0, "Repaired": 0},
                },
                "Rear Right Door": {
                    "Paint": {"Original": 0, "Repainted": 0},
                    "Seals": {"Ok": 0, "Damaged": 0, "Repaired": 0},
                },
                "Rear Left Door": {
                    "Paint": {"Original": 0, "Repainted": 0},
                    "Seals": {"Ok": 0, "Damaged": 0, "Repaired": 0},
                },
            },
            #   INTERIOR
            "Interior": {
                "Stearing Wheel": {
                    "Condition": {"Damage": 0, "Covered": 0, "Normal": 0},
                    "img_urls": [""],
                },
                "Dashboard": {
                    "Condition": {"Damage": 0, "Normal": 0, "Faded": 0},
                    "img_urls": [""],
                },
                "Front Driver Seat": {
                    "Condition": {"Damage": 0, "Normal": 0},
                    "img_urls": [""],
                },
                "Front Passenger Seat": {
                    "Condition": {"Damage": 0, "Normal": 0},
                    "img_urls": [""],
                },
                "Rear Seats": {
                    "Condition": {"Damage": 0, "Normal": 0},
                    "img_urls": [""],
                },
                "Roof": {
                    "Condition": {"Damage": 0, "Normal": 0, "Dirty": 0},
                    "img_urls": [""],
                },
            },
            #   Boot
            "Boot": {
                "Boot Floor": {
                    "Condition": {"Clean": 0, "Dirty": 0, "Damaged": 0},
                    "img_urls": [""],
                },
                "Spare Tyre": {"Status": {"Present": 0, "Missing": 0, "Damaged": 0}},
                "Tools": {
                    "Completeness": {"Complete": 0, "Incomplete": 0, "Missing": 0}
                },
            },
        }
    }
}


# -- other code here
sample_json = {
    "basicInfo": {
        "bodyColor": "haha",
        "carModel": "32323",
        "carName": "2323",
        "company": "2323"
    },
    "techSpecs": {
        "assembly": "ewrewrewr",
        "condition": "ewrewr",
        "engineCapacity": "ewrewr",
        "fuelType": "ewrewrwer",
        "kmsDriven": "erewr",
        "variant": "ewrwer"
    },
    "bodyParts": {
        "Front Left Fender": {
            "Paint": "Original",
            "Seals": "Ok",
            "Dents": "None"
        },
        "Bonnet": {
            "Paint": "Original",
            "Seals": "Ok"
        },
        "Front Right Fender": {
            "Paint": "Original",
            "Seals": "Ok",
            "Dents": "None"
        },
        "Rear Left Fender": {
            "Paint": "Original",
            "Seals": "Ok"
        },
        "Engine Health": {
            "Condition": "Good"
        },

    },
}


def merge_json(default_json, new_json):
    merged_json = copy.deepcopy(default_json)

    def find_and_update(part_name, category, selected_option):
        """
        Search for part_name inside merged_json and update the correct field.
        """
        sections = merged_json["Car Detail"]["bodyParts"]

        for section_name, section_parts in sections.items():
            if part_name in section_parts:
                part_info = section_parts[part_name]
                if category in part_info:
                    for option in part_info[category]:
                        part_info[category][option] = 0
                    if selected_option in part_info[category]:
                        part_info[category][selected_option] = 1
                    else:
                        print(
                            f"Warning: Option '{selected_option}' not found in '{category}' for '{part_name}'")
                else:
                    print(
                        f"Warning: Category '{category}' not found in '{part_name}'")
                return True  # Part found and processed
        print(f"Warning: Part '{part_name}' not found in any section")
        return False

    for part_name, part_values in new_json.get("bodyParts", {}).items():
        for category, selected_option in part_values.items():
            find_and_update(part_name, category, selected_option)

    # Merge basicInfo
    for key, value in new_json.get("basicInfo", {}).items():
        if key in merged_json["Car Detail"]["basicInfo"]:
            merged_json["Car Detail"]["basicInfo"][key] = value
        else:
            print(f"Warning: Key '{key}' not found in 'basicInfo'")

    # Merge techSpecs
    for key, value in new_json.get("techSpecs", {}).items():
        if key in merged_json["Car Detail"]["techSpecs"]:
            merged_json["Car Detail"]["techSpecs"][key] = value
        else:
            print(f"Warning: Key '{key}' not found in 'techSpecs'")

    return merged_json


# Merging
# merged_result = merge_json(my_default_json, sample_json)

# # Pretty print
# print(json.dumps(merged_result, indent=4))
