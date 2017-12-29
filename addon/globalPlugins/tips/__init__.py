##
## Tips
## Show tips to help the user use NVDa more efficiently.
##
## See the LICENSE file for licensing informations
## (C) 2017 Yannick PLASSIARD

import time
import os
from NVDAObjects import NVDAObject
import api
import controlTypes
import speech
import globalPluginHandler, addonHandler, sayAllHandler
addonHandler.initTranslation()
import wx
import logHandler



ignoredRoles = (controlTypes.ROLE_PANE, controlTypes.ROLE_WINDOW, controlTypes.ROLE_CLOCK)


class GlobalPlugin(globalPluginHandler.GlobalPlugin):
    scriptCategory = _("TIPS")

    lastAction = None
    tipTimer = None
    tipDelay = 2

    def __init__(self, *args, **kwargs):
        super(GlobalPlugin, self).__init__(*args, **kwargs)
        self.tipTimer = wx.PyTimer(self.sayTip)
    

    def event_gainFocus(self, obj, nextHandler):
        self.obj = obj
        self.lastAction = time.time()
        self.tipTimer.Stop()
        self.tipTimer.Start(self.tipDelay * 1000, True)
        nextHandler()
    
    def event_loseFocus(self, obj, nextHandler):
        self.obj = None
        self.lastAction = None
        nextHandler()

    def sayTip(self):
        global ignoredRoles
        if sayAllHandler.isRunning():
            return

        if self.obj is None:
            return
        if self.obj.role in ignoredRoles:
            return
        msg = self.explain()
        speech.speakMessage(_("You are on a {elementType}: {elementMessage}").format(elementType=controlTypes.roleLabels[self.obj.role], elementMessage=msg))

    def explain(self):
        msg = ""
        if self.obj.role in (controlTypes.ROLE_EDITABLETEXT, controlTypes.ROLE_RICHEDIT):
            if self.obj.role is controlTypes.ROLE_EDITABLETEXT:
                msg = _("Use left and right arrow keys to browse the text.")
            else:
                msg = _("Use up, down, left and right arrow keys to browse the text.")
            if controlTypes.STATE_READONLY in self.obj.states:
                msg += _(" This edit field is read-only; you cannot enter text here.")
            else:
                msg += _(" You can enter text here.")
                ti = self.obj.treeInterceptor
                if ti and ti.passThrough is False:
                    msg += _(" You are currently in browse mode. To enter text, use NVDA+Space to switch to focus mode.")
        elif self.obj.role in (controlTypes.ROLE_BUTTON, controlTypes.ROLE_LINK):
            if controlTypes.STATE_UNAVAILABLE in self.obj.states:
                msg = _("Cannot activate %s because it's grayed.") % (controlTypes.roleLabels[self.obj.role])
            else:
                msg = _("Press enter to activate it.")
            if controlTypes.STATE_HASPOPUP in self.obj.states:
                msg += _("This element contains a submenu with more options. Use the Application key to open it.")
        elif self.obj.role is controlTypes.ROLE_CHECKBOX:
            if controlTypes.STATE_CHECKED in self.obj.states:
                msg = _("Press space to uncheck.")
            else:
                msg = _("Press space to check.")
        elif self.obj.role is controlTypes.ROLE_RADIOBUTTON:
            if controlTypes.STATE_CHECKED not in self.obj.states:
                msg = _("Press space to select this option, or use the arrow keys to select another one in this group.")
            else:
                msg = _("Option selected: use the arrow keys to see and select other options.")
        elif self.obj.role is controlTypes.ROLE_SLIDER:
            msg = _("Use left and down arrow keys to decrease the value, or right and up arrow keys to increase it.")
        
                
        return msg

    def script_contextHelp(self, gesture):
        obj = api.getFocusObject()
        msg = u""
        if obj.role is controlTypes.ROLE_BUTTON:
            if obj.parent and obj.parent.__class__.__name__ is 'NotificationArea':
                msg = _("You are in the notification area. This area contains icons of running programs and services allowing you to control their execution and settings. Use the left and right arrow keys to move bitween them and enter to activate the desired icon. You may also use the Application key (or context menu key) to open a pop-up menu containg more options regarding the currently focused icon. To quickly go to the notification area from anywhere, use the Windows+B shortcut.")
        if obj.role is controlTypes.ROLE_LISTITEM:
            if obj and obj.parent is not None and obj.parent.parent is not None and obj.parent.parent.__class__.__name__ == u'WindowRoot':
                msg = _("You are on the Desktop, containing several icons to start programs or open documents. Arranged as a grid, you can move using arrow keys bitween them, and press enter to activate the desired one. You may also use the Application (or context menu) key to open a pop-up menu containing other options related to an icon. To quickly go to the Desktop from anywhere, simply use the Windows+D shortcut.")
            elif obj.appModule.appName == u'explorer':
                msg = _("You are in the file Explorer application. Use the arrow keys to navigate bitween files, andenter to open the desired one, or Application (context menu) key to open a pop-up menu with more options. Use the Alt+up-arrow key to go to the parent folder. To cycle forward through the explorer's panels, use F6, and Shift+F6 to cycle backward.")
        if len(msg) > 0:
            speech.speakMessage(msg)
    script_contextHelp.__doc__ = _("Announces some contextual help based on the currently focused object, window, or application.")

    __gestures = {
        "kb:nvda+h": "contextHelp",
}
    
