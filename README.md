<!--
╔════════════════════════════════════════════════════════════════════════════════════╗
║                                                                                    ║
║   Copyright (c) 2020 https://prrvchr.github.io                                     ║
║                                                                                    ║
║   Permission is hereby granted, free of charge, to any person obtaining            ║
║   a copy of this software and associated documentation files (the "Software"),     ║
║   to deal in the Software without restriction, including without limitation        ║
║   the rights to use, copy, modify, merge, publish, distribute, sublicense,         ║
║   and/or sell copies of the Software, and to permit persons to whom the Software   ║
║   is furnished to do so, subject to the following conditions:                      ║
║                                                                                    ║
║   The above copyright notice and this permission notice shall be included in       ║
║   all copies or substantial portions of the Software.                              ║
║                                                                                    ║
║   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,                  ║
║   EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES                  ║
║   OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.        ║
║   IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY             ║
║   CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,             ║
║   TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE       ║
║   OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.                                    ║
║                                                                                    ║
╚════════════════════════════════════════════════════════════════════════════════════╝
-->
# [![OAuth2OOo logo][1]][2] Documentation

**Ce [document][3] en français.**

**The use of this software subjects you to our [Terms Of Use][4] and [Data Protection Policy][5].**

# version [1.4.1][6]

## Introduction:

**OAuth2OOo** is part of a [Suite][7] of [LibreOffice][8] ~~and/or [OpenOffice][9]~~ extensions allowing to offer you innovative services in these office suites.

This extension is the implementation of the [OAuth 2.0 protocol][10]. Protocol allowing you to obtain your consent so that an application can access your data present at the GAFA.

It allows **executing HTTP requests in BASIC** and provides the following macros as an example:
- [HTTPGetRequest][11]
- [HTTPPostRequest][12]
- [ChatGPTRequest][13]
- [GoogleAPIRequest][14]
- [GraphAPIRequest][15]

If you open a document beforehand, you can launch them by:  
**Tools -> Macros -> Run Macro... -> My Macros -> OAuth2OOo -> `macro-name` -> Main -> Run**

It also allows **grabbing internet data in a Calc sheet**. See the following Calc files as an example:
- [LDLC MacBook Pro.ods][16]
- [LDLC Asus Zenbook.ods][17]

And finally, it allows you to **drive Firefox using a Calc file** (or any other browser supported by [Selenium][18]). See the following files:
- [Page Jaunes (Windows).ods][19]
- [Page Jaunes (Linux).ods][20]

Being free software I encourage you:
- To duplicate its [source code][21].
- To make changes, corrections, improvements.
- To open [issue][22] if needed.

In short, to participate in the development of this extension.
Because it is together that we can make Free Software smarter.

___

## Requirement:

The minimum version of LibreOffice supported by the OAuth2OOo extension depends on how you installed LibreOffice on your computer:

- **Regardless of platform**, if you installed LibreOffice from the [LibreOffice download site][23], **the minimum version of LibreOffice is 7.0**.

- **On Linux**, if you used the package manager to install LibreOffice, **the minimum version of LibreOffice is 6.0**. However, you must ensure that the system-provided Python version is not lower than 3.8.  
In addition, your system-provided Python packages can be out of date. The extension's logging will allow you to check if this is the case. It is accessible via the menu: **Tools -> Options -> Internet -> OAuth2 protocol -> View log -> System Info** and requires restarting LibreOffice after activation.  
If outdated packages appear, you can update them with this procedure:  
    - Download the file [requirements.txt][24].
    - Install using [pip][25], the Python packages necessary for the extension with the command:  
    `pip install requirements.txt`

If you want to **drive Firefox in Calc on Ubuntu** then you need to reinstall Firefox from the Mozilla PPA.  
To install the Mozilla PPA please type the command:  
`sudo add-apt-repository ppa:mozillateam/ppa`

___

## Installation:

It seems important that the file was not renamed when it was downloaded.  
If necessary, rename it before installing it.

- ![OAuth2OOo logo][26] Install **[OAuth2OOo.oxt][27]** extension [![Version][28]][27]

Restart LibreOffice after installation.  
**Be careful, restarting LibreOffice may not be enough.**
- **On Windows** to ensure that LibreOffice restarts correctly, use Windows Task Manager to verify that no LibreOffice services are visible after LibreOffice shuts down (and kill it if so).
- **Under Linux or macOS** you can also ensure that LibreOffice restarts correctly, by launching it from a terminal with the command `soffice` and using the key combination `Ctrl + C` if after stopping LibreOffice, the terminal is not active (no command prompt).

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

![OAuth2OOo Wizard Page1 screenshot][29]

![OAuth2OOo Wizard Page2 screenshot][30]

![OAuth2OOo Wizard Page3 screenshot][31]

![OAuth2OOo Browser Page1 screenshot][32]

![OAuth2OOo Browser Page2 screenshot][33]

![OAuth2OOo Browser Page3 screenshot][34]

![OAuth2OOo Browser Page4 screenshot][35]

![OAuth2OOo Wizard Page4 screenshot][36]

The OAuth2 protocol allows access to server resources, after accepting the connection authorization, by exchanging tokens.

The revocation takes place in the management of the applications associated with your account.

No more password is stored in LibreOffice.

___

## How to build the extension:

Normally, the extension is created with Eclipse for Java and [LOEclipse][37]. To work around Eclipse, I modified LOEclipse to allow the extension to be created with Apache Ant.  
To create the jdbcDriverOOo extension with the help of Apache Ant, you need to:
- Install the [Java SDK][38] version 17 or higher.
- Install [Apache Ant][39] version 1.9.1 or higher.
- Install [LibreOffice and its SDK][40] version 7.x or higher.
- Clone the [OAuth2OOo][41] repository on GitHub into a folder.
- From this folder, move to the directory: `source/OAuth2OOo/`
- In this directory, edit the file: `build.properties` so that the `office.install.dir` and `sdk.dir` properties point to the folders where LibreOffice and its SDK were installed, respectively.
- Start the archive creation process using the command: `ant`
- You will find the generated archive in the subfolder: `dist/`

___

## Has been tested with:

* LibreOffice 7.3.7.2 - Lubuntu 22.04 - Python version 3.10.12

* LibreOffice 7.5.4.2(x86) - Windows 10 - Python version 3.8.16 (under Lubuntu 22.04 / VirtualBox 6.1.38)

* LibreOffice 7.4.3.2(x64) - Windows 10(x64) - Python version 3.8.15 (under Lubuntu 22.04 / VirtualBox 6.1.38)

* LibreOffice 24.8.0.3 (x86_64) - Windows 10(x64) - Python version 3.9.19 (under Lubuntu 22.04 / VirtualBox 6.1.38)

* **Does not work with OpenOffice** see [bug 128569][37]. Having no solution, I encourage you to install **LibreOffice**.

I encourage you in case of problem :confused:  
to create an [issue][22]  
I will try to solve it :smile:

___

## Historical:

### What has been done for version 0.0.5:

- Writing of a new [XWizard][38] interface in order to replace the Wizard service which became defective with version 6.4.x and 7.x of LibreOffice (see [bug 132110][39]).

    This new interface also fixes [bug 132661][40] and [bug 132666][41] and allows access to versions 6.4.x and 7.x of LibreOffice...

    In addition this new XWizard adds new functionality such as:

    - Automatic resizing of the Wizard to the dimensions of the first displayed page.
    - Automatic move to page X on opening if possible.

- Fixed an issue with tokens without expiration (as used by Dropbox) on testing their validity...

- Many other fix...

### What has been done for version 0.0.6:

- Rewrite of the OAuth2 wizard trying to follow the [MVA model][42] as best as possible. This wizard is made up of 5 pages inheriting from the UNO [XWizardPage][43] interface:

    - Page 1: [Adapter][44] and [View][45]
    - Page 2: [Adapter][46] and [View][47]
    - Page 3: [Adapter][48] and [View][49]
    - Page 4: [Adapter][50] and [View][51]
    - Page 5: [Adapter][52] and [View][53]

- Rewrite of the three UNO services provided by the OAuth2OOo extension in three separate files:

    - The [OAuth2Service][54] service implementing the interface described in the [XOAuth2Service][55] IDL file.
    - The [OAuth2Dispacher][56] service implementing the UNO interface [XDispatchProvider][57].
    - The [OAuth2Handler][58] service implementing the UNO interface [XInteractionHandler2][59].

- Rewrite of the options dialog accessible by **Tools -> Options -> Internet -> Protocol OAuth2**. This dialog is composed of two windows:

    - The logging window: [Adapter][60] and [View][61].
    - The OAuth2OOo extension configuration options window: [Adapter][62] and [View][63].

- Rewrite a single data model: [OAuth2Model][64] managing wizard, services and options dialog.

- Google loopback flow error has been fixed. See [Issue #10][65]

- Use for Dropbox their new OAuth2 API with expirable tokens.

- Many other fix...

### What has been done for version 1.0.0:

- Porting Python API [Requests][66] to LibreOffice / OpenOffice UNO API. Two UNO interfaces are accessible:

    - HTTP request parameters: [com.sun.star.rest.XRequestParameter.idl][67]
    - The response to the HTTP request: [com.sun.star.rest.XRequestResponse.idl][68]  

    The XRequestParameter interface supports sync token handling as well as HTTP request paging, as used in the HTTP Rest APIs

- Uploading and downloading files is possible thanks to the methods or properties:

    - `XOAuth2Service.download()` allowing resumable file download.
    - `XOAuth2Service.upload()` allowing resumable file upload.
    - `XOAuth2Service.getInputStream()` to get an input stream.
    - `XRequestParameter.DataSink` to set an input stream.
    - `XRequestResponse.getInputStream()` to get an input stream.

- Porting Java API [javax.json][69] to LibreOffice / OpenOffice UNO API as defined in idl files: [com.sun.star.json.*][70]

    - A factory of JSON structures is accessible via the `getJsonBuilder()` interface of [XRequestParameter][67].
    - A Json parser is returned by the `getJson()` interface of [XRequestResponse][68].

**This makes HTTP requests using JSON easily usable in the BASIC language of LibreOffice.**

### What has been done for version 1.0.1:

- Writing of 15 functions in Calc AddIns as described in the following files:

    - The file [OAuth2Plugin.idl][71] which declares new interfaces to UNO.
    - The file [CalcAddIns.xcu][72] which makes available these new interfaces in the list of Calc functions.
    - The file [OAuth2Plugin.py][73] which is the implementation of the UNO service `com.sun.star.auth.Oauth2Plugin` providing these new interfaces.
    - The file [plugin.py][74] which is the library implementing the interfaces of this new UNO service.

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

### What has been done for version 1.1.0:

- **End of support for Python 2.x and therefore for OpenOffice**.

- Integration of [Selenium][18] version 4.10 in the extension in order to make **LibreOffice able to control a browser via Calc formulas** inserted in a spreadsheet.

- Use of [webdriver_manager][75] version 3.8.6 to automate the installation of the browser's [WebDriver][76].

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

- Fixed an issue in [the implementation][77] of the [com.sun.star.rest.XRequestParameter][67] interface not allowing to create empty JSON objects (ie: "Object": {} ) as requested by the Microsoft Graph API.

### What has been done for version 1.1.2:

- Modification of the idl files: [XRequestParameter.idl][67] and [XRequestResponse.idl][68] and the underlying python implementations: [requestparameter.py][77] and [requestresponse.py][78] in order to make it possible **POST** requests with **application/x-www-form-urlencoded** encoding. See [issue #13][79].

- 3 macros in BASIC: `ChatGPTRequest`, `HTTPGetRequest` and `HTTPPostRequest` are available in: **Tools -> Macros -> Run Macros... -> My Macros -> OAuth2OOo**. Be careful, these macros **will not work if no document is open** (I don't know why?)...

- From now on, with each push, a [workflow perform a scan][80] on the code with [Fluid Attacks][81]. This has been implemented to follow the [Cloud Application Security Assessment][82] (CASA) and meet the requirements for revalidation of the OAuth2OOo extension with Google.

- For the same reasons, the [Data Protection Policy][5] has been modified in order to specify the [Nature and scope rights over your data][83].

### What has been done for version 1.2.0:

- There are now two methods of creating the [OAuth2Service][84] service which are:
    - `create()` without parameter, returns an instance of the service.
    - `createWithOAuth2([in] string sUrl, [in] string sUser)` with an Url and the user's address, returns an instance of the service with the OAuth2 protocol.  
    In its second form, the OAuth2 authorization Wizard will launch automatically if the scope of the Url rights has not yet been granted by the user (ie: first connection).  
    If this is the case and the Wizard is aborted then a null value will be returned instead of the requested service.

- Two BASIC macros: `GoogleAPIRequest` and `GraphAPIRequest` allow you to make HTTP requests on the Google Contact and Microsoft Graph APIs.  
    The OAuth2 protocol essential for the use of these APIs is integrated automatically and transparently into HTTP requests. You won't have to worry about it.

### What has been done for version 1.2.1:

- Added a new method `isAuthorized()` to the [XOAuth2Service][55] interface supported by the [OAuth2Service][84] service. This method allows you to launch the OAuth2 configuration Wizard if the user is not authorized.

### What has been done for version 1.2.2:

- Fixed an error when refreshing OAuth2 tokens.

### What has been done for version 1.2.3:

- Fixed an error on isAuthorized() on OAuth2Service.

### What has been done for version 1.2.4:

- Updated embedded python packages.

### What has been done for version 1.3.0:

- Using the new version 3.6.2 of [pyRdfa3][85].
- All Python packages necessary for the extension are now recorded in a [requirements.txt][23] file following [PEP 508][86].
- Now if you are not on Windows then the Python packages necessary for the extension can be easily installed with the command:  
  `sudo -i pip3 install requirements.txt`
- Simplification of the [Requirement][87] section.
- Many fixes...

### What has been done for version 1.3.1:

- Fixed the `Headers` property in the [implementation][78] of the UNO interface [XRequestResponse][68] allowing to obtain the headers of an HTTP response.
- Many fixes...

### What has been done for version 1.3.2:

- Integration of Python 3.8 binaries for Linux x86_64 and Darwin x86_64, in order to be compatible with the version of LibreOffice 24.2.x for Linux, for the `lxml`, `ijson`, `cffi` and `charset-normalizer` packages.
- Opening of issue [#159988][88] for the impossibility of importing Python libraries containing binary files with LibreOffice 24.2.x under Linux.

### What has been done for version 1.3.3:

- Implemented a workaround for issue [#159988][88] which may take time to resolve.

### What has been done for version 1.3.4:

- Updated the [Python Idna][89] package to version 3.7 in order to respond to the [security vulnerability alert][90].
- Some fixes...

### What has been done for version 1.3.5:

- Updated the [Python tqdm][91] package to version 4.66.4 in order to respond to the [security vulnerability alert][92].
- Updated the [Python Requests][93] package to version 2.32.3 in order to respond to the [security vulnerability alert][94].
- In order to avoid any conflict with the [Python oauth2][95] package, the folder put in the python path by the extension has been renamed to `oauth20`. This should also resolve [issue #15][96].
- Some fixes...

### What has been done for version 1.3.6:

- Updated the [Python beautifulsoup][97] package to version 4.12.3.
- Updated the [Python certifi][98] package to version 2024.7.4.
- Added binaries for Python/Manylinux versions 3.9, 3.11 and 3.12 for package [Python cffi][99] version 1.16.0.
- Updated the [Python charset-normalizer][100] package to version 3.3.2.
- Updated the [Python exceptiongroup][101] package to version 1.2.2.
- Updated the [Python extruct][102] package to version 0.17.0.
- Updated the [Python html-text][103] package to version 0.6.2.
- Updated the [Python ijson][104] package to version 3.3.0.
- Updated the [Python jsonpath_ng][105] package to version 1.6.1.
- Updated the [Python lxml][106] package to version 5.2.2.
- Added package [Python lxml-html-clean][107] version 0.2.0.
- Updated the [Python packaging][108] package to version 24.1.
- Updated the [Python prasel][109] package to version 1.9.1.
- Updated the [Python pycparser][110] package to version 2.22.
- Updated the [Python pyparsing][111] package to version 3.1.2.
- Updated the [Python pyRdfa3][112] package to version 3.6.4.
- Updated the [Python python-dotenv][113] package to version 1.0.1.
- Updated the [Python selenium][114] package to version 4.23.1.
- Updated the [Python setuptools][115] package to version 72.1.0 in order to respond to the [security vulnerability alert][116].
- Updated the [Python sniffio][117] package to version 1.3.1.
- Updated the [Python trio][118] package to version 0.26.0.
- Added package [Python typing-extensions][119] version 4.12.2.
- Updated the [Python urllib3][120] package to version 2.2.2.
- Updated the [Python validators][121] package to version 0.33.2.
- Updated the [Python w3lib][122] package to version 2.2.1.
- Updated the [Python webdriver-manager][123] package to version 4.0.2.
- Added package [Python websocket-client][124] version 1.8.0.

Updating all these Python packages should make it possible to use Python 3.8, 3.9, 3.10, 3.11 and 3.12 under ManyLinux x86_64 architecture.  
For win32 and win_amd64 architectures, only Python version 3.8 is supported. This means that since Python is embedded into LibreOffice for these architectures, only LibreOffice versions 7.x and 24.x are supported.  
If your architecture is not yet supported by OAuth2OOo (Mac OSX, arm...), I advise you to open an [issue][22] so that I can add the missing binaries.

### What has been done for version 1.3.7:

- Updated the [Python attrs][125] package to version 24.2.0.
- Updated the [Python cffi][99] package to version 1.17.0.
- Updated the [Python idna][89] package to version 3.8.
- Updated the [Python lxml][106] package to version 5.3.0.
- Updated the [Python pyparsing][111] package to version 3.1.4.
- Updated the [Python setuptools][115] package to version 73.0.1.
- Updated the [Python soupsieve][126] package to version 2.6.
- Updated the [Python tqdm][91] package to version 4.66.5.
- Updated the [Python trio][118] package to version 0.26.2.
- Logging accessible in extension options now displays correctly on Windows.
- Changes to extension options that require a restart of LibreOffice will result in a message being displayed.
- To work with LibreOffice 24.8.x and Windows (32 and 64 bit), added binaries, for Python version 3.9 and win32 or win_adm64 architectures, to all Python packages included in the extension.

### What has been done for version 1.3.8:

- Modification of the extension options accessible via: **Tools -> Options... -> Internet -> OAuth2 Protocol** in order to comply with the new graphic charter.

### What has been done for version 1.3.9:

- Added a new `fromJson()` method to the [XRequestParameter][67] interface to make it easier to execute an HTTP request from parameters coming from LibreOffice configuration files (ie: xcu/xcs XML files).
- Preparation for the migration of the scopes of rights specific to connections to Google servers.
- Some fixes...

### What has been done for version 1.4.0:

- All data needed for OAuth2 authorization code flow management is now stored in LibreOffice configuration file [Options.xcu][127].
- It is now possible to have an OAuth2 redirect uri (ie: `redirect_uri`) in https mode as required by some third party APIs, using Github's SSL certificate and JavaScript, see the file [OAuth2Redirect.md][128].
- The TCP/IP port allowing the reception of the GAFA authorization code is now chosen randomly among the free ports (ie: no more conflict problems).
- It is possible to build the extension archive (ie: the oxt file) with the [Apache Ant][129] utility and the [build.xml][130] script file.
- The extension will refuse to install under OpenOffice regardless of version or LibreOffice other than 7.x or higher.
- OAuth2 data flow management using authorization code copy has been removed. Only receiving the authorization code via HTTP is now supported.
- Two methods have been added to the [XOAuth2Service.idl interface][55]:
  - `isRegisteredUrl` to know if a URL is registered in the OAuth2 configuration.
  - `getTokenWithParameters` to obtain an OAuth2 token in the format given by the parameters.
- Added binaries needed for Python libraries to work on Linux and LibreOffice 24.8 (ie: Python 3.9).
- Many fixes...

### What has been done for version 1.4.1:

- Updated the [Python attrs][125] package to version 25.1.0.
- Updated the [Python beautifulsoup4][97] package to version 4.13.3.
- Updated the [Python certifi][98] package to version 2025.1.31.
- Updated the [Python cffi][99] package to version 1.17.1.
- Updated the [Python charset-normalizer][100] package to version 3.4.1.
- Updated the [Python extruct][102] package to version 0.18.0.
- Updated the [Python html-text][103] package to version 0.7.0.
- Updated the [Python idna][89] package to version 3.10.
- Updated the [Python isodate][131] package to version 0.7.2.
- Updated the [Python jsonpath_ng][105] package to version 1.7.0.
- Updated the [Python lxml][106] package to version 5.3.1.
- Updated the [Python packaging][108] package to version 24.2.
- Updated the [Python parsel][109] package to version 1.10.0.
- Updated the [Python pyparsing][111] package to version 3.2.1.
- Updated the [Python rdflib][132] package to version 7.1.3.
- Updated the [Python selenium][114] package to version 4.28.1.
- Updated the [Python setuptools][115] package to version 75.8.0.
- Updated the [Python six][133] package to version 1.17.0.
- Updated the [Python tqdm][91] package to version 4.67.1.
- Updated the [Python trio][118] package to version 0.29.0.
- Updated the [Python urllib3][120] package to version 2.3.0.
- Updated the [Python validators][121] package to version 0.34.0.
- Updated the [Python w3lib][122] package to version 2.3.1.
- Support for Python version 3.13.

### What has been done for version 1.5.0:

- Updated the [Python packaging][108] package to version 25.0.
- Downgrade the [Python setuptools][115] package to version 75.3.2. to ensure support for Python 3.8.
- Updated the [Python h11][134] package to version 0.16.0 to address the [Dependabot #16][135] security alert.

### What remains to be done for version 1.5.0:

- Add new language for internationalization...

- Anything welcome...

[1]: </img/oauth2.svg#collapse>
[2]: <https://prrvchr.github.io/OAuth2OOo/>
[3]: <https://prrvchr.github.io/OAuth2OOo/README_fr>
[4]: <https://prrvchr.github.io/OAuth2OOo/source/OAuth2OOo/registration/TermsOfUse_en>
[5]: <https://prrvchr.github.io/OAuth2OOo/source/OAuth2OOo/registration/PrivacyPolicy_en>
[6]: <https://prrvchr.github.io/OAuth2OOo/#what-has-been-done-for-version-141>
[7]: <https://prrvchr.github.io>
[8]: <https://www.libreoffice.org/download/download/>
[9]: <https://www.openoffice.org/download/index.html>
[10]: <https://en.wikipedia.org/wiki/OAuth>
[11]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/OAuth2OOo/HTTPGetRequest.xba>
[12]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/OAuth2OOo/HTTPPostRequest.xba>
[13]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/OAuth2OOo/ChatGPTRequest.xba>
[14]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/OAuth2OOo/GoogleAPIRequest.xba>
[15]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/OAuth2OOo/GraphAPIRequest.xba>
[16]: <https://github.com/prrvchr/OAuth2OOo/releases/latest/download/LDLC-MacBook-Pro.ods>
[17]: <https://github.com/prrvchr/OAuth2OOo/releases/latest/download/LDLC-Asus-Zenbook.ods>
[18]: <https://pypi.org/project/selenium/4.16.0/>
[19]: <https://github.com/prrvchr/OAuth2OOo/releases/latest/download/Page-Jaunes-Windows.ods>
[20]: <https://github.com/prrvchr/OAuth2OOo/releases/latest/download/Page-Jaunes-Linux.ods>
[21]: <https://github.com/prrvchr/OAuth2OOo>
[22]: <https://github.com/prrvchr/OAuth2OOo/issues/new>
[23]: <https://github.com/prrvchr/OAuth2OOo/releases/latest/download/requirements.txt>
[24]: <https://packaging.python.org/en/latest/tutorials/installing-packages/#use-pip-for-installing>
[25]: <https://prrvchr.github.io/OAuth2OOo/#what-has-been-done-for-version-130>
[26]: <https://prrvchr.github.io/OAuth2OOo/img/OAuth2OOo.svg#middle>
[27]: <https://github.com/prrvchr/OAuth2OOo/releases/latest/download/OAuth2OOo.oxt>
[28]: <https://img.shields.io/github/downloads/prrvchr/OAuth2OOo/latest/total?label=v1.4.1#right>
[29]: <https://prrvchr.github.io/OAuth2OOo/img/OAuth2Wizard1.png>
[30]: <https://prrvchr.github.io/OAuth2OOo/img/OAuth2Wizard2.png>
[31]: <https://prrvchr.github.io/OAuth2OOo/img/OAuth2Wizard3.png>
[32]: <https://prrvchr.github.io/OAuth2OOo/img/OAuth2Wizard4.png>
[33]: <https://prrvchr.github.io/OAuth2OOo/img/OAuth2Wizard5.png>
[34]: <https://prrvchr.github.io/OAuth2OOo/img/OAuth2Wizard6.png>
[35]: <https://prrvchr.github.io/OAuth2OOo/img/OAuth2Wizard7.png>
[36]: <https://prrvchr.github.io/OAuth2OOo/img/OAuth2Wizard8.png>
[37]: <https://bz.apache.org/ooo/show_bug.cgi?id=128569>
[38]: <https://github.com/prrvchr/OAuth2OOo/blob/master/uno/lib/uno/wizard/wizard.py>
[39]: <https://bugs.documentfoundation.org/show_bug.cgi?id=132110>
[40]: <https://bugs.documentfoundation.org/show_bug.cgi?id=132661>
[41]: <https://bugs.documentfoundation.org/show_bug.cgi?id=132666>
[42]: <https://en.wikipedia.org/wiki/Model%E2%80%93view%E2%80%93adapter>
[43]: <https://www.openoffice.org/api/docs/common/ref/com/sun/star/ui/dialogs/XWizardPage.html>
[44]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/service/pythonpath/oauth2/window/page1/oauth2manager.py>
[45]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/service/pythonpath/oauth2/window/page1/oauth2view.py>
[46]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/service/pythonpath/oauth2/window/page2/oauth2manager.py>
[47]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/service/pythonpath/oauth2/window/page2/oauth2view.py>
[48]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/service/pythonpath/oauth2/window/page3/oauth2manager.py>
[49]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/service/pythonpath/oauth2/window/page3/oauth2view.py>
[50]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/service/pythonpath/oauth2/window/page4/oauth2manager.py>
[51]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/service/pythonpath/oauth2/window/page4/oauth2view.py>
[52]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/service/pythonpath/oauth2/window/page5/oauth2manager.py>
[53]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/service/pythonpath/oauth2/window/page5/oauth2view.py>
[54]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/service/OAuth2Service.py>
[55]: <https://github.com/prrvchr/OAuth2OOo/blob/master/uno/rdb/idl/com/sun/star/auth/XOAuth2Service.idl>
[56]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/service/OAuth2Dispatcher.py>
[57]: <https://www.openoffice.org/api/docs/common/ref/com/sun/star/frame/XDispatchProvider.html>
[58]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/service/OAuth2Handler.py>
[59]: <https://www.openoffice.org/api/docs/common/ref/com/sun/star/task/XInteractionHandler2.html>
[60]: <https://github.com/prrvchr/OAuth2OOo/blob/master/uno/lib/uno/logger/logmanager.py>
[61]: <https://github.com/prrvchr/OAuth2OOo/blob/master/uno/lib/uno/logger/logview.py>
[62]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/service/pythonpath/oauth2/options/optionsmanager.py>
[63]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/service/pythonpath/oauth2/options/optionsview.py>
[64]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/service/pythonpath/oauth2/oauth2model.py>
[65]: <https://github.com/prrvchr/OAuth2OOo/issues/10>
[66]: <https://pypi.org/project/requests/2.31.0/>
[67]: <https://github.com/prrvchr/OAuth2OOo/blob/master/uno/rdb/idl/com/sun/star/rest/XRequestParameter.idl>
[68]: <https://github.com/prrvchr/OAuth2OOo/blob/master/uno/rdb/idl/com/sun/star/rest/XRequestResponse.idl>
[69]: <https://javadoc.io/static/javax.json/javax.json-api/1.1.4/index.html?overview-summary.html>
[70]: <https://github.com/prrvchr/OAuth2OOo/tree/master/uno/rdb/idl/com/sun/star/json>
[71]: <https://github.com/prrvchr/OAuth2OOo/tree/master/uno/rdb/idl/com/sun/star/auth/XOAuth2Plugin.idl>
[72]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/CalcAddIns.xcu>
[73]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/service/OAuth2Plugin.py>
[74]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/service/pythonpath/oauth2/plugin.py>
[75]: <https://pypi.org/project/webdriver-manager/3.8.6/>
[76]: <https://developer.mozilla.org/en-US/docs/Web/WebDriver>
[77]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/service/pythonpath/oauth2/requestparameter.py>
[78]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/service/pythonpath/oauth2/requestresponse.py>
[79]: <https://github.com/prrvchr/OAuth2OOo/issues/13>
[80]: <https://github.com/prrvchr/OAuth2OOo/actions/workflows/dev.yml>
[81]: <https://github.com/fluidattacks>
[82]: <https://appdefensealliance.dev/casa/tier-2/tier2-overview>
[83]: <https://prrvchr.github.io/OAuth2OOo/source/OAuth2OOo/registration/PrivacyPolicy_en#nature-and-scope-rights-over-your-data>
[84]: <https://github.com/prrvchr/OAuth2OOo/blob/master/uno/rdb/idl/com/sun/star/auth/OAuth2Service.idl>
[85]: <https://github.com/prrvchr/pyrdfa3>
[86]: <https://peps.python.org/pep-0508/>
[87]: <https://prrvchr.github.io/OAuth2OOo/#requirement>
[88]: <https://bugs.documentfoundation.org/show_bug.cgi?id=159988>
[89]: <https://pypi.org/project/idna/>
[90]: <https://github.com/prrvchr/OAuth2OOo/security/dependabot/5>
[91]: <https://pypi.org/project/tqdm/4.66.4/>
[92]: <https://github.com/prrvchr/OAuth2OOo/security/dependabot/8>
[93]: <https://pypi.org/project/requests/2.32.3/>
[94]: <https://github.com/prrvchr/OAuth2OOo/security/dependabot/10>
[95]: <https://pypi.org/project/oauth2/1.9.0.post1/>
[96]: <https://github.com/prrvchr/OAuth2OOo/issues/15>
[97]: <https://pypi.org/project/beautifulsoup4/>
[98]: <https://pypi.org/project/certifi/>
[99]: <https://pypi.org/project/cffi/>
[100]: <https://pypi.org/project/charset-normalizer/>
[101]: <https://pypi.org/project/exceptiongroup/>
[102]: <https://pypi.org/project/extruct/>
[103]: <https://pypi.org/project/html-text/>
[104]: <https://pypi.org/project/ijson/>
[105]: <https://pypi.org/project/jsonpath-ng/>
[106]: <https://pypi.org/project/lxml/>
[107]: <https://pypi.org/project/lxml-html-clean/>
[108]: <https://pypi.org/project/packaging/>
[109]: <https://pypi.org/project/parsel/>
[110]: <https://pypi.org/project/pycparser/>
[111]: <https://pypi.org/project/pyparsing/>
[112]: <https://pypi.org/project/pyRdfa3/>
[113]: <https://pypi.org/project/python-dotenv/>
[114]: <https://pypi.org/project/selenium/>
[115]: <https://pypi.org/project/setuptools/>
[116]: <https://github.com/prrvchr/OAuth2OOo/security/dependabot/14>
[117]: <https://pypi.org/project/sniffio/>
[118]: <https://pypi.org/project/trio/>
[119]: <https://pypi.org/project/typing-extensions/>
[120]: <https://pypi.org/project/urllib3/>
[121]: <https://pypi.org/project/validators/>
[122]: <https://pypi.org/project/w3lib/>
[123]: <https://pypi.org/project/webdriver-manager/>
[124]: <https://pypi.org/project/websocket-client/>
[125]: <https://pypi.org/project/attrs/>
[126]: <https://pypi.org/project/soupsieve/>
[127]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/Options.xcu>
[128]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/registration/OAuth2Redirect.md>
[129]: <https://ant.apache.org/>
[130]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/build.xml>
[131]: <https://pypi.org/project/isodate/>
[132]: <https://pypi.org/project/rdflib/>
[133]: <https://pypi.org/project/six/>
[134]: <https://pypi.org/project/h11/>
[135]: <https://github.com/prrvchr/OAuth2OOo/security/dependabot/16>
