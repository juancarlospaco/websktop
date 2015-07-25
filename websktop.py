#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""Websktop."""


__version__ = '1.0.0'
__license__ = ' GPLv3+ LGPLv3+ '
__author__ = ' Juan Carlos '
__email__ = ' juancarlospaco@gmail.com '
__url__ = 'https://github.com/juancarlospaco/websktop'
__source__ = ('https://raw.githubusercontent.com/websktop/'
              'websktop/master/websktop.py')


import os
import signal
import socket
import sys
from ctypes import byref, cdll, create_string_buffer
from getpass import getuser
from platform import platform, python_version
from random import randint
from tempfile import mkdtemp
from webbrowser import open_new_tab

from PyQt5.QtCore import Qt, QThread, QTimer, QUrl
from PyQt5.QtGui import QColor, QCursor, QIcon, QPainter, QPalette, QPen
from PyQt5.QtNetwork import QNetworkProxyFactory
from PyQt5.QtWebKit import QWebSettings
from PyQt5.QtWebKitWidgets import QWebView
from PyQt5.QtWidgets import (QApplication, QDesktopWidget, QFileDialog,
                             QFontDialog, QLabel, QMainWindow, QMenu,
                             QMessageBox, QShortcut, QStyle, QToolBar, QWidget)

try:
    import resource
except ImportError:
    resource = None
try:
    import qdarkstyle  # https://github.com/ColinDuquesnoy/QDarkStyleSheet
except ImportError:    # sudo pip3 install qdarkstyle
    qdarkstyle = None  # 100% optional, but cute.


HTML_PLACEHOLDER = """<meta charset=utf-8><meta http-equiv=refresh content=3>
<center style='color:#fff'><h1><i>Powered by ImportD, Django, Qt5, Python3."""


##############################################################################
# GUI


class WebView(QWebView):

    """Main QWebView."""

    def __init__(self, parent=None):
        """Initialize QWebView."""
        super(WebView, self).__init__(parent)
        self.setStyleSheet("background-color: transparent")
        QNetworkProxyFactory.setUseSystemConfiguration(True)
        settings, temporary_directory = self.settings(), mkdtemp()
        settings.setDefaultTextEncoding("utf-8")
        settings.setIconDatabasePath(temporary_directory)
        settings.setLocalStoragePath(temporary_directory)
        settings.setOfflineStoragePath(temporary_directory)
        settings.setMaximumPagesInCache(settings.maximumPagesInCache() * 2)
        settings.setOfflineWebApplicationCachePath(temporary_directory)
        settings.setAttribute(QWebSettings.DeveloperExtrasEnabled, True)
        settings.setAttribute(QWebSettings.LocalStorageEnabled, True)
        settings.setAttribute(QWebSettings.OfflineStorageDatabaseEnabled, True)
        settings.setAttribute(QWebSettings.PluginsEnabled, True)
        settings.setAttribute(QWebSettings.DnsPrefetchEnabled, True)
        settings.setAttribute(QWebSettings.JavascriptCanOpenWindows, True)
        settings.setAttribute(QWebSettings.JavascriptCanCloseWindows, True)
        settings.setAttribute(QWebSettings.JavascriptCanAccessClipboard, True)
        settings.setAttribute(QWebSettings.SpatialNavigationEnabled, True)
        settings.setAttribute(QWebSettings.PrivateBrowsingEnabled, True)
        settings.setAttribute(QWebSettings.LocalContentCanAccessFileUrls, True)
        settings.setAttribute(QWebSettings.CSSGridLayoutEnabled, True)
        settings.setAttribute(QWebSettings.ScrollAnimatorEnabled, True)
        settings.setAttribute(
            QWebSettings.LocalContentCanAccessRemoteUrls, True)
        settings.setAttribute(
            QWebSettings.OfflineWebApplicationCacheEnabled, True)
        self.setHtml(HTML_PLACEHOLDER.strip(), QUrl("http://127.0.0.1:8000/"))
        settings.setUserStyleSheetUrl(QUrl(  # HTML Transparent Background.
            "data:text/css;charset=utf-8;base64,"
            "Ym9keXtiYWNrZ3JvdW5kOnRyYW5zcGFyZW50fQ=="))
        self.page().setForwardUnsupportedContent(True)


class MainWindow(QMainWindow):

    """Main Window."""

    def __init__(self, parent=None):
        """Initialize MainWindow."""
        super(MainWindow, self).__init__(parent)
        self.ram_info, self.ram_timer = QLabel(self), QTimer(self)
        self.menubar, self.view = QMenu(self), WebView(self)
        self.ram_timer.timeout.connect(self.update_statusbar)
        self.ram_timer.start(60000)  # Every 60 seconds
        self.statusBar().insertPermanentWidget(0, self.ram_info)
        self.setMinimumSize(640, 480)
        self.setMaximumSize(QDesktopWidget().screenGeometry().width() * 2,
                            QDesktopWidget().screenGeometry().height() * 2)
        self.palette().setBrush(QPalette.Base, Qt.transparent)
        self.setPalette(self.palette())  # Transparent palette
        self.setAttribute(Qt.WA_OpaquePaintEvent, False)  # no opaque paint
        self.setAttribute(Qt.WA_TranslucentBackground, True)  # translucent
        QShortcut("Ctrl+q", self, activated=self.close)
        self.make_toolbar()
        self.make_menubar()
        self.update_statusbar()
        self.setCentralWidget(self.view)
        if qdarkstyle:
            self.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())

    def paintEvent(self, event):
        """Paint transparent background,animated pattern,background text."""
        painter, font = QPainter(self), self.font()
        painter.fillRect(event.rect(), Qt.transparent)  # fill transparent rect
        painter.setPen(QPen(QColor(randint(9, 255), randint(9, 255), 255)))
        painter.rotate(30)  # Rotate painter ~30 Degree
        font.setBold(True)  # Set painter Font for text
        font.setPixelSize(100)
        painter.setFont(font)
        painter.drawText(99, 99, "Python Qt")  # draw the background text
        painter.rotate(-30)  # Rotate -30 the QPen back
        painter.setPen(Qt.NoPen)  # set the pen to no pen
        painter.setBrush(QColor("black"))  # Background Color
        painter.setOpacity(0.9)  # Background Opacity
        painter.drawRoundedRect(self.rect(), 25, 25)  # Back Rounded Borders
        for i in range(2048):  # animated random dots background pattern
            x = randint(10, self.size().width() - 10)
            y = randint(10, self.size().height() - 10)
            painter.setPen(QPen(QColor(randint(9, 255), randint(9, 255), 255)))
            painter.drawPoint(x, y)
        QMainWindow.paintEvent(self, event)

    def make_toolbar(self, list_of_actions=None):
        """Make or Update the main Tool Bar."""
        self.toolbar = QToolBar(self)
        self.left_spacer, self.right_spacer = QWidget(self), QWidget(self)
        self.left_spacer.setSizePolicy(1 | 2, 1 | 2)  # Expanding, Expanding
        self.right_spacer.setSizePolicy(1 | 2, 1 | 2)  # Expanding, Expanding
        self.toolbar.addAction("Menu",
                               lambda: self.menubar.exec_(QCursor.pos()))
        self.toolbar.addWidget(self.left_spacer)
        self.toolbar.addSeparator()
        self.toolbar.addAction(QIcon.fromTheme("help-contents"),
                               "Help and Docs", lambda: open_new_tab(__url__))
        self.toolbar.addAction(QIcon.fromTheme("help-about"), "About Qt 5",
                               lambda: QMessageBox.aboutQt(self))
        self.toolbar.addAction(QIcon.fromTheme("help-about"), "About Python 3",
                               lambda: open_new_tab('http://python.org/about'))
        self.toolbar.addAction(QIcon.fromTheme("application-exit"),
                               "Quit", self.close)
        self.toolbar.addSeparator()
        if list_of_actions and len(list_of_actions):
            for action in list_of_actions:  # if list_of_actions, add actions.
                self.toolbar.addAction(action)
            self.toolbar.addSeparator()
        self.toolbar.addWidget(self.right_spacer)
        self.addToolBar(self.toolbar)
        if sys.platform.startswith("win"):
            self.toolbar.hide()  # windows dont have QIcon.fromTheme,so hide.
        return self.toolbar

    def make_menubar(self, list_of_actions=None):
        """Make or Update the main Tool Bar."""
        self.menuBar().addMenu("&File").addAction("Exit", self.close)
        self.menubar.addMenu("&File").addAction("Exit", self.close)
        viewMenu = self.menuBar().addMenu("&View")
        viewMenu.addAction(
            "Toggle ToolBar", lambda:
                self.toolbar.setVisible(not self.toolbar.isVisible()))
        viewMenu.addAction(
            "Toggle StatusBar", lambda:
                self.statusBar().setVisible(not self.statusBar().isVisible()))
        viewMenu.addAction(
            "Toggle MenuBar", lambda:
                self.menuBar().setVisible(not self.menuBar().isVisible()))
        viewMenu2 = self.menubar.addMenu("&View")
        for action in viewMenu.actions():
            viewMenu2.addAction(action)
        windowMenu = self.menuBar().addMenu("&Window")
        windowMenu.addAction("Minimize", lambda: self.showMinimized())
        windowMenu.addAction("Maximize", lambda: self.showMaximized())
        windowMenu.addAction("Restore", lambda: self.showNormal())
        windowMenu.addAction("Full-Screen", lambda: self.showFullScreen())
        windowMenu.addAction("Center", lambda: self.center())
        windowMenu.addAction("Top-Left", lambda: self.move(0, 0))
        windowMenu.addAction("To Mouse", lambda: self.move(QCursor.pos()))
        windowMenu.addSeparator()
        windowMenu.addAction("Increase size", lambda: self.resize(
            self.size().width() * 1.5, self.size().height() * 1.5))
        windowMenu.addAction("Decrease size", lambda: self.resize(
            self.size().width() // 1.5, self.size().height() // 1.5))
        windowMenu.addAction("Minimum size", lambda:
                             self.resize(self.minimumSize()))
        windowMenu.addAction("Maximum size", lambda:
                             self.resize(self.maximumSize()))
        windowMenu.addAction("Horizontal Wide", lambda: self.resize(
            self.maximumSize().width(), self.minimumSize().height()))
        windowMenu.addAction("Vertical Tall", lambda: self.resize(
            self.minimumSize().width(), self.maximumSize().height()))
        windowMenu.addSeparator()
        windowMenu.addAction("Disable Resize", lambda:
                             self.setFixedSize(self.size()))
        windowMenu2 = self.menubar.addMenu("&Window")
        for action in windowMenu.actions():
            windowMenu2.addAction(action)
        optionMenu = self.menuBar().addMenu("&Options")
        optionMenu.addAction("Set Interface Font...", lambda:
                             self.setFont(QFontDialog.getFont(self)[0]))
        optionMenu.addAction("Load CSS Skin...", lambda:
                             self.setStyleSheet(self.skin()))
        optionMenu.addAction("Take ScreenShoot...", lambda: self.grab().save(
            QFileDialog.getSaveFileName(self, "Save", os.path.expanduser("~"),
                                        "(*.png) PNG image file", "png")[0]))
        optionMenu2 = self.menubar.addMenu("&Options")
        for action in optionMenu.actions():
            optionMenu2.addAction(action)
        helpMenu = self.menuBar().addMenu("&Help")
        helpMenu.addAction("About Qt 5", lambda: QMessageBox.aboutQt(self))
        helpMenu.addAction("About Python 3", lambda:
                           open_new_tab('https://www.python.org/about'))
        helpMenu.addSeparator()
        if sys.platform.startswith('linux'):
            helpMenu.addAction("View Source Code",
                               lambda: open_new_tab(__file__))
        helpMenu.addAction("View GitHub Repo", lambda: open_new_tab(__url__))
        helpMenu.addAction("Report Bugs", lambda:
                           open_new_tab(__url__ + '/issues?state=open'))
        helpMenu2 = self.menubar.addMenu("&Help")
        for action in helpMenu.actions():
            helpMenu2.addAction(action)
        return self.menuBar()

    def update_statusbar(self, custom_message=None):
        """Make or Update the Status Bar."""
        statusbar = self.statusBar()
        if resource:
            ram_use = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss *
                          resource.getpagesize() / 1024 / 1024)
            ram_byt = os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES')
            ram_all = int(ram_byt / 1024 / 1024)
            self.ram_info.setText("{0} / {1} Mb".format(ram_use, ram_all))
            self.ram_info.setToolTip(
                "{0} of {1} MegaBytes of RAM Memory.".format(ram_use, ram_all))
        if custom_message and len(custom_message):
            return statusbar.showMessage(custom_message)
        return statusbar.showMessage(__doc__)

    def skin(self, filename=None):
        """Open QSS from filename,if no QSS return None,if no filename ask."""
        if not filename:
            filename = str(QFileDialog.getOpenFileName(
                self, __doc__ + " - Open QSS Skin", os.path.expanduser("~"),
                "CSS Cascading Style Sheet for Qt 5 (*.qss);;All (*.*)")[0])
        if filename and os.path.isfile(filename):
            with open(filename, 'r', encoding="utf-8-sig") as file_to_read:
                text = file_to_read.read().strip()
        if text:
            return text

    def center(self):
        """Center and resize the window."""
        self.showNormal()
        self.resize(QDesktopWidget().screenGeometry().width() // 1.25,
                    QDesktopWidget().screenGeometry().height() // 1.25)
        qr = self.frameGeometry()
        qr.moveCenter(QDesktopWidget().availableGeometry().center())
        return self.move(qr.topLeft())

    def closeEvent(self, event):
        """Ask to Quit."""
        return event.accept() if QMessageBox.question(
            self, "Close", "<h1>Quit ?.", QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No) == QMessageBox.Yes else event.ignore()


##############################################################################
# Helpers


def make_post_execution_message(app: str=__doc__.splitlines()[0].strip()):
    """Simple Post-Execution Message with information about RAM and Time.

    >>> make_post_execution_message() >= 0
    True
    """
    ram_use = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss *
                  resource.getpagesize() / 1024 / 1024 if resource else 0)
    ram_all = int(os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES')
                  / 1024 / 1024)
    print("Total Maximum RAM Memory used: ~{0} of {1} MegaBytes.".format(
        ram_use, ram_all))
    print("Thanks for using this App,share your experience!{0}".format("""
    Twitter: https://twitter.com/home?status=I%20Like%20{n}!:%20{u}
    Facebook: https://www.facebook.com/share.php?u={u}&t=I%20Like%20{n}
    G+: https://plus.google.com/share?url={u}""".format(u=__url__, n=app)))


def make_root_check_and_encoding_debug() -> bool:
    """Debug and Log Encodings and Check for root/administrator,return Boolean.

    >>> make_root_check_and_encoding_debug()
    True
    """
    print(__doc__ + __version__)
    print("Python {0} on {1}.".format(python_version(), platform()))
    print("STDIN Encoding: {0}.".format(sys.stdin.encoding))
    print("STDERR Encoding: {0}.".format(sys.stderr.encoding))
    print("STDOUT Encoding:{}".format(getattr(sys.stdout, "encoding", "")))
    print("Default Encoding: {0}.".format(sys.getdefaultencoding()))
    print("FileSystem Encoding: {0}.".format(sys.getfilesystemencoding()))
    print("PYTHONIOENCODING Encoding: {0}.".format(
        os.environ.get("PYTHONIOENCODING", None)))
    os.environ["PYTHONIOENCODING"] = "utf-8"
    if not sys.platform.startswith("win"):  # root check
        if not os.geteuid():
            print("Runing as root is not Recommended,NOT Run as root!.")
            return False
    elif sys.platform.startswith("win"):  # administrator check
        if getuser().lower().startswith("admin"):
            print("Runing as Administrator is not Recommended!.")
            return False
    return True


def set_process_name_and_cpu_priority(name: str) -> bool:
    """Set process name and cpu priority.

    >>> set_process_name_and_cpu_priority("test_test")
    True
    """
    try:
        os.nice(19)  # smooth cpu priority
        libc = cdll.LoadLibrary("libc.so.6")  # set process name
        buff = create_string_buffer(len(name.lower().strip()) + 1)
        buff.value = bytes(name.lower().strip().encode("utf-8"))
        libc.prctl(15, byref(buff), 0, 0, 0)
    except Exception:
        return False  # this may fail on windows and its normal, so be silent.
    else:
        print("Process Name set to: {0}.".format(name))
        return True


def set_single_instance(name: str, single_instance: bool=True, port: int=8888):
    """Set process name and cpu priority, return socket.socket object or None.

    >>> isinstance(set_single_instance("test"), socket.socket)
    True
    """
    __lock = None
    if single_instance:
        try:  # Single instance app ~crossplatform, uses udp socket.
            print("Creating Abstract UDP Socket Lock for Single Instance.")
            __lock = socket.socket(
                socket.AF_UNIX if sys.platform.startswith("linux")
                else socket.AF_INET, socket.SOCK_STREAM)
            __lock.bind(
                "\0_{name}__lock".format(name=str(name).lower().strip())
                if sys.platform.startswith("linux") else ("127.0.0.1", port))
        except socket.error as e:
            print(e)
        else:
            print("Socket Lock for Single Instance: {}.".format(__lock))
    else:  # if multiple instance want to touch same file bad things can happen
        print("Multiple instance on same file can cause Race Condition.")
    return __lock


##############################################################################
# Call to work


class DThread(QThread):

    """QThread to run ImportD."""

    def __init__(self, parent=None, importd=None):
        """Initialize DThread."""
        super(DThread, self).__init__(parent)
        self.importd, self.parent = importd, parent

    def run(self):
        """Take D instance and run it on a separate Thread."""
        self.importd.main()


def main(d):
    """Main Loop."""
    make_root_check_and_encoding_debug()
    set_process_name_and_cpu_priority("websktop")
    set_single_instance("websktop")
    signal.signal(signal.SIGINT, signal.SIG_DFL)  # CTRL+C work to quit app
    app = QApplication(sys.argv)
    app.setApplicationName("websktop")
    app.setOrganizationName("websktop")
    app.setOrganizationDomain("websktop")
    # app.instance().setQuitOnLastWindowClosed(False)  # no quit on dialog quit
    icon = QIcon(app.style().standardPixmap(QStyle.SP_FileIcon))
    app.setWindowIcon(icon)
    window = MainWindow()
    window.show()
    importd_thread = DThread(app, d)
    importd_thread.finished.connect(app.exit)  # if ImportD Quits then Quit GUI
    app.aboutToQuit.connect(importd_thread.exit)  # UI Quits then Quit ImportD
    importd_thread.start()
    make_post_execution_message()
    sys.exit(app.exec())


if __name__ in '__main__':
    main()
