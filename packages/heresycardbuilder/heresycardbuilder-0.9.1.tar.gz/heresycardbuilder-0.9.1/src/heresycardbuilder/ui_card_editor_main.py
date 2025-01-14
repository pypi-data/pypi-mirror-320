# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'card_editor_main.ui'
##
## Created by: Qt User Interface Compiler version 6.8.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QComboBox, QDockWidget,
    QDoubleSpinBox, QGridLayout, QHBoxLayout, QHeaderView,
    QLabel, QLineEdit, QListWidget, QListWidgetItem,
    QMainWindow, QMenu, QMenuBar, QPushButton,
    QSizePolicy, QSpacerItem, QSpinBox, QSplitter,
    QStackedWidget, QStatusBar, QToolBar, QTreeWidgetItem,
    QVBoxLayout, QWidget)

from spelltextedit import SpellTextEdit
from view_widgets import (AssetTreeWidget, CardTreeWidget)
import card_editor_res_rc

class Ui_card_editor_main(object):
    def setupUi(self, card_editor_main):
        if not card_editor_main.objectName():
            card_editor_main.setObjectName(u"card_editor_main")
        card_editor_main.resize(1218, 763)
        icon = QIcon()
        icon.addFile(u"media/TS_CreaPack_Icon_-1-.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        card_editor_main.setWindowIcon(icon)
        self.actionQuit = QAction(card_editor_main)
        self.actionQuit.setObjectName(u"actionQuit")
        self.actionAbout = QAction(card_editor_main)
        self.actionAbout.setObjectName(u"actionAbout")
        self.actionNew = QAction(card_editor_main)
        self.actionNew.setObjectName(u"actionNew")
        self.actionLoad = QAction(card_editor_main)
        self.actionLoad.setObjectName(u"actionLoad")
        icon1 = QIcon()
        icon1.addFile(u":/images/file_open", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.actionLoad.setIcon(icon1)
        self.actionSave = QAction(card_editor_main)
        self.actionSave.setObjectName(u"actionSave")
        icon2 = QIcon()
        icon2.addFile(u":/images/file_save", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.actionSave.setIcon(icon2)
        self.actionSaveAs = QAction(card_editor_main)
        self.actionSaveAs.setObjectName(u"actionSaveAs")
        self.actionFrontFace = QAction(card_editor_main)
        self.actionFrontFace.setObjectName(u"actionFrontFace")
        self.actionFrontFace.setCheckable(True)
        icon3 = QIcon()
        icon3.addFile(u":/images/ui_face_off", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        icon3.addFile(u":/images/ui_face_on", QSize(), QIcon.Mode.Normal, QIcon.State.On)
        self.actionFrontFace.setIcon(icon3)
        self.actionZoomIn = QAction(card_editor_main)
        self.actionZoomIn.setObjectName(u"actionZoomIn")
        self.actionZoomIn.setCheckable(False)
        icon4 = QIcon()
        icon4.addFile(u":/images/ui_zoom_in", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.actionZoomIn.setIcon(icon4)
        self.actionZoomReset = QAction(card_editor_main)
        self.actionZoomReset.setObjectName(u"actionZoomReset")
        self.actionZoomReset.setCheckable(False)
        icon5 = QIcon()
        icon5.addFile(u":/images/ui_zoom_reset", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.actionZoomReset.setIcon(icon5)
        self.actionZoomOut = QAction(card_editor_main)
        self.actionZoomOut.setObjectName(u"actionZoomOut")
        self.actionZoomOut.setCheckable(False)
        icon6 = QIcon()
        icon6.addFile(u":/images/ui_zoom_out", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.actionZoomOut.setIcon(icon6)
        self.action100 = QAction(card_editor_main)
        self.action100.setObjectName(u"action100")
        self.action100.setCheckable(True)
        self.action100.setChecked(True)
        self.action125 = QAction(card_editor_main)
        self.action125.setObjectName(u"action125")
        self.action125.setCheckable(True)
        self.action150 = QAction(card_editor_main)
        self.action150.setObjectName(u"action150")
        self.action150.setCheckable(True)
        self.action175 = QAction(card_editor_main)
        self.action175.setObjectName(u"action175")
        self.action175.setCheckable(True)
        self.centralwidget = QWidget(card_editor_main)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout_3 = QVBoxLayout(self.centralwidget)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.lblInfo = QLabel(self.centralwidget)
        self.lblInfo.setObjectName(u"lblInfo")

        self.verticalLayout_3.addWidget(self.lblInfo)

        self.wCardView = QWidget(self.centralwidget)
        self.wCardView.setObjectName(u"wCardView")

        self.verticalLayout_3.addWidget(self.wCardView)

        self.verticalLayout_3.setStretch(1, 10)
        card_editor_main.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(card_editor_main)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1218, 21))
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName(u"menuFile")
        self.menuHelp = QMenu(self.menubar)
        self.menuHelp.setObjectName(u"menuHelp")
        self.menuView = QMenu(self.menubar)
        self.menuView.setObjectName(u"menuView")
        self.menuCard_zoom = QMenu(self.menuView)
        self.menuCard_zoom.setObjectName(u"menuCard_zoom")
        card_editor_main.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(card_editor_main)
        self.statusbar.setObjectName(u"statusbar")
        card_editor_main.setStatusBar(self.statusbar)
        self.dwCards = QDockWidget(card_editor_main)
        self.dwCards.setObjectName(u"dwCards")
        self.dockWidgetContents = QWidget()
        self.dockWidgetContents.setObjectName(u"dockWidgetContents")
        self.verticalLayout_6 = QVBoxLayout(self.dockWidgetContents)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.splitter_2 = QSplitter(self.dockWidgetContents)
        self.splitter_2.setObjectName(u"splitter_2")
        self.splitter_2.setOrientation(Qt.Vertical)
        self.twCards = CardTreeWidget(self.splitter_2)
        __qtreewidgetitem = QTreeWidgetItem()
        __qtreewidgetitem.setText(0, u"Name");
        self.twCards.setHeaderItem(__qtreewidgetitem)
        self.twCards.setObjectName(u"twCards")
        self.twCards.setContextMenuPolicy(Qt.CustomContextMenu)
        self.twCards.setDragEnabled(True)
        self.twCards.setDragDropMode(QAbstractItemView.InternalMove)
        self.twCards.setAlternatingRowColors(True)
        self.twCards.setRootIsDecorated(True)
        self.twCards.setUniformRowHeights(True)
        self.twCards.setColumnCount(1)
        self.splitter_2.addWidget(self.twCards)
        self.twCards.header().setVisible(True)
        self.lwGfxItems = QListWidget(self.splitter_2)
        self.lwGfxItems.setObjectName(u"lwGfxItems")
        self.splitter_2.addWidget(self.lwGfxItems)
        self.swGfxItemProps = QStackedWidget(self.splitter_2)
        self.swGfxItemProps.setObjectName(u"swGfxItemProps")
        self.pg_none = QWidget()
        self.pg_none.setObjectName(u"pg_none")
        self.swGfxItemProps.addWidget(self.pg_none)
        self.pg_render_image = QWidget()
        self.pg_render_image.setObjectName(u"pg_render_image")
        self.verticalLayout = QVBoxLayout(self.pg_render_image)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.label_2 = QLabel(self.pg_render_image)
        self.label_2.setObjectName(u"label_2")

        self.verticalLayout.addWidget(self.label_2)

        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.label = QLabel(self.pg_render_image)
        self.label.setObjectName(u"label")

        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)

        self.label_5 = QLabel(self.pg_render_image)
        self.label_5.setObjectName(u"label_5")

        self.gridLayout.addWidget(self.label_5, 1, 0, 1, 1)

        self.label_6 = QLabel(self.pg_render_image)
        self.label_6.setObjectName(u"label_6")

        self.gridLayout.addWidget(self.label_6, 2, 0, 1, 1)

        self.dsImageR = QDoubleSpinBox(self.pg_render_image)
        self.dsImageR.setObjectName(u"dsImageR")
        self.dsImageR.setDecimals(0)
        self.dsImageR.setMaximum(360.000000000000000)
        self.dsImageR.setSingleStep(10.000000000000000)

        self.gridLayout.addWidget(self.dsImageR, 2, 1, 1, 1)

        self.sbImageY = QSpinBox(self.pg_render_image)
        self.sbImageY.setObjectName(u"sbImageY")
        self.sbImageY.setMaximum(5000)
        self.sbImageY.setSingleStep(10)

        self.gridLayout.addWidget(self.sbImageY, 0, 3, 1, 1)

        self.sbImageH = QSpinBox(self.pg_render_image)
        self.sbImageH.setObjectName(u"sbImageH")
        self.sbImageH.setMinimum(-1)
        self.sbImageH.setMaximum(5000)
        self.sbImageH.setSingleStep(10)

        self.gridLayout.addWidget(self.sbImageH, 1, 3, 1, 1)

        self.sbImageX = QSpinBox(self.pg_render_image)
        self.sbImageX.setObjectName(u"sbImageX")
        self.sbImageX.setMaximum(5000)
        self.sbImageX.setSingleStep(10)

        self.gridLayout.addWidget(self.sbImageX, 0, 1, 1, 1)

        self.sbImageW = QSpinBox(self.pg_render_image)
        self.sbImageW.setObjectName(u"sbImageW")
        self.sbImageW.setMinimum(-1)
        self.sbImageW.setMaximum(5000)
        self.sbImageW.setSingleStep(10)

        self.gridLayout.addWidget(self.sbImageW, 1, 1, 1, 1)


        self.verticalLayout.addLayout(self.gridLayout)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label_7 = QLabel(self.pg_render_image)
        self.label_7.setObjectName(u"label_7")

        self.horizontalLayout.addWidget(self.label_7)

        self.cbImageImage = QComboBox(self.pg_render_image)
        self.cbImageImage.setObjectName(u"cbImageImage")

        self.horizontalLayout.addWidget(self.cbImageImage)

        self.horizontalLayout.setStretch(1, 10)

        self.verticalLayout.addLayout(self.horizontalLayout)

        self.verticalSpacer_2 = QSpacerItem(20, 190, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer_2)

        self.swGfxItemProps.addWidget(self.pg_render_image)
        self.pg_render_text = QWidget()
        self.pg_render_text.setObjectName(u"pg_render_text")
        self.verticalLayout_5 = QVBoxLayout(self.pg_render_text)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.label_3 = QLabel(self.pg_render_text)
        self.label_3.setObjectName(u"label_3")

        self.verticalLayout_5.addWidget(self.label_3)

        self.gridLayout_2 = QGridLayout()
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.label_8 = QLabel(self.pg_render_text)
        self.label_8.setObjectName(u"label_8")

        self.gridLayout_2.addWidget(self.label_8, 0, 0, 1, 1)

        self.label_9 = QLabel(self.pg_render_text)
        self.label_9.setObjectName(u"label_9")

        self.gridLayout_2.addWidget(self.label_9, 1, 0, 1, 1)

        self.label_10 = QLabel(self.pg_render_text)
        self.label_10.setObjectName(u"label_10")

        self.gridLayout_2.addWidget(self.label_10, 2, 0, 1, 1)

        self.dsTextR = QDoubleSpinBox(self.pg_render_text)
        self.dsTextR.setObjectName(u"dsTextR")
        self.dsTextR.setDecimals(0)
        self.dsTextR.setMaximum(360.000000000000000)
        self.dsTextR.setSingleStep(10.000000000000000)

        self.gridLayout_2.addWidget(self.dsTextR, 2, 1, 1, 1)

        self.sbTextY = QSpinBox(self.pg_render_text)
        self.sbTextY.setObjectName(u"sbTextY")
        self.sbTextY.setMaximum(5000)
        self.sbTextY.setSingleStep(10)

        self.gridLayout_2.addWidget(self.sbTextY, 0, 3, 1, 1)

        self.sbTextH = QSpinBox(self.pg_render_text)
        self.sbTextH.setObjectName(u"sbTextH")
        self.sbTextH.setMinimum(-1)
        self.sbTextH.setMaximum(5000)
        self.sbTextH.setSingleStep(10)

        self.gridLayout_2.addWidget(self.sbTextH, 1, 3, 1, 1)

        self.sbTextW = QSpinBox(self.pg_render_text)
        self.sbTextW.setObjectName(u"sbTextW")
        self.sbTextW.setMinimum(-1)
        self.sbTextW.setMaximum(5000)
        self.sbTextW.setSingleStep(10)

        self.gridLayout_2.addWidget(self.sbTextW, 1, 1, 1, 1)

        self.sbTextX = QSpinBox(self.pg_render_text)
        self.sbTextX.setObjectName(u"sbTextX")
        self.sbTextX.setMaximum(5000)
        self.sbTextX.setSingleStep(10)

        self.gridLayout_2.addWidget(self.sbTextX, 0, 1, 1, 1)


        self.verticalLayout_5.addLayout(self.gridLayout_2)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label_14 = QLabel(self.pg_render_text)
        self.label_14.setObjectName(u"label_14")

        self.horizontalLayout_2.addWidget(self.label_14)

        self.cbTextStyle = QComboBox(self.pg_render_text)
        self.cbTextStyle.setObjectName(u"cbTextStyle")

        self.horizontalLayout_2.addWidget(self.cbTextStyle)

        self.horizontalLayout_2.setStretch(1, 10)

        self.verticalLayout_5.addLayout(self.horizontalLayout_2)

        self.leTextText = SpellTextEdit(self.pg_render_text)
        self.leTextText.setObjectName(u"leTextText")

        self.verticalLayout_5.addWidget(self.leTextText)

        self.swGfxItemProps.addWidget(self.pg_render_text)
        self.pg_render_rect = QWidget()
        self.pg_render_rect.setObjectName(u"pg_render_rect")
        self.verticalLayout_2 = QVBoxLayout(self.pg_render_rect)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.label_4 = QLabel(self.pg_render_rect)
        self.label_4.setObjectName(u"label_4")

        self.verticalLayout_2.addWidget(self.label_4)

        self.gridLayout_3 = QGridLayout()
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.label_12 = QLabel(self.pg_render_rect)
        self.label_12.setObjectName(u"label_12")

        self.gridLayout_3.addWidget(self.label_12, 1, 0, 1, 1)

        self.label_11 = QLabel(self.pg_render_rect)
        self.label_11.setObjectName(u"label_11")

        self.gridLayout_3.addWidget(self.label_11, 0, 0, 1, 1)

        self.label_13 = QLabel(self.pg_render_rect)
        self.label_13.setObjectName(u"label_13")

        self.gridLayout_3.addWidget(self.label_13, 2, 0, 1, 1)

        self.dsRectR = QDoubleSpinBox(self.pg_render_rect)
        self.dsRectR.setObjectName(u"dsRectR")
        self.dsRectR.setDecimals(0)
        self.dsRectR.setMaximum(360.000000000000000)
        self.dsRectR.setSingleStep(10.000000000000000)

        self.gridLayout_3.addWidget(self.dsRectR, 2, 1, 1, 1)

        self.sbRectY = QSpinBox(self.pg_render_rect)
        self.sbRectY.setObjectName(u"sbRectY")
        self.sbRectY.setMaximum(5000)
        self.sbRectY.setSingleStep(10)

        self.gridLayout_3.addWidget(self.sbRectY, 0, 3, 1, 1)

        self.sbRectH = QSpinBox(self.pg_render_rect)
        self.sbRectH.setObjectName(u"sbRectH")
        self.sbRectH.setMinimum(-1)
        self.sbRectH.setMaximum(5000)
        self.sbRectH.setSingleStep(10)

        self.gridLayout_3.addWidget(self.sbRectH, 1, 3, 1, 1)

        self.sbRectW = QSpinBox(self.pg_render_rect)
        self.sbRectW.setObjectName(u"sbRectW")
        self.sbRectW.setMinimum(-1)
        self.sbRectW.setMaximum(5000)
        self.sbRectW.setSingleStep(10)

        self.gridLayout_3.addWidget(self.sbRectW, 1, 1, 1, 1)

        self.sbRectX = QSpinBox(self.pg_render_rect)
        self.sbRectX.setObjectName(u"sbRectX")
        self.sbRectX.setMaximum(5000)
        self.sbRectX.setSingleStep(10)

        self.gridLayout_3.addWidget(self.sbRectX, 0, 1, 1, 1)


        self.verticalLayout_2.addLayout(self.gridLayout_3)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.label_15 = QLabel(self.pg_render_rect)
        self.label_15.setObjectName(u"label_15")

        self.horizontalLayout_3.addWidget(self.label_15)

        self.cbRectStyle = QComboBox(self.pg_render_rect)
        self.cbRectStyle.setObjectName(u"cbRectStyle")

        self.horizontalLayout_3.addWidget(self.cbRectStyle)

        self.horizontalLayout_3.setStretch(1, 10)

        self.verticalLayout_2.addLayout(self.horizontalLayout_3)

        self.verticalSpacer_3 = QSpacerItem(20, 190, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer_3)

        self.swGfxItemProps.addWidget(self.pg_render_rect)
        self.splitter_2.addWidget(self.swGfxItemProps)

        self.verticalLayout_6.addWidget(self.splitter_2)

        self.dwCards.setWidget(self.dockWidgetContents)
        card_editor_main.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.dwCards)
        self.dwAssets = QDockWidget(card_editor_main)
        self.dwAssets.setObjectName(u"dwAssets")
        self.dockWidgetContents_3 = QWidget()
        self.dockWidgetContents_3.setObjectName(u"dockWidgetContents_3")
        self.verticalLayout_8 = QVBoxLayout(self.dockWidgetContents_3)
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.splitter = QSplitter(self.dockWidgetContents_3)
        self.splitter.setObjectName(u"splitter")
        self.splitter.setOrientation(Qt.Vertical)
        self.twAssets = AssetTreeWidget(self.splitter)
        __qtreewidgetitem1 = QTreeWidgetItem()
        __qtreewidgetitem1.setText(0, u"Name");
        self.twAssets.setHeaderItem(__qtreewidgetitem1)
        self.twAssets.setObjectName(u"twAssets")
        self.twAssets.setContextMenuPolicy(Qt.CustomContextMenu)
        self.twAssets.setAcceptDrops(False)
        self.twAssets.setDragEnabled(True)
        self.twAssets.setDragDropMode(QAbstractItemView.InternalMove)
        self.twAssets.setAlternatingRowColors(True)
        self.twAssets.setRootIsDecorated(True)
        self.twAssets.setUniformRowHeights(True)
        self.twAssets.setColumnCount(1)
        self.splitter.addWidget(self.twAssets)
        self.twAssets.header().setVisible(True)
        self.swAssetProps = QStackedWidget(self.splitter)
        self.swAssetProps.setObjectName(u"swAssetProps")
        self.pgnone = QWidget()
        self.pgnone.setObjectName(u"pgnone")
        self.swAssetProps.addWidget(self.pgnone)
        self.pgimage = QWidget()
        self.pgimage.setObjectName(u"pgimage")
        self.verticalLayout_4 = QVBoxLayout(self.pgimage)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.lblImgAssetName = QLabel(self.pgimage)
        self.lblImgAssetName.setObjectName(u"lblImgAssetName")

        self.verticalLayout_4.addWidget(self.lblImgAssetName)

        self.horizontalLayout_7 = QHBoxLayout()
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.lblImgAssetFile = QLabel(self.pgimage)
        self.lblImgAssetFile.setObjectName(u"lblImgAssetFile")

        self.horizontalLayout_7.addWidget(self.lblImgAssetFile)

        self.cbImgAssetFile = QComboBox(self.pgimage)
        self.cbImgAssetFile.setObjectName(u"cbImgAssetFile")

        self.horizontalLayout_7.addWidget(self.cbImgAssetFile)

        self.horizontalLayout_7.setStretch(1, 10)

        self.verticalLayout_4.addLayout(self.horizontalLayout_7)

        self.gridLayout_4 = QGridLayout()
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.leImgAssetY = QLineEdit(self.pgimage)
        self.leImgAssetY.setObjectName(u"leImgAssetY")

        self.gridLayout_4.addWidget(self.leImgAssetY, 0, 2, 1, 1)

        self.leImgAssetX = QLineEdit(self.pgimage)
        self.leImgAssetX.setObjectName(u"leImgAssetX")

        self.gridLayout_4.addWidget(self.leImgAssetX, 0, 1, 1, 1)

        self.leImgAssetW = QLineEdit(self.pgimage)
        self.leImgAssetW.setObjectName(u"leImgAssetW")

        self.gridLayout_4.addWidget(self.leImgAssetW, 1, 1, 1, 1)

        self.label_16 = QLabel(self.pgimage)
        self.label_16.setObjectName(u"label_16")

        self.gridLayout_4.addWidget(self.label_16, 0, 0, 1, 1)

        self.leImgAssetH = QLineEdit(self.pgimage)
        self.leImgAssetH.setObjectName(u"leImgAssetH")

        self.gridLayout_4.addWidget(self.leImgAssetH, 1, 2, 1, 1)

        self.label_17 = QLabel(self.pgimage)
        self.label_17.setObjectName(u"label_17")

        self.gridLayout_4.addWidget(self.label_17, 1, 0, 1, 1)


        self.verticalLayout_4.addLayout(self.gridLayout_4)

        self.lbImgAssetImage = QLabel(self.pgimage)
        self.lbImgAssetImage.setObjectName(u"lbImgAssetImage")
        self.lbImgAssetImage.setScaledContents(False)

        self.verticalLayout_4.addWidget(self.lbImgAssetImage)

        self.label_21 = QLabel(self.pgimage)
        self.label_21.setObjectName(u"label_21")

        self.verticalLayout_4.addWidget(self.label_21)

        self.lbImgAssetFile = QLabel(self.pgimage)
        self.lbImgAssetFile.setObjectName(u"lbImgAssetFile")

        self.verticalLayout_4.addWidget(self.lbImgAssetFile)

        self.verticalSpacer_4 = QSpacerItem(20, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_4.addItem(self.verticalSpacer_4)

        self.swAssetProps.addWidget(self.pgimage)
        self.pgfile = QWidget()
        self.pgfile.setObjectName(u"pgfile")
        self.verticalLayout_7 = QVBoxLayout(self.pgfile)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.lblFileName = QLabel(self.pgfile)
        self.lblFileName.setObjectName(u"lblFileName")

        self.verticalLayout_7.addWidget(self.lblFileName)

        self.lblFileFilename = QLabel(self.pgfile)
        self.lblFileFilename.setObjectName(u"lblFileFilename")

        self.verticalLayout_7.addWidget(self.lblFileFilename)

        self.pbSelectFile = QPushButton(self.pgfile)
        self.pbSelectFile.setObjectName(u"pbSelectFile")

        self.verticalLayout_7.addWidget(self.pbSelectFile)

        self.lblFileSize = QLabel(self.pgfile)
        self.lblFileSize.setObjectName(u"lblFileSize")

        self.verticalLayout_7.addWidget(self.lblFileSize)

        self.lblFileImage = QLabel(self.pgfile)
        self.lblFileImage.setObjectName(u"lblFileImage")

        self.verticalLayout_7.addWidget(self.lblFileImage)

        self.verticalSpacer = QSpacerItem(20, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_7.addItem(self.verticalSpacer)

        self.swAssetProps.addWidget(self.pgfile)
        self.pgstyle = QWidget()
        self.pgstyle.setObjectName(u"pgstyle")
        self.verticalLayout_9 = QVBoxLayout(self.pgstyle)
        self.verticalLayout_9.setObjectName(u"verticalLayout_9")
        self.lblStyleName = QLabel(self.pgstyle)
        self.lblStyleName.setObjectName(u"lblStyleName")

        self.verticalLayout_9.addWidget(self.lblStyleName)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.label_18 = QLabel(self.pgstyle)
        self.label_18.setObjectName(u"label_18")

        self.horizontalLayout_4.addWidget(self.label_18)

        self.lblStyleTypeface = QLabel(self.pgstyle)
        self.lblStyleTypeface.setObjectName(u"lblStyleTypeface")

        self.horizontalLayout_4.addWidget(self.lblStyleTypeface)

        self.lblStyleSize = QLabel(self.pgstyle)
        self.lblStyleSize.setObjectName(u"lblStyleSize")

        self.horizontalLayout_4.addWidget(self.lblStyleSize)

        self.horizontalSpacer_4 = QSpacerItem(13, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer_4)


        self.verticalLayout_9.addLayout(self.horizontalLayout_4)

        self.pushButton = QPushButton(self.pgstyle)
        self.pushButton.setObjectName(u"pushButton")

        self.verticalLayout_9.addWidget(self.pushButton)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.label_19 = QLabel(self.pgstyle)
        self.label_19.setObjectName(u"label_19")

        self.horizontalLayout_5.addWidget(self.label_19)

        self.pbStyleFillcolor = QPushButton(self.pgstyle)
        self.pbStyleFillcolor.setObjectName(u"pbStyleFillcolor")

        self.horizontalLayout_5.addWidget(self.pbStyleFillcolor)

        self.horizontalSpacer_5 = QSpacerItem(13, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_5.addItem(self.horizontalSpacer_5)


        self.verticalLayout_9.addLayout(self.horizontalLayout_5)

        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.label_20 = QLabel(self.pgstyle)
        self.label_20.setObjectName(u"label_20")

        self.horizontalLayout_6.addWidget(self.label_20)

        self.sbStyleBorderthickness = QSpinBox(self.pgstyle)
        self.sbStyleBorderthickness.setObjectName(u"sbStyleBorderthickness")
        self.sbStyleBorderthickness.setMinimum(1)
        self.sbStyleBorderthickness.setMaximum(20)

        self.horizontalLayout_6.addWidget(self.sbStyleBorderthickness)

        self.horizontalSpacer_6 = QSpacerItem(13, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_6.addItem(self.horizontalSpacer_6)


        self.verticalLayout_9.addLayout(self.horizontalLayout_6)

        self.horizontalLayout_8 = QHBoxLayout()
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.label_22 = QLabel(self.pgstyle)
        self.label_22.setObjectName(u"label_22")

        self.horizontalLayout_8.addWidget(self.label_22)

        self.pbStyleBordercolor = QPushButton(self.pgstyle)
        self.pbStyleBordercolor.setObjectName(u"pbStyleBordercolor")

        self.horizontalLayout_8.addWidget(self.pbStyleBordercolor)

        self.horizontalSpacer_8 = QSpacerItem(13, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_8.addItem(self.horizontalSpacer_8)


        self.verticalLayout_9.addLayout(self.horizontalLayout_8)

        self.horizontalLayout_9 = QHBoxLayout()
        self.horizontalLayout_9.setObjectName(u"horizontalLayout_9")
        self.label_23 = QLabel(self.pgstyle)
        self.label_23.setObjectName(u"label_23")

        self.horizontalLayout_9.addWidget(self.label_23)

        self.pbStyleTextcolor = QPushButton(self.pgstyle)
        self.pbStyleTextcolor.setObjectName(u"pbStyleTextcolor")

        self.horizontalLayout_9.addWidget(self.pbStyleTextcolor)

        self.horizontalSpacer_9 = QSpacerItem(13, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_9.addItem(self.horizontalSpacer_9)


        self.verticalLayout_9.addLayout(self.horizontalLayout_9)

        self.horizontalLayout_10 = QHBoxLayout()
        self.horizontalLayout_10.setObjectName(u"horizontalLayout_10")
        self.label_24 = QLabel(self.pgstyle)
        self.label_24.setObjectName(u"label_24")

        self.horizontalLayout_10.addWidget(self.label_24)

        self.cbStyleLinestyle = QComboBox(self.pgstyle)
        self.cbStyleLinestyle.addItem("")
        self.cbStyleLinestyle.addItem("")
        self.cbStyleLinestyle.addItem("")
        self.cbStyleLinestyle.addItem("")
        self.cbStyleLinestyle.addItem("")
        self.cbStyleLinestyle.setObjectName(u"cbStyleLinestyle")

        self.horizontalLayout_10.addWidget(self.cbStyleLinestyle)

        self.horizontalLayout_10.setStretch(1, 10)

        self.verticalLayout_9.addLayout(self.horizontalLayout_10)

        self.horizontalLayout_11 = QHBoxLayout()
        self.horizontalLayout_11.setObjectName(u"horizontalLayout_11")
        self.label_25 = QLabel(self.pgstyle)
        self.label_25.setObjectName(u"label_25")

        self.horizontalLayout_11.addWidget(self.label_25)

        self.cbStyleJustification = QComboBox(self.pgstyle)
        self.cbStyleJustification.addItem("")
        self.cbStyleJustification.addItem("")
        self.cbStyleJustification.addItem("")
        self.cbStyleJustification.setObjectName(u"cbStyleJustification")

        self.horizontalLayout_11.addWidget(self.cbStyleJustification)

        self.horizontalLayout_11.setStretch(1, 10)

        self.verticalLayout_9.addLayout(self.horizontalLayout_11)

        self.horizontalLayout_12 = QHBoxLayout()
        self.horizontalLayout_12.setObjectName(u"horizontalLayout_12")
        self.label_26 = QLabel(self.pgstyle)
        self.label_26.setObjectName(u"label_26")

        self.horizontalLayout_12.addWidget(self.label_26)

        self.sbStyleBoundaryoffset = QSpinBox(self.pgstyle)
        self.sbStyleBoundaryoffset.setObjectName(u"sbStyleBoundaryoffset")
        self.sbStyleBoundaryoffset.setMinimum(1)
        self.sbStyleBoundaryoffset.setMaximum(20)

        self.horizontalLayout_12.addWidget(self.sbStyleBoundaryoffset)

        self.horizontalSpacer_12 = QSpacerItem(13, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_12.addItem(self.horizontalSpacer_12)


        self.verticalLayout_9.addLayout(self.horizontalLayout_12)

        self.verticalSpacer_5 = QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_9.addItem(self.verticalSpacer_5)

        self.swAssetProps.addWidget(self.pgstyle)
        self.splitter.addWidget(self.swAssetProps)

        self.verticalLayout_8.addWidget(self.splitter)

        self.dwAssets.setWidget(self.dockWidgetContents_3)
        card_editor_main.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.dwAssets)
        self.toolbar = QToolBar(card_editor_main)
        self.toolbar.setObjectName(u"toolbar")
        self.toolbar.setMovable(False)
        self.toolbar.setAllowedAreas(Qt.TopToolBarArea)
        self.toolbar.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.toolbar.setFloatable(False)
        card_editor_main.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.toolbar)
        QWidget.setTabOrder(self.pbStyleTextcolor, self.cbStyleLinestyle)
        QWidget.setTabOrder(self.cbStyleLinestyle, self.cbStyleJustification)
        QWidget.setTabOrder(self.cbStyleJustification, self.sbStyleBoundaryoffset)
        QWidget.setTabOrder(self.sbStyleBoundaryoffset, self.leImgAssetX)
        QWidget.setTabOrder(self.leImgAssetX, self.leImgAssetW)
        QWidget.setTabOrder(self.leImgAssetW, self.leImgAssetY)
        QWidget.setTabOrder(self.leImgAssetY, self.twAssets)
        QWidget.setTabOrder(self.twAssets, self.leImgAssetH)
        QWidget.setTabOrder(self.leImgAssetH, self.lwGfxItems)
        QWidget.setTabOrder(self.lwGfxItems, self.pbSelectFile)
        QWidget.setTabOrder(self.pbSelectFile, self.cbImgAssetFile)
        QWidget.setTabOrder(self.cbImgAssetFile, self.twCards)
        QWidget.setTabOrder(self.twCards, self.sbRectX)
        QWidget.setTabOrder(self.sbRectX, self.sbRectY)
        QWidget.setTabOrder(self.sbRectY, self.sbRectW)
        QWidget.setTabOrder(self.sbRectW, self.sbRectH)
        QWidget.setTabOrder(self.sbRectH, self.dsRectR)
        QWidget.setTabOrder(self.dsRectR, self.cbRectStyle)
        QWidget.setTabOrder(self.cbRectStyle, self.sbTextX)
        QWidget.setTabOrder(self.sbTextX, self.sbTextY)
        QWidget.setTabOrder(self.sbTextY, self.sbTextW)
        QWidget.setTabOrder(self.sbTextW, self.sbTextH)
        QWidget.setTabOrder(self.sbTextH, self.dsTextR)
        QWidget.setTabOrder(self.dsTextR, self.cbTextStyle)
        QWidget.setTabOrder(self.cbTextStyle, self.leTextText)
        QWidget.setTabOrder(self.leTextText, self.sbImageX)
        QWidget.setTabOrder(self.sbImageX, self.sbImageY)
        QWidget.setTabOrder(self.sbImageY, self.sbImageW)
        QWidget.setTabOrder(self.sbImageW, self.sbImageH)
        QWidget.setTabOrder(self.sbImageH, self.dsImageR)
        QWidget.setTabOrder(self.dsImageR, self.cbImageImage)
        QWidget.setTabOrder(self.cbImageImage, self.pushButton)
        QWidget.setTabOrder(self.pushButton, self.pbStyleFillcolor)
        QWidget.setTabOrder(self.pbStyleFillcolor, self.sbStyleBorderthickness)
        QWidget.setTabOrder(self.sbStyleBorderthickness, self.pbStyleBordercolor)

        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuView.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())
        self.menuFile.addAction(self.actionNew)
        self.menuFile.addAction(self.actionLoad)
        self.menuFile.addAction(self.actionSave)
        self.menuFile.addAction(self.actionSaveAs)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionQuit)
        self.menuHelp.addAction(self.actionAbout)
        self.menuView.addAction(self.actionFrontFace)
        self.menuView.addAction(self.menuCard_zoom.menuAction())
        self.menuCard_zoom.addAction(self.actionZoomIn)
        self.menuCard_zoom.addAction(self.actionZoomReset)
        self.menuCard_zoom.addAction(self.actionZoomOut)

        self.retranslateUi(card_editor_main)
        self.actionQuit.triggered.connect(card_editor_main.close)
        self.actionAbout.triggered.connect(card_editor_main.do_about)
        self.actionLoad.triggered.connect(card_editor_main.do_load)
        self.actionNew.triggered.connect(card_editor_main.do_new)
        self.actionSave.triggered.connect(card_editor_main.do_save)
        self.actionSaveAs.triggered.connect(card_editor_main.do_saveas)
        self.twAssets.currentItemChanged.connect(card_editor_main.current_asset_changed)
        self.twCards.currentItemChanged.connect(card_editor_main.current_card_changed)
        self.actionFrontFace.toggled.connect(card_editor_main.do_frontface)
        self.actionZoomIn.triggered.connect(card_editor_main.do_zoom)
        self.actionZoomReset.triggered.connect(card_editor_main.do_zoom)
        self.actionZoomOut.triggered.connect(card_editor_main.do_zoom)
        self.lwGfxItems.currentRowChanged.connect(card_editor_main.current_card_renderable_changed)
        self.cbRectStyle.currentIndexChanged.connect(card_editor_main.do_rect_update_int)
        self.cbImageImage.currentIndexChanged.connect(card_editor_main.do_image_update_int)
        self.leTextText.textChanged.connect(card_editor_main.do_text_update)
        self.cbTextStyle.currentIndexChanged.connect(card_editor_main.do_text_update_int)
        self.dsTextR.valueChanged.connect(card_editor_main.do_text_update_double)
        self.dsImageR.valueChanged.connect(card_editor_main.do_image_update_double)
        self.dsRectR.valueChanged.connect(card_editor_main.do_rect_update_double)
        self.leImgAssetX.editingFinished.connect(card_editor_main.do_as_image_update)
        self.leImgAssetW.editingFinished.connect(card_editor_main.do_as_image_update)
        self.leImgAssetY.editingFinished.connect(card_editor_main.do_as_image_update)
        self.leImgAssetH.editingFinished.connect(card_editor_main.do_as_image_update)
        self.sbStyleBorderthickness.valueChanged.connect(card_editor_main.do_as_style_update_int)
        self.cbStyleLinestyle.currentIndexChanged.connect(card_editor_main.do_as_style_update_int)
        self.cbStyleJustification.currentIndexChanged.connect(card_editor_main.do_as_style_update_int)
        self.sbStyleBoundaryoffset.valueChanged.connect(card_editor_main.do_as_style_update_int)
        self.pbStyleFillcolor.clicked.connect(card_editor_main.do_as_style_fillcolor)
        self.pbStyleBordercolor.clicked.connect(card_editor_main.do_as_style_bordercolor)
        self.pbStyleTextcolor.clicked.connect(card_editor_main.do_as_style_textcolor)
        self.pushButton.clicked.connect(card_editor_main.do_as_style_font)
        self.pbSelectFile.clicked.connect(card_editor_main.do_as_file_select)
        self.cbImgAssetFile.currentIndexChanged.connect(card_editor_main.do_as_image_update)
        self.sbImageX.valueChanged.connect(card_editor_main.do_image_update_int)
        self.sbImageY.valueChanged.connect(card_editor_main.do_image_update_int)
        self.sbImageW.valueChanged.connect(card_editor_main.do_image_update_int)
        self.sbImageH.valueChanged.connect(card_editor_main.do_image_update_int)
        self.sbTextX.valueChanged.connect(card_editor_main.do_text_update_int)
        self.sbTextY.valueChanged.connect(card_editor_main.do_text_update_int)
        self.sbTextW.valueChanged.connect(card_editor_main.do_text_update_int)
        self.sbTextH.valueChanged.connect(card_editor_main.do_text_update_int)
        self.sbRectX.valueChanged.connect(card_editor_main.do_rect_update_int)
        self.sbRectY.valueChanged.connect(card_editor_main.do_rect_update_int)
        self.sbRectW.valueChanged.connect(card_editor_main.do_rect_update_int)
        self.sbRectH.valueChanged.connect(card_editor_main.do_rect_update_int)

        self.swGfxItemProps.setCurrentIndex(3)
        self.swAssetProps.setCurrentIndex(3)


        QMetaObject.connectSlotsByName(card_editor_main)
    # setupUi

    def retranslateUi(self, card_editor_main):
        card_editor_main.setWindowTitle(QCoreApplication.translate("card_editor_main", u"T.I.M.E Stories Card Editor", None))
        self.actionQuit.setText(QCoreApplication.translate("card_editor_main", u"Quit", None))
        self.actionAbout.setText(QCoreApplication.translate("card_editor_main", u"About...", None))
        self.actionNew.setText(QCoreApplication.translate("card_editor_main", u"New deck", None))
        self.actionLoad.setText(QCoreApplication.translate("card_editor_main", u"Load deck...", None))
        self.actionSave.setText(QCoreApplication.translate("card_editor_main", u"Save deck...", None))
        self.actionSaveAs.setText(QCoreApplication.translate("card_editor_main", u"Save deck as...", None))
        self.actionFrontFace.setText(QCoreApplication.translate("card_editor_main", u"Front face", None))
#if QT_CONFIG(shortcut)
        self.actionFrontFace.setShortcut(QCoreApplication.translate("card_editor_main", u"Ctrl+F", None))
#endif // QT_CONFIG(shortcut)
        self.actionZoomIn.setText(QCoreApplication.translate("card_editor_main", u"Zoom in", None))
#if QT_CONFIG(shortcut)
        self.actionZoomIn.setShortcut(QCoreApplication.translate("card_editor_main", u"Ctrl++", None))
#endif // QT_CONFIG(shortcut)
        self.actionZoomReset.setText(QCoreApplication.translate("card_editor_main", u"Reset zoom", None))
#if QT_CONFIG(shortcut)
        self.actionZoomReset.setShortcut(QCoreApplication.translate("card_editor_main", u"Ctrl+=", None))
#endif // QT_CONFIG(shortcut)
        self.actionZoomOut.setText(QCoreApplication.translate("card_editor_main", u"Zoom out", None))
#if QT_CONFIG(shortcut)
        self.actionZoomOut.setShortcut(QCoreApplication.translate("card_editor_main", u"Ctrl+-", None))
#endif // QT_CONFIG(shortcut)
        self.action100.setText(QCoreApplication.translate("card_editor_main", u"100%", None))
        self.action125.setText(QCoreApplication.translate("card_editor_main", u"125%", None))
        self.action150.setText(QCoreApplication.translate("card_editor_main", u"150%", None))
        self.action175.setText(QCoreApplication.translate("card_editor_main", u"175%", None))
        self.lblInfo.setText(QCoreApplication.translate("card_editor_main", u"TextLabel", None))
        self.menuFile.setTitle(QCoreApplication.translate("card_editor_main", u"File", None))
        self.menuHelp.setTitle(QCoreApplication.translate("card_editor_main", u"Help", None))
        self.menuView.setTitle(QCoreApplication.translate("card_editor_main", u"View", None))
        self.menuCard_zoom.setTitle(QCoreApplication.translate("card_editor_main", u"Card zoom", None))
        self.dwCards.setWindowTitle(QCoreApplication.translate("card_editor_main", u"Cards", None))
        self.label_2.setText(QCoreApplication.translate("card_editor_main", u"Image item", None))
        self.label.setText(QCoreApplication.translate("card_editor_main", u"Location", None))
        self.label_5.setText(QCoreApplication.translate("card_editor_main", u"Size", None))
        self.label_6.setText(QCoreApplication.translate("card_editor_main", u"Rotation", None))
        self.dsImageR.setSuffix(QCoreApplication.translate("card_editor_main", u" deg", None))
        self.label_7.setText(QCoreApplication.translate("card_editor_main", u"Image asset", None))
        self.label_3.setText(QCoreApplication.translate("card_editor_main", u"Textbox item", None))
        self.label_8.setText(QCoreApplication.translate("card_editor_main", u"Location", None))
        self.label_9.setText(QCoreApplication.translate("card_editor_main", u"Size", None))
        self.label_10.setText(QCoreApplication.translate("card_editor_main", u"Rotation", None))
        self.dsTextR.setSuffix(QCoreApplication.translate("card_editor_main", u" deg", None))
        self.label_14.setText(QCoreApplication.translate("card_editor_main", u"Style", None))
        self.label_4.setText(QCoreApplication.translate("card_editor_main", u"Rectangle item", None))
        self.label_12.setText(QCoreApplication.translate("card_editor_main", u"Size", None))
        self.label_11.setText(QCoreApplication.translate("card_editor_main", u"Location", None))
        self.label_13.setText(QCoreApplication.translate("card_editor_main", u"Rotation", None))
        self.dsRectR.setSuffix(QCoreApplication.translate("card_editor_main", u" deg", None))
        self.label_15.setText(QCoreApplication.translate("card_editor_main", u"Style", None))
        self.dwAssets.setWindowTitle(QCoreApplication.translate("card_editor_main", u"Assets", None))
        self.lblImgAssetName.setText(QCoreApplication.translate("card_editor_main", u"TextLabel", None))
        self.lblImgAssetFile.setText(QCoreApplication.translate("card_editor_main", u"TextLabel", None))
        self.label_16.setText(QCoreApplication.translate("card_editor_main", u"Location", None))
        self.label_17.setText(QCoreApplication.translate("card_editor_main", u"Size", None))
        self.lbImgAssetImage.setText(QCoreApplication.translate("card_editor_main", u"TextLabel", None))
        self.label_21.setText(QCoreApplication.translate("card_editor_main", u"Source file:", None))
        self.lbImgAssetFile.setText(QCoreApplication.translate("card_editor_main", u"TextLabel", None))
        self.lblFileName.setText(QCoreApplication.translate("card_editor_main", u"TextLabel", None))
        self.lblFileFilename.setText(QCoreApplication.translate("card_editor_main", u"TextLabel", None))
        self.pbSelectFile.setText(QCoreApplication.translate("card_editor_main", u"Select file...", None))
        self.lblFileSize.setText(QCoreApplication.translate("card_editor_main", u"TextLabel", None))
        self.lblFileImage.setText(QCoreApplication.translate("card_editor_main", u"TextLabel", None))
        self.lblStyleName.setText(QCoreApplication.translate("card_editor_main", u"TextLabel", None))
        self.label_18.setText(QCoreApplication.translate("card_editor_main", u"Family:", None))
        self.lblStyleTypeface.setText(QCoreApplication.translate("card_editor_main", u"TextLabel", None))
        self.lblStyleSize.setText(QCoreApplication.translate("card_editor_main", u"Point size", None))
        self.pushButton.setText(QCoreApplication.translate("card_editor_main", u"Select typeface and size...", None))
        self.label_19.setText(QCoreApplication.translate("card_editor_main", u"Fill color", None))
        self.pbStyleFillcolor.setText("")
        self.label_20.setText(QCoreApplication.translate("card_editor_main", u"Border thickness", None))
        self.label_22.setText(QCoreApplication.translate("card_editor_main", u"Border color", None))
        self.pbStyleBordercolor.setText("")
        self.label_23.setText(QCoreApplication.translate("card_editor_main", u"Text color", None))
        self.pbStyleTextcolor.setText("")
        self.label_24.setText(QCoreApplication.translate("card_editor_main", u"Line style", None))
        self.cbStyleLinestyle.setItemText(0, QCoreApplication.translate("card_editor_main", u"solid", None))
        self.cbStyleLinestyle.setItemText(1, QCoreApplication.translate("card_editor_main", u"dash", None))
        self.cbStyleLinestyle.setItemText(2, QCoreApplication.translate("card_editor_main", u"dot", None))
        self.cbStyleLinestyle.setItemText(3, QCoreApplication.translate("card_editor_main", u"dashdot", None))
        self.cbStyleLinestyle.setItemText(4, QCoreApplication.translate("card_editor_main", u"halo", None))

        self.label_25.setText(QCoreApplication.translate("card_editor_main", u"Justification", None))
        self.cbStyleJustification.setItemText(0, QCoreApplication.translate("card_editor_main", u"center", None))
        self.cbStyleJustification.setItemText(1, QCoreApplication.translate("card_editor_main", u"left", None))
        self.cbStyleJustification.setItemText(2, QCoreApplication.translate("card_editor_main", u"right", None))

        self.label_26.setText(QCoreApplication.translate("card_editor_main", u"Boundary offset", None))
        self.toolbar.setWindowTitle(QCoreApplication.translate("card_editor_main", u"Actions", None))
    # retranslateUi

