from PyQt6.QtCore import QByteArray, QBuffer, QIODevice
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor, QBrush, QLinearGradient, QFont

def create_app_icon():
    """Create a lock icon for the application"""
    pixmap = QPixmap(128, 128)
    pixmap.fill(QColor(0, 0, 0, 0))
    
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    
    # Create a gradient background
    gradient = QLinearGradient(0, 0, 0, 128)
    gradient.setColorAt(0, QColor("#4a86e8"))
    gradient.setColorAt(1, QColor("#2a66c8"))
    
    # Draw a rounded rectangle
    painter.setBrush(QBrush(gradient))
    painter.setPen(QColor(255, 255, 255, 30))
    painter.drawRoundedRect(14, 14, 100, 100, 20, 20)
    
    # Draw lock icon
    painter.setBrush(QBrush(QColor(255, 255, 255)))
    painter.setPen(QColor(255, 255, 255, 0))
    
    # Lock body
    painter.drawRoundedRect(34, 50, 60, 50, 5, 5)
    
    # Lock shackle
    painter.setPen(QColor(255, 255, 255))
    painter.drawRoundedRect(44, 30, 40, 40, 10, 10)
    painter.setBrush(QBrush(gradient))
    painter.drawRoundedRect(49, 35, 30, 30, 8, 8)
    
    # Draw a keyhole
    painter.setBrush(QBrush(gradient))
    painter.drawEllipse(59, 65, 10, 10)
    painter.drawRect(63, 75, 2, 10)
    
    painter.end()
    
    return QIcon(pixmap)

def get_app_icon():
    """Get the application icon"""
    return create_app_icon() 