import random
import cv2
import numpy as np


class ZDraw:
    def __init__(self, class_colors=None):
        """
        Initialize the ZDraw object.
        :param class_colors: Optional dictionary for class-to-color mapping.
        """
        self.class_colors = class_colors or {}
        self.shape_colors = {
            "line": (
                random.randint(0, 255),
                random.randint(0, 255),
                random.randint(0, 255),
            ),
            "triangle": (
                random.randint(0, 255),
                random.randint(0, 255),
                random.randint(0, 255),
            ),
            "rectangle": (
                random.randint(0, 255),
                random.randint(0, 255),
                random.randint(0, 255),
            ),
            "square": (
                random.randint(0, 255),
                random.randint(0, 255),
                random.randint(0, 255),
            ),
            "polygon": (
                random.randint(0, 255),
                random.randint(0, 255),
                random.randint(0, 255),
            ),
        }

    def get_color_for_class(self, class_name):
        """
        Get or assign a random color for the class.
        :param class_name: Name of the class.
        :return: RGB color tuple.
        """
        if class_name not in self.class_colors:
            self.class_colors[class_name] = (
                random.randint(0, 255),
                random.randint(0, 255),
                random.randint(0, 255),
            )
        return self.class_colors[class_name]

    def __draw_rec__(self, frame, top_left, bottom_right, border_color, fill_color):
        """
        Draw a rounded rectangle with dynamic corner radius and thickness.
        :param frame: The input image frame.
        :param top_left: Top-left corner (x1, y1).
        :param bottom_right: Bottom-right corner (x2, y2).
        :param border_color: Color of the border (BGR tuple).
        :param fill_color: Color of the fill (BGR tuple).
        :return: Modified frame.
        """
        x1, y1 = top_left
        x2, y2 = bottom_right
        box_width = x2 - x1
        box_height = y2 - y1

        # Dynamically adjust corner radius and thickness based on box size
        corner_radius = max(5, min(box_width, box_height) // 10)
        thickness = max(1, min(box_width, box_height) // 50)

        # Create a mask for the filled rectangle with rounded corners
        mask = np.zeros_like(frame, dtype=np.uint8)
        cv2.rectangle(mask, (x1 + corner_radius, y1), (x2 - corner_radius, y2), fill_color, -1)
        cv2.rectangle(mask, (x1, y1 + corner_radius), (x2, y2 - corner_radius), fill_color, -1)
        cv2.ellipse(mask, (x1 + corner_radius, y1 + corner_radius), (corner_radius, corner_radius), 180, 0, 90, fill_color, -1)
        cv2.ellipse(mask, (x2 - corner_radius, y1 + corner_radius), (corner_radius, corner_radius), 270, 0, 90, fill_color, -1)
        cv2.ellipse(mask, (x1 + corner_radius, y2 - corner_radius), (corner_radius, corner_radius), 90, 0, 90, fill_color, -1)
        cv2.ellipse(mask, (x2 - corner_radius, y2 - corner_radius), (corner_radius, corner_radius), 0, 0, 90, fill_color, -1)
        frame = cv2.addWeighted(frame, 1.0, mask, 0.2, 0)
        # Draw the rounded corner borders
        cv2.ellipse(frame, (x1 + corner_radius, y1 + corner_radius), (corner_radius, corner_radius), 180, 0, 90, border_color, thickness)
        cv2.ellipse(frame, (x2 - corner_radius, y1 + corner_radius), (corner_radius, corner_radius), 270, 0, 90, border_color, thickness)
        cv2.ellipse(frame, (x1 + corner_radius, y2 - corner_radius), (corner_radius, corner_radius), 90, 0, 90, border_color, thickness)
        cv2.ellipse(frame, (x2 - corner_radius, y2 - corner_radius), (corner_radius, corner_radius), 0, 0, 90, border_color, thickness)

        return frame

    def __draw_shape__(self, frame, points, shape=None, return_original_frame=False):
        """
        Draw a universal shape (line, triangle, rectangle, square, or polygon) based on points and shape type.
        :param frame: Input image frame.
        :param points: List of points defining the shape.
        :param shape: Optional shape name for double-checking ('line', 'triangle', etc.).
        :return: Frame with the drawn shape.
        """
        original_frame = frame.copy()
        num_points = len(points)
        # Determine the shape type based on points
        if num_points == 2:
            detected_shape = "line"
        elif num_points == 3:
            detected_shape = "triangle"
        elif num_points == 4:
            x_coords = [p[0] for p in points]
            y_coords = [p[1] for p in points]
            width = max(x_coords) - min(x_coords)
            height = max(y_coords) - min(y_coords)
            detected_shape = "square" if abs(width - height) <= 5 else "rectangle"
        else:
            detected_shape = "polygon"
        # Use the shape parameter to confirm or override detection
        if shape and shape != detected_shape:
            raise ValueError(f"Shape mismatch: detected '{detected_shape}', but provided '{shape}'")
        # Get color for the shape
        color = self.shape_colors.get(detected_shape, (255, 255, 255))
        # Draw the shape
        if detected_shape == "line":
            cv2.line(frame, points[0], points[1], color, thickness=2)
        elif detected_shape == "triangle":
            mask = np.zeros_like(frame, dtype=np.uint8)
            cv2.fillPoly(mask, [np.array(points)], color)
            frame = cv2.addWeighted(frame, 1.0, mask, 0.2, 0)
            cv2.polylines(frame, [np.array(points)], isClosed=True, color=color, thickness=2)
        elif detected_shape == "rectangle" or detected_shape == "square":
            frame = self.__draw_rec__(frame, points[0], points[2], color, color)
        else:  # Polygon
            mask = np.zeros_like(frame, dtype=np.uint8)
            cv2.fillPoly(mask, [np.array(points)], color)
            frame = cv2.addWeighted(frame, 1.0, mask, 0.2, 0)
            cv2.polylines(frame, [np.array(points)], isClosed=True, color=color, thickness=2)
        if return_original_frame:
            return original_frame, frame
        return frame    

    def ZDrawShape(self, frame, points, shape=None, return_original_frame=False):
        """
        Draw a universal shape (line, triangle, rectangle, square, or polygon) based on points and shape type.
        :param frame: Input image frame.
        :param points: List of points defining the shape.
        :param shape: Optional shape name for double-checking ('line', 'triangle', etc.).
        :return: Frame with the drawn shape.
        """
        return self.__draw_shape__(frame, points, shape, return_original_frame)

    def ZDrawRect(self, frame, x1, y1, x2, y2, class_name=None, color=None, return_original_frame=False):
        """
        Draw a custom bounding box with rounded corners and an optional label.
        :param frame: Input image frame.
        :param x1: Top-left x-coordinate of the bounding box.
        :param y1: Top-left y-coordinate of the bounding box.
        :param x2: Bottom-right x-coordinate of the bounding box.
        :param y2: Bottom-right y-coordinate of the bounding box.
        :param class_name: Optional class name for the label.
        :param color: Optional color (BGR). If None, a random color is assigned.
        :param return_original_frame: If True, return the original frame without the bounding box.
        :return: Tuple (original frame, frame with bounding box).
        """
        original_frame = frame.copy()
        frame_height, frame_width, _ = frame.shape
        # Dynamically adjust font size and thickness based on frame size
        font_scale = max(0.4, min(frame_width, frame_height) / 1000)
        font_thickness = max(1, int(min(frame_width, frame_height) / 300))
        # Assign color if not provided
        if color is None:
            color = (0, 255, 0) if class_name is None else self.get_color_for_class(class_name)
        # Draw the main bounding box with rounded corners
        frame = self.__draw_rec__(frame, (x1 - 2, y1 - 2), (x2 + 2, y2 + 2), color, color)
        # Draw the label if class_name is provided
        if class_name:
            label_size, _ = cv2.getTextSize(class_name, cv2.FONT_HERSHEY_SIMPLEX, font_scale, font_thickness)
            label_width, label_height = label_size
            label_y_offset = y1 - label_height - 10 if y1 - label_height - 10 > 0 else y1 + label_height + 10
            # Draw the solid background for the label
            cv2.rectangle(frame, (x1 - 1, label_y_offset - label_height - 2),
                          (x1 + label_width + 10, label_y_offset), color, -1)
            # Draw the class name on the label
            cv2.putText(frame, class_name, (x1 + 5, label_y_offset - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), font_thickness)
        if return_original_frame:
            return original_frame, frame
        return frame


