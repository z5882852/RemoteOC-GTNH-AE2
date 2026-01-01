import json
import re

def test(result: list):
    print(result)


def parse_data(result: list):
    res = json.loads(result[0])
    extract_number = lambda x: int(re.sub(r'[^0-9]', '', x))

    capacitor_dict = {}
    for item in res:
        if ":" in item:
            split_ = item.split(":")
            if (split_[0] == "EU Stored" or split_[0] == "Total wireless EU") and "^" in split_[1]:
                continue
            capacitor_dict[split_[0]] = split_[1]

    eu_stored = extract_number(capacitor_dict.get('EU Stored', '0').replace(',', ''))
    total_wireless_eu = extract_number(capacitor_dict.get('Total wireless EU', '0').replace(',', ''))

    capacitor_info = {
        "eu_stored": eu_stored,
        "total_wireless_eu": total_wireless_eu,
    }
    return capacitor_info


def check_cpu_free(result: list):
    cpu_status = json.loads(result[0]).get("data", {})
    return cpu_status.get("busy") == False
    