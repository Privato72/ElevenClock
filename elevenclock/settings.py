import platform
import subprocess
import os
import sys
import locale
import tempfile
import time
from urllib.request import urlopen
from PyQt5 import QtGui
from PyQt5 import QtCore

import psutil
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSignal as Signal


import globals
from win32mica import ApplyMica, MICAMODE

from languages import * 
from tools import *
from tools import _
import welcome

import win32gui

from win32con import GWL_STYLE, WS_BORDER, WS_THICKFRAME, WS_CAPTION, WS_SYSMENU, WS_POPUP

from external.FramelessWindow import QFramelessWindow, QFramelessDialog
from external.blurwindow import GlobalBlur

class SettingsWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.scrollArea = QScrollArea()
        self.vlayout = QVBoxLayout()
        self.vlayout.setContentsMargins(0, 0, 0, 0)
        self.vlayout.setContentsMargins(0, 0, 0, 0)
        self.vlayout.setSpacing(0)
        layout = QVBoxLayout()
        self.updateSize = True
        self.scrollArea.setWidgetResizable(True)
        self.setObjectName("backgroundWindow")
        self.scrollArea.setFrameShape(QFrame.NoFrame)
        self.settingsWidget = QWidget()
        self.settingsWidget.setObjectName("background")
        self.setWindowIcon(QIcon(getPath("icon.ico")))
        layout.addSpacing(0)
        title = QLabel(_("ElevenClock Settings"))
        title.setObjectName("title")
        if lang == lang_zh_TW:
            title.setStyleSheet("font-size: 25pt;font-family: \"Microsoft JhengHei UI\";font-weight: 450;")
        elif lang == lang_zh_CN:
            title.setStyleSheet("font-size: 25pt;font-family: \"Microsoft YaHei UI\";font-weight: 450;")
        else:
            title.setStyleSheet("font-size: 25pt;font-family: \"Segoe UI Variable Text\";font-weight: 450;")
        layout.addWidget(title)
        layout.setSpacing(5)
        layout.setContentsMargins(10, 0, 0, 0)
        layout.addSpacing(0)
        self.resize(900, 600)
        self.setMinimumWidth(520)
        if isWindowDark():
            self.iconMode = "white"
        else:
            self.iconMode = "black"

        self.announcements = QAnnouncements()
        layout.addWidget(self.announcements)



        self.updateButton = QSettingsButton(_("<b>Update to the latest version!</b>"), _("Install update"))
        self.updateButton.setStyleSheet("")
        self.updateButton.clicked.connect(lambda: KillableThread(target=globals.updateIfPossible, args=((True,))).start())
        self.updateButton.hide()
        layout.addWidget(self.updateButton)

        self.generalSettingsTitle = QIconLabel(_("General Settings:"), getPath(f"settings_{self.iconMode}.png"), _("Updates, icon tray, language"))
        layout.addWidget(self.generalSettingsTitle)
        self.selectedLanguage = QSettingsComboBox(_("ElevenClock's language")+" (Language)", _("Change")) # The non-translated (Language) string is there to let people know what the language option is if you accidentaly change the language
        self.selectedLanguage.setStyleSheet("QWidget#stBtn{border-bottom-left-radius: 0px;border-bottom-right-radius: 0px;border-bottom: 0px;}")
        try:
            self.selectedLanguage.setItems(list(languageReference.values()), list(languageReference.keys()).index(langName))
        except Exception as e:
            report(e)
            self.selectedLanguage.setItems(list(languageReference.values()), 0)

        def changeLang(text):
            keys = list(languageReference.keys())
            values = list(languageReference.values())
            for i in range(len(values)):
                if(text == values[i]):
                    setSettingsValue("PreferredLanguage", str(keys[i]), r=False)
                    self.selectedLanguage.showRestartButton()

        def restartElevenClockByLangChange():
            subprocess.run(str("start /B \"\" \""+sys.executable)+"\" --settings", shell=True)
            globals.app.quit()

        self.selectedLanguage.restartButton.clicked.connect(restartElevenClockByLangChange)
        self.selectedLanguage.textChanged.connect(changeLang)
        self.generalSettingsTitle.addWidget(self.selectedLanguage)
        self.enableUpdates = QSettingsCheckBox(_("Automatically check for updates"))
        self.enableUpdates.setChecked(not getSettings("DisableAutoCheckForUpdates"))
        self.enableUpdates.stateChanged.connect(lambda i: setSettings("DisableAutoCheckForUpdates", not bool(i), r = False))
        self.generalSettingsTitle.addWidget(self.enableUpdates)
        self.installUpdates = QSettingsCheckBox(_("Automatically install available updates"))
        self.installUpdates.setChecked(not getSettings("DisableAutoInstallUpdates"))
        self.installUpdates.stateChanged.connect(lambda i: setSettings("DisableAutoInstallUpdates", not bool(i), r = False))
        self.generalSettingsTitle.addWidget(self.installUpdates)
        self.silentUpdates = QSettingsCheckBox(_("Enable really silent updates"))
        self.silentUpdates.setChecked(getSettings("EnableSilentUpdates"))
        self.silentUpdates.stateChanged.connect(lambda i: setSettings("EnableSilentUpdates", bool(i), r = False))
        self.generalSettingsTitle.addWidget(self.silentUpdates)
        self.bypassCNAMECheck = QSettingsCheckBox(_("Bypass update provider authenticity check (NOT RECOMMENDED, AT YOUR OWN RISK)"))
        self.bypassCNAMECheck.setChecked(getSettings("BypassDomainAuthCheck"))
        self.bypassCNAMECheck.stateChanged.connect(lambda i: setSettings("BypassDomainAuthCheck", bool(i), r = False))
        self.generalSettingsTitle.addWidget(self.bypassCNAMECheck)
        self.enableSystemTray = QSettingsCheckBox(_("Show ElevenClock on system tray"))
        self.enableSystemTray.setChecked(not getSettings("DisableSystemTray"))
        self.enableSystemTray.stateChanged.connect(lambda i: setSettings("DisableSystemTray", not bool(i)))
        self.generalSettingsTitle.addWidget(self.enableSystemTray)
        self.disableTaskMgr = QSettingsCheckBox(_("Hide extended options from the clock right-click menu (needs a restart to be aplied)"))
        self.disableTaskMgr.setChecked(getSettings("HideTaskManagerButton"))
        self.disableTaskMgr.stateChanged.connect(lambda i: setSettings("HideTaskManagerButton", bool(i)))
        self.generalSettingsTitle.addWidget(self.disableTaskMgr)
        self.startupButton = QSettingsButton(_("Change startup behaviour"), _("Change"))
        self.startupButton.clicked.connect(lambda: os.startfile("ms-settings:startupapps"))
        self.generalSettingsTitle.addWidget(self.startupButton)


        self.clockSettingsTitle = QIconLabel(_("Clock Settings:"), getPath(f"clock_{self.iconMode}.png"), _("Fullscreen behaviour, clock position, 1st monitor clock, other miscellanious settings"))
        layout.addWidget(self.clockSettingsTitle)
        self.legacyHideOnFullScreen = QSettingsCheckBox(_("Hide the clock in fullscreen mode"))
        self.legacyHideOnFullScreen.setChecked(not getSettings("DisableHideOnFullScreen"))
        self.legacyHideOnFullScreen.stateChanged.connect(lambda i: setSettings("DisableHideOnFullScreen", not bool(i)))
        self.clockSettingsTitle.addWidget(self.legacyHideOnFullScreen)
        self.newFullScreenHide = QSettingsCheckBox(_("Hide the clock when a program occupies all screens"))
        self.newFullScreenHide.setChecked(getSettings("NewFullScreenMethod"))
        self.newFullScreenHide.stateChanged.connect(lambda i: setSettings("NewFullScreenMethod", bool(i)))
        self.clockSettingsTitle.addWidget(self.newFullScreenHide)
        self.forceClockToShow = QSettingsCheckBox(_("Show the clock when the taskbar is set to hide automatically"))
        self.forceClockToShow.setChecked(getSettings("DisableHideWithTaskbar"))
        self.forceClockToShow.stateChanged.connect(lambda i: setSettings("DisableHideWithTaskbar", bool(i)))
        self.clockSettingsTitle.addWidget(self.forceClockToShow)
        self.showDesktopButton = QSettingsCheckBox(_("Add the \"Show Desktop\" button on the left corner of every clock"))
        self.showDesktopButton.setChecked(getSettings("ShowDesktopButton"))
        self.showDesktopButton.stateChanged.connect(lambda i: setSettings("ShowDesktopButton", bool(i)))
        self.primaryScreen = QSettingsCheckBox(_("Show the clock on the primary screen"))
        self.primaryScreen.setChecked(getSettings("ForceClockOnFirstMonitor"))
        self.primaryScreen.stateChanged.connect(lambda i: setSettings("ForceClockOnFirstMonitor", bool(i)))
        self.clockSettingsTitle.addWidget(self.primaryScreen)
        self.onlyPrimaryScreen = QSettingsCheckBox(_("Do not show the clock on secondary monitors"))
        self.onlyPrimaryScreen.setChecked(getSettings("HideClockOnSecondaryMonitors"))
        self.onlyPrimaryScreen.stateChanged.connect(lambda i: setSettings("HideClockOnSecondaryMonitors", bool(i)))
        self.clockSettingsTitle.addWidget(self.onlyPrimaryScreen)
        self.hideClockWhenClicked = QSettingsCheckBox(_("Hide the clock during 10 seconds when clicked"))
        self.hideClockWhenClicked.setChecked(getSettings("HideClockWhenClicked"))
        self.hideClockWhenClicked.stateChanged.connect(lambda i: setSettings("HideClockWhenClicked", bool(i)))
        self.clockSettingsTitle.addWidget(self.hideClockWhenClicked)
        self.enableLowCpuMode = QSettingsCheckBoxWithWarning(_("Enable low-cpu mode"), _("You might lose functionalities, like the notification counter or the dynamic background"))
        self.enableLowCpuMode.setStyleSheet(f"QWidget#stChkBg{{border-bottom-left-radius: {self.getPx(6)}px;border-bottom-right-radius: {self.getPx(6)}px;border-bottom: {self.getPx(1)}px;}}")
        self.enableLowCpuMode.setChecked(getSettings("EnableLowCpuMode"))
        self.enableLowCpuMode.stateChanged.connect(lambda i: setSettings("EnableLowCpuMode", bool(i)))
        self.disableNotificationBadge = QSettingsCheckBox(_("Disable the notification badge"))
        self.disableNotificationBadge.setChecked(getSettings("DisableNotifications"))
        self.disableNotificationBadge.stateChanged.connect(lambda i: setSettings("DisableNotifications", bool(i)))
        self.clockSettingsTitle.addWidget(self.disableNotificationBadge)
        self.clockSettingsTitle.addWidget(self.enableLowCpuMode)

        self.clockPosTitle = QIconLabel(_("Clock position and size:"), getPath(f"size_{self.iconMode}.png"), _("Clock size preferences, position offset, clock at the left, etc."))
        layout.addWidget(self.clockPosTitle)
        self.clockPosTitle.addWidget(self.showDesktopButton)
        self.clockAtLeft = QSettingsCheckBox(_("Show the clock at the left of the screen"))
        self.clockAtLeft.setChecked(getSettings("ClockOnTheLeft"))
        self.clockAtLeft.stateChanged.connect(lambda i: setSettings("ClockOnTheLeft", bool(i)))
        self.clockPosTitle.addWidget(self.clockAtLeft)
        self.clockAtBottom = QSettingsCheckBox(_("Force the clock to be at the bottom of the screen"))
        self.clockAtBottom.setChecked(getSettings("ForceOnBottom"))
        self.clockAtBottom.stateChanged.connect(lambda i: setSettings("ForceOnBottom", bool(i)))
        self.clockPosTitle.addWidget(self.clockAtBottom)
        self.clockAtTop = QSettingsCheckBox(_("Force the clock to be at the top of the screen"))
        self.clockAtTop.setChecked(getSettings("ForceOnTop"))
        self.clockAtTop.setStyleSheet(f"QWidget#stChkBg{{border-bottom-left-radius: {self.getPx(6)}px;border-bottom-right-radius: {self.getPx(6)}px;border-bottom: {self.getPx(1)}px;}}")
        self.clockAtTop.stateChanged.connect(lambda i: setSettings("ForceOnTop", bool(i)))
        self.clockPosTitle.addWidget(self.clockAtTop)
        self.clockFixedHeight = QSettingsSliderWithCheckBox(_("Override clock default height"), self, 20, 105)
        self.clockFixedHeight.setChecked(getSettings("ClockFixedHeight"))
        if self.clockFixedHeight.isChecked():
            try:
                self.clockFixedHeight.slider.setValue(int(getSettingsValue("ClockFixedHeight")))
            except ValueError:
                print("🟠 Unable to parse int from ClockFixedHeight settings value")
        self.clockFixedHeight.stateChanged.connect(lambda v: setSettings("ClockFixedHeight", bool(v)))
        self.clockFixedHeight.valueChanged.connect(lambda v: setSettingsValue("ClockFixedHeight", str(v)))
        self.clockPosTitle.addWidget(self.clockFixedHeight)

        self.clockXOffset = QSettingsSliderWithCheckBox(_("Adjust horizontal clock position"), self, -200, 200)
        self.clockXOffset.setChecked(getSettings("ClockXOffset"))
        if self.clockXOffset.isChecked():
            try:
                self.clockXOffset.slider.setValue(int(getSettingsValue("ClockXOffset")))
            except ValueError:
                print("🟠 Unable to parse int from ClockXOffset settings value")
        self.clockXOffset.stateChanged.connect(lambda v: setSettings("ClockXOffset", bool(v)))
        self.clockXOffset.valueChanged.connect(lambda v: setSettingsValue("ClockXOffset", str(v)))
        self.clockPosTitle.addWidget(self.clockXOffset)

        self.clockYOffset = QSettingsSliderWithCheckBox(_("Adjust vertical clock position"), self, -200, 200)
        self.clockYOffset.setChecked(getSettings("ClockYOffset"))
        if self.clockYOffset.isChecked():
            try:
                self.clockYOffset.slider.setValue(int(getSettingsValue("ClockYOffset")))
            except ValueError:
                print("🟠 Unable to parse int from clockYOffset settings value")
        self.clockYOffset.stateChanged.connect(lambda v: setSettings("ClockYOffset", bool(v)))
        self.clockYOffset.valueChanged.connect(lambda v: setSettingsValue("ClockYOffset", str(v)))
        self.clockPosTitle.addWidget(self.clockYOffset)
        def unblacklist():
            global msg
            setSettingsValue("BlacklistedMonitors", "")
            globals.restartClocks()
            msg = QFramelessDialog(parent=self, closeOnClick=True)
            msg.setAutoFillBackground(True)
            msg.setStyleSheet(globals.sw.styleSheet())
            msg.setAttribute(Qt.WA_StyledBackground)
            msg.setObjectName("QMessageBox")
            msg.setTitle(_("Success"))
            msg.setText(f"""{_("The monitors were unblacklisted successfully.")}<br>
    {_("Now you should see the clock everywhere")}""")
            msg.addButton(_("Ok"), QDialogButtonBox.ButtonRole.ApplyRole)
            msg.setDefaultButtonRole(QDialogButtonBox.ButtonRole.ApplyRole, self.styleSheet())
            msg.show()

        self.unBlackListButton = QSettingsButton(_("Reset monitor blacklisting status"), _("Reset"))
        self.unBlackListButton.clicked.connect(unblacklist)
        self.clockPosTitle.addWidget(self.unBlackListButton)

        self.clockAppearanceTitle = QIconLabel(_("Clock Appearance:"), getPath(f"appearance_{self.iconMode}.png"), _("Clock's font, font size, font color and background, text alignment"))
        layout.addWidget(self.clockAppearanceTitle)
        self.fontPrefs = QSettingsFontBoxComboBox(_("Use a custom font"))
        self.fontPrefs.setChecked(getSettings("UseCustomFont"))
        if self.fontPrefs.isChecked():
            customFont = getSettingsValue("UseCustomFont")
            if customFont:
                self.fontPrefs.combobox.setCurrentText(customFont)
                self.fontPrefs.combobox.lineEdit().setFont(QFont(customFont))
        else:
            if lang == lang_ko:
                self.fontPrefs.combobox.setCurrentText("Malgun Gothic")
            elif lang == lang_zh_TW:
                self.fontPrefs.combobox.setCurrentText("Microsoft JhengHei UI")
            elif lang == lang_zh_CN:
                self.fontPrefs.combobox.setCurrentText("Microsoft YaHei UI")
            else:
                self.fontPrefs.combobox.setCurrentText("Segoe UI Variable Display")
        self.fontPrefs.stateChanged.connect(lambda i: setSettings("UseCustomFont", bool(i)))
        self.fontPrefs.valueChanged.connect(lambda v: setSettingsValue("UseCustomFont", v))
        self.clockAppearanceTitle.addWidget(self.fontPrefs)
        
        self.fontSize = QSettingsSizeBoxComboBox(_("Use a custom font size"))
        self.fontSize.setChecked(getSettings("UseCustomFontSize"))
        self.fontSize.loadItems()
        if self.fontSize.isChecked():
            customFontSize = getSettingsValue("UseCustomFontSize")
            if customFontSize:
                self.fontSize.combobox.setCurrentText(customFontSize)
        else:
                self.fontSize.combobox.setCurrentText("9")
        self.fontSize.stateChanged.connect(lambda i: setSettings("UseCustomFontSize", bool(i)))
        self.fontSize.valueChanged.connect(lambda v: setSettingsValue("UseCustomFontSize", v))
        self.clockAppearanceTitle.addWidget(self.fontSize)
        
        self.fontColor = QSettingsSizeBoxColorDialog(_("Use a custom font color"))
        self.fontColor.setChecked(getSettings("UseCustomFontColor"))
        if self.fontColor.isChecked():
            self.fontColor.button.setStyleSheet(f"color: rgb({getSettingsValue('UseCustomFontColor')})")
        self.fontColor.stateChanged.connect(lambda i: setSettings("UseCustomFontColor", bool(i)))
        self.fontColor.valueChanged.connect(lambda v: setSettingsValue("UseCustomFontColor", v))
        self.clockAppearanceTitle.addWidget(self.fontColor)
        self.disableSystemTrayColor = QSettingsCheckBox(_("Disable clock taskbar background color (make clock transparent)"))
        self.disableSystemTrayColor.setChecked(getSettings("DisableTaskbarBackgroundColor"))
        self.disableSystemTrayColor.stateChanged.connect(lambda i: setSettings("DisableTaskbarBackgroundColor", bool(i)))
        self.clockAppearanceTitle.addWidget(self.disableSystemTrayColor)
        self.backgroundcolor = QSettingsBgBoxColorDialog(_("Use a custom background color"))
        self.backgroundcolor.setChecked(getSettings("UseCustomBgColor"))
        self.backgroundcolor.colorDialog.setOption(QColorDialog.ShowAlphaChannel, True)
        if self.backgroundcolor.isChecked():
            self.backgroundcolor.button.setStyleSheet(f"background-color: rgba({getSettingsValue('UseCustomBgColor')})")
        self.backgroundcolor.stateChanged.connect(lambda i: setSettings("UseCustomBgColor", bool(i)))
        self.backgroundcolor.valueChanged.connect(lambda v: setSettingsValue("UseCustomBgColor", v))
        self.clockAppearanceTitle.addWidget(self.backgroundcolor)
        self.centerText = QSettingsCheckBox(_("Align the clock text to the center"))
        self.centerText.setChecked(getSettings("CenterAlignment"))
        self.centerText.setStyleSheet(f"QWidget#stChkBg{{border-bottom-left-radius: {self.getPx(6)}px;border-bottom-right-radius: {self.getPx(6)}px;border-bottom: {self.getPx(1)}px;}}")
        self.centerText.stateChanged.connect(lambda i: setSettings("CenterAlignment", bool(i)))
        self.clockAppearanceTitle.addWidget(self.centerText)


        self.dateTimeTitle = QIconLabel(_("Date & Time Settings:"), getPath(f"datetime_{self.iconMode}.png"), _("Date format, Time format, seconds,weekday, weeknumber, regional settings"))
        layout.addWidget(self.dateTimeTitle)
        self.showTime = QSettingsCheckBox(_("Show time on the clock"))
        self.showTime.setChecked(not getSettings("DisableTime"))
        self.showTime.stateChanged.connect(lambda i: setSettings("DisableTime", not bool(i), r = False))
        self.dateTimeTitle.addWidget(self.showTime)
        self.showSeconds = QSettingsCheckBox(_("Show seconds on the clock"))
        self.showSeconds.setChecked(getSettings("EnableSeconds"))
        self.showSeconds.stateChanged.connect(lambda i: setSettings("EnableSeconds", bool(i), r = False))
        self.dateTimeTitle.addWidget(self.showSeconds)
        self.showDate = QSettingsCheckBox(_("Show date on the clock"))
        self.showDate.setChecked(not getSettings("DisableDate"))
        self.showDate.stateChanged.connect(lambda i: setSettings("DisableDate", not bool(i), r = False))
        self.dateTimeTitle.addWidget(self.showDate)
        self.showWeekCount = QSettingsCheckBox(_("Show week number on the clock"))
        self.showWeekCount.setChecked(getSettings("EnableWeekNumber"))
        self.showWeekCount.stateChanged.connect(lambda i: setSettings("EnableWeekNumber", bool(i), r = False))
        self.dateTimeTitle.addWidget(self.showWeekCount)
        self.showWeekday = QSettingsCheckBox(_("Show weekday on the clock"))
        self.showWeekday.setChecked(getSettings("EnableWeekDay"))
        self.showWeekday.stateChanged.connect(lambda i: setSettings("EnableWeekDay", bool(i)))
        self.dateTimeTitle.addWidget(self.showWeekday)
        self.RegionButton = QSettingsButton(_("Change date and time format (Regional settings)"), _("Regional settings"))
        self.RegionButton.clicked.connect(lambda: os.startfile("intl.cpl"))
        self.dateTimeTitle.addWidget(self.RegionButton)

        
        self.experimentalTitle = QIconLabel(_("Fixes and other experimental features: (Use ONLY if something is not working)"), getPath(f"experiment_{self.iconMode}.png"), _("Testing features and error-fixing tools"))
        layout.addWidget(self.experimentalTitle)
        self.wizardButton = QSettingsButton(_("Open the welcome wizard")+_(" (ALPHA STAGE, MAY NOT WORK)"), _("Open"))
        
        def ww():
            global welcomewindow
            welcomewindow = welcome.WelcomeWindow()
        
        self.wizardButton.clicked.connect(ww)
        self.wizardButton.button.setObjectName("AccentButton")
        self.wizardButton.setStyleSheet("QWidget#stBtn{border-bottom-left-radius: 0px;border-bottom-right-radius: 0px;border-bottom: 0px;}")
        self.experimentalTitle.addWidget(self.wizardButton)
        self.fixDash = QSettingsCheckBox(_("Fix the hyphen/dash showing over the month"))
        self.fixDash.setChecked(getSettings("EnableHyphenFix"))
        self.fixDash.stateChanged.connect(lambda i: setSettings("EnableHyphenFix", bool(i)))
        self.experimentalTitle.addWidget(self.fixDash)
        self.fixSSL = QSettingsCheckBox(_("Alternative non-SSL update server (This might help with SSL errors)"))
        self.fixSSL.setChecked(getSettings("AlternativeUpdateServerProvider"))
        self.fixSSL.stateChanged.connect(lambda i: setSettings("AlternativeUpdateServerProvider", bool(i)))
        self.experimentalTitle.addWidget(self.fixSSL)
        self.win32alignment = QSettingsCheckBox(_("Alternative clock alignment (may not work)"))
        self.win32alignment.setChecked(getSettings("EnableWin32API"))
        self.win32alignment.setStyleSheet(f"QWidget#stChkBg{{border-bottom-left-radius: {self.getPx(6)}px;border-bottom-right-radius: {self.getPx(6)}px;border-bottom: {self.getPx(1)}px;}}")
        self.win32alignment.stateChanged.connect(lambda i: setSettings("EnableWin32API", bool(i)))
        self.experimentalTitle.addWidget(self.win32alignment)
        self.legacyRDPHide = QSettingsCheckBox(_("Hide the clock when RDP Client or Citrix Workspace are running")+" (Old method)".replace("RDP", "RDP, VMWare Horizon"))
        self.legacyRDPHide.setChecked(getSettings("EnableHideOnRDP"))
        self.legacyRDPHide.stateChanged.connect(lambda i: setSettings("EnableHideOnRDP", bool(i)))
        self.experimentalTitle.addWidget(self.legacyRDPHide)
        self.legacyFullScreenHide = QSettingsCheckBox(_("Check only the focused window on the fullscreen check"))
        self.legacyFullScreenHide.setChecked(getSettings("legacyFullScreenMethod"))
        self.legacyFullScreenHide.stateChanged.connect(lambda i: setSettings("legacyFullScreenMethod", bool(i)))
        self.experimentalTitle.addWidget(self.legacyFullScreenHide)

        self.languageSettingsTitle = QIconLabel(_("About the language pack:"), getPath(f"lang_{self.iconMode}.png"), _("Language pack author(s), help translating ElevenClock"))
        layout.addWidget(self.languageSettingsTitle)
        self.PackInfoButton = QSettingsButton(_("Translated to English by martinet101"), "")
        self.PackInfoButton.button.hide()
        self.PackInfoButton.setStyleSheet("QWidget#stBtn{border-bottom-left-radius: 0px;border-bottom-right-radius: 0px;border-bottom: 0px;}")
        self.languageSettingsTitle.addWidget(self.PackInfoButton)
        self.openTranslateButton = QSettingsButton(_("Translate ElevenClock to your language"), _("Get started"))
        self.openTranslateButton.clicked.connect(lambda: os.startfile("https://github.com/martinet101/ElevenClock/wiki/Translating-ElevenClock#translating-elevenclock"))
        self.languageSettingsTitle.addWidget(self.openTranslateButton)

        def thirdPartyLicenses():
            msg = QFramelessDialog(parent=self, closeOnClick=False)
            msg.setAutoFillBackground(True)
            msg.setStyleSheet(self.styleSheet())
            msg.setAttribute(Qt.WA_StyledBackground)
            msg.setWindowFlag(Qt.WindowStaysOnTopHint)
            msg.setObjectName("QMessageBox")
            msg.setTitle(_("Third Party Open-Source Software in Elevenclock {0} (And their licenses)").format(versionName))
            colors = getColors()
            msg.setText(f"""
                <p>{_("ElevenClock is an Open-Source application made with the help of other libraries made by the community:")}</p><br>
                <style> a {{color: rgb({colors[2 if isWindowDark() else 4]})}}</style>
                <ul>
                <li> <b>Python 3.9</b>: <a href="https://docs.python.org/3/license.html">PSF License Agreement</a></li>
                <li> <b>Win32mica</b> (Also made by me): <a href="https://github.com/martinet101/pymica/blob/master/LICENSE">MIT License</a></li>
                <li> <b>PyWin32</b>: <a href="https://pypi.org/project/pynput/">LGPL-v3</a></li>
                <li> <b>PyQt5 (Qt5)</b>: <a href="https://www.riverbankcomputing.com/commercial/license-faq">LGPL-v3</a></li>
                <li> <b>Psutil</b>: <a href="https://github.com/giampaolo/psutil/blob/master/LICENSE">BSD 3-Clause</a></li>
                <li> <b>PyInstaller</b>: <a href="https://www.pyinstaller.org/license.html">Custom GPL</a></li>
                <li> <b>Frameless Window</b>: <a href="https://github.com/mustafaahci/FramelessWindow/blob/master/LICENSE">The Unlicense</a></li>
                <li> <b>WNFUN</b>: <a href="https://github.com/ionescu007/wnfun/blob/master/LICENSE">BSD 2-Clause</a></li>
                </ul>    """)
            msg.addButton(_("Ok"), QDialogButtonBox.ButtonRole.ApplyRole, lambda: msg.close())
            msg.addButton(_("More Info"), QDialogButtonBox.ButtonRole.ResetRole, lambda: os.startfile("https://github.com/martinet101/ElevenClock/wiki#third-party-libraries"))
            def closeAndQt():
                msg.close()
                QMessageBox.aboutQt(self, "ElevenClock - "+_("About Qt"))
            msg.addButton(_("About Qt"), QDialogButtonBox.ButtonRole.ResetRole, lambda: closeAndQt())
            msg.setDefaultButtonRole(QDialogButtonBox.ButtonRole.ApplyRole, self.styleSheet())
            msg.show()

        self.aboutTitle = QIconLabel(_("About ElevenClock version {0}:").format(versionName), getPath(f"about_{self.iconMode}.png"), _("Info, report a bug, submit a feature request, donate, about"))
        layout.addWidget(self.aboutTitle)
        self.WebPageButton = QSettingsButton(_("View ElevenClock's homepage"), _("Open"))
        self.WebPageButton.clicked.connect(lambda: os.startfile("https://github.com/martinet101/ElevenClock/"))
        self.WebPageButton.setStyleSheet("QWidget#stBtn{border-bottom-left-radius: 0px;border-bottom-right-radius: 0px;border-bottom: 0px;}")
        self.aboutTitle.addWidget(self.WebPageButton)
        self.ThirdParty = QSettingsButton(_("Third party licenses"), _("View"))
        self.ThirdParty.clicked.connect(lambda: thirdPartyLicenses())
        self.ThirdParty.setStyleSheet("QWidget#stBtn{border-bottom-left-radius: 0px;border-bottom-right-radius: 0px;border-bottom: 0px;}")
        self.aboutTitle.addWidget(self.ThirdParty)
        self.IssueButton = QSettingsButton(_("Report an issue/request a feature"), _("Report"))
        self.IssueButton.clicked.connect(lambda: os.startfile("https://github.com/martinet101/ElevenClock/issues/new/choose"))
        self.IssueButton.setStyleSheet("QWidget#stBtn{border-bottom-left-radius: 0px;border-bottom-right-radius: 0px;border-bottom: 0px;}")
        self.aboutTitle.addWidget(self.IssueButton)
        self.CofeeButton = QSettingsButton(_("Support the dev: Give me a coffee☕"), _("Open page"))
        self.CofeeButton.clicked.connect(lambda: os.startfile("https://ko-fi.com/martinet101"))
        self.CofeeButton.setStyleSheet("QWidget#stBtn{border-bottom-left-radius: 0px;border-bottom-right-radius: 0px;border-bottom: 0px;}")
        self.aboutTitle.addWidget(self.CofeeButton)
        self.closeButton = QSettingsButton(_("Close settings"), _("Close"))
        self.closeButton.clicked.connect(lambda: self.hide())
        self.aboutTitle.addWidget(self.closeButton)


        self.debbuggingTitle = QIconLabel(_("Debbugging information:"), getPath(f"bug_{self.iconMode}.png"), _("Log, debugging information"))
        layout.addWidget(self.debbuggingTitle)
        self.logButton = QSettingsButton(_("Open ElevenClock's log"), _("Open"))
        self.logButton.clicked.connect(lambda: self.showDebugInfo())
        self.logButton.setStyleSheet("QWidget#stBtn{border-bottom-left-radius: 0px;border-bottom-right-radius: 0px;border-bottom: 0px;}")
        self.debbuggingTitle.addWidget(self.logButton)
        try:
            self.hiddenButton = QSettingsButton(f"ElevenClock Version: {versionName} {platform.architecture()[0]} (version code {version})\nSystem version: {platform.system()} {str(int(platform.release())+1) if int(platform.version().split('.')[-1])>=22000 else platform.release()} {platform.win32_edition()} {platform.version()}\nSystem architecture: {platform.machine()}\n\nTotal RAM: {psutil.virtual_memory().total/(1000.**3)}\n\nSystem locale: {locale.getdefaultlocale()[0]}\nElevenClock language locale: lang_{langName}", _(""), h=140)
        except Exception as e:
            report(e)
            self.hiddenButton = QSettingsButton(f"ElevenClock Version: {versionName} {platform.architecture()[0]} (version code {version})\nSystem version: {platform.system()} {platform.release()} {platform.win32_edition()} {platform.version()}\nSystem architecture: {platform.machine()}\n\nTotal RAM: {psutil.virtual_memory().total/(1000.**3)}\n\nSystem locale: {locale.getdefaultlocale()[0]}\nElevenClock language locale: lang_{langName}", _(""), h=140)

        self.hiddenButton.button.setVisible(False)
        self.debbuggingTitle.addWidget(self.hiddenButton)
        layout.addSpacing(15)
        layout.addStretch()

        shl = QHBoxLayout()
        shl.setSpacing(0)
        shl.setContentsMargins(0, 0, 0, 0)
        shl.addWidget(QWidget(), stretch=0)
        shl.addLayout(layout, stretch=1)
        shl.addWidget(QWidget(), stretch=0)

        self.settingsWidget.setLayout(shl)
        self.scrollArea.setWidget(self.settingsWidget)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scrollArea.setStyleSheet(f"QScrollArea{{border-bottom-left-radius: {self.getPx(6)}px;border-bottom-right-radius: {self.getPx(6)}px;}}")
        self.vlayout.addWidget(self.scrollArea)
        self.setWindowTitle(_("ElevenClock Settings"))
        self.applyStyleSheet()
        self.updateCheckBoxesStatus()
        w = QWidget()
        w.setObjectName("borderBackground")
        w.setLayout(self.vlayout)
        self.setCentralWidget(w)
        self.setMouseTracking(True)
        self.resize(self.getPx(1100), self.getPx(700))
        self.hwnd = self.winId().__int__()
        self.setAttribute(Qt.WA_TranslucentBackground)
        if QtWin.isCompositionEnabled():
            QtWin.extendFrameIntoClientArea(self, -1, -1, -1, -1)
        else:
            QtWin.resetExtendedFrame(self)

        self.installEventFilter(self)

    def showEvent(self, event: QShowEvent) -> None:
        threading.Thread(target=self.announcements.loadAnnouncements, daemon=True, name="Settings: Announce loader").start()
        return super().showEvent(event)

    def updateCheckBoxesStatus(self):
        
        # General settings section
        if not self.enableUpdates.isChecked(): # Check if check for updates enabled
            for checkbox in [self.installUpdates, self.silentUpdates, self.bypassCNAMECheck]:
                checkbox.setToolTip(_("<b>{0}</b> needs to be enabled to change this setting").format(_("Automatically check for updates")))
                checkbox.setEnabled(False)
        else:
            for checkbox in [self.installUpdates, self.silentUpdates, self.bypassCNAMECheck]:
                checkbox.setToolTip("")
                checkbox.setEnabled(True)
            if not self.installUpdates.isChecked(): # Check if install updates enabled
                for checkbox in [self.silentUpdates, self.bypassCNAMECheck]:
                    checkbox.setToolTip(_("<b>{0}</b> needs to be enabled to change this setting").format(_("Automatically install available updates")))
                    checkbox.setEnabled(False)
            else:
                for checkbox in [self.silentUpdates, self.bypassCNAMECheck]:
                    checkbox.setToolTip("")
                    checkbox.setEnabled(True)
        
                    
        # Date & time settings
        if not self.showTime.isChecked(): # Check if time is shown
            self.showSeconds.setToolTip(_("<b>{0}</b> needs to be enabled to change this setting").format(_("Show time on the clock")))
            self.showSeconds.setEnabled(False)
        else:
            self.showSeconds.setToolTip("")
            self.showSeconds.setEnabled(True)
            
        if not self.showDate.isChecked(): # Check if date is shown
            self.showWeekCount.setToolTip(_("<b>{0}</b> needs to be enabled to change this setting").format(_("Show date on the clock")))
            self.showWeekCount.setEnabled(False)
        else:
            self.showWeekCount.setToolTip("")
            self.showWeekCount.setEnabled(True)
            
            
        if not self.primaryScreen.isChecked(): # Clock is set to be in primary monitor
            self.onlyPrimaryScreen.setToolTip(_("<b>{0}</b> needs to be enabled to change this setting").format(_("Show the clock on the primary screen")))
            self.onlyPrimaryScreen.setEnabled(False)
            self.onlyPrimaryScreen.setChecked(False)
        else:
            self.onlyPrimaryScreen.setToolTip("")
            self.onlyPrimaryScreen.setEnabled(True)

        if self.enableLowCpuMode.isChecked():
            self.disableSystemTrayColor.setToolTip(_("<b>{0}</b> needs to be disabled to change this setting").format(_("Enable low-cpu mode")))
            self.disableSystemTrayColor.setEnabled(False)
            self.disableNotificationBadge.setToolTip(_("<b>{0}</b> needs to be disabled to change this setting").format(_("Enable low-cpu mode")))
            self.disableNotificationBadge.setEnabled(False)
            self.legacyRDPHide.setToolTip(_("<b>{0}</b> needs to be disabled to change this setting").format(_("Enable low-cpu mode")))
            self.legacyRDPHide.setEnabled(False)
        else:
            self.disableSystemTrayColor.setToolTip("")
            self.disableSystemTrayColor.setEnabled(True)
            self.disableNotificationBadge.setToolTip("")
            self.disableNotificationBadge.setEnabled(True)
            self.legacyRDPHide.setToolTip("")
            self.legacyRDPHide.setEnabled(True)

        if self.backgroundcolor.isChecked():
            self.disableSystemTrayColor.setEnabled(False)
            self.disableSystemTrayColor.setToolTip(_("<b>{0}</b> needs to be disabled to change this setting").format(_("Use a custom background color")))
        else:
            self.disableSystemTrayColor.setEnabled(True)
            self.disableSystemTrayColor.setToolTip("")


    def applyStyleSheet(self):
        colors = getColors()
        if isWindowDark():
            if ApplyMica(self.winId().__int__(), MICAMODE.DARK) != 0x0:
                GlobalBlur(self.winId(), Dark=True, Acrylic=True, hexColor="#333333ff")
            self.iconMode = "white"
            self.aboutTitle.setIcon(getPath(f"about_{self.iconMode}.png"))
            self.dateTimeTitle.setIcon(getPath(f"datetime_{self.iconMode}.png"))
            self.clockSettingsTitle.setIcon(getPath(f"clock_{self.iconMode}.png"))
            self.languageSettingsTitle.setIcon(getPath(f"lang_{self.iconMode}.png"))
            self.generalSettingsTitle.setIcon(getPath(f"settings_{self.iconMode}.png"))
            self.experimentalTitle.setIcon(getPath(f"experiment_{self.iconMode}.png"))
            self.clockPosTitle.setIcon(getPath(f"size_{self.iconMode}.png"))
            self.debbuggingTitle.setIcon(QIcon(getPath(f"bug_{self.iconMode}.png")))
            self.clockAppearanceTitle.setIcon(QIcon(getPath(f"appearance_{self.iconMode}.png")))
            self.setStyleSheet(f"""
                               #backgroundWindow {{
                                   
                                   /*background-color: rgba({colors[3]}, 1);*/
                                   background: transparent;
                               }}
                               #titlebarButton {{
                                   border-radius: 0px;
                                   border:none;
                                   background-color: rgba(0, 0, 0, 0.01);
                               }}
                               #titlebarButton:hover {{
                                   border-radius: 0px;
                                   background-color: rgba(80, 80, 80, 25%);
                               }}
                               #closeButton {{
                                   border-radius: 0px;
                                   border:none;
                                   background-color: rgba(0, 0, 0, 0.01);
                               }}
                               #closeButton:hover {{
                                   border-radius: 0px;
                                   background-color: rgba(196, 43, 28, 25%);
                               }}

                                QSlider {{
                                    background: transparent;
                                    height: {self.getPx(20)}px;
                                    margin-left: {self.getPx(10)}px;
                                    margin-right: {self.getPx(10)}px;
                                    border-radius: {self.getPx(2)}px;
                                }}
                                QSlider::groove {{
                                    height: {self.getPx(4)}px;
                                    border: {self.getPx(1)}px solid #212121;
                                    background: #212121;
                                    border-radius: {self.getPx(2)}px;
                                }}
                                QSlider::handle {{
                                    border: {self.getPx(4)}px solid #404040;
                                    margin: {self.getPx(-8)}px {self.getPx(-10)}px;
                                    height: {self.getPx(8)}px;
                                    border-radius: {self.getPx(9)}px; 
                                    background: rgb({colors[0]});
                                }}
                                QSlider::handle:hover {{
                                    border: {self.getPx(3)}px solid #404040;
                                    margin: {self.getPx(-8)}px {self.getPx(-10)}px;
                                    height: {self.getPx(7)}px;
                                    border-radius: {self.getPx(9)}px; 
                                    background: rgb({colors[0]});
                                }}
                                QSlider::handle:disabled {{
                                    border: {self.getPx(4)}px solid #404040;
                                    margin: {self.getPx(-8)}px {self.getPx(-10)}px;
                                    height: {self.getPx(8)}px;
                                    border-radius: {self.getPx(9)}px; 
                                    background: #212121;
                                }}
                                QSlider::add-page {{
                                    border-radius: {self.getPx(3)}px;
                                    background: #303030;
                                }}
                                QSlider::sub-page {{
                                    border-radius: {self.getPx(3)}px;
                                    background: rgb({colors[0]});
                                }}
                                QSlider::add-page:disabled {{
                                    border-radius: {self.getPx(2)}px;
                                    background: #212121;
                                }}
                                QSlider::sub-page:disabled {{
                                    border-radius: {self.getPx(2)}px;
                                    background: #212121;
                                }}
                                QToolTip {{
                                    border: {self.getPx(1)}px solid #222222;
                                    padding: {self.getPx(4)}px;
                                    border-radius: {self.getPx(6)}px;
                                    background-color: #262626;
                                }}
                                QMenu {{
                                    border: {self.getPx(1)}px solid rgb(60, 60, 60);
                                    padding: {self.getPx(2)}px;
                                    outline: 0px;
                                    color: white;
                                    background: #262626;
                                    border-radius: {self.getPx(8)}px;
                                }}
                                QMenu::separator {{
                                    margin: {self.getPx(2)}px;
                                    height: {self.getPx(1)}px;
                                    background: rgb(60, 60, 60);
                                }}
                                QMenu::icon{{
                                    padding-left: {self.getPx(10)}px;
                                }}
                                QMenu::item{{
                                    height: {self.getPx(30)}px;
                                    border: none;
                                    background: transparent;
                                    padding-right: {self.getPx(10)}px;
                                    padding-left: {self.getPx(10)}px;
                                    border-radius: {self.getPx(4)}px;
                                    margin: {self.getPx(2)}px;
                                }}
                                QMenu::item:selected{{
                                    background: rgba(255, 255, 255, 10%);
                                    height: {self.getPx(30)}px;
                                    outline: none;
                                    border: none;
                                    padding-right: {self.getPx(10)}px;
                                    padding-left: {self.getPx(10)}px;
                                    border-radius: {self.getPx(4)}px;
                                }}  
                                QMenu::item:selected:disabled{{
                                    background: transparent;
                                    height: {self.getPx(30)}px;
                                    outline: none;
                                    border: none;
                                    padding-right: {self.getPx(10)}px;
                                    padding-left: {self.getPx(10)}px;
                                    border-radius: {self.getPx(4)}px;
                                }}
                                QColorDialog {{
                                    background-color: transparent;
                                    border: none;
                                }}
                                QLineEdit {{
                                    background-color: #1d1d1d;
                                    padding: {self.getPx(5)}px;
                                    border-radius: {self.getPx(6)}px;
                                    border: {self.getPx(1)}px solid #262626;
                                }}
                                #background,QMessageBox,QDialog,QSlider,#ControlWidget{{
                                   color: white;
                                   /*background-color: #212121;*/
                                   background: transparent;
                                }}
                                QScrollArea {{
                                   color: white;
                                   /*background-color: #212121;*/
                                   background: transparent;
                                }}
                                QLabel {{
                                    font-family: "Segoe UI Variable Display Semib";
                                    font-weight: medium;
                                }}
                                * {{
                                   color: #dddddd;
                                   font-size: 8pt;
                                }}
                                #greyishLabel {{
                                    color: #aaaaaa;
                                }}
                                #warningLabel {{
                                    color: #bdba00;
                                }}
                                QPlainTextEdit{{
                                    font-family: "Cascadia Mono";
                                    background-color: #212121;
                                    selection-background-color: rgb({colors[4]});
                                    border: none;
                                }}
                                QSpinBox {{
                                   background-color: rgba(81, 81, 81, 25%);
                                   border-radius: {self.getPx(6)}px;
                                   border: {self.getPx(1)}px solid rgba(86, 86, 86, 25%);
                                   height: {self.getPx(25)}px;
                                   border-top: {self.getPx(1)}px solid rgba(99, 99, 99, 25%);
                                }}
                                QPushButton {{
                                   width: {self.getPx(100)}px;
                                   background-color:rgba(81, 81, 81, 25%);
                                   border-radius: {self.getPx(6)}px;
                                   border: {self.getPx(1)}px solid rgba(86, 86, 86, 25%);
                                   height: {self.getPx(25)}px;
                                   border-top: {self.getPx(1)}px solid rgba(99, 99, 99, 25%);
                                }}
                                QPushButton:hover {{
                                   background-color:rgba(86, 86, 86, 25%);
                                   border-radius: {self.getPx(6)}px;
                                   border: {self.getPx(1)}px solid rgba(100, 100, 100, 25%);
                                   height: {self.getPx(25)}px;
                                   border-top: {self.getPx(1)}px solid rgba(107, 107, 107, 25%);
                                }}
                                #AccentButton{{
                                    color: black;
                                    background-color: rgb({colors[1]});
                                    border-color: rgb({colors[1]});
                                    border-bottom-color: rgb({colors[2]});
                                }}
                                #AccentButton:hover{{
                                    background-color: rgba({colors[1]}, 80%);
                                    border-color: rgb({colors[2]});
                                    border-bottom-color: rgb({colors[2]});
                                }}
                                #AccentButton:pressed{{
                                    color: #555555;
                                    background-color: rgba({colors[1]}, 80%);
                                    border-color: rgb({colors[2]});
                                    border-bottom-color: rgb({colors[2]});
                                }}
                                #title{{
                                   /*background-color: #303030;
                                   */margin: {self.getPx(2)}px;
                                   margin-bottom: 0px;
                                   padding-left: {self.getPx(20)}px;
                                   padding-top: {self.getPx(15)}px;
                                   padding-bottom: {self.getPx(15)}px;
                                   /*border: {self.getPx(1)}px solid rgba(36, 36, 36, 50%);
                                   */font-size: 13pt;
                                   border-radius: {self.getPx(4)}px;
                                }}
                                #subtitleLabel{{
                                   background-color: rgba(71, 71, 71, 25%);
                                   margin: {self.getPx(10)}px;
                                   margin-bottom: 0px;
                                   margin-top: 0px;
                                   padding-left: {self.getPx(20)}px;
                                   padding-top: {self.getPx(15)}px;
                                   padding-bottom: {self.getPx(15)}px;
                                   border: {self.getPx(1)}px solid rgba(36, 36, 36, 50%);
                                   font-size: 13pt;
                                   border-top-left-radius: {self.getPx(6)}px;
                                   border-top-right-radius: {self.getPx(6)}px;
                                }}
                                #subtitleLabelHover {{
                                   background-color: rgba(20, 20, 20, 1%);
                                   margin: {self.getPx(10)}px;
                                   margin-top: 0px;
                                   margin-bottom: 0px;
                                   border-radius: {self.getPx(6)}px;
                                   border-top-left-radius: {self.getPx(6)}px;
                                   border-top-right-radius: {self.getPx(6)}px;
                                   border: {self.getPx(1)}px solid transparent;
                                }}
                                #subtitleLabelHover:hover{{
                                   background-color: rgba(255, 255, 255, 4%);
                                   margin: {self.getPx(10)}px;
                                   margin-top: 0px;
                                   margin-bottom: 0px;
                                   padding-left: {self.getPx(20)}px;
                                   padding-top: {self.getPx(15)}px;
                                   padding-bottom: {self.getPx(15)}px;
                                   border: {self.getPx(1)}px solid rgba(36, 36, 36, 50%);
                                   border-bottom: 0px;
                                   font-size: 13pt;
                                   border-top-left-radius: {self.getPx(6)}px;
                                   border-top-right-radius: {self.getPx(6)}px;
                                }}
                                #StLbl{{
                                   padding: 0px;
                                   background-color: rgba(71, 71, 71, 0%);
                                   margin: 0px;
                                   border:none;
                                   font-size: {self.getPx(11)}px;
                                }}
                                #stBtn{{
                                   background-color: rgba(71, 71, 71, 0%);
                                   margin: {self.getPx(10)}px;
                                   margin-bottom: 0px;
                                   margin-top: 0px;
                                   border: {self.getPx(1)}px solid rgba(36, 36, 36, 50%);
                                   border-bottom-left-radius: {self.getPx(6)}px;
                                   border-bottom-right-radius: {self.getPx(6)}px;
                                }}
                                #lastWidget{{
                                   border-bottom-left-radius: {self.getPx(6)}px;
                                   border-bottom-right-radius: {self.getPx(6)}px;
                                }}
                                #stChkBg{{
                                   padding: {self.getPx(15)}px;
                                   padding-left: {self.getPx(45)}px;
                                   background-color: rgba(71, 71, 71, 0%);
                                   margin: {self.getPx(10)}px;
                                   margin-bottom: 0px;
                                   margin-top: 0px;
                                   border: {self.getPx(1)}px solid rgba(36, 36, 36, 50%);
                                   border-bottom: 0px;
                                }}
                                #stChk::indicator{{
                                   height: {self.getPx(20)}px;
                                   width: {self.getPx(20)}px;
                                }}
                                #stChk::indicator:unchecked {{
                                    background-color: rgba(30, 30, 30, 25%);
                                    border: {self.getPx(1)}px solid #444444;
                                    border-radius: {self.getPx(6)}px;
                                }}
                                #stChk::indicator:disabled {{
                                    background-color: rgba(71, 71, 71, 0%);
                                    color: #bbbbbb;
                                    border: {self.getPx(1)}px solid #444444;
                                    border-radius: {self.getPx(6)}px;
                                }}
                                #stChk::indicator:unchecked:hover {{
                                    background-color: #2a2a2a;
                                    border: {self.getPx(1)}px solid #444444;
                                    border-radius: {self.getPx(6)}px;
                                }}
                                #stChk::indicator:checked {{
                                    border: {self.getPx(1)}px solid #444444;
                                    background-color: rgb({colors[1]});
                                    border-radius: {self.getPx(6)}px;
                                    image: url("{getPath("tick_white.png")}");
                                }}
                                #stChk::indicator:checked:disabled {{
                                    border: {self.getPx(1)}px solid #444444;
                                    background-color: #303030;
                                    color: #bbbbbb;
                                    border-radius: {self.getPx(6)}px;
                                    image: url("{getPath("tick_black.png")}");
                                }}
                                #stChk::indicator:checked:hover {{
                                    border: {self.getPx(1)}px solid #444444;
                                    background-color: rgb({colors[2]});
                                    border-radius: {self.getPx(6)}px;
                                    image: url("{getPath("tick_white.png")}");
                                }}
                                #stCmbbx {{
                                   width: {self.getPx(100)}px;
                                   background-color:rgba(81, 81, 81, 25%);
                                   border-radius: {self.getPx(6)}px;
                                   border: {self.getPx(1)}px solidrgba(86, 86, 86, 25%);
                                   height: {self.getPx(25)}px;
                                   padding-left: {self.getPx(10)}px;
                                   border-top: {self.getPx(1)}px solidrgba(99, 99, 99, 25%);
                                }}
                                #stCmbbx:disabled {{
                                   width: {self.getPx(100)}px;
                                   background-color: #303030;
                                   border-radius: {self.getPx(6)}px;
                                   border: {self.getPx(1)}px solidrgba(86, 86, 86, 25%);
                                   height: {self.getPx(25)}px;
                                   padding-left: {self.getPx(10)}px;
                                   border-top: {self.getPx(1)}px solidrgba(86, 86, 86, 25%);
                                }}
                                #stCmbbx:hover {{
                                   background-color:rgba(86, 86, 86, 25%);
                                   border-radius: {self.getPx(6)}px;
                                   border: {self.getPx(1)}px solidrgba(100, 100, 100, 25%);
                                   height: {self.getPx(25)}px;
                                   padding-left: {self.getPx(10)}px;
                                   border-top: {self.getPx(1)}px solid rgba(107, 107, 107, 25%);
                                }}
                                #stCmbbx::drop-down {{
                                    subcontrol-origin: padding;
                                    subcontrol-position: top right;
                                    padding: {self.getPx(5)}px;
                                    border-radius: {self.getPx(6)}px;
                                    border: none;
                                    width: {self.getPx(30)}px;
                                }}
                                #stCmbbx::down-arrow {{
                                    image: url("{getPath(f"down-arrow_{self.iconMode}.png")}");
                                    height: {self.getPx(8)}px;
                                    width: {self.getPx(8)}px;
                                }}
                                #stCmbbx::down-arrow:disabled {{
                                    image: url("{getPath(f"down-arrow_{self.iconMode}.png")}");
                                    height: {self.getPx(2)}px;
                                    width: {self.getPx(2)}px;
                                }}
                                #stCmbbx QAbstractItemView {{
                                    border: {self.getPx(1)}px solid rgba(36, 36, 36, 50%);
                                    padding: {self.getPx(4)}px;
                                    outline: 0px;
                                    padding-right: {self.getPx(0)}px;
                                    background-color: #303030;
                                    border-radius: {self.getPx(8)}px;
                                }}
                                #stCmbbx QAbstractItemView::item{{
                                    height: {self.getPx(30)}px;
                                    border: none;
                                    padding-left: {self.getPx(10)}px;
                                    border-radius: {self.getPx(4)}px;
                                }}
                                #stCmbbx QAbstractItemView::item:selected{{
                                    background-color: #4c4c4c;
                                    height: {self.getPx(30)}px;
                                    outline: none;
                                    border: none;
                                    padding-left: {self.getPx(10)}px;
                                    border-radius: {self.getPx(4)}px;
                                }}
                                QSCrollArea, QVBoxLayout{{
                                    border: none;
                                    margin: none;
                                    padding: none;
                                    outline: none;
                                }}
                                QScrollBar:vertical {{
                                    background: rgba(71, 71, 71, 25%);
                                    margin: {self.getPx(4)}px;
                                    width: {self.getPx(20)}px;
                                    border: none;
                                    border-radius: {self.getPx(5)}px;
                                }}
                                QScrollBar::handle:vertical {{
                                    margin: {self.getPx(3)}px;
                                    min-height: {self.getPx(20)}px;
                                    border-radius: {self.getPx(3)}px;
                                    background: rgba(80, 80, 80, 25%);
                                }}
                                QScrollBar::handle:vertical:hover {{
                                    margin: {self.getPx(3)}px;
                                    border-radius: {self.getPx(3)}px;
                                    background: rgba(112, 112, 112, 25%);
                                }}
                                QScrollBar::add-line:vertical {{
                                    height: 0;
                                    subcontrol-position: bottom;
                                    subcontrol-origin: margin;
                                }}
                                QScrollBar::sub-line:vertical {{
                                    height: 0;
                                    subcontrol-position: top;
                                    subcontrol-origin: margin;
                                }}
                                QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {{
                                    background: none;
                                }}
                                QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                                    background: none;
                                }}
                                #titlebarLabel {{
                                    color: red;
                                    background: transparent;
                                    font-size: 10pt;
                                }}
                                #dialogButtonWidget{{
                                    background-color: #1d1d1d;
                                }}
                               """)
        else:
            if ApplyMica(self.winId().__int__(), MICAMODE.LIGHT) != 0x0:
                GlobalBlur(self.winId().__int__(), Dark=False, Acrylic=True, hexColor="#ffffffdd")
            self.iconMode = "black"
            self.aboutTitle.setIcon(getPath(f"about_{self.iconMode}.png"))
            self.dateTimeTitle.setIcon(getPath(f"datetime_{self.iconMode}.png"))
            self.clockSettingsTitle.setIcon(getPath(f"clock_{self.iconMode}.png"))
            self.generalSettingsTitle.setIcon(getPath(f"settings_{self.iconMode}.png"))
            self.experimentalTitle.setIcon(getPath(f"experiment_{self.iconMode}.png"))
            self.languageSettingsTitle.setIcon(getPath(f"lang_{self.iconMode}.png"))
            self.clockPosTitle.setIcon(getPath(f"size_{self.iconMode}.png"))
            self.debbuggingTitle.setIcon(QIcon(getPath(f"bug_{self.iconMode}.png")))
            self.clockAppearanceTitle.setIcon(QIcon(getPath(f"appearance_{self.iconMode}.png")))
            self.setStyleSheet(f"""
                               #backgroundWindow {{
                                   background-color: transparent;
                               }}
                               #titlebarButton {{
                                   border-radius: 0px;
                                   border:none;
                                   background-color: rgba(0, 0, 0, 0.01);
                               }}
                               #titlebarButton:hover {{
                                   border-radius: 0px;
                                   background-color: rgba({colors[4]}, 1);
                               }}
                               #closeButton {{
                                   border-radius: 0px;
                                   border:none;
                                   background-color: rgba(0, 0, 0, 0.01);
                               }}
                               #closeButton:hover {{
                                   border-radius: 0px;
                                   background-color: rgba(196, 43, 28, 1);
                               }}
                                QSlider {{
                                    height: {self.getPx(20)}px;
                                    margin-left: {self.getPx(10)}px;
                                    margin-right: {self.getPx(10)}px;
                                    border-radius: {self.getPx(2)}px;
                                }}
                                QSlider::groove {{
                                    height: {self.getPx(4)}px;
                                    border: {self.getPx(1)}px solid rgba(196, 196, 196, 25%);
                                    background: #303030;
                                }}
                                QSlider::handle {{
                                    border: {self.getPx(4)}px solid #eeeeee;
                                    margin: -{self.getPx(8)}px -{self.getPx(10)}px;
                                    height: {self.getPx(8)}px;
                                    border-radius: {self.getPx(9)}px; 
                                    background: rgb({colors[4]});
                                }}
                                QSlider::handle:hover {{
                                    border: {self.getPx(1)}px solid #eeeeee;
                                    margin: -{self.getPx(8)}px -{self.getPx(10)}px;
                                    height: {self.getPx(8)}px;
                                    border-radius: {self.getPx(9)}px; 
                                    background: rgb({colors[4]});
                                }}
                                QSlider::handle:disabled {{
                                    border: {self.getPx(4)}px solid #eeeeee;
                                    margin: -{self.getPx(8)}px -{self.getPx(10)}px;
                                    height: {self.getPx(8)}px;
                                    border-radius: {self.getPx(9)}px; 
                                    background: rgba(106, 106, 106, 25%);
                                }}
                                QSlider::add-page {{
                                    border-radius: {self.getPx(3)}px;
                                    background: #eeeeee;
                                }}
                                QSlider::sub-page {{
                                    border-radius: {self.getPx(3)}px;
                                    background: rgb({colors[4]});
                                }}
                                QSlider::add-page:disabled {{
                                    border-radius: {self.getPx(3)}px;
                                    background: #eeeeee;
                                }}
                                QSlider::sub-page:disabled {{
                                    border-radius: {self.getPx(3)}px;
                                    background: #eeeeee;
                                }}
                                QToolTip{{
                                    border: {self.getPx(1)}px solid rgba(196, 196, 196, 25%);
                                    padding: {self.getPx(4)}px;
                                    border-radius: {self.getPx(6)}px;
                                    background-color: #eeeeee;
                                }}
                                QPlainTextEdit{{
                                    font-family: "Cascadia Mono";
                                    background-color: rgba(255, 255, 255, 10%);
                                    selection-background-color: rgb({colors[3]});
                                    border: none;
                                }}
                                QMenu {{
                                    border: {self.getPx(1)}px solid rgb(200, 200, 200);
                                    padding: {self.getPx(2)}px;
                                    outline: 0px;
                                    color: black;
                                    background: #eeeeee;
                                    border-radius: {self.getPx(8)}px;
                                }}
                                QMenu::separator {{
                                    margin: {self.getPx(2)}px;
                                    height: {self.getPx(1)}px;
                                    background: rgb(200, 200, 200);
                                }}
                                QMenu::icon{{
                                    padding-left: {self.getPx(10)}px;
                                }}
                                QMenu::item{{
                                    height: {self.getPx(30)}px;
                                    border: none;
                                    background: transparent;
                                    padding-right: {self.getPx(10)}px;
                                    padding-left: {self.getPx(10)}px;
                                    border-radius: {self.getPx(4)}px;
                                    margin: {self.getPx(2)}px;
                                }}
                                QMenu::item:selected{{
                                    background: rgba(0, 0, 0, 10%);
                                    height: {self.getPx(30)}px;
                                    outline: none;
                                    border: none;
                                    padding-right: {self.getPx(10)}px;
                                    padding-left: {self.getPx(10)}px;
                                    border-radius: {self.getPx(4)}px;
                                }}  
                                QMenu::item:selected:disabled{{
                                    background: transparent;
                                    height: {self.getPx(30)}px;
                                    outline: none;
                                    border: none;
                                    padding-right: {self.getPx(10)}px;
                                    padding-left: {self.getPx(10)}px;
                                    border-radius: {self.getPx(4)}px;
                                }}
                                QColorDialog {{
                                    background-color: transparent;
                                    border: none;
                                }}
                                #background,QScrollArea,QMessageBox,QDialog,QSlider,#ControlWidget{{
                                   color: white;
                                   background-color: transparent;
                                }}
                                * {{
                                   background-color: transparent;
                                   color: black;
                                   font-size: 8pt;
                                }}
                                #warningLabel {{
                                    color: #bd0000;
                                    background-color: transparent;
                                }}
                                QPushButton {{
                                   width: {self.getPx(100)}px;
                                   background-color: rgba(255, 255, 255, 70%);
                                   border-radius: {self.getPx(6)}px;
                                   border: {self.getPx(1)}px solid rgba(196, 196, 196, 25%);
                                   height: {self.getPx(25)}px;
                                   border-bottom: {self.getPx(1)}px solid rgba(204, 204, 204, 25%);
                                }}
                                QPushButton:hover {{
                                   background-color: rgba(238, 238, 238, 100%);
                                   border-radius: {self.getPx(6)}px;
                                   border: {self.getPx(1)}px solid rgba(196, 196, 196, 25%);
                                   height: {self.getPx(25)}px;
                                   border-bottom: {self.getPx(1)}px solid rgba(204, 204, 204, 25%);
                                }}
                                #AccentButton{{
                                    background-color: rgb({colors[3]});
                                    border-color: rgb({colors[4]});
                                    border-bottom-color: rgb({colors[5]});
                                    color: white;
                                }}
                                #AccentButton:hover{{
                                    background-color: rgb({colors[2]});
                                    border-color: rgb({colors[3]});
                                    color: white;
                                    border-bottom-color: rgb({colors[3]});
                                }}
                                #title{{
                                   /*background-color: rgba(255, 255, 255, 10%);
                                   */margin: {self.getPx(2)}px;
                                   margin-bottom: 0px;
                                   padding-left: {self.getPx(20)}px;
                                   padding-top: {self.getPx(15)}px;
                                   padding-bottom: {self.getPx(15)}px;
                                   font-size: 13pt;
                                   border-radius: {self.getPx(6)}px;
                                }}
                                #subtitleLabel{{
                                   background-color: rgba(255, 255, 255, 10%);
                                   margin: {self.getPx(10)}px;
                                   margin-bottom: 0px;
                                   margin-top: 0px;
                                   padding-left: {self.getPx(20)}px;
                                   padding-top: {self.getPx(15)}px;
                                   padding-bottom: {self.getPx(15)}px;
                                   border-radius: {self.getPx(4)}px;
                                   border: {self.getPx(1)}px solid rgba(196, 196, 196, 25%);
                                   font-size: 13pt;
                                   border-top-left-radius: {self.getPx(6)}px;
                                   border-top-right-radius: {self.getPx(6)}px;
                                }}
                                #subtitleLabelHover {{
                                   background-color: rgba(0, 0, 0, 1%);
                                   margin: {self.getPx(10)}px;
                                   margin-top: 0px;
                                   margin-bottom: 0px;
                                   border-radius: {self.getPx(6)}px;
                                   border-top-left-radius: {self.getPx(6)}px;
                                   border-top-right-radius: {self.getPx(6)}px;
                                   border: {self.getPx(1)}px solid transparent;
                                }}
                                #subtitleLabelHover:hover{{
                                   background-color: rgba(0, 0, 0, 6%);
                                   margin: {self.getPx(10)}px;
                                   margin-top: 0px;
                                   margin-bottom: 0px;
                                   padding-left: {self.getPx(20)}px;
                                   padding-top: {self.getPx(15)}px;
                                   padding-bottom: {self.getPx(15)}px;
                                   border: {self.getPx(1)}px solid rgba(196, 196, 196, 25%);
                                   font-size: 13pt;
                                   border-top-left-radius: {self.getPx(6)}px;
                                   border-top-right-radius: {self.getPx(6)}px;
                                }}
                                #StLbl{{
                                   padding: 0px;
                                   background-color: rgba(255, 255, 255, 10%);
                                   margin: 0px;
                                   border:none;
                                   font-size: {self.getPx(11)}px;
                                }}
                                #stBtn{{
                                   background-color: rgba(255, 255, 255, 10%);
                                   margin: {self.getPx(10)}px;
                                   margin-bottom: 0px;
                                   margin-top: 0px;
                                   border: {self.getPx(1)}px solid rgba(196, 196, 196, 25%);
                                   border-bottom: 0px;
                                   border-bottom-left-radius: {self.getPx(0)}px;
                                   border-bottom-right-radius: {self.getPx(0)}px;
                                }}
                                #lastWidget{{
                                   border-bottom-left-radius: {self.getPx(6)}px;
                                   border-bottom-right-radius: {self.getPx(6)}px;
                                   border-bottom: {self.getPx(1)}px;
                                }}
                                #stChkBg{{
                                   padding: {self.getPx(15)}px;
                                   padding-left: {self.getPx(45)}px;
                                   background-color: rgba(255, 255, 255, 10%);
                                   margin: {self.getPx(10)}px;
                                   margin-bottom: 0px;
                                   margin-top: 0px;
                                   border: {self.getPx(1)}px solid rgba(196, 196, 196, 25%);
                                   border-bottom: 0px;
                                }}
                                #stChk::indicator{{
                                   height: {self.getPx(20)}px;
                                   width: {self.getPx(20)}px;
                                }}
                                #stChk::indicator:unchecked {{
                                    background-color: rgba(255, 255, 255, 10%);
                                    border: {self.getPx(1)}px solid rgba(136, 136, 136, 25%);
                                    border-radius: {self.getPx(6)}px;
                                }}
                                #stChk::indicator:disabled {{
                                    background-color: #eeeeee;
                                    color: rgba(136, 136, 136, 25%);
                                    border: {self.getPx(1)}px solid rgba(136, 136, 136, 25%);
                                    border-radius: {self.getPx(6)}px;
                                }}
                                #stChk::indicator:unchecked:hover {{
                                    background-color: #eeeeee;
                                    border: {self.getPx(1)}px solid rgba(136, 136, 136, 25%);
                                    border-radius: {self.getPx(6)}px;
                                }}
                                #stChk::indicator:checked {{
                                    border: {self.getPx(0)}px solid rgba(136, 136, 136, 25%);
                                    background-color: rgb({colors[4]});
                                    border-radius: {self.getPx(5)}px;
                                    image: url("{getPath("tick_black.png")}");
                                }}
                                #stChk::indicator:checked:hover {{
                                    border: {self.getPx(0)}px solid rgba(136, 136, 136, 25%);
                                    background-color: rgb({colors[3]});
                                    border-radius: {self.getPx(5)}px;
                                    image: url("{getPath("tick_black.png")}");
                                }}
                                #stChk::indicator:checked:disabled {{
                                    border: {self.getPx(1)}px solid rgba(136, 136, 136, 25%);
                                    background-color: #eeeeee;
                                    color: rgba(136, 136, 136, 25%);
                                    border-radius: {self.getPx(6)}px;
                                    image: url("{getPath("tick_white.png")}");
                                }}
                                #stCmbbx {{
                                   width: {self.getPx(100)}px;
                                   background-color: rgba(255, 255, 255, 10%);
                                   border-radius: {self.getPx(6)}px;
                                   border: {self.getPx(1)}px solid rgba(196, 196, 196, 25%);
                                   height: {self.getPx(25)}px;
                                   padding-left: {self.getPx(10)}px;
                                   border-bottom: {self.getPx(1)}px solid rgba(204, 204, 204, 25%);
                                }}
                                #stCmbbx:disabled {{
                                   width: {self.getPx(100)}px;
                                   background-color: #eeeeee;
                                   border-radius: {self.getPx(6)}px;
                                   border: {self.getPx(1)}px solid rgba(196, 196, 196, 25%);
                                   height: {self.getPx(25)}px;
                                   padding-left: {self.getPx(10)}px;
                                   border-top: {self.getPx(1)}px solid rgba(196, 196, 196, 25%);
                                }}
                                #stCmbbx:hover {{
                                   background-color: rgba(238, 238, 238, 25%);
                                   border-radius: {self.getPx(6)}px;
                                   border: {self.getPx(1)}px solid rgba(196, 196, 196, 25%);
                                   height: {self.getPx(25)}px;
                                   padding-left: {self.getPx(10)}px;
                                   border-bottom: {self.getPx(1)}px solid rgba(204, 204, 204, 25%);
                                }}
                                #stCmbbx::drop-down {{
                                    subcontrol-origin: padding;
                                    subcontrol-position: top right;
                                    padding: {self.getPx(5)}px;
                                    border-radius: {self.getPx(6)}px;
                                    border: none;
                                    width: {self.getPx(30)}px;
                                }}
                                #stCmbbx::down-arrow {{
                                    image: url("{getPath(f"down-arrow_{self.iconMode}.png")}");
                                    height: {self.getPx(8)}px;
                                    width: {self.getPx(8)}px;
                                }}
                                #stCmbbx::down-arrow:disabled {{
                                    image: url("{getPath(f"down-arrow_{self.iconMode}.png")}");
                                    height: {self.getPx(2)}px;
                                    width: {self.getPx(2)}px;
                                }}
                                #stCmbbx QAbstractItemView {{
                                    border: {self.getPx(1)}px solid rgba(196, 196, 196, 25%);
                                    padding: {self.getPx(4)}px;
                                    outline: 0px;
                                    background-color: rgba(255, 255, 255, 10%);
                                    border-radius: {self.getPx(8)}px;
                                }}
                                #stCmbbx QAbstractItemView::item{{
                                    height: {self.getPx(30)}px;
                                    border: none;
                                    padding-left: {self.getPx(10)}px;
                                    border-radius: {self.getPx(4)}px;
                                }}
                                #stCmbbx QAbstractItemView::item:selected{{
                                    background-color: #eeeeee;
                                    height: {self.getPx(30)}px;
                                    outline: none;
                                    color: black;
                                    border: none;
                                    padding-left: {self.getPx(10)}px;
                                    border-radius: {self.getPx(4)}px;
                                }}
                                QSCrollArea,QVBoxLayout{{
                                    border: none;
                                    margin: none;
                                    padding: none;
                                    outline: none;
                                }}
                                QScrollBar:vertical {{
                                    background: rgba(255, 255, 255, 10%);
                                    margin: {self.getPx(4)}px;
                                    width: {self.getPx(20)}px;
                                    border: none;
                                    border-radius: {self.getPx(5)}px;
                                }}
                                QScrollBar::handle:vertical {{
                                    margin: {self.getPx(3)}px;
                                    border-radius: {self.getPx(3)}px;
                                    min-height: {self.getPx(20)}px;
                                    background: rgba(196, 196, 196, 25%);
                                }}
                                QScrollBar::handle:vertical:hover {{
                                    margin: {self.getPx(3)}px;
                                    border-radius: {self.getPx(3)}px;
                                    background: rgba(136, 136, 136, 25%);
                                }}
                                QScrollBar::add-line:vertical {{
                                    height: 0;
                                    subcontrol-position: bottom;
                                    subcontrol-origin: margin;
                                }}
                                QScrollBar::sub-line:vertical {{
                                    height: 0;
                                    subcontrol-position: top;
                                    subcontrol-origin: margin;
                                }}
                                QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {{
                                    background: none;
                                }}
                                QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                                    background: none;
                                }}
                                #greyishLabel {{
                                    color: #888888;
                                }}
                                #dialogButtonWidget{{
                                    background-color: #eeeeee;
                                }}
                               """)

    def showDebugInfo(self):

        class QPlainTextEditWithFluentMenu(QPlainTextEdit):
            def __init__(self):
                super().__init__()

            def contextMenuEvent(self, e: QtGui.QContextMenuEvent) -> None:
                menu = self.createStandardContextMenu()
                menu.addSeparator()

                a = QAction()
                a.setText(_("Reload log"))
                a.triggered.connect(lambda: textEdit.setPlainText(globals.buffer.getvalue()))
                menu.addAction(a)

                a2 = QAction()
                a2.setText(_("Export log as a file"))
                a2.triggered.connect(lambda: saveLog())
                menu.addAction(a2)

                a3 = QAction()
                a3.setText(_("Copy log to clipboard"))
                a3.triggered.connect(lambda: copyLog())
                menu.addAction(a3)

                ApplyMenuBlur(menu.winId().__int__(), menu)
                menu.exec(e.globalPos())
                return super().contextMenuEvent(e)

        global old_stdout, buffer
        win = QMainWindow(self)
        win.resize(self.getPx(900), self.getPx(600))
        win.setObjectName("background")
        win.setWindowTitle(_("ElevenClock's log"))
        
        w = QWidget()
        w.setLayout(QVBoxLayout())
        w.setContentsMargins(0, 0, 0, 0)
        
        textEdit = QPlainTextEditWithFluentMenu()
        textEdit.setReadOnly(True)
        if isWindowDark():
            textEdit.setStyleSheet(f"QPlainTextEdit{{margin: {self.getPx(10)}px;border-radius: {self.getPx(4)}px;border: {self.getPx(1)}px solid #161616;}}")
        else:
            textEdit.setStyleSheet(f"QPlainTextEdit{{margin: {self.getPx(10)}px;border-radius: {self.getPx(4)}px;border: {self.getPx(1)}px solid #dddddd;}}")



        textEdit.setPlainText(globals.buffer.getvalue())
        
        reloadButton = QPushButton(_("Reload log"))
        reloadButton.setFixedWidth(self.getPx(200))
        reloadButton.clicked.connect(lambda: textEdit.setPlainText(globals.buffer.getvalue()))
        
        def saveLog():
            try:
                print("🔵 Saving log...")
                f = QFileDialog.getSaveFileName(win, "Save log", os.path.expanduser("~"), "Text file (.txt)")
                if f[0]:
                    fpath = f[0]
                    if not ".txt" in fpath.lower():
                        fpath += ".txt"
                    with open(fpath, "wb") as fobj:
                        fobj.write(globals.buffer.getvalue().encode("utf-8"))
                        fobj.close()
                    os.startfile(fpath)
                    print("🟢 log saved successfully")
                    textEdit.setPlainText(globals.buffer.getvalue())
                else:
                    print("🟡 log save cancelled!")
                    textEdit.setPlainText(globals.buffer.getvalue())
            except Exception as e:
                report(e)
                textEdit.setPlainText(globals.buffer.getvalue())

        
        exportButtom = QPushButton(_("Export log as a file"))
        exportButtom.setFixedWidth(self.getPx(200))
        exportButtom.clicked.connect(lambda: saveLog())

        def copyLog():
            try:
                print("🔵 Copying log to the clipboard...")
                globals.app.clipboard().setText(globals.buffer.getvalue())
                print("🟢 Log copied to the clipboard successfully!")
                textEdit.setPlainText(globals.buffer.getvalue())
            except Exception as e:
                report(e)
                textEdit.setPlainText(globals.buffer.getvalue())


        copyButton = QPushButton(_("Copy log to clipboard"))
        copyButton.setFixedWidth(self.getPx(200))
        copyButton.clicked.connect(lambda: copyLog())
         


        hl = QHBoxLayout()
        hl.setSpacing(self.getPx(5))
        hl.setContentsMargins(self.getPx(10), self.getPx(10), self.getPx(10), 0)
        hl.addWidget(exportButtom)
        hl.addWidget(copyButton)
        hl.addStretch()
        hl.addWidget(reloadButton)
        
        w.layout().setSpacing(0)
        w.layout().setContentsMargins(self.getPx(5), self.getPx(5), self.getPx(5), self.getPx(5))
        w.layout().addLayout(hl, stretch=0)
        w.layout().addWidget(textEdit, stretch=1)
        
        win.setCentralWidget(w)
        win.hwnd = win.winId().__int__()


        win.setAttribute(Qt.WA_TranslucentBackground)
        win.setAttribute(Qt.WA_NoSystemBackground)
        win.setAutoFillBackground(True)

        win.hwnd = win.winId().__int__()
        window_style = win32gui.GetWindowLong(win.hwnd, GWL_STYLE)
        win32gui.SetWindowLong(win.hwnd, GWL_STYLE, window_style | WS_POPUP | WS_THICKFRAME | WS_CAPTION | WS_SYSMENU)

        if QtWin.isCompositionEnabled():
            QtWin.extendFrameIntoClientArea(win, -1, -1, -1, -1)
        else:
            QtWin.resetExtendedFrame(win)

        
        if ApplyMica(win.hwnd, isWindowDark()) != 0:
            if isWindowDark():    
                GlobalBlur(win.winId().__int__(), Dark=True, Acrylic=True, hexColor="#333333ff")
            else:
                GlobalBlur(win.winId().__int__(), Dark=False, Acrylic=True, hexColor="#ffffffdd")

        win.show()

    def moveEvent(self, event: QMoveEvent) -> None:
        if(self.updateSize):
            pass
        else:
            def enableUpdateSize(self: SettingsWindow):
                time.sleep(1)
                self.updateSize = True

            self.updateSize = False
            KillableThread(target=enableUpdateSize, args=(self,)).start()
        super().moveEvent(event)
            
    def mouseReleaseEvent(self, event) -> None:
        if(self.updateSize):
            self.settingsWidget.resize(self.width()-self.getPx(17), self.settingsWidget.height())
            self.applyStyleSheet()
            if not self.isMaximized():
                self.scrollArea.setStyleSheet(f"QScrollArea{{border-bottom-left-radius: {self.getPx(6)}px;border-bottom-right-radius: {self.getPx(6)}px;}}")
            self.updateSize = False
        return super().mouseReleaseEvent(event)


    def show(self) -> None:
        self.applyStyleSheet()
        self.raise_()
        self.activateWindow()
        return super().show()
    
    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if event.type() == event.WindowStateChange:
            if self.isMaximized():
                self.scrollArea.setStyleSheet(f"QScrollArea{{border-bottom-left-radius: 0px;border-bottom-right-radius: 0px;}}")
            else:
                self.scrollArea.setStyleSheet(f"QScrollArea{{border-bottom-left-radius: {self.getPx(6)}px;border-bottom-right-radius: {self.getPx(6)}px;}}")
        return super().eventFilter(watched, event)


    def closeEvent(self, event: QCloseEvent) -> None:
        self.hide()
        event.ignore()

    def getPx(self, original) -> int:
        return round(original*(self.screen().logicalDotsPerInch()/96))


class QIconLabel(QWidget):
    def __init__(self, text: str, icon: str, descText: str = "No description provided"):
        if isWindowDark():
            self.iconMode = "white"
            semib = "Semib"
        else:
            self.iconMode = "black"
            semib = ""
        super().__init__()
        self.icon = icon
        self.setObjectName("subtitleLabel")
        self.label = QLabel(text, self)
        self.setMaximumWidth(self.getPx(1000))
        self.descLabel = QLabel(descText, self)
        self.descLabel.setObjectName("greyishLabel")
        if lang == lang_zh_TW:
            self.label.setStyleSheet("font-size: 10pt;background: none;font-family: \"Microsoft JhengHei UI\";")
            self.descLabel.setStyleSheet("font-size: 8pt;background: none;font-family: \"Microsoft JhengHei UI\";")
        elif lang == lang_zh_CN:
            self.label.setStyleSheet("font-size: 10pt;background: none;font-family: \"Microsoft YaHei UI\";")
            self.descLabel.setStyleSheet("font-size: 8pt;background: none;font-family: \"Microsoft YaHei UI\";")
        else:
            self.label.setStyleSheet(f"font-size: 10pt;background: none;font-family: \"Segoe UI Variable Display {semib}\";")
            self.descLabel.setStyleSheet(f"font-size: 8pt;background: none;font-family: \"Segoe UI Variable Display {semib}\";")

        self.image = QLabel(self)
        self.image.setStyleSheet(f"padding: {self.getPx(1)}px;background: none;")
        self.setAttribute(Qt.WA_StyledBackground)
        self.compressibleWidget = QWidget(self)
        self.compressibleWidget.show()
        self.childOpacity=QGraphicsOpacityEffect(self)
        self.childOpacity.setOpacity(1.0)
        self.compressibleWidget.setGraphicsEffect(self.childOpacity)
        self.compressibleWidget.setAutoFillBackground(True)
        self.compressibleWidget.setObjectName("compressibleWidget")
        self.compressibleWidget.setStyleSheet("#compressibleWidget{background-color: transparent;}")

        self.showHideButton = QPushButton("", self)
        self.showHideButton.setIcon(QIcon(getPath(f"expand_{self.iconMode}.png")))
        self.showHideButton.setStyleSheet("border: none; background-color:none;")
        self.showHideButton.clicked.connect(self.toggleChilds)
        l = QVBoxLayout()
        l.setSpacing(0)
        l.setContentsMargins(0, 0, 0, 0)
        self.childsVisible = False
        self.compressibleWidget.setLayout(l)

        self.setStyleSheet(f"QWidget#subtitleLabel{{border-bottom-left-radius: {self.getPx(6)}px;border-bottom-right-radius: {self.getPx(6)}px;border-bottom: {self.getPx(1)}px;}}")

        self.showAnim = QVariantAnimation(self.compressibleWidget)
        self.showAnim.setEasingCurve(QEasingCurve.InOutQuart)
        self.showAnim.setStartValue(0)
        self.showAnim.setEndValue(1000)
        self.showAnim.valueChanged.connect(lambda v: self.setChildFixedHeight(v, v/self.compressibleWidget.sizeHint().height()))
        self.showAnim.setDuration(300)
        self.showAnim.finished.connect(self.invertNotAnimated)
        self.hideAnim = QVariantAnimation(self.compressibleWidget)
        self.hideAnim.setEndValue(0)
        self.hideAnim.setEasingCurve(QEasingCurve.InOutQuart)
        self.hideAnim.valueChanged.connect(lambda v: self.setChildFixedHeight(v, v/self.compressibleWidget.sizeHint().height()))
        self.hideAnim.setDuration(300)
        self.hideAnim.finished.connect(self.invertNotAnimated)
        self.NotAnimated = True

     

        self.button = QPushButton("", self)
        self.button.setObjectName("subtitleLabelHover")
        self.button.clicked.connect(self.toggleChilds)
        self.button.setStyleSheet(f"border-bottom-left-radius: 0px;border-bottom-right-radius: 0px;")

        self.setChildFixedHeight(0, 0)
        self.button.setStyleSheet(f"border-bottom-left-radius: {self.getPx(6)}px;border-bottom-right-radius: {self.getPx(6)}px;")

        
    def setChildFixedHeight(self, h: int, o:float = 1.0) -> None:
        self.compressibleWidget.setFixedHeight(h)
        self.setFixedHeight(h+self.getPx(70))
        self.childOpacity.setOpacity((o-(0.5))*2 if (o-(0.5))*2>0 else 0)
        self.compressibleWidget.setGraphicsEffect(self.childOpacity)

    def invertNotAnimated(self):
        self.NotAnimated = not self.NotAnimated

    def toggleChilds(self):
        if(readRegedit(r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize", "AppsUseLightTheme", 1)==0):
            self.iconMode = "white"
        else:
            self.iconMode = "black"
        if self.childsVisible:
            self.childsVisible = False
            self.hideAnim.setStartValue(self.compressibleWidget.sizeHint().height())
            self.hideAnim.setEndValue(0)
            self.invertNotAnimated()
            self.showHideButton.setIcon(QIcon(getPath(f"expand_{self.iconMode}.png")))
            self.hideAnim.finished.connect(lambda: self.button.setStyleSheet(f"border-bottom-left-radius: {self.getPx(6)}px;border-bottom-right-radius: {self.getPx(6)}px;"))
            self.hideAnim.start()
        else:
            self.showAnim.setStartValue(0)
            self.showHideButton.setIcon(QIcon(getPath(f"collapse_{self.iconMode}.png")))
            self.showAnim.setEndValue(self.compressibleWidget.sizeHint().height())
            self.button.setStyleSheet(f"border-bottom-left-radius: 0px;border-bottom-right-radius: 0px;")
            self.showAnim.start()
            self.invertNotAnimated()
            self.childsVisible = True
        
    def getPx(self, original) -> int:
        return round(original*(self.screen().logicalDotsPerInchX()/96))

    def setIcon(self, icon: str) -> None:
        self.image.setPixmap(QIcon(icon).pixmap(QSize(24, 24)))

    def resizeEvent(self, event: QResizeEvent) -> None:
        self.image.setPixmap(QIcon(self.icon).pixmap(QSize(self.getPx(24), self.getPx(24))))
        self.showHideButton.setIconSize(QSize(self.getPx(12), self.getPx(12)))
        self.button.move(0, 0)
        self.button.resize(self.width(), self.getPx(70))
        self.showHideButton.setFixedSize(self.getPx(30), self.getPx(30))
        self.showHideButton.move(self.width()-self.getPx(55), self.getPx(20))
        
        self.label.move(self.getPx(70), self.getPx(17))
        self.label.setFixedHeight(self.getPx(20))
        self.descLabel.move(self.getPx(70), self.getPx(37))
        self.descLabel.setFixedHeight(self.getPx(20))

        self.image.move(self.getPx(27), self.getPx(20))
        self.image.setFixedHeight(self.getPx(30))
        if self.childsVisible and self.NotAnimated:
            self.setFixedHeight(self.compressibleWidget.sizeHint().height()+self.getPx(70))
            self.compressibleWidget.setFixedHeight(self.compressibleWidget.sizeHint().height())
        elif self.NotAnimated:
            self.setFixedHeight(self.getPx(70))
        self.compressibleWidget.move(0, self.getPx(70))
        self.compressibleWidget.setFixedWidth(self.width())
        self.image.setFixedHeight(self.getPx(30))
        self.label.setFixedWidth(self.width()-self.getPx(70))
        self.image.setFixedWidth(self.getPx(30))
        return super().resizeEvent(event)
    
    def addWidget(self, widget: QWidget) -> None:
        self.compressibleWidget.layout().addWidget(widget)
        
class QSettingsButton(QWidget):
    clicked = Signal()
    def __init__(self, text="", btntext="", parent=None, h = 30):
        super().__init__(parent)
        self.fh = h
        self.setAttribute(Qt.WA_StyledBackground)
        self.button = QPushButton(btntext+" ", self)
        self.button.setLayoutDirection(Qt.RightToLeft)
        self.setObjectName("stBtn")
        self.label = QLabel(text, self)
        if lang == lang_zh_TW:
            self.label.setStyleSheet("font-size: 10pt;background: none;font-family: \"Microsoft JhengHei UI\";font-weight: 450;")
            self.button.setStyleSheet("font-size: 10pt;font-family: \"Microsoft JhengHei UI\";font-weight: 450;")
        elif lang == lang_zh_CN:
            self.label.setStyleSheet("font-size: 10pt;background: none;font-family: \"Microsoft YaHei UI\";font-weight: 450;")
            self.button.setStyleSheet("font-size: 10pt;font-family: \"Microsoft YaHei UI\";font-weight: 450;")
        else:
            self.label.setStyleSheet("font-size: 9pt;background: none;font-family: \"Segoe UI Variable Text\";font-weight: 450;")
            self.button.setStyleSheet("font-size: 9pt;font-family: \"Segoe UI Variable Text\";font-weight: 450;")
        self.label.setObjectName("StLbl")
        self.button.clicked.connect(self.clicked.emit)

    def getPx(self, original) -> int:
        return round(original*(self.screen().logicalDotsPerInchX()/96))

    def resizeEvent(self, event: QResizeEvent) -> None:
        self.button.move(self.width()-self.getPx(170), self.getPx(10))
        self.label.move(self.getPx(70), self.getPx(10))
        self.label.setFixedWidth(self.width()-self.getPx(230))
        self.label.setFixedHeight(self.getPx(self.fh))
        self.setFixedHeight(self.getPx(50+(self.fh-30)))
        self.button.setFixedHeight(self.getPx(self.fh))
        self.button.setFixedWidth(self.getPx(150))
        return super().resizeEvent(event)

    def setIcon(self, icon: QIcon) -> None:
        self.button.setIcon(icon)

class QSettingsComboBox(QWidget):
    textChanged = Signal(str)
    def __init__(self, text="", btntext="", parent=None):
        super().__init__(parent)

        class QcomboBoxWithFluentMenu(QComboBox):
            def __init__(self, parent) -> None:
                super().__init__(parent)


        self.setAttribute(Qt.WA_StyledBackground)
        self.combobox = QcomboBoxWithFluentMenu(self)
        self.combobox.setObjectName("stCmbbx")
        self.combobox.setItemDelegate(QStyledItemDelegate(self.combobox))
        self.setObjectName("stBtn")
        self.restartButton = QPushButton("Restart ElevenClock", self)
        self.restartButton.hide()
        self.restartButton.setObjectName("AccentButton")
        self.label = QLabel(text, self)

        if lang == lang_zh_TW:
            self.label.setStyleSheet("font-size: 11pt;background: none;font-family: \"Microsoft JhengHei UI\";font-weight: 450;")
            self.combobox.setStyleSheet("font-size: 11pt;font-family: \"Microsoft JhengHei UI\";font-weight: 450;")
            self.restartButton.setStyleSheet("font-size: 11pt;font-family: \"Microsoft JhengHei UI\";font-weight: 450;")
        elif lang == lang_zh_CN:
            self.label.setStyleSheet("font-size: 11pt;background: none;font-family: \"Microsoft YaHei UI\";font-weight: 450;")
            self.combobox.setStyleSheet("font-size: 11pt;font-family: \"Microsoft YaHei UI\";font-weight: 450;")
            self.restartButton.setStyleSheet("font-size: 11pt;font-family: \"Microsoft YaHei UI\";font-weight: 450;")
        else:
            self.label.setStyleSheet("font-size: 9pt;background: none;font-family: \"Segoe UI Variable Text\";font-weight: 450;")
            self.combobox.setStyleSheet("font-size: 9pt;font-family: \"Segoe UI Variable Text\";font-weight: 450;")
            self.restartButton.setStyleSheet("font-size: 9pt;font-family: \"Segoe UI Variable Text\";font-weight: 450;")
        self.label.setObjectName("StLbl")

    def getPx(self, original) -> int:
        return round(original*(self.screen().logicalDotsPerInchX()/96))

    def setItems(self, items: list, index: int) -> None:
        self.combobox.addItems(items)
        try:
            self.combobox.setCurrentIndex(index)
        except Exception as e:
            report(e)
            self.combobox.setCurrentIndex(0)
        self.combobox.currentTextChanged.connect(self.textChanged.emit)

    def resizeEvent(self, event: QResizeEvent) -> None:
        self.combobox.move(self.width()-self.getPx(270), self.getPx(10))
        self.label.move(self.getPx(70), self.getPx(10))
        self.label.setFixedWidth(self.width()-self.getPx(480))
        self.label.setFixedHeight(self.getPx(30))
        self.restartButton.move(self.width()-self.getPx(430), self.getPx(10))
        self.restartButton.setFixedWidth(self.getPx(150))
        self.restartButton.setFixedHeight(self.getPx(30))
        self.setFixedHeight(self.getPx(50))
        self.combobox.setFixedHeight(self.getPx(30))
        self.combobox.setFixedWidth(self.getPx(250))
        return super().resizeEvent(event)

    def setIcon(self, icon: QIcon) -> None:
        pass
        #self.button.setIcon(icon)

    def showRestartButton(self) -> None:
        self.restartButton.show()

class QSettingsCheckBox(QWidget):
    stateChanged = Signal(bool)
    def __init__(self, text="", parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_StyledBackground)
        self.setObjectName("stChkBg")
        self.checkbox = QCheckBox(text, self)
        if lang == lang_zh_TW:
            self.checkbox.setStyleSheet("font-size: 11pt;background: none;font-family: \"Microsoft JhengHei UI\";font-weight: 450;")
        elif lang == lang_zh_CN:
            self.checkbox.setStyleSheet("font-size: 11pt;background: none;font-family: \"Microsoft YaHei UI\";font-weight: 450;")
        else:
            self.checkbox.setStyleSheet("font-size: 9pt;background: none;font-family: \"Segoe UI Variable Text\";font-weight: 450;")
        self.checkbox.setObjectName("stChk")
        self.checkbox.stateChanged.connect(self.stateChanged.emit)

    def setChecked(self, checked: bool) -> None:
        self.checkbox.setChecked(checked)

    def isChecked(self) -> bool:
        return self.checkbox.isChecked()

    def getPx(self, original) -> int:
        return round(original*(self.screen().logicalDotsPerInchX()/96))

    def resizeEvent(self, event: QResizeEvent) -> None:
        self.checkbox.move(self.getPx(70), self.getPx(10))
        self.checkbox.setFixedHeight(self.getPx(30))
        self.checkbox.setFixedWidth(self.width()-self.getPx(70))
        self.setFixedHeight(self.getPx(50))
        return super().resizeEvent(event)

class QSettingsCheckBoxWithWarning(QSettingsCheckBox):
    def __init__(self, text = "", infotext = "", parent=None):
        super().__init__(text=text, parent=parent)
        self.infolabel = QLabel(infotext, self)
        self.infolabel.setTextFormat(Qt.RichText)
        self.infolabel.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.infolabel.setTextInteractionFlags(Qt.TextBrowserInteraction)
        self.infolabel.setOpenExternalLinks(True)
        self.infolabel.setObjectName("warningLabel")
        self.infolabel.setVisible(self.checkbox.isChecked())
        self.checkbox.stateChanged.connect(self.stateChangedFun)
        
    def stateChangedFun(self, checked: bool) -> bool:
        self.infolabel.setVisible(checked)
        self.stateChanged.emit(checked)
        
    def resizeEvent(self, event: QResizeEvent) -> None:
        self.checkbox.move(self.getPx(70), self.getPx(10))
        self.checkbox.setFixedHeight(self.getPx(30))
        self.checkbox.setFixedWidth(self.width()-self.getPx(70))
        self.infolabel.move(self.getPx(150), self.getPx(10))
        self.infolabel.setFixedHeight(self.getPx(30))
        self.infolabel.setFixedWidth(self.width()-self.getPx(70)-self.getPx(150))
        self.setFixedHeight(self.getPx(50))
        return super().resizeEvent(event)

class QSettingsSizeBoxComboBox(QSettingsCheckBox):
    stateChanged = Signal(bool)
    valueChanged = Signal(str)
    
    def __init__(self, text: str, parent=None):
        super().__init__(text=text, parent=parent)
        self.setAttribute(Qt.WA_StyledBackground)
        self.combobox = QComboBox(self)
        self.combobox.setObjectName("stCmbbx")
        self.combobox.currentIndexChanged.connect(self.valuechangedEvent)
        self.checkbox.stateChanged.connect(self.stateChangedEvent)
        self.stateChangedEvent(self.checkbox.isChecked())
        
    def resizeEvent(self, event: QResizeEvent) -> None:
        self.combobox.move(self.width()-self.getPx(270), self.getPx(10))
        self.checkbox.move(self.getPx(70), self.getPx(10))
        self.checkbox.setFixedWidth(self.width()-self.getPx(280))
        self.checkbox.setFixedHeight(self.getPx(30))
        self.setFixedHeight(self.getPx(50))
        self.combobox.setFixedHeight(self.getPx(30))
        self.combobox.setFixedWidth(self.getPx(250))
        return super().resizeEvent(event)
    
    def valuechangedEvent(self, i: int):
        self.valueChanged.emit(self.combobox.itemText(i))
    
    def stateChangedEvent(self, v: bool):
        self.combobox.setEnabled(self.checkbox.isChecked())
        if not self.checkbox.isChecked():
            self.combobox.setEnabled(False)
            self.combobox.setToolTip(_("<b>{0}</b> needs to be enabled to change this setting").format(_(self.checkbox.text())))
        else:
            self.combobox.setEnabled(True)
            self.combobox.setToolTip("")
            self.valueChanged.emit(self.combobox.currentText())
        self.stateChanged.emit(v)
        
    def loadItems(self):
        self.combobox.clear()
        self.combobox.addItems(str(item) for item in [5, 6, 7, 7.5, 8, 8.5, 9, 9.5, 10, 10.5, 11, 11.5, 12, 13, 14, 16])


class QSettingsSliderWithCheckBox(QSettingsCheckBox):
    stateChanged = Signal(bool)
    valueChanged = Signal(int)
    
    def __init__(self, text: str, parent=None, min: int = 10, max: int = 100):
        super().__init__(text=text, parent=parent)
        self.setAttribute(Qt.WA_StyledBackground)
        self.slider = QSlider(self)
        self.slider.setRange(min, max)
        self.slider.setOrientation(Qt.Horizontal)
        self.slider.setObjectName("slider")
        self.slider.sliderReleased.connect(self.valuechangedEvent)
        self.checkbox.stateChanged.connect(self.stateChangedEvent)
        self.stateChangedEvent(self.checkbox.isChecked())
        
    def resizeEvent(self, event: QResizeEvent) -> None:
        self.slider.move(self.width()-self.getPx(270), self.getPx(10))
        self.checkbox.move(self.getPx(70), self.getPx(10))
        self.checkbox.setFixedWidth(self.width()-self.getPx(280))
        self.checkbox.setFixedHeight(self.getPx(30))
        self.setFixedHeight(self.getPx(50))
        self.slider.setFixedHeight(self.getPx(30))
        self.slider.setFixedWidth(self.getPx(250))
        return super().resizeEvent(event)
    
    def valuechangedEvent(self):
        self.valueChanged.emit(self.slider.value())
    
    def stateChangedEvent(self, v: bool):
        self.slider.setEnabled(self.checkbox.isChecked())
        if not self.checkbox.isChecked():
            self.slider.setEnabled(False)
            self.slider.setToolTip(_("<b>{0}</b> needs to be enabled to change this setting").format(_(self.checkbox.text())))
        else:
            self.slider.setEnabled(True)
            self.slider.setToolTip("")
            self.valueChanged.emit(self.slider.value())
        self.stateChanged.emit(v)
        



class QCustomColorDialog(QColorDialog):
    def __init__(self, parent = ...) -> None:
        super().__init__(parent=parent)
        self.setWindowModality(Qt.WindowModality.WindowModal)
        self.setStyleSheet(f"*{{border-radius: {self.getPx(4)}px;}}  QColorLuminancePicker {{background-color: transparent; border: {self.getPx(4)}px solid black;margin: none; border: none; padding: none;}} ")
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAutoFillBackground(True)

        self.hwnd = self.winId().__int__()
        window_style = win32gui.GetWindowLong(self.hwnd, GWL_STYLE)
        win32gui.SetWindowLong(self.hwnd, GWL_STYLE, window_style | WS_POPUP | WS_THICKFRAME | WS_CAPTION | WS_SYSMENU)

        if QtWin.isCompositionEnabled():
            QtWin.extendFrameIntoClientArea(self, -1, -1, -1, -1)
        else:
            QtWin.resetExtendedFrame(self)
        
        
        if ApplyMica(self.hwnd, isWindowDark()) != 0x0:
            if isWindowDark():    
                GlobalBlur(self.winId().__int__(), Dark=True, Acrylic=True, hexColor="#333333ff")
            else:
                GlobalBlur(self.winId().__int__(), Dark=False, Acrylic=True, hexColor="#ffffffdd")

        self.setWindowIcon(self.window().windowIcon())
        self.setWindowTitle(_("Pick a color"))

    def getPx(self, i: int):
        return round(i*(self.screen().logicalDotsPerInch()/96))

class QSettingsSizeBoxColorDialog(QSettingsCheckBox):
    stateChanged = Signal(bool)
    valueChanged = Signal(str)
    
    def __init__(self, text: str, parent=None):
        super().__init__(text=text, parent=parent)
        self.setAttribute(Qt.WA_StyledBackground)
        self.colorDialog = QCustomColorDialog(self)
        self.colorDialog.setOptions(QColorDialog.DontUseNativeDialog)
        self.button = QPushButton(self)
        self.button.setObjectName("stCmbbx")
        self.button.setText(_("Select custom color"))
        self.button.clicked.connect(self.colorDialog.show)
        self.colorDialog.colorSelected.connect(self.valuechangedEvent)
        self.checkbox.stateChanged.connect(self.stateChangedEvent)
        self.stateChangedEvent(self.checkbox.isChecked())
        
    def resizeEvent(self, event: QResizeEvent) -> None:
        self.button.move(self.width()-self.getPx(270), self.getPx(10))
        self.checkbox.move(self.getPx(70), self.getPx(10))
        self.checkbox.setFixedWidth(self.width()-self.getPx(280))
        self.checkbox.setFixedHeight(self.getPx(30))
        self.setFixedHeight(self.getPx(50))
        self.button.setFixedHeight(self.getPx(30))
        self.button.setFixedWidth(self.getPx(250))
        return super().resizeEvent(event)
    
    def valuechangedEvent(self, c: QColor):
        r = c.red()
        g = c.green()
        b = c.blue()
        color = f"{r},{g},{b}"
        self.valueChanged.emit(color)
        self.button.setStyleSheet(f"color: rgb({color})")
    
    def stateChangedEvent(self, v: bool):
        self.button.setEnabled(self.checkbox.isChecked())
        if not self.checkbox.isChecked():
            self.button.setEnabled(False)
            self.button.setStyleSheet("")
            self.button.setToolTip(_("<b>{0}</b> needs to be enabled to change this setting").format(_(self.checkbox.text())))
        else:
            self.button.setEnabled(True)
            self.button.setToolTip("")
        self.stateChanged.emit(v)
        
class QSettingsBgBoxColorDialog(QSettingsSizeBoxColorDialog):
 
    def valuechangedEvent(self, c: QColor):
        r = c.red()
        g = c.green()
        b = c.blue()
        a = c.alpha()
        color = f"{r},{g},{b},{a/255*100}"
        self.valueChanged.emit(color)
        self.button.setStyleSheet(f"background-color: rgba({color})")    

class QSettingsFontBoxComboBox(QSettingsCheckBox):
    stateChanged = Signal(bool)
    valueChanged = Signal(str)
    
    def __init__(self, text: str, parent=None):
        super().__init__(text=text, parent=parent)
        self.setAttribute(Qt.WA_StyledBackground)
        self.combobox = QFontComboBox(self)
        self.combobox.setObjectName("stCmbbx")
        self.combobox.currentIndexChanged.connect(self.valuechangedEvent)
        self.checkbox.stateChanged.connect(self.stateChangedEvent)
        self.stateChangedEvent(self.checkbox.isChecked())
        
    def resizeEvent(self, event: QResizeEvent) -> None:
        self.combobox.move(self.width()-self.getPx(270), self.getPx(10))
        self.checkbox.move(self.getPx(70), self.getPx(10))
        self.checkbox.setFixedWidth(self.width()-self.getPx(280))
        self.checkbox.setFixedHeight(self.getPx(30))
        self.setFixedHeight(self.getPx(50))
        self.combobox.setFixedHeight(self.getPx(30))
        self.combobox.setFixedWidth(self.getPx(250))
        return super().resizeEvent(event)
    
    def valuechangedEvent(self, i: int):
        self.valueChanged.emit(self.combobox.itemText(i))
        self.combobox.lineEdit().setFont(QFont(self.combobox.itemText(i)))
    
    def stateChangedEvent(self, v: bool):
        self.combobox.setEnabled(self.checkbox.isChecked())
        if not self.checkbox.isChecked():
            self.combobox.setEnabled(False)
            self.combobox.setToolTip(_("<b>{0}</b> needs to be enabled to change this setting").format(_(self.checkbox.text())))
        else:
            self.combobox.setEnabled(True)
            self.combobox.setToolTip("")
            self.valueChanged.emit(self.combobox.currentText())
            self.combobox.lineEdit().setFont(QFont(self.combobox.currentText()))
        self.stateChanged.emit(v)
        
    def setItems(self, items: list):
        self.combobox.clear()
        self.combobox.addItems(items)
    
class QAnnouncements(QLabel):
    callInMain = Signal(object)

    def __init__(self):
        super().__init__()
        self.area = QScrollArea()
        self.setMaximumWidth(self.getPx(1000))
        self.callInMain.connect(lambda f: f())
        self.setObjectName("subtitleLabel")
        self.setFixedHeight(self.getPx(110))
        self.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.setStyleSheet(f"#subtitleLabel{{border-bottom-left-radius: {self.getPx(6)}px;border-bottom-right-radius: {self.getPx(6)}px;border-bottom: {self.getPx(1)}px;font-size: 12pt;}}*{{padding: 3px;}}")
        self.setTtext(_("Fetching latest announcement, please wait..."))
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.pictureLabel = QLabel()
        self.pictureLabel.setContentsMargins(0, 0, 0, 0)
        self.pictureLabel.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.textLabel = QLabel()
        self.textLabel.setOpenExternalLinks(True)
        self.textLabel.setContentsMargins(self.getPx(10), 0, self.getPx(10), 0)
        self.textLabel.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        layout.addStretch()
        layout.addWidget(self.textLabel, stretch=0)
        layout.addWidget(self.pictureLabel, stretch=0)
        layout.addStretch()
        self.w = QWidget()
        self.w.setObjectName("backgroundWindow")
        self.w.setLayout(layout)
        self.w.setContentsMargins(0, 0, 0, 0)
        self.area.setWidget(self.w)
        l = QVBoxLayout()
        l.setSpacing(0)
        l.setContentsMargins(0, self.getPx(5), 0, self.getPx(5))
        l.addWidget(self.area, stretch=1)
        self.area.setWidgetResizable(True)
        self.area.setContentsMargins(0, 0, 0, 0)
        self.area.setObjectName("backgroundWindow")
        self.area.setStyleSheet("border: 0px solid black; padding: 0px; margin: 0px;")
        self.area.setFrameShape(QFrame.NoFrame)
        self.area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.pictureLabel.setFixedHeight(self.area.height())
        self.textLabel.setFixedHeight(self.area.height())
        self.setLayout(l)



    def loadAnnouncements(self):
        try:
            response = urlopen("http://www.somepythonthings.tk/resources/elevenclock.announcement")
            print("🔵 Announcement URL:", response.url)
            response = response.read().decode("utf8")
            self.callInMain.emit(lambda: self.setTtext(""))
            announcement_body = response.split("////")[0].strip().replace("http://", "ignore:").replace("https://", "ignoreSecure:").replace("linkId", "http://somepythonthings.tk/redirect/").replace("linkColor", f"rgb({getColors()[2 if isWindowDark() else 4]})")
            self.callInMain.emit(lambda: self.textLabel.setText(announcement_body))
            self.callInMain.emit(lambda: self.pictureLabel.setText("Loading media..."))
            announcement_image_url = response.split("////")[1].strip()
            try:
                response = urlopen(announcement_image_url)
                print("🔵 Image URL:", response.url)
                response = response.read()
                self.file =  open(os.path.join(os.path.join(os.path.join(os.path.expanduser("~"), ".elevenclock")), "announcement.png"), "wb")
                self.file.write(response)
                self.callInMain.emit(lambda: self.pictureLabel.setText(""))
                self.file.close()
                h = self.area.height()
                self.callInMain.emit(lambda: self.pictureLabel.setFixedHeight(h))
                self.callInMain.emit(lambda: self.textLabel.setFixedHeight(h))
                self.callInMain.emit(lambda: self.pictureLabel.setPixmap(QPixmap(self.file.name).scaledToHeight(h-self.getPx(6), Qt.SmoothTransformation)))
            except Exception as ex:
                s = _("Couldn't load the announcement image")+"\n\n"+str(ex)
                self.callInMain.emit(lambda: self.pictureLabel.setText(s))
                print("🟠 Unable to retrieve announcement image")
                report(ex)
        except Exception as e:
            s = _("Couldn't load the announcements. Please try again later")+"\n\n"+str(e)
            self.callInMain.emit(lambda: self.setTtext(s))
            print("🟠 Unable to retrieve latest announcement")
            report(e)

    def showEvent(self, a0: QShowEvent) -> None:
        return super().showEvent(a0)

    def getPx(self, i: int) -> int:
        return round(i*(self.screen().logicalDotsPerInch()/96))

    def setTtext(self, a0: str) -> None:
        return super().setText(a0)

    def setText(self, a: str) -> None:
        raise Exception("This member should not be used under any circumstances")

if __name__ == "__main__":
    import __init__
