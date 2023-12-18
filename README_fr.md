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
# Documentation

**This [document][3] in English.**

**L'utilisation de ce logiciel vous soumet à nos [Conditions d'utilisation][4] et à notre [Politique de protection des données][5].**

# version [1.2.4][6]

## Introduction:

**OAuth2OOo** fait partie d'une [Suite][7] d'extensions [LibreOffice][8] ~~et/ou [OpenOffice][9]~~ permettant de vous offrir des services inovants dans ces suites bureautique.  
Cette extension est l'implémentation du protocole OAuth 2.0. Protocole permettant d'obtenir votre consentement pour qu'une application puisse accéder à vos données présentes chez les GAFA.

Etant un logiciel libre je vous encourage:
- A dupliquer son [code source][10].
- A apporter des modifications, des corrections, des ameliorations.
- D'ouvrir un [dysfonctionnement][11] si nécessaire.

Bref, à participer au developpement de cette extension.
Car c'est ensemble que nous pouvons rendre le Logiciel Libre plus intelligent.

___

## Prérequis:

Afin de profiter des dernières versions des bibliothèques Python utilisées dans OAuth2OOo, la version 2 de Python a été abandonnée au profit de **Python 3.8 minimum**.  
Cela signifie que **OAuth2OOo ne supporte plus OpenOffice et LibreOffice 6.x sous Windows depuis sa version 1.1.0**.
Je ne peux que vous conseiller **de migrer vers LibreOffice 7.x**.

Pour vous proposer tous ces nouveaux services dans LibreOffice, l'extension OAuth2OOo utilise de nombreuses bibliothèques Python.
Certaines de ces librairies embarquent des fichiers binaires qui dépendent:
- De la version de Python (entre 3.8 et 3.11 inclus)
- Du système d'exploitation (Linux, Windows, Macos, etc...)
- De l'architecture de votre ordinateur (i386, adm x64, arm64, ppc, etc...)

Trois bibliothèques ou **paquets Python** dépendent de votre système et ont les fichiers binaires embarqués suivant:
- [Fichiers binaires][12] pour le paquet [charset-normalizer][13] version 3.1.0.
- [Fichiers binaires][14] pour le paquet [ijson] [15] version 3.2.2.
- [Fichiers binaires][16] pour le paquet [lxml] [17] version 4.9.2.
- [Fichiers binaires][18] pour le paquet [cffi] [19] version 1.16.0.

Pour toutes ces raisons:
- Si vous êtes **sous Windows tous les différents binaires nécessaires sont livrés avec l'extension OAuth2OOo**.
- Si vous êtes **sur Linux x86_64 les binaires nécessaires pour Python version 3.10 sont livrés avec l'extension OAuth2OOo**.
- **Pour toutes les autres combinaisons de configuration possibles, si ils ne sont pas déjà présents, vous devrez installer ces 3 paquets python**.  
En leur absence, une erreur devrait apparaître lors de l'installation de l'extension OAuthOOo lors de l'importation du package lxml.
Cette erreur peut être corrigée en installant, généralement à l'aide de [pip][20], les 3 paquets Python requis par votre configuration.

Si vous voulez **piloter Firefox dans Calc sous Ubuntu** alors il vous faut reinstaller Firefox à partir du PPA de Mozilla.
Pour installer le PPA de Mozilla veuillez taper la commande:
- `sudo add-apt-repository ppa:mozillateam/ppa`

___

## Installation:

Il semble important que le fichier n'ait pas été renommé lors de son téléchargement.  
Si nécessaire, renommez-le avant de l'installer.

- ![OAuth2OOo logo][21] Installer l'extension **[OAuth2OOo.oxt][22]** [![Version][23]][22]

Redémarrez LibreOffice / OpenOffice après l'installation.

___

## Utilisation:

Cette extension n'est pas faite pour être utilisée seule, mais fournit le service OAuth2 à d'autres extensions LibreOffice ~~/ OpenOffice~~.  
Voici comment nous utilisons son API:

### Créer le service OAuth2:

> identifier = "io.github.prrvchr.OAuth2OOo.OAuth2Service"  
> service = ctx.ServiceManager.createInstanceWithContext(identifier, ctx)

### Initialiser la Session ou au moins l'Url:

- Initialiser la Session: 

> initialized = service.initializeSession(registered_url, user_account)

La valeur renvoyée: `initialized` est True si `user_account` est déjà autorisé pour `registered_url`.

- Initialiser l'Url:

> initialized = service.initializeUrl(registered_url)

La valeur renvoyée: `initialized` est True si `registered_url` a été trouvé avec succès dans la configuration du service OAuth2.

### Obtenir le jeton d'accès:

> format = 'Bearer %s'  
> token = service.getToken(format)

___

## Uno OAuth2.0 API pour LibreOffice.

![OAuth2OOo Wizard Page1 screenshot][24]

![OAuth2OOo Wizard Page2 screenshot][25]

![OAuth2OOo Wizard Page3 screenshot][26]

![OAuth2OOo Browser Page1 screenshot][27]

![OAuth2OOo Browser Page2 screenshot][28]

![OAuth2OOo Browser Page3 screenshot][29]

![OAuth2OOo Browser Page4 screenshot][30]

![OAuth2OOo Wizard Page4 screenshot][31]

Le protocole OAuth2 permet d'accéder aux ressources de serveurs, après acceptation de l'autorisation de connexion, en échangeant des jetons.

La révocation a lieu dans la gestion des applications associées à votre compte.

Plus aucun mot de passe n'est stocké dans LibreOffice.

___

## A été testé avec:

* LibreOffice 7.3.7.2 - Lubuntu 22.04 - Python version 3.10.12

* LibreOffice 7.5.4.2(x86) - Windows 10 - Python version 3.8.16 (sous Lubuntu 22.04 / VirtualBox 6.1.38)

* LibreOffice 7.4.3.2(x64) - Windows 10(x64) - Python version 3.8.15 (sous Lubuntu 22.04 / VirtualBox 6.1.38)

* **Ne fonctionne pas avec OpenOffice** voir [dysfonctionnement 128569][32]. N'ayant aucune solution, je vous encourrage d'installer **LibreOffice**.

Je vous encourage en cas de problème :confused:  
de créer un [dysfonctionnement][11]  
J'essaierai de le résoudre :smile:

___

## Historique:

### Ce qui a été fait pour la version 0.0.5:

- Ecriture d'une nouvelle interface [XWizard][33] afin de remplacer le service Wizard devenu défectueux avec les versions 6.4.x et 7.x de LibreOffice (voir [bug 132110][34]).

    Cette nouvelle interface corrige également le [bug 132661][35] et le [bug 132666][36] et permet d'accéder aux versions 6.4.x et 7.x de LibreOffice...

    De plus, ce nouveau XWizard ajoute de nouvelles fonctionnalités telles que:

    - Redimensionnement automatique de l'assistant aux dimensions de la première page affichée.
    - Déplacement automatique vers la page X à l'ouverture si possible.

- Correction d'un problème avec les jetons sans expiration (tels qu'utilisés par Dropbox) lors du test de leur validité...

- Beaucoup d'autres correctifs...

### Ce qui a été fait pour la version 0.0.6:

- Réécriture de l'assistant OAuth2 (Wizard) en essayant de suivre au mieux le [modèle MVA][37]. Cet assistant est composé de 5 pages héritant de l'interface UNO [XWizardPage][38]:

    - Page 1: [Adapteur][39] et [Vue][40]
    - Page 2: [Adapteur][41] et [Vue][42]
    - Page 3: [Adapteur][43] et [Vue][44]
    - Page 4: [Adapteur][45] et [Vue][46]
    - Page 5: [Adapteur][47] et [Vue][48]

- Réécriture des trois services UNO fournis par l'extension OAuth2OOo dans trois fichiers distincts:

    - Le service [OAuth2Service][49] implémentant l'interface décrite dans le fichier IDL [XOAuth2Service][50].
    - Le service [OAuth2Dispacher][51] implémentant l'interface UNO [XDispatchProvider][52].
    - Le service [OAuth2Handler][53] implémentant l'interface UNO [XInteractionHandler2][54].

- Réécriture de la fenêtre des options accessible par **Outils -> Options -> Internet -> Protocole OAuth2**. Cette fenêtre est composée de deux fenêtres:

    - La fenêtre de journalisation: [Adapteur][55] et [Vue][56].
    - La fenêtre des options de configuration de l'extension OAuth2OOo: [Adapteur][57] et [Vue][58].

- Réécriture d'un modèle de données unique [OAuth2Model][59] gérant l'assistant, les services, et la fenêtre des options.

- L'erreur de flux de bouclage Google a été corrigée. Voir [Dysfonctionnement #10][60]

- Utilisation pour Dropbox de leur nouvelle API avec des jetons expirables.

- Beaucoup d'autres correctifs...

### Ce qui a été fait pour la version 1.0.0:

- Portage de l'API Python [Requests][61] vers l'API LibreOffice / OpenOffice UNO. Deux interfaces UNO sont accessibles:

    - Les paramètres de requête HTTP: [com.sun.star.rest.XRequestParameter.idl][62]
    - La réponse à la requête HTTP: [com.sun.star.rest.XRequestResponse.idl][63]  

    L'interface XRequestParameter prend en charge la gestion des jetons de synchronisation ainsi que la pagination des requêtes HTTP, telles qu'elles sont utilisées dans les API HTTP Rest.

- La mise à jour et le téléchargement des fichiers est possible grâce aux méthodes ou propriétés:

    - `XOAuth2Service.download()` permettant le téléchargement de fichiers avec reprise.
    - `XOAuth2Service.upload()` permettant la mise à jour de fichiers avec reprise.
    - `XOAuth2Service.getInputStream()` pour obtenir un flux d'entrée.
    - `XRequestParameter.DataSink` pour définir un flux d'entrée.
    - `XRequestResponse.getInputStream()` pour obtenir un flux d'entrée.

- Portage de l'API Java [javax.json][64] vers l'API LibreOffice / OpenOffice UNO comme défini dans les fichiers idl: [com.sun.star.json.*][65]

    - Une fabrique de structures JSON est accessible via l'interface `getJsonBuilder()` de [XRequestParameter][62].
    - Un analyseur Json est renvoyé par l'interface `getJson()` de [XRequestResponse][63].

**Cela rend les requêtes HTTP utilisant JSON facilement utilisable dans le langage BASIC de LibreOffice.**

Voir les macros [Requêtes HTTP sous BASIC][66] et [Requêtes ChatGPT en BASIC][67].

### Ce qui a été fait pour la version 1.0.1:

- Ecriture de 15 fonctions en AddIns de Calc comme décrit dans les fichiers suivants:

    - Le fichier [OAuth2Plugin.idl][68] qui declare à UNO les nouvelles interfaces.
    - Le fichier [CalcAddIns.xcu][69] qui rend disponible ces nouvelles interface dans le liste des fonctions de Calc.
    - Le fichier [OAuth2Plugin.py][70] qui est l'implementation du service UNO `com.sun.star.auth.Oauth2Plugin` founissant ces nouvelles interfaces.
    - Le fichier [plugin.py][71] qui est la bibliotheque implementant les interface de ce nouveau service UNO.

- Ces 4 nouveaux fichiers donne acces à **15 nouvelles formules Calc** qui sont:

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

- Un bon exemple vaut mieux qu'un long discours, je vous invite donc à télécharger deux feuilles Calc permettant de récupérer très facilement les micro données HTML de n'importe quelle site Web.

    - [LDLC Home.ods][72]
    - [LDLC poducts.ods][73]

### Ce qui a été fait pour la version 1.1.0:

- **Fin du support de Python 2.x et donc d'OpenOffice**.

- Intégration de [Selenium][74] version 4.10 dans l'extension afin de rendre **LibreOffice capable de piloter un navigateur via des formules Calc** insérées dans une feuille de calcul.

- Utilisation de [webdriver_manager][75] version 3.8.6 permettant d'automatiser l'installation du [WebDriver][76] du navigateur.

- Création de 5 formules Calc permettant le **pilotage du navigateur**:

    - `BROWSEROPEN(BROWSER,PATH,INIT,OPTIONS)`
    - `BROWSERCLICK(SESSION,BY,PATH,URL,INIT,WAIT)`
    - `BROWSERFIELD(SESSION,BY,PATH,VALUE,URL,INIT,WAIT)`
    - `BROWSERFORM(SESSION,FORM,URL,INIT,WAIT)`
    - `BROWSERCONTENT(SESSION,URL,ENCODING)`

- Création d'une formule Calc permettant l'authentification HTTP Basic Auth pour les requêtes HTTP:

    - `HTTPAUTH(NAME,PASSWORD)`

- La formule Calc `GETHTTPBOBY` a été renommée en `HTTPCONTENT`.

### Ce qui a été fait pour la version 1.1.1:

- Correction d'un problème dans [l'implémentation][77] de l'interface [com.sun.star.rest.XRequestParameter][62] ne permettant pas de créer des objets JSON vides (ie : "Object": {} ) comme demandé par l'API Microsoft Graph.

### Ce qui a été fait pour la version 1.1.2:

- Modification des fichiers idl: [XRequestParameter.idl][62] et [XRequestResponse.idl][63] et des implementations python sous jacente: [requestparameter.py][77] et [requestresponse.py][78] afin de rendre possible les requêtes **POST** avec l'encodage **application/x-www-form-urlencoded**. Voir [dysfonctionnement #13][79].

- 3 macros en BASIC: `ChatGPTRequest`, `HTTPGetRequest` et `HTTPPostRequest` sont disponible dans: **Outils -> Macros -> Exécuter la macro... -> Mes macros -> OAuth2OOo**. Attention, ces macros **ne fonctionneront pas si aucun document n'est ouvert** (je ne sais pas pourquoi?)...

- Désormais, à chaque push, un [workflow effectue un scan][80] du code avec [Fluid Attacks][81]. Ceci a été mis en place pour suivre le [Cloud Application Security Assessment][82] (CASA) et répondre aux exigences de revalidation de l'extension OAuth2OOo avec Google.

- Pour les mêmes raisons, la [Politique de Protection des Données][5] a été modifiée afin de préciser la [Nature et l'étendue des droits sur vos données][83].

### Ce qui a été fait pour la version 1.2.0:

- Il existe désormais deux méthodes pour créer le service [OAuth2Service][84] qui sont :
  - `create()` sans paramètre, renvoie une instance du service.
  - `createWithOAuth2([in] string sUrl, [in] string sUser)` avec une Url et l'adresse de l'utilisateur, renvoie une instance du service avec le protocole OAuth2.  
    Dans sa deuxième forme, l'assistant d'autorisation OAuth2 (Wizard) se lancera automatiquement si l'étendue des droits de l'Url n'a pas encore été accordée par l'utilisateur (ie : première connexion).  
    Si tel est le cas et que l'assistant est abandonné, une valeur nulle sera renvoyée à la place du service demandé.

- Deux macros BASIC: `GoogleAPIRequest` et `GraphAPIRequest` permettent d'effectuer des requêtes HTTP sur les API de Google Contact et Microsoft Graph.  
  Le protocole OAuth2 indispensable à l'utilisation de ces API est intégré de manière automatique et transparente aux requêtes HTTP. Vous n'aurez pas à vous en soucier.

### Ce qui a été fait pour la version 1.2.1:

- Ajout d'une nouvelle méthode `isAuthorized()` à l'interface [XOAuth2Service][49] prise en charge par le service [OAuth2Service][84]. Cette méthode permet de lancer l'assistant de configuration OAuth2 si l'utilisateur n'est pas autorisé.

### Ce qui a été fait pour la version 1.2.2:

- Correction d'une erreur lors de l'actualisation des jetons OAuth2.

### Ce qui a été fait pour la version 1.2.3:

- Correction d'une erreur sur isAuthorized() du OAuth2Service.

### Ce qui a été fait pour la version 1.2.4:

- Mise à jour des paquets python embarqués.

### Que reste-t-il à faire pour la version 1.2.4:

- Ajouter de nouvelles langue pour l'internationalisation...

- Tout ce qui est bienvenu...

[1]: </img/oauth2.svg#collapse>
[2]: <https://prrvchr.github.io/OAuth2OOo/>
[3]: <https://prrvchr.github.io/OAuth2OOo>
[4]: <https://prrvchr.github.io/OAuth2OOo/source/OAuth2OOo/registration/TermsOfUse_fr>
[5]: <https://prrvchr.github.io/OAuth2OOo/source/OAuth2OOo/registration/PrivacyPolicy_fr>
[6]: <https://prrvchr.github.io/OAuth2OOo/README_fr#ce-qui-a-été-fait-pour-la-version-110>
[7]: <https://prrvchr.github.io/README_fr>
[8]: <https://fr.libreoffice.org/download/telecharger-libreoffice/>
[9]: <https://www.openoffice.org/fr/Telecharger/>
[10]: <https://github.com/prrvchr/OAuth2OOo>
[11]: <https://github.com/prrvchr/OAuth2OOo/issues/new>
[12]: <https://github.com/prrvchr/OAuth2OOo/blob/master/uno/lib/python/charset_normalizer>
[13]: <https://pypi.org/project/charset-normalizer/3.1.0/#files>
[14]: <https://github.com/prrvchr/OAuth2OOo/blob/master/uno/lib/python/ijson/backends>
[15]: <https://pypi.org/project/ijson/3.2.2/#files>
[16]: <https://github.com/prrvchr/OAuth2OOo/blob/master/uno/lib/python/lxml>
[17]: <https://pypi.org/project/lxml/4.9.2/#files>
[18]: <https://github.com/prrvchr/OAuth2OOo/blob/master/uno/lib/python/cffi>
[19]: <https://pypi.org/project/cffi/1.16.0/#files>
[20]: <https://packaging.python.org/en/latest/tutorials/installing-packages/#use-pip-for-installing>
[21]: <https://prrvchr.github.io/OAuth2OOo/img/OAuth2OOo.svg#middle>
[22]: <https://github.com/prrvchr/OAuth2OOo/releases/latest/download/OAuth2OOo.oxt>
[23]: <https://img.shields.io/github/downloads/prrvchr/OAuth2OOo/latest/total?label=v1.2.4#right>
[24]: <https://prrvchr.github.io/OAuth2OOo/img/OAuth2Wizard1_fr.png>
[25]: <https://prrvchr.github.io/OAuth2OOo/img/OAuth2Wizard2_fr.png>
[26]: <https://prrvchr.github.io/OAuth2OOo/img/OAuth2Wizard3_fr.png>
[27]: <https://prrvchr.github.io/OAuth2OOo/img/OAuth2Wizard4_fr.png>
[28]: <https://prrvchr.github.io/OAuth2OOo/img/OAuth2Wizard5_fr.png>
[29]: <https://prrvchr.github.io/OAuth2OOo/img/OAuth2Wizard6_fr.png>
[30]: <https://prrvchr.github.io/OAuth2OOo/img/OAuth2Wizard7_fr.png>
[31]: <https://prrvchr.github.io/OAuth2OOo/img/OAuth2Wizard8_fr.png>
[32]: <https://bz.apache.org/ooo/show_bug.cgi?id=128569>
[33]: <https://github.com/prrvchr/OAuth2OOo/blob/master/uno/lib/uno/wizard/wizard.py>
[34]: <https://bugs.documentfoundation.org/show_bug.cgi?id=132110>
[35]: <https://bugs.documentfoundation.org/show_bug.cgi?id=132661>
[36]: <https://bugs.documentfoundation.org/show_bug.cgi?id=132666>
[37]: <https://en.wikipedia.org/wiki/Model%E2%80%93view%E2%80%93adapter>
[38]: <https://www.openoffice.org/api/docs/common/ref/com/sun/star/ui/dialogs/XWizardPage.html>
[39]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/service/pythonpath/oauth2/wizard/page1/oauth2manager.py>
[40]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/service/pythonpath/oauth2/wizard/page1/oauth2view.py>
[41]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/service/pythonpath/oauth2/wizard/page2/oauth2manager.py>
[42]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/service/pythonpath/oauth2/wizard/page2/oauth2view.py>
[43]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/service/pythonpath/oauth2/wizard/page3/oauth2manager.py>
[44]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/service/pythonpath/oauth2/wizard/page3/oauth2view.py>
[45]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/service/pythonpath/oauth2/wizard/page4/oauth2manager.py>
[46]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/service/pythonpath/oauth2/wizard/page4/oauth2view.py>
[47]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/service/pythonpath/oauth2/wizard/page5/oauth2manager.py>
[48]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/service/pythonpath/oauth2/wizard/page5/oauth2view.py>
[49]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/service/OAuth2Service.py>
[50]: <https://github.com/prrvchr/OAuth2OOo/blob/master/uno/rdb/idl/com/sun/star/auth/XOAuth2Service.idl>
[51]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/service/OAuth2Dispatcher.py>
[52]: <https://www.openoffice.org/api/docs/common/ref/com/sun/star/frame/XDispatchProvider.html>
[53]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/service/OAuth2Handler.py>
[54]: <https://www.openoffice.org/api/docs/common/ref/com/sun/star/task/XInteractionHandler2.html>
[55]: <https://github.com/prrvchr/OAuth2OOo/blob/master/uno/lib/uno/logger/logmanager.py>
[56]: <https://github.com/prrvchr/OAuth2OOo/blob/master/uno/lib/uno/logger/logview.py>
[57]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/service/pythonpath/oauth2/options/optionsmanager.py>
[58]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/service/pythonpath/oauth2/options/optionsview.py>
[59]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/service/pythonpath/oauth2/oauth2model.py>
[60]: <https://github.com/prrvchr/OAuth2OOo/issues/10>
[61]: <https://pypi.org/project/requests/2.31.0/>
[62]: <https://github.com/prrvchr/OAuth2OOo/blob/master/uno/rdb/idl/com/sun/star/rest/XRequestParameter.idl>
[63]: <https://github.com/prrvchr/OAuth2OOo/blob/master/uno/rdb/idl/com/sun/star/rest/XRequestResponse.idl>
[64]: <https://javadoc.io/static/javax.json/javax.json-api/1.1.4/index.html?overview-summary.html>
[65]: <https://github.com/prrvchr/OAuth2OOo/tree/master/uno/rdb/idl/com/sun/star/json>
[66]: <https://forum.openoffice.org/fr/forum/viewtopic.php?t=67387>
[67]: <https://forum.openoffice.org/fr/forum/viewtopic.php?t=67402>
[68]: <https://github.com/prrvchr/OAuth2OOo/tree/master/uno/rdb/idl/com/sun/star/auth/XOAuth2Plugin.idl>
[69]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/CalcAddIns.xcu>
[70]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/service/OAuth2Plugin.py>
[71]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/service/pythonpath/oauth2/plugin.py>
[72]: <https://forum.openoffice.org/fr/forum/download/file.php?id=150036>
[73]: <https://forum.openoffice.org/fr/forum/download/file.php?id=150040>
[74]: <https://pypi.org/project/selenium/4.10/>
[75]: <https://pypi.org/project/webdriver-manager/3.8.6/>
[76]: <https://developer.mozilla.org/en-US/docs/Web/WebDriver>
[77]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/service/pythonpath/oauth2/requestparameter.py>
[78]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/service/pythonpath/oauth2/requestresponse.py>
[79]: <https://github.com/prrvchr/OAuth2OOo/issues/13>
[80]: <https://github.com/prrvchr/OAuth2OOo/actions/workflows/dev.yml>
[81]: <https://github.com/fluidattacks>
[82]: <https://appdefensealliance.dev/casa/tier-2/tier2-overview>
[83]: <https://prrvchr.github.io/OAuth2OOo/source/OAuth2OOo/registration/PrivacyPolicy_fr#nature-et-étendue-des-droits-sur-vos-données>
[84]: <https://github.com/prrvchr/OAuth2OOo/blob/master/uno/rdb/idl/com/sun/star/auth/OAuth2Service.idl>
