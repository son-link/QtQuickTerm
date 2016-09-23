#!/bin/env python3
import sys, signal, os, configparser
from PyQt5 import QtCore, uic
from PyQt5.QtWidgets import (QApplication, QMenu, QSystemTrayIcon, QDialog, QMainWindow, QAction, QFontDialog, QFontComboBox)
from PyQt5.QtGui import QIcon, QPixmap, QCursor, QFont, QFontInfo
import QTermWidget
from GUI import Ui_Dialog

signal.signal(signal.SIGINT, signal.SIG_DFL)

Ui_MainWindow, QtBaseClass = uic.loadUiType('QtQuickTerm.ui')
Ui_About, QtBaseClass = uic.loadUiType('about.ui')
Ui_Config, QtBaseClass = uic.loadUiType('config.ui')

# Configutarion
config = {}
cfg = configparser.ConfigParser()

class About(QDialog, Ui_About):
	
	def __init__(self):
		
		QMainWindow.__init__(self)
		self.setupUi(self)

class Config(QDialog, Ui_Config):
	def __init__(self):
		
		QMainWindow.__init__(self)
		self.setupUi(self)
		self.font = QFont()
		self.font.setFamily(config['font']);
		self.font.setPointSize(config['fontsize'])
		self.fontPreview.setFont(self.font)
		self.fontComboBox.setCurrentIndex(self.fontComboBox.findText(config['font']))
		self.fontSize.setValue(config['fontsize'])
		self.schemeComboBox.setCurrentIndex(self.schemeComboBox.findText(config['colorscheme']))
		self.widthSpinBox.setValue(config['width'])
		self.widthSpinBox.setMaximum(ws)
		self.heightSpinBox.setValue(config['height'])
		self.heightSpinBox.setMaximum(hs)
		
		self.fontComboBox.currentFontChanged.connect(self.fontPrev)
		self.fontSize.valueChanged.connect(self.fontPrev)
		self.buttonBox.accepted.connect(self.accept)
		
	def fontPrev(self):
		# Update font preview
		f = self.fontComboBox.currentFont()
		self.font.setFamily(QFontInfo(f).family());
		self.font.setPointSize(self.fontSize.value())
		self.fontPreview.setFont(self.font)
		
	def accept(self):
		# If user lick om Accep button save the new config
		font = self.fontComboBox.currentFont()
		print(QFontInfo(font).family())
		config['font'] = QFontInfo(font).family()
		config['fontSize'] = self.fontSize.value()
		config['colorscheme'] = self.schemeComboBox.currentText()
		config['width'] = self.widthSpinBox.value()
		config['height'] = self.heightSpinBox.value()
		
		# Write the config to configutarion file
		f = open('qtquicktermrc', "w")
		for k in config:
			cfg['qtquickterm'][k] = str(config[k])
			
		cfg.write(f)
		f.close()
		
		self.hide()


class QtQuickTerm(QDialog, Ui_MainWindow):
	
	def __init__(self, parent=None):
		
		QMainWindow.__init__(self)
		super(QtQuickTerm, self).__init__(parent,QtCore.Qt.SplashScreen)
		self.setupUi(self)
		self.setFixedSize(config['width'], config['height'])
		self.closeButton.clicked.connect(self.closeEvent)
		
		self.isActive = False
		self.config = Config()
		self.about = About()
		
		self.font = QFont()
		self.font.setFamily(config['font']);
		self.font.setPointSize(config['fontsize']);
		
		self.term = QTermWidget.QTermWidget()
		self.term.setColorScheme(config['colorscheme'])
		self.term.finished.connect(self.resetTerm)
		#self.term.termLostFocus()
		self.term.setScrollBarPosition(self.term.ScrollBarRight)
		self.term.setWorkingDirectory(os.environ['HOME'])
		self.gridLayout.addWidget(self.term)
		self.term.setTerminalFont(self.font)
				
		# The SystemTrayIcon
		self.systray_menu = QMenu(self)
		
		self.config_app = self.systray_menu.addAction(QIcon.fromTheme('configure'), self.tr("Configure"))
		self.config_app.triggered.connect(self.changeConfig)
		self.about_app = self.systray_menu.addAction(QIcon.fromTheme('gtk-about'), self.tr("About"))
		self.about_app.triggered.connect(self.about.show)
		self.exit_app = self.systray_menu.addAction(QIcon.fromTheme('exit'), self.tr("Exit"))
		self.exit_app.triggered.connect(exit)
		
		icon = QIcon.fromTheme('utilities-terminal-symbolic')
		self.systray = QSystemTrayIcon(self)
		self.systray.setIcon(icon)
		self.systray.activated.connect(self.systemIcon)
		self.systray.setContextMenu(self.systray_menu)
		self.systray.show()
		
		# Terminal menu
		copyAction = QAction(QIcon.fromTheme('editcopy'), self.tr('Copy'), self, shortcut="Ctrl+Shift+C",
			triggered=self.term.copyClipboard)
		self.addAction(copyAction)
		
		pasteAction = QAction(QIcon.fromTheme('editpaste'), self.tr('Paste'), self, shortcut='Ctrl+Shift+V',
			triggered=self.term.pasteClipboard)
		self.addAction(pasteAction)
		
		clearAction = QAction(QIcon.fromTheme('edit-clear-all-symbolic'), self.tr('Clear'), self, shortcut="Ctrl+Shift+R",
			triggered=self.term.clear)
		self.addAction(clearAction)
		
		self.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
		
	def systemIcon(self, reason):
		
		# Move the window to the cursor position
		currentPos = QCursor.pos()
		w = config['width']
		h = config['height']
		xpos = 0
		ypos = 0
		xc = currentPos.x()
		yc = currentPos.y()
		
		if xc+w >= ws:
			xpos = ws-w
			
		elif xc-w <= 0:
			xpos=0
			
		if yc+h >= hs:
			ypos = hs-h
			
		elif yc-h <= 0:
			ypos=0
		
		self.setGeometry(xpos, ypos, w, h)
		self.setFixedSize(w, h)
		
		if reason == QSystemTrayIcon.Trigger:
			# if click on the SystemTrayIcon
			# The window is not active
			if not self.isActive:
				self.show()
				self.term.setFocus()
				self.isActive = True
			else:
				self.hide()
				self.isActive = False
	
	def changeConfig(self):
		c = self.config.exec_()
		self.font.setFamily(config['font'])
		self.font.setPointSize(config['fontsize'])
		self.term.setTerminalFont(self.font)
		self.term.setColorScheme(config['colorscheme'])
		self.setFixedSize(config['width'], config['height'])
		
	def resetTerm(self):
		# if user execute the exit command on terminal create the widget again
		self.hide()
		self.gridLayout.removeWidget(self.term)
		self.term = QTermWidget.QTermWidget()
		self.term.setColorScheme(config['colorscheme'])
		self.term.finished.connect(self.resetTerm)
		self.term.setWorkingDirectory(os.environ['HOME'])
		self.term.setTerminalFont(self.font)
		self.gridLayout.addWidget(self.term)
		
	def closeEvent(self, event):
		# don't exit
		self.hide()
		if event:
			event.ignore()
			
		self.isActive = False
		
if __name__ == '__main__':
	app = QApplication(sys.argv)
	
	# Get avaliable resolution
	screen_resolution = app.desktop().availableGeometry()
	ws, hs = screen_resolution.width(), screen_resolution.height()
	
	app.setQuitOnLastWindowClosed(False)
	translator = QtCore.QTranslator()
	app.installTranslator(translator)
	lang = QtCore.QLocale.system().name().split('_')[0]
	translator.load('qtquickterm_%s.qm' % lang)
	
	# Load config
	cfg.read('qtquicktermrc')
	config = {
		'colorscheme': cfg['qtquickterm']['colorscheme'],
		'font': cfg['qtquickterm']['font'],
		'fontsize': int(cfg['qtquickterm']['fontsize']),
		'width': int(cfg['qtquickterm']['width']),
		'height': int(cfg['qtquickterm']['height'])
	}
	
	qqt = QtQuickTerm()
	sys.exit(app.exec_())
	
