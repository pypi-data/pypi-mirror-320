from pyvistaqt import QtInteractor, MainWindow
from PyQt5 import QtCore, QtWidgets, Qt, QtGui, QtWebEngineWidgets
from .Styles import Styles
from .Generator import Generator, WorkerWrapper
from time import perf_counter
import re
import os
from pyvista import Camera

current_dir = os.path.dirname(os.path.abspath(__file__))
instructions_file_path = os.path.join(current_dir, "instructions.html")


class MyMainWindow(MainWindow):

    def __init__(self, userDir, parent=None, show=True):
        QtWidgets.QMainWindow.__init__(self, parent)

        styleSheet = Styles()
        super().setStyleSheet(styleSheet.getStyles())
        self.interactorColor = styleSheet.colors["green"]
        self.grayColor = styleSheet.colors["lightGray"]
        primaryLayout = Qt.QHBoxLayout()
        self.frame = QtWidgets.QFrame()
        self.plotters = []
        self.regen_button = QtWidgets.QPushButton("Generate Parts")
        self.regen_button.clicked.connect(self.regen)
        self.pbar = QtWidgets.QProgressBar(self)
        self.pbar.setFormat("Initialized")
        self.pbar.setValue(100)
        self.generator = Generator(userDir)
        self.generator.signals.progress.connect(self.update_progress)
        self.generator.signals.finished.connect(self.task_finished)
        self.threadpool = QtCore.QThreadPool()
        self.dataValidationCheckBox = QtWidgets.QCheckBox("Data Validation", self)
        self.dataValidationCheckBox.setChecked(True)
        self.dataValidationCheckBox.clicked.connect(self.setDataValidation)

        tab = Qt.QWidget()
        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(self.paramtersPane())
        vbox = QtWidgets.QVBoxLayout()
        time1 = perf_counter()
        vbox.addWidget(self.pbar)
        vbox.addWidget(self.initTilePane())
        vbox.addWidget(self.initPeripheralsPane())
        self.settings = []
        for pl in self.plotters[3:]:
            self.settings.append(pl.camera.copy())
        reset_view = QtWidgets.QPushButton("Reset View")
        reset_view.clicked.connect(self.reset_view)
        vbox.addWidget(reset_view)
        print(f"Initialization time: {perf_counter() - time1}")
        hbox.addLayout(vbox)
        tab.setLayout(hbox)

        tabs = Qt.QTabWidget()
        tabs.addTab(tab, "Generate Tiles")
        tabs.addTab(self.initInstructions(), "Instructions")
        primaryLayout.addWidget(tabs)

        centralWidget = Qt.QWidget(objectName="totalBackground")
        centralWidget.setLayout(primaryLayout)
        self.setCentralWidget(centralWidget)

        if show:
            self.show()

    def initInstructions(self):
        view = QtWebEngineWidgets.QWebEngineView()
        with open(instructions_file_path, "r") as instructions_file:
            view.setHtml(instructions_file.read())
        return view

    def paramtersPane(self):
        self.entryBox = QtWidgets.QScrollArea()
        scroll = QtWidgets.QWidget()

        vbox = QtWidgets.QVBoxLayout()
        vbox.setContentsMargins(20, 20, 40, 20)

        attributes = self.generator.__dict__
        parameter_attributes = {
            "Tile Parameters": [
                "concentricPolygonRadius",
                "tactorRadius",
                "numSides",
                "foamThickness",
                "distanceBetweenMagnetClipAndPolygonEdge",
                "numMangetsInRing",
            ],
            "Magnet Parameters": [
                "magnetRadius",
                "magnetThickness",
            ],
            "Clip Parameters": [
                "slotWidth",
                "slotHeight",
                "slotBorderRadius",
                "magnetRingRadius",
                "magnetClipThickness",
                "magnetClipRingThickness",
                "distanceBetweenMagnetsInClip",
                "distanceBetweenMagnetClipAndSlot",
            ],
        }

        unitless = ["numMangetsInRing", "numSides"]
        for header, params in parameter_attributes.items():
            header = QtWidgets.QLabel(header, objectName="parameterHeader")
            header.setAlignment(QtCore.Qt.AlignLeft)
            vbox.addWidget(header)
            for attributeKey in params:
                attributeVal = attributes[attributeKey]
                hbox = QtWidgets.QHBoxLayout()
                formattedAttributeName = re.sub(
                    r"(?<!^)(?=[A-Z])", " ", attributeKey
                ).title()
                if attributeKey not in unitless:
                    formattedAttributeName += " (mm)"
                label = QtWidgets.QLabel(formattedAttributeName)
                if attributeKey == "numSides" or attributeKey == "numMagnetsInRing":
                    le = QtWidgets.QLineEdit()
                    le.setValidator(
                        QtGui.QRegularExpressionValidator(
                            QtCore.QRegularExpression("^\d+$")
                        )
                    )
                    le.setText(str(attributeVal))
                else:
                    le = QtWidgets.QLineEdit()
                    le.setValidator(
                        QtGui.QRegularExpressionValidator(
                            QtCore.QRegularExpression("^\d+(\.\d+)?$")
                        )
                    )
                    le.setText(str(attributeVal))
                le.textChanged.connect(
                    lambda value, attributeKey=attributeKey: self.setGeneratorAttribute(
                        attributeKey, value
                    )
                )
                hbox.addWidget(label)
                hbox.addWidget(le)
                vbox.addLayout(hbox)

        vbox.addWidget(self.dataValidationCheckBox)
        vbox.addWidget(self.regen_button)
        label = QtWidgets.QLabel(self)
        pixmap = QtGui.QPixmap("haptic_harness_generator/anatomyOfTile.jpg")
        scaled_pixmap = pixmap.scaledToWidth(
            self.entryBox.width(), mode=QtCore.Qt.SmoothTransformation
        )
        label.setPixmap(scaled_pixmap)
        vbox.addWidget(label)

        scroll.setLayout(vbox)
        self.entryBox.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.entryBox.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.entryBox.setWidgetResizable(True)
        self.entryBox.setWidget(scroll)
        self.entryBox.setFixedWidth(scroll.width())
        return self.entryBox

    def initTilePane(self):
        interactors_layout = QtWidgets.QHBoxLayout()
        labels = ["Tyvek Tile", "Foam Liner", "Magnetic Ring"]
        for i in range(3):
            section = QtWidgets.QVBoxLayout()
            interactor = QtInteractor(self.frame)
            interactor.disable()
            self.plotters.append(interactor)
            label = QtWidgets.QLabel(labels[i], objectName="sectionHeader")
            label.setAlignment(QtCore.Qt.AlignCenter)
            section.addWidget(label)
            section.addWidget(self.plotters[i].interactor)
            frame = Qt.QFrame(objectName="sectionFrame")
            frame.setFrameShape(Qt.QFrame.StyledPanel)
            frame.setLayout(section)
            interactors_layout.addWidget(frame)

        self.plotters[0].add_mesh(
            self.generator.tyvek_tile,
            show_edges=True,
            line_width=3,
            color=self.interactorColor,
        )
        self.plotters[1].add_mesh(
            self.generator.foam,
            show_edges=True,
            line_width=3,
            color=self.interactorColor,
        )
        self.plotters[2].add_mesh(
            self.generator.magnet_ring,
            show_edges=True,
            line_width=3,
            color=self.interactorColor,
        )

        frame = Qt.QFrame(objectName="sectionFrame")
        frame.setFrameShape(Qt.QFrame.StyledPanel)
        frame.setLayout(interactors_layout)
        return frame

    def reset_view(self):
        for i in range(3):
            self.plotters[i + 3].camera = self.settings[i].copy()

    def initPeripheralsPane(self):
        plotLayout = Qt.QHBoxLayout()

        section = QtWidgets.QVBoxLayout()
        self.plotters.append(QtInteractor(self.frame))
        label = QtWidgets.QLabel("Base", objectName="sectionHeader")
        label.setAlignment(QtCore.Qt.AlignCenter)
        section.addWidget(label)
        section.addWidget(self.plotters[3].interactor)
        frame = Qt.QFrame(objectName="sectionFrame")
        frame.setFrameShape(Qt.QFrame.StyledPanel)
        frame.setLayout(section)
        plotLayout.addWidget(frame)
        self.plotters[3].add_mesh(self.generator.base, color=self.interactorColor)
        self.plotters[3].add_logo_widget(
            "haptic_harness_generator/rotateIcon.png",
            position=(0.05, 0.05),
            size=(0.1, 0.1),
        )

        section = QtWidgets.QVBoxLayout()
        self.plotters.append(QtInteractor(self.frame))
        label = QtWidgets.QLabel("Bottom Clip", objectName="sectionHeader")
        label.setAlignment(QtCore.Qt.AlignCenter)
        section.addWidget(label)
        section.addWidget(self.plotters[4].interactor)
        frame = Qt.QFrame(objectName="sectionFrame")
        frame.setFrameShape(Qt.QFrame.StyledPanel)
        frame.setLayout(section)
        plotLayout.addWidget(frame)
        self.plotters[4].add_mesh(
            self.generator.bottom_clip, color=self.interactorColor
        )
        self.plotters[4].add_logo_widget(
            "haptic_harness_generator/rotateIcon.png",
            position=(0.05, 0.05),
            size=(0.1, 0.1),
        )

        section = QtWidgets.QVBoxLayout()
        self.plotters.append(QtInteractor(self.frame))
        label = QtWidgets.QLabel("Top Clip", objectName="sectionHeader")
        label.setAlignment(QtCore.Qt.AlignCenter)
        section.addWidget(label)
        section.addWidget(self.plotters[5].interactor)
        frame = Qt.QFrame(objectName="sectionFrame")
        frame.setFrameShape(Qt.QFrame.StyledPanel)
        frame.setLayout(section)
        plotLayout.addWidget(frame)
        self.plotters[5].add_mesh(self.generator.top_clip, color=self.interactorColor)
        self.plotters[5].add_logo_widget(
            "haptic_harness_generator/rotateIcon.png",
            position=(0.05, 0.05),
            size=(0.1, 0.1),
        )

        frame = Qt.QFrame(objectName="sectionFrame")
        frame.setFrameShape(Qt.QFrame.StyledPanel)
        frame.setLayout(plotLayout)
        return frame

    def setGeneratorAttribute(self, attrName, val):
        self.generator.customSetAttr(attrName=attrName, val=val)
        self.grayOutPlotters()
        self.pbar.setValue(0)
        self.pbar.setFormat("Ready to Generate")

    def grayOutPlotters(self):
        opacity = 0.7
        self.plotters[0].clear_actors()
        self.plotters[0].add_mesh(
            self.generator.tyvek_tile,
            show_edges=True,
            line_width=3,
            opacity=opacity,
            color=self.grayColor,
        )
        self.plotters[1].clear_actors()
        self.plotters[1].add_mesh(
            self.generator.foam,
            show_edges=True,
            line_width=3,
            opacity=opacity,
            color=self.grayColor,
        )
        self.plotters[2].clear_actors()
        self.plotters[2].add_mesh(
            self.generator.magnet_ring,
            show_edges=True,
            line_width=3,
            opacity=opacity,
            color=self.grayColor,
        )

        self.plotters[3].clear_actors()
        self.plotters[3].add_mesh(
            self.generator.base, color=self.grayColor, opacity=opacity
        )

        self.plotters[4].clear_actors()
        self.plotters[4].add_mesh(
            self.generator.bottom_clip, color=self.grayColor, opacity=opacity
        )

        self.plotters[5].clear_actors()
        self.plotters[5].add_mesh(
            self.generator.top_clip, color=self.grayColor, opacity=opacity
        )

    def setDataValidation(self, state):
        if not self.dataValidationCheckBox.isChecked():
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Critical)
            msg.setText(
                "Turning off data validation may lead to incompatible geometry, which may crash the program"
            )
            msg.setWindowTitle("Validation Error")
            msg.setStandardButtons(
                QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel
            )
            retval = msg.exec_()
            if retval == QtWidgets.QMessageBox.Ok:
                self.dataValidationCheckBox.setChecked(False)
            elif retval == QtWidgets.QMessageBox.Cancel:
                self.dataValidationCheckBox.setChecked(True)

    def update_progress(self, value):
        progress_labels = {
            1: "Generating tyvek tile",
            2: "Generating foam",
            3: "Generating magnet ring",
            4: "Generating base",
            5: "Generating bottom clip",
            6: "Generating top clip",
            7: "Generation complete",
        }
        self.pbar.setValue(value / len(progress_labels) * 100)
        self.pbar.setFormat(progress_labels[value])

    def task_finished(self):
        self.regen_button.setEnabled(True)
        self.regen_button.setStyleSheet("background-color: #333333")
        self.plotters[0].clear_actors()
        self.plotters[0].add_mesh(
            self.generator.tyvek_tile,
            show_edges=True,
            line_width=3,
            color=self.interactorColor,
        )
        self.plotters[1].clear_actors()
        self.plotters[1].add_mesh(
            self.generator.foam,
            show_edges=True,
            line_width=3,
            color=self.interactorColor,
        )
        self.plotters[2].clear_actors()
        self.plotters[2].add_mesh(
            self.generator.magnet_ring,
            show_edges=True,
            line_width=3,
            color=self.interactorColor,
        )

        self.plotters[3].clear_actors()
        self.plotters[3].add_mesh(self.generator.base, color=self.interactorColor)

        self.plotters[4].clear_actors()
        self.plotters[4].add_mesh(
            self.generator.bottom_clip, color=self.interactorColor
        )

        self.plotters[5].clear_actors()
        self.plotters[5].add_mesh(self.generator.top_clip, color=self.interactorColor)

    def regen(self):
        messages = []
        if self.dataValidationCheckBox.isChecked():
            messages = self.generator.validate()
        if len(messages) == 0:
            self.regen_button.setEnabled(False)
            self.regen_button.setStyleSheet("background-color: #777777")
            self.threadpool.start(WorkerWrapper(self.generator))
        else:
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Critical)
            msg.setText("\n\n".join(messages))
            msg.setWindowTitle("Validation Error")
            msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
            retval = msg.exec_()
