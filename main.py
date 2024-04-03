import math
import sys
from typing import Dict, Tuple, List

from PyQt5.QtCore import QPointF
from PyQt5.QtGui import QPainter, QPolygonF, QFontMetrics
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QVBoxLayout


class Main:
    """Main class of the application. This class is responsible for starting the app."""

    def __init__(self):
        pass  # Constructor is empty as there is no need for any initialization

    @staticmethod
    def start_game():
        live_board = Board()
        live_board.setup_board()

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
        pass

    def setup(self):
        pass


class GameController:
    """GameController class is responsible for controlling the flow of the game."""

    def __init__(self):
        pass

    def start_game(self):
        pass

    def end_game(self):
        pass

    def pause_game(self):
        pass

    def resume_game(self):
        pass


class Hexagon:
    """Hexagon class is responsible for creating a single hexagon on the board. It has a position"""

    def __init__(self, q: int = 0, r: int = 0):
        self.q: int = q
        self.r: int = r
        self.cube_coordinates_q_r: Tuple[int, int] = (q, r)  # q,r coordinates


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
        self.size_x: int = 9
        self.size_y: int = 9

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
        print(f"Hexagon at {hex.cube_coordinates_q_r} has been deleted")

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


class BoardWidget(QWidget):
    def __init__(self, board: Board, parent=None):
        super().__init__(parent)

        self.board = board
        self.hex_radius = 30

        self.draw_coordinates = False

    def toggle_coordinates(self):
        self.draw_coordinates = not self.draw_coordinates
        self.update()  # Redraw the widget

    def paintEvent(self, event):
        """Paint the board with hexagons and their coordinates."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        for hex_coords, hexagon in self.board.hexes.items():
            self.draw_hex(painter, hexagon)
            if self.draw_coordinates is True:
                self.draw_coordiantes(painter, hexagon)

    def draw_hex(self, painter, hex: Hexagon):
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

    def get_offset_to_textcenter(self, painter: object, text: str) -> Tuple[int, int]:
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

        x_offset: int = self.hex_radius
        y_offset: int = self.hex_radius

        x: int = round(self.hex_radius * math.sqrt(3) * (hex.q + hex.r / 2) + x_offset)
        y: int = round(self.hex_radius * 3 / 2 * hex.r + y_offset)

        return (x, y)

    def calc_hex_corner_points(self, center_x_y: Tuple[int, int]) -> List:
        """Calculate the corner points of a hexagon based on its center coordinates and radius"""
        hex_points: list = []
        for i in range(6):
            angle_deg = 60 * i - 30
            angle_rad = math.pi / 180 * angle_deg
            x = center_x_y[0] + self.hex_radius * math.cos(angle_rad)
            y = center_x_y[1] + self.hex_radius * math.sin(angle_rad)
            hex_points.append(QPointF(x, y))
        return hex_points


Main.start_game()
