# ZRect

ZRect is a Python library for drawing custom bounding boxes with rounded corners on images using OpenCV. It supports dynamic adjustment of corner radius and border thickness, along with options for adding labels to the bounding boxes.

## Features

- Draws rounded rectangles on images.
- Dynamically adjusts corner radius and border thickness based on box dimensions.
- Add custom labels with solid background and rounded edges.
- Assign random colors to classes for better visualization.

## Installation


```bash
pip install zdraw
```


### Usage Example

```python
import cv2
from zdraw import ZDraw
# Initialize ZRect with an optional class color map
# Initialize ZRect
zdraw = ZDraw()

# Load an image
frame = cv2.imread("image.jpg")

# Define bounding box coordinates and class
x1, y1, x2, y2 = 100, 150, 400, 300
class_name = "DynamicObject"

# Draw bounding box with label
original_frame, modified_frame = zdraw.ZRectDraw(frame, x1, y1, x2, y2, class_name, return_original_frame=True)

# Display the result
cv2.imshow("Original Frame", original_frame)
cv2.imshow("Modified Frame", modified_frame)
cv2.waitKey(0)
cv2.destroyAllWindows()
```

## API Reference

`ZDraw`

`__init__(class_colors={})`

- Initializes the `ZDraw` object.
- Parameters:

    - `class_colors` (dict): A dictionary mapping class names to RGB tuples.

`get_color_for_class(class_name)`
- Returns a random color for a given class if not already assigned.

`__draw_rec__(frame, top_left, bottom_right, border_color, fill_color)`
- Draws a rounded rectangle on the frame, private.

`ZRectDraw(frame, x1, y1, x2, y2)`
- Draws a bounding box with rounded corners and a label.

### Dependencies
- Python 3.8 or higher
- OpenCV (opencv-python)
- NumPy

## License
This project is licensed under the MIT License. See the LICENSE file for details.