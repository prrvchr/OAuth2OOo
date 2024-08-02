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

# version [1.3.6][6]

## Introduction:

**OAuth2OOo** fait partie d'une [Suite][7] d'extensions [LibreOffice][8] ~~et/ou [OpenOffice][9]~~ permettant de vous offrir des services inovants dans ces suites bureautique.

Cette extension est l'implémentation du [protocole OAuth 2.0][10]. Protocole permettant d'obtenir votre consentement pour qu'une application puisse accéder à vos données présentes chez les GAFA.

Elle permet d'**exécuter des requêtes HTTP en BASIC** et fournit les macros suivantes à titre d'exemple:
- [HTTPGetRequest][11]
- [HTTPPostRequest][12]
- [ChatGPTRequest][13]
- [GoogleAPIRequest][14]
- [GraphAPIRequest][15]

Si au préalable vous ouvrez un document, vous pouvez les lancer par:  
**Outils -> Macros -> Exécuter la macro... -> Mes macros -> OAuth2OOo -> `nom-macro` -> Main -> Exécuter**

Elle permet également de **récupérer des données Internet dans une feuille Calc**. Voir les fichiers Calc suivants à titre d'exemple:
- [LDLC MacBook Pro.ods][16]
- [LDLC Asus Zenbook.ods][17]

Et enfin, elle permet de **piloter Firefox par un fichier Calc** (ou tout autre navigateur pris en charge par [Selenium][18]). Voir les fichiers suivant:
- [Page Jaunes (Windows).ods][19]
- [Page Jaunes (Linux).ods][20]

Etant un logiciel libre je vous encourage:
- A dupliquer son [code source][21].
- A apporter des modifications, des corrections, des ameliorations.
- D'ouvrir un [dysfonctionnement][22] si nécessaire.

Bref, à participer au developpement de cette extension.
Car c'est ensemble que nous pouvons rendre le Logiciel Libre plus intelligent.

___

## Prérequis:

Afin de profiter des dernières versions des bibliothèques Python utilisées dans OAuth2OOo, la version 2 de Python a été abandonnée au profit de **Python 3.8 minimum**.  
Cela signifie que **OAuth2OOo ne supporte plus OpenOffice et LibreOffice 6.x sous Windows depuis sa version 1.1.0**.
Je ne peux que vous conseiller **de migrer vers LibreOffice 7.x**.

Les prérequis dépendent de la **plateforme (architecture)** sur laquelle l'extension est installée:

- Si vous êtes **sous Windows (win32 or win_amd64)** vous devez utiliser **LibreOffice version 7.x minimum**.

- Si vous êtes **sous Linux (x86_64) avec une version Python de 3.8 à 3.12** vous devez utiliser **LibreOffice version 6.x ou supérieure** (LibreOffice version 7.x est fortement recommandée).

- Pour toutes les autres **plateformes / architectures (Linux, macOS... / aarch64, arm64...) ou version de Python**, vous devez:
  - Vous assurez que votre version de Python est 3.8 minimum.
  - Télécharger le fichier [requirements.txt][23].
  - Installer à l'aide de [pip][24], les paquets Python nécessaires à l'extension avec la commande:  
    `pip install requirements.txt`
  - Installer l'extension sous LibreOffice version 6.x ou supérieure.

**Sous Linux et macOS les paquets** utilisés par l'extension, peuvent s'il sont déja installé provenir du système et donc, **peuvent ne pas être à jour**.  
Afin de s'assurer que vos paquets Python sont à jour il est recommandé d'utiliser l'option **Info système** dans les Options de l'extension accessible par:  
**Outils -> Options -> Internet -> Protocole OAuth2 -> Voir journal -> Info système**  
Si des paquets obsolètes apparaissent, vous pouvez les mettre à jour avec la commande:  
`pip install --upgrade <package-name>`

Pour plus d'information voir: [Ce qui a été fait pour la version 1.3.0][25].

Si vous voulez **piloter Firefox dans Calc sous Ubuntu** alors il vous faut reinstaller Firefox à partir du PPA de Mozilla.  
Pour installer le PPA de Mozilla veuillez taper la commande:  
`sudo add-apt-repository ppa:mozillateam/ppa`

___

## Installation:

Il semble important que le fichier n'ait pas été renommé lors de son téléchargement.  
Si nécessaire, renommez-le avant de l'installer.

- ![OAuth2OOo logo][26] Installer l'extension **[OAuth2OOo.oxt][27]** [![Version][28]][27]

Redémarrez LibreOffice après l'installation.  
**Attention, redémarrer LibreOffice peut ne pas suffire.**
- **Sous Windows** pour vous assurer que LibreOffice redémarre correctement, utilisez le Gestionnaire de tâche de Windows pour vérifier qu'aucun service LibreOffice n'est visible après l'arrêt de LibreOffice (et tuez-le si ç'est le cas).
- **Sous Linux ou macOS** vous pouvez également vous assurer que LibreOffice redémarre correctement, en le lançant depuis un terminal avec la commande `soffice` et en utilisant la combinaison de touches `Ctrl + C` si après l'arrêt de LibreOffice, le terminal n'est pas actif (pas d'invité de commande).

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

![OAuth2OOo Wizard Page1 screenshot][29]

![OAuth2OOo Wizard Page2 screenshot][30]

![OAuth2OOo Wizard Page3 screenshot][31]

![OAuth2OOo Browser Page1 screenshot][32]

![OAuth2OOo Browser Page2 screenshot][33]

![OAuth2OOo Browser Page3 screenshot][34]

![OAuth2OOo Browser Page4 screenshot][35]

![OAuth2OOo Wizard Page4 screenshot][36]

Le protocole OAuth2 permet d'accéder aux ressources de serveurs, après acceptation de l'autorisation de connexion, en échangeant des jetons.

La révocation a lieu dans la gestion des applications associées à votre compte.

Plus aucun mot de passe n'est stocké dans LibreOffice.

___

## A été testé avec:

* LibreOffice 7.3.7.2 - Lubuntu 22.04 - Python version 3.10.12

* LibreOffice 7.5.4.2(x86) - Windows 10 - Python version 3.8.16 (sous Lubuntu 22.04 / VirtualBox 6.1.38)

* LibreOffice 7.4.3.2(x64) - Windows 10(x64) - Python version 3.8.15 (sous Lubuntu 22.04 / VirtualBox 6.1.38)

* **Ne fonctionne pas avec OpenOffice** voir [dysfonctionnement 128569][37]. N'ayant aucune solution, je vous encourrage d'installer **LibreOffice**.

Je vous encourage en cas de problème :confused:  
de créer un [dysfonctionnement][22]  
J'essaierai de le résoudre :smile:

___

## Historique:

### Ce qui a été fait pour la version 0.0.5:

- Ecriture d'une nouvelle interface [XWizard][38] afin de remplacer le service Wizard devenu défectueux avec les versions 6.4.x et 7.x de LibreOffice (voir [bug 132110][39]).

    Cette nouvelle interface corrige également le [bug 132661][40] et le [bug 132666][41] et permet d'accéder aux versions 6.4.x et 7.x de LibreOffice...

    De plus, ce nouveau XWizard ajoute de nouvelles fonctionnalités telles que:

    - Redimensionnement automatique de l'assistant aux dimensions de la première page affichée.
    - Déplacement automatique vers la page X à l'ouverture si possible.

- Correction d'un problème avec les jetons sans expiration (tels qu'utilisés par Dropbox) lors du test de leur validité...

- Beaucoup d'autres correctifs...

### Ce qui a été fait pour la version 0.0.6:

- Réécriture de l'assistant OAuth2 (Wizard) en essayant de suivre au mieux le [modèle MVA][42]. Cet assistant est composé de 5 pages héritant de l'interface UNO [XWizardPage][43]:

    - Page 1: [Adapteur][44] et [Vue][45]
    - Page 2: [Adapteur][46] et [Vue][47]
    - Page 3: [Adapteur][48] et [Vue][49]
    - Page 4: [Adapteur][50] et [Vue][51]
    - Page 5: [Adapteur][52] et [Vue][53]

- Réécriture des trois services UNO fournis par l'extension OAuth2OOo dans trois fichiers distincts:

    - Le service [OAuth2Service][54] implémentant l'interface décrite dans le fichier IDL [XOAuth2Service][55].
    - Le service [OAuth2Dispacher][56] implémentant l'interface UNO [XDispatchProvider][57].
    - Le service [OAuth2Handler][58] implémentant l'interface UNO [XInteractionHandler2][59].

- Réécriture de la fenêtre des options accessible par **Outils -> Options -> Internet -> Protocole OAuth2**. Cette fenêtre est composée de deux fenêtres:

    - La fenêtre de journalisation: [Adapteur][60] et [Vue][61].
    - La fenêtre des options de configuration de l'extension OAuth2OOo: [Adapteur][62] et [Vue][63].

- Réécriture d'un modèle de données unique [OAuth2Model][64] gérant l'assistant, les services, et la fenêtre des options.

- L'erreur de flux de bouclage Google a été corrigée. Voir [Dysfonctionnement #10][65]

- Utilisation pour Dropbox de leur nouvelle API avec des jetons expirables.

- Beaucoup d'autres correctifs...

### Ce qui a été fait pour la version 1.0.0:

- Portage de l'API Python [Requests][66] vers l'API LibreOffice / OpenOffice UNO. Deux interfaces UNO sont accessibles:

    - Les paramètres de requête HTTP: [com.sun.star.rest.XRequestParameter.idl][67]
    - La réponse à la requête HTTP: [com.sun.star.rest.XRequestResponse.idl][68]  

    L'interface XRequestParameter prend en charge la gestion des jetons de synchronisation ainsi que la pagination des requêtes HTTP, telles qu'elles sont utilisées dans les API HTTP Rest.

- La mise à jour et le téléchargement des fichiers est possible grâce aux méthodes ou propriétés:

    - `XOAuth2Service.download()` permettant le téléchargement de fichiers avec reprise.
    - `XOAuth2Service.upload()` permettant la mise à jour de fichiers avec reprise.
    - `XOAuth2Service.getInputStream()` pour obtenir un flux d'entrée.
    - `XRequestParameter.DataSink` pour définir un flux d'entrée.
    - `XRequestResponse.getInputStream()` pour obtenir un flux d'entrée.

- Portage de l'API Java [javax.json][69] vers l'API LibreOffice / OpenOffice UNO comme défini dans les fichiers idl: [com.sun.star.json.*][70]

    - Une fabrique de structures JSON est accessible via l'interface `getJsonBuilder()` de [XRequestParameter][67].
    - Un analyseur Json est renvoyé par l'interface `getJson()` de [XRequestResponse][68].

**Cela rend les requêtes HTTP utilisant JSON facilement utilisable dans le langage BASIC de LibreOffice.**

### Ce qui a été fait pour la version 1.0.1:

- Ecriture de 15 fonctions en AddIns de Calc comme décrit dans les fichiers suivants:

    - Le fichier [OAuth2Plugin.idl][71] qui declare à UNO les nouvelles interfaces.
    - Le fichier [CalcAddIns.xcu][72] qui rend disponible ces nouvelles interface dans le liste des fonctions de Calc.
    - Le fichier [OAuth2Plugin.py][73] qui est l'implementation du service UNO `com.sun.star.auth.Oauth2Plugin` founissant ces nouvelles interfaces.
    - Le fichier [plugin.py][74] qui est la bibliotheque implementant les interface de ce nouveau service UNO.

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

### Ce qui a été fait pour la version 1.1.0:

- **Fin du support de Python 2.x et donc d'OpenOffice**.

- Intégration de [Selenium][18] version 4.10 dans l'extension afin de rendre **LibreOffice capable de piloter un navigateur via des formules Calc** insérées dans une feuille de calcul.

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

- Correction d'un problème dans [l'implémentation][77] de l'interface [com.sun.star.rest.XRequestParameter][67] ne permettant pas de créer des objets JSON vides (ie : "Object": {} ) comme demandé par l'API Microsoft Graph.

### Ce qui a été fait pour la version 1.1.2:

- Modification des fichiers idl: [XRequestParameter.idl][67] et [XRequestResponse.idl][68] et des implementations python sous jacente: [requestparameter.py][77] et [requestresponse.py][78] afin de rendre possible les requêtes **POST** avec l'encodage **application/x-www-form-urlencoded**. Voir [dysfonctionnement #13][79].

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

- Ajout d'une nouvelle méthode `isAuthorized()` à l'interface [XOAuth2Service][55] prise en charge par le service [OAuth2Service][84]. Cette méthode permet de lancer l'assistant de configuration OAuth2 si l'utilisateur n'est pas autorisé.

### Ce qui a été fait pour la version 1.2.2:

- Correction d'une erreur lors de l'actualisation des jetons OAuth2.

### Ce qui a été fait pour la version 1.2.3:

- Correction d'une erreur sur isAuthorized() du OAuth2Service.

### Ce qui a été fait pour la version 1.2.4:

- Mise à jour des paquets python embarqués.

### Ce qui a été fait pour la version 1.3.0:

- Utilisation de la nouvelle version 3.6.2 de [pyRdfa3][85].
- Tous les paquets Python nécessaires à l'extension sont désormais enregistrés dans un fichier [requirements.txt][23] suivant la [PEP 508][86].
- Désormais si vous n'êtes pas sous Windows alors les paquets Python nécessaires à l'extension peuvent être facilement installés avec la commande:  
  `pip install requirements.txt`
- Simplification de la section [Prérequis][87].
- De nombreuses corrections...

### Ce qui a été fait pour la version 1.3.1:

- Correction de la propriété `Headers` dans l'[implémentation][78] de l'interface UNO [XRequestResponse][68] permettant d'obtenir les en-têtes d'une réponse HTTP.
- De nombreuses corrections...

### Ce qui a été fait pour la version 1.3.2:

- Intégration des binaires Python 3.8 pour Linux x86_64 et Darwin x86_64, afin d'être compatible avec la version de LibreOffice 24.2.x sous Linux, pour les paquets `lxml`, `ijson`, `cffi` et `charset-normalizer`.
- Ouverture du dysfonctionnement [#159988][88] pour impossibilité d'importer des bibliothèques Python contenant des fichiers binaires avec LibreOffice 24.2.x sous Linux.

### Ce qui a été fait pour la version 1.3.3:

- Mise en oeuvre d'une solution de contournement pour le dysfonctionnement [#159988][88] dont la résolution risque de prendre du temps.

### Ce qui a été fait pour la version 1.3.4:

- Mise à jour du paquet [Python Idna][89] vers la version 3.7 afin de répondre à l'[alerte de vulnérabilité de sécurité][90].
- Quelques corrections...

### Ce qui a été fait pour la version 1.3.5:

- Mise à jour du paquet [Python tqdm][91] vers la version 4.66.4 afin de répondre à l'[alerte de vulnérabilité de sécurité][92].
- Mise à jour du paquet [Python requests][93] vers la version 2.32.3 afin de répondre à l'[alerte de vulnérabilité de sécurité][94].
- Afin d'éviter tout conflit avec le paquet [Python oauth2][95], le dossier mis dans le chemin python par l'extension a été renommé `oauth20`. Cela devrait également résoudre le [dysfonctionnement n°10][96].
- Quelques corrections...

### Ce qui a été fait pour la version 1.3.6:

- Mise à jour du paquet [Python beautifulsoup][97] vers la version 4.12.3.
- Mise à jour du paquet [Python certifi][98] vers la version 2024.7.4.
- Ajout des fichiers binaires pour les version 3.9, 3.11 et 3.12 de Python/Manylinux pour le paquet [Python cffi][99] version 1.16.0.
- Mise à jour du paquet [Python charset-normalizer][100] vers la version 3.3.2.
- Mise à jour du paquet [Python exceptiongroup][101] vers la version 1.2.2.
- Mise à jour du paquet [Python extruct][102] vers la version 0.17.0.
- Mise à jour du paquet [Python html-text][103] vers la version 0.6.2.
- Mise à jour du paquet [Python ijson][104] vers la version 3.3.0.
- Mise à jour du paquet [Python jsonpath_ng][105] vers la version 1.6.1.
- Mise à jour du paquet [Python lxml][106] vers la version 5.2.2.
- Ajout du paquet [Python lxml-html-clean][107] version 0.2.0.
- Mise à jour du paquet [Python packaging][108] vers la version 24.1.
- Mise à jour du paquet [Python prasel][109] vers la version 1.9.1.
- Mise à jour du paquet [Python pycparser][110] vers la version 2.22.
- Mise à jour du paquet [Python pyparsing][111] vers la version 3.1.2.
- Mise à jour du paquet [Python pyRdfa3][112] vers la version 3.6.4.
- Mise à jour du paquet [Python python-dotenv][113] vers la version 1.0.1.
- Mise à jour du paquet [Python selenium][114] vers la version 4.23.1.
- Mise à jour du paquet [Python setuptools][115] vers la version 72.1.0 afin de répondre à l'[alerte de vulnérabilité de sécurité][116].
- Mise à jour du paquet [Python sniffio][117] vers la version 1.3.1.
- Mise à jour du paquet [Python trio][118] vers la version 0.26.0.
- Ajout du paquet [Python typing-extensions][119] version 4.12.2.
- Mise à jour du paquet [Python urllib3][120] vers la version 2.2.2.
- Mise à jour du paquet [Python validators][121] vers la version 0.33.0.
- Mise à jour du paquet [Python w3lib][122] vers la version 2.2.1.
- Mise à jour du paquet [Python webdriver-manager][123] vers la version 4.0.2.
- Ajout du paquet [Python websocket-client][124] version 1.8.0.

La mise à jour de tous ces paquets Python devrait permettre d'utiliser Python 3.8, 3.9, 3.10, 3.11 et 3.12 sous l'architecture ManyLinux x86_64.  
Pour les architectures win32 et win_amd64, seule la version 3.8 de Python est prise en charge. Cela signifie, puisque Python est intégré à LibreOffice pour ces architectures, que seules les versions 7.x et 24.x de LibreOffice sont prises en charge.  
Si votre architecture n'est pas encore supportée par OAuth2OOo (Mac OSX, arm...), je vous conseille d'ouvrir un [dysfonctionnement][22] pour que je puisse ajouter les fichiers binaires manquants.

### Que reste-t-il à faire pour la version 1.3.6:

- Ajouter de nouvelles langue pour l'internationalisation...

- Tout ce qui est bienvenu...

[1]: </img/oauth2.svg#collapse>
[2]: <https://prrvchr.github.io/OAuth2OOo/>
[3]: <https://prrvchr.github.io/OAuth2OOo>
[4]: <https://prrvchr.github.io/OAuth2OOo/source/OAuth2OOo/registration/TermsOfUse_fr>
[5]: <https://prrvchr.github.io/OAuth2OOo/source/OAuth2OOo/registration/PrivacyPolicy_fr>
[6]: <https://prrvchr.github.io/OAuth2OOo/README_fr#ce-qui-a-été-fait-pour-la-version-136>
[7]: <https://prrvchr.github.io/README_fr>
[8]: <https://fr.libreoffice.org/download/telecharger-libreoffice/>
[9]: <https://www.openoffice.org/fr/Telecharger/>
[10]: <https://fr.wikipedia.org/wiki/OAuth>
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
[25]: <https://prrvchr.github.io/OAuth2OOo/README_fr#ce-qui-a-%C3%A9t%C3%A9-fait-pour-la-version-130>
[26]: <https://prrvchr.github.io/OAuth2OOo/img/OAuth2OOo.svg#middle>
[27]: <https://github.com/prrvchr/OAuth2OOo/releases/latest/download/OAuth2OOo.oxt>
[28]: <https://img.shields.io/github/downloads/prrvchr/OAuth2OOo/latest/total?label=v1.3.6#right>
[29]: <https://prrvchr.github.io/OAuth2OOo/img/OAuth2Wizard1_fr.png>
[30]: <https://prrvchr.github.io/OAuth2OOo/img/OAuth2Wizard2_fr.png>
[31]: <https://prrvchr.github.io/OAuth2OOo/img/OAuth2Wizard3_fr.png>
[32]: <https://prrvchr.github.io/OAuth2OOo/img/OAuth2Wizard4_fr.png>
[33]: <https://prrvchr.github.io/OAuth2OOo/img/OAuth2Wizard5_fr.png>
[34]: <https://prrvchr.github.io/OAuth2OOo/img/OAuth2Wizard6_fr.png>
[35]: <https://prrvchr.github.io/OAuth2OOo/img/OAuth2Wizard7_fr.png>
[36]: <https://prrvchr.github.io/OAuth2OOo/img/OAuth2Wizard8_fr.png>
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
[83]: <https://prrvchr.github.io/OAuth2OOo/source/OAuth2OOo/registration/PrivacyPolicy_fr#nature-et-étendue-des-droits-sur-vos-données>
[84]: <https://github.com/prrvchr/OAuth2OOo/blob/master/uno/rdb/idl/com/sun/star/auth/OAuth2Service.idl>
[85]: <https://github.com/prrvchr/pyrdfa3>
[86]: <https://peps.python.org/pep-0508/>
[87]: <https://prrvchr.github.io/OAuth2OOo/README_fr#pr%C3%A9requis>
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
