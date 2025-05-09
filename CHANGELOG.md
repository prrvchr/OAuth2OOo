<!--
╔════════════════════════════════════════════════════════════════════════════════════╗
║                                                                                    ║
║   Copyright (c) 2020-25 https://prrvchr.github.io                                  ║
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
# [![OAuth2OOo logo][1]][2] Historical

**Ce [document][3] en français.**

Regarding installation, configuration and use, please consult the **[documentation][4]**.

### What has been done for version 0.0.5:

- Writing of a new [XWizard][5] interface in order to replace the Wizard service which became defective with version 6.4.x and 7.x of LibreOffice (see [bug 132110][6]).

    This new interface also fixes [bug 132661][7] and [bug 132666][8] and allows access to versions 6.4.x and 7.x of LibreOffice...

    In addition this new XWizard adds new functionality such as:

    - Automatic resizing of the Wizard to the dimensions of the first displayed page.
    - Automatic move to page X on opening if possible.

- Fixed an issue with tokens without expiration (as used by Dropbox) on testing their validity...

- Many other fix...

### What has been done for version 0.0.6:

- Rewrite of the OAuth2 wizard trying to follow the [MVA model][9] as best as possible. This wizard is made up of 5 pages inheriting from the UNO [XWizardPage][10] interface:

    - Page 1: [Adapter][11] and [View][12]
    - Page 2: [Adapter][13] and [View][14]
    - Page 3: [Adapter][15] and [View][16]
    - Page 4: [Adapter][17] and [View][18]
    - Page 5: [Adapter][19] and [View][20]

- Rewrite of the three UNO services provided by the OAuth2OOo extension in three separate files:

    - The [OAuth2Service][21] service implementing the interface described in the [XOAuth2Service][22] IDL file.
    - The [OAuth2Dispacher][23] service implementing the UNO interface [XDispatchProvider][24].
    - The [OAuth2Handler][25] service implementing the UNO interface [XInteractionHandler2][26].

- Rewrite of the options dialog accessible by **Tools -> Options -> Internet -> Protocol OAuth2**. This dialog is composed of two windows:

    - The logging window: [Adapter][27] and [View][28].
    - The OAuth2OOo extension configuration options window: [Adapter][29] and [View][30].

- Rewrite a single data model: [OAuth2Model][31] managing wizard, services and options dialog.

- Google loopback flow error has been fixed. See [Issue #10][32]

- Use for Dropbox their new OAuth2 API with expirable tokens.

- Many other fix...

### What has been done for version 1.0.0:

- Porting Python API [Requests][33] to LibreOffice / OpenOffice UNO API. Two UNO interfaces are accessible:

    - HTTP request parameters: [com.sun.star.rest.XRequestParameter.idl][34]
    - The response to the HTTP request: [com.sun.star.rest.XRequestResponse.idl][35]  

    The XRequestParameter interface supports sync token handling as well as HTTP request paging, as used in the HTTP Rest APIs

- Uploading and downloading files is possible thanks to the methods or properties:

    - `XOAuth2Service.download()` allowing resumable file download.
    - `XOAuth2Service.upload()` allowing resumable file upload.
    - `XOAuth2Service.getInputStream()` to get an input stream.
    - `XRequestParameter.DataSink` to set an input stream.
    - `XRequestResponse.getInputStream()` to get an input stream.

- Porting Java API [javax.json][36] to LibreOffice / OpenOffice UNO API as defined in idl files: [com.sun.star.json.*][37]

    - A factory of JSON structures is accessible via the `getJsonBuilder()` interface of [XRequestParameter][34].
    - A Json parser is returned by the `getJson()` interface of [XRequestResponse][35].

**This makes HTTP requests using JSON easily usable in the BASIC language of LibreOffice.**

### What has been done for version 1.0.1:

- Writing of 15 functions in Calc AddIns as described in the following files:

    - The file [OAuth2Plugin.idl][38] which declares new interfaces to UNO.
    - The file [CalcAddIns.xcu][39] which makes available these new interfaces in the list of Calc functions.
    - The file [OAuth2Plugin.py][40] which is the implementation of the UNO service `com.sun.star.auth.Oauth2Plugin` providing these new interfaces.
    - The file [plugin.py][41] which is the library implementing the interfaces of this new UNO service.

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

- Integration of [Selenium][42] version 4.10 in the extension in order to make **LibreOffice able to control a browser via Calc formulas** inserted in a spreadsheet.

- Use of [webdriver_manager][43] version 3.8.6 to automate the installation of the browser's [WebDriver][44].

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

- Fixed an issue in [the implementation][45] of the [com.sun.star.rest.XRequestParameter][34] interface not allowing to create empty JSON objects (ie: "Object": {} ) as requested by the Microsoft Graph API.

### What has been done for version 1.1.2:

- Modification of the idl files: [XRequestParameter.idl][34] and [XRequestResponse.idl][35] and the underlying python implementations: [requestparameter.py][77] and [requestresponse.py][78] in order to make it possible **POST** requests with **application/x-www-form-urlencoded** encoding. See [issue #13][79].

- 3 macros in BASIC: `ChatGPTRequest`, `HTTPGetRequest` and `HTTPPostRequest` are available in: **Tools -> Macros -> Run Macros... -> My Macros -> OAuth2OOo**. Be careful, these macros **will not work if no document is open** (I don't know why?)...

- From now on, with each push, a [workflow perform a scan][48] on the code with [Fluid Attacks][49]. This has been implemented to follow the [Cloud Application Security Assessment][50] (CASA) and meet the requirements for revalidation of the OAuth2OOo extension with Google.

- For the same reasons, the [Data Protection Policy][51] has been modified in order to specify the [Nature and scope rights over your data][52].

### What has been done for version 1.2.0:

- There are now two methods of creating the [OAuth2Service][53] service which are:
    - `create()` without parameter, returns an instance of the service.
    - `createWithOAuth2([in] string sUrl, [in] string sUser)` with an Url and the user's address, returns an instance of the service with the OAuth2 protocol.  
    In its second form, the OAuth2 authorization Wizard will launch automatically if the scope of the Url rights has not yet been granted by the user (ie: first connection).  
    If this is the case and the Wizard is aborted then a null value will be returned instead of the requested service.

- Two BASIC macros: `GoogleAPIRequest` and `GraphAPIRequest` allow you to make HTTP requests on the Google Contact and Microsoft Graph APIs.  
    The OAuth2 protocol essential for the use of these APIs is integrated automatically and transparently into HTTP requests. You won't have to worry about it.

### What has been done for version 1.2.1:

- Added a new method `isAuthorized()` to the [XOAuth2Service][22] interface supported by the [OAuth2Service][53] service. This method allows you to launch the OAuth2 configuration Wizard if the user is not authorized.

### What has been done for version 1.2.2:

- Fixed an error when refreshing OAuth2 tokens.

### What has been done for version 1.2.3:

- Fixed an error on isAuthorized() on OAuth2Service.

### What has been done for version 1.2.4:

- Updated embedded python packages.

### What has been done for version 1.3.0:

- Using the new version 3.6.2 of [pyRdfa3][54].
- All Python packages necessary for the extension are now recorded in a [requirements.txt][55] file following [PEP 508][56].
- Now if you are not on Windows then the Python packages necessary for the extension can be easily installed with the command:  
  `sudo -i pip3 install requirements.txt`
- Simplification of the [Requirement][57] section.
- Many fixes...

### What has been done for version 1.3.1:

- Fixed the `Headers` property in the [implementation][46] of the UNO interface [XRequestResponse][35] allowing to obtain the headers of an HTTP response.
- Many fixes...

### What has been done for version 1.3.2:

- Integration of Python 3.8 binaries for Linux x86_64 and Darwin x86_64, in order to be compatible with the version of LibreOffice 24.2.x for Linux, for the `lxml`, `ijson`, `cffi` and `charset-normalizer` packages.
- Opening of issue [#159988][58] for the impossibility of importing Python libraries containing binary files with LibreOffice 24.2.x under Linux.

### What has been done for version 1.3.3:

- Implemented a workaround for issue [#159988][58] which may take time to resolve.

### What has been done for version 1.3.4:

- Updated the [Python Idna][59] package to version 3.7 in order to respond to the [security vulnerability alert][60].
- Some fixes...

### What has been done for version 1.3.5:

- Updated the [Python tqdm][61] package to version 4.66.4 in order to respond to the [security vulnerability alert][62].
- Updated the [Python Requests][63] package to version 2.32.3 in order to respond to the [security vulnerability alert][64].
- In order to avoid any conflict with the [Python oauth2][65] package, the folder put in the python path by the extension has been renamed to `oauth20`. This should also resolve [issue #15][66].
- Some fixes...

### What has been done for version 1.3.6:

- Updated the [Python beautifulsoup][67] package to version 4.12.3.
- Updated the [Python certifi][68] package to version 2024.7.4.
- Added binaries for Python/Manylinux versions 3.9, 3.11 and 3.12 for package [Python cffi][69] version 1.16.0.
- Updated the [Python charset-normalizer][70] package to version 3.3.2.
- Updated the [Python exceptiongroup][71] package to version 1.2.2.
- Updated the [Python extruct][72] package to version 0.17.0.
- Updated the [Python html-text][73] package to version 0.6.2.
- Updated the [Python ijson][74] package to version 3.3.0.
- Updated the [Python jsonpath_ng][75] package to version 1.6.1.
- Updated the [Python lxml][76] package to version 5.2.2.
- Added package [Python lxml-html-clean][77] version 0.2.0.
- Updated the [Python packaging][78] package to version 24.1.
- Updated the [Python prasel][79] package to version 1.9.1.
- Updated the [Python pycparser][80] package to version 2.22.
- Updated the [Python pyparsing][81] package to version 3.1.2.
- Updated the [Python pyRdfa3][82] package to version 3.6.4.
- Updated the [Python python-dotenv][83] package to version 1.0.1.
- Updated the [Python selenium][84] package to version 4.23.1.
- Updated the [Python setuptools][85] package to version 72.1.0 in order to respond to the [security vulnerability alert][86].
- Updated the [Python sniffio][87] package to version 1.3.1.
- Updated the [Python trio][88] package to version 0.26.0.
- Added package [Python typing-extensions][89] version 4.12.2.
- Updated the [Python urllib3][90] package to version 2.2.2.
- Updated the [Python validators][91] package to version 0.33.2.
- Updated the [Python w3lib][92] package to version 2.2.1.
- Updated the [Python webdriver-manager][93] package to version 4.0.2.
- Added package [Python websocket-client][94] version 1.8.0.

Updating all these Python packages should make it possible to use Python 3.8, 3.9, 3.10, 3.11 and 3.12 under ManyLinux x86_64 architecture.  
For win32 and win_amd64 architectures, only Python version 3.8 is supported. This means that since Python is embedded into LibreOffice for these architectures, only LibreOffice versions 7.x and 24.x are supported.  
If your architecture is not yet supported by OAuth2OOo (Mac OSX, arm...), I advise you to open an [issue][95] so that I can add the missing binaries.

### What has been done for version 1.3.7:

- Updated the [Python attrs][96] package to version 24.2.0.
- Updated the [Python cffi][69] package to version 1.17.0.
- Updated the [Python idna][59] package to version 3.8.
- Updated the [Python lxml][76] package to version 5.3.0.
- Updated the [Python pyparsing][81] package to version 3.1.4.
- Updated the [Python setuptools][85] package to version 73.0.1.
- Updated the [Python soupsieve][97] package to version 2.6.
- Updated the [Python tqdm][61] package to version 4.66.5.
- Updated the [Python trio][88] package to version 0.26.2.
- Logging accessible in extension options now displays correctly on Windows.
- Changes to extension options that require a restart of LibreOffice will result in a message being displayed.
- To work with LibreOffice 24.8.x and Windows (32 and 64 bit), added binaries, for Python version 3.9 and win32 or win_adm64 architectures, to all Python packages included in the extension.

### What has been done for version 1.3.8:

- Modification of the extension options accessible via: **Tools -> Options... -> Internet -> OAuth2 Protocol** in order to comply with the new graphic charter.

### What has been done for version 1.3.9:

- Added a new `fromJson()` method to the [XRequestParameter][34] interface to make it easier to execute an HTTP request from parameters coming from LibreOffice configuration files (ie: xcu/xcs XML files).
- Preparation for the migration of the scopes of rights specific to connections to Google servers.
- Some fixes...

### What has been done for version 1.4.0:

- All data needed for OAuth2 authorization code flow management is now stored in LibreOffice configuration file [Options.xcu][98].
- It is now possible to have an OAuth2 redirect uri (ie: `redirect_uri`) in https mode as required by some third party APIs, using Github's SSL certificate and JavaScript, see the file [OAuth2Redirect.md][99].
- The TCP/IP port allowing the reception of the GAFA authorization code is now chosen randomly among the free ports (ie: no more conflict problems).
- It is possible to build the extension archive (ie: the oxt file) with the [Apache Ant][100] utility and the [build.xml][101] script file.
- The extension will refuse to install under OpenOffice regardless of version or LibreOffice other than 7.x or higher.
- OAuth2 data flow management using authorization code copy has been removed. Only receiving the authorization code via HTTP is now supported.
- Two methods have been added to the [XOAuth2Service.idl interface][22]:
  - `isRegisteredUrl` to know if a URL is registered in the OAuth2 configuration.
  - `getTokenWithParameters` to obtain an OAuth2 token in the format given by the parameters.
- Added binaries needed for Python libraries to work on Linux and LibreOffice 24.8 (ie: Python 3.9).
- Many fixes...

### What has been done for version 1.4.1:

- Updated the [Python attrs][96] package to version 25.1.0.
- Updated the [Python beautifulsoup4][67] package to version 4.13.3.
- Updated the [Python certifi][68] package to version 2025.1.31.
- Updated the [Python cffi][69] package to version 1.17.1.
- Updated the [Python charset-normalizer][70] package to version 3.4.1.
- Updated the [Python extruct][72] package to version 0.18.0.
- Updated the [Python html-text][73] package to version 0.7.0.
- Updated the [Python idna][59] package to version 3.10.
- Updated the [Python isodate][102] package to version 0.7.2.
- Updated the [Python jsonpath_ng][75] package to version 1.7.0.
- Updated the [Python lxml][76] package to version 5.3.1.
- Updated the [Python packaging][78] package to version 24.2.
- Updated the [Python parsel][79] package to version 1.10.0.
- Updated the [Python pyparsing][81] package to version 3.2.1.
- Updated the [Python rdflib][103] package to version 7.1.3.
- Updated the [Python selenium][84] package to version 4.28.1.
- Updated the [Python setuptools][85] package to version 75.8.0.
- Updated the [Python six][104] package to version 1.17.0.
- Updated the [Python tqdm][61] package to version 4.67.1.
- Updated the [Python trio][88] package to version 0.29.0.
- Updated the [Python urllib3][90] package to version 2.3.0.
- Updated the [Python validators][91] package to version 0.34.0.
- Updated the [Python w3lib][92] package to version 2.3.1.
- Support for Python version 3.13.

### What has been done for version 1.5.0:

- Updated the [Python packaging][78] package to version 25.0.
- Downgrade the [Python setuptools][85] package to version 75.3.2. to ensure support for Python 3.8.
- Updated the [Python h11][105] package to version 0.16.0 to address the [Dependabot #16][106] security alert.
- Passive registration deployment that allows for much faster installation of extensions and differentiation of registered UNO services from those provided by a Java or Python implementation. This passive registration is provided by the [LOEclipse][37] extension via [PR#152][107] and [PR#157][108].
- It is now possible to build the oxt file of the OAuth2OOo extension only with the help of Apache Ant and a copy of the GitHub repository. The [How to build the extension][109] section has been added to the documentation.
- Implemented [PEP 570][110] in [logging][111] to support unique multiple arguments.

### What remains to be done for version 1.5.0:

- Add new language for internationalization...

- Anything welcome...

[1]: </img/oauth2.svg#collapse>
[2]: <https://prrvchr.github.io/OAuth2OOo/>
[3]: <https://prrvchr.github.io/OAuth2OOo/CHANGELOG_fr>
[4]: <https://prrvchr.github.io/OAuth2OOo/>
[5]: <https://github.com/prrvchr/OAuth2OOo/blob/master/uno/lib/uno/wizard/wizard.py>
[6]: <https://bugs.documentfoundation.org/show_bug.cgi?id=132110>
[7]: <https://bugs.documentfoundation.org/show_bug.cgi?id=132661>
[8]: <https://bugs.documentfoundation.org/show_bug.cgi?id=132666>
[9]: <https://en.wikipedia.org/wiki/Model%E2%80%93view%E2%80%93adapter>
[10]: <https://www.openoffice.org/api/docs/common/ref/com/sun/star/ui/dialogs/XWizardPage.html>
[11]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/service/pythonpath/oauth2/window/page1/oauth2manager.py>
[12]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/service/pythonpath/oauth2/window/page1/oauth2view.py>
[13]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/service/pythonpath/oauth2/window/page2/oauth2manager.py>
[14]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/service/pythonpath/oauth2/window/page2/oauth2view.py>
[15]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/service/pythonpath/oauth2/window/page3/oauth2manager.py>
[16]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/service/pythonpath/oauth2/window/page3/oauth2view.py>
[17]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/service/pythonpath/oauth2/window/page4/oauth2manager.py>
[18]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/service/pythonpath/oauth2/window/page4/oauth2view.py>
[19]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/service/pythonpath/oauth2/window/page5/oauth2manager.py>
[20]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/service/pythonpath/oauth2/window/page5/oauth2view.py>
[21]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/service/OAuth2Service.py>
[22]: <https://github.com/prrvchr/OAuth2OOo/blob/master/uno/rdb/idl/com/sun/star/auth/XOAuth2Service.idl>
[23]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/service/OAuth2Dispatcher.py>
[24]: <https://www.openoffice.org/api/docs/common/ref/com/sun/star/frame/XDispatchProvider.html>
[25]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/service/OAuth2Handler.py>
[26]: <https://www.openoffice.org/api/docs/common/ref/com/sun/star/task/XInteractionHandler2.html>
[27]: <https://github.com/prrvchr/OAuth2OOo/blob/master/uno/lib/uno/logger/logmanager.py>
[28]: <https://github.com/prrvchr/OAuth2OOo/blob/master/uno/lib/uno/logger/logview.py>
[29]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/service/pythonpath/oauth2/options/optionsmanager.py>
[30]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/service/pythonpath/oauth2/options/optionsview.py>
[31]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/service/pythonpath/oauth2/oauth2model.py>
[32]: <https://github.com/prrvchr/OAuth2OOo/issues/10>
[33]: <https://pypi.org/project/requests/2.31.0/>
[34]: <https://github.com/prrvchr/OAuth2OOo/blob/master/uno/rdb/idl/com/sun/star/rest/XRequestParameter.idl>
[35]: <https://github.com/prrvchr/OAuth2OOo/blob/master/uno/rdb/idl/com/sun/star/rest/XRequestResponse.idl>
[36]: <https://javadoc.io/static/javax.json/javax.json-api/1.1.4/index.html?overview-summary.html>
[37]: <https://github.com/prrvchr/OAuth2OOo/tree/master/uno/rdb/idl/com/sun/star/json>
[38]: <https://github.com/prrvchr/OAuth2OOo/tree/master/uno/rdb/idl/com/sun/star/auth/XOAuth2Plugin.idl>
[39]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/CalcAddIns.xcu>
[40]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/service/OAuth2Plugin.py>
[41]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/service/pythonpath/oauth2/plugin.py>
[42]: <https://pypi.org/project/selenium/4.16.0/>
[43]: <https://pypi.org/project/webdriver-manager/3.8.6/>
[44]: <https://developer.mozilla.org/en-US/docs/Web/WebDriver>
[45]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/service/pythonpath/oauth2/requestparameter.py>
[46]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/service/pythonpath/oauth2/requestresponse.py>
[47]: <https://github.com/prrvchr/OAuth2OOo/issues/13>
[48]: <https://github.com/prrvchr/OAuth2OOo/actions/workflows/dev.yml>
[49]: <https://github.com/fluidattacks>
[50]: <https://appdefensealliance.dev/casa/tier-2/tier2-overview>
[51]: <https://prrvchr.github.io/OAuth2OOo/source/OAuth2OOo/registration/PrivacyPolicy_fr>
[52]: <https://prrvchr.github.io/OAuth2OOo/source/OAuth2OOo/registration/PrivacyPolicy_en#nature-and-scope-rights-over-your-data>
[53]: <https://github.com/prrvchr/OAuth2OOo/blob/master/uno/rdb/idl/com/sun/star/auth/OAuth2Service.idl>
[54]: <https://github.com/prrvchr/pyrdfa3>
[55]: <https://github.com/prrvchr/OAuth2OOo/releases/latest/download/requirements.txt>
[56]: <https://peps.python.org/pep-0508/>
[57]: <https://prrvchr.github.io/OAuth2OOo/#requirement>
[58]: <https://bugs.documentfoundation.org/show_bug.cgi?id=159988>
[59]: <https://pypi.org/project/idna/>
[60]: <https://github.com/prrvchr/OAuth2OOo/security/dependabot/5>
[61]: <https://pypi.org/project/tqdm/4.66.4/>
[62]: <https://github.com/prrvchr/OAuth2OOo/security/dependabot/8>
[63]: <https://pypi.org/project/requests/2.32.3/>
[64]: <https://github.com/prrvchr/OAuth2OOo/security/dependabot/10>
[65]: <https://pypi.org/project/oauth2/1.9.0.post1/>
[66]: <https://github.com/prrvchr/OAuth2OOo/issues/15>
[67]: <https://pypi.org/project/beautifulsoup4/>
[68]: <https://pypi.org/project/certifi/>
[69]: <https://pypi.org/project/cffi/>
[70]: <https://pypi.org/project/charset-normalizer/>
[71]: <https://pypi.org/project/exceptiongroup/>
[72]: <https://pypi.org/project/extruct/>
[73]: <https://pypi.org/project/html-text/>
[74]: <https://pypi.org/project/ijson/>
[75]: <https://pypi.org/project/jsonpath-ng/>
[76]: <https://pypi.org/project/lxml/>
[77]: <https://pypi.org/project/lxml-html-clean/>
[78]: <https://pypi.org/project/packaging/>
[79]: <https://pypi.org/project/parsel/>
[80]: <https://pypi.org/project/pycparser/>
[81]: <https://pypi.org/project/pyparsing/>
[82]: <https://pypi.org/project/pyRdfa3/>
[83]: <https://pypi.org/project/python-dotenv/>
[84]: <https://pypi.org/project/selenium/>
[85]: <https://pypi.org/project/setuptools/>
[86]: <https://github.com/prrvchr/OAuth2OOo/security/dependabot/14>
[87]: <https://pypi.org/project/sniffio/>
[88]: <https://pypi.org/project/trio/>
[89]: <https://pypi.org/project/typing-extensions/>
[90]: <https://pypi.org/project/urllib3/>
[91]: <https://pypi.org/project/validators/>
[92]: <https://pypi.org/project/w3lib/>
[93]: <https://pypi.org/project/webdriver-manager/>
[94]: <https://pypi.org/project/websocket-client/>
[95]: <https://github.com/prrvchr/OAuth2OOo/issues/new>
[96]: <https://pypi.org/project/attrs/>
[97]: <https://pypi.org/project/soupsieve/>
[98]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/Options.xcu>
[99]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/registration/OAuth2Redirect.md>
[100]: <https://ant.apache.org/>
[101]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/build.xml>
[102]: <https://pypi.org/project/isodate/>
[103]: <https://pypi.org/project/rdflib/>
[104]: <https://pypi.org/project/six/>
[105]: <https://pypi.org/project/h11/>
[106]: <https://github.com/prrvchr/OAuth2OOo/security/dependabot/16>
[107]: <https://github.com/LibreOffice/loeclipse/pull/152>
[108]: <https://github.com/LibreOffice/loeclipse/pull/157>
[109]: <https://prrvchr.github.io/OAuth2OOo/#how-to-build-the-extension>
[110]: <https://peps.python.org/pep-0570/>
[111]: <https://github.com/prrvchr/OAuth2OOo/blob/master/uno/lib/uno/logger/logwrapper.py#L109>
