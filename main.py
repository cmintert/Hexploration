import math
import sys

from typing import Dict, Tuple, List

from PyQt6.QtCore import QPointF, Qt
from PyQt6.QtGui import (
    QPainter,
    QPolygonF,
    QFontMetrics,
    QPixmap,
    QWheelEvent,
    QMouseEvent,
    QColor,
)
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QVBoxLayout


class Main:
    """Main class of the application. This class is responsible for starting the app."""

    def __init__(self):
        pass  # Constructor is empty as there is no need for any initialization

    @staticmethod
    def start_game():
        live_board = Board()
        live_board.setup_board()

        live_board.change_hex(
            TerrainFactory().create_terrain_at(
                "forest",
                6,
                5,
            )
        )

        app = QApplication(sys.argv)
        window = MainWindow(live_board)
        window.show()
        app.exec()


class HexPositionError(Exception):
    """Raised when a hexagon already exists at a certain position"""

    pass


class Game:
    """Game class is responsible for starting up a new game."""

    def __init__(self):
        # Placeholder for structure
        pass

    def setup(self):
        # Placeholder for structure
        pass


class GameController:
    """GameController class is responsible for controlling the flow of the game."""

    def __init__(self):
        # Placeholder for structure
        pass

    def start_game(self):
        # Placeholder for structure
        pass

    def end_game(self):
        # Placeholder for structure
        pass

    def pause_game(self):
        # Placeholder for structure
        pass

    def resume_game(self):
        # Placeholder for structure
        pass


class Hexagon:
    """Hexagon class is responsible for creating a single hexagon on the board. It has a position"""

    def __init__(self, q: int = 0, r: int = 0):
        self.q: int = q
        self.r: int = r
        self.s: int = -q - r
        self.cube_coordinates_q_r: Tuple[int, int] = (q, r)  # q,r coordinates


class TerrainHex(Hexagon):
    def __init__(self, q: int = 0, r: int = 0):
        super().__init__(q, r)
        self.game_piece_type: str = "terrain"
        self.move_cost: int = 1

    def __str__(self):
        return f"{self.game_piece_type} at {self.q}, {self.r}"


class TerrainFactory:
    def __init__(self):
        # The factory has no need for attributes at this point
        pass

    def create_terrain_at(self, terrain_type: str, q: int, r: int) -> Hexagon:
        if terrain_type == "forest":
            return ForestHex(q, r)
        elif terrain_type == "mountain":
            return MountainHex(q, r)
        elif terrain_type == "water":
            return WaterHex(q, r)
        elif terrain_type == "plain":
            return PlainHex(q, r)
        else:
            raise ValueError("Invalid terrain type")


class ForestHex(TerrainHex):

    def __init__(self, q: int = 0, r: int = 0):
        super().__init__(q, r)
        self.type = "forest"
        self.graphic = "assets/forest.png"

    def __str__(self):
        return f"{self.type} at {self.q}, {self.r}"


class MountainHex(TerrainHex):
    def __init__(self, q: int = 0, r: int = 0):
        super().__init__(q, r)
        self.type: str = "mountain"
        self.graphic: str = "assets/mountain.png"

    def __str__(self):
        return f"{self.type} at {self.q}, {self.r}"


class WaterHex(TerrainHex):
    def __init__(self, q: int = 0, r: int = 0):
        super().__init__(q, r)
        self.type: str = "water"
        self.graphic: str = "assets/water.png"

    def __str__(self):
        return f"{self.type} at {self.q}, {self.r}"


class PlainHex(TerrainHex):
    def __init__(self, q: int = 0, r: int = 0):
        super().__init__(q, r)
        self.type: str = "plain"
        self.graphic: str = "assets/plain.png"

    def __str__(self):
        return f"{self.type} at {self.q}, {self.r}"


class Edge:
    """Edge class is responsible for creating an edge between two hexagons on the board."""

    def __init__(self):
        self.hex1: Hexagon = Hexagon()
        self.hex2: Hexagon = Hexagon()

    # Ensure that edge between Hex1/Hex2 is the same as Hex2/Hex1
    def __eq__(self, other):
        if isinstance(other, Edge):
            return (self.hex1 == other.hex1 and self.hex2 == other.hex2) or (
                self.hex1 == other.hex2 and self.hex2 == other.hex1
            )
        return False


class Board:
    """Board class is responsible for creating the game board and operating on it (*A and Dijkstra Algorythm).
    The board is made up of hexagons and edges between them."""

    def __init__(self):
        self.hexes: Dict[Tuple[int, int], Hexagon] = (
            {}
        )  # Dictionary with q,r coordinates as keys and hexes as values
        self.edges: List[Edge] = []
        self.size_x: int = 20
        self.size_y: int = 20

    def setup_board(self):
        for r in range(self.size_x):
            for q in range(self.size_y):
                new_hex = Hexagon(
                    q - math.floor(r / 2), r
                )  # Offset for odd rows see redblobgames.com/grids/hexagons
                self.add_hex(new_hex)

    def add_hex(self, hex: Hexagon):
        if self.is_hex_present(hex) is True:
            raise HexPositionError("add_hex: Hex already exists at this position")
        self.hexes[hex.cube_coordinates_q_r] = hex

    def delete_hex(self, hex: Hexagon):
        if self.is_hex_present(hex) is False:
            raise HexPositionError("delete_hex: No hex at this position")
        del self.hexes[hex.cube_coordinates_q_r]

    def change_hex(self, hex: Hexagon):
        if self.is_hex_present(hex) is True:
            self.delete_hex(hex)
        self.add_hex(hex)

    def is_hex_present(self, hex: Hexagon) -> bool:
        """Verify if there is only one hexagon at a certain position.
        Return True if there is no hexagon at the position."""
        if hex.cube_coordinates_q_r in self.hexes:
            return True
        else:
            return False


class MainWindow(QMainWindow):
    def __init__(self, board: Board):
        super().__init__()

        self.setWindowTitle("Hexagon Game")

        self.boardWidget = BoardWidget(board, self)
        self.setCentralWidget(self.boardWidget)

        self.button = QPushButton("Toggle Coordinates", self)
        self.button.clicked.connect(self.boardWidget.toggle_coordinates)
        self.button.move(10, 10)

        layout = QVBoxLayout()
        layout.addWidget(self.boardWidget)
        layout.addWidget(self.button)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        self.resize(
            self.boardWidget.calculate_board_size()[0],
            self.boardWidget.calculate_board_size()[1],
        )


class BoardWidget(QWidget):
    def __init__(self, board: Board, parent=None):
        super().__init__(parent)

        self.board = board
        self._hex_radius: int = 30

        self.MATH_SQRT3 = math.sqrt(3)
        self.MATH_PI_DIV_180 = math.pi / 180

        self.draw_coordinates: bool = False

        self.hex_coordinate_cache: dict = {}
        self.hex_corner_point_cache: dict = {}

        self.panning = False
        self.last_mouse_pos = None

    def get_mouse_position_in_board(self, event: QMouseEvent) -> Tuple[int, int]:
        """Get the current mouse position in the board's coordinate system."""
        return (event.position().x(), event.position().y())

    def mousePressEvent(self, event: QMouseEvent):
        if (
            event.button() == Qt.MouseButton.LeftButton
            and event.modifiers() == Qt.KeyboardModifier.AltModifier
            and self.rect().contains(event.pos())
        ):
            self.panning = True
            self.last_mouse_pos = event.pos()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.panning is True:

            delta = event.pos() - self.last_mouse_pos
            self.last_mouse_pos = event.pos()

            scaling_factor = 1  # Adjust this value to your liking
            scaled_delta_x = delta.x() * scaling_factor
            scaled_delta_y = delta.y() * scaling_factor

            new_x = round(self.x() + scaled_delta_x)
            new_y = round(self.y() + scaled_delta_y)

            self.move(new_x, new_y)
            self.update()
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.panning = False
            self.setCursor(Qt.CursorShape.ArrowCursor)
            event.accept()
        else:
            super().mouseReleaseEvent(event)

    def wheelEvent(self, event: QWheelEvent):
        """Zoom in or out based on the mouse wheel event. Zooming is based on recalculating the hex radius."""

        if event.angleDelta().y() > 0:
            self.zoom_in(event)
        else:
            self.zoom_out(event)

        event.accept()

    def zoom_in(self, event: QWheelEvent):

        original_board_size: Tuple[int, int] = self.calculate_board_size()
        zoom_step: int = 5
        new_radius: int = self._hex_radius + zoom_step

        new_radius = self.limit_zoom(new_radius)

        self.set_hex_radius(new_radius)

        self.zoom_movement(event, original_board_size)

        self.update()

    def zoom_out(self, event: QWheelEvent):

        original_board_size: Tuple[int, int] = self.calculate_board_size()
        zoom_step: int = 5
        new_radius: int = self._hex_radius - zoom_step

        new_radius = self.limit_zoom(new_radius)

        self.set_hex_radius(new_radius)

        self.zoom_movement(event, original_board_size)

        self.update()

    def limit_zoom(self, new_radius: int) -> int:
        min_radius: int = 30
        max_radius: int = 150

        if new_radius < min_radius:
            new_radius = min_radius
        elif new_radius > max_radius:
            new_radius = max_radius

        return new_radius

    def zoom_movement(
        self, event: QWheelEvent, original_board_size: Tuple[int, int] = None
    ):
        initial_area = original_board_size[0] * original_board_size[1]
        new_area = self.width() * self.height()

        # Square root because we scale both width and height
        scale_factor = (new_area / initial_area) ** 0.5

        scale_change = scale_factor - 1

        offset_x = round(-(event.position().x() * scale_change))
        offset_y = round(-(event.position().y() * scale_change))

        self.move(self.x() + offset_x, self.y() + offset_y)

    def update_board_size(self):

        new_size: Tuple[int, int] = self.calculate_board_size()
        self.resize(new_size[0], new_size[1])

    def get_hex_radius(self) -> int:
        return self._hex_radius

    def set_hex_radius(self, radius: int) -> None:

        if radius == self._hex_radius:
            return

        self.clear_caches()
        self._hex_radius = radius
        self.update_board_size()

    def clear_caches(self):
        """Clear the hex coordinate and hex corner point caches."""
        self.hex_coordinate_cache = {}
        self.hex_corner_point_cache = {}

    def toggle_coordinates(self):
        self.draw_coordinates = not self.draw_coordinates
        self.update()  # Redraw the widget

    def paintEvent(self, event):
        """Paint the board with hexagons and their coordinates."""

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        for hex_coords, hexagon in self.board.hexes.items():
            self.draw_hex_outline(painter, hexagon)

            self.draw_terrain(painter, hexagon)

            if self.draw_coordinates is True:
                self.draw_coordiantes(painter, hexagon)

    def draw_terrain(self, painter: QPainter, hexagon: Hexagon):
        """Draw the terrain of a hexagon on the board."""

        if hasattr(hexagon, "graphic"):

            image: QPixmap = QPixmap(hexagon.graphic)

            imageposition_x, imageposition_y = self.calc_hex_pixel_coordinates(hexagon)

            x_size: int = round(self._hex_radius * self.MATH_SQRT3)
            y_size: int = round(2.3 * self._hex_radius)

            painter.drawPixmap(
                imageposition_x - round(x_size / 2),
                imageposition_y - round(y_size / 2),
                x_size,
                y_size,
                image,
            )

    def draw_hex_outline(self, painter: QPainter, hex: Hexagon):
        """Draw a single hexagon on the board, based on its q,r coordinates and radius."""
        center_x_y: Tuple[int, int] = self.calc_hex_pixel_coordinates(hex)
        hex_points: List = self.calc_hex_corner_points(center_x_y)

        polygon = QPolygonF(hex_points)
        painter.drawPolygon(polygon)

    def draw_coordiantes(self, painter, hex: Hexagon):
        """Draw the q,r coordinates of a hexagon on the board in text form."""

        coordinate_text: str = f"{hex.q}, {hex.r}"
        center_x_y: Tuple[int, int] = self.calc_hex_pixel_coordinates(hex)

        # offset the coordinate_text to center on center_x_y of hex
        offset_x_y: Tuple[int, int] = self.get_offset_to_textcenter(
            painter, coordinate_text
        )

        painter.drawText(
            center_x_y[0] - offset_x_y[0],
            center_x_y[1] + offset_x_y[1],
            coordinate_text,
        )

    def get_offset_to_textcenter(self, painter: QPainter, text: str) -> Tuple[int, int]:
        """Calculate the bbox center of a given text for qt5 painter"""
        font_metrics: QFontMetrics = QFontMetrics(painter.font())

        text_width: int = font_metrics.horizontalAdvance(text)
        text_height: int = font_metrics.height()

        # Adjust the x and y coordinates
        x_offset: int = round(text_width / 2)
        # We use 1/4 instead of 1/2 to better center the text vertically
        y_offset: int = round(text_height / 4)

        return (x_offset, y_offset)

    def calc_hex_pixel_coordinates(self, hex: Hexagon) -> Tuple[int, int]:
        """Calculate the pixel coordinates of a hexagon on the board based on its q,r
        coordinates and its radius. It starts in upper left corner of drawing area, therefore
        we need to add an offset to capture the whole hex inside the widget area."""

        if hex in self.hex_coordinate_cache:
            return self.hex_coordinate_cache[hex]

        x_offset: int = self._hex_radius
        y_offset: int = self._hex_radius

        x: int = round(
            self._hex_radius * self.MATH_SQRT3 * (hex.q + hex.r / 2) + x_offset
        )
        y: int = round(self._hex_radius * 3 / 2 * hex.r + y_offset)

        self.hex_coordinate_cache[hex] = (x, y)

        return (x, y)

    def calc_hex_corner_points(self, center_x_y: Tuple[int, int]) -> List:
        """Calculate the corner points of a hexagon based on its center coordinates and radius"""

        if center_x_y in self.hex_corner_point_cache:
            return self.hex_corner_point_cache[center_x_y]

        hex_points: list = []
        for i in range(6):
            angle_deg = 60 * i - 30
            angle_rad = self.MATH_PI_DIV_180 * angle_deg
            x = center_x_y[0] + self.get_hex_radius() * math.cos(angle_rad)
            y = center_x_y[1] + self.get_hex_radius() * math.sin(angle_rad)
            hex_points.append(QPointF(x, y))

        self.hex_corner_point_cache[center_x_y] = hex_points

        return hex_points

    def calculate_board_size(self) -> Tuple[int, int]:
        """Calculate the size of the board based on the hexagons. Return the width and height of the board
        as a tuple (x,y)."""

        size_x: int = self.board.size_x
        size_y: int = self.board.size_y

        board_width: int = math.ceil(size_x * self.get_hex_radius() * self.MATH_SQRT3)
        board_height: int = math.ceil(size_y * self.get_hex_radius() * 1.5)

        window_width: int = board_width + self.get_hex_radius() * 2
        window_height: int = board_height + self.get_hex_radius() * 2

        return (window_width, window_height)


Main.start_game()
