#!
# -*- coding: utf_8 -*-

import uno
import unohelper

from com.sun.star.ui.dialogs import XWizardController
from com.sun.star.awt import XContainerWindowEventHandler, XDialogEventHandler
from com.sun.star.uno import XReference

import unotools
from unotools import PyServiceInfo, PyPropertySet, PyInitialization
import base64
import hashlib
from requests.compat import urlencode, quote, unquote

# pythonloader looks for a static g_ImplementationHelper variable
g_ImplementationHelper = unohelper.ImplementationHelper()
g_ImplementationName = "com.gmail.prrvchr.extensions.OAuth2OOo.WizardController"


class PyWizardController(unohelper.Base, PyServiceInfo, PyPropertySet, PyInitialization,
                         XWizardController, XContainerWindowEventHandler, XDialogEventHandler, XReference):
    def __init__(self, ctx, *namedvalues):
        self.ctx = ctx
        self.properties = {}
        struct = "com.sun.star.beans.Property"
        readonly = uno.getConstantByName("com.sun.star.beans.PropertyAttribute.READONLY")
        transient = uno.getConstantByName("com.sun.star.beans.PropertyAttribute.TRANSIENT")
        self.properties["ResourceUrl"] = unotools.getProperty("ResourceUrl", "string", transient)
        self.properties["UserName"] = unotools.getProperty("UserName", "string", transient)
        self.properties["ActivePath"] = unotools.getProperty("ActivePath", "short", readonly)
        self.properties["AuthorizationCode"] = unotools.getProperty("AuthorizationCode", "string", transient)
        self.properties["AuthorizationUrl"] = unotools.getProperty("AuthorizationUrl", "string", readonly)
        self.properties["AuthorizationStr"] = unotools.getProperty("AuthorizationStr", "string", readonly)
        self.properties["CheckUrl"] = unotools.getProperty("CheckUrl", "boolean", readonly)
        self.properties["CodeVerifier"] = unotools.getProperty("CodeVerifier", "string", readonly)
        self.properties["Configuration"] = unotools.getProperty("Configuration", "com.sun.star.uno.XInterface", readonly)
        self.properties["Handler"] = unotools.getProperty("Handler", "any", transient)
        self.properties["Paths"] = unotools.getProperty("Paths", "[][]short", readonly)
        self.properties["State"] = unotools.getProperty("State", "string", readonly)
        self.properties["Wizard"] = unotools.getProperty("Wizard", "com.sun.star.ui.dialogs.XWizard", readonly)
        self._UserName = ""
        self._AuthorizationCode = ""
        self._Configuration = unotools.createService(self.ctx, "com.gmail.prrvchr.extensions.OAuth2OOo.ConfigurationWriter")
        self._Handler = None
        self._Paths = ((1, 2, 3), (1, 2, 4))
        self._CodeVerifier = unotools.generateUuid() + unotools.generateUuid()
        self._State = unotools.generateUuid()
        self.advanceTo = True
        self.locale = unotools.getCurrentLocale(self.ctx)
        identifier = "com.gmail.prrvchr.extensions.OAuth2OOo"
        self.stringResource = unotools.getStringResource(self.ctx, self.locale)
        self._Wizard = unotools.createService(self.ctx, "com.sun.star.ui.dialogs.Wizard")
        arguments = ((uno.Any("[][]short", (self.Paths)), self), )
        uno.invoke(self._Wizard, "initialize", arguments)
        self.initialize(namedvalues)

    @property
    def ResourceUrl(self):
        return self.Configuration.Url.Id
    @ResourceUrl.setter
    def ResourceUrl(self, url):
        self.Configuration.Url.Id = url
    @property
    def UserName(self):
        return self.Configuration.Url.Provider.Scope.User.Id
    @UserName.setter
    def UserName(self, name):
        self.Configuration.Url.Provider.Scope.User.Id = name
    @property
    def ActivePath(self):
        return 0 if self.Configuration.Url.Provider.HttpHandler else 1
    @property
    def AuthorizationCode(self):
        return self._AuthorizationCode
    @AuthorizationCode.setter
    def AuthorizationCode(self, code):
        self._AuthorizationCode = code
    @property
    def AuthorizationUrl(self):
        return self._getAuthorizationUrl()
    @property
    def AuthorizationStr(self):
        message = "" if self.CheckUrl else "Erreur: "
        return "%s%s" % (message, self._getAuthorizationStr())
    @property
    def CheckUrl(self):
        return self._checkUrl()
    @property
    def Configuration(self):
        return self._Configuration
    @property
    def Handler(self):
        return self._Handler
    @Handler.setter
    def Handler(self, handler):
        self._Handler = handler
    @property
    def Paths(self):
        return self._Paths
    @property
    def Wizard(self):
        return self._Wizard
    @property
    def CodeVerifier(self):
        return self._CodeVerifier
    @property
    def State(self):
        return self._State

    # XContainerWindowEventHandler, XDialogEventHandler
    def callHandlerMethod(self, window, event, method):
        handled = False
        if method == "Add":
            item = event.Source.Model.Tag
            id = self._addItem(window, item)
            if item == "Url" or item == "Value":
                handled = self._updateWindow(window, method, item, id)
            else:
                handled = self._showDialog(window, method, item, id)
        elif method == "Edit":
            item = event.Source.Model.Tag
            handled = self._showDialog(window, method, item)
        elif method == "Remove":
            item = event.Source.Model.Tag
            handled = self._showDialog(window, method, item)
        elif method == "Changed":
            handled = self._updateUI(window, event.Source)
        elif method == "Clicked":
            handled = self.callHandlerMethod(window, event, "Edit")
        return handled
    def getSupportedMethodNames(self):
        return ("Add", "Edit", "Remove", "Changed", "Clicked")

    # XWizardController
    def createPage(self, parent, id):
        window = self._createWindow(parent, id)
        service = "com.gmail.prrvchr.extensions.OAuth2OOo.WizardPage"
        page = unotools.createService(self.ctx, service, Controller=self, PageId=id, Window=window)
        if id == 1:
            window.getControl("TextField1").setText(self.UserName)
            urls = self.Configuration.UrlList
            control = window.getControl("ComboBox1")
            control.Model.StringItemList = urls
            providers = self.Configuration.Url.ProviderList
            window.getControl("ComboBox2").Model.StringItemList = providers
            url = self.ResourceUrl
            if url:
                control.setText(url)
        elif id == 2:
            address = self.Configuration.Url.Provider.RedirectAddress
            window.getControl("TextField2").setText(address)
            port = self.Configuration.Url.Provider.RedirectPort
            window.getControl("NumericField1").setValue(port)
            window.getControl("OptionButton%s" % self.ActivePath).setState(True)
        elif id == 3:
            service = "com.gmail.prrvchr.extensions.OAuth2OOo.HttpCodeHandler"
            self.Handler = unotools.createService(self.ctx, service)
            self.Handler.addCallback(page, self)
            self._openUrl(self.AuthorizationUrl)
        elif id == 4:
            self._openUrl(self.AuthorizationUrl)
        return page
    def getPageTitle(self, id):
        title = self.stringResource.resolveString("PageWizard%s.Step" % (id, ))
        return title
    def canAdvance(self):
        return True
    def onActivatePage(self, id):
        title = self.stringResource.resolveString("PageWizard%s.Title" % (id, ))
        self.Wizard.setTitle(title)
        finish = uno.getConstantByName("com.sun.star.ui.dialogs.WizardButton.FINISH")
        self.Wizard.enableButton(finish, False)
        if id == 1:
            self.Wizard.activatePath(self.ActivePath, True)
        self.Wizard.updateTravelUI()
#       if self.advanceTo:
#           self.advanceTo = False
#           self.Wizard.advanceTo(2)
    def onDeactivatePage(self, id):
        pass
    def confirmFinish(self):
        return True

    # XReference
    def dispose(self):
        self.Wizard.DialogWindow.dispose()
        if self.Handler is not None:
            self.Handler.cancel()

    def _createWindow(self, parent, id):
        provider = "com.sun.star.awt.ContainerWindowProvider"
        url = "vnd.sun.star.script:OAuth2OOo.PageWizard%s?location=application" % id
        return unotools.createService(self.ctx, provider).createContainerWindow(url, "", parent, self)

    def _addItem(self, window, item):
        if item == "Url":
            id = window.getControl("ComboBox1").getText()
            self.ResourceUrl = id
        elif item == "Provider":
            id = window.getControl("ComboBox2").getText()
            self.Configuration.Url.ProviderName = id
        elif item == "Scope":
            id = window.getControl("ComboBox3").getText()
            self.Configuration.Url.ScopeName = id
        elif item == "Value":
            id = window.getControl("TextField1").getText()
            control = window.getControl("ListBox1").Model
            control.insertItemText(control.ItemCount, id)
        return id

    def _showDialog(self, window, method, item, id=""):
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
        if method != "Remove":
            url = "vnd.sun.star.script:OAuth2OOo.%sDialog?location=application" % item
            provider = unotools.createService(self.ctx, "com.sun.star.awt.DialogProvider")
            dialog = provider.createDialogWithHandler(url, self)
        else:
            title = self.stringResource.resolveString("MessageBox.Title")
            message = self.stringResource.resolveString("MessageBox.Message")
            dialog = unotools.createMessageBox(window.Peer, message, title)
        return dialog

    def _initDialog(self, dialog, method, item):
        if method == "Edit":
            if item == "Provider":
                dialog.getControl("TextField1").setText(self.Configuration.Url.Provider.ClientId)
                dialog.getControl("TextField2").setText(self.Configuration.Url.Provider.AuthorizationUrl)
                dialog.getControl("TextField3").setText(self.Configuration.Url.Provider.TokenUrl)
                dialog.getControl("TextField4").setText(self.Configuration.Url.Provider.ClientSecret)
                pkce = self.Configuration.Url.Provider.CodeChallenge
                control = dialog.getControl("OptionButton1" if pkce else "OptionButton0")
                control.setState(True)
                self._updateUI(dialog, control)
            elif item == "Scope":
                values = self.Configuration.Url.Provider.Scope.Values
                dialog.getControl("ListBox1").Model.StringItemList = values

    def _saveData(self, window, dialog, method, item):
        if method == "Remove":
            if item == "Url":
                self.Configuration.Url.State = 8
            elif item == "Provider":
                self.Configuration.Url.Provider.State = 8
            elif item == "Scope":
                self.Configuration.Url.Provider.Scope.State = 8
            elif item == "Value":
                control = window.getControl("ListBox1")
                control.Model.removeItem(control.SelectedItemPos)
        else:
            if item == "Provider":
                clientid = dialog.getControl("TextField1").getText()
                self.Configuration.Url.Provider.ClientId = clientid
                authorizationUrl = dialog.getControl("TextField2").getText()
                self.Configuration.Url.Provider.AuthorizationUrl = authorizationUrl
                tokenUrl = dialog.getControl("TextField3").getText()
                self.Configuration.Url.Provider.TokenUrl = tokenUrl
                pkce = dialog.getControl("OptionButton1").getState()
                self.Configuration.Url.Provider.CodeChallenge = pkce
                clientsecret = dialog.getControl("TextField4").getText()
                self.Configuration.Url.Provider.ClientSecret = clientsecret
                self.Configuration.Url.Provider.State = 4
            elif item == "Scope":
                values = dialog.getControl("ListBox1").Model.StringItemList
                self.Configuration.Url.Provider.Scope.Values = values
                self.Configuration.Url.Provider.Scope.State = 4
            
    def _updateWindow(self, window, method, item, id):
        if method != "Edit":
            if item == "Url":
                urls = self.Configuration.UrlList
                control = window.getControl("ComboBox1")
                control.Model.StringItemList = urls
                control.setText(id)
            elif item == "Provider":
                providers = self.Configuration.Url.ProviderList
                control = window.getControl("ComboBox2")
                control.Model.StringItemList = providers
                control.setText(id)
            elif item == "Scope":
                scopes = self.Configuration.Url.ScopeList
                control = window.getControl("ComboBox3")
                control.Model.StringItemList = scopes
                control.setText(id)
            elif method == "Add" and item == "Value":
                window.getControl("TextField1").setText("")
            elif method == "Remove" and item == "Value":
                window.getControl("CommandButton2").Model.Enabled = False
        return True

    def _updateUI(self, window, control):
        item = control.Model.Tag
        if item == "User":
            self.Wizard.updateTravelUI()
        elif item == "Url":
            url = control.getText()
            urls = control.Model.StringItemList
            enabled = url in urls
            if enabled:
                self.ResourceUrl = url
                title = self.stringResource.resolveString("PageWizard1.FrameControl2.Label")
                window.getControl("FrameControl2").Model.Label = title % url
                window.getControl("ComboBox2").setText(self.Configuration.Url.ProviderName)
                window.getControl("ComboBox3").setText(self.Configuration.Url.ScopeName)
            window.getControl("CommandButton1").Model.Enabled = url != "" and not enabled
            window.getControl("CommandButton2").Model.Enabled = enabled and len(urls) > 1
            self.Wizard.updateTravelUI()
        elif item == "Provider":
            provider = control.getText()
            providers = control.Model.StringItemList
            scopes = ()
            enabled = provider in providers
            if enabled:
                self.Configuration.Url.ProviderName = provider
                scopes = self.Configuration.Url.ScopeList
            combobox = window.getControl("ComboBox3")
            combobox.Model.StringItemList = scopes
            if combobox.getText() != "":
                combobox.setText("")
            window.getControl("CommandButton3").Model.Enabled = provider != "" and not enabled
            window.getControl("CommandButton4").Model.Enabled = enabled
            window.getControl("CommandButton5").Model.Enabled = enabled and len(providers) > 1
            self.Wizard.activatePath(self.ActivePath, True)
            self.Wizard.updateTravelUI()
        elif item == "Scope":
            scope = control.getText()
            scopes = control.Model.StringItemList
            enabled = scope in scopes
            if enabled:
                self.Configuration.Url.ScopeName = scope
            window.getControl("CommandButton7").Model.Enabled = enabled
            window.getControl("CommandButton8").Model.Enabled = enabled and len(scopes) > 1
            scopes = self.Configuration.Url.ScopesList
            window.getControl("CommandButton6").Model.Enabled = scope != "" and scope not in scopes
            self.Wizard.updateTravelUI()
        elif item == "Values":
            count = control.Model.ItemCount
            button = window.getControl("CommandButton2")
            button.Model.Enabled = control.SelectedItemPos != -1 and count > 1
        elif item == "Value":
            value = control.getText()
            values = window.getControl("ListBox1").Model.StringItemList
            button = window.getControl("CommandButton1")
            button.Model.Enabled = value != "" and value not in values
        elif item == "HttpHandler":
            address = window.getControl("TextField2").getText()
            self.Configuration.Url.Provider.RedirectAddress = address
            port = int(window.getControl("NumericField1").getValue())
            self.Configuration.Url.Provider.RedirectPort = port
            self.Configuration.Url.Provider.HttpHandler = True
            self.Wizard.activatePath(self.ActivePath, True)
            window.getControl("TextField1").setText(self.AuthorizationStr)
            self.Wizard.updateTravelUI()
        elif item == "GuiHandler":
            self.Configuration.Url.Provider.HttpHandler = False
            self.Wizard.activatePath(self.ActivePath, True)
            window.getControl("TextField1").setText(self.AuthorizationStr)
            self.Wizard.updateTravelUI()
        elif item == "EnablePkce":
            window.getControl("TextField4").Model.Enabled = False
        elif item == "DisablePkce":
            window.getControl("TextField4").Model.Enabled = True
        elif item == "AuthorizationCode":
            enabled = window.getControl("TextField1").getText() != ""
            finish = uno.getConstantByName("com.sun.star.ui.dialogs.WizardButton.FINISH")
            self.Wizard.enableButton(finish, enabled)
            self.Wizard.updateTravelUI()
        return True

    def _getAuthorizationUrl(self):
        success, main, parameters = self._getUrlMainAndParameters()
        parameters = urlencode(self._getUrlParameters(parameters))
        return "%s?%s" % (main, parameters)

    def _getAuthorizationStr(self):
        presentation = "Error: "
        success, main, parameters = self._getUrlMainAndParameters()
        if success:
            transformer = unotools.createService(self.ctx, "com.sun.star.util.URLTransformer")
            url = uno.createUnoStruct("com.sun.star.util.URL")
            url.Complete = "%s?%s" % (main, self._getUrlArguments(parameters))
            success, url = transformer.parseStrict(url)
            if success:
                presentation = transformer.getPresentation(url, False)
        return presentation

    def _checkUrl(self):
        success, main, parameters = self._getUrlMainAndParameters()
        if success:
            transformer = unotools.createService(self.ctx, "com.sun.star.util.URLTransformer")
            url = uno.createUnoStruct("com.sun.star.util.URL")
            url.Complete = "%s?%s" % (main, self._getUrlArguments(parameters))
            success, url = transformer.parseStrict(url)
        return success

    def _getUrlMainAndParameters(self):
        main = self.Configuration.Url.Provider.AuthorizationUrl
        parameters = {}
        transformer = unotools.createService(self.ctx, "com.sun.star.util.URLTransformer")
        url = uno.createUnoStruct("com.sun.star.util.URL")
        url.Complete = main
        success, url = transformer.parseStrict(url)
        if success:
            main = url.Main
            parameters = self._getParametersFromArguments(url.Arguments)
        return success, main, parameters

    def _getParametersFromArguments(self, arguments):
        parameters = {}
        for arg in arguments.split("&"):
            parts = arg.split("=")
            if len(parts) > 1:
                name = unquote(parts[0]).strip()
                value = unquote("=".join(parts[1:])).strip()
                parameters[name] = value
        return parameters

    def _getUrlParameters(self, parameters={}):
        parameters["client_id"] = self.Configuration.Url.Provider.ClientId
        parameters["redirect_uri"] = self.Configuration.Url.Provider.RedirectUri
        parameters["response_type"] = "code"
        parameters["response_mode"] = "query"
        parameters["scope"] = self.Configuration.Url.Provider.Scope.Value
#        parameters["access_type"] = "offline"
        if self.Configuration.Url.Provider.CodeChallenge:
            parameters["code_challenge_method"] = "S256"
            parameters["code_challenge"] = self._getCodeChallenge()
        if self.Configuration.Url.Provider.ClientSecret:
            parameters["client_secret"] = self.Configuration.Url.Provider.ClientSecret
        parameters["login_hint"] = self.UserName
        parameters["prompt"] = "consent"
        parameters["hl"] = self.locale.Language
        parameters["state"] = self.State
        return parameters

    def _getUrlArguments(self, parameters={}):
        arguments = []
        parameters = self._getUrlParameters(parameters)
        for key, value in parameters.items():
            arguments.append("%s=%s" % (key, value))
        return "&".join(arguments)
            
    def _getCodeChallenge(self):
        code = hashlib.sha256(self.CodeVerifier.encode("utf-8")).digest()
        padding = {0:0, 1:2, 2:1}[len(code) % 3]
        challenge = base64.urlsafe_b64encode(code).decode("utf-8")
        return challenge[:len(challenge)-padding]

    def _openUrl(self, url, option=""):
        service = "com.sun.star.system.SystemShellExecute"
        self.ctx.ServiceManager.createInstance(service).execute(url, option, 0)


g_ImplementationHelper.addImplementation(PyWizardController,                        # UNO object class
                                         g_ImplementationName,                      # Implementation name
                                        (g_ImplementationName, ))                   # List of implemented services
