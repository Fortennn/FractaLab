from PyQt5.QtWidgets import QDoubleSpinBox
from PyQt5 import QtCore


class CleanSpinBox(QDoubleSpinBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
    
    def textFromValue(self, value):
        if value == 0.0:
            return "0"
        
        text = super().textFromValue(value)
        
        if '.' in text:
            text = text.rstrip('0').rstrip('.')
        
        return text