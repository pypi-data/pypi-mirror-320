#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This script is a PyQt5 GUI for picking seismic traveltimes.
Copyright (C) 2024, 2025 Sylvain Pasquet
Email: sylvain.pasquet@sorbonne-universite.fr

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

# Import libraries
import sys, os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QSplitter, QSizePolicy,
    QFileDialog, QInputDialog, QAction, QLabel, QListWidget, QComboBox, QStatusBar,
    QPushButton, QDialog, QHBoxLayout, QVBoxLayout, QLineEdit
)
# from PyQt5.QtGui import QPen, QColor
from PyQt5.QtCore import QLocale
import pyqtgraph as pqg
from pyqtgraph.Qt import QtCore
import numpy as np
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt
import obspy
import re

# Obspy functions
def read_seismic_file(seismic_file, separate_sources=False):
    '''
    Read a seismic file and return a list of streams, one for each source.

    Parameters
    ----------
    seismic_file : str
        The path to the seismic file.
    separate_sources : bool, optional
        If True, separate the traces into different streams based on the original_field_record_number.
        Default is False.
        
    Returns
    -------
    stream : obspy.Stream
        The stream object containing the seismic data.
    '''
    # Read the seismic file
    stream = obspy.read(seismic_file,unpack_trace_headers=True)

    input_format = check_format(stream)

    if input_format == 'seg2':
        input_format = 'segy'
        file_base_name, _ = os.path.splitext(seismic_file)
        try: # Try to convert file_base_name to an integer
            ffid = int(file_base_name)
        except ValueError:
            ffid = 1
        stream.write('tmp.sgy',format='SEGY',data_encoding=5, byteorder='>')
        stream = obspy.read('tmp.sgy',unpack_trace_headers=True)
        os.remove('tmp.sgy')
        for trace_index, trace in enumerate(stream):
            trace.stats[input_format].trace_header.trace_sequence_number_within_line = trace_index+1 #tracl
            trace.stats[input_format].trace_header.trace_sequence_number_within_segy_file = trace_index+1 #tracr
            trace.stats[input_format].trace_header.original_field_record_number = ffid #fldr
            trace.stats[input_format].trace_header.trace_number_within_the_original_field_record = trace_index+1 #tracf
    
    if separate_sources:
        stream = separate_streams(stream)

    return stream

def check_format(stream):
    '''
    Check the input format of the stream.
    
    Parameters
    ----------
    stream : obspy.Stream
        The stream object containing the seismic data.
        
    Returns
    -------
    input_format : str
        The input format of the stream.
    '''

    if hasattr(stream[0].stats, 'su'):
        input_format = 'su'
    elif hasattr(stream[0].stats, 'segy'):
        input_format = 'segy'
    elif hasattr(stream[0].stats, 'seg2'):
        input_format = 'seg2'
    else:
        raise ValueError('The input format is not recognized')
    
    return input_format

def separate_streams(stream):
    '''
    Separate the traces into different streams based on the original_field_record_number.

    Parameters
    ----------
    stream : obspy.Stream
        The stream object containing the seismic data.

    Returns
    -------
    streams : list
        A list of streams, one for each source.
    '''
    
    # Check the input format
    input_format = check_format(stream)
        
    # Get the unique original_field_record_number values
    unique_record_numbers = sorted(list(set(trace.stats[input_format].trace_header.original_field_record_number for trace in stream)))
    
    # Initialize an empty list to store the shot gathers in different streams
    streams = []
    
    # Iterate over the unique record numbers
    for record_number in unique_record_numbers:
        # Select the traces with the current record number and add them to the list
        substream = obspy.Stream([trace for trace in stream if trace.stats[input_format].trace_header.original_field_record_number == record_number])
        streams.append(substream)
    
    return streams

# Custom classes
class CustomViewBox(pqg.ViewBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def mouseDragEvent(self, ev, axis=None):
        if ev.button() == pqg.QtCore.Qt.LeftButton:
            self.setMouseMode(self.PanMode)  # Switch to pan mode
            ev.accept()  # Accept the event to handle it
            super().mouseDragEvent(ev, axis)
        elif ev.button() == pqg.QtCore.Qt.MiddleButton:
            self.setMouseMode(self.RectMode)
            super().mouseDragEvent(ev, axis)
        else:
            super().mouseDragEvent(ev, axis)

# Error Parameters Dialog
class ErrorParametersDialog(QDialog):
    def __init__(self, relativeError, absoluteError, maxRelativeError, minAbsoluteError, maxAbsoluteError, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Set Error Parameters")

        # Create layout
        layout = QVBoxLayout(self)

        # Create input fields
        self.relativeErrorLineEdit = self.createLineEdit(relativeError)
        self.absoluteErrorLineEdit = self.createLineEdit(absoluteError)
        self.maxRelativeErrorLineEdit = self.createLineEdit(maxRelativeError)
        self.minAbsoluteErrorLineEdit = self.createLineEdit(minAbsoluteError)
        self.maxAbsoluteErrorLineEdit = self.createLineEdit(maxAbsoluteError)

        # Add input fields to layout
        layout.addLayout(self.createFormItem("Relative Error:", self.relativeErrorLineEdit))
        layout.addLayout(self.createFormItem("Absolute Error:", self.absoluteErrorLineEdit))
        layout.addLayout(self.createFormItem("Max Relative Error:", self.maxRelativeErrorLineEdit))
        layout.addLayout(self.createFormItem("Min Absolute Error:", self.minAbsoluteErrorLineEdit))
        layout.addLayout(self.createFormItem("Max Absolute Error:", self.maxAbsoluteErrorLineEdit))

        # Add OK and Cancel buttons
        buttonLayout = QHBoxLayout()
        okButton = QPushButton("OK")
        cancelButton = QPushButton("Cancel")
        buttonLayout.addWidget(okButton)
        buttonLayout.addWidget(cancelButton)
        layout.addLayout(buttonLayout)

        # Connect buttons
        okButton.clicked.connect(self.accept)
        cancelButton.clicked.connect(self.reject)

    def createLineEdit(self, value):
        lineEdit = QLineEdit()
        if value is not None:
            lineEdit.setText(str(value))
        return lineEdit

    def createFormItem(self, label, widget):
        layout = QHBoxLayout()
        layout.addWidget(QLabel(label))
        layout.addWidget(widget)
        return layout

    @property
    def relativeError(self):
        text = self.relativeErrorLineEdit.text()
        return float(text) if text else None

    @property
    def absoluteError(self):
        text = self.absoluteErrorLineEdit.text()
        return float(text) if text else None

    @property
    def maxRelativeError(self):
        text = self.maxRelativeErrorLineEdit.text()
        return float(text) if text else None

    @property
    def minAbsoluteError(self):
        text = self.minAbsoluteErrorLineEdit.text()
        return float(text) if text else None

    @property
    def maxAbsoluteError(self):
        text = self.maxAbsoluteErrorLineEdit.text()
        return float(text) if text else None
    
class AssistedPickingParametersDialog(QDialog):
    def __init__(self, smoothing_window_size, deviation_threshold, 
                 picking_window_size, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Assisted Picking Parameters")

        # Create layout
        layout = QVBoxLayout(self)

        # Create input fields
        self.smoothingWindowSizeLineEdit = self.createLineEdit(smoothing_window_size)
        self.secondDerivativePercentileLineEdit = self.createLineEdit(deviation_threshold)
        self.inflectionWindowSizeLineEdit = self.createLineEdit(picking_window_size)

        # Add input fields to layout
        layout.addLayout(self.createFormItem("Smoothing Window Size:", self.smoothingWindowSizeLineEdit))
        layout.addLayout(self.createFormItem("Second Derivative Percentile:", self.secondDerivativePercentileLineEdit))
        layout.addLayout(self.createFormItem("Inflection Window Size:", self.inflectionWindowSizeLineEdit))

        # Add OK and Cancel buttons
        buttonLayout = QHBoxLayout()
        okButton = QPushButton("OK")
        cancelButton = QPushButton("Cancel")
        buttonLayout.addWidget(okButton)
        buttonLayout.addWidget(cancelButton)
        layout.addLayout(buttonLayout)

        # Connect buttons
        okButton.clicked.connect(self.accept)
        cancelButton.clicked.connect(self.reject)

    def createLineEdit(self, value):
        lineEdit = QLineEdit()
        if value is not None:
            lineEdit.setText(str(value))
        return lineEdit

    def createFormItem(self, label, widget):
        layout = QHBoxLayout()
        layout.addWidget(QLabel(label))
        layout.addWidget(widget)
        return layout

    @property
    def smoothing_window_size(self):
        text = self.smoothingWindowSizeLineEdit.text()
        return int(text) if text else None

    @property
    def deviation_threshold(self):
        text = self.secondDerivativePercentileLineEdit.text()
        return int(text) if text else None
    
    @property
    def picking_window_size(self):
        text = self.inflectionWindowSizeLineEdit.text()
        return int(text) if text else None
    
class TopoParametersDialog(QDialog):
    # Dialog for setting topography parameters
    # x column, z column, delimiter, skiprows
    def __init__(self, column_x, column_z, delimiter, skiprows, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Topography Parameters")

        # Create layout
        layout = QVBoxLayout(self)

        # Create input fields
        self.xColumnLineEdit = self.createLineEdit(column_x)
        self.zColumnLineEdit = self.createLineEdit(column_z)
        if delimiter == '\t':
            delimiter_display = "'\\t'"
        else:
            delimiter_display = f"'{delimiter}'"
        self.delimiterLineEdit = self.createLineEdit(delimiter_display)
        self.skiprowsLineEdit = self.createLineEdit(skiprows)

        # Add input fields to layout
        layout.addLayout(self.createFormItem("Column for x coord.:", self.xColumnLineEdit))
        layout.addLayout(self.createFormItem("Column for z coord.:", self.zColumnLineEdit))
        layout.addLayout(self.createFormItem("Delimiter (between quotes):", self.delimiterLineEdit))
        layout.addLayout(self.createFormItem("Skip rows:", self.skiprowsLineEdit))

        # Add OK and Cancel buttons
        buttonLayout = QHBoxLayout()
        okButton = QPushButton("OK")
        cancelButton = QPushButton("Cancel")
        buttonLayout.addWidget(okButton)
        buttonLayout.addWidget(cancelButton)
        layout.addLayout(buttonLayout)

        # Connect buttons
        okButton.clicked.connect(self.accept)
        cancelButton.clicked.connect(self.reject)

    def createLineEdit(self, value):
        lineEdit = QLineEdit()
        if value is not None:
            lineEdit.setText(str(value))
        return lineEdit
    
    def createFormItem(self, label, widget):
        layout = QHBoxLayout()
        layout.addWidget(QLabel(label))
        layout.addWidget(widget)
        return layout
    
    @property
    def column_x(self):
        text = self.xColumnLineEdit.text()
        return int(text) if text else None
    
    @property
    def column_z(self):
        text = self.zColumnLineEdit.text()
        return int(text) if text else None
    
    @property
    def delimiter(self):
        text = self.delimiterLineEdit.text()
        if text == "'\\t'":
            return '\t'
        return text.strip("'")
    
    @property
    def skiprows(self):
        text = self.skiprowsLineEdit.text()
        return int(text) if text else None
    
    
class HeaderDialog(QDialog):
    def __init__(self, headers, header_values, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Header Fields")
        self.setGeometry(100, 100, 300, 200)
        
        layout = QVBoxLayout(self)
        
        self.label = QLabel("Select a header field:")
        layout.addWidget(self.label)
        
        self.comboBox = QComboBox()
        self.comboBox.addItems(headers)
        self.comboBox.currentIndexChanged.connect(self.updateValue)
        layout.addWidget(self.comboBox)
        
        self.valueLabel = QLabel("Value: ")
        layout.addWidget(self.valueLabel)
        
        self.okButton = QPushButton("OK")
        self.okButton.clicked.connect(self.accept)
        layout.addWidget(self.okButton)
        
        self.header_values = header_values
        self.updateValue(0)  # Initialize with the first header value

    def updateValue(self, index):
        display_name = self.comboBox.itemText(index)
        values = self.header_values.get(display_name, {}).get('values', ["N/A"])
        unique_values = ", ".join(map(str, values))
        self.valueLabel.setText(f"Value: {unique_values}")

# Main window class
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Initialize attributes
        self.initializeAttributes()

        centralWidget = QWidget()
        mainLayout = QHBoxLayout(centralWidget)  # Main horizontal layout
        self.setCentralWidget(centralWidget)

        # Create a horizontal QSplitter
        horSplitter = QSplitter(QtCore.Qt.Horizontal)

        # Create a vertical layout for the left side
        leftLayout = QVBoxLayout()

        # Create a QComboBox to select the display option
        self.displayOptionComboBox = QComboBox()
        self.displayOptionComboBox.addItems(["Filename", "Source Position", "FFID"])
        self.displayOptionComboBox.currentIndexChanged.connect(self.updateFileListDisplay)
        self.displayOptionComboBox.setMinimumSize(50, 30)  # Set minimum size for the QComboBox
        leftLayout.addWidget(self.displayOptionComboBox)

        # Create a QListWidget for file names and add it to the left
        self.fileListWidget = QListWidget()
        self.fileListWidget.itemSelectionChanged.connect(self.onFileSelectionChanged)
        self.fileListWidget.setMinimumSize(50, 200)  # Set minimum size for the QListWidget
        self.fileListWidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # Ensure it expands to fill space
        leftLayout.addWidget(self.fileListWidget)

        # Create a QWidget to hold the left layout and add it to the horizontal splitter
        leftWidget = QWidget()
        leftWidget.setLayout(leftLayout)
        horSplitter.addWidget(leftWidget)

        # Create a vertical QSplitter
        vertSplitter = QSplitter(QtCore.Qt.Vertical)

        # Create a top ViewBox for seismograms
        self.viewBox = CustomViewBox()
        self.viewBox.setBackgroundColor('w')
        self.viewBox.invertY(True)  # Invert the y-axis

        # Create a plot widget with the top ViewBox
        self.plotWidget = pqg.PlotWidget(viewBox=self.viewBox)
        self.plotWidget.setBackground('w')  # Set background color to white
        vertSplitter.addWidget(self.plotWidget)

        # Create the bottom ViewBox for the acquisition setup / traveltimes view
        self.bottomViewBox = CustomViewBox()
        self.bottomViewBox.setBackgroundColor('w')

        # Create a plot widget with the bottom ViewBox
        self.bottomPlotWidget = pqg.PlotWidget(viewBox=self.bottomViewBox)
        self.bottomPlotWidget.setBackground('w')  # Set background color to white
        vertSplitter.addWidget(self.bottomPlotWidget)

        # Set initial sizes for the splitters
        horSplitter.setSizes([25, 100])
        vertSplitter.setSizes([300, 300])

        # Add the vertical splitter to the horizontal splitter
        horSplitter.addWidget(vertSplitter)

        # Add the horizontal splitter to the main layout
        mainLayout.addWidget(horSplitter)

        # Resize the window to almost full screen
        screen = QApplication.primaryScreen()
        screen_size = screen.size()
        self.resize(int(screen_size.width() * 0.9), int(screen_size.height() * 0.9))  # Resize to 90% of the screen size

        # Alternatively, you can use the following line to maximize the window
        # self.showMaximized()

        # Set the title of the window
        self.statusBar = QStatusBar(self)
        permanentMessage = QLabel(self.statusBar)
        permanentMessage.setText('S. Pasquet - 2024, 2025')
        self.statusBar.addPermanentWidget(permanentMessage)
        self.setStatusBar(self.statusBar)      

        # Connect the mouseClickEvent signal to the pickTime slot
        self.plotWidget.scene().sigMouseClicked.connect(self.pickTime)

        # Add a QLabel to the MainWindow
        self.label = QLabel(self)

        # Create a menu bar and add a File menu
        self.fileMenu = self.menuBar().addMenu('File')

        self.openFileAction = QAction('Open file(s)', self)
        self.fileMenu.addAction(self.openFileAction)
        self.openFileAction.triggered.connect(self.openFile)

        self.clearMemoryAction = QAction('Clear Memory', self)
        self.fileMenu.addAction(self.clearMemoryAction)
        self.clearMemoryAction.triggered.connect(self.clearMemory)

        # Create a menu bar and add Header menu
        self.headerMenu = self.menuBar().addMenu('Headers')

        self.showHeadersAction = QAction('Show Headers', self)
        self.headerMenu.addAction(self.showHeadersAction)
        self.showHeadersAction.triggered.connect(self.showHeaders)

        # Create a menu bar and add a View menu
        self.viewMenu = self.menuBar().addMenu('View')

        # Create a submenu for x-axis plot types
        self.plotTypeSubMenu = self.viewMenu.addMenu('Plot traces by')

        self.shotTraceNumberAction = QAction("Number", self)
        self.plotTypeSubMenu.addAction(self.shotTraceNumberAction)
        self.shotTraceNumberAction.triggered.connect(self.setShotTraceNumber)

        self.tracePositionAction = QAction("Position", self)
        self.plotTypeSubMenu.addAction(self.tracePositionAction)
        self.tracePositionAction.triggered.connect(self.setTracePosition)

        # Redundant with trace position now that files with multiple streams are separated
        # self.fileTraceNumberAction = QAction("File Trace Number", self)
        # self.plotTypeSubMenu.addAction(self.fileTraceNumberAction)
        # self.fileTraceNumberAction.triggered.connect(self.setFileTraceNumber)

        # Create a submenu for y-axis plot types
        self.plotTypeSubMenu = self.viewMenu.addMenu('Plot sources by')

        self.ffidAction = QAction("FFID", self)
        self.plotTypeSubMenu.addAction(self.ffidAction)
        self.ffidAction.triggered.connect(self.setFFID)

        self.sourcePositionAction = QAction("Position", self)
        self.plotTypeSubMenu.addAction(self.sourcePositionAction)
        self.sourcePositionAction.triggered.connect(self.setSourcePosition)

        self.offsetAction = QAction("Offset", self)
        self.plotTypeSubMenu.addAction(self.offsetAction)
        self.offsetAction.triggered.connect(self.setOffset)

        # Create Menu for choosing bottom plot type
        self.bottomPlotSubMenu = self.viewMenu.addMenu('Bottom Plot Type')

        self.bottomPlotSetupAction = QAction('Source / Trace', self)
        self.bottomPlotSubMenu.addAction(self.bottomPlotSetupAction)
        self.bottomPlotSetupAction.triggered.connect(self.setPlotSetup)

        self.bottomPlotTravelTimeAction = QAction('Traveltimes', self)
        self.bottomPlotSubMenu.addAction(self.bottomPlotTravelTimeAction)
        self.bottomPlotTravelTimeAction.triggered.connect(self.setPlotTravelTime)

        self.bottomPlotTopographyAction = QAction('Topography', self)
        self.bottomPlotSubMenu.addAction(self.bottomPlotTopographyAction)
        self.bottomPlotTopographyAction.triggered.connect(self.setPlotTopo)

        # Create QAction for resetting the view
        self.resetViewAction = QAction("Reset View", self)
        self.viewMenu.addAction(self.resetViewAction)
        self.resetViewAction.triggered.connect(self.resetSeismoView)
        self.resetViewAction.triggered.connect(self.resetBottomView)

        # Create a menu bar and add a Seismogram menu
        self.seismoMenu = self.menuBar().addMenu('Seismogram')

        # Create a submenu for wiggle plot options
        self.plotWiggleSubMenu = self.seismoMenu.addMenu('Amplitude Fill')

        self.fillPositiveAction = QAction("Fill positive amplitudes", self)
        self.plotWiggleSubMenu.addAction(self.fillPositiveAction)
        self.fillPositiveAction.triggered.connect(self.fillPositive)

        self.fillNegativeAction = QAction("Fill negative amplitudes", self)
        self.plotWiggleSubMenu.addAction(self.fillNegativeAction)
        self.fillNegativeAction.triggered.connect(self.fillNegative)

        self.noFillAction = QAction("No fill", self)
        self.plotWiggleSubMenu.addAction(self.noFillAction)
        self.noFillAction.triggered.connect(self.noFill)

        # Create a QAction for normalizing the traces
        self.normalizeAction = QAction("Normalize traces", self)
        self.seismoMenu.addAction(self.normalizeAction)
        self.normalizeAction.setCheckable(True)
        self.normalizeAction.setChecked(self.normalize)
        self.normalizeAction.triggered.connect((self.toggleNormalize))

        # Create a QAction for clipping the traces
        self.clipAction = QAction("Clip traces", self)
        self.seismoMenu.addAction(self.clipAction)
        self.clipAction.setCheckable(True)
        self.clipAction.setChecked(self.clip)
        self.clipAction.triggered.connect((self.toggleClip))

        # Create a QAction for showing time samples
        self.showTimeSamplesAction = QAction("Show time samples", self)
        self.seismoMenu.addAction(self.showTimeSamplesAction)
        self.showTimeSamplesAction.setCheckable(True)
        self.showTimeSamplesAction.setChecked(self.show_time_samples)
        self.showTimeSamplesAction.triggered.connect(self.toggleShowTimeSamples)

        # Create a QAction for showing the air wave
        self.showAirWaveAction = QAction("Show air wave", self)
        self.seismoMenu.addAction(self.showAirWaveAction)
        self.showAirWaveAction.setCheckable(True)
        self.showAirWaveAction.setChecked(self.show_air_wave)
        self.showAirWaveAction.triggered.connect(self.toggleShowAirWave)

        # Create a QAction for setting the gain
        self.setGainAction = QAction("Set Gain", self)
        self.seismoMenu.addAction(self.setGainAction)
        self.setGainAction.triggered.connect(self.setGain)

        # Create a QAction for setting the maximum time 
        self.setMaxTimeAction = QAction("Set Maximum Time", self)
        self.seismoMenu.addAction(self.setMaxTimeAction)
        self.setMaxTimeAction.triggered.connect(self.setMaxTime)

        # Create a menu bar and add a Topography menu
        self.topographyMenu = self.menuBar().addMenu('Topography')

        self.importTopoAction = QAction('Import Topography', self)
        self.topographyMenu.addAction(self.importTopoAction)
        self.importTopoAction.triggered.connect(self.importTopo)

        self.setTopoParametersAction = QAction('Set Topography Parameters', self)
        self.topographyMenu.addAction(self.setTopoParametersAction)
        self.setTopoParametersAction.triggered.connect(self.setTopoParameters)

        # Create a menu bar and add a Picks menu
        self.picksMenu = self.menuBar().addMenu('Picks')

        self.savePicksAction = QAction('Save Picks', self)
        self.picksMenu.addAction(self.savePicksAction)
        self.savePicksAction.triggered.connect(self.savePicks)

        self.loadPicksAction = QAction('Load Picks', self)
        self.picksMenu.addAction(self.loadPicksAction)
        self.loadPicksAction.triggered.connect(self.loadPicks)

        self.clearPicksMenu = self.picksMenu.addMenu('Clear Picks')

        self.clearAllPicksAction = QAction('Clear All Picks', self)
        self.clearPicksMenu.addAction(self.clearAllPicksAction)
        self.clearAllPicksAction.triggered.connect(self.clearAllPicks)

        self.clearCurrentPicksAction = QAction('Clear Current Picks', self)
        self.clearPicksMenu.addAction(self.clearCurrentPicksAction)
        self.clearCurrentPicksAction.triggered.connect(self.clearCurrentPicks)

        self.errorPicksMenu = self.picksMenu.addMenu('Error Parameters')

        self.setErrorParametersAction = QAction('Set Error Parameters', self)
        self.errorPicksMenu.addAction(self.setErrorParametersAction)
        self.setErrorParametersAction.triggered.connect(self.setErrorParameters)

        self.setAllPickErrorAction = QAction('Set Errors For All Picks', self)
        self.errorPicksMenu.addAction(self.setAllPickErrorAction)
        self.setAllPickErrorAction.triggered.connect(self.setAllPickError)

        self.assistedPickingMenu = self.picksMenu.addMenu('Assisted Picking (experimental)')

        # Create a QAction for showing time samples
        self.assistedPickingAction = QAction("Assisted Picking", self)
        self.assistedPickingMenu.addAction(self.assistedPickingAction)
        self.assistedPickingAction.setCheckable(True)
        self.assistedPickingAction.setChecked(self.assisted_picking)
        self.assistedPickingAction.triggered.connect(self.toggleAssistedPicking)

        # Create a QAction for setting assisted picking parameters
        self.setAssistedPickingParametersAction = QAction("Assisted Picking Parameters", self)
        self.assistedPickingMenu.addAction(self.setAssistedPickingParametersAction)
        self.setAssistedPickingParametersAction.triggered.connect(self.setAssistedPickingParameters)

        # Create a Menu bar for exporting figures
        self.exportMenu = self.menuBar().addMenu('Export')

        self.exportSeismoAction = QAction('Export Seismogram', self)
        self.exportMenu.addAction(self.exportSeismoAction)
        self.exportSeismoAction.triggered.connect(self.exportSeismoPlot)

        # Initialize the variables
        self.clearMemory()

        # Update the file list display initially
        self.updateFileListDisplay()  
    
    def initializeAttributes(self):

        # Initialize single attributes
        self.currentFileName = None
        self.currentIndex = None
        self.streamIndex = None
        self.stream = None
        self.normalize = True
        self.polarity = 'negative'
        self.clip = True
        self.show_time_samples = False
        self.show_air_wave = False
        self.assisted_picking = True
        self.smoothing_window_size = 5  
        self.deviation_threshold = 15  
        self.picking_window_size = 20 
        self.column_x = 0
        self.column_z = 1
        self.delimiter = '\t'
        self.skiprows = 0
        self.gain = 1
        self.mean_dg = 1
        self.mean_ds = 1
        self.display_option = "Filename"
        self.bottomPlotType = 'setup'
        self.max_auto_load_files = 1000
        self.max_time = 0.05
        self.col = 'k'
        self.plotTypeX = 'trace_position'
        self.plotTypeY = 'source_position'
        self.x_label = 'Trace Position (m)'
        self.y_label = 'Source Position (m)'
        self.t_label = 'Time (s)'
        self.relativeError = 0.05
        self.absoluteError = 0
        self.maxRelativeError = None
        self.minAbsoluteError = None
        self.maxAbsoluteError = None

    def clearMemory(self):

        self.initializeAttributes()

        # Clear the plot widgets
        self.plotWidget.clear()
        self.plotWidget.autoRange()
        self.viewBox.setLimits(xMin=None, xMax=None, yMin=None, yMax=None)
        self.bottomPlotWidget.clear()
        self.bottomPlotWidget.autoRange()
        self.bottomViewBox.setLimits(xMin=None, xMax=None, yMin=None, yMax=None)
        self.fileListWidget.clear()

        # Initialize the lists for each stream
        self.attributes_to_initialize = [
            'fileNames', 'streams', 'input_format', 'n_sample', 
            'sample_interval', 'delay', 'time', 'record_length','ffid',  
            'source_position', 'shot_trace_number', 'trace_position', 
            'file_trace_number', 'trace_elevation', 'source_elevation',
            'offset', 'picks', 'error', 'pickSeismoItems', 'pickSetupItems', 'airWaveItems'
        ]

        # Initialize the lists for each stream
        for attr in self.attributes_to_initialize:
            setattr(self, attr, [])

        # Setup the dictionary
        self.plotTypeDict = {
            'shot_trace_number': self.shot_trace_number,
            'file_trace_number': self.file_trace_number,
            'trace_position': self.trace_position,
            'source_position': self.source_position,
            'ffid': self.ffid,  
            'offset': self.offset
        }

    def updatePlotTypeDict(self):
        # Update the dictionary mapping plot types to attributes
        self.plotTypeDict = {
            'shot_trace_number': self.shot_trace_number,
            'file_trace_number': self.file_trace_number,
            'trace_position': self.trace_position,
            'source_position': self.source_position,
            'ffid': self.ffid,
            'offset': self.offset
        }

    def openFile(self, fileNames_new=None):
        if fileNames_new is None or not fileNames_new:
            fileNames_new, _ = QFileDialog.getOpenFileNames(self, "Open seismic file(s)", "", 
                                                        "Seismic files (*.seg2 *.dat *.segy *.sgy *.sg2 *.su)")
            
        firstNewFile = None
        counter_files = 0
        if fileNames_new:
            fileNames_new.sort(key=lambda x: self.extractFileNumber(os.path.basename(x)))  # Sort the new file paths by filename

            # Check if files are already in the list
            for i, fileName in enumerate(fileNames_new):
                if not fileName in self.fileNames:
                    counter_files += 1
                    
                    self.currentFileName = fileName
                    self.loadFile() # Load the file
                    
                    counter_stream = 0
                    for j in range(len(self.stream)):
                        if len(self.stream) > 1:
                            fileName = fileNames_new[i] + f'_{j+1}'
                        
                        if not fileName in self.fileNames:
                            counter_stream += 1
                            if firstNewFile is None: # Get the first new file
                                firstNewFile = fileName

                            self.currentIndex = len(self.fileNames) # Set the current index to the length of the file names list
                            self.currentFileName = fileName 
                            self.streamIndex = j

                            # Create attributes_to_append_none by excluding 'fileNames' and 'airWaveItems'
                            attributes_to_append_none = [attr for attr in self.attributes_to_initialize if attr not in ['fileNames', 'airWaveItems']]

                            for attr in attributes_to_append_none:
                                getattr(self, attr).append(None)

                            self.fileNames.append(fileName)  # Append the file name to the list
                            self.airWaveItems.append([None,None,None])  # Append the air wave items to the list

                            self.loadStream() # Load the file

                    if i == 0:
                        if self.max_time is None:
                            self.max_time = max(self.time[0])

                    if counter_stream > 0:           
                        self.currentFileName = firstNewFile
                        self.currentIndex = self.fileNames.index(firstNewFile)

            if counter_stream > 0:
                if counter_stream > 1:
                    print(f'{counter_files} file(s) succesfully loaded')
                    print(f'{counter_stream} streams succesfully loaded')
                else:
                    print(f'{counter_files} file(s) succesfully loaded')
            else:
                print('No new files loaded')

            self.sortFiles()  # Sort the files based on the file names
            self.sortFileList() # Sort the file list widget
            self.updateFileListDisplay() # Update the file list display
            self.updatePlotTypeDict() # Update the plot type dictionary

    def loadFile(self):
        print(f"Loading file: {self.currentFileName}")
        # Load the seismic file
        self.stream = read_seismic_file(self.currentFileName, separate_sources=True)

    def loadStream(self):
        self.streams[self.currentIndex] = self.stream[self.streamIndex]
        self.input_format[self.currentIndex] = check_format(self.streams[self.currentIndex])
        self.getPlotParameters()

        # If it is the first time the file is loaded, update the sources and traces lists
        if self.picks[self.currentIndex] is None:
            # Initialize picks for the current file with a list of nans of the same length as the traces
            self.picks[self.currentIndex] = [np.nan] * len(self.trace_position[self.currentIndex])
            # Intialize errors for the current file with a list of nans of the same length as the traces
            self.error[self.currentIndex] = [np.nan] * len(self.trace_position[self.currentIndex])
            # Initialize the scatter items for the current file with list of empty lists of the same length as the traces
            self.pickSeismoItems[self.currentIndex] = [None] * len(self.trace_position[self.currentIndex])
            # Initialize the scatter items for the current file with list of empty lists of the same length as the traces
            self.pickSetupItems[self.currentIndex] = [None] * len(self.trace_position[self.currentIndex])

    def getPlotParameters(self):
        # Get the trace numbers from the Stream
        shot_trace_number = [trace.stats[self.input_format[self.currentIndex]].trace_header.trace_number_within_the_original_field_record 
                             for trace in self.streams[self.currentIndex]]
        # Get the file trace numbers from the Stream
        file_trace_number = np.arange(1, len(self.streams[self.currentIndex])+1)

        # Get the data and group coordinates from the Stream
        group_coordinates_x = [trace.stats[self.input_format[self.currentIndex]].trace_header.group_coordinate_x / abs(trace.stats[self.input_format[self.currentIndex]].trace_header.scalar_to_be_applied_to_all_coordinates) 
                               if trace.stats[self.input_format[self.currentIndex]].trace_header.scalar_to_be_applied_to_all_coordinates < 0 
                               else trace.stats[self.input_format[self.currentIndex]].trace_header.group_coordinate_x * trace.stats[self.input_format[self.currentIndex]].trace_header.scalar_to_be_applied_to_all_coordinates 
                               for trace in self.streams[self.currentIndex]]
        
        receiver_group_elevation = [trace.stats[self.input_format[self.currentIndex]].trace_header.receiver_group_elevation / abs(trace.stats[self.input_format[self.currentIndex]].trace_header.scalar_to_be_applied_to_all_coordinates) 
                                    if trace.stats[self.input_format[self.currentIndex]].trace_header.scalar_to_be_applied_to_all_coordinates < 0 
                                    else trace.stats[self.input_format[self.currentIndex]].trace_header.receiver_group_elevation * trace.stats[self.input_format[self.currentIndex]].trace_header.scalar_to_be_applied_to_all_coordinates
                                    for trace in self.streams[self.currentIndex]]
        
        # Check if group_coordinates_x has only zeros
        if np.all(np.array(group_coordinates_x) == 0):
            group_coordinates_x = file_trace_number

        # Get the source coordinate from the first trace
        source_coordinates_x = [trace.stats[self.input_format[self.currentIndex]].trace_header.source_coordinate_x / abs(trace.stats[self.input_format[self.currentIndex]].trace_header.scalar_to_be_applied_to_all_coordinates) 
                                if trace.stats[self.input_format[self.currentIndex]].trace_header.scalar_to_be_applied_to_all_coordinates < 0 
                                else trace.stats[self.input_format[self.currentIndex]].trace_header.source_coordinate_x * trace.stats[self.input_format[self.currentIndex]].trace_header.scalar_to_be_applied_to_all_coordinates 
                                for trace in self.streams[self.currentIndex]]
        source_coordinate_x = np.unique(source_coordinates_x)[0]

        surface_elevation_at_source = [trace.stats[self.input_format[self.currentIndex]].trace_header.surface_elevation_at_source / abs(trace.stats[self.input_format[self.currentIndex]].trace_header.scalar_to_be_applied_to_all_coordinates)
                            if trace.stats[self.input_format[self.currentIndex]].trace_header.scalar_to_be_applied_to_all_coordinates < 0
                            else trace.stats[self.input_format[self.currentIndex]].trace_header.surface_elevation_at_source * trace.stats[self.input_format[self.currentIndex]].trace_header.scalar_to_be_applied_to_all_coordinates
                            for trace in self.streams[self.currentIndex]]
        surface_elevation_at_source = np.unique(surface_elevation_at_source)[0]

        # Get the sample interval and delay from the first trace
        self.sample_interval[self.currentIndex] = self.streams[self.currentIndex][0].stats[self.input_format[self.currentIndex]].trace_header.sample_interval_in_ms_for_this_trace / 1_000_000 
        self.delay[self.currentIndex] = self.streams[self.currentIndex][0].stats[self.input_format[self.currentIndex]].trace_header.delay_recording_time/1000

        self.n_sample[self.currentIndex] = len(self.streams[self.currentIndex][0].data)

        self.time[self.currentIndex] = np.arange(self.n_sample[self.currentIndex]) * self.sample_interval[self.currentIndex] + self.delay[self.currentIndex]
        self.ffid[self.currentIndex] = self.streams[self.currentIndex][0].stats[self.input_format[self.currentIndex]].trace_header.original_field_record_number
        self.offset[self.currentIndex] = np.round([group_coordinates_x[i] - source_coordinate_x for i in range(len(group_coordinates_x))],5)
        self.source_position[self.currentIndex] = source_coordinate_x
        self.trace_position[self.currentIndex] = group_coordinates_x
        self.source_elevation[self.currentIndex] = surface_elevation_at_source
        self.trace_elevation[self.currentIndex] = receiver_group_elevation
        self.shot_trace_number[self.currentIndex] = shot_trace_number
        self.file_trace_number[self.currentIndex] = file_trace_number
        self.record_length[self.currentIndex] = (self.n_sample[self.currentIndex]-1) * self.sample_interval[self.currentIndex]

        # Update the mean_dg and mean_ds
        if self.plotTypeX == 'trace_position':
            if len(self.streams[self.currentIndex]) == 1:
                self.mean_dg = 1
            else:
                self.mean_dg = np.round(np.mean(np.diff(self.trace_position[self.currentIndex])),5)
        else:
            self.mean_dg = 1
        
        if self.plotTypeY == 'ffid':
            self.mean_ds = 1
        else:
            if len(self.streams) == 1:
                self.mean_ds = 1
            else:
                self.mean_ds = np.round(np.mean(np.diff(self.source_position)),5)

    def sortFiles(self):
        # Sort files based on the file names
        # Original file paths
        fileNames = self.fileNames
        
        # Get sorted indices based on the file names
        sorted_indices = sorted(range(len(fileNames)), key=lambda i: self.extractFileNumber(os.path.basename(fileNames[i])))

        # Sort each attribute using the sorted indices
        for attr in self.attributes_to_initialize:
            setattr(self, attr, [getattr(self, attr)[i] for i in sorted_indices])

    def extractFileNumber(self, filename):
        # Extract the numeric part from the filename
        match = re.search(r'\d+', filename)
        return int(match.group()) if match else float('inf')

    def sortFileList(self):
        self.fileListWidget.clear()  # Clear the list widget
        for fileName in self.fileNames: #: Add the file names to the list widget
            baseName = os.path.basename(fileName)
            self.fileListWidget.addItem(baseName)
        
        self.fileListWidget.setCurrentRow(self.currentIndex) # Set the current row to the current index

    def updateFileListDisplay(self):
        # Clear the current items in the QListWidget
        self.fileListWidget.clear()

        # Get the selected display option
        self.display_option = self.displayOptionComboBox.currentText()

        # Update the QListWidget based on the selected display option
        if self.display_option == "Filename":
            for file_path in self.fileNames:
                self.fileListWidget.addItem(os.path.basename(file_path))
        elif self.display_option == "Source Position":
            for source_position in self.source_position:
                self.fileListWidget.addItem(str(source_position))
        elif self.display_option == "FFID":
            for ffid in self.ffid:
                self.fileListWidget.addItem(str(ffid))

    def onFileSelectionChanged(self):
        # Get the selected item
        selectedItems = self.fileListWidget.selectedItems()
        # If an item is selected
        if selectedItems:
            selectedBaseName = selectedItems[0].text() # Get the text of the selected item
            
            # Find the index of the selected file path
            for index in range(self.fileListWidget.count()):
                # If the text of the item at the index is the same as the selected base name
                if self.fileListWidget.item(index).text() == selectedBaseName:
                    self.currentFileName = self.fileNames[index] # Set the current file name
                    self.currentIndex = index # Set the current index
                    break
            # Plot the selected file
            self.plotSeismo()
            self.plotBottom()

    def resetSeismoView(self):
        self.plotWidget.autoRange()
        self.plotWidget.getViewBox().setLimits(xMin=None, xMax=None, yMin=None, yMax=None)

        if self.streams:
            # Ensure the dictionary is updated
            self.updatePlotTypeDict()

            # Access the appropriate attribute based on self.plotTypeX
            plot_data_x = self.plotTypeDict.get(self.plotTypeX, [])

            # Flatten the list of lists into a single list
            flat_plot_data_x = [item for sublist in plot_data_x for item in sublist]

            # Set x and y limits
            self.plotWidget.getViewBox().setXRange(min(flat_plot_data_x) - self.mean_dg, 
                                                max(flat_plot_data_x) + self.mean_dg)
            self.plotWidget.getViewBox().setYRange(min(self.time[self.currentIndex]), 
                                                self.max_time)
            # Set zoom limits
            self.plotWidget.getViewBox().setLimits(xMin=min(flat_plot_data_x) - self.mean_dg, 
                                                xMax=max(flat_plot_data_x) + self.mean_dg, 
                                                yMin=min(self.time[self.currentIndex]), 
                                                yMax=self.max_time)
            
    def resetBottomView(self):
        if self.bottomPlotType == 'setup':
            self.resetSetupView()
        elif self.bottomPlotType == 'traveltime':
            self.resetTravelTimeView()

    def resetSetupView(self):
        self.bottomPlotWidget.autoRange()
        self.bottomPlotWidget.getViewBox().setLimits(xMin=None, xMax=None, yMin=None, yMax=None)

        self.updatePlotTypeDict()
        
        if self.source_position:
            # Access the appropriate attribute based on self.plotTypeX (shot_trace_number, file_trace_number, trace_position)
            plot_data_x = self.plotTypeDict.get(self.plotTypeX, [])
            # Flatten the list of lists into a single list
            flat_plot_data_x = [item for sublist in plot_data_x for item in sublist]

            # Access the appropriate attribute based on self.plotTypeY (source_position, ffid, offset)
            plot_data_y = self.plotTypeDict.get(self.plotTypeY, [])
            if self.plotTypeY == 'offset':
                flat_plot_data_y = [item for sublist in plot_data_y for item in sublist] # Flatten the list of lists into a single list
            else:
                flat_plot_data_y = plot_data_y
            
            # Get unique traces and sources from list of list of traces array that are not None
            traces = [trace for trace in flat_plot_data_x if trace is not None]
            sources = [source for source in flat_plot_data_y if source is not None]

            # Set x and y limits
            self.bottomPlotWidget.getViewBox().setXRange(min(traces) - self.mean_dg, 
                                                         max(traces) + self.mean_dg)
            self.bottomPlotWidget.getViewBox().setYRange(min(sources) - 1,
                                                         max(sources) + 1)
            self.bottomPlotWidget.getViewBox().setLimits(xMin=min(traces) - self.mean_dg,
                                                         xMax=max(traces) + self.mean_dg,
                                                         yMin=min(sources) - 1,
                                                         yMax=max(sources) + 1)
            
    def resetTravelTimeView(self):
        self.bottomPlotWidget.autoRange()
        self.bottomPlotWidget.getViewBox().setLimits(xMin=None, xMax=None, yMin=None, yMax=None)

        self.updatePlotTypeDict()
        
        if self.source_position:
            # Access the appropriate attribute based on self.plotTypeX (shot_trace_number, file_trace_number, trace_position)
            plot_data_x = self.plotTypeDict.get(self.plotTypeX, [])
            # Flatten the list of lists into a single list
            flat_plot_data_x = [item for sublist in plot_data_x for item in sublist]

            # Access the appropriate attribute based on self.plotTypeY (source_position, ffid, offset)
            plot_data_y = self.picks
            # Flatten the list of lists into a single list
            flat_plot_data_y = [item for sublist in plot_data_y for item in sublist]

            # Get unique traces and times from list of list of traces array that are not None
            traces = [trace for trace in flat_plot_data_x if trace is not None]
            times = [time for time in flat_plot_data_y if time is not None]

            # Keep only the times where times is not Nan
            times = [time for time in times if not np.isnan(time)]

            # If there are no times, set the min time to 0 and max time to 1
            if not times:
                times = [np.min(self.time[self.currentIndex]), np.max(self.time[self.currentIndex])]
            
            # Set x and y limits
            self.bottomPlotWidget.getViewBox().setXRange(min(traces) - self.mean_dg, 
                                                         max(traces) + self.mean_dg)
            self.bottomPlotWidget.getViewBox().setYRange(min(times) - min(times)*0.1,
                                                         max(times) + max(times)*0.1)
            self.bottomPlotWidget.getViewBox().setLimits(xMin=min(traces) - self.mean_dg,
                                                            xMax=max(traces) + self.mean_dg,
                                                            yMin=min(times) - min(times)*0.1,
                                                            yMax=max(times) + max(times)*0.1)

    def resetTopoView(self):
        self.bottomPlotWidget.autoRange()
        self.bottomPlotWidget.getViewBox().setLimits(xMin=None, xMax=None, yMin=None, yMax=None)

        self.updatePlotTypeDict()
        
        if self.trace_elevation:

            mean_dx = np.mean(np.diff(self.trace_position[self.currentIndex]))
            mean_dz = np.mean(np.diff(self.trace_elevation[self.currentIndex]))

            # Set x and y limits
            self.bottomPlotWidget.getViewBox().setXRange(min(min(self.trace_position)) - mean_dx, max(max(self.trace_position)) + mean_dx)
            self.bottomPlotWidget.getViewBox().setYRange(min(min(self.trace_elevation)) - mean_dz*10, max(max(self.trace_elevation)) + mean_dz)
            self.bottomPlotWidget.getViewBox().setLimits(xMin=min(min(self.trace_position)) -  mean_dx, xMax=max(max(self.trace_position)) + mean_dx,
                                                        yMin=min(min(self.trace_elevation)) - mean_dz*10, yMax=max(max(self.trace_elevation)) + mean_dz)

    def showRawHeaders(self):
        if self.streams:
            headers = set()
            header_values = {}

            # Collect unique headers and their values across all traces
            for trace in self.streams[self.currentIndex]:
                for header, value in trace.stats[self.input_format[self.currentIndex]].trace_header.items():
                    headers.add(header)
                    if header not in header_values:
                        header_values[header] = {'values': set()}
                    header_values[header]['values'].add(value)

            # Convert sets to lists for display
            for key in header_values:
                header_values[key]['values'] = list(header_values[key]['values'])

            # Sort the headers and header_values alphabetically
            headers = sorted(headers)
            header_values = {key: header_values[key] for key in sorted(header_values)}
            
            dialog = HeaderDialog(list(headers), header_values, self)
            dialog.exec_()

    def showHeaders(self):
        if self.streams:
            attributes_to_collect = {
                "ffid": "FFID",
                "source_position": "Source Position (m)",
                "source_elevation": "Source Elevation (m)",
                "delay": "Delay (s)",
                "sample_interval": "Sample Interval (s)",
                "n_sample": "Number of Samples",
                "record_length": "Record Length (s)",
                "shot_trace_number": "Trace No",
                "trace_position": "Trace Position (m)",
                "trace_elevation": "Trace Elevation (m)",
                "offset": "Offset (m)",
            }

            # Collect unique headers and their values across all traces
            header_values = {}

            for header, display_name in attributes_to_collect.items():
                header_values[display_name] = {'original': header, 'values': []}
                attribute_values = getattr(self, header, [])[self.currentIndex]
                trace_numbers = getattr(self, "shot_trace_number", [])[self.currentIndex]
                if not isinstance(attribute_values, list):
                    attribute_values = [attribute_values]

                for trace_number, value in zip(trace_numbers, attribute_values):
                    if isinstance(value, (list, tuple, np.ndarray)):
                        # Flatten the list if it contains lists
                        for item in value:
                            if isinstance(item, (list, tuple, np.ndarray)):
                                header_values[display_name]['values'].extend((trace_number, v) for v in item)
                            else:
                                header_values[display_name]['values'].append((trace_number, item))
                    else:
                        header_values[display_name]['values'].append((trace_number, value))

            # Sort the values by trace number
            for key in header_values:
                header_values[key]['values'] = [v for _, v in sorted(header_values[key]['values'], key=lambda x: x[0])]

            dialog = HeaderDialog(list(attributes_to_collect.values()), header_values, self)
            dialog.exec_()
    
    def setMaxTime(self):
        # Save the current locale
        original_locale = QLocale()
        # Set the locale to 'C' to use the dot as the decimal separator
        QLocale.setDefault(QLocale(QLocale.C))

        if self.max_time is None:
            self.max_time = 0.05

        # Open a dialog to set the maximum time to display
        self.max_time, ok = QInputDialog.getDouble(self, "Set Maximum Time", "Enter maximum time to plot (in s):",  
            decimals=2, value=self.max_time)
        
        # Restore the original locale
        QLocale.setDefault(original_locale)

        if ok:
            print(f"Maximum time set to {self.max_time} s")
            self.updatePlotWithMaxTime()

    def toggleClip(self):
        self.clip = self.clipAction.isChecked()
        if self.streams:
            self.plotSeismo()

    def toggleNormalize(self):
        self.normalize = self.normalizeAction.isChecked()
        if self.streams:
            self.plotSeismo()

    def toggleShowTimeSamples(self):
        self.show_time_samples = self.showTimeSamplesAction.isChecked()
        if self.streams:
            self.plotSeismo()

    def toggleShowAirWave(self):
        self.show_air_wave = self.showAirWaveAction.isChecked()
        if self.streams:
            if self.show_air_wave:
                if self.plotTypeX == 'trace_position':
                    self.plotAirWave()
                else:   
                    print('Air wave not plotted with trace number')
            else:     
                self.hideAirWave()

    def toggleAssistedPicking(self):
        self.assisted_picking = self.assistedPickingAction.isChecked()

    def setGain(self):
        # Open a dialog to set the gain
        self.gain, ok = QInputDialog.getDouble(self, "Set Gain", "Enter gain:", 
            min=self.gain, decimals=2)
        if ok and self.streams:
            self.plotSeismo()

    def updatePlotWithMaxTime(self):
        # Update the plot to limit the y-axis to the specified maximum time
        self.plotWidget.getViewBox().setYRange(0, self.max_time)
        self.viewBox.setLimits(yMax=self.max_time)

    def setTracePosition(self):
        self.plotTypeX = 'trace_position'
        self.statusBar.showMessage('Switching to trace position',1000)
        if len(self.streams[self.currentIndex]) == 1:
            self.mean_dg = 1
        else:
            self.mean_dg = np.mean(np.diff(self.trace_position[self.currentIndex]))
        self.x_label = 'Trace Position (m)'
        if self.streams:
            self.plotSeismo()
            self.plotBottom()

    def setFileTraceNumber(self):
        self.plotTypeX = 'file_trace_number'
        self.statusBar.showMessage('Switching to file trace number',1000)
        self.mean_dg = 1
        self.x_label = 'Trace number in file'
        if self.streams:
            self.plotSeismo()
            self.plotBottom()

    def setShotTraceNumber(self):
        self.plotTypeX = 'shot_trace_number'
        self.statusBar.showMessage('Switching to trace number',1000)
        self.mean_dg = 1
        self.x_label = 'Trace number'
        if self.streams:
            self.plotSeismo()
            self.plotBottom()

    def setSourcePosition(self):
        self.plotTypeY = 'source_position'
        self.statusBar.showMessage('Switching to source position',1000)
        if len(self.streams) == 1:
            self.mean_ds = 1
        else:
            self.mean_ds = np.mean(np.diff(self.source_position))
        self.y_label = 'Source Position (m)'
        if self.streams:
            self.plotBottom()

    def setFFID(self):
        self.plotTypeY = 'ffid'
        self.statusBar.showMessage('Switching to FFID',1000)
        self.mean_ds = 1
        self.y_label = 'FFID'
        if self.streams:
            self.plotBottom()

    def setOffset(self):
        self.plotTypeY = 'offset'
        self.statusBar.showMessage('Switching to offset',1000)
        if len(self.streams) == 1:
            self.mean_ds = 1
        else:
            self.mean_ds = np.mean(np.diff(self.source_position))
        self.y_label = 'Offset (m)'
        if self.streams:
            self.plotBottom()

    def LoadAllFiles(self):
        for filepath in self.fileNames:
            self.currentFileName = filepath
            self.loadFile()

        print(f'{len(self.fileNames)} files succesfully loaded.')

    def updatePickPosition(self, i):
        # Ensure the dictionary is updated
        self.updatePlotTypeDict()

        # Access the appropriate attribute based on self.plotTypeX
        plot_data_x = self.plotTypeDict.get(self.plotTypeX, [])

        # Flatten the list of lists into a single list
        flat_plot_data_x = [item for sublist in plot_data_x for item in sublist]

        # Get the x position based on the plot type
        x_ok = flat_plot_data_x[i] if i < len(flat_plot_data_x) else None

        # Get the y position (assuming y_ok is already defined)
        y_ok = self.picks[self.currentIndex][i] if i < len(self.picks[self.currentIndex]) else None

        # Update the pick position if x_ok and y_ok are valid
        if x_ok is not None and y_ok is not None:
            self.pickSeismoItems[self.currentIndex][i].setData(x=[x_ok], y=[y_ok])

    def fillPositive(self):
        self.polarity = 'positive'
        self.statusBar.showMessage('Filling positive amplitudes',1000)
        if self.streams:
            self.plotSeismo()

    def fillNegative(self):
        self.polarity = 'negative'
        self.statusBar.showMessage('Filling negative amplitudes',1000)
        if self.streams:
            self.plotSeismo()

    def noFill(self):
        self.polarity = 'None'
        self.statusBar.showMessage('No fill',1000)
        if self.streams:
            self.plotSeismo()

    def updateTitle(self):
        if self.streams:
            title = f"FFID: {self.ffid[self.currentIndex]}  |  Source at {self.source_position[self.currentIndex]} m"
            self.plotWidget.getPlotItem().setTitle(title, size='12pt', color='k')

    def getWiggleInfo(self, i, trace):

        # Ensure trace.data is a NumPy array of floats
        trace_data = np.array(trace.data, dtype=float)

        if self.normalize:
            # Normalize to max value of 1 and scale by mean_dg/2
            normalized_trace_data = (trace_data / np.max(np.abs(trace_data))) * (self.mean_dg/2) * self.gain
        else: 
            normalized_trace_data = trace_data * self.gain

        # Clip the trace data
        if self.clip:
            normalized_trace_data = np.clip(normalized_trace_data, -(self.mean_dg/2), (self.mean_dg/2))

        # Access the appropriate attribute based on self.plotTypeX (shot_trace_number, file_trace_number, trace_position)
        plot_data_x = self.plotTypeDict.get(self.plotTypeX, [])

        # Ensure offset is a float
        offset = float(plot_data_x[self.currentIndex][i])

        # Add the offset to the normalized trace data
        x = normalized_trace_data + offset

        # Get the fill level and put in a NumPy array of floats (in order to make the curve filling work)
        fillLevel = np.array(offset)

        # Create a mask for positive or negative amplitudes
        if self.polarity == 'positive':
            mask = x >= fillLevel
        elif self.polarity == 'negative':
            mask = x <= fillLevel
        else:
            mask = None

        # Interpolate points to ensure smooth transition
        x_interpolated = []
        t_interpolated = []
        for j in range(len(x) - 1):
            x_interpolated.append(x[j])
            t_interpolated.append(self.time[self.currentIndex][j])
            if mask is not None and mask[j] != mask[j + 1]:
                # Linear interpolation
                t_interp = self.time[self.currentIndex][j] + (self.time[self.currentIndex][j + 1] - self.time[self.currentIndex][j]) * (fillLevel - x[j]) / (x[j + 1] - x[j])
                x_interpolated.append(fillLevel)
                t_interpolated.append(t_interp)

        x_interpolated.append(x[-1])
        t_interpolated.append(self.time[self.currentIndex][-1])

        x_interpolated = np.array(x_interpolated)
        t_interpolated = np.array(t_interpolated)

        # Create arrays for the positive parts
        if self.polarity == 'positive':
            x_filled = np.where(x_interpolated >= fillLevel, x_interpolated, fillLevel)
        elif self.polarity == 'negative':
            x_filled = np.where(x_interpolated <= fillLevel, x_interpolated, fillLevel)
        else:
            x_filled = x_interpolated

        return x, x_filled, t_interpolated, fillLevel, mask

    def plotSeismo(self):
        # Clear previous plots
        self.plotWidget.clear()

        # Update the title
        self.updateTitle()

        # Set axis labels
        self.plotWidget.setLabel('left', self.t_label)
        self.plotWidget.setLabel('top', self.x_label)

        # Move x-axis to the top
        self.plotWidget.getAxis('bottom').setLabel('')
        self.plotWidget.getAxis('top').setLabel(self.x_label)
        self.plotWidget.showAxis('top')
        self.plotWidget.showAxis('bottom')
        self.plotWidget.showAxis('left')
        self.plotWidget.showAxis('right')

        # Display shot position and ffid in the title
        self.statusBar.showMessage(f'FFID: {self.ffid[self.currentIndex]} | Source at {self.source_position[self.currentIndex]} m')

        #####
        # Plotting could be optimized to only plot time samples, 
        # or positive negative parts instead of replotting the whole thing (as it is done for airwave)
        #####
        
        for i, trace in enumerate(self.streams[self.currentIndex]):
            
            # Get the wiggle info
            x, x_filled, t_interpolated, fillLevel, mask = self.getWiggleInfo(i, trace)

            # Plot the original curve
            if self.show_time_samples:
                self.plotWidget.plot(x, self.time[self.currentIndex], pen=self.col,
                                                 symbol='o', symbolBrush='k', symbolPen='k', symbolSize=2)
            else:
                self.plotWidget.plot(x, self.time[self.currentIndex], pen=self.col)

            # Plot the positive/negative part of the curve with fill
            if mask is not None:
                self.plotWidget.plot(x_filled, t_interpolated, pen=None, 
                                    fillLevel=fillLevel, fillBrush=(0, 0, 0, 150))

            # Plot the picks
            if not np.isnan(self.picks[self.currentIndex][i]):
                self.updatePickPosition(i)
                scatter = self.pickSeismoItems[self.currentIndex][i]
                self.plotWidget.addItem(scatter)

        if self.show_air_wave:
            self.plotAirWave()
        
        self.resetSeismoView()  # Reset the plot 

    def plotAirWave(self):
        # Velocity of the air wave in m/s
        air_wave_velocity = 340.0

        # Get the source position and offsets for the current index
        source_position = self.source_position[self.currentIndex]
        offsets = self.offset[self.currentIndex]

        # Separate positive and negative offsets
        positive_offsets = offsets[offsets > 0]
        negative_offsets = offsets[offsets < 0]

        # Calculate the corresponding times
        positive_times = positive_offsets / air_wave_velocity
        negative_times = -negative_offsets / air_wave_velocity

        # Concatenate positive and negative times and add 0 at source position
        positive_times = np.concatenate((np.array([0]), positive_times))
        negative_times = np.concatenate((np.array([0]), negative_times))

        # Concatenate positive and negative offsets and add 0 at the beginning
        positive_offsets = np.concatenate((np.array([0]), positive_offsets))
        negative_offsets = np.concatenate((np.array([0]), negative_offsets))

        # Plot the positive offsets
        self.airWaveItems[self.currentIndex][0] = pqg.PlotDataItem(positive_offsets + source_position, positive_times, pen='b')
        self.plotWidget.addItem(self.airWaveItems[self.currentIndex][0])

        # Plot the negative offsets
        self.airWaveItems[self.currentIndex][1] = pqg.PlotDataItem(negative_offsets + source_position, negative_times, pen='b')
        self.plotWidget.addItem(self.airWaveItems[self.currentIndex][1])

        # Add point scatter at the source position
        self.airWaveItems[self.currentIndex][2] = pqg.PlotDataItem(x=[source_position], y=[0], pen='b', symbol='o', 
                                                                        symbolBrush='b', symbolPen='b', symbolSize=5)
        self.plotWidget.addItem(self.airWaveItems[self.currentIndex][2])

    def hideAirWave(self):
        for item in self.airWaveItems[self.currentIndex]:
            if item is not None:
                self.plotWidget.removeItem(item)
                item = None

    def pickTime(self, event):

        if event.button() == QtCore.Qt.LeftButton or event.button() == QtCore.Qt.MiddleButton:
            mousePoint = self.plotWidget.plotItem.vb.mapSceneToView(event.scenePos())
            x = mousePoint.x()
            y = mousePoint.y()
            
            # Get the current axis ranges
            x_range = self.plotWidget.plotItem.vb.viewRange()[0]
            y_range = self.plotWidget.plotItem.vb.viewRange()[1]

            # Access the appropriate attribute based on self.plotTypeX (shot_trace_number, file_trace_number, trace_position)
            plot_data_x = self.plotTypeDict.get(self.plotTypeX, [])

            # Check if the clicked position is within the axis bounds
            if x_range[0] <= x <= x_range[1] and y_range[0] <= y <= y_range[1]:
                # Calculate the distance between the clicked point and the trace
                x_distance = np.array(plot_data_x[self.currentIndex]) - x
                y_distance = np.array(self.time[self.currentIndex]) - y

                # Get index of the closest trace
                index_x = np.argmin(np.abs(x_distance))
                index_y = np.argmin(np.abs(y_distance))

                # Get the x and y values of the closest trace
                x_ok = np.array(self.plotTypeDict[self.plotTypeX][self.currentIndex])[index_x]
                y_ok = np.array(self.time[self.currentIndex])[index_y]

                if self.assisted_picking:

                    # Smooth the trace data
                    trace_data = np.array(self.streams[self.currentIndex][index_x].data)
                    trace_data = trace_data / np.max(np.abs(trace_data))
                    smoothed_trace_data = np.convolve(trace_data, np.ones(self.smoothing_window_size)/self.smoothing_window_size, mode='same')

                    # Calculate the mean and standard deviation of the data within the window around the pick
                    pick_index = np.argmin(np.abs(self.time[self.currentIndex] - y))
                    window_start = 0
                    window_end = pick_index
                    mean_window = np.mean(np.abs(smoothed_trace_data[window_start:window_end]))
                    std_window = np.std(np.abs(smoothed_trace_data[window_start:window_end]))
                    deviation_threshold = std_window * self.deviation_threshold

                    # Look for significant deviation within the window
                    for i in range(pick_index, pick_index+self.picking_window_size):
                        if np.abs(smoothed_trace_data[i] - mean_window) > deviation_threshold:
                            # plt.close()  # Clear the current figure
                            # plt.plot(smoothed_trace_data[window_start:window_end+self.picking_window_size] - mean_window)
                            # plt.plot(i, np.abs(smoothed_trace_data[i]) - mean_window, 'ro')
                            # plt.plot([window_start, window_end+self.picking_window_size], [mean_window, mean_window], 'g')
                            # plt.plot([window_start, window_end+self.picking_window_size], [mean_window+deviation_threshold, mean_window+deviation_threshold], 'r')
                            # plt.plot([window_start, window_end+self.picking_window_size], [mean_window-deviation_threshold, mean_window-deviation_threshold], 'r')
                            # plt.show()
                            y_ok = self.time[self.currentIndex][i]
                            break

                # Set the text of the QLabel to the clicked position
                self.label.setText(f"Clicked position: x = {x_ok}, y = {y_ok}")

                # If there's already a scatter plot item for this trace, update its position
                if self.pickSeismoItems[self.currentIndex][index_x] is not None:
                    if event.button() == QtCore.Qt.LeftButton:
                        self.pickSeismoItems[self.currentIndex][index_x].setData(x=[x_ok], y=[y_ok])
                        
                        self.picks[self.currentIndex][index_x] = y_ok # Update the pick
                        self.error[self.currentIndex][index_x] = self.pickError(y_ok) # Update the error
                        
                    else:
                        self.plotWidget.removeItem(self.pickSeismoItems[self.currentIndex][index_x])
                        self.pickSeismoItems[self.currentIndex][index_x] = None

                        self.picks[self.currentIndex][index_x] = np.nan # Remove the pick
                        self.error[self.currentIndex][index_x] = np.nan # Remove the error
                else:
                    if event.button() == QtCore.Qt.LeftButton:
                        # Otherwise, create a new scatter plot item and add it to the plot widget and the dictionary
                        scatter1 = pqg.ScatterPlotItem(x=[x_ok], y=[y_ok], pen='r', symbol='+')
                        self.plotWidget.addItem(scatter1)
                        self.pickSeismoItems[self.currentIndex][index_x] = scatter1

                        self.picks[self.currentIndex][index_x] = y_ok # Add the pick
                        self.error[self.currentIndex][index_x] = self.pickError(y_ok) # Add the error
                # Update the color map if there are picks that are not nan in all files
                if not np.isnan(self.picks).all():
                    self.createPicksColorMap()

                self.plotBottom() # Update the setup plot

    def setErrorParameters(self):
        # Open a dialog to set the error parameters where default values are the current values
        dialog = ErrorParametersDialog(self.relativeError, self.absoluteError, self.maxRelativeError, self.minAbsoluteError, self.maxAbsoluteError)
        if dialog.exec_():
            self.relativeError = dialog.relativeError
            self.absoluteError = dialog.absoluteError
            self.maxRelativeError = dialog.maxRelativeError
            self.minAbsoluteError = dialog.minAbsoluteError
            self.maxAbsoluteError = dialog.maxAbsoluteError

    def setAssistedPickingParameters(self):
        # Open a dialog to set the assisted picking parameters where default values are the current values
        dialog = AssistedPickingParametersDialog(self.smoothing_window_size, self.deviation_threshold, 
                                                 self.picking_window_size)
        if dialog.exec_():
            self.smoothing_window_size = dialog.smoothing_window_size
            self.deviation_threshold = dialog.deviation_threshold
            self.picking_window_size = dialog.picking_window_size

    def setTopoParameters(self):
        # Open a dialog to set the topography parameters where default values are the current values
        dialog = TopoParametersDialog(self.column_x, self.column_z, self.delimiter, self.skiprows)
        if dialog.exec_():
            self.column_x = dialog.column_x
            self.column_z = dialog.column_z
            self.delimiter = dialog.delimiter
            self.skiprows = dialog.skiprows
        
    def pickError(self, pick):
        
        error = pick * self.relativeError + self.absoluteError
        if self.maxAbsoluteError is not None:
            if error > self.maxAbsoluteError:
                error = self.maxAbsoluteError
        if self.minAbsoluteError is not None:
            if error < self.minAbsoluteError:
                error = self.minAbsoluteError
        if self.maxRelativeError is not None:
            if error > self.maxRelativeError * pick:
                error = self.maxRelativeError * pick

        return error
    
    def setAllPickError(self):
        # Set self.error to the error calculated from the picks
        for i, _ in enumerate(self.picks):
            for j, pick in enumerate(self.picks[i]):
                if not np.isnan(pick):
                    self.error[i][j] = self.pickError(pick)

    def createPicksColorMap(self):
        # Create a colormap
        colormap = pqg.colormap.get('Spectral_r',source='matplotlib')

        # Get the values of the picks that are not nan in a list of list
        values = [value for sublist in self.picks for value in sublist if not np.isnan(value)]

        # Normalize the values to the range [0, 1]
        min_val = min(values)
        max_val = max(values)
        if min_val == max_val:
            min_val = min_val - 1
            max_val = max_val + 1
        normalized_values = [(val - min_val) / (max_val - min_val) for val in values]

        # Map values to colors
        self.colors = colormap.map(normalized_values, mode='qcolor')

    def plotSetup(self):

        # Clear previous plots
        self.bottomPlotWidget.clear()

        # Flatten the traces and repeat sources
        x_all = []
        y_all = []
        pick_all = []
        
        for i, _ in enumerate(self.source_position):
            traces = self.plotTypeDict[self.plotTypeX][i]  # List of traces for the current source
            m = len(traces)  # Number of traces for the current source
            x_all.extend(traces)  # Add traces to x_values
            plot_y = self.plotTypeDict[self.plotTypeY] # List of sources for the current trace

            if self.plotTypeY == 'offset':
                y_all.extend(plot_y[i])
            else:
                y_all.extend([plot_y[i]] * m)
            pick_all.extend(self.picks[i])  # Add picks to pick_all

        scatter = pqg.ScatterPlotItem(x=x_all, y=y_all, symbol='o',
                                      brush =(0, 0, 0, 150), size=5) 
        self.bottomPlotWidget.addItem(scatter)        

        # If there are picks that are not nan, plot them with colors      
        x_pick = [x_all[i] for i in range(len(x_all)) if not np.isnan(pick_all[i])]
        y_pick = [y_all[i] for i in range(len(y_all)) if not np.isnan(pick_all[i])]

        if x_pick:
            # Create a colormap
            self.createPicksColorMap()

            # Create ScatterPlotItem with colors
            scatter = pqg.ScatterPlotItem(x=x_pick, y=y_pick, symbol='s', 
                                          brush=self.colors, pen=self.colors, size=8)
            self.bottomPlotWidget.addItem(scatter)

        # Add horizontal lines around the current source position
        if self.source_position:
            current_source = self.plotTypeDict[self.plotTypeY][self.currentIndex]
            first_trace = self.plotTypeDict[self.plotTypeX][self.currentIndex][0]
            last_trace = self.plotTypeDict[self.plotTypeX][self.currentIndex][-1]

            if len(self.source_position) > 1:
                if self.plotTypeY == 'offset':
                    first_y = current_source[0]
                    last_y = current_source[-1]
                    mean_dy = np.mean(np.abs(np.diff(self.plotTypeDict[self.plotTypeY][self.currentIndex])))
                else:
                    first_y = current_source
                    last_y = current_source
                    # mean_dy = np.mean(np.abs(np.diff(self.plotTypeDict[self.plotTypeY])))
                    mean_dy = self.mean_ds

                x_line = [first_trace - self.mean_dg, last_trace + self.mean_dg]
                y_line_1 = [first_y - mean_dy, last_y - mean_dy]
                y_line_2 = [first_y + mean_dy, last_y + mean_dy]

                line1 = pqg.PlotDataItem(x_line, y_line_1, pen='k')
                line2 = pqg.PlotDataItem(x_line, y_line_2, pen='k')
                self.bottomPlotWidget.addItem(line1)
                self.bottomPlotWidget.addItem(line2)

        # Set axis labels
        self.bottomPlotWidget.setLabel('left', self.y_label)
        self.bottomPlotWidget.setLabel('top', self.x_label)
        self.bottomPlotWidget.showAxis('top')
        self.bottomPlotWidget.showAxis('bottom')
        self.bottomPlotWidget.showAxis('left')
        self.bottomPlotWidget.showAxis('right')

        # Reset the view
        self.resetSetupView()

    def plotTravelTime(self):

        # Clear previous plots
        self.bottomPlotWidget.clear()

        # Loop over the sources
        for i, _ in enumerate(self.source_position):
            # Check if the list of picks is not None or full of nans
            if self.picks[i] is not None and not np.isnan(self.picks[i]).all():
                
                # Plot trace position vs travel time with points and lines
                if i == self.currentIndex:
                    pen = pqg.mkPen('b', width=2)
                    # Plot the trace position vs travel time with different color
                    plot_item = pqg.PlotDataItem(x=self.plotTypeDict[self.plotTypeX][i], y=self.picks[i], 
                                                 symbol='+', pen=pen, symbolBrush='r', symbolPen='r', symbolSize=8)
                else:
                    # Plot the trace position vs travel time with default color
                    plot_item = pqg.PlotDataItem(x=self.plotTypeDict[self.plotTypeX][i], y=self.picks[i], 
                                                 symbol='o', pen='k', symbolBrush='k', symbolPen='k', symbolSize=2)
                self.bottomPlotWidget.addItem(plot_item)

        # Set axis labels
        self.bottomPlotWidget.setLabel('left', self.t_label)
        self.bottomPlotWidget.setLabel('top', self.x_label)
        self.bottomPlotWidget.showAxis('top')
        self.bottomPlotWidget.showAxis('bottom')
        self.bottomPlotWidget.showAxis('left')
        self.bottomPlotWidget.showAxis('right')

        # Reset the view
        self.resetTravelTimeView()

    def importTopo(self):
        # Import a topography file

        # The first argument returned is the filename and path
        fname, _ = QFileDialog.getOpenFileName(
            self, 'Open file', filter='Topography files (*.xyz *.csv *.txt)')

        if fname != "":
            # Load the file
            try:
                # Load the file
                data = np.loadtxt(fname, delimiter=self.delimiter, skiprows=self.skiprows)
                self.input_position = data[:, self.column_x]
                self.input_elevation = data[:, self.column_z]
                self.updateTopography()
                print(f'Topography loaded from: {fname}')
                if self.bottomPlotType == 'topo':
                    self.plotTopo()
            except Exception as e:
                print(f'Error loading topography: {e}')

    def updateTopography(self):
        # Interpolate the topography at the station positions
        # Create an interpolation function
        f = interp1d(self.input_position,self.input_elevation, fill_value="extrapolate", kind='linear')

        # Update the trace and source
        for i, (trace, elevation) in enumerate(zip(self.trace_position, self.trace_elevation)):
            if trace is not None:
                for j, (x, y) in enumerate(zip(trace, elevation)): 
                    self.trace_position[i][j] = x
                    self.trace_elevation[i][j] = float(np.round(f(x),5))

        for i, (source, elevation) in enumerate(zip(self.source_position, self.source_elevation)):
            if source is not None:
                self.source_elevation[i] = float(np.round(f(source),5))

    def plotTopo(self):
        # Clear previous plots
        self.bottomPlotWidget.clear()

        # Get unique traces position/elevation from list of list of traces array that are not None
        traces = [(trace, elevation) for sublist_position, sublist_elevation in zip(self.trace_position, self.trace_elevation) if sublist_position is not None for trace, elevation in zip(sublist_position, sublist_elevation)]

        # Get unique sources position/elevation from list of sources array that are not None
        sources = [(source, elevation) for source, elevation in zip(self.source_position, self.source_elevation) if source is not None]

        # Concatenate traces and sources (x,z) positions
        all_positions = np.concatenate((traces, sources))

        # Get unique (x,z) positions from concatenated array of (x,z) positions
        unique_positions = np.unique(all_positions, axis=0)
        unique_traces = np.unique(traces, axis=0)
        unique_sources = np.unique(sources, axis=0)
        
        # Plot the topography
        self.bottomPlotWidget.plot(unique_positions[:,0], unique_positions[:,1], pen='k')

        # Plot the traces
        trace_plot = self.bottomPlotWidget.plot(unique_traces[:,0], unique_traces[:,1], pen=None, symbol='o', symbolBrush='r', symbolPen='r', symbolSize=5)

        # Plot the sources
        source_plot = self.bottomPlotWidget.plot(unique_sources[:,0], unique_sources[:,1], pen=None, symbol='o', symbolBrush='b', symbolPen='b', symbolSize=5)

        # Set axis labels
        self.bottomPlotWidget.setLabel('left', 'Elevation (m)')
        self.bottomPlotWidget.setLabel('top', 'Position (m)')
        self.bottomPlotWidget.showAxis('top')
        self.bottomPlotWidget.showAxis('bottom')
        self.bottomPlotWidget.showAxis('left')
        self.bottomPlotWidget.showAxis('right')

        # Add legend
        legend = pqg.LegendItem((100,60), offset=(10,10))
        legend.setParentItem(self.bottomPlotWidget.getViewBox())
        legend.addItem(trace_plot, 'Traces')
        legend.addItem(source_plot, 'Sources')

        # Reset the view
        self.resetTopoView()

    def savePicks(self):
        # Save the picks to a pygimli .sgt file 

        # Get unique traces from list of list of traces array that are not None
        trace_pairs = []
        for sublist_position, sublist_elevation in zip(self.trace_position, self.trace_elevation):
            if sublist_position is not None:
                for trace, elevation in zip(sublist_position, sublist_elevation):
                    trace_pairs.append((trace, elevation))

        # Get unique sources from list of sources array
        source_pairs = [(source, elevation) for source, elevation in zip(self.source_position, self.source_elevation) if source is not None]

        # Convert trace_pairs and source_pairs to numpy structured arrays
        trace_pairs = np.array(trace_pairs, dtype=[('position', float), ('elevation', float)])
        source_pairs = np.array(source_pairs, dtype=[('position', float), ('elevation', float)])

        # Concatenate trace_pairs and source_pairs
        all_pairs = np.concatenate((trace_pairs, source_pairs))

        # Get unique stations from all_pairs
        stations = np.unique(all_pairs)

        # Get trace indices in station list
        trace_indices = [np.where((stations['position'] == trace_pair['position']) & (stations['elevation'] == trace_pair['elevation']))[0][0] for trace_pair in trace_pairs]

        # Get source indices in station list
        source_indices = [np.where((stations['position'] == source_pair['position']) & (stations['elevation'] == source_pair['elevation']))[0][0] for source_pair in source_pairs]

        # Number of non-NaN picks in the list of picks where list of picks is not None
        picks = [pick for sublist in self.picks if sublist is not None for pick in sublist]
        n_picks = np.sum(~np.isnan(picks))

        # Write file with the following format:
        # Number of stations
        # x, y, z coordinates of stations
        # Number of picks
        # Source index, trace index, pick time, pick error

        ### TODO
        # Add z coordinates of stations
        # Remove unused stations (or not)

        if n_picks == 0:
            self.statusBar.showMessage('No picks to save!', 2000)
            return
        
        # The first argument returned is the filename and path
        fname, _ = QFileDialog.getSaveFileName(
            self, 'Save to file', filter='Source-Geophone-Time file (*.sgt)')
        
        if fname != "":
            with open(fname, 'w') as f:
                # Write number of stations
                f.write(f"{len(stations)} # shot/geophone points\n")
                f.write("# x\ty\n")
                for station in stations:
                    x = station[0]
                    y = station[1]
                    f.write(f"{x}\t{y}\n")
                # Write number of picks
                f.write(f"{n_picks} # measurements\n")
                f.write("# s\tg\tt\terr\n")

                for i, pick_list in enumerate(self.picks):
                    if pick_list is not None:
                        for j, pick in enumerate(pick_list):
                            if not np.isnan(pick):
                                # Write source index, trace index, pick time, pick error
                                # format for time is in seconds with 5 decimal places
                                error = self.error[i][j]
                                f.write(f"{source_indices[i] + 1}\t{trace_indices[j] + 1}\t{pick:.5f}\t{error:.5f}\n")

            self.statusBar.showMessage(f'Picking saved at: {fname}.', 10000)
        else:
            self.statusBar.showMessage('No file saved!', 2000)

    def setPlotTravelTime(self):
        self.bottomPlotType = 'traveltime'
        self.statusBar.showMessage('Switching to traveltime plot',1000)
        if self.streams:
            self.plotTravelTime()

    def setPlotSetup(self):
        self.bottomPlotType = 'setup'
        self.statusBar.showMessage('Switching to source/trace diagram',1000)
        if self.streams:
            self.plotSetup()

    def setPlotTopo(self):
        self.bottomPlotType = 'topo'
        self.statusBar.showMessage('Switching to topography plot',1000)
        if self.streams:
            self.plotTopo()

    def plotBottom(self):
        if self.bottomPlotType == 'traveltime':
            self.plotTravelTime()
        elif self.bottomPlotType == 'setup':
            self.plotSetup()
        elif self.bottomPlotType == 'topo':
            self.plotTopo()

    def loadPicks(self, fname=None, verbose=False):
        # Load picks from a pygimli .sgt file

        # The first argument returned is the filename and path
        if fname is None or not fname:
            fname, _ = QFileDialog.getOpenFileName(
                self, 'Open file', filter='Source-Geophone-Time file (*.sgt)')
        
        if fname != "":
            with open(fname, 'r') as f:
                # Read number of stations
                n_stations = int(f.readline().split('#')[0].strip())
                if verbose:
                    print(f"Number of stations: {n_stations}")

                # Read line and check if it is a comment
                flag_comment = True
                while flag_comment:
                    line = f.readline().strip()
                    
                    if '#' in line[0]:
                        if verbose:
                            print(f"Comment: {line}")
                        flag_comment = True
                    else:
                        flag_comment = False

                # Read x, y coordinates of stations
                uploaded_stations = []
                for i in range(n_stations):
                    if i>0:
                        line = f.readline().strip()

                    if verbose:
                        if i < 5 or i > n_stations - 5:
                            print(f"Reading station line: {line}")
                
                    if line:  # Check if the line is not empty
                        parts = line.split()
                        if len(parts) == 2:  # Ensure there are exactly two values
                            x, y = map(float, parts)
                            uploaded_stations.append((x, y))
                        elif len(parts) == 3:  # Ensure there are exactly three values
                            x, y, z = map(float, parts)
                            uploaded_stations.append((x, y, z))
                            
                # Read number of picks
                n_picks = int(f.readline().split('#')[0].strip())
                if verbose:
                    print(f"Number of picks: {n_picks}")

                # Read line and check if it is a comment
                flag_comment = True
                while flag_comment:
                    line = f.readline().strip()
                    
                    if '#' in line[0]:
                        if verbose:
                            print(f"Comment: {line}")
                        flag_comment = True
                        # Find order of s, g, t and err in comment line
                        if 's' in line:
                            s_ind = line.split().index('s') - 1
                        if 'g' in line:
                            g_ind = line.split().index('g') - 1
                        if 't' in line:
                            t_ind = line.split().index('t') - 1
                        if 'err' in line:
                            err_ind = line.split().index('err') - 1
                    else:
                        flag_comment = False

                # Read source index, trace index, pick time, pick error
                uploaded_picks = []
                for i in range(n_picks):
                    if i>0:
                        line = f.readline().strip()

                    if verbose:
                        if i < 5 or i > n_picks - 5:
                            print(f"Reading pick line: {line}")

                    if line:  # Check if the line is not empty
                        parts = line.split()
                        #### TODO 
                        # handle more or less values than 4
                        if len(parts) == 4:  # Ensure there are exactly four values (could be more or less)
                            # use the indices to get the values
                            source = int(parts[s_ind])
                            trace = int(parts[g_ind])
                            pick = float(parts[t_ind])
                            error = float(parts[err_ind])
                            uploaded_picks.append((source, trace, pick, error))

                self.statusBar.showMessage(f'Picking loaded from: {fname}.', 10000)    

            if self.currentFileName is not None:
                # Get current file index
                n_picks_total = 0
                n_sources_total = 0

                # Loop over files in self.fileNames
                for i, _ in enumerate(self.fileNames):
                    # Get the current source
                    source = self.source_position[i]

                    # Loop over uploaded picks
                    if source is not None:

                        # Find the source index in the uploaded stations
                        try:
                            source_index = np.where(np.array(uploaded_stations) == source)[0][0]
                        except IndexError:
                            print(f"Source {source} not found in uploaded_stations")
                            # Handle the case where the source is not found
                            source_index = None  # or any other appropriate action

                        # Find the corresponding picks for the current source
                        up_picks_tmp = [pick for pick in uploaded_picks if pick[0] == source_index + 1]
                
                        # Unpack the picks to get the trace indices, picks and errors
                        trace_indices = [int(pick[1]) - 1 for pick in up_picks_tmp]
                        picks = [pick[2] for pick in up_picks_tmp]
                        errors = [pick[3] for pick in up_picks_tmp]

                        if picks:
                            print(f"{len(picks)} picks loaded for source at {source} m")
                            n_picks_total += len(picks)
                            n_sources_total += 1

                        # Update the picks list
                        if self.picks[i] is None:
                            self.picks[i] = [np.nan] * len(self.trace_position[i])

                        # Access the appropriate attribute based on self.plotTypeX (shot_trace_number, file_trace_number, trace_position)
                        plot_data_x = self.plotTypeDict.get(self.plotTypeX, [])

                        for trace_index_all, pick, error in zip(trace_indices, picks, errors):
                            # Get trace position from uploaded_stations
                            trace = uploaded_stations[trace_index_all][0]
                            # Find the trace index in the current file
                            trace_index_source = np.where(np.array(self.trace_position[i]) == trace)[0][0]

                            scatter1 = pqg.ScatterPlotItem(x=[plot_data_x[i][trace_index_source]], 
                                                          y=[pick], pen='r', symbol='+')

                            if i == self.currentIndex:
                                if ~np.isnan(self.picks[i][trace_index_source]):
                                    self.plotWidget.removeItem(self.pickSeismoItems[i][trace_index_source])
                                
                                self.plotWidget.addItem(scatter1)

                            self.pickSeismoItems[i][trace_index_source] = scatter1
                            self.picks[i][trace_index_source] = pick
                            self.error[i][trace_index_source] = error
                                                                
                print(f'{n_picks_total} picks loaded for {n_sources_total} sources')
                self.plotBottom()

        else:
            self.statusBar.showMessage('No file loaded!', 2000) 

    def clearAllPicks(self):
        # Reset all picks to nan
        for i, _ in enumerate(self.picks):
            if self.picks[i] is not None:
                for j, _ in enumerate(self.picks[i]):
                    self.picks[i][j] = np.nan
                    self.error[i][j] = np.nan
                    if self.pickSeismoItems[i][j] is not None:
                        self.plotWidget.removeItem(self.pickSeismoItems[i][j])
                        self.pickSeismoItems[i][j] = None
        self.plotBottom()

    def clearCurrentPicks(self):
        # Reset picks to nan for the current file
        if self.fileNames:
            if self.picks[self.currentIndex] is not None:
                for i, _ in enumerate(self.picks[self.currentIndex]):
                    self.picks[self.currentIndex][i] = np.nan
                    self.error[self.currentIndex][i] = np.nan
                    if self.pickSeismoItems[self.currentIndex][i] is not None:
                        self.plotWidget.removeItem(self.pickSeismoItems[self.currentIndex][i])
                        self.pickSeismoItems[self.currentIndex][i] = None
            self.plotBottom()
    
    def mplPlotSeismo(self):
        # Plot the seismogram using matplotlib
        aspect_ratio = (10,5)
        show_source = True
        fontsize = 12

        if self.streams:
            # Create a figure and axis
            _, ax = plt.subplots(figsize=aspect_ratio)

            if show_source:
                if self.plotTypeX == 'trace_position':
                    # Display a red star at the source location on the bottom x-axis
                    ax.scatter(self.source_position[self.currentIndex], 0, 
                            color='red', marker='*', s=100, transform=ax.get_xaxis_transform(), clip_on=False)
                else:
                    print('Source position not yet displayed for this plot type')
                
            for i, trace in enumerate(self.streams[self.currentIndex]):
                
                # Get the wiggle info
                x, _, _, _, mask = self.getWiggleInfo(i, trace)

                ax.plot(x, self.time[self.currentIndex], color='k',linewidth=0.5)
                ax.fill_betweenx(self.time[self.currentIndex], self.plotTypeDict[self.plotTypeX][self.currentIndex][i],
                                    x, where=mask, color='k', alpha=0.75, interpolate=True)

            # Access the appropriate attribute based on self.plotTypeX
            plot_data_x = self.plotTypeDict.get(self.plotTypeX, [])

            # Flatten the list of lists into a single list
            flat_plot_data_x = [item for sublist in plot_data_x for item in sublist]
        
            # Set the limits of the x and y axes
            ax.set_xlim(min(flat_plot_data_x) - self.mean_dg, max(flat_plot_data_x) + self.mean_dg)
            ax.set_ylim(min(self.time[self.currentIndex]), self.max_time)

            # Move the x-axis labels to the top
            ax.xaxis.tick_top()
            ax.xaxis.set_label_position('top')
            # Set the font size of the tick labels
            ax.tick_params(axis='both', labelsize=fontsize)
            # Invert the y-axis
            ax.invert_yaxis()  

            # Set the x-axis label and get its position
            ax.set_xlabel(self.x_label, fontsize=fontsize)
            # Set the y-axis label and get its position
            ax.set_ylabel('Time (s)', fontsize=fontsize)

            title = f"FFID: {self.ffid[self.currentIndex]}  |  Source at {self.source_position[self.currentIndex]} m"

            # Set the title
            plt.text(0.025, 0.05, title, fontsize=fontsize, ha='left', va='bottom', weight='bold',
                bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.5'), transform=plt.gca().transAxes)

    def exportSeismoPlot(self):
        # Export the seismogram plot as an image with matplotlib

        # The first argument returned is the filename and path
        fname, _ = QFileDialog.getSaveFileName(
            self, 'Save to file', filter='PNG image (*.png)')
        
        if fname != "":
            # Create figure and axis with matplotlib
            self.mplPlotSeismo()

            # Save the figure
            plt.savefig(fname, dpi=300, bbox_inches='tight')


def main():
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()