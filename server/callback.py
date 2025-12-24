import json

monitor_data = {
    "last": None,
    "current": None,
}


def test(result: list):
    print(result)


def parse_data(result: list):
    capacitor_info = json.loads(result[0])
    fluid = json.loads(result[1])
    item = json.loads(result[2])
    data = [capacitor_info]
    if monitor_data.get("current") is not None:
        monitor_data["last"] = monitor_data.get("current")
    monitor_data["current"] = data
    return monitor_data


def check_cpu_free(result: list):
    cpu_status = json.loads(result[0]).get("data", {})
    return cpu_status.get("busy") == False
    