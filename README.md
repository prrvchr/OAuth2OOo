# ![OAuth2OOo logo][1] OAuth2OOo

**Ce [document][2] en français.**

**The use of this software subjects you to our** [**Terms Of Use**][3] **and** [**Data Protection Policy**][4].

# version [0.0.6][5]

## Introduction:

**OAuth2OOo** is part of a [Suite][6] of [LibreOffice][7] and/or [OpenOffice][8] extensions allowing to offer you innovative services in these office suites.  
This extension is the implementation of the OAuth 2.0 protocol. Protocol allowing you to obtain your consent so that an application can access your data present at the GAFA.

Being free software I encourage you:
- To duplicate its [source code][9].
- To make changes, corrections, improvements.
- To open [issue][10] if needed.

In short, to participate in the development of this extension.
Because it is together that we can make Free Software smarter.

## Uno OAuth2.0 API for LibreOffice / OpenOffice.

![OAuth2OOo Wizard Page1 screenshot][11]

![OAuth2OOo Wizard Page2 screenshot][12]

![OAuth2OOo Wizard Page3 screenshot][13]

![OAuth2OOo Browser Page1 screenshot][14]

![OAuth2OOo Browser Page2 screenshot][15]

![OAuth2OOo Browser Page3 screenshot][16]

![OAuth2OOo Browser Page4 screenshot][17]

![OAuth2OOo Wizard Page4 screenshot][18]

The OAuth2 protocol allows access to server resources, after accepting the connection authorization, by exchanging tokens.

The revocation takes place in the management of the applications associated with your account.

No more password is stored in LibreOffice / OpenOffice.

## Install:

It seems important that the file was not renamed when it was downloaded.
If necessary, rename it before installing it.

- Install the ![OAuth2OOo logo][1] **[OAuth2OOo.oxt][19]** extension version 0.0.6.

- Restart LibreOffice / OpenOffice after installation.

## Use:

This extension is not made to be used alone, but provide OAuth2 service to other LibreOffice / OpenOffice extensions.  
Here's how we use its API:

### Create OAuth2 service:

> identifier = "com.gmail.prrvchr.extensions.OAuth2OOo.OAuth2Service"  
> service = ctx.ServiceManager.createInstanceWithContext(identifier, ctx)

### Initialize Session or at least Url:

- Initialize Session: 

> initialized = service.initializeSession(registered_url, user_account)

- Initialize Url:

> initialized = service.initializeUrl(registered_url)

The returned value: `initialized` is True if `registered_url` and/or `user_account` has been retreived from the OAuth2 service configuration.

### Get the access token:

> format = 'Bearer %s'  
> token = service.getToken(format)

## Has been tested with:

* LibreOffice 7.3.7.2 - Lubuntu 22.04 - LXQt 1.1.0

* LibreOffice 7.4.3.2.(x64) - Windows 10(x64)

* OpenOffice 4.1.13 - Lubuntu 22.04 - LXQt 0.17.0

I encourage you in case of problem :-(  
to create an [issue][10]  
I will try to solve it ;-)

## Historical:

### What has been done for version 0.0.5:

- Writing of a new [XWizard][20] interface in order to replace the Wizard service which became defective with version 6.4.x and 7.x of LibreOffice (see [bug 132110][21]).

    This new interface also fixes [bug 132661][22] and [bug 132666][23] and allows access to versions 6.4.x and 7.x of LibreOffice...

    In addition this new XWizard adds new functionality such as:

    - Automatic resizing of the Wizard to the dimensions of the first displayed page.
    - Automatic move to page X on opening if possible.

- Fixed an issue with tokens without expiration (as used by Dropbox) on testing their validity...

- Many other fix...

### What has been done for version 0.0.6:

- Rewrite of the OAuth2 wizard trying to follow the MCV model as best as possible. This wizard is made up of 5 pages inheriting from the UNO [XWizardPage][24] interface:

    - Page 1: [Controller][25] and [View][26]
    - Page 2: [Controller][27] and [View][28]
    - Page 3: [Controller][29] and [View][30]
    - Page 4: [Controller][31] and [View][32]
    - Page 5: [Controller][33] and [View][34]

- Rewrite of the three UNO services provided by the OAuth2OOo extension in three separate files:

    - The [OAuth2Service][35] service implementing the interface described in the [XOAuth2Service][36] IDL file.
    - The [OAuth2Dispacher][37] service implementing the UNO interface [XDispatchProvider][38].
    - The [OAuth2Handler][39] service implementing the UNO interface [XInteractionHandler2][40].

- Rewrite of the options dialog accessible by **Tools -> Options -> Internet -> Protocol OAuth2**. This dialog is composed of two windows:

    - The logging window: [Controller][41] and [View][42].
    - The OAuth2OOo extension configuration options window: [Controller][43] and [View][44].

- Rewrite a single model: [OAuth2Model][45] managing wizard, services and options dialog.

- Google loopback flow error has been fixed. See [Issue #10][46]

- Use for Dropbox their new OAuth2 API with expirable tokens.

- Many other fix...

### What remains to be done for version 0.0.6:

- Write the implementation of the Help button (CommandButton5) in the new [XWizard][20] interface.

- Add new language for internationalization...

- Anything welcome...

[1]: <https://prrvchr.github.io/OAuth2OOo/img/OAuth2OOo.png>
[2]: <https://prrvchr.github.io/OAuth2OOo/README_fr>
[3]: <https://prrvchr.github.io/OAuth2OOo/source/OAuth2OOo/registration/TermsOfUse_en>
[4]: <https://prrvchr.github.io/OAuth2OOo/source/OAuth2OOo/registration/PrivacyPolicy_en>
[5]: <https://prrvchr.github.io/OAuth2OOo#historical>
[6]: <https://prrvchr.github.io>
[7]: <https://www.libreoffice.org/download/download/>
[8]: <https://www.openoffice.org/download/index.html>
[9]: <https://github.com/prrvchr/OAuth2OOo>
[10]: <https://github.com/prrvchr/OAuth2OOo/issues/new>
[11]: <https://prrvchr.github.io/OAuth2OOo/img/OAuth2Wizard1.png>
[12]: <https://prrvchr.github.io/OAuth2OOo/img/OAuth2Wizard2.png>
[13]: <https://prrvchr.github.io/OAuth2OOo/img/OAuth2Wizard3.png>
[14]: <https://prrvchr.github.io/OAuth2OOo/img/OAuth2Wizard4.png>
[15]: <https://prrvchr.github.io/OAuth2OOo/img/OAuth2Wizard5.png>
[16]: <https://prrvchr.github.io/OAuth2OOo/img/OAuth2Wizard6.png>
[17]: <https://prrvchr.github.io/OAuth2OOo/img/OAuth2Wizard7.png>
[18]: <https://prrvchr.github.io/OAuth2OOo/img/OAuth2Wizard8.png>
[19]: <https://github.com/prrvchr/OAuth2OOo/raw/master/OAuth2OOo.oxt>
[20]: <https://github.com/prrvchr/OAuth2OOo/blob/master/uno/lib/uno/wizard/wizard.py>
[21]: <https://bugs.documentfoundation.org/show_bug.cgi?id=132110>
[22]: <https://bugs.documentfoundation.org/show_bug.cgi?id=132661>
[23]: <https://bugs.documentfoundation.org/show_bug.cgi?id=132666>
[24]: <https://www.openoffice.org/api/docs/common/ref/com/sun/star/ui/dialogs/XWizardPage.html>
[25]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/pythonpath/oauth2/wizard/page1/oauth2manager.py>
[26]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/pythonpath/oauth2/wizard/page1/oauth2view.py>
[27]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/pythonpath/oauth2/wizard/page2/oauth2manager.py>
[28]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/pythonpath/oauth2/wizard/page2/oauth2view.py>
[29]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/pythonpath/oauth2/wizard/page3/oauth2manager.py>
[30]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/pythonpath/oauth2/wizard/page3/oauth2view.py>
[31]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/pythonpath/oauth2/wizard/page4/oauth2manager.py>
[32]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/pythonpath/oauth2/wizard/page4/oauth2view.py>
[33]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/pythonpath/oauth2/wizard/page5/oauth2manager.py>
[34]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/pythonpath/oauth2/wizard/page5/oauth2view.py>
[35]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/OAuth2Service.py>
[36]: <https://github.com/prrvchr/OAuth2OOo/blob/master/uno/rdb/idl/com/sun/star/auth/XOAuth2Service.idl>
[37]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/OAuth2Dispatcher.py>
[38]: <https://www.openoffice.org/api/docs/common/ref/com/sun/star/frame/XDispatchProvider.html>
[39]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/OAuth2Handler.py>
[40]: <https://www.openoffice.org/api/docs/common/ref/com/sun/star/task/XInteractionHandler2.html>
[41]: <https://github.com/prrvchr/OAuth2OOo/blob/master/uno/lib/uno/logger/logmanager.py>
[42]: <https://github.com/prrvchr/OAuth2OOo/blob/master/uno/lib/uno/logger/logview.py>
[43]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/pythonpath/oauth2/options/optionsmanager.py>
[44]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/pythonpath/oauth2/options/optionsview.py>
[45]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/pythonpath/oauth2/oauth2model.py>
[46]: <https://github.com/prrvchr/OAuth2OOo/issues/10>
