# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main.ui'
##
## Created by: Qt User Interface Compiler version 6.8.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (
    QCoreApplication,
    QDate,
    QDateTime,
    QLocale,
    QMetaObject,
    QObject,
    QPoint,
    QRect,
    QSize,
    QTime,
    QUrl,
    Qt,
)
from PySide6.QtGui import (
    QAction,
    QBrush,
    QColor,
    QConicalGradient,
    QCursor,
    QFont,
    QFontDatabase,
    QGradient,
    QIcon,
    QImage,
    QKeySequence,
    QLinearGradient,
    QPainter,
    QPalette,
    QPixmap,
    QRadialGradient,
    QTransform,
)
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QLabel,
    QMainWindow,
    QMenu,
    QMenuBar,
    QPushButton,
    QScrollBar,
    QSizePolicy,
    QSpinBox,
    QStatusBar,
    QWidget,
)


class Ui_UIMainWindow(object):
    def setupUi(self, UIMainWindow):
        if not UIMainWindow.objectName():
            UIMainWindow.setObjectName("UIMainWindow")
        UIMainWindow.resize(800, 380)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(UIMainWindow.sizePolicy().hasHeightForWidth())
        UIMainWindow.setSizePolicy(sizePolicy)
        UIMainWindow.setMinimumSize(QSize(800, 380))
        UIMainWindow.setMaximumSize(QSize(800, 380))
        UIMainWindow.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        UIMainWindow.setLocale(QLocale(QLocale.English, QLocale.UnitedKingdom))
        self.actionSettings = QAction(UIMainWindow)
        self.actionSettings.setObjectName("actionSettings")
        self.actionQuit = QAction(UIMainWindow)
        self.actionQuit.setObjectName("actionQuit")
        # icon = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.ApplicationExit))
        # self.actionQuit.setIcon(icon)
        self.actionImport = QAction(UIMainWindow)
        self.actionImport.setObjectName("actionImport")
        # icon1 = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.DocumentOpen))
        # self.actionImport.setIcon(icon1)
        self.actionBankExport = QAction(UIMainWindow)
        self.actionBankExport.setObjectName("actionBankExport")
        # icon2 = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.DocumentSaveAs))
        # self.actionBankExport.setIcon(icon2)
        self.actionBankSave = QAction(UIMainWindow)
        self.actionBankSave.setObjectName("actionBankSave")
        # icon3 = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.DocumentSave))
        # self.actionBankSave.setIcon(icon3)
        self.actionAbout = QAction(UIMainWindow)
        self.actionAbout.setObjectName("actionAbout")
        # icon4 = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.HelpAbout))
        # self.actionAbout.setIcon(icon4)
        self.actionBufferExport = QAction(UIMainWindow)
        self.actionBufferExport.setObjectName("actionBufferExport")
        # icon5 = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.MailAttachment))
        # self.actionBufferExport.setIcon(icon5)
        self.actionNew = QAction(UIMainWindow)
        self.actionNew.setObjectName("actionNew")
        # icon6 = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.DocumentNew))
        # self.actionNew.setIcon(icon6)
        self.actionStoreProgram = QAction(UIMainWindow)
        self.actionStoreProgram.setObjectName("actionStoreProgram")
        # icon7 = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.GoNext))
        # self.actionStoreProgram.setIcon(icon7)
        self.actionDeviceStoreBank = QAction(UIMainWindow)
        self.actionDeviceStoreBank.setObjectName("actionDeviceStoreBank")
        # self.actionDeviceStoreBank.setIcon(icon7)
        self.actionHelp = QAction(UIMainWindow)
        self.actionHelp.setObjectName("actionHelp")
        # icon8 = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.DialogQuestion))
        # self.actionHelp.setIcon(icon8)
        self.centralwidget = QWidget(UIMainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.CONFIGURATION = QComboBox(self.centralwidget)
        self.CONFIGURATION.addItem("")
        self.CONFIGURATION.addItem("")
        self.CONFIGURATION.addItem("")
        self.CONFIGURATION.addItem("")
        self.CONFIGURATION.addItem("")
        self.CONFIGURATION.addItem("")
        self.CONFIGURATION.addItem("")
        self.CONFIGURATION.addItem("")
        self.CONFIGURATION.addItem("")
        self.CONFIGURATION.addItem("")
        self.CONFIGURATION.addItem("")
        self.CONFIGURATION.addItem("")
        self.CONFIGURATION.addItem("")
        self.CONFIGURATION.addItem("")
        self.CONFIGURATION.addItem("")
        self.CONFIGURATION.setObjectName("CONFIGURATION")
        self.CONFIGURATION.setGeometry(QRect(90, 220, 331, 32))
        self.CONFIGURATION.setTabletTracking(True)
        self.CONFIGURATION.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.CONFIGURATION.setLocale(QLocale(QLocale.English, QLocale.UnitedKingdom))
        self.CHRS_TYPE = QComboBox(self.centralwidget)
        self.CHRS_TYPE.addItem("")
        self.CHRS_TYPE.addItem("")
        self.CHRS_TYPE.addItem("")
        self.CHRS_TYPE.addItem("")
        self.CHRS_TYPE.addItem("")
        self.CHRS_TYPE.addItem("")
        self.CHRS_TYPE.addItem("")
        self.CHRS_TYPE.addItem("")
        self.CHRS_TYPE.addItem("")
        self.CHRS_TYPE.addItem("")
        self.CHRS_TYPE.addItem("")
        self.CHRS_TYPE.addItem("")
        self.CHRS_TYPE.setObjectName("CHRS_TYPE")
        self.CHRS_TYPE.setGeometry(QRect(100, 70, 141, 32))
        self.CHRS_TYPE.setTabletTracking(True)
        self.CHRS_TYPE.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.CHRS_TYPE.setLocale(QLocale(QLocale.English, QLocale.UnitedKingdom))
        self.CHRS_STEREO = QCheckBox(self.centralwidget)
        self.CHRS_STEREO.setObjectName("CHRS_STEREO")
        self.CHRS_STEREO.setGeometry(QRect(130, 110, 85, 20))
        self.CHRS_STEREO.setTabletTracking(True)
        self.CHRS_STEREO.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.CHRS_STEREO.setLocale(QLocale(QLocale.English, QLocale.UnitedKingdom))
        self.DLY_TIME_T = QLabel(self.centralwidget)
        self.DLY_TIME_T.setObjectName("DLY_TIME_T")
        self.DLY_TIME_T.setGeometry(QRect(260, 180, 51, 31))
        self.DLY_TIME_T.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.DLY_TIME_T.setLocale(QLocale(QLocale.English, QLocale.UnitedKingdom))
        self.DLY_TIME_T.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.DLY_TIME_T.setWordWrap(True)
        self.DLY_TIME = QScrollBar(self.centralwidget)
        self.DLY_TIME.setObjectName("DLY_TIME")
        self.DLY_TIME.setGeometry(QRect(280, 70, 10, 101))
        self.DLY_TIME.setTabletTracking(True)
        self.DLY_TIME.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.DLY_TIME.setLocale(QLocale(QLocale.English, QLocale.UnitedKingdom))
        self.DLY_TIME.setMinimum(1)
        self.DLY_TIME.setMaximum(100)
        self.DLY_TIME.setOrientation(Qt.Orientation.Vertical)
        self.DLY_TIME.setInvertedAppearance(False)
        self.DLY_TIME.setInvertedControls(False)
        self.DLY_TIME_L = QLabel(self.centralwidget)
        self.DLY_TIME_L.setObjectName("DLY_TIME_L")
        self.DLY_TIME_L.setGeometry(QRect(250, 50, 71, 16))
        self.DLY_TIME_L.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.DLY_TIME_L.setLocale(QLocale(QLocale.English, QLocale.UnitedKingdom))
        self.DLY_TIME_L.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.REV_MIX_T = QLabel(self.centralwidget)
        self.REV_MIX_T.setObjectName("REV_MIX_T")
        self.REV_MIX_T.setGeometry(QRect(500, 180, 51, 31))
        self.REV_MIX_T.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.REV_MIX_T.setLocale(QLocale(QLocale.English, QLocale.UnitedKingdom))
        self.REV_MIX_T.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.REV_MIX_T.setWordWrap(True)
        self.REV_MIX_L = QLabel(self.centralwidget)
        self.REV_MIX_L.setObjectName("REV_MIX_L")
        self.REV_MIX_L.setGeometry(QRect(490, 50, 71, 16))
        self.REV_MIX_L.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.REV_MIX_L.setLocale(QLocale(QLocale.English, QLocale.UnitedKingdom))
        self.REV_MIX_L.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.REV_MIX = QScrollBar(self.centralwidget)
        self.REV_MIX.setObjectName("REV_MIX")
        self.REV_MIX.setGeometry(QRect(520, 70, 10, 101))
        self.REV_MIX.setTabletTracking(True)
        self.REV_MIX.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.REV_MIX.setLocale(QLocale(QLocale.English, QLocale.UnitedKingdom))
        self.REV_MIX.setMinimum(0)
        self.REV_MIX.setMaximum(99)
        self.REV_MIX.setSliderPosition(0)
        self.REV_MIX.setOrientation(Qt.Orientation.Vertical)
        self.REV_MIX.setInvertedAppearance(False)
        self.REV_MIX.setInvertedControls(False)
        self.DLY_REGEN_L = QLabel(self.centralwidget)
        self.DLY_REGEN_L.setObjectName("DLY_REGEN_L")
        self.DLY_REGEN_L.setGeometry(QRect(310, 50, 71, 16))
        self.DLY_REGEN_L.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.DLY_REGEN_L.setLocale(QLocale(QLocale.English, QLocale.UnitedKingdom))
        self.DLY_REGEN_L.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.DLY_REGEN_T = QLabel(self.centralwidget)
        self.DLY_REGEN_T.setObjectName("DLY_REGEN_T")
        self.DLY_REGEN_T.setGeometry(QRect(320, 180, 51, 31))
        self.DLY_REGEN_T.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.DLY_REGEN_T.setLocale(QLocale(QLocale.English, QLocale.UnitedKingdom))
        self.DLY_REGEN_T.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.DLY_REGEN_T.setWordWrap(True)
        self.DLY_REGEN = QScrollBar(self.centralwidget)
        self.DLY_REGEN.setObjectName("DLY_REGEN")
        self.DLY_REGEN.setGeometry(QRect(340, 70, 10, 101))
        self.DLY_REGEN.setTabletTracking(True)
        self.DLY_REGEN.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.DLY_REGEN.setLocale(QLocale(QLocale.English, QLocale.UnitedKingdom))
        self.DLY_REGEN.setMinimum(0)
        self.DLY_REGEN.setMaximum(99)
        self.DLY_REGEN.setOrientation(Qt.Orientation.Vertical)
        self.DLY_REGEN.setInvertedAppearance(False)
        self.DLY_REGEN.setInvertedControls(False)
        self.REV_DECAY_L = QLabel(self.centralwidget)
        self.REV_DECAY_L.setObjectName("REV_DECAY_L")
        self.REV_DECAY_L.setGeometry(QRect(430, 50, 71, 16))
        self.REV_DECAY_L.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.REV_DECAY_L.setLocale(QLocale(QLocale.English, QLocale.UnitedKingdom))
        self.REV_DECAY_L.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.REV_DECAY = QScrollBar(self.centralwidget)
        self.REV_DECAY.setObjectName("REV_DECAY")
        self.REV_DECAY.setGeometry(QRect(460, 70, 10, 101))
        self.REV_DECAY.setTabletTracking(True)
        self.REV_DECAY.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.REV_DECAY.setLocale(QLocale(QLocale.English, QLocale.UnitedKingdom))
        self.REV_DECAY.setMinimum(0)
        self.REV_DECAY.setMaximum(99)
        self.REV_DECAY.setOrientation(Qt.Orientation.Vertical)
        self.REV_DECAY.setInvertedAppearance(False)
        self.REV_DECAY.setInvertedControls(False)
        self.REV_DECAY_T = QLabel(self.centralwidget)
        self.REV_DECAY_T.setObjectName("REV_DECAY_T")
        self.REV_DECAY_T.setGeometry(QRect(440, 180, 51, 31))
        self.REV_DECAY_T.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.REV_DECAY_T.setLocale(QLocale(QLocale.English, QLocale.UnitedKingdom))
        self.REV_DECAY_T.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.REV_DECAY_T.setWordWrap(True)
        self.DLY_MIX_T = QLabel(self.centralwidget)
        self.DLY_MIX_T.setObjectName("DLY_MIX_T")
        self.DLY_MIX_T.setGeometry(QRect(380, 175, 51, 41))
        self.DLY_MIX_T.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.DLY_MIX_T.setLocale(QLocale(QLocale.English, QLocale.UnitedKingdom))
        self.DLY_MIX_T.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.DLY_MIX_T.setWordWrap(True)
        self.DLY_MIX_L = QLabel(self.centralwidget)
        self.DLY_MIX_L.setObjectName("DLY_MIX_L")
        self.DLY_MIX_L.setGeometry(QRect(370, 50, 71, 16))
        self.DLY_MIX_L.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.DLY_MIX_L.setLocale(QLocale(QLocale.English, QLocale.UnitedKingdom))
        self.DLY_MIX_L.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.DLY_MIX = QScrollBar(self.centralwidget)
        self.DLY_MIX.setObjectName("DLY_MIX")
        self.DLY_MIX.setGeometry(QRect(400, 70, 10, 101))
        self.DLY_MIX.setTabletTracking(True)
        self.DLY_MIX.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.DLY_MIX.setLocale(QLocale(QLocale.English, QLocale.UnitedKingdom))
        self.DLY_MIX.setMinimum(0)
        self.DLY_MIX.setMaximum(99)
        self.DLY_MIX.setOrientation(Qt.Orientation.Vertical)
        self.DLY_MIX.setInvertedAppearance(False)
        self.DLY_MIX.setInvertedControls(False)
        self.REVERB_TYPE = QComboBox(self.centralwidget)
        self.REVERB_TYPE.addItem("")
        self.REVERB_TYPE.addItem("")
        self.REVERB_TYPE.addItem("")
        self.REVERB_TYPE.addItem("")
        self.REVERB_TYPE.addItem("")
        self.REVERB_TYPE.addItem("")
        self.REVERB_TYPE.addItem("")
        self.REVERB_TYPE.addItem("")
        self.REVERB_TYPE.addItem("")
        self.REVERB_TYPE.addItem("")
        self.REVERB_TYPE.addItem("")
        self.REVERB_TYPE.addItem("")
        self.REVERB_TYPE.addItem("")
        self.REVERB_TYPE.addItem("")
        self.REVERB_TYPE.addItem("")
        self.REVERB_TYPE.addItem("")
        self.REVERB_TYPE.addItem("")
        self.REVERB_TYPE.addItem("")
        self.REVERB_TYPE.addItem("")
        self.REVERB_TYPE.addItem("")
        self.REVERB_TYPE.setObjectName("REVERB_TYPE")
        self.REVERB_TYPE.setGeometry(QRect(530, 220, 201, 32))
        self.REVERB_TYPE.setTabletTracking(True)
        self.REVERB_TYPE.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.REVERB_TYPE.setLocale(QLocale(QLocale.English, QLocale.UnitedKingdom))
        self.IN_EQ_T = QLabel(self.centralwidget)
        self.IN_EQ_T.setObjectName("IN_EQ_T")
        self.IN_EQ_T.setGeometry(QRect(30, 180, 51, 31))
        self.IN_EQ_T.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.IN_EQ_T.setLocale(QLocale(QLocale.English, QLocale.UnitedKingdom))
        self.IN_EQ_T.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.IN_EQ_T.setWordWrap(True)
        self.IN_EQ_L = QLabel(self.centralwidget)
        self.IN_EQ_L.setObjectName("IN_EQ_L")
        self.IN_EQ_L.setGeometry(QRect(20, 50, 71, 16))
        self.IN_EQ_L.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.IN_EQ_L.setLocale(QLocale(QLocale.English, QLocale.UnitedKingdom))
        self.IN_EQ_L.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.IN_EQ = QScrollBar(self.centralwidget)
        self.IN_EQ.setObjectName("IN_EQ")
        self.IN_EQ.setGeometry(QRect(50, 70, 10, 101))
        self.IN_EQ.setTabletTracking(True)
        self.IN_EQ.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.IN_EQ.setToolTipDuration(-1)
        self.IN_EQ.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.IN_EQ.setLocale(QLocale(QLocale.English, QLocale.UnitedKingdom))
        self.IN_EQ.setMinimum(0)
        self.IN_EQ.setMaximum(30)
        self.IN_EQ.setOrientation(Qt.Orientation.Vertical)
        self.IN_EQ.setInvertedAppearance(False)
        self.IN_EQ.setInvertedControls(False)
        self.OUT_EQ_T = QLabel(self.centralwidget)
        self.OUT_EQ_T.setObjectName("OUT_EQ_T")
        self.OUT_EQ_T.setGeometry(QRect(560, 180, 51, 31))
        self.OUT_EQ_T.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.OUT_EQ_T.setLocale(QLocale(QLocale.English, QLocale.UnitedKingdom))
        self.OUT_EQ_T.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.OUT_EQ_T.setWordWrap(True)
        self.OUT_EQ_L = QLabel(self.centralwidget)
        self.OUT_EQ_L.setObjectName("OUT_EQ_L")
        self.OUT_EQ_L.setGeometry(QRect(550, 50, 71, 16))
        self.OUT_EQ_L.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.OUT_EQ_L.setLocale(QLocale(QLocale.English, QLocale.UnitedKingdom))
        self.OUT_EQ_L.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.OUT_EQ = QScrollBar(self.centralwidget)
        self.OUT_EQ.setObjectName("OUT_EQ")
        self.OUT_EQ.setGeometry(QRect(580, 70, 10, 101))
        self.OUT_EQ.setTabletTracking(True)
        self.OUT_EQ.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.OUT_EQ.setLocale(QLocale(QLocale.English, QLocale.UnitedKingdom))
        self.OUT_EQ.setMinimum(0)
        self.OUT_EQ.setMaximum(30)
        self.OUT_EQ.setOrientation(Qt.Orientation.Vertical)
        self.OUT_EQ.setInvertedAppearance(False)
        self.OUT_EQ.setInvertedControls(False)
        self.MOD_SOURCE = QComboBox(self.centralwidget)
        self.MOD_SOURCE.addItem("")
        self.MOD_SOURCE.addItem("")
        self.MOD_SOURCE.addItem("")
        self.MOD_SOURCE.addItem("")
        self.MOD_SOURCE.addItem("")
        self.MOD_SOURCE.addItem("")
        self.MOD_SOURCE.addItem("")
        self.MOD_SOURCE.addItem("")
        self.MOD_SOURCE.setObjectName("MOD_SOURCE")
        self.MOD_SOURCE.setGeometry(QRect(614, 70, 161, 32))
        self.MOD_SOURCE.setTabletTracking(True)
        self.MOD_SOURCE.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.MOD_SOURCE.setLocale(QLocale(QLocale.English, QLocale.UnitedKingdom))
        self.MOD_DEST = QComboBox(self.centralwidget)
        self.MOD_DEST.addItem("")
        self.MOD_DEST.addItem("")
        self.MOD_DEST.addItem("")
        self.MOD_DEST.addItem("")
        self.MOD_DEST.addItem("")
        self.MOD_DEST.addItem("")
        self.MOD_DEST.addItem("")
        self.MOD_DEST.setObjectName("MOD_DEST")
        self.MOD_DEST.setGeometry(QRect(614, 110, 161, 32))
        self.MOD_DEST.setTabletTracking(True)
        self.MOD_DEST.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.MOD_DEST.setLocale(QLocale(QLocale.English, QLocale.UnitedKingdom))
        self.CHORUS_T = QLabel(self.centralwidget)
        self.CHORUS_T.setObjectName("CHORUS_T")
        self.CHORUS_T.setGeometry(QRect(80, 6, 181, 40))
        self.CHORUS_T.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.CHORUS_T.setLocale(QLocale(QLocale.English, QLocale.UnitedKingdom))
        self.CHORUS_T.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.CHORUS_T.setWordWrap(True)
        self.DLY_T = QLabel(self.centralwidget)
        self.DLY_T.setObjectName("DLY_T")
        self.DLY_T.setGeometry(QRect(257, 10, 181, 31))
        self.DLY_T.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.DLY_T.setLocale(QLocale(QLocale.English, QLocale.UnitedKingdom))
        self.DLY_T.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.DLY_T.setWordWrap(True)
        self.REV_T = QLabel(self.centralwidget)
        self.REV_T.setObjectName("REV_T")
        self.REV_T.setGeometry(QRect(440, 10, 170, 31))
        self.REV_T.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.REV_T.setLocale(QLocale(QLocale.English, QLocale.UnitedKingdom))
        self.REV_T.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.REV_T.setWordWrap(True)
        self.MOD_T = QLabel(self.centralwidget)
        self.MOD_T.setObjectName("MOD_T")
        self.MOD_T.setGeometry(QRect(610, 10, 181, 31))
        self.MOD_T.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.MOD_T.setLocale(QLocale(QLocale.English, QLocale.UnitedKingdom))
        self.MOD_T.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.MOD_T.setWordWrap(True)
        self.MOD_AMT = QScrollBar(self.centralwidget)
        self.MOD_AMT.setObjectName("MOD_AMT")
        self.MOD_AMT.setGeometry(QRect(624, 158, 141, 10))
        self.MOD_AMT.setTabletTracking(True)
        self.MOD_AMT.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.MOD_AMT.setLocale(QLocale(QLocale.English, QLocale.UnitedKingdom))
        self.MOD_AMT.setMaximum(198)
        self.MOD_AMT.setOrientation(Qt.Orientation.Horizontal)
        self.MOD_AMT.setInvertedAppearance(False)
        self.MOD_AMT.setInvertedControls(False)
        self.MOD_AMT_L = QLabel(self.centralwidget)
        self.MOD_AMT_L.setObjectName("MOD_AMT_L")
        self.MOD_AMT_L.setGeometry(QRect(656, 180, 71, 16))
        self.MOD_AMT_L.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.MOD_AMT_L.setLocale(QLocale(QLocale.English, QLocale.UnitedKingdom))
        self.MOD_AMT_L.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.CHRS_SPEED = QScrollBar(self.centralwidget)
        self.CHRS_SPEED.setObjectName("CHRS_SPEED")
        self.CHRS_SPEED.setGeometry(QRect(110, 150, 121, 10))
        self.CHRS_SPEED.setTabletTracking(True)
        self.CHRS_SPEED.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.CHRS_SPEED.setLocale(QLocale(QLocale.English, QLocale.UnitedKingdom))
        self.CHRS_SPEED.setOrientation(Qt.Orientation.Horizontal)
        self.CHRS_SPEED.setInvertedAppearance(False)
        self.CHRS_SPEED.setInvertedControls(False)
        self.CHRS_SPEED_L = QLabel(self.centralwidget)
        self.CHRS_SPEED_L.setObjectName("CHRS_SPEED_L")
        self.CHRS_SPEED_L.setGeometry(QRect(130, 170, 71, 16))
        self.CHRS_SPEED_L.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.CHRS_SPEED_L.setLocale(QLocale(QLocale.English, QLocale.UnitedKingdom))
        self.CHRS_SPEED_L.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.PROG_T_2 = QLabel(self.centralwidget)
        self.PROG_T_2.setObjectName("PROG_T_2")
        self.PROG_T_2.setGeometry(QRect(443, 226, 91, 16))
        self.PROG_T_2.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.PROG_T_2.setLocale(QLocale(QLocale.English, QLocale.UnitedKingdom))
        self.PROG_T_3 = QLabel(self.centralwidget)
        self.PROG_T_3.setObjectName("PROG_T_3")
        self.PROG_T_3.setGeometry(QRect(20, 226, 91, 16))
        self.PROG_T_3.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.PROG_T_3.setLocale(QLocale(QLocale.English, QLocale.UnitedKingdom))
        self.BANK_PATH = QLabel(self.centralwidget)
        self.BANK_PATH.setObjectName("BANK_PATH")
        self.BANK_PATH.setGeometry(QRect(20, 259, 451, 31))
        self.BANK_PATH.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.BANK_PATH.setLocale(QLocale(QLocale.English, QLocale.UnitedKingdom))
        self.BANK_PATH.setAlignment(
            Qt.AlignmentFlag.AlignLeading
            | Qt.AlignmentFlag.AlignLeft
            | Qt.AlignmentFlag.AlignVCenter
        )
        self.BANK_PATH.setWordWrap(True)
        self.PROGRAM_ID = QSpinBox(self.centralwidget)
        self.PROGRAM_ID.setObjectName("PROGRAM_ID")
        self.PROGRAM_ID.setGeometry(QRect(500, 267, 41, 21))
        self.PROGRAM_ID.setMinimum(100)
        self.PROGRAM_ID.setMaximum(199)
        self.PROG_RECALL = QPushButton(self.centralwidget)
        self.PROG_RECALL.setObjectName("PROG_RECALL")
        self.PROG_RECALL.setGeometry(QRect(670, 260, 91, 32))
        self.PROG_SYNC = QPushButton(self.centralwidget)
        self.PROG_SYNC.setObjectName("PROG_SYNC")
        self.PROG_SYNC.setGeometry(QRect(570, 260, 91, 32))
        UIMainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(UIMainWindow)
        self.statusbar.setObjectName("statusbar")
        UIMainWindow.setStatusBar(self.statusbar)
        self.menubar = QMenuBar(UIMainWindow)
        self.menubar.setObjectName("menubar")
        self.menubar.setGeometry(QRect(0, 0, 800, 37))
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuDevice = QMenu(self.menubar)
        self.menuDevice.setObjectName("menuDevice")
        UIMainWindow.setMenuBar(self.menubar)

        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuDevice.menuAction())
        self.menuFile.addAction(self.actionNew)
        self.menuFile.addAction(self.actionImport)
        self.menuFile.addAction(self.actionBankSave)
        self.menuFile.addAction(self.actionBankExport)
        self.menuFile.addAction(self.actionBufferExport)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionSettings)
        self.menuFile.addAction(self.actionHelp)
        self.menuFile.addAction(self.actionAbout)
        self.menuFile.addAction(self.actionQuit)
        self.menuDevice.addSeparator()
        self.menuDevice.addAction(self.actionStoreProgram)
        self.menuDevice.addAction(self.actionDeviceStoreBank)

        self.retranslateUi(UIMainWindow)

        QMetaObject.connectSlotsByName(UIMainWindow)

    # setupUi

    def retranslateUi(self, UIMainWindow):
        UIMainWindow.setWindowTitle(
            QCoreApplication.translate("UIMainWindow", "Midiverb III", None)
        )
        self.actionSettings.setText(
            QCoreApplication.translate("UIMainWindow", "Settings", None)
        )
        self.actionQuit.setText(
            QCoreApplication.translate("UIMainWindow", "Quit", None)
        )
        # if QT_CONFIG(shortcut)
        self.actionQuit.setShortcut(
            QCoreApplication.translate("UIMainWindow", "Ctrl+Q", None)
        )
        # endif // QT_CONFIG(shortcut)
        self.actionImport.setText(
            QCoreApplication.translate("UIMainWindow", "Open", None)
        )
        # if QT_CONFIG(tooltip)
        self.actionImport.setToolTip(
            QCoreApplication.translate(
                "UIMainWindow", "Import a bank or a program", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        # if QT_CONFIG(shortcut)
        self.actionImport.setShortcut(
            QCoreApplication.translate("UIMainWindow", "Ctrl+O", None)
        )
        # endif // QT_CONFIG(shortcut)
        self.actionBankExport.setText(
            QCoreApplication.translate("UIMainWindow", "Save As", None)
        )
        # if QT_CONFIG(tooltip)
        self.actionBankExport.setToolTip(
            QCoreApplication.translate(
                "UIMainWindow", "Save bank as a separate syx file", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        # if QT_CONFIG(shortcut)
        self.actionBankExport.setShortcut(
            QCoreApplication.translate("UIMainWindow", "Ctrl+Shift+S", None)
        )
        # endif // QT_CONFIG(shortcut)
        self.actionBankSave.setText(
            QCoreApplication.translate("UIMainWindow", "Save", None)
        )
        # if QT_CONFIG(tooltip)
        self.actionBankSave.setToolTip(
            QCoreApplication.translate(
                "UIMainWindow", "Save the current bank data", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        # if QT_CONFIG(shortcut)
        self.actionBankSave.setShortcut(
            QCoreApplication.translate("UIMainWindow", "Ctrl+S", None)
        )
        # endif // QT_CONFIG(shortcut)
        self.actionAbout.setText(
            QCoreApplication.translate("UIMainWindow", "About", None)
        )
        self.actionBufferExport.setText(
            QCoreApplication.translate("UIMainWindow", "Save Buffer", None)
        )
        # if QT_CONFIG(shortcut)
        self.actionBufferExport.setShortcut(
            QCoreApplication.translate("UIMainWindow", "Ctrl+Shift+X", None)
        )
        # endif // QT_CONFIG(shortcut)
        self.actionNew.setText(QCoreApplication.translate("UIMainWindow", "New", None))
        # if QT_CONFIG(tooltip)
        self.actionNew.setToolTip(
            QCoreApplication.translate(
                "UIMainWindow", "Create a new bank from template", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        # if QT_CONFIG(shortcut)
        self.actionNew.setShortcut(
            QCoreApplication.translate("UIMainWindow", "Ctrl+N", None)
        )
        # endif // QT_CONFIG(shortcut)
        self.actionStoreProgram.setText(
            QCoreApplication.translate("UIMainWindow", "Store Program", None)
        )
        # if QT_CONFIG(tooltip)
        self.actionStoreProgram.setToolTip(
            QCoreApplication.translate(
                "UIMainWindow",
                "Save the current buffer to the device and save it in the selected slot",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.actionDeviceStoreBank.setText(
            QCoreApplication.translate("UIMainWindow", "Store Bank", None)
        )
        # if QT_CONFIG(tooltip)
        self.actionDeviceStoreBank.setToolTip(
            QCoreApplication.translate(
                "UIMainWindow", "Send the whole bank to the device", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.actionHelp.setText(
            QCoreApplication.translate("UIMainWindow", "Help", None)
        )
        self.CONFIGURATION.setItemText(
            0, QCoreApplication.translate("UIMainWindow", "EQ > CHRS > DLY > REV", None)
        )
        self.CONFIGURATION.setItemText(
            1,
            QCoreApplication.translate(
                "UIMainWindow", "EQ > CHRS > REV | EQ > CHRS > DLY", None
            ),
        )
        self.CONFIGURATION.setItemText(
            2, QCoreApplication.translate("UIMainWindow", "EQ > CHRS > REV | DLY", None)
        )
        self.CONFIGURATION.setItemText(
            3,
            QCoreApplication.translate(
                "UIMainWindow", "EQ > CHRS > REV | EQ > DLY", None
            ),
        )
        self.CONFIGURATION.setItemText(
            4, QCoreApplication.translate("UIMainWindow", "EQ >REV | CHRS > DLY", None)
        )
        self.CONFIGURATION.setItemText(
            5, QCoreApplication.translate("UIMainWindow", "EQ > DLY | CHRS > REV", None)
        )
        self.CONFIGURATION.setItemText(
            6,
            QCoreApplication.translate(
                "UIMainWindow", "EQ > CHRS > DLY > REV -CH", None
            ),
        )
        self.CONFIGURATION.setItemText(
            7,
            QCoreApplication.translate(
                "UIMainWindow", "EQ > CHRS > REV | EQ > CHRS > DLY -CH", None
            ),
        )
        self.CONFIGURATION.setItemText(
            8,
            QCoreApplication.translate(
                "UIMainWindow", "EQ > CHRS > REV | DLY -CH", None
            ),
        )
        self.CONFIGURATION.setItemText(
            9,
            QCoreApplication.translate(
                "UIMainWindow", "EQ > CHRS > REV | EQ > DLY -CH", None
            ),
        )
        self.CONFIGURATION.setItemText(
            10,
            QCoreApplication.translate(
                "UIMainWindow", "EQ >REV | CHRS > DLY -CH", None
            ),
        )
        self.CONFIGURATION.setItemText(
            11,
            QCoreApplication.translate(
                "UIMainWindow", "EQ > DLY | CHRS > REV -CH", None
            ),
        )
        self.CONFIGURATION.setItemText(
            12,
            QCoreApplication.translate("UIMainWindow", "EQ > DLY > REV | CHRS", None),
        )
        self.CONFIGURATION.setItemText(
            13, QCoreApplication.translate("UIMainWindow", "EQ > CHRS > DLY", None)
        )
        self.CONFIGURATION.setItemText(
            14, QCoreApplication.translate("UIMainWindow", "EQ > CHRS > DLY -CH", None)
        )

        # if QT_CONFIG(tooltip)
        self.CONFIGURATION.setToolTip(
            QCoreApplication.translate(
                "UIMainWindow",
                "Choose routing, there are some parallel and some sequential algorithms, note that some fx blocks may be disabled for some algorithms",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.CHRS_TYPE.setItemText(
            0, QCoreApplication.translate("UIMainWindow", "CHORUS XS", None)
        )
        self.CHRS_TYPE.setItemText(
            1, QCoreApplication.translate("UIMainWindow", "CHORUS S", None)
        )
        self.CHRS_TYPE.setItemText(
            2, QCoreApplication.translate("UIMainWindow", "CHORUS M", None)
        )
        self.CHRS_TYPE.setItemText(
            3, QCoreApplication.translate("UIMainWindow", "CHORUS XM", None)
        )
        self.CHRS_TYPE.setItemText(
            4, QCoreApplication.translate("UIMainWindow", "CHORUS L", None)
        )
        self.CHRS_TYPE.setItemText(
            5, QCoreApplication.translate("UIMainWindow", "CHORUS XL", None)
        )
        self.CHRS_TYPE.setItemText(
            6, QCoreApplication.translate("UIMainWindow", "FLANGER XS", None)
        )
        self.CHRS_TYPE.setItemText(
            7, QCoreApplication.translate("UIMainWindow", "FLANGER S", None)
        )
        self.CHRS_TYPE.setItemText(
            8, QCoreApplication.translate("UIMainWindow", "FLANGER M", None)
        )
        self.CHRS_TYPE.setItemText(
            9, QCoreApplication.translate("UIMainWindow", "FLANGER XM", None)
        )
        self.CHRS_TYPE.setItemText(
            10, QCoreApplication.translate("UIMainWindow", "FLANGER L", None)
        )
        self.CHRS_TYPE.setItemText(
            11, QCoreApplication.translate("UIMainWindow", "FLANGER XL", None)
        )

        # if QT_CONFIG(tooltip)
        self.CHRS_TYPE.setToolTip(
            QCoreApplication.translate(
                "UIMainWindow",
                "Pitch FX types: choruses and flangers, the sizes mean the depth of effect",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        # if QT_CONFIG(tooltip)
        self.CHRS_STEREO.setToolTip(
            QCoreApplication.translate(
                "UIMainWindow", "Switch between mono and stereo", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.CHRS_STEREO.setText(
            QCoreApplication.translate("UIMainWindow", "Stereo", None)
        )
        # if QT_CONFIG(tooltip)
        self.DLY_TIME_T.setToolTip(
            QCoreApplication.translate(
                "UIMainWindow",
                "Delay time in ms, note that for some algorithms the max time is 100ms, for others it's 400",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.DLY_TIME_T.setText(
            QCoreApplication.translate("UIMainWindow", "Time", None)
        )
        # if QT_CONFIG(tooltip)
        self.DLY_TIME.setToolTip(
            QCoreApplication.translate(
                "UIMainWindow",
                "Delay time in ms, note that for some algorithms the max time is 100ms, for others it's 400",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.DLY_TIME_L.setText(QCoreApplication.translate("UIMainWindow", "+0", None))
        # if QT_CONFIG(tooltip)
        self.REV_MIX_T.setToolTip(
            QCoreApplication.translate("UIMainWindow", "Reverb level", None)
        )
        # endif // QT_CONFIG(tooltip)
        self.REV_MIX_T.setText(
            QCoreApplication.translate("UIMainWindow", "Level", None)
        )
        self.REV_MIX_L.setText(QCoreApplication.translate("UIMainWindow", "+0", None))
        # if QT_CONFIG(tooltip)
        self.REV_MIX.setToolTip(
            QCoreApplication.translate("UIMainWindow", "Reverb level", None)
        )
        # endif // QT_CONFIG(tooltip)
        self.DLY_REGEN_L.setText(QCoreApplication.translate("UIMainWindow", "+0", None))
        self.DLY_REGEN_T.setText(
            QCoreApplication.translate("UIMainWindow", "Regen", None)
        )
        # if QT_CONFIG(tooltip)
        self.DLY_REGEN.setToolTip(
            QCoreApplication.translate("UIMainWindow", "Delay feedback amount", None)
        )
        # endif // QT_CONFIG(tooltip)
        self.REV_DECAY_L.setText(QCoreApplication.translate("UIMainWindow", "+0", None))
        # if QT_CONFIG(tooltip)
        self.REV_DECAY.setToolTip(
            QCoreApplication.translate("UIMainWindow", "Reverb decay amount", None)
        )
        # endif // QT_CONFIG(tooltip)
        self.REV_DECAY_T.setText(
            QCoreApplication.translate("UIMainWindow", "Decay", None)
        )
        self.DLY_MIX_T.setText(
            QCoreApplication.translate("UIMainWindow", "Level", None)
        )
        self.DLY_MIX_L.setText(QCoreApplication.translate("UIMainWindow", "+0", None))
        # if QT_CONFIG(tooltip)
        self.DLY_MIX.setToolTip(
            QCoreApplication.translate("UIMainWindow", "Delay level", None)
        )
        # endif // QT_CONFIG(tooltip)
        self.REVERB_TYPE.setItemText(
            0, QCoreApplication.translate("UIMainWindow", "SMALL ROOM", None)
        )
        self.REVERB_TYPE.setItemText(
            1, QCoreApplication.translate("UIMainWindow", "SMALL ROOM DIFF", None)
        )
        self.REVERB_TYPE.setItemText(
            2, QCoreApplication.translate("UIMainWindow", "MEDIUM ROOM", None)
        )
        self.REVERB_TYPE.setItemText(
            3, QCoreApplication.translate("UIMainWindow", "LARGE ROOM", None)
        )
        self.REVERB_TYPE.setItemText(
            4, QCoreApplication.translate("UIMainWindow", "SMALL HALL", None)
        )
        self.REVERB_TYPE.setItemText(
            5, QCoreApplication.translate("UIMainWindow", "SMALL HALL DIFF", None)
        )
        self.REVERB_TYPE.setItemText(
            6, QCoreApplication.translate("UIMainWindow", "MEDIUM HALL", None)
        )
        self.REVERB_TYPE.setItemText(
            7, QCoreApplication.translate("UIMainWindow", "LARGE HALL", None)
        )
        self.REVERB_TYPE.setItemText(
            8, QCoreApplication.translate("UIMainWindow", "MEDIUM CHAMBER", None)
        )
        self.REVERB_TYPE.setItemText(
            9, QCoreApplication.translate("UIMainWindow", "MEDIUM CHAMBER DIFF", None)
        )
        self.REVERB_TYPE.setItemText(
            10, QCoreApplication.translate("UIMainWindow", "LARGE CHAMBER", None)
        )
        self.REVERB_TYPE.setItemText(
            11, QCoreApplication.translate("UIMainWindow", "PERC CHAMBER", None)
        )
        self.REVERB_TYPE.setItemText(
            12, QCoreApplication.translate("UIMainWindow", "PERC PLATE", None)
        )
        self.REVERB_TYPE.setItemText(
            13, QCoreApplication.translate("UIMainWindow", "TIGHT PLATE", None)
        )
        self.REVERB_TYPE.setItemText(
            14, QCoreApplication.translate("UIMainWindow", "SOFT PLATE", None)
        )
        self.REVERB_TYPE.setItemText(
            15, QCoreApplication.translate("UIMainWindow", "VOCAL PLATE", None)
        )
        self.REVERB_TYPE.setItemText(
            16, QCoreApplication.translate("UIMainWindow", "BRIGHT GATE", None)
        )
        self.REVERB_TYPE.setItemText(
            17, QCoreApplication.translate("UIMainWindow", "POWER GATE", None)
        )
        self.REVERB_TYPE.setItemText(
            18, QCoreApplication.translate("UIMainWindow", "MEDIUM REVERSE", None)
        )
        self.REVERB_TYPE.setItemText(
            19, QCoreApplication.translate("UIMainWindow", "SLOW REVERSE", None)
        )

        # if QT_CONFIG(tooltip)
        self.REVERB_TYPE.setToolTip(
            QCoreApplication.translate("UIMainWindow", "Reverb algorithms", None)
        )
        # endif // QT_CONFIG(tooltip)
        # if QT_CONFIG(tooltip)
        self.IN_EQ_T.setToolTip(
            QCoreApplication.translate(
                "UIMainWindow", "Input lowpass filter (-3db)", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.IN_EQ_T.setText(QCoreApplication.translate("UIMainWindow", "LPF", None))
        self.IN_EQ_L.setText(QCoreApplication.translate("UIMainWindow", "+0", None))
        # if QT_CONFIG(tooltip)
        self.IN_EQ.setToolTip(
            QCoreApplication.translate(
                "UIMainWindow", "Input lowpass filter (-3db)", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        # if QT_CONFIG(tooltip)
        self.OUT_EQ_T.setToolTip(
            QCoreApplication.translate(
                "UIMainWindow",
                "Delay feedback filter or reverb regen filter if the reverb is on",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.OUT_EQ_T.setText(QCoreApplication.translate("UIMainWindow", "LPF", None))
        self.OUT_EQ_L.setText(QCoreApplication.translate("UIMainWindow", "+0", None))
        # if QT_CONFIG(tooltip)
        self.OUT_EQ.setToolTip(
            QCoreApplication.translate(
                "UIMainWindow",
                "Delay feedback filter or reverb regen filter if the reverb is on",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.MOD_SOURCE.setItemText(
            0, QCoreApplication.translate("UIMainWindow", "VOLUME (CC7)", None)
        )
        self.MOD_SOURCE.setItemText(
            1, QCoreApplication.translate("UIMainWindow", "PITCH BEND", None)
        )
        self.MOD_SOURCE.setItemText(
            2, QCoreApplication.translate("UIMainWindow", "MOD WHEEL (CC1)", None)
        )
        self.MOD_SOURCE.setItemText(
            3, QCoreApplication.translate("UIMainWindow", "NOTE NUMBER", None)
        )
        self.MOD_SOURCE.setItemText(
            4, QCoreApplication.translate("UIMainWindow", "VELOCITY", None)
        )
        self.MOD_SOURCE.setItemText(
            5, QCoreApplication.translate("UIMainWindow", "AFTERTOUCH", None)
        )
        self.MOD_SOURCE.setItemText(
            6, QCoreApplication.translate("UIMainWindow", "SUSTAIN PEDAL (CC64)", None)
        )
        self.MOD_SOURCE.setItemText(
            7, QCoreApplication.translate("UIMainWindow", "BREATH", None)
        )

        # if QT_CONFIG(tooltip)
        self.MOD_SOURCE.setToolTip(
            QCoreApplication.translate("UIMainWindow", "Modulation source", None)
        )
        # endif // QT_CONFIG(tooltip)
        self.MOD_DEST.setItemText(
            0, QCoreApplication.translate("UIMainWindow", "OFF", None)
        )
        self.MOD_DEST.setItemText(
            1, QCoreApplication.translate("UIMainWindow", "REV DECAY", None)
        )
        self.MOD_DEST.setItemText(
            2, QCoreApplication.translate("UIMainWindow", "DLY TIME", None)
        )
        self.MOD_DEST.setItemText(
            3, QCoreApplication.translate("UIMainWindow", "DLY REGEN", None)
        )
        self.MOD_DEST.setItemText(
            4, QCoreApplication.translate("UIMainWindow", "CHRS SPEED", None)
        )
        self.MOD_DEST.setItemText(
            5, QCoreApplication.translate("UIMainWindow", "REV LEVEL", None)
        )
        self.MOD_DEST.setItemText(
            6, QCoreApplication.translate("UIMainWindow", "DLY LEVEl", None)
        )

        # if QT_CONFIG(tooltip)
        self.MOD_DEST.setToolTip(
            QCoreApplication.translate(
                "UIMainWindow",
                "Modulation destination, note that some destinations may produce artifacts when modulated",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.CHORUS_T.setText(
            QCoreApplication.translate("UIMainWindow", "CHORUS", None)
        )
        self.DLY_T.setText(QCoreApplication.translate("UIMainWindow", "DELAY", None))
        self.REV_T.setText(QCoreApplication.translate("UIMainWindow", "REVERB", None))
        self.MOD_T.setText(
            QCoreApplication.translate("UIMainWindow", "MODULATION", None)
        )
        # if QT_CONFIG(tooltip)
        self.MOD_AMT.setToolTip(
            QCoreApplication.translate("UIMainWindow", "Modulation depth", None)
        )
        # endif // QT_CONFIG(tooltip)
        self.MOD_AMT_L.setText(QCoreApplication.translate("UIMainWindow", "+0", None))
        # if QT_CONFIG(tooltip)
        self.CHRS_SPEED.setToolTip(
            QCoreApplication.translate("UIMainWindow", "Chorus / flanger speed", None)
        )
        # endif // QT_CONFIG(tooltip)
        self.CHRS_SPEED_L.setText(
            QCoreApplication.translate("UIMainWindow", "+0", None)
        )
        # if QT_CONFIG(tooltip)
        self.PROG_T_2.setToolTip(
            QCoreApplication.translate("UIMainWindow", "Reverb algorithms", None)
        )
        # endif // QT_CONFIG(tooltip)
        self.PROG_T_2.setText(
            QCoreApplication.translate("UIMainWindow", "ALGORITHM", None)
        )
        # if QT_CONFIG(tooltip)
        self.PROG_T_3.setToolTip(
            QCoreApplication.translate(
                "UIMainWindow",
                "Choose routing, there are some parallel and some sequential algorithms, note that some fx blocks may be disabled for some algorithms",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.PROG_T_3.setText(
            QCoreApplication.translate("UIMainWindow", "ROUTING", None)
        )
        # if QT_CONFIG(tooltip)
        self.BANK_PATH.setToolTip(
            QCoreApplication.translate("UIMainWindow", "Loaded bank path", None)
        )
        # endif // QT_CONFIG(tooltip)
        self.BANK_PATH.setText(
            QCoreApplication.translate("UIMainWindow", "DEFAULT BANK", None)
        )
        # if QT_CONFIG(tooltip)
        self.PROG_RECALL.setToolTip(
            QCoreApplication.translate(
                "UIMainWindow", "Discard the buffer and recall the stored program", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.PROG_RECALL.setText(
            QCoreApplication.translate("UIMainWindow", "RECALL", None)
        )
        # if QT_CONFIG(tooltip)
        self.PROG_SYNC.setToolTip(
            QCoreApplication.translate(
                "UIMainWindow",
                "Sync buffer to the device, this does not save the program in the program slot",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.PROG_SYNC.setText(QCoreApplication.translate("UIMainWindow", "SYNC", None))
        self.menuFile.setTitle(QCoreApplication.translate("UIMainWindow", "File", None))
        self.menuDevice.setTitle(
            QCoreApplication.translate("UIMainWindow", "Device", None)
        )

    # retranslateUi
