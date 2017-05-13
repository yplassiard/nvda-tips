# *-* coding: utf8 *-*
##
## Tips
## Show tips to help the user use NVDa more efficiently.
##
## (C) 2017 Yannick PLASSIARD

import time
import json
from NVDAObjects import NVDAObject
import api
import controlTypes
import speech
import globalPluginHandler
import wx
import logHandler



ignoredRoles = (controlTypes.ROLE_PANE, controlTypes.ROLE_WINDOW, controlTypes.ROLE_CLOCK)

class GlobalPlugin(globalPluginHandler.GlobalPlugin):
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

        msg = None
        if self.obj is None:
            return
        if self.obj.role in ignoredRoles:
            return
        speech.speakMessage(u"Vous êtes sur %s: %s" %(controlTypes.roleLabels[self.obj.role], self.explain()))

    def explain(self):
        msg = ""
        if self.obj.role in (controlTypes.ROLE_EDITABLETEXT, controlTypes.ROLE_RICHEDIT):
            if self.obj.role is controlTypes.ROLE_EDITABLETEXT:
                msg = u"Utilisez les flèches gauche et droite pour parcourir le texte."
            else:
                msg = u"Utilisez les flèches haut, bas, gauche et droite sour sarcourir le texte."
            if controlTypes.STATE_READONLY in self.obj.states:
                msg += u" Ce champs d'édition est en lecture seule, vous ne pouvez entrer de texte ici."
            else:
                msg += u" Vous pouvez également entrer du texte dans ce champs."
            ti = self.obj.treeInterceptor
            if ti and ti.passThrough is False:
                msg += u" Vous êtes en mode navigation, pour entrer du texte, utiliser NVDA+Espace pour passer en mode focus."
        elif self.obj.role in (controlTypes.ROLE_BUTTON, controlTypes.ROLE_LINK):
            if controlTypes.STATE_UNAVAILABLE in self.obj.states:
                msg = u"Vous ne pouvez activer ce %s car il est grisé." % (controlTypes.roleLabels[self.obj.role])
            else:
                msg = u"Appuyez sur entrée pour l'activer."
            if controlTypes.STATE_HASPOPUP in self.obj.states:
                msg += u" Cet élément contient un sous-menu contenant davantage d'options. Utilisez la touche Application pour y accéder."
        elif self.obj.role is controlTypes.ROLE_CHECKBOX:
            if controlTypes.STATE_CHECKED in self.obj.states:
                msg = u"Appuyez sur espace pour décocher la case."
            else:
                msg = u"Appuyez sur espace pour cocher la case."
        elif self.obj.role is controlTypes.ROLE_RADIOBUTTON:
            if controlTypes.STATE_CHECKED not in self.obj.states:
                msg = u"Appuyez sur espace pour sélectionner cette option, ou sur les flèches vers le haut, le bas, la gauche ou la droite pour examiner les autres options disponibles."
            else:
                msg = u"Cette ostion est sélectionnée: Appuyez sur les flèches vers le haut, le bas, la gauche ou la droite pour examiner les autres options disponibles."
        elif self.obj.role is controlTypes.ROLE_SLIDER:
            msg = u"Utilisez les flèches vers la gauche ou le bas pour diminuer la valeur, ou vers la droite ou le haut pour l'augmenter."
        
                
        return msg

    def script_contextHelp(self, gesture):
        obj = api.getFocusObject()
        msg = u""
        if obj.role is controlTypes.ROLE_BUTTON:
            if obj.parent and obj.parent.__class__.__name__ is 'NotificationArea':
                msg = u"Vous vous trouvez dans la zone de notification système. Cette zone contient des icônes de programmes ou services en cours d'exécution. Utilisez les flèches gauche et droite pour parcourir la liste, puis appuyez sur entrée pour activer l'icône souhaitée. Vous pourvez également appuyer sur la touche Application (ou menu contextuel) afin d'ouvrir un menu permettant de sélectionner d'autres options concernant ce programme ou service. Pour vous rendre directement danscette zone la prochaine fois, utilisez la combinaison Windows+B."
        if obj.role is controlTypes.ROLE_LISTITEM:
            logHandler.log.info("In a list view item.")
            if obj.parent.parent.__class__.__name__ == u'WindowRoot':
                msg = u"Vous êtes sur le bureau: Il contient des icônes permettant de lancer des programmes, ou d'ouvrir des documents. Arrangées sous la forme d'une grille, vous pouvez utiliser les flèches vers le haut, le bas, la gauche ou la droite afin de sélectionner l'icône souhaitée, et appuyer sur entrée pour l'activer. Vous pouvez également appuyer sur la touche Application (ou menu contextuel), afin d'ouvrir un menu qui vous permettra d'effectuer d'autres actions sur l'icône sélectionnée. Pour vous rendre rapidement sur le bureau, vous pouvez utiliser la combinaison de touche Windows+D."
            elif obj.appModule.appName == u'explorer':
                msg = u"Vous êtes dans l'explorateur de fichiers. Utilisez les flèches de direction pour naviguer dans le contenu du répertoire en cours. Pour ourrir un élément, appuyez sur Entrée. Pour revenir au niveau supérieur, appuyez sur la combinaison Alt+Flèche vers le haut. Pour naviguer entre les différentes zones de l'explorateur, utilisez la touche F6 pour aller à la zone suivante, ou Shift+F6 pour la zone précédente."
        if len(msg) > 0:
            speech.speakMessage(msg)
            
    __gestures = {
        "kb:nvda+h": "contextHelp",
}
    
