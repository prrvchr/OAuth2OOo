# Documentation

**Ce [document][2] en français.**

**The use of this software subjects you to our [Terms Of Use][3] and [Data Protection Policy][4].**

# version [1.1.2][5]

## Introduction:

**OAuth2OOo** is part of a [Suite][6] of [LibreOffice][7] ~~and/or [OpenOffice][8]~~ extensions allowing to offer you innovative services in these office suites.  
This extension is the implementation of the OAuth 2.0 protocol. Protocol allowing you to obtain your consent so that an application can access your data present at the GAFA.

Being free software I encourage you:
- To duplicate its [source code][9].
- To make changes, corrections, improvements.
- To open [issue][10] if needed.

In short, to participate in the development of this extension.
Because it is together that we can make Free Software smarter.

___
## Requirement:

In order to take advantage of the latest versions of the Python libraries used in OAuth2OOo, version 2 of Python has been abandoned in favor of **Python 3.8 minimum**.  
This means that **OAuth2OOo no longer supports OpenOffice and LibreOffice 6.x on Windows since version 1.1.0**.
I can only advise you **to migrate to LibreOffice 7.x**.

To offer you all these new services in LibreOffice, the OAuth2OOo extension uses many Python libraries.
Some of these libraries embed binary files which depend on:
- Python version (between 3.8 and 3.11 included)
- Operating system (Linux, Windows, Macos, etc...)
- The architecture of your computer (i386, adm x64, arm64, ppc, etc...)

Three libraries or **Python packages** depend on your system and have the following embedded binaries:
- [Binaries][11] for package [charset-normalizer][12] version 3.1.0.
- [Binaries][13] for package [ijson][14] version 3.2.2.
- [Binaries][15] for package [lxml][16] version 4.9.2.

For all these reasons:
- If you are **on Windows all the different necessary binaries come with the OAuth2OOo extension**.
- If you are **on Linux x86_64 necessary binaries for Python version 3.10 come with the OAuth2OOo extension**.
- **For all other possible configuration combinations, if they are not already present, you will need to install these 3 python packages**.  
In their absence, an error should appear when installing the OAuthOOo extension while importing the lxml package.
This error can be corrected by installing, usually with the help of [pip][17], the 3 Python packages required by your configuration.

If you want to **drive Firefox in Calc on Ubuntu** then you need to reinstall Firefox from the Mozilla PPA.
To install the Mozilla PPA please type the command:
- `sudo add-apt-repository ppa:mozillateam/ppa`

___
## Install:

It seems important that the file was not renamed when it was downloaded.
If necessary, rename it before installing it.

- Install the ![OAuth2OOo logo][1] **[OAuth2OOo.oxt][18]** extension version 1.1.2.

- Restart LibreOffice / OpenOffice after installation.

___
## Use:

This extension is not made to be used alone, but provide OAuth2 service to other LibreOffice ~~/ OpenOffice~~ extensions.  
Here's how we use its API:

### Create OAuth2 service:

> identifier = "io.github.prrvchr.OAuth2OOo.OAuth2Service"  
> service = ctx.ServiceManager.createInstanceWithContext(identifier, ctx)

### Initialize Session or at least Url:

- Initialize Session: 

> initialized = service.initializeSession(registered_url, user_account)

The return value: `initialized` is True if `user_account` is already authorized for `registered_url`.

- Initialize Url:

> initialized = service.initializeUrl(registered_url)

The return value: `initialized` is True if `registered_url` was successfully found in the OAuth2 service configuration.

### Get the access token:

> format = 'Bearer %s'  
> token = service.getToken(format)

___
## Uno OAuth2.0 API for LibreOffice.

![OAuth2OOo Wizard Page1 screenshot][19]

![OAuth2OOo Wizard Page2 screenshot][20]

![OAuth2OOo Wizard Page3 screenshot][21]

![OAuth2OOo Browser Page1 screenshot][22]

![OAuth2OOo Browser Page2 screenshot][23]

![OAuth2OOo Browser Page3 screenshot][24]

![OAuth2OOo Browser Page4 screenshot][25]

![OAuth2OOo Wizard Page4 screenshot][26]

The OAuth2 protocol allows access to server resources, after accepting the connection authorization, by exchanging tokens.

The revocation takes place in the management of the applications associated with your account.

No more password is stored in LibreOffice.

___
## Has been tested with:

* LibreOffice 7.3.7.2 - Lubuntu 22.04 - Python version 3.10.12

* LibreOffice 7.5.4.2(x86) - Windows 10 - Python version 3.8.16 (under Lubuntu 22.04 / VirtualBox 6.1.38)

* LibreOffice 7.4.3.2(x64) - Windows 10(x64) - Python version 3.8.15 (under Lubuntu 22.04 / VirtualBox 6.1.38)

* **Does not work with OpenOffice** see [bug 128569][27]. Having no solution, I encourage you to install **LibreOffice**.

I encourage you in case of problem :confused:  
to create an [issue][10]  
I will try to solve it :smile:

___
## Historical:

### What has been done for version 0.0.5:

- Writing of a new [XWizard][28] interface in order to replace the Wizard service which became defective with version 6.4.x and 7.x of LibreOffice (see [bug 132110][29]).

    This new interface also fixes [bug 132661][30] and [bug 132666][31] and allows access to versions 6.4.x and 7.x of LibreOffice...

    In addition this new XWizard adds new functionality such as:

    - Automatic resizing of the Wizard to the dimensions of the first displayed page.
    - Automatic move to page X on opening if possible.

- Fixed an issue with tokens without expiration (as used by Dropbox) on testing their validity...

- Many other fix...

### What has been done for version 0.0.6:

- Rewrite of the OAuth2 wizard trying to follow the [MVA model][32] as best as possible. This wizard is made up of 5 pages inheriting from the UNO [XWizardPage][33] interface:

    - Page 1: [Adapter][34] and [View][35]
    - Page 2: [Adapter][36] and [View][37]
    - Page 3: [Adapter][38] and [View][39]
    - Page 4: [Adapter][40] and [View][41]
    - Page 5: [Adapter][42] and [View][43]

- Rewrite of the three UNO services provided by the OAuth2OOo extension in three separate files:

    - The [OAuth2Service][44] service implementing the interface described in the [XOAuth2Service][45] IDL file.
    - The [OAuth2Dispacher][46] service implementing the UNO interface [XDispatchProvider][47].
    - The [OAuth2Handler][48] service implementing the UNO interface [XInteractionHandler2][49].

- Rewrite of the options dialog accessible by **Tools -> Options -> Internet -> Protocol OAuth2**. This dialog is composed of two windows:

    - The logging window: [Adapter][50] and [View][51].
    - The OAuth2OOo extension configuration options window: [Adapter][52] and [View][53].

- Rewrite a single data model: [OAuth2Model][54] managing wizard, services and options dialog.

- Google loopback flow error has been fixed. See [Issue #10][55]

- Use for Dropbox their new OAuth2 API with expirable tokens.

- Many other fix...

### What has been done for version 1.0.0:

- Porting Python API [Requests][56] to LibreOffice / OpenOffice UNO API. Two UNO interfaces are accessible:

    - HTTP request parameters: [com.sun.star.rest.XRequestParameter.idl][57]
    - The response to the HTTP request: [com.sun.star.rest.XRequestResponse.idl][58]  

    The XRequestParameter interface supports sync token handling as well as HTTP request paging, as used in the HTTP Rest APIs

- Uploading and downloading files is possible thanks to the methods or properties:

    - `XOAuth2Service.download()` allowing resumable file download.
    - `XOAuth2Service.upload()` allowing resumable file upload.
    - `XOAuth2Service.getInputStream()` to get an input stream.
    - `XRequestParameter.DataSink` to set an input stream.
    - `XRequestResponse.getInputStream()` to get an input stream.

- Porting Java API [javax.json][59] to LibreOffice / OpenOffice UNO API as defined in idl files: [com.sun.star.json.*][60]

    - A factory of JSON structures is accessible via the `getJsonBuilder()` interface of [XRequestParameter][57].
    - A Json parser is returned by the `getJson()` interface of [XRequestResponse][58].

**This makes HTTP requests using JSON easily usable in the Basic language of LibreOffice.**

See the macros [HTTP requests in Basic][61] and [ChatGPT requests in Basic][62].

### What has been done for version 1.0.1:

- Writing of 15 functions in Calc AddIns as described in the following files:

    - The file [OAuth2Plugin.idl][63] which declares new interfaces to UNO.
    - The file [CalcAddIns.xcu][64] which makes available these new interfaces in the list of Calc functions.
    - The file [OAuth2Plugin.py][65] which is the implementation of the UNO service `com.sun.star.auth.Oauth2Plugin` providing these new interfaces.
    - The file [plugin.py][66] which is the library implementing the interfaces of this new UNO service.

- These 4 new files give access to **15 new Calc formulas** which are:

    - `GETHTTPBOBY(URL,METHOD,ENCODING,PARAMETERS)`
    - `PARSEHTML(DATA,PATH,BASEURL)`
    - `PARSEXML(DATA,PATH,BASEURL)`
    - `PARSEJSON(DATA,PATH)`
    - `JAVASCRIPT2XML(DATA,PATH)`
    - `XML2JSON(DATA,PATH)`
    - `JAVASCRIPT2JSON(DATA,PATH)`
    - `DUBLINCORE2JSON(DATA,BASEURL)`
    - `JSONLD2JSON(DATA,BASEURL)`
    - `MICRODATA2JSON(DATA,BASEURL)`
    - `MICROFORMAT2JSON(DATA,BASEURL)`
    - `OPENGRAPH2JSON(DATA,BASEURL)`
    - `RDFA2JSON(DATA,BASEURL)`
    - `FLATTENJSON(DATA,TYPENAME,PATH,SEPARATOR)`
    - `SPLITJSON(DATA,TYPENAME,PATH,SEPARATOR)`

- A good example is better than a long speech, so I invite you to download two Calc sheets allowing you to very easily recover HTML micro data from any Web site.

    - [LDLC Home.ods][67]
    - [LDLC poducts.ods][68]

### What has been done for version 1.1.0:

- **End of support for Python 2.x and therefore for OpenOffice**.

- Integration of [Selenium][69] version 4.10 in the extension in order to make **LibreOffice able to control a browser via Calc formulas** inserted in a spreadsheet.

- Use of [webdriver_manager][70] version 3.8.6 to automate the installation of the browser's [WebDriver][71].

- Creation of 5 Calc formulas allowing the **piloting of the browser**:

    - `BROWSEROPEN(BROWSER,PATH,INIT,OPTIONS)`
    - `BROWSERCLICK(SESSION,BY,PATH,URL,INIT,WAIT)`
    - `BROWSERFIELD(SESSION,BY,PATH,VALUE,URL,INIT,WAIT)`
    - `BROWSERFORM(SESSION,FORM,URL,INIT,WAIT)`
    - `BROWSERCONTENT(SESSION,URL,ENCODING)`

- Creation of a Calc formula allowing HTTP Basic Auth authentication for HTTP requests:

    - `HTTPAUTH(NAME,PASSWORD)`

- Calc formula `GETHTTPBOBY` has been renamed to `HTTPCONTENT`.

### What has been done for version 1.1.1:

- Fixed an issue in [the implementation][72] of the [com.sun.star.rest.XRequestParameter][57] interface not allowing to create empty JSON objects (ie: "Object": {} ) as requested by the Microsoft Graph API.

### What has been done for version 1.1.2:

- Modification of the idl files: [XRequestParameter.idl][57] and [XRequestResponse.idl][58] and the underlying python implementations: [requestparameter.py][72] and [requestresponse.py][73] in order to make it possible **POST** requests with **application/x-www-form-urlencoded** encoding.

- 3 macros in Basic: `ChatGPTRequest`, `HTTPGetRequest` and `HTTPPostRequest` are available in: **Tools -> Macros -> Run Macros... -> My Macros -> OAuth2OOo**. Be careful, these macros **will not work if no document is open** (I don't know why?)...

- From now on, with each push, a [workflow perform a scan][74] on the code with [Fluid Attacks][75]. This has been implemented to follow the [Cloud Application Security Assessment][76] (CASA) and meet the requirements for revalidation of the OAuth2OOo extension with Google.

- For the same reasons, the [Data Protection Policy][4] has been modified in order to specify the [Nature and scope rights over your data][77].

### What remains to be done for version 1.1.2:

- Add new language for internationalization...

- Anything welcome...

[1]: <https://prrvchr.github.io/OAuth2OOo/img/OAuth2OOo.svg>
[2]: <https://prrvchr.github.io/OAuth2OOo/README_fr>
[3]: <https://prrvchr.github.io/OAuth2OOo/source/OAuth2OOo/registration/TermsOfUse_en>
[4]: <https://prrvchr.github.io/OAuth2OOo/source/OAuth2OOo/registration/PrivacyPolicy_en>
[5]: <https://prrvchr.github.io/OAuth2OOo/#what-has-been-done-for-version-110>
[6]: <https://prrvchr.github.io>
[7]: <https://www.libreoffice.org/download/download/>
[8]: <https://www.openoffice.org/download/index.html>
[9]: <https://github.com/prrvchr/OAuth2OOo>
[10]: <https://github.com/prrvchr/OAuth2OOo/issues/new>
[11]: <https://github.com/prrvchr/OAuth2OOo/blob/master/uno/lib/python/charset_normalizer>
[12]: <https://pypi.org/project/charset-normalizer/3.1.0/#files>
[13]: <https://github.com/prrvchr/OAuth2OOo/blob/master/uno/lib/python/ijson/backends>
[14]: <https://pypi.org/project/ijson/3.2.2/#files>
[15]: <https://github.com/prrvchr/OAuth2OOo/blob/master/uno/lib/python/lxml>
[16]: <https://pypi.org/project/lxml/4.9.2/#files>
[17]: <https://packaging.python.org/en/latest/tutorials/installing-packages/#use-pip-for-installing>
[18]: <https://github.com/prrvchr/OAuth2OOo/raw/master/OAuth2OOo.oxt>
[19]: <https://prrvchr.github.io/OAuth2OOo/img/OAuth2Wizard1.png>
[20]: <https://prrvchr.github.io/OAuth2OOo/img/OAuth2Wizard2.png>
[21]: <https://prrvchr.github.io/OAuth2OOo/img/OAuth2Wizard3.png>
[22]: <https://prrvchr.github.io/OAuth2OOo/img/OAuth2Wizard4.png>
[23]: <https://prrvchr.github.io/OAuth2OOo/img/OAuth2Wizard5.png>
[24]: <https://prrvchr.github.io/OAuth2OOo/img/OAuth2Wizard6.png>
[25]: <https://prrvchr.github.io/OAuth2OOo/img/OAuth2Wizard7.png>
[26]: <https://prrvchr.github.io/OAuth2OOo/img/OAuth2Wizard8.png>
[27]: <https://bz.apache.org/ooo/show_bug.cgi?id=128569>
[28]: <https://github.com/prrvchr/OAuth2OOo/blob/master/uno/lib/uno/wizard/wizard.py>
[29]: <https://bugs.documentfoundation.org/show_bug.cgi?id=132110>
[30]: <https://bugs.documentfoundation.org/show_bug.cgi?id=132661>
[31]: <https://bugs.documentfoundation.org/show_bug.cgi?id=132666>
[32]: <https://en.wikipedia.org/wiki/Model%E2%80%93view%E2%80%93adapter>
[33]: <https://www.openoffice.org/api/docs/common/ref/com/sun/star/ui/dialogs/XWizardPage.html>
[34]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/service/pythonpath/oauth2/wizard/page1/oauth2manager.py>
[35]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/service/pythonpath/oauth2/wizard/page1/oauth2view.py>
[36]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/service/pythonpath/oauth2/wizard/page2/oauth2manager.py>
[37]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/service/pythonpath/oauth2/wizard/page2/oauth2view.py>
[38]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/service/pythonpath/oauth2/wizard/page3/oauth2manager.py>
[39]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/service/pythonpath/oauth2/wizard/page3/oauth2view.py>
[40]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/service/pythonpath/oauth2/wizard/page4/oauth2manager.py>
[41]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/service/pythonpath/oauth2/wizard/page4/oauth2view.py>
[42]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/service/pythonpath/oauth2/wizard/page5/oauth2manager.py>
[43]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/service/pythonpath/oauth2/wizard/page5/oauth2view.py>
[44]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/service/OAuth2Service.py>
[45]: <https://github.com/prrvchr/OAuth2OOo/blob/master/uno/rdb/idl/com/sun/star/auth/XOAuth2Service.idl>
[46]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/service/OAuth2Dispatcher.py>
[47]: <https://www.openoffice.org/api/docs/common/ref/com/sun/star/frame/XDispatchProvider.html>
[48]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/service/OAuth2Handler.py>
[49]: <https://www.openoffice.org/api/docs/common/ref/com/sun/star/task/XInteractionHandler2.html>
[50]: <https://github.com/prrvchr/OAuth2OOo/blob/master/uno/lib/uno/logger/logmanager.py>
[51]: <https://github.com/prrvchr/OAuth2OOo/blob/master/uno/lib/uno/logger/logview.py>
[52]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/service/pythonpath/oauth2/options/optionsmanager.py>
[53]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/service/pythonpath/oauth2/options/optionsview.py>
[54]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/service/pythonpath/oauth2/oauth2model.py>
[55]: <https://github.com/prrvchr/OAuth2OOo/issues/10>
[56]: <https://pypi.org/project/requests/2.31.0/>
[57]: <https://github.com/prrvchr/OAuth2OOo/blob/master/uno/rdb/idl/com/sun/star/rest/XRequestParameter.idl>
[58]: <https://github.com/prrvchr/OAuth2OOo/blob/master/uno/rdb/idl/com/sun/star/rest/XRequestResponse.idl>
[59]: <https://javadoc.io/static/javax.json/javax.json-api/1.1.4/index.html?overview-summary.html>
[60]: <https://github.com/prrvchr/OAuth2OOo/tree/master/uno/rdb/idl/com/sun/star/json>
[61]: <https://forum.openoffice.org/en/forum/viewtopic.php?t=110092>
[62]: <https://forum.openoffice.org/en/forum/viewtopic.php?t=110118>
[63]: <https://github.com/prrvchr/OAuth2OOo/tree/master/uno/rdb/idl/com/sun/star/auth/XOAuth2Plugin.idl>
[64]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/CalcAddIns.xcu>
[65]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/service/OAuth2Plugin.py>
[66]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/service/pythonpath/oauth2/plugin.py>
[67]: <https://forum.openoffice.org/en/forum/download/file.php?id=47297>
[68]: <https://forum.openoffice.org/en/forum/download/file.php?id=47301>
[69]: <https://pypi.org/project/selenium/4.10/>
[70]: <https://pypi.org/project/webdriver-manager/3.8.6/>
[71]: <https://developer.mozilla.org/en-US/docs/Web/WebDriver>
[72]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/service/pythonpath/oauth2/requestparameter.py>
[73]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/service/pythonpath/oauth2/requestresponse.py>
[74]: <https://github.com/prrvchr/OAuth2OOo/actions/workflows/dev.yml>
[75]: <https://github.com/fluidattacks>
[76]: <https://appdefensealliance.dev/casa/tier-2/tier2-overview>
[77]: <https://prrvchr.github.io/OAuth2OOo/source/OAuth2OOo/registration/PrivacyPolicy_en#nature-and-scope-rights-over-your-data>
