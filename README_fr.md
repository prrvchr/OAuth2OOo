# Documentation

**This [document][2] in English.**

**L'utilisation de ce logiciel vous soumet à nos [Conditions d'utilisation][3] et à notre [Politique de protection des données][4].**

# version [1.1.2][5]

## Introduction:

**OAuth2OOo** fait partie d'une [Suite][6] d'extensions [LibreOffice][7] ~~et/ou [OpenOffice][8]~~ permettant de vous offrir des services inovants dans ces suites bureautique.  
Cette extension est l'implémentation du protocole OAuth 2.0. Protocole permettant d'obtenir votre consentement pour qu'une application puisse accéder à vos données présentes chez les GAFA.

Etant un logiciel libre je vous encourage:
- A dupliquer son [code source][9].
- A apporter des modifications, des corrections, des ameliorations.
- D'ouvrir un [dysfonctionnement][10] si nécessaire.

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
- [Fichiers binaires][11] pour le paquet [charset-normalizer][12] version 3.1.0.
- [Fichiers binaires][13] pour le paquet [ijson] [14] version 3.2.2.
- [Fichiers binaires][15] pour le paquet [lxml] [16] version 4.9.2.

Pour toutes ces raisons:
- Si vous êtes **sous Windows tous les différents binaires nécessaires sont livrés avec l'extension OAuth2OOo**.
- Si vous êtes **sur Linux x86_64 les binaires nécessaires pour Python version 3.10 sont livrés avec l'extension OAuth2OOo**.
- **Pour toutes les autres combinaisons de configuration possibles, si ils ne sont pas déjà présents, vous devrez installer ces 3 paquets python**.  
En leur absence, une erreur devrait apparaître lors de l'installation de l'extension OAuthOOo lors de l'importation du package lxml.
Cette erreur peut être corrigée en installant, généralement à l'aide de [pip][17], les 3 paquets Python requis par votre configuration.

Si vous voulez **piloter Firefox dans Calc sous Ubuntu** alors il vous faut reinstaller Firefox à partir du PPA de Mozilla.
Pour installer le PPA de Mozilla veuillez taper la commande:
- `sudo add-apt-repository ppa:mozillateam/ppa`

___
## Installation:

Il semble important que le fichier n'ait pas été renommé lors de son téléchargement.  
Si nécessaire, renommez-le avant de l'installer.

- Installer l'extension ![OAuth2OOo logo][1] **[OAuth2OOo.oxt][18]** version 1.1.2.

- Redémarrez LibreOffice / OpenOffice après l'installation.

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

![OAuth2OOo Wizard Page1 screenshot][19]

![OAuth2OOo Wizard Page2 screenshot][20]

![OAuth2OOo Wizard Page3 screenshot][21]

![OAuth2OOo Browser Page1 screenshot][22]

![OAuth2OOo Browser Page2 screenshot][23]

![OAuth2OOo Browser Page3 screenshot][24]

![OAuth2OOo Browser Page4 screenshot][25]

![OAuth2OOo Wizard Page4 screenshot][26]

Le protocole OAuth2 permet d'accéder aux ressources de serveurs, après acceptation de l'autorisation de connexion, en échangeant des jetons.

La révocation a lieu dans la gestion des applications associées à votre compte.

Plus aucun mot de passe n'est stocké dans LibreOffice.

___
## A été testé avec:

* LibreOffice 7.3.7.2 - Lubuntu 22.04 - Python version 3.10.12

* LibreOffice 7.5.4.2(x86) - Windows 10 - Python version 3.8.16 (sous Lubuntu 22.04 / VirtualBox 6.1.38)

* LibreOffice 7.4.3.2(x64) - Windows 10(x64) - Python version 3.8.15 (sous Lubuntu 22.04 / VirtualBox 6.1.38)

* **Ne fonctionne pas avec OpenOffice** voir [dysfonctionnement 128569][27]. N'ayant aucune solution, je vous encourrage d'installer **LibreOffice**.

Je vous encourage en cas de problème :confused:  
de créer un [dysfonctionnement][10]  
J'essaierai de le résoudre :smile:

___
## Historique:

### Ce qui a été fait pour la version 0.0.5:

- Ecriture d'une nouvelle interface [XWizard][28] afin de remplacer le service Wizard devenu défectueux avec les versions 6.4.x et 7.x de LibreOffice (voir [bug 132110][29]).

    Cette nouvelle interface corrige également le [bug 132661][30] et le [bug 132666][31] et permet d'accéder aux versions 6.4.x et 7.x de LibreOffice...

    De plus, ce nouveau XWizard ajoute de nouvelles fonctionnalités telles que:

    - Redimensionnement automatique de l'assistant aux dimensions de la première page affichée.
    - Déplacement automatique vers la page X à l'ouverture si possible.

- Correction d'un problème avec les jetons sans expiration (tels qu'utilisés par Dropbox) lors du test de leur validité...

- Beaucoup d'autres correctifs...

### Ce qui a été fait pour la version 0.0.6:

- Réécriture de l'assistant OAuth2 (Wizard) en essayant de suivre au mieux le [modèle MVA][32]. Cet assistant est composé de 5 pages héritant de l'interface UNO [XWizardPage][33]:

    - Page 1: [Adapteur][34] et [Vue][35]
    - Page 2: [Adapteur][36] et [Vue][37]
    - Page 3: [Adapteur][38] et [Vue][39]
    - Page 4: [Adapteur][40] et [Vue][41]
    - Page 5: [Adapteur][42] et [Vue][43]

- Réécriture des trois services UNO fournis par l'extension OAuth2OOo dans trois fichiers distincts:

    - Le service [OAuth2Service][44] implémentant l'interface décrite dans le fichier IDL [XOAuth2Service][45].
    - Le service [OAuth2Dispacher][46] implémentant l'interface UNO [XDispatchProvider][47].
    - Le service [OAuth2Handler][48] implémentant l'interface UNO [XInteractionHandler2][49].

- Réécriture de la fenêtre des options accessible par **Outils -> Options -> Internet -> Protocole OAuth2**. Cette fenêtre est composée de deux fenêtres:

    - La fenêtre de journalisation: [Adapteur][50] et [Vue][51].
    - La fenêtre des options de configuration de l'extension OAuth2OOo: [Adapteur][52] et [Vue][53].

- Réécriture d'un modèle de données unique [OAuth2Model][54] gérant l'assistant, les services, et la fenêtre des options.

- L'erreur de flux de bouclage Google a été corrigée. Voir [Dysfonctionnement #10][55]

- Utilisation pour Dropbox de leur nouvelle API avec des jetons expirables.

- Beaucoup d'autres correctifs...

### Ce qui a été fait pour la version 1.0.0:

- Portage de l'API Python [Requests][56] vers l'API LibreOffice / OpenOffice UNO. Deux interfaces UNO sont accessibles:

    - Les paramètres de requête HTTP: [com.sun.star.rest.XRequestParameter.idl][57]
    - La réponse à la requête HTTP: [com.sun.star.rest.XRequestResponse.idl][58]  

    L'interface XRequestParameter prend en charge la gestion des jetons de synchronisation ainsi que la pagination des requêtes HTTP, telles qu'elles sont utilisées dans les API HTTP Rest.

- La mise à jour et le téléchargement des fichiers est possible grâce aux méthodes ou propriétés:

    - `XOAuth2Service.download()` permettant le téléchargement de fichiers avec reprise.
    - `XOAuth2Service.upload()` permettant la mise à jour de fichiers avec reprise.
    - `XOAuth2Service.getInputStream()` pour obtenir un flux d'entrée.
    - `XRequestParameter.DataSink` pour définir un flux d'entrée.
    - `XRequestResponse.getInputStream()` pour obtenir un flux d'entrée.

- Portage de l'API Java [javax.json][59] vers l'API LibreOffice / OpenOffice UNO comme défini dans les fichiers idl: [com.sun.star.json.*][60]

    - Une fabrique de structures JSON est accessible via l'interface `getJsonBuilder()` de [XRequestParameter][57].
    - Un analyseur Json est renvoyé par l'interface `getJson()` de [XRequestResponse][58].

**Cela rend les requêtes HTTP utilisant JSON facilement utilisable dans le langage Basic de LibreOffice.**

Voir les macros [Requêtes HTTP sous Basic][61] et [Requêtes ChatGPT en Basic][62].

### Ce qui a été fait pour la version 1.0.1:

- Ecriture de 15 fonctions en AddIns de Calc comme décrit dans les fichiers suivants:

    - Le fichier [OAuth2Plugin.idl][63] qui declare à UNO les nouvelles interfaces.
    - Le fichier [CalcAddIns.xcu][64] qui rend disponible ces nouvelles interface dans le liste des fonctions de Calc.
    - Le fichier [OAuth2Plugin.py][65] qui est l'implementation du service UNO `com.sun.star.auth.Oauth2Plugin` founissant ces nouvelles interfaces.
    - Le fichier [plugin.py][66] qui est la bibliotheque implementant les interface de ce nouveau service UNO.

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

    - [LDLC Home.ods][67]
    - [LDLC poducts.ods][68]

### Ce qui a été fait pour la version 1.1.0:

- **Fin du support de Python 2.x et donc d'OpenOffice**.

- Intégration de [Selenium][69] version 4.10 dans l'extension afin de rendre **LibreOffice capable de piloter un navigateur via des formules Calc** insérées dans une feuille de calcul.

- Utilisation de [webdriver_manager][70] version 3.8.6 permettant d'automatiser l'installation du [WebDriver][71] du navigateur.

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

- Correction d'un problème dans [l'implémentation][72] de l'interface [com.sun.star.rest.XRequestParameter][57] ne permettant pas de créer des objets JSON vides (ie : "Object": {} ) comme demandé par l'API Microsoft Graph.

### Ce qui a été fait pour la version 1.1.2:

- Modification des fichiers idl: [XRequestParameter.idl][57] et [XRequestResponse.idl][58] et des implementations python sous jacente: [requestparameter.py][72] et [requestresponse.py][73] afin de rendre possible les requêtes **POST** avec l'encodage **application/x-www-form-urlencoded**. Voir [dysfonctionnement #13][74].

- 3 macros en Basic: `ChatGPTRequest`, `HTTPGetRequest` et `HTTPPostRequest` sont disponible dans: **Outils -> Macros -> Exécuter la macro... -> Mes macros -> OAuth2OOo**. Attention, ces macros **ne fonctionneront pas si aucun document n'est ouvert** (je ne sais pas pourquoi?)...

- Désormais, à chaque push, un [workflow effectue un scan][75] du code avec [Fluid Attacks][76]. Ceci a été mis en place pour suivre le [Cloud Application Security Assessment][77] (CASA) et répondre aux exigences de revalidation de l'extension OAuth2OOo avec Google.

- Pour les mêmes raisons, la [Politique de Protection des Données][4] a été modifiée afin de préciser la [Nature et l'étendue des droits sur vos données][78].

### Que reste-t-il à faire pour la version 1.1.2:

- Ajouter de nouvelles langue pour l'internationalisation...

- Tout ce qui est bienvenu...

[1]: <https://prrvchr.github.io/OAuth2OOo/img/OAuth2OOo.svg>
[2]: <https://prrvchr.github.io/OAuth2OOo>
[3]: <https://prrvchr.github.io/OAuth2OOo/source/OAuth2OOo/registration/TermsOfUse_fr>
[4]: <https://prrvchr.github.io/OAuth2OOo/source/OAuth2OOo/registration/PrivacyPolicy_fr>
[5]: <https://prrvchr.github.io/OAuth2OOo/README_fr#ce-qui-a-été-fait-pour-la-version-110>
[6]: <https://prrvchr.github.io/README_fr>
[7]: <https://fr.libreoffice.org/download/telecharger-libreoffice/>
[8]: <https://www.openoffice.org/fr/Telecharger/>
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
[19]: <https://prrvchr.github.io/OAuth2OOo/img/OAuth2Wizard1_fr.png>
[20]: <https://prrvchr.github.io/OAuth2OOo/img/OAuth2Wizard2_fr.png>
[21]: <https://prrvchr.github.io/OAuth2OOo/img/OAuth2Wizard3_fr.png>
[22]: <https://prrvchr.github.io/OAuth2OOo/img/OAuth2Wizard4_fr.png>
[23]: <https://prrvchr.github.io/OAuth2OOo/img/OAuth2Wizard5_fr.png>
[24]: <https://prrvchr.github.io/OAuth2OOo/img/OAuth2Wizard6_fr.png>
[25]: <https://prrvchr.github.io/OAuth2OOo/img/OAuth2Wizard7_fr.png>
[26]: <https://prrvchr.github.io/OAuth2OOo/img/OAuth2Wizard8_fr.png>
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
[61]: <https://forum.openoffice.org/fr/forum/viewtopic.php?t=67387>
[62]: <https://forum.openoffice.org/fr/forum/viewtopic.php?t=67402>
[63]: <https://github.com/prrvchr/OAuth2OOo/tree/master/uno/rdb/idl/com/sun/star/auth/XOAuth2Plugin.idl>
[64]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/CalcAddIns.xcu>
[65]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/service/OAuth2Plugin.py>
[66]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/service/pythonpath/oauth2/plugin.py>
[67]: <https://forum.openoffice.org/fr/forum/download/file.php?id=150036>
[68]: <https://forum.openoffice.org/fr/forum/download/file.php?id=150040>
[69]: <https://pypi.org/project/selenium/4.10/>
[70]: <https://pypi.org/project/webdriver-manager/3.8.6/>
[71]: <https://developer.mozilla.org/en-US/docs/Web/WebDriver>
[72]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/service/pythonpath/oauth2/requestparameter.py>
[73]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/service/pythonpath/oauth2/requestresponse.py>
[74]: <https://github.com/prrvchr/OAuth2OOo/issues/13>
[75]: <https://github.com/prrvchr/OAuth2OOo/actions/workflows/dev.yml>
[76]: <https://github.com/fluidattacks>
[77]: <https://appdefensealliance.dev/casa/tier-2/tier2-overview>
[78]: <https://prrvchr.github.io/OAuth2OOo/source/OAuth2OOo/registration/PrivacyPolicy_fr#nature-et-étendue-des-droits-sur-vos-données>
