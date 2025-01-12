import base64
import re
from typing import Any, Union

from PIL.Image import Image


def encode_image(image_path: Union[str, bytes]) -> str:
    if isinstance(image_path, bytes):
        return base64.b64encode(image_path).decode("utf-8")

    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def is_url(path: str) -> bool:
    url_pattern = re.compile(r"^[a-zA-Z][a-zA-Z\d+\-.]*://")
    return bool(url_pattern.match(path))


def contains_image(inputs: Any) -> bool:
    if isinstance(inputs, list):
        return any(isinstance(item, Image) for item in inputs)
    return isinstance(inputs, Image)


def inline_defs(schema):
    if "$defs" in schema:
        defs = schema.pop("$defs")
        for key, value in defs.items():
            ref_path = f"#/$defs/{key}"
            replace_refs(schema, ref_path, value)
    return schema


def replace_refs(obj, ref_path, definition):
    if isinstance(obj, dict):
        for key, value in list(obj.items()):
            if key == "$ref" and value == ref_path:
                obj.clear()
                obj.update(definition)
            else:
                replace_refs(value, ref_path, definition)
    elif isinstance(obj, list):
        for item in obj:
            replace_refs(item, ref_path, definition)
