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
# [![OAuth2OOo logo][1]][2] Documentation

**Ce [document][3] en français.**

**The use of this software subjects you to our [Terms Of Use][4] and [Data Protection Policy][5].**

# version [1.6.0][6]

## Introduction:

**OAuth2OOo** is part of a [Suite][7] of [LibreOffice][8] ~~and/or [OpenOffice][9]~~ extensions allowing to offer you innovative services in these office suites.

This extension is the implementation of the [OAuth 2.0 protocol][10]. Protocol allowing you to obtain your consent so that an application can access your data present at the GAFA.

It allows **executing HTTP requests** in [BASIC][11] and provides the following macros as an example:
- [HTTPGetRequest][12]
- [HTTPPostRequest][13]
- [ChatGPTRequest][14]
- [GoogleAPIRequest][15]
- [GraphAPIRequest][16]
- [GithubDownloadRequest][17]

If you open a document beforehand, you can launch them by:  
**Tools -> Macros -> Run Macro... -> My Macros -> OAuth2OOo -> `macro-name` -> Main -> Run**

It also allows **grabbing internet data in a Calc sheet**. See the following Calc files as an example:
- [LDLC MacBook Pro.ods][18]
- [LDLC Asus Zenbook.ods][19]

And finally, it allows you to **drive Firefox using a Calc file** (or any other browser supported by [Selenium][20]). See the following files:
- [Page Jaunes (Windows).ods][21]
- [Page Jaunes (Linux).ods][22]

Being free software I encourage you:
- To duplicate its [source code][23].
- To make changes, corrections, improvements.
- To open [issue][24] if needed.
- To [participate in the costs][25] of [CASA certification][26].

In short, to participate in the development of this extension.
Because it is together that we can make Free Software smarter.

___

## CASA certification:

In order to provide you with interoperability with **Google**, the **OAuth2OOo** extension requires [CASA certification][26].  
Until now, this certification was free and carried out by a Google partner.  
The **OAuth2OOo** application obtained its [CASA certification][27] on 11/28/2023.

**Now this certification has become paid and costs $600.**

I never anticipated such costs and I am counting on your contribution to finance this certification.

Thank you for your help. [![Sponsor][28]][25]

___

## Requirement:

The minimum version of LibreOffice supported by the OAuth2OOo extension depends on how you installed LibreOffice on your computer:

- **Regardless of platform**, if you installed LibreOffice from the [LibreOffice download site][29], **the minimum version of LibreOffice is 7.0**.

- **On Linux**, if you used the package manager to install LibreOffice, **the minimum version of LibreOffice is 6.0**. However, you must ensure that the system-provided Python version is not lower than 3.8.  
In addition, your system-provided Python packages can be out of date. The extension's logging will allow you to check if this is the case. It is accessible via the menu: **Tools -> Options -> Internet -> OAuth2 protocol -> View log -> System Info** and requires restarting LibreOffice after activation.  
If outdated packages appear, you can update them with this procedure:  
    - Download the file [requirements.txt][30].
    - Install using [pip][31], the Python packages necessary for the extension with the command:  
    `pip install requirements.txt`

If you want to **drive Firefox in Calc on Ubuntu** then you need to reinstall Firefox from the Mozilla PPA.  
To install the Mozilla PPA please type the command:  
`sudo add-apt-repository ppa:mozillateam/ppa`

___

## Installation:

It seems important that the file was not renamed when it was downloaded.  
If necessary, rename it before installing it.

- ![OAuth2OOo logo][32] Install **[OAuth2OOo.oxt][33]** extension [![Version][34]][33]

Restart LibreOffice after installation.  
**Be careful, restarting LibreOffice may not be enough.**
- **On Windows** to ensure that LibreOffice restarts correctly, use Windows Task Manager to verify that no LibreOffice services are visible after LibreOffice shuts down (and kill it if so).
- **Under Linux or macOS** you can also ensure that LibreOffice restarts correctly, by launching it from a terminal with the command `soffice` and using the key combination `Ctrl + C` if after stopping LibreOffice, the terminal is not active (no command prompt).

___

## Use:

This extension was originally designed to provide [OAuth2][10] protocol support to other LibreOffice extensions.  
It also provides an API usable in [BASIC][11] to make HTTP requests:

### Create the UNO OAuth2Service with the OAuth2 protocol support:

```
sUser = "account@gmail.com"
sUrl = "people.googleapis.com"
oRequest = createUnoServiceWithArguments("io.github.prrvchr.OAuth2OOo.OAuth2Service", Array(sUrl, sUser))
```

### Create the UNO OAuth2Service without the OAuth2 protocol support:

```
oRequest = createUnoServiceWithArguments("io.github.prrvchr.OAuth2OOo.OAuth2Service")
```

### Use the UNO OAuth2Service to perform HTTP requests:

You now have an `oRequest` object that responds to the interface defined in the [XOAuth2Service.idl][35] file.  
With this interface, two methods are required to execute an HTTP request:
- `getRequestParameter([in] string Name)`, which allows you to obtain an object responding to the [XRequestParameter.idl][36] interface. This interface allows you to configure the HTTP request before execution.
- `execute([in] com::sun::star::rest::XRequestParameter Parameter)`, which allows you to obtain an object responding to the [XRequestResponse.idl][37] interface. This allows you to achieve almost anything possible with an HTTP response.

To go further, I advise you to take a look at the macros that are delivered with the extension and which implement all types of HTTP requests.

___

## Uno OAuth2.0 API for LibreOffice.

![OAuth2OOo Wizard Page1 screenshot][38]

![OAuth2OOo Wizard Page2 screenshot][39]

![OAuth2OOo Wizard Page3 screenshot][40]

![OAuth2OOo Browser Page1 screenshot][41]

![OAuth2OOo Browser Page2 screenshot][42]

![OAuth2OOo Browser Page3 screenshot][43]

![OAuth2OOo Browser Page4 screenshot][44]

![OAuth2OOo Wizard Page4 screenshot][45]

The OAuth2 protocol allows access to server resources, after accepting the connection authorization, by exchanging tokens.

The revocation takes place in the management of the applications associated with your account.

No more password is stored in LibreOffice.

___

## How to build the extension:

Normally, the extension is created with Eclipse for Java and [LOEclipse][46]. To work around Eclipse, I modified LOEclipse to allow the extension to be created with Apache Ant.  
To create the OAuth2OOo extension with the help of Apache Ant, you need to:
- Install the [Java SDK][47] version 17 or higher.
- Install [Apache Ant][48] version 1.10.0 or higher.
- Install [LibreOffice and its SDK][49] version 7.x or higher.
- Clone the [OAuth2OOo][50] repository on GitHub into a folder.
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

* **Does not work with OpenOffice** see [bug 128569][51]. Having no solution, I encourage you to install **LibreOffice**.

I encourage you in case of problem :confused:  
to create an [issue][24]  
I will try to solve it :smile:

___

## Historical:

### [All changes are logged in the version History][52]

[1]: </img/oauth2.svg#collapse>
[2]: <https://prrvchr.github.io/OAuth2OOo/>
[3]: <https://prrvchr.github.io/OAuth2OOo/README_fr>
[4]: <https://prrvchr.github.io/OAuth2OOo/source/OAuth2OOo/registration/TermsOfUse_en>
[5]: <https://prrvchr.github.io/OAuth2OOo/source/OAuth2OOo/registration/PrivacyPolicy_en>
[6]: <https://prrvchr.github.io/OAuth2OOo/CHANGELOG#what-has-been-done-for-version-160>
[7]: <https://prrvchr.github.io>
[8]: <https://www.libreoffice.org/download/download/>
[9]: <https://www.openoffice.org/download/index.html>
[10]: <https://en.wikipedia.org/wiki/OAuth>
[11]: <https://help.libreoffice.org/latest/en-US/text/sbasic/shared/01000000.html?DbPAR=BASIC>
[12]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/OAuth2OOo/HTTPGetRequest.xba>
[13]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/OAuth2OOo/HTTPPostRequest.xba>
[14]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/OAuth2OOo/ChatGPTRequest.xba>
[15]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/OAuth2OOo/GoogleAPIRequest.xba>
[16]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/OAuth2OOo/GraphAPIRequest.xba>
[17]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/OAuth2OOo/GithubDownloadRequest.xba>
[18]: <https://github.com/prrvchr/OAuth2OOo/releases/latest/download/LDLC-MacBook-Pro.ods>
[19]: <https://github.com/prrvchr/OAuth2OOo/releases/latest/download/LDLC-Asus-Zenbook.ods>
[20]: <https://pypi.org/project/selenium/4.16.0/>
[21]: <https://github.com/prrvchr/OAuth2OOo/releases/latest/download/Page-Jaunes-Windows.ods>
[22]: <https://github.com/prrvchr/OAuth2OOo/releases/latest/download/Page-Jaunes-Linux.ods>
[23]: <https://github.com/prrvchr/OAuth2OOo>
[24]: <https://github.com/prrvchr/OAuth2OOo/issues/new>
[25]: <https://github.com/sponsors/prrvchr>
[26]: <https://appdefensealliance.dev/casa>
[27]: <https://github.com/prrvchr/OAuth2OOo/blob/master/LOV_OAuth2OOo.pdf>
[28]: <https://img.shields.io/static/v1?label=Sponsor&message=%E2%9D%A4&logo=GitHub&color=%23fe8e86#right>
[29]: <https://www.libreoffice.org/download/download-libreoffice/>
[30]: <https://github.com/prrvchr/OAuth2OOo/releases/latest/download/requirements.txt>
[31]: <https://packaging.python.org/en/latest/tutorials/installing-packages/#use-pip-for-installing>
[32]: <https://prrvchr.github.io/OAuth2OOo/img/OAuth2OOo.svg#middle>
[33]: <https://github.com/prrvchr/OAuth2OOo/releases/latest/download/OAuth2OOo.oxt>
[34]: <https://github.com/prrvchr/OAuth2OOo/blob/master/uno/rdb/idl/com/sun/star/auth/XOAuth2Service.idl>
[35]: <https://github.com/prrvchr/OAuth2OOo/blob/master/uno/rdb/idl/com/sun/star/rest/XRequestParameter.idl>
[36]: <https://github.com/prrvchr/OAuth2OOo/blob/master/uno/rdb/idl/com/sun/star/rest/XRequestResponse.idl>
[37]: <https://img.shields.io/github/downloads/prrvchr/OAuth2OOo/latest/total?label=v1.6.0#right>
[38]: <https://prrvchr.github.io/OAuth2OOo/img/OAuth2Wizard1.png>
[39]: <https://prrvchr.github.io/OAuth2OOo/img/OAuth2Wizard2.png>
[40]: <https://prrvchr.github.io/OAuth2OOo/img/OAuth2Wizard3.png>
[41]: <https://prrvchr.github.io/OAuth2OOo/img/OAuth2Wizard4.png>
[42]: <https://prrvchr.github.io/OAuth2OOo/img/OAuth2Wizard5.png>
[43]: <https://prrvchr.github.io/OAuth2OOo/img/OAuth2Wizard6.png>
[44]: <https://prrvchr.github.io/OAuth2OOo/img/OAuth2Wizard7.png>
[45]: <https://prrvchr.github.io/OAuth2OOo/img/OAuth2Wizard8.png>
[46]: <https://github.com/LibreOffice/loeclipse>
[47]: <https://adoptium.net/temurin/releases/?version=8&package=jdk>
[48]: <https://ant.apache.org/manual/install.html>
[49]: <https://downloadarchive.documentfoundation.org/libreoffice/old/7.6.7.2/>
[50]: <https://github.com/prrvchr/OAuth2OOo.git>
[51]: <https://bz.apache.org/ooo/show_bug.cgi?id=128569>
[52]: <https://prrvchr.github.io/OAuth2OOo/CHANGELOG>
