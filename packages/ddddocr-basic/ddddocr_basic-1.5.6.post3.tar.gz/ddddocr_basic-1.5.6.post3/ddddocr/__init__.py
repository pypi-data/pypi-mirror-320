import warnings

warnings.filterwarnings('ignore')
import io
import pathlib
from base64 import b64decode
from typing import Any

import numpy as np
import onnxruntime
from PIL import Image

from ._charset import CHARSET

onnxruntime.set_default_logger_severity(3)


def base64_to_image(img_base64: str):
    img_data = b64decode(img_base64)
    return Image.open(io.BytesIO(img_data))


class DdddOcr(object):
    def __init__(self):
        self.__graph_path = pathlib.Path(__file__).parent / "common_old.onnx"
        self.__ort_session = onnxruntime.InferenceSession(self.__graph_path)

    def classification(self, img: bytes | Image.Image | str | pathlib.PurePath):
        if isinstance(img, bytes):
            image = Image.open(io.BytesIO(img))
        elif isinstance(img, Image.Image):
            image = img.copy()
        elif isinstance(img, str):
            image = base64_to_image(img)
        else:
            image = Image.open(img)

        image = image.resize(
            (int(64 / image.size[1] * image.size[0]), 64), Image.Resampling.LANCZOS
        ).convert('L')
        image = np.array(image)
        image = np.expand_dims(image, 0) / 255
        image = (image - 0.5) / 0.5

        ort_outs: Any = self.__ort_session.run(0, {'input1': [image]})
        result: list[str] = []

        last_item = 0

        argmax_result: list[np.int64] = np.squeeze(np.argmax(ort_outs[0], 2))
        for item in argmax_result:
            if item is not last_item:
                last_item = item
            if item:
                result.append(CHARSET[item])
        return "".join(result)
