import json


def process_extra_context(context: dict):
    if not context:
        return ""
    if type(context) is str:
        raise TypeError(
            f"Context must be a object dict, not {type(context).__name__}!!!"
        )

    for key, value in context.items():
        if isinstance(value, (str, int, float, bool, list, dict, tuple, set)):
            continue
        elif hasattr(value, "__str__"):
            class_name = value.__class__.__name__
            new_value = f"<object ({class_name})>: {str(value)}"
            context.update({key: new_value})

    return " - " + json.dumps(context)
