def get_configured_int_value(inputs, key, default_value):
    return int(inputs.get(key, {"value": default_value})["value"])


def get_configured_float_value(inputs, key, default_value):
    return float(inputs.get(key, {"value": default_value})["value"])


def get_configured_string_value(inputs, key, default_value):
    return inputs.get(key, {"value": default_value})["value"]
