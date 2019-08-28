#!
# -*- coding: utf_8 -*-

import uno
import unohelper

from com.sun.star.awt import XContainerWindowEventHandler

from .unolib import PropertySet

from .dialoghandler import DialogHandler
from .unotools import getDialog
from .unotools import createMessageBox
from .unotools import createService
from .unotools import getCurrentLocale
from .unotools import getProperty
from .unotools import getStringResource
from .oauth2tools import getActivePath
from .oauth2tools import openUrl
#from .oauth2tools import g_wizard_paths
from .oauth2tools import g_identifier

import traceback

class WizardHandler(unohelper.Base,
                    XContainerWindowEventHandler):
    def __init__(self, ctx, configuration, wizard):
        self.ctx = ctx
        self.Configuration = configuration
        self.Wizard = wizard
        #self.Wizard = createService(self.ctx, 'com.sun.star.ui.dialogs.Wizard')
        #arguments = ((uno.Any('[][]short', (g_wizard_paths)), controller), )
        #uno.invoke(self.Wizard, 'initialize', arguments)
        self.stringResource = getStringResource(self.ctx, g_identifier, 'OAuth2OOo')
        #mri = self.ctx.ServiceManager.createInstance('mytools.Mri')
        #mri.inspect(self.Wizard)

    # XContainerWindowEventHandler
    def callHandlerMethod(self, window, event, method):
        try:
            handled = False
            print("WizardHandler.callHandlerMethod() %s - %s" % (method, handled))
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
            elif method == 'LoadUrl':
                handled = self._loadUrl(window, event.Source)
            elif method == 'StateChange':
                handled = self._updateUI(window, event.Source)
            elif method == 'TextChange':
                handled = self._updateUI(window, event.Source)
            elif method == 'PerformAction':
                handled = True
            print("WizardHandler.callHandlerMethod() %s - %s" % (method, handled))
            return handled
        except Exception as e:
            print("WizardHandler.callHandlerMethod() ERROR: %s - %s" % (e, traceback.print_exc()))
    def getSupportedMethodNames(self):
        return ('Add', 'Edit', 'Remove', 'Changed', 'Clicked', 'LoadUrl',
                'StateChange', 'TextChange', 'PerformAction')

    def _loadUrl(self, window, control):
        name = control.Model.Name
        url = self.stringResource.resolveString('PageWizard2.%s.Url' % name)
        openUrl(self.ctx, url)

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
        return id

    def _showDialog(self, window, method, item, id=''):
        print("WizardHandler._showDialog() %s - %s" % (method, item))
        dialog = self._getDialog(window, method, item)
        self._initDialog(dialog, method, item, id)
        if dialog.execute():
            self._saveData(window, dialog, method, item, id)
            print("WizardHandler._showDialog() %s - %s - %s" % (method, item, id))
            self._updateWindow(window, method, item, id)
        else:
            # TODO: need delete AddItem
            pass
        dialog.dispose()
        return True

    def _getDialog(self, window, method, item):
        if method != 'Remove':
            print("WizardHandler._getDialog() %s - %s" % (method, item))
            xdl = '%sDialog' % item
            handler = DialogHandler()
            dialog = getDialog(self.ctx, window.Peer, handler, 'OAuth2OOo', xdl)
        else:
            title = self.stringResource.resolveString('MessageBox.Title')
            message = self.stringResource.resolveString('MessageBox.Message')
            dialog = createMessageBox(window.Peer, message, title)
        return dialog

    def _initDialog(self, dialog, method, item, id):
        if item == 'Provider':
            if not id:
                id = self.Configuration.Url.ProviderName
            title = self.stringResource.resolveString('ProviderDialog.Title')
            dialog.setTitle(title % id)
            title = self.stringResource.resolveString('ProviderDialog.FrameControl1.Label')
            print("WizardHandler._initDialog() Provider")
            dialog.getControl('FrameControl1').Model.Label = title % id
            if method == 'Edit':
                clientid = self.Configuration.Url.Scope.Provider.ClientId
                dialog.getControl('TextField1').setText(clientid)
                authurl = self.Configuration.Url.Scope.Provider.AuthorizationUrl
                dialog.getControl('TextField2').setText(authurl)
                tokenurl = self.Configuration.Url.Scope.Provider.TokenUrl
                dialog.getControl('TextField3').setText(tokenurl)
                clientsecret = self.Configuration.Url.Scope.Provider.ClientSecret
                dialog.getControl('TextField4').setText(clientsecret)
                authparameters = self.Configuration.Url.Scope.Provider.AuthorizationParameters
                dialog.getControl('TextField5').setText(authparameters)
                tokenparameters = self.Configuration.Url.Scope.Provider.TokenParameters
                dialog.getControl('TextField6').setText(tokenparameters)
                # CodeChallengeMethod is 'S256' by default in ProviderDialog.xdl
                if self.Configuration.Url.Scope.Provider.CodeChallengeMethod == 'plain':
                    dialog.getControl('OptionButton2').State = 1
                # CodeChallenge is enabled by default in ProviderDialog.xdl
                if not self.Configuration.Url.Scope.Provider.CodeChallenge:
                    control = dialog.getControl('CheckBox1')
                    control.State = 0
                    self._updateUI(dialog, control)
                address = self.Configuration.Url.Scope.Provider.RedirectAddress
                dialog.getControl('TextField7').Text = address
                port = self.Configuration.Url.Scope.Provider.RedirectPort
                dialog.getControl('NumericField1').Value = port
                # HttpHandler is enabled by default in ProviderDialog.xdl
                if not self.Configuration.Url.Scope.Provider.HttpHandler:
                    control = dialog.getControl('OptionButton4')
                    control.State = 1
                    self._updateUI(dialog, control)
        elif item == 'Scope':
            if not id:
                id = self.Configuration.Url.ScopeName
            print("WizardHandler._initDialog() Scope: %s" % (id, ))
            title = self.stringResource.resolveString('ScopeDialog.Title')
            dialog.setTitle(title % id)
            title = self.stringResource.resolveString('ScopeDialog.FrameControl1.Label')
            dialog.getControl('FrameControl1').Model.Label = title % id
            if method == 'Edit':
                values = self.Configuration.Url.Scope.Values
                dialog.getControl('ListBox1').Model.StringItemList = values
                print("WizardHandler._initDialog() Scope: %s" % (values, ))

    def _saveData(self, window, dialog, method, item, id):
        if method == 'Remove':
            if item == 'Url':
                self.Configuration.Url.State = 8
            elif item == 'Provider':
                self.Configuration.Url.Scope.Provider.State = 8
            elif item == 'Scope':
                self.Configuration.Url.Scope.State = 8
        else:
            if item == 'Provider':
                clientid = dialog.getControl('TextField1').Text
                self.Configuration.Url.Scope.Provider.ClientId = clientid
                authurl = dialog.getControl('TextField2').Text
                self.Configuration.Url.Scope.Provider.AuthorizationUrl = authurl
                tokenurl = dialog.getControl('TextField3').Text
                self.Configuration.Url.Scope.Provider.TokenUrl = tokenurl
                challenge = bool(dialog.getControl('CheckBox1').State)
                self.Configuration.Url.Scope.Provider.CodeChallenge = challenge
                method = 'S256' if dialog.getControl('OptionButton1').State else 'plain'
                self.Configuration.Url.Scope.Provider.CodeChallengeMethod = method
                clientsecret = dialog.getControl('TextField4').Text
                self.Configuration.Url.Scope.Provider.ClientSecret = clientsecret
                authparameters = dialog.getControl('TextField5').Text
                self.Configuration.Url.Scope.Provider.AuthorizationParameters = authparameters
                tokenparameters = dialog.getControl('TextField6').Text
                self.Configuration.Url.Scope.Provider.TokenParameters = tokenparameters
                address = dialog.getControl('TextField7').Text
                self.Configuration.Url.Scope.Provider.RedirectAddress = address
                port = int(dialog.getControl('NumericField1').Value)
                self.Configuration.Url.Scope.Provider.RedirectPort = port
                enabled = bool(dialog.getControl('OptionButton3').State)
                print("WizardHandler._saveData() Provider %s" % enabled)
                self.Configuration.Url.Scope.Provider.HttpHandler = enabled
                self.Configuration.Url.Scope.Provider.State = 4
                self.Wizard.activatePath(0 if enabled else 1, True)
                self.Wizard.updateTravelUI()
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
        return True

    def _updateControl1(self, window, control, selection=''):
        return True

    def _updateControl(self, window, control, selection=''):
        item = control.Model.Tag
        if not selection:
            print("WizardHandler._updateControl() ******************************************")
            selection = control.SelectedText
        print("WizardHandler._updateControl() 1 %s - %s" % (item, selection))
        if item == 'Url':
            self.Configuration.Url.Id = selection
            provider = self.Configuration.Url.ProviderName
            scope = self.Configuration.Url.ScopeName
            print("WizardHandler._updateControl() 1 %s - %s - %s" % (item, provider, scope))
            window.getControl('ComboBox2').Text = provider
            window.getControl('ComboBox3').Text = scope
        elif item == 'Provider':
            self.Configuration.Url.ProviderName = selection
            scopes = window.getControl('ComboBox3')
            print("WizardHandler._updateControl() 1 %s - %s" % (item, self.Configuration.Url.ScopeList))
            scopes.Model.StringItemList = self.Configuration.Url.ScopeList
            scopes.Text = ''
            self.Wizard.activatePath(getActivePath(self.Configuration), True)
        elif item == 'Scope':
            self.Configuration.Url.ScopeName = selection
            #self.Wizard.updateTravelUI()
        return True

    def _isSelected(self, control, item=''):
        item = item if item else control.Text
        # TODO: OpenOffice dont return a empty <tuple> but a <ByteSequence instance ''> on
        # ComboBox.Model.StringItemList if StringItemList is empty!!!
        # items = control.Model.StringItemList
        items = control.Model.StringItemList if control.ItemCount else ()
        return item in items

    def _isEdited(self, control, item=''):
        item = item if item else control.Text
        # TODO: OpenOffice dont return a empty <tuple> but a <ByteSequence instance ''> on
        # ComboBox.Model.StringItemList if StringItemList is empty!!!
        # items = control.Model.StringItemList
        items = control.Model.StringItemList if control.ItemCount else ()
        return item != '' and item not in items

    def _updateUI(self, window, control):
        try:
            item = control.Model.Tag
            print("WizardHandler._updateUI() %s - %s" % (item, control.Model.Name))
            if item == 'User':
                self.Wizard.updateTravelUI()
            elif item == 'Url':
                url = control.Text
                if self._isSelected(control, url):
                    self._updateControl(window, control, url)
                    window.getControl('CommandButton1').Model.Enabled = False
                    window.getControl('CommandButton2').Model.Enabled = True
                else:
                    canadd = url != ''
                    canadd &= self._isSelected(window.getControl('ComboBox2'))
                    canadd &= self._isSelected(window.getControl('ComboBox3'))
                    window.getControl('CommandButton1').Model.Enabled = canadd
                    window.getControl('CommandButton2').Model.Enabled = False
                    providers = window.getControl('ComboBox2')
                    #providers.setText('')
                title = self.stringResource.resolveString('PageWizard1.FrameControl2.Label')
                window.getControl('FrameControl2').Model.Label = title % url
                self.Wizard.updateTravelUI()
            elif item == 'Provider':
                provider = control.Text
                if self._isSelected(control, provider):
                    self._updateControl(window, control, provider)
                    canadd = self._isEdited(window.getControl('ComboBox1'))
                    canadd &= self._isSelected(window.getControl('ComboBox3'))
                    window.getControl('CommandButton1').Model.Enabled = canadd
                    window.getControl('CommandButton3').Model.Enabled = False
                    window.getControl('CommandButton4').Model.Enabled = True
                    window.getControl('CommandButton5').Model.Enabled = True
                else:
                    canadd = provider != ''
                    canadd &= self._isEdited(window.getControl('ComboBox3'))
                    window.getControl('CommandButton1').Model.Enabled = False
                    window.getControl('CommandButton3').Model.Enabled = canadd
                    window.getControl('CommandButton4').Model.Enabled = False
                    window.getControl('CommandButton5').Model.Enabled = False
                    scopes = window.getControl('ComboBox3')
                    scopes.Model.StringItemList = ()
                    scopes.setText('')
                #self.Wizard.activatePath(getActivePath(self.Configuration), True)
                self.Wizard.updateTravelUI()
            elif item == 'Scope':
                scope = control.Text
                if self._isSelected(control, scope):
                    self._updateControl(window, control, scope)
                    canadd = self._isEdited(window.getControl('ComboBox1'))
                    canadd &= self._isSelected(window.getControl('ComboBox2'))
                    window.getControl('CommandButton1').Model.Enabled = canadd
                    window.getControl('CommandButton6').Model.Enabled = False
                    window.getControl('CommandButton7').Model.Enabled = True
                    window.getControl('CommandButton8').Model.Enabled = True
                else:
                    canadd = scope != ''
                    canadd &= window.getControl('ComboBox2').Text != ''
                    window.getControl('CommandButton1').Model.Enabled = False
                    window.getControl('CommandButton6').Model.Enabled = canadd
                    canadd &= self._isEdited(window.getControl('ComboBox2'))
                    window.getControl('CommandButton3').Model.Enabled = canadd
                    window.getControl('CommandButton7').Model.Enabled = False
                    window.getControl('CommandButton8').Model.Enabled = False
                print("WizardHandler._updateUI() %s  - %s - %s" % (item, scope, control.SelectedText))
                self.Wizard.updateTravelUI()
            elif item == 'AcceptPolicy':
                print("WizardHandler._updateUI() %s - %s" % (item, control.State))
                self.Wizard.updateTravelUI()
            elif item == 'AuthorizationCode':
                enabled = window.getControl('TextField1').Text != ''
                finish = uno.getConstantByName('com.sun.star.ui.dialogs.WizardButton.FINISH')
                self.Wizard.enableButton(finish, enabled)
                self.Wizard.updateTravelUI()
            return True
        except Exception as e:
            print("WizardHandler._updateUI() ERROR: %s - %s" % (e, traceback.print_exc()))
