from typing import List
from PIL import Image
import io
def center_bbox(bbox: List[int]) -> List[int]:
    """
    Calculate the center coordinates of a bounding box
    """
    return [(bbox[0] + bbox[2]) // 2, (bbox[1] + bbox[3]) // 2]


def screenshot_to_image(screenshot: bytes) -> Image:
    return Image.open(io.BytesIO(screenshot))
