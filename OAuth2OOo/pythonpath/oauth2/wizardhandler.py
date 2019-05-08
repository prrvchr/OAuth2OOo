#!
# -*- coding: utf_8 -*-

import uno
import unohelper

from com.sun.star.awt import XContainerWindowEventHandler
from com.sun.star.awt import XDialogEventHandler

from .unolib import PropertySet

from .unotools import createMessageBox
from .unotools import createService
from .unotools import getCurrentLocale
from .unotools import getProperty
from .unotools import getStringResource
from .oauth2tools import getActivePath
from .oauth2tools import g_wizard_paths
from .oauth2tools import g_identifier


class WizardHandler(unohelper.Base,
                    PropertySet,
                    XContainerWindowEventHandler,
                    XDialogEventHandler):
    def __init__(self, ctx, configuration, controller):
        self.ctx = ctx
        self.Configuration = configuration
        self.Wizard = createService(self.ctx, 'com.sun.star.ui.dialogs.Wizard')
        arguments = ((uno.Any('[][]short', (g_wizard_paths)), controller), )
        uno.invoke(self.Wizard, 'initialize', arguments)
        self.stringResource = getStringResource(self.ctx, g_identifier, 'OAuth2OOo')

    # XContainerWindowEventHandler, XDialogEventHandler
    def callHandlerMethod(self, window, event, method):
        handled = False
        if method == 'Add':
            item = event.Source.Model.Tag
            id = self._addItem(window, item)
            if item == 'Url' or item == 'Value':
                handled = self._updateWindow(window, method, item, id)
            else:
                handled = self._showDialog(window, method, item, id)
        elif method == 'Edit':
            item = event.Source.Model.Tag
            handled = self._showDialog(window, method, item)
        elif method == 'Remove':
            item = event.Source.Model.Tag
            handled = self._showDialog(window, method, item)
        elif method == 'Changed':
            handled = self._updateUI(window, event.Source)
        elif method == 'Clicked':
            handled = self.callHandlerMethod(window, event, 'Edit')
        return handled
    def getSupportedMethodNames(self):
        return ('Add', 'Edit', 'Remove', 'Changed', 'Clicked')

    def _addItem(self, window, item):
        if item == 'Url':
            id = window.getControl('ComboBox1').getText()
            self.Configuration.Url.Id = id
        elif item == 'Provider':
            id = window.getControl('ComboBox2').getText()
            self.Configuration.Url.ProviderName = id
        elif item == 'Scope':
            id = window.getControl('ComboBox3').getText()
            self.Configuration.Url.ScopeName = id
        elif item == 'Value':
            id = window.getControl('TextField1').getText()
            control = window.getControl('ListBox1').Model
            control.insertItemText(control.ItemCount, id)
        return id

    def _showDialog(self, window, method, item, id=''):
        dialog = self._getDialog(window, method, item)
        self._initDialog(dialog, method, item)
        if dialog.execute():
            self._saveData(window, dialog, method, item)
            self._updateWindow(window, method, item, id)
        else:
            pass #need delete AddItem
        dialog.dispose()
        return True

    def _getDialog(self, window, method, item):
        if method != 'Remove':
            url = 'vnd.sun.star.script:OAuth2OOo.%sDialog?location=application' % item
            provider = createService(self.ctx, 'com.sun.star.awt.DialogProvider')
            dialog = provider.createDialogWithHandler(url, self)
        else:
            title = self.stringResource.resolveString('MessageBox.Title')
            message = self.stringResource.resolveString('MessageBox.Message')
            dialog = createMessageBox(window.Peer, message, title)
        return dialog

    def _initDialog(self, dialog, method, item):
        if method == 'Edit':
            if item == 'Provider':
                dialog.getControl('TextField1').setText(self.Configuration.Url.Scope.Provider.ClientId)
                dialog.getControl('TextField2').setText(self.Configuration.Url.Scope.Provider.AuthorizationUrl)
                dialog.getControl('TextField3').setText(self.Configuration.Url.Scope.Provider.TokenUrl)
                dialog.getControl('TextField4').setText(self.Configuration.Url.Scope.Provider.ClientSecret)
                dialog.getControl('TextField5').setText(self.Configuration.Url.Scope.Provider.AuthorizationParameters)
                dialog.getControl('TextField6').setText(self.Configuration.Url.Scope.Provider.TokenParameters)
                method = self.Configuration.Url.Scope.Provider.CodeChallengeMethod
                name = 'OptionButton1' if method == 'S256' else 'OptionButton2'
                dialog.getControl(name).State = 1
                challenge = self.Configuration.Url.Scope.Provider.CodeChallenge
                control = dialog.getControl('CheckBox1')
                control.State = 1 if challenge else 0
                self._updateUI(dialog, control)
            elif item == 'Scope':
                values = self.Configuration.Url.Scope.Values
                dialog.getControl('ListBox1').Model.StringItemList = values

    def _saveData(self, window, dialog, method, item):
        if method == 'Remove':
            if item == 'Url':
                self.Configuration.Url.State = 8
            elif item == 'Provider':
                self.Configuration.Url.Scope.Provider.State = 8
            elif item == 'Scope':
                self.Configuration.Url.Scope.State = 8
            elif item == 'Value':
                control = window.getControl('ListBox1')
                control.Model.removeItem(control.SelectedItemPos)
        else:
            if item == 'Provider':
                clientid = dialog.getControl('TextField1').Text
                self.Configuration.Url.Scope.Provider.ClientId = clientid
                authorizationUrl = dialog.getControl('TextField2').Text
                self.Configuration.Url.Scope.Provider.AuthorizationUrl = authorizationUrl
                tokenUrl = dialog.getControl('TextField3').Text
                self.Configuration.Url.Scope.Provider.TokenUrl = tokenUrl
                challenge = bool(dialog.getControl('CheckBox1').State)
                self.Configuration.Url.Scope.Provider.CodeChallenge = challenge
                method = 'S256' if dialog.getControl('OptionButton1').State else 'plain'
                self.Configuration.Url.Scope.Provider.CodeChallengeMethod = method
                clientsecret = dialog.getControl('TextField4').Text
                self.Configuration.Url.Scope.Provider.ClientSecret = clientsecret
                authorizationparameters = dialog.getControl('TextField5').Text
                self.Configuration.Url.Scope.Provider.AuthorizationParameters = authorizationparameters
                tokenparameters = dialog.getControl('TextField6').Text
                self.Configuration.Url.Scope.Provider.TokenParameters = tokenparameters
                self.Configuration.Url.Scope.Provider.State = 4
            elif item == 'Scope':
                values = dialog.getControl('ListBox1').Model.StringItemList
                self.Configuration.Url.Scope.Values = values
                self.Configuration.Url.Scope.State = 4

    def _updateWindow(self, window, method, item, id):
        if method != 'Edit':
            if item == 'Url':
                urls = self.Configuration.UrlList
                control = window.getControl('ComboBox1')
                control.Model.StringItemList = urls
                control.setText(id)
            elif item == 'Provider':
                providers = self.Configuration.Url.ProviderList
                control = window.getControl('ComboBox2')
                control.Model.StringItemList = providers
                control.setText(id)
            elif item == 'Scope':
                scopes = self.Configuration.Url.ScopeList
                control = window.getControl('ComboBox3')
                control.Model.StringItemList = scopes
                control.setText(id)
            elif method == 'Add' and item == 'Value':
                window.getControl('TextField1').setText('')
            elif method == 'Remove' and item == 'Value':
                window.getControl('CommandButton2').Model.Enabled = False
        return True

    def _updateUI(self, window, control):
        item = control.Model.Tag
        if item == 'User':
            self.Wizard.updateTravelUI()
        elif item == 'Url':
            url = control.getText()
            urls = control.Model.StringItemList
            enabled = url in urls
            if enabled:
                self.Configuration.Url.Id = url
                title = self.stringResource.resolveString('PageWizard1.FrameControl2.Label')
                window.getControl('FrameControl2').Model.Label = title % url
                window.getControl('ComboBox2').setText(self.Configuration.Url.ProviderName)
                window.getControl('ComboBox3').setText(self.Configuration.Url.ScopeName)
            window.getControl('CommandButton1').Model.Enabled = url != '' and not enabled
            window.getControl('CommandButton2').Model.Enabled = enabled and len(urls) > 1
            self.Wizard.updateTravelUI()
        elif item == 'Provider':
            provider = control.getText()
            providers = control.Model.StringItemList
            scopes = ()
            enabled = provider in providers
            if enabled:
                self.Configuration.Url.ProviderName = provider
                scopes = self.Configuration.Url.ScopeList
            combobox = window.getControl('ComboBox3')
            combobox.Model.StringItemList = scopes
            if combobox.getText() != '':
                combobox.setText('')
            window.getControl('CommandButton3').Model.Enabled = provider != '' and not enabled
            window.getControl('CommandButton4').Model.Enabled = enabled
            window.getControl('CommandButton5').Model.Enabled = enabled and len(providers) > 1
            self.Wizard.activatePath(getActivePath(self.Configuration), True)
            self.Wizard.updateTravelUI()
        elif item == 'Scope':
            scope = control.getText()
            scopes = control.Model.StringItemList
            enabled = scope in scopes
            if enabled:
                self.Configuration.Url.ScopeName = scope
            window.getControl('CommandButton7').Model.Enabled = enabled
            window.getControl('CommandButton8').Model.Enabled = enabled and len(scopes) > 1
            scopes = self.Configuration.Url.ScopesList
            window.getControl('CommandButton6').Model.Enabled = scope != '' and scope not in scopes
            self.Wizard.updateTravelUI()
        elif item == 'Values':
            count = control.Model.ItemCount
            button = window.getControl('CommandButton2')
            button.Model.Enabled = control.SelectedItemPos != -1 and count > 1
        elif item == 'Value':
            value = control.getText()
            values = window.getControl('ListBox1').Model.StringItemList
            button = window.getControl('CommandButton1')
            button.Model.Enabled = value != '' and value not in values
        elif item == 'HttpHandler':
            address = window.getControl('TextField2').getText()
            self.Configuration.Url.Scope.Provider.RedirectAddress = address
            port = int(window.getControl('NumericField1').getValue())
            self.Configuration.Url.Scope.Provider.RedirectPort = port
            self.Configuration.Url.Scope.Provider.HttpHandler = True
            self.Wizard.activatePath(getActivePath(self.Configuration), True)
            window.getControl('TextField1').setText(self.AuthorizationStr)
            self.Wizard.updateTravelUI()
        elif item == 'GuiHandler':
            self.Configuration.Url.Scope.Provider.HttpHandler = False
            self.Wizard.activatePath(getActivePath(self.Configuration), True)
            window.getControl('TextField1').setText(self.AuthorizationStr)
            self.Wizard.updateTravelUI()
        elif item == 'CodeChallenge':
            enabled = bool(control.State)
            window.getControl('OptionButton1').Model.Enabled = enabled
            window.getControl('OptionButton2').Model.Enabled = enabled
        elif item == 'AuthorizationCode':
            enabled = window.getControl('TextField1').getText() != ''
            finish = uno.getConstantByName('com.sun.star.ui.dialogs.WizardButton.FINISH')
            self.Wizard.enableButton(finish, enabled)
            self.Wizard.updateTravelUI()
        return True

    def _getPropertySetInfo(self):
        properties = {}
        readonly = uno.getConstantByName('com.sun.star.beans.PropertyAttribute.READONLY')
        properties['Wizard'] = getProperty('Wizard', 'com.sun.star.ui.dialogs.XWizard', readonly)
        return properties
