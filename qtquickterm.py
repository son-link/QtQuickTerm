#!/bin/env python3
import sys, signal
from PyQt5 import QtCore, uic
from PyQt5.QtWidgets import (QApplication, QMenu, QSystemTrayIcon, QDialog, QMainWindow, QAction, QFontDialog, QFontComboBox)
from PyQt5.QtGui import QIcon, QPixmap, QCursor, QFont
import QTermWidget
from GUI import Ui_Dialog

signal.signal(signal.SIGINT, signal.SIG_DFL)

Ui_MainWindow, QtBaseClass = uic.loadUiType('QtQuickTerm.ui')
Ui_About, QtBaseClass2 = uic.loadUiType('about.ui')

config = {
	'width': 600,
	'height': 300,
	'colorScheme': 'Linux'
}

class About(QDialog, Ui_About):
	
	def __init__(self):
		
		QMainWindow.__init__(self)
		self.setupUi(self)	

class QtQuickTerm(QDialog, Ui_MainWindow):
	
	def __init__(self, parent=None):
		
		QMainWindow.__init__(self)
		super(QtQuickTerm, self).__init__(parent,QtCore.Qt.SplashScreen)

		self.setupUi(self)
		self.closeButton.clicked.connect(self.closeEvent)
		
		self.isActive = False
		self.about = About()
		
		self.term = QTermWidget.QTermWidget()
		self.term.setColorScheme(config['colorScheme'])
		self.term.finished.connect(self.resetTerm)
		self.term.setScrollBarPosition(self.term.ScrollBarRight)
		self.gridLayout.addWidget(self.term)
				
		# The SystemTrayIcon
		self.systray_menu = QMenu(self)
		
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
				
		copyAction = QAction(QIcon.fromTheme('editcopy'), self.tr('Copy'), self, shortcut="Ctrl+Shift+C",
		triggered=self.term.copyClipboard)
		self.addAction(copyAction)
		
		pasteAction = QAction(QIcon.fromTheme('editpaste'), self.tr('Paste'), self, shortcut='Ctrl+Shift+V',
		triggered=self.term.pasteClipboard)
		self.addAction(pasteAction)
		
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
		screen_resolution = app.desktop().availableGeometry()
		ws, hs = screen_resolution.width(), screen_resolution.height()
		
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
				
		elif reason == QSystemTrayIcon.Context:
			# If click in the system tray icon with the right mouse button
			pass
		
	def resetTerm(self):
		# if user execute the exit command on terminal create the widget again
		self.term = QTermWidget.QTermWidget()
		self.term.setColorScheme(config['colorScheme'])
		self.term.finished.connect(self.resetTerm)
		self.term.startShellProgram()
		
	def closeEvent(self, event):
		# don't exit
		self.hide()
		if event:
			event.ignore()
			
		self.isActive = False
		
if __name__ == '__main__':
	app = QApplication(sys.argv)
	app.setQuitOnLastWindowClosed(False)
	translator = QtCore.QTranslator()
	app.installTranslator(translator)
	lang = QtCore.QLocale.system().name().split('_')[0]
	print(lang)
	translator.load('qtquickterm_%s.qm' % lang)
	
	qqt = QtQuickTerm()
	sys.exit(app.exec_())
