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

![OAuth2OOo Wizard Page4 screenshot][17]

The OAuth2 protocol allows access to server resources, after accepting the connection authorization, by exchanging tokens.

The revocation takes place in the management of the applications associated with your account.

No more password is stored in LibreOffice / OpenOffice.

## Install:

It seems important that the file was not renamed when it was downloaded.
If necessary, rename it before installing it.

- Install the ![OAuth2OOo logo][1] **[OAuth2OOo.oxt][18]** extension version 0.0.6.

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

- Writing of a new [XWizard][19] interface in order to replace the Wizard service which became defective with version 6.4.x and 7.x of LibreOffice (see [bug 132110](https://bugs.documentfoundation.org/show_bug.cgi?id=132110)).

    This new interface also fixes [bug 132661][20] and [bug 132666][21] and allows access to versions 6.4.x and 7.x of LibreOffice...

    In addition this new XWizard adds new functionality such as:

    - Automatic resizing of the Wizard to the dimensions of the first displayed page.
    - Automatic move to page X on opening if possible.

- Fixed an issue with tokens without expiration (as used by Dropbox) on testing their validity...

- Many other fix...

### What has been done for version 0.0.6:

- Google loopback flow error has been fixed. See [Issue #10][22]

### What remains to be done for version 0.0.6:

- Write the implementation of the Help button (CommandButton5) in the new [XWizard][19] interface.

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
[18]: <https://github.com/prrvchr/OAuth2OOo/raw/master/OAuth2OOo.oxt>
[19]: <https://github.com/prrvchr/OAuth2OOo/blob/master/python/wizard.py>
[20]: <https://bugs.documentfoundation.org/show_bug.cgi?id=132661>
[21]: <https://bugs.documentfoundation.org/show_bug.cgi?id=132666>
[22]: <https://github.com/prrvchr/OAuth2OOo/issues/10>
