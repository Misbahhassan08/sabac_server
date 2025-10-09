import copy
import json

my_default_json = {
    "Car Detail": {
        "basicInfo": {
            "bodyColor": "",
            "carModel": "",
            "carName": "",
            "carVariant":"",
            "company": "",
            # "registeredYear":"",
            
        },
        "techSpecs": {
            "assembly": "",
            "condition": "",
            "engineCapacity": "",
            "fuelType": "",
            "kmsDriven": "",
            "variant": "",
            # "inspectionDate":"",
            # "chassesNumber":"",
            # "engineNumber":"",
            # "regNo":"",
            # "registeredIn":"",
            # "auctionSheet":""
        },

        "bodyParts": {
            "Car Body (Outer)": {
                "Radiator Core Support": {
                    "Condition": {"Ok": 0, "Hit Impact": 1},
                    "img_urls": [""]
                },
                "Right Strut Tower": {
                    "Condition": {"Ok": 0, "Hit Impact": 1},
                    "img_urls": [""]
                },
                "Left Strut Tower": {
                    "Condition": {"Ok": 0, "Hit Impact": 1},
                    "img_urls": [""]
                },
                "Right Front Rail": {
                    "Condition": {"Ok": 0, "Hit Impact": 1},
                    "img_urls": [""]
                },
                "Left Front Rail": {
                    "Condition": {"Ok": 0, "Hit Impact": 1},
                    "img_urls": [""]
                },
                "Cowl Panel Firewall": {
                    "Condition": {"Ok": 0, "Hit Impact": 1}
                },
                "Front Bumper": {
                    "Condition": {"Ok": 0, "Repaint": 1}
                },
                "Bonnet": {
                    "Paint": {"Original": 0, "Repainted": 1},
                    "Seals": {"Ok": 0, "Repaired": 1, "Damaged": 1},
                    "img_urls": [""]
                },
                "Front Right Fender": {
                    "Paint": {"Original": 0, "Repainted": 1}
                },
                "Front Windscreen": {
                    "Condition": {"Ok": 0, "Scratch": 1, "Chip": 1, "Crack": 1}
                },
                "Right Mirror": {
                    "Condition": {"Ok": 0, "Not Rotating": 1, "Broken": 1},
                    "img_urls": [""]
                },
                "Front Right Door": {
                    "Paint": {"Original": 0, "Repainted": 1},
                    "Seals": {"Ok": 0, "Repaired": 1, "Damaged": 1},
                    "img_urls": [""]
                },
                "Foot Board (Right)": {
                    "Paint": {"Original": 0, "Repainted": 1},
                    "Seals": {"Ok": 0, "Repaired": 1, "Damaged": 1},
                    "img_urls": [""]
                },
                "Right A Pillar": {
                    "Condition": {"Ok": 0, "Repaired": 1},
                    "img_urls": [""]
                },
                "Rear Right Door": {
                    "Paint": {"Original": 0, "Repainted": 1},
                    "Seals": {"Ok": 0, "Repaired": 1, "Damaged": 1},
                    "img_urls": [""]
                },
                "Right B Pillar": {
                    "Paint": {"Original": 0, "Repainted": 1},
                    "Seals": {"Ok": 0, "Repaired": 1, "Damaged": 1},
                    "img_urls": [""]
                },
                "Rear Right Fender": {
                    "Condition": {"Ok": 0, "Repainted": 1},
                    "img_urls": [""]
                },
                "Right C Pillar": {
                    "Paint": {"Original": 0, "Repainted": 1},
                    "img_urls": [""]
                },
                "Right D Pillar": {
                    "Paint": {"Original": 0, "Repainted": 1},
                    "img_urls": [""]
                },
                "Back Windscreen": {
                    "Condition": {"Ok": 0, "Scratch": 1, "Crack": 1},
                    "img_urls": [""]
                },
                "Trunk": {
                    "Paint": {"Original": 0, "Repainted": 1},
                    "Seals": {"Ok": 0, "Repaired": 1, "Damaged": 1}
                },
                "Tool Kit / Spare Tyre": {
                    "Condition": {"Complete": 0, "Incomplete": 1, "Not Applicable": 0},
                    "img_urls": [""]
                },
                "Boot Floor": {
                    "Condition": {"Ok": 0, "Hit Impact": 1},
                    "img_urls": [""]
                },
                "Boot Lock Pillar": {
                    "Condition": {"Ok": 0, "Hit Impact": 1}
                },
                "Rear Sub Frame": {
                    "Condition": {"Ok": 0, "Hit Impact": 1},
                    "img_urls": [""]
                },
                "Left D Pillar": {
                    "Condition": {"Not Applicable": 0, "Ok": 0, "Repair": 1},
                    "img_urls": [""]
                },
                "Left Rear Fender": {
                    "Paint": {"Original": 0, "Repainted": 1},
                    "Seals": {"Ok": 0, "Repaired": 1, "Damaged": 1}
                },
                "Left C Pillar": {
                    "Condition": {"Ok": 0, "Repaired": 1},
                    "img_urls": [""]
                },
                "Left Rear Door": {
                    "Condition": {"Ok": 0, "Repainted": 1},
                    "img_urls": [""]
                },
                "Foot Board (Left)": {
                    "Condition": {"Ok": 0, "Repainted": 1},
                    "img_urls": [""]
                },
                "Left B Pillar": {
                    "Condition": {"Ok": 0, "Repair": 1},
                    "img_urls": [""]
                },
                "Left Front Door": {
                    "Paint": {"Original": 0, "Repainted": 1},
                    "Seals": {"Ok": 0, "Repaired": 1, "Damaged": 1},
                    "img_urls": [""]
                },
                "Left A Pillar": {
                    "Condition": {"Ok": 0, "Repaired": 1},
                    "img_urls": [""]
                },
                "Front Sub Frame": {
                    "Condition": {"Ok": 0, "Hit Impact": 1},
                    "img_urls": [""]
                },
                "Roof": {
                    "Condition": {"Ok": 0, "Repainted": 1}
                },
                "Ladder Frame": {
                    "Condition": {"Ok": 0, "Hit Impact": 1, "Not Applicable": 0},
                    "img_urls": [""]
                }
            },

            "Engine/Transmission": {
                "Engine Oil Leakage": {
                    "Condition": {"No Leakage": 0, "Leakage": 1, "Seepage": 1}
                },
                "Transmission Leakage": {
                    "Condition": {"No Leakage": 0, "Leakage": 1, "Seepage": 1}
                },
                "Coolant Leakage": {
                    "Condition": {"No Leakage": 0, "Leakage": 1, "Seepage": 1}
                },
                "Brake Oil Leakage": {
                    "Condition": {"No Leakage": 0, "Leakage": 1, "Seepage": 1}
                },
                "Power Steering Leakage": {
                    "Condition": {"No Leakage": 0, "Leakage": 1, "Seepage": 1}
                },
                "4x4 Leakage": {
                    "Condition": {"No Leakage": 0, "Leakage": 1, "Seepage": 1, "Not Available": 0}
                },
                "Differential Oil Leakage": {
                    "Condition": {"No Leakage": 0, "Leakage": 1, "Seepage": 1, "Not Available": 0}
                },
                "Fan Belts": {
                    "Condition": {"Ok": 0, "Crack": 1}
                },
                "Wires/Wiring": {
                    "Condition": {"Ok": 0, "Repaired": 1, "Damaged": 1}
                },
                "Engine Blow Manual Check": {
                    "Condition": {"Not Applicable": 0, "Ok": 0, "Engine Blow": 1}
                },
                "Engine Noise": {
                    "Condition": {"Normal": 0, "Abnormal": 1}
                },
                "Engine Vibration": {
                    "Condition": {"Normal": 0, "Abnormal": 1}
                },
                "Pulleys Adjuster Belts Noise": {
                    "Condition": {"Normal": 0, "Abnormal": 1}
                },
                "Hoses": {
                    "Condition": {"Normal": 0, "Leakage": 1}
                },
                "Radiator": {
                    "Condition": {"Normal": 0, "Leakage": 1, "Damaged": 1}
                },
                "Suction Fan": {
                    "Condition": {"Working": 0, "Not Working": 1}
                },
                "Starter Operation": {
                    "Condition": {"Ok": 0, "Long Starting": 1}
                },
                "Exhaust Sound": {
                    "Condition": {"Normal": 0, "Abnormal": 1}
                }
            },

            "Interior": {
                "Steering Wheel": {
                    "Condition": {"Ok": 0, "Scratch": 1, "Fade": 1, "Damaged": 1}
                },
                "Steering Button": {
                    "Condition": {"Not Applicable": 0, "Working Properly": 0, "Not Working Properly": 1}
                },
                "Dash Board": {
                    "Condition": {"Ok": 0, "Scratch": 1, "Damaged": 1, "Fade": 1}
                },
                "Glove Box": {
                    "Condition": {"Ok": 0, "Not Working": 1, "Damaged": 1}
                },
                "Horn": {
                    "Condition": {"Working Properly": 0, "Not Working Properly": 1}
                },
                "Wiper/Washer Speed": {
                    "Condition": {"Working Properly": 0, "Not Working Properly": 1}
                },
                "Rear View Mirror Dimmer": {
                    "Condition": {"Ok": 0, "Not Showing Reflection": 1, "Damaged": 1}
                },
                "Seat Controls": {
                    "Condition": {"Working Properly": 0, "Not Working Properly": 1}
                },
                "All Seats Covers": {
                    "Condition": {"Ok": 0, "Damaged": 1, "After Market Installed": 1}
                },
                "All Seats Belts": {
                    "Condition": {"Ok": 0, "Damaged": 1, "Not Working": 1}
                },
                "All Power Windows": {
                    "Condition": {"Working Properly": 0, "Not Working Properly": 1}
                },
                "Auto Lock Button": {
                    "Condition": {"Working Properly": 0, "Not Working Properly": 1}
                },
                "All Interior Lighting": {
                    "Condition": {"Working Properly": 0, "Not Working Properly": 1}
                },
                "A/C": {
                    "Condition": {"Working Properly": 0, "Not Working Properly": 1}
                },
                "Heater": {
                    "Condition": {"Working Properly": 0, "Not Working Properly": 1}
                },
                "Rear Camera": {
                    "Condition": {"Working": 0, "Not Working": 1, "Not Applicable": 0}
                },
                "Roof Posish": {
                    "Condition": {"Ok": 0, "Dirty": 1, "Damaged": 1}
                },
                "Floor Mat": {
                    "Condition": {"Ok": 0, "Dirty": 1, "Damaged": 1}
                },
                "Sun Roof": {
                    "Condition": {"Working": 0, "Not Working": 1, "Glass Damaged": 1, "Scratch": 1, "Not Applicable": 0}
                },
                "Computer Scanner Errors": {
                    "Condition": {"No Error": 0, "Error": 1},
                    "img_urls": [""]
                }
            },

            "Exterior Lights": {
                "Front Right Headlight": {
                    "Condition": {"Ok": 0, "Foggy": 1, "Repaired": 1, "Damaged": 1}
                },
                "Front Left Headlight": {
                    "Condition": {"Ok": 0, "Foggy": 1, "Repaired": 1, "Damaged": 1}
                },
                "Rear Right Tail Light": {
                    "Condition": {"Ok": 0, "Foggy": 1, "Repaired": 1, "Damaged": 1}
                },
                "Rear Left Tail Light": {
                    "Condition": {"Ok": 0, "Foggy": 1, "Repaired": 1, "Damaged": 1}
                },
                "Fog Light": {
                    "Condition": {"Not Applicable": 0, "Ok": 0, "Not Working": 1}
                }
            },

            "Brakes & Tyres": {
                "Front Right Tyre": {
                    "Remaining Thread": {"100%": 0, "75%": 1, "50%": 2, "25%": 3, "0%": 4},
                    "Brake Pads": {"More than 50%": 0, "Less than 50%": 1}
                },
                "Rear Right Tyre": {
                    "Remaining Thread": {"100%": 0, "75%": 1, "50%": 2, "25%": 3, "0%": 4}
                },
                "Rear Left Tyre": {
                    "Remaining Thread": {"100%": 0, "75%": 1, "50%": 2, "25%": 3, "0%": 4}
                },
                "Front Left Tyre": {
                    "Remaining Thread": {"100%": 0, "75%": 1, "50%": 2, "25%": 3, "0%": 4}
                },
                "Front Left Tyre Disc Pad": {
                    "Remaining Thread": {"100%": 0, "75%": 1, "50%": 2, "25%": 3, "0%": 4},
                    "Brake Pads": {"More than 50%": 0, "Less than 50%": 1}
                }
            },

            "Test Drive Remarks": {
                "Engine Pick": {
                    "Condition": {"Normal": 0, "Abnormal": 1}
                },
                "Gear Shifting": {
                    "Condition": {
                        "Normal": 0,
                        "Jerk While Shifting": 1,
                        "Delay in Shift": 1,
                        "Problem in Shifting": 1
                    }
                },
                "Brake Response": {
                    "Condition": {"Normal": 0, "Abnormal": 1}
                },
                "ABS Operation": {
                    "Condition": {"Working Properly": 0, "Not Working Properly": 1, "Not Available": 0}
                },
                "Front Suspension Noise": {
                    "Condition": {"Normal": 0, "Abnormal": 1}
                },
                "Rear Suspension Noise": {
                    "Condition": {"Normal": 0, "Abnormal": 1}
                },
                "Exhaust": {
                    "Condition": {"Normal": 0, "Abnormal": 1}
                },
                "A/C While Driving": {
                    "Condition": {"Normal": 0, "Abnormal": 1}
                },
                "Speedometer and Other Gauges": {
                    "Condition": {"Working Properly": 0, "Not Working Properly": 1}
                },
                "Wheel Alignment": {
                    "Condition": {"Centred": 0, "Not Centred": 1}
                },
                "4x4": {
                    "Condition": {"Engaging": 0, "Not Engaging": 1, "Not Available": 0}
                },
                "Wheel Balancing": {
                    "Condition": {"Normal": 0, "Abnormal": 1}
                }
            }
        }
            }
        }



# my_default_json = {
#     "Car Detail": {
#         "basicInfo": {
#             "bodyColor": "",
#             "carModel": "",
#             "carName": "",
#             "carVariant":"",
#             "company": "",
#             "registeredYear":"",
            
#         },
#         "techSpecs": {
#             "assembly": "",
#             "condition": "",
#             "engineCapacity": "",
#             "fuelType": "",
#             "kmsDriven": "",
#             "variant": "",
#             "inspectionDate":"",
#             "chassesNumber":"",
#             "engineNumber":"",
#             "regNo":"",
#             "registeredIn":"",
#             "auctionSheet":""
#         },
#         "CarInspectionData" : {
#             "Car Detail": {
#                 "Body Parts Inspection": {
#                     "Car Body (Outer)": {
#                         "Radiator Core Support": {
#                             "Condition": {"Ok": 0, "Hit Impact": 1},
#                             "img_urls": [""]
#                         },
#                         "Right Strut Tower": {
#                             "Condition": {"Ok": 0, "Hit Impact": 1},
#                             "img_urls": [""]
#                         },
#                         "Left Strut Tower": {
#                             "Condition": {"Ok": 0, "Hit Impact": 1},
#                             "img_urls": [""]
#                         },
#                         "Right Front Rail": {
#                             "Condition": {"Ok": 0, "Hit Impact": 1},
#                             "img_urls": [""]
#                         },
#                         "Left Front Rail": {
#                             "Condition": {"Ok": 0, "Hit Impact": 1},
#                             "img_urls": [""]
#                         },
#                         "Cowl Panel Firewall": {
#                             "Condition": {"Ok": 0, "Hit Impact": 1}
#                         },
#                         "Front Bumper": {
#                             "Condition": {"Ok": 0, "Repaint": 1}
#                         },
#                         "Bonnet": {
#                             "Paint": {"Original": 0, "Repainted": 1},
#                             "Seals": {"Ok": 0, "Repaired": 1, "Damaged": 1},
#                             "img_urls": [""]
#                         },
#                         "Front Right Fender": {
#                             "Paint": {"Original": 0, "Repainted": 1}
#                         },
#                         "Front Windscreen": {
#                             "Condition": {"Ok": 0, "Scratch": 1, "Chip": 1, "Crack": 1}
#                         },
#                         "Right Mirror": {
#                             "Condition": {"Ok": 0, "Not Rotating": 1, "Broken": 1},
#                             "img_urls": [""]
#                         },
#                         "Front Right Door": {
#                             "Paint": {"Original": 0, "Repainted": 1},
#                             "Seals": {"Ok": 0, "Repaired": 1, "Damaged": 1},
#                             "img_urls": [""]
#                         },
#                         "Foot Board (Right)": {
#                             "Paint": {"Original": 0, "Repainted": 1},
#                             "Seals": {"Ok": 0, "Repaired": 1, "Damaged": 1},
#                             "img_urls": [""]
#                         },
#                         "Right A Pillar": {
#                             "Condition": {"Ok": 0, "Repaired": 1},
#                             "img_urls": [""]
#                         },
#                         "Rear Right Door": {
#                             "Paint": {"Original": 0, "Repainted": 1},
#                             "Seals": {"Ok": 0, "Repaired": 1, "Damaged": 1},
#                             "img_urls": [""]
#                         },
#                         "Right B Pillar": {
#                             "Paint": {"Original": 0, "Repainted": 1},
#                             "Seals": {"Ok": 0, "Repaired": 1, "Damaged": 1},
#                             "img_urls": [""]
#                         },
#                         "Rear Right Fender": {
#                             "Condition": {"Ok": 0, "Repainted": 1},
#                             "img_urls": [""]
#                         },
#                         "Right C Pillar": {
#                             "Paint": {"Original": 0, "Repainted": 1},
#                             "img_urls": [""]
#                         },
#                         "Right D Pillar": {
#                             "Paint": {"Original": 0, "Repainted": 1},
#                             "img_urls": [""]
#                         },
#                         "Back Windscreen": {
#                             "Condition": {"Ok": 0, "Scratch": 1, "Crack": 1},
#                             "img_urls": [""]
#                         },
#                         "Trunk": {
#                             "Paint": {"Original": 0, "Repainted": 1},
#                             "Seals": {"Ok": 0, "Repaired": 1, "Damaged": 1}
#                         },
#                         "Tool Kit / Spare Tyre": {
#                             "Condition": {"Complete": 0, "Incomplete": 1, "Not Applicable": 0},
#                             "img_urls": [""]
#                         },
#                         "Boot Floor": {
#                             "Condition": {"Ok": 0, "Hit Impact": 1},
#                             "img_urls": [""]
#                         },
#                         "Boot Lock Pillar": {
#                             "Condition": {"Ok": 0, "Hit Impact": 1}
#                         },
#                         "Rear Sub Frame": {
#                             "Condition": {"Ok": 0, "Hit Impact": 1},
#                             "img_urls": [""]
#                         },
#                         "Left D Pillar": {
#                             "Condition": {"Not Applicable": 0, "Ok": 0, "Repair": 1},
#                             "img_urls": [""]
#                         },
#                         "Left Rear Fender": {
#                             "Paint": {"Original": 0, "Repainted": 1},
#                             "Seals": {"Ok": 0, "Repaired": 1, "Damaged": 1}
#                         },
#                         "Left C Pillar": {
#                             "Condition": {"Ok": 0, "Repaired": 1},
#                             "img_urls": [""]
#                         },
#                         "Left Rear Door": {
#                             "Condition": {"Ok": 0, "Repainted": 1},
#                             "img_urls": [""]
#                         },
#                         "Foot Board (Left)": {
#                             "Condition": {"Ok": 0, "Repainted": 1},
#                             "img_urls": [""]
#                         },
#                         "Left B Pillar": {
#                             "Condition": {"Ok": 0, "Repair": 1},
#                             "img_urls": [""]
#                         },
#                         "Left Front Door": {
#                             "Paint": {"Original": 0, "Repainted": 1},
#                             "Seals": {"Ok": 0, "Repaired": 1, "Damaged": 1},
#                             "img_urls": [""]
#                         },
#                         "Left A Pillar": {
#                             "Condition": {"Ok": 0, "Repaired": 1},
#                             "img_urls": [""]
#                         },
#                         "Front Sub Frame": {
#                             "Condition": {"Ok": 0, "Hit Impact": 1},
#                             "img_urls": [""]
#                         },
#                         "Roof": {
#                             "Condition": {"Ok": 0, "Repainted": 1}
#                         },
#                         "Ladder Frame": {
#                             "Condition": {"Ok": 0, "Hit Impact": 1, "Not Applicable": 0},
#                             "img_urls": [""]
#                         }
#                     },

#                     "Engine/Transmission": {
#                         "Engine Oil Leakage": {
#                             "Condition": {"No Leakage": 0, "Leakage": 1, "Seepage": 1}
#                         },
#                         "Transmission Leakage": {
#                             "Condition": {"No Leakage": 0, "Leakage": 1, "Seepage": 1}
#                         },
#                         "Coolant Leakage": {
#                             "Condition": {"No Leakage": 0, "Leakage": 1, "Seepage": 1}
#                         },
#                         "Brake Oil Leakage": {
#                             "Condition": {"No Leakage": 0, "Leakage": 1, "Seepage": 1}
#                         },
#                         "Power Steering Leakage": {
#                             "Condition": {"No Leakage": 0, "Leakage": 1, "Seepage": 1}
#                         },
#                         "4x4 Leakage": {
#                             "Condition": {"No Leakage": 0, "Leakage": 1, "Seepage": 1, "Not Available": 0}
#                         },
#                         "Differential Oil Leakage": {
#                             "Condition": {"No Leakage": 0, "Leakage": 1, "Seepage": 1, "Not Available": 0}
#                         },
#                         "Fan Belts": {
#                             "Condition": {"Ok": 0, "Crack": 1}
#                         },
#                         "Wires/Wiring": {
#                             "Condition": {"Ok": 0, "Repaired": 1, "Damaged": 1}
#                         },
#                         "Engine Blow Manual Check": {
#                             "Condition": {"Not Applicable": 0, "Ok": 0, "Engine Blow": 1}
#                         },
#                         "Engine Noise": {
#                             "Condition": {"Normal": 0, "Abnormal": 1}
#                         },
#                         "Engine Vibration": {
#                             "Condition": {"Normal": 0, "Abnormal": 1}
#                         },
#                         "Pulleys Adjuster Belts Noise": {
#                             "Condition": {"Normal": 0, "Abnormal": 1}
#                         },
#                         "Hoses": {
#                             "Condition": {"Normal": 0, "Leakage": 1}
#                         },
#                         "Radiator": {
#                             "Condition": {"Normal": 0, "Leakage": 1, "Damaged": 1}
#                         },
#                         "Suction Fan": {
#                             "Condition": {"Working": 0, "Not Working": 1}
#                         },
#                         "Starter Operation": {
#                             "Condition": {"Ok": 0, "Long Starting": 1}
#                         },
#                         "Exhaust Sound": {
#                             "Condition": {"Normal": 0, "Abnormal": 1}
#                         }
#                     },

#                     "Interior": {
#                         "Steering Wheel": {
#                             "Condition": {"Ok": 0, "Scratch": 1, "Fade": 1, "Damaged": 1}
#                         },
#                         "Steering Button": {
#                             "Condition": {"Not Applicable": 0, "Working Properly": 0, "Not Working Properly": 1}
#                         },
#                         "Dash Board": {
#                             "Condition": {"Ok": 0, "Scratch": 1, "Damaged": 1, "Fade": 1}
#                         },
#                         "Glove Box": {
#                             "Condition": {"Ok": 0, "Not Working": 1, "Damaged": 1}
#                         },
#                         "Horn": {
#                             "Condition": {"Working Properly": 0, "Not Working Properly": 1}
#                         },
#                         "Wiper/Washer Speed": {
#                             "Condition": {"Working Properly": 0, "Not Working Properly": 1}
#                         },
#                         "Rear View Mirror Dimmer": {
#                             "Condition": {"Ok": 0, "Not Showing Reflection": 1, "Damaged": 1}
#                         },
#                         "Seat Controls": {
#                             "Condition": {"Working Properly": 0, "Not Working Properly": 1}
#                         },
#                         "All Seats Covers": {
#                             "Condition": {"Ok": 0, "Damaged": 1, "After Market Installed": 1}
#                         },
#                         "All Seats Belts": {
#                             "Condition": {"Ok": 0, "Damaged": 1, "Not Working": 1}
#                         },
#                         "All Power Windows": {
#                             "Condition": {"Working Properly": 0, "Not Working Properly": 1}
#                         },
#                         "Auto Lock Button": {
#                             "Condition": {"Working Properly": 0, "Not Working Properly": 1}
#                         },
#                         "All Interior Lighting": {
#                             "Condition": {"Working Properly": 0, "Not Working Properly": 1}
#                         },
#                         "A/C": {
#                             "Condition": {"Working Properly": 0, "Not Working Properly": 1}
#                         },
#                         "Heater": {
#                             "Condition": {"Working Properly": 0, "Not Working Properly": 1}
#                         },
#                         "Rear Camera": {
#                             "Condition": {"Working": 0, "Not Working": 1, "Not Applicable": 0}
#                         },
#                         "Roof Posish": {
#                             "Condition": {"Ok": 0, "Dirty": 1, "Damaged": 1}
#                         },
#                         "Floor Mat": {
#                             "Condition": {"Ok": 0, "Dirty": 1, "Damaged": 1}
#                         },
#                         "Sun Roof": {
#                             "Condition": {"Working": 0, "Not Working": 1, "Glass Damaged": 1, "Scratch": 1, "Not Applicable": 0}
#                         },
#                         "Computer Scanner Errors": {
#                             "Condition": {"No Error": 0, "Error": 1},
#                             "img_urls": [""]
#                         }
#                     },

#                     "Exterior Lights": {
#                         "Front Right Headlight": {
#                             "Condition": {"Ok": 0, "Foggy": 1, "Repaired": 1, "Damaged": 1}
#                         },
#                         "Front Left Headlight": {
#                             "Condition": {"Ok": 0, "Foggy": 1, "Repaired": 1, "Damaged": 1}
#                         },
#                         "Rear Right Tail Light": {
#                             "Condition": {"Ok": 0, "Foggy": 1, "Repaired": 1, "Damaged": 1}
#                         },
#                         "Rear Left Tail Light": {
#                             "Condition": {"Ok": 0, "Foggy": 1, "Repaired": 1, "Damaged": 1}
#                         },
#                         "Fog Light": {
#                             "Condition": {"Not Applicable": 0, "Ok": 0, "Not Working": 1}
#                         }
#                     },

#                     "Brakes & Tyres": {
#                         "Front Right Tyre": {
#                             "Remaining Thread": {"100%": 0, "75%": 1, "50%": 2, "25%": 3, "0%": 4},
#                             "Brake Pads": {"More than 50%": 0, "Less than 50%": 1}
#                         },
#                         "Rear Right Tyre": {
#                             "Remaining Thread": {"100%": 0, "75%": 1, "50%": 2, "25%": 3, "0%": 4}
#                         },
#                         "Rear Left Tyre": {
#                             "Remaining Thread": {"100%": 0, "75%": 1, "50%": 2, "25%": 3, "0%": 4}
#                         },
#                         "Front Left Tyre": {
#                             "Remaining Thread": {"100%": 0, "75%": 1, "50%": 2, "25%": 3, "0%": 4}
#                         },
#                         "Front Left Tyre Disc Pad": {
#                             "Remaining Thread": {"100%": 0, "75%": 1, "50%": 2, "25%": 3, "0%": 4},
#                             "Brake Pads": {"More than 50%": 0, "Less than 50%": 1}
#                         }
#                     },

#                     "Test Drive Remarks": {
#                         "Engine Pick": {
#                             "Condition": {"Normal": 0, "Abnormal": 1}
#                         },
#                         "Gear Shifting": {
#                             "Condition": {
#                                 "Normal": 0,
#                                 "Jerk While Shifting": 1,
#                                 "Delay in Shift": 1,
#                                 "Problem in Shifting": 1
#                             }
#                         },
#                         "Brake Response": {
#                             "Condition": {"Normal": 0, "Abnormal": 1}
#                         },
#                         "ABS Operation": {
#                             "Condition": {"Working Properly": 0, "Not Working Properly": 1, "Not Available": 0}
#                         },
#                         "Front Suspension Noise": {
#                             "Condition": {"Normal": 0, "Abnormal": 1}
#                         },
#                         "Rear Suspension Noise": {
#                             "Condition": {"Normal": 0, "Abnormal": 1}
#                         },
#                         "Exhaust": {
#                             "Condition": {"Normal": 0, "Abnormal": 1}
#                         },
#                         "A/C While Driving": {
#                             "Condition": {"Normal": 0, "Abnormal": 1}
#                         },
#                         "Speedometer and Other Gauges": {
#                             "Condition": {"Working Properly": 0, "Not Working Properly": 1}
#                         },
#                         "Wheel Alignment": {
#                             "Condition": {"Centred": 0, "Not Centred": 1}
#                         },
#                         "4x4": {
#                             "Condition": {"Engaging": 0, "Not Engaging": 1, "Not Available": 0}
#                         },
#                         "Wheel Balancing": {
#                             "Condition": {"Normal": 0, "Abnormal": 1}
#                         }
#                     }
#                 }
#             }
#         }

#     }
# }

# my_default_json = {
#     "Car Detail": {
#         "basicInfo": {
#             "bodyColor": "",
#             "carModel": "",
#             "carName": "",
#             "carVariant":"",
#             "company": ""
#         },
#         "techSpecs": {
#             "assembly": "",
#             "condition": "",
#             "engineCapacity": "",
#             "fuelType": "",
#             "kmsDriven": "",
#             "variant": ""
#         },
#         "bodyParts": {
#             "Car Body (Outer)": {
#                 "Front Right Fender": {
#                     "Paint": {"Original": 0, "Repainted": 0},
#                     "Seals": {"Ok": 0, "Damaged": 0, "Repaired": 0},
#                     "Dents": {"None": 0, "Minor": 0, "Major": 0},
#                 },
#                 "Front Left Fender": {
#                     "Paint": {"Original": 0, "Repainted": 0},
#                     "Seals": {"Ok": 0, "Damaged": 0, "Repaired": 0},
#                     "Dents": {"None": 0, "Minor": 0, "Major": 0},
#                 },
#                 "Bonnet": {
#                     "Paint": {"Original": 0, "Repainted": 0},
#                     "Seals": {"Ok": 0, "Damaged": 0, "Repaired": 0},
#                     "img_urls": [""],
#                 },
#                 "Front Driver Door": {
#                     "Paint": {"Original": 0, "Repainted": 0},
#                     "Seals": {"Ok": 0, "Damaged": 0, "Repaired": 0},
#                     "img_urls": [""],
#                 },
#                 "Front Passenger Door": {
#                     "Paint": {"Original": 0, "Repainted": 0},
#                     "Seals": {"Ok": 0, "Damaged": 0, "Repaired": 0},
#                     "img_urls": [""],
#                 },
#                 "Rear Right Door": {
#                     "Paint": {"Original": 0, "Repainted": 0},
#                     "Seals": {"Ok": 0, "Damaged": 0, "Repaired": 0},
#                     "img_urls": [""],
#                 },
#                 "Rear Right Fender": {
#                     "Paint": {"Original": 0, "Repainted": 0},
#                     "Seals": {"Ok": 0, "Damaged": 0, "Repaired": 0},
#                     "img_urls": [""],
#                 },
#                 "Rear Left Fender": {
#                     "Paint": {"Original": 0, "Repainted": 0},
#                     "Seals": {"Ok": 0, "Damaged": 0, "Repaired": 0},
#                     "img_urls": [""],
#                 },
#             },
#             #   BODY FRAME
#             "Body Frame": {
#                 "Radiator Core Support": {
#                     "Condition": {"Ok": 0, "Damaged": 0, "Repaired": 0},
#                     "img_urls": [""],
#                 },
#                 "Right Strut Tower Appron": {
#                     "Condition": {"Ok": 0, "Damaged": 0, "Repaired": 0},
#                     "img_urls": [""],
#                 },
#                 "Left Strut Tower Appron": {
#                     "Condition": {"Ok": 0, "Damaged": 0, "Repaired": 0},
#                     "img_urls": [""],
#                 },
#                 "Right Front Rail": {
#                     "Condition": {"Ok": 0, "Damaged": 0, "Repaired": 0},
#                     "img_urls": [""],
#                 },
#                 "Left Front Rail": {
#                     "Condition": {"Ok": 0, "Damaged": 0, "Repaired": 0},
#                     "img_urls": [""],
#                 },
#                 "Cowl Panel Firewall": {
#                     "Condition": {"Ok": 0, "Damaged": 0, "Repaired": 0},
#                     "img_urls": [""],
#                 },
#                 "Right Pilar Front": {
#                     "Condition": {"Ok": 0, "Damaged": 0, "Repaired": 0},
#                     "img_urls": [""],
#                 },
#                 "Right Pilar Back": {
#                     "Condition": {"Ok": 0, "Damaged": 0, "Repaired": 0},
#                     "img_urls": [""],
#                 },
#                 "Left Pilar Front": {
#                     "Condition": {"Ok": 0, "Damaged": 0, "Repaired": 0},
#                     "img_urls": [""],
#                 },
#                 "Left Pilar Back": {
#                     "Condition": {"Ok": 0, "Damaged": 0, "Repaired": 0},
#                     "img_urls": [""],
#                 },
#                 "Right Front Side Panel": {
#                     "Condition": {"Ok": 0, "Damaged": 0, "Repaired": 0},
#                     "img_urls": [""],
#                 },
#                 "Right Rear Side Panel": {
#                     "Condition": {"Ok": 0, "Damaged": 0, "Repaired": 0},
#                     "img_urls": [""],
#                 },
#                 "Left Front Side Panel": {
#                     "Condition": {"Ok": 0, "Damaged": 0, "Repaired": 0},
#                     "img_urls": [""],
#                 },
#                 "Left Rear Side Panel": {
#                     "Condition": {"Ok": 0, "Damaged": 0, "Repaired": 0},
#                     "img_urls": [""],
#                 },
#             },
#             #   TEST DRIVE REMARKS
#             "Test Drive Remarks": {
#                 "Engine Starts Properly": {
#                     "Status": {"Yes": 0, "No": 0, "With Difficulty": 0}
#                 },
#                 "Engine Health": {"Condition": {"Good": 0, "Average": 0, "Poor": 0}},
#                 "Gear Shifting": {
#                     "Smoothness": {
#                         "Smooth": 0,
#                         "Rough": 0,
#                         "Stuck": 0,
#                         "Jerk": 0,
#                         "late": 0,
#                     }
#                 },
#                 "Turning": {"Condition": {"Normal": 0, "Abnormal": 0}},
#                 "Suspention Check": {"Condition": {"Normal": 0, "Abnormal": 0}},
#                 "Exhaust": {"Condition": {"Normal": 0, "Abnormal": 0}},
#                 "Cruise Control": {
#                     "Condition": {"Not Available": 0, "Working": 0, "Not Working": 0}
#                 },
#                 "Stearing Controls": {
#                     "Condition": {"Not Available": 0, "Working": 0, "Not Working": 0}
#                 },
#                 "Horn": {
#                     "Condition": {"Not Available": 0, "Working": 0, "Not Working": 0}
#                 },
#                 "Cameras": {
#                     "Condition": {"Not Available": 0, "Working": 0, "Not Working": 0}
#                 },
#                 "Sensors": {
#                     "Condition": {"Not Available": 0, "Working": 0, "Not Working": 0}
#                 },
#                 "Warning Lights": {"Present": {"Yes": 0, "No": 0}},
#             },
#             #   DOORS CHECK
#             "Doors Check": {
#                 "Front Right Door": {
#                     "Paint": {"Original": 0, "Repainted": 0},
#                     "Seals": {"Ok": 0, "Damaged": 0, "Repaired": 0},
#                 },
#                 "Front Left Door": {
#                     "Paint": {"Original": 0, "Repainted": 0},
#                     "Seals": {"Ok": 0, "Damaged": 0, "Repaired": 0},
#                 },
#                 # "Rear Right Door": {
#                 #     "Paint": {"Original": 0, "Repainted": 0},
#                 #     "Seals": {"Ok": 0, "Damaged": 0, "Repaired": 0},
#                 # },
#                 "Rear Left Door": {
#                     "Paint": {"Original": 0, "Repainted": 0},
#                     "Seals": {"Ok": 0, "Damaged": 0, "Repaired": 0},
#                 },
#             },
#             #   INTERIOR
#             "Interior": {
#                 "Stearing Wheel": {
#                     "Condition": {"Damage": 0, "Covered": 0, "Normal": 0},
#                     "img_urls": [""],
#                 },
#                 "Dashboard": {
#                     "Condition": {"Damage": 0, "Normal": 0, "Faded": 0},
#                     "img_urls": [""],
#                 },
#                 "Front Driver Seat": {
#                     "Condition": {"Damage": 0, "Normal": 0},
#                     "img_urls": [""],
#                 },
#                 "Front Passenger Seat": {
#                     "Condition": {"Damage": 0, "Normal": 0},
#                     "img_urls": [""],
#                 },
#                 "Rear Seats": {
#                     "Condition": {"Damage": 0, "Normal": 0},
#                     "img_urls": [""],
#                 },
#                 "Roof": {
#                     "Condition": {"Damage": 0, "Normal": 0, "Dirty": 0},
#                     "img_urls": [""],
#                 },
#             },
#             #   Boot
#             "Boot": {
#                 "Boot Floor": {
#                     "Condition": {"Clean": 0, "Dirty": 0, "Damaged": 0},
#                     "img_urls": [""],
#                 },
#                 "Spare Tyre": {"Status": {"Present": 0, "Missing": 0, "Damaged": 0}},
#                 "Tools": {
#                     "Completeness": {"Complete": 0, "Incomplete": 0, "Missing": 0}
#                 },
#             },
#         }
#     }
# }


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
        
    if "comments" in new_json:
        merged_json["Car Detail"]["comments"] = new_json["comments"]

    return merged_json


# Merging
# merged_result = merge_json(my_default_json, sample_json)

# # Pretty print
# print(json.dumps(merged_result, indent=4))
