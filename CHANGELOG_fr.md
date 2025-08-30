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
# [![OAuth2OOo logo][1]][2] Historique

**This [document][3] in English.**

Concernant l'installation, la configuration et l'utilisation, veuillez consulter la **[documentation][4]**.

### Ce qui a été fait pour la version 0.0.5:

- Ecriture d'une nouvelle interface [XWizard][5] afin de remplacer le service Wizard devenu défectueux avec les versions 6.4.x et 7.x de LibreOffice (voir [bug 132110][6]).

    Cette nouvelle interface corrige également le [bug 132661][7] et le [bug 132666][8] et permet d'accéder aux versions 6.4.x et 7.x de LibreOffice...

    De plus, ce nouveau XWizard ajoute de nouvelles fonctionnalités telles que:

    - Redimensionnement automatique de l'assistant aux dimensions de la première page affichée.
    - Déplacement automatique vers la page X à l'ouverture si possible.

- Correction d'un problème avec les jetons sans expiration (tels qu'utilisés par Dropbox) lors du test de leur validité...

- Beaucoup d'autres correctifs...

### Ce qui a été fait pour la version 0.0.6:

- Réécriture de l'assistant OAuth2 (Wizard) en essayant de suivre au mieux le [modèle MVA][9]. Cet assistant est composé de 5 pages héritant de l'interface UNO [XWizardPage][10]:

    - Page 1: [Adapteur][11] et [Vue][12]
    - Page 2: [Adapteur][13] et [Vue][14]
    - Page 3: [Adapteur][15] et [Vue][16]
    - Page 4: [Adapteur][17] et [Vue][18]
    - Page 5: [Adapteur][19] et [Vue][20]

- Réécriture des trois services UNO fournis par l'extension OAuth2OOo dans trois fichiers distincts:

    - Le service [OAuth2Service][21] implémentant l'interface décrite dans le fichier IDL [XOAuth2Service][22].
    - Le service [OAuth2Dispacher][23] implémentant l'interface UNO [XDispatchProvider][24].
    - Le service [OAuth2Handler][25] implémentant l'interface UNO [XInteractionHandler2][26].

- Réécriture de la fenêtre des options accessible par **Outils -> Options -> Internet -> Protocole OAuth2**. Cette fenêtre est composée de deux fenêtres:

    - La fenêtre de journalisation: [Adapteur][27] et [Vue][28].
    - La fenêtre des options de configuration de l'extension OAuth2OOo: [Adapteur][29] et [Vue][30].

- Réécriture d'un modèle de données unique [OAuth2Model][31] gérant l'assistant, les services, et la fenêtre des options.

- L'erreur de flux de bouclage Google a été corrigée. Voir [Dysfonctionnement #10][32]

- Utilisation pour Dropbox de leur nouvelle API avec des jetons expirables.

- Beaucoup d'autres correctifs...

### Ce qui a été fait pour la version 1.0.0:

- Portage de l'API Python [Requests][33] vers l'API LibreOffice / OpenOffice UNO. Deux interfaces UNO sont accessibles:

    - Les paramètres de requête HTTP: [com.sun.star.rest.XRequestParameter.idl][34]
    - La réponse à la requête HTTP: [com.sun.star.rest.XRequestResponse.idl][35]  

    L'interface XRequestParameter prend en charge la gestion des jetons de synchronisation ainsi que la pagination des requêtes HTTP, telles qu'elles sont utilisées dans les API HTTP Rest.

- La mise à jour et le téléchargement des fichiers est possible grâce aux méthodes ou propriétés:

    - `XOAuth2Service.download()` permettant le téléchargement de fichiers avec reprise.
    - `XOAuth2Service.upload()` permettant la mise à jour de fichiers avec reprise.
    - `XOAuth2Service.getInputStream()` pour obtenir un flux d'entrée.
    - `XRequestParameter.DataSink` pour définir un flux d'entrée.
    - `XRequestResponse.getInputStream()` pour obtenir un flux d'entrée.

- Portage de l'API Java [javax.json][36] vers l'API LibreOffice / OpenOffice UNO comme défini dans les fichiers idl: [com.sun.star.json.*][37]

    - Une fabrique de structures JSON est accessible via l'interface `getJsonBuilder()` de [XRequestParameter][34].
    - Un analyseur Json est renvoyé par l'interface `getJson()` de [XRequestResponse][35].

**Cela rend les requêtes HTTP utilisant JSON facilement utilisable dans le langage BASIC de LibreOffice.**

### Ce qui a été fait pour la version 1.0.1:

- Ecriture de 15 fonctions en AddIns de Calc comme décrit dans les fichiers suivants:

    - Le fichier [OAuth2Plugin.idl][38] qui declare à UNO les nouvelles interfaces.
    - Le fichier [CalcAddIns.xcu][39] qui rend disponible ces nouvelles interface dans le liste des fonctions de Calc.
    - Le fichier [OAuth2Plugin.py][40] qui est l'implementation du service UNO `com.sun.star.auth.Oauth2Plugin` founissant ces nouvelles interfaces.
    - Le fichier [plugin.py][41] qui est la bibliotheque implementant les interface de ce nouveau service UNO.

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

- Intégration de [Selenium][42] version 4.10 dans l'extension afin de rendre **LibreOffice capable de piloter un navigateur via des formules Calc** insérées dans une feuille de calcul.

- Utilisation de [webdriver_manager][43] version 3.8.6 permettant d'automatiser l'installation du [WebDriver][44] du navigateur.

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

- Correction d'un problème dans [l'implémentation][45] de l'interface [com.sun.star.rest.XRequestParameter][34] ne permettant pas de créer des objets JSON vides (ie : "Object": {} ) comme demandé par l'API Microsoft Graph.

### Ce qui a été fait pour la version 1.1.2:

- Modification des fichiers idl: [XRequestParameter.idl][34] et [XRequestResponse.idl][35] et des implementations python sous jacente: [requestparameter.py][45] et [requestresponse.py][46] afin de rendre possible les requêtes **POST** avec l'encodage **application/x-www-form-urlencoded**. Voir [dysfonctionnement #13][47].

- 3 macros en BASIC: `ChatGPTRequest`, `HTTPGetRequest` et `HTTPPostRequest` sont disponible dans: **Outils -> Macros -> Exécuter la macro... -> Mes macros -> OAuth2OOo**. Attention, ces macros **ne fonctionneront pas si aucun document n'est ouvert** (je ne sais pas pourquoi?)...

- Désormais, à chaque push, un [workflow effectue un scan][48] du code avec [Fluid Attacks][49]. Ceci a été mis en place pour suivre le [Cloud Application Security Assessment][50] (CASA) et répondre aux exigences de revalidation de l'extension OAuth2OOo avec Google.

- Pour les mêmes raisons, la [Politique de Protection des Données][51] a été modifiée afin de préciser la [Nature et l'étendue des droits sur vos données][52].

### Ce qui a été fait pour la version 1.2.0:

- Il existe désormais deux méthodes pour créer le service [OAuth2Service][53] qui sont :
  - `create()` sans paramètre, renvoie une instance du service.
  - `createWithOAuth2([in] string sUrl, [in] string sUser)` avec une Url et l'adresse de l'utilisateur, renvoie une instance du service avec le protocole OAuth2.  
    Dans sa deuxième forme, l'assistant d'autorisation OAuth2 (Wizard) se lancera automatiquement si l'étendue des droits de l'Url n'a pas encore été accordée par l'utilisateur (ie : première connexion).  
    Si tel est le cas et que l'assistant est abandonné, une valeur nulle sera renvoyée à la place du service demandé.

- Deux macros BASIC: `GoogleAPIRequest` et `GraphAPIRequest` permettent d'effectuer des requêtes HTTP sur les API de Google Contact et Microsoft Graph.  
  Le protocole OAuth2 indispensable à l'utilisation de ces API est intégré de manière automatique et transparente aux requêtes HTTP. Vous n'aurez pas à vous en soucier.

### Ce qui a été fait pour la version 1.2.1:

- Ajout d'une nouvelle méthode `isAuthorized()` à l'interface [XOAuth2Service][22] prise en charge par le service [OAuth2Service][53]. Cette méthode permet de lancer l'assistant de configuration OAuth2 si l'utilisateur n'est pas autorisé.

### Ce qui a été fait pour la version 1.2.2:

- Correction d'une erreur lors de l'actualisation des jetons OAuth2.

### Ce qui a été fait pour la version 1.2.3:

- Correction d'une erreur sur isAuthorized() du OAuth2Service.

### Ce qui a été fait pour la version 1.2.4:

- Mise à jour des paquets python embarqués.

### Ce qui a été fait pour la version 1.3.0:

- Utilisation de la nouvelle version 3.6.2 de [pyRdfa3][54].
- Tous les paquets Python nécessaires à l'extension sont désormais enregistrés dans un fichier [requirements.txt][55] suivant la [PEP 508][56].
- Désormais si vous n'êtes pas sous Windows alors les paquets Python nécessaires à l'extension peuvent être facilement installés avec la commande:  
  `sudo -i pip3 install requirements.txt`
- Simplification de la section [Prérequis][57].
- De nombreuses corrections...

### Ce qui a été fait pour la version 1.3.1:

- Correction de la propriété `Headers` dans l'[implémentation][46] de l'interface UNO [XRequestResponse][35] permettant d'obtenir les en-têtes d'une réponse HTTP.
- De nombreuses corrections...

### Ce qui a été fait pour la version 1.3.2:

- Intégration des binaires Python 3.8 pour Linux x86_64 et Darwin x86_64, afin d'être compatible avec la version de LibreOffice 24.2.x sous Linux, pour les paquets `lxml`, `ijson`, `cffi` et `charset-normalizer`.
- Ouverture du dysfonctionnement [#159988][58] pour impossibilité d'importer des bibliothèques Python contenant des fichiers binaires avec LibreOffice 24.2.x sous Linux.

### Ce qui a été fait pour la version 1.3.3:

- Mise en oeuvre d'une solution de contournement pour le dysfonctionnement [#159988][58] dont la résolution risque de prendre du temps.

### Ce qui a été fait pour la version 1.3.4:

- Mise à jour du paquet [Python Idna][59] vers la version 3.7 afin de répondre à l'[alerte de vulnérabilité de sécurité][60].
- Quelques corrections...

### Ce qui a été fait pour la version 1.3.5:

- Mise à jour du paquet [Python tqdm][61] vers la version 4.66.4 afin de répondre à l'[alerte de vulnérabilité de sécurité][62].
- Mise à jour du paquet [Python requests][63] vers la version 2.32.3 afin de répondre à l'[alerte de vulnérabilité de sécurité][64].
- Afin d'éviter tout conflit avec le paquet [Python oauth2][65], le dossier mis dans le chemin python par l'extension a été renommé `oauth20`. Cela devrait également résoudre le [dysfonctionnement n°10][66].
- Quelques corrections...

### Ce qui a été fait pour la version 1.3.6:

- Mise à jour du paquet [Python beautifulsoup][67] vers la version 4.12.3.
- Mise à jour du paquet [Python certifi][68] vers la version 2024.7.4.
- Ajout des fichiers binaires pour les version 3.9, 3.11 et 3.12 de Python/Manylinux pour le paquet [Python cffi][69] version 1.16.0.
- Mise à jour du paquet [Python charset-normalizer][70] vers la version 3.3.2.
- Mise à jour du paquet [Python exceptiongroup][71] vers la version 1.2.2.
- Mise à jour du paquet [Python extruct][72] vers la version 0.17.0.
- Mise à jour du paquet [Python html-text][73] vers la version 0.6.2.
- Mise à jour du paquet [Python ijson][74] vers la version 3.3.0.
- Mise à jour du paquet [Python jsonpath_ng][75] vers la version 1.6.1.
- Mise à jour du paquet [Python lxml][76] vers la version 5.2.2.
- Ajout du paquet [Python lxml-html-clean][77] version 0.2.0.
- Mise à jour du paquet [Python packaging][78] vers la version 24.1.
- Mise à jour du paquet [Python prasel][79] vers la version 1.9.1.
- Mise à jour du paquet [Python pycparser][80] vers la version 2.22.
- Mise à jour du paquet [Python pyparsing][81] vers la version 3.1.2.
- Mise à jour du paquet [Python pyRdfa3][82] vers la version 3.6.4.
- Mise à jour du paquet [Python python-dotenv][83] vers la version 1.0.1.
- Mise à jour du paquet [Python selenium][84] vers la version 4.23.1.
- Mise à jour du paquet [Python setuptools][85] vers la version 72.1.0 afin de répondre à l'[alerte de vulnérabilité de sécurité][86].
- Mise à jour du paquet [Python sniffio][87] vers la version 1.3.1.
- Mise à jour du paquet [Python trio][88] vers la version 0.26.0.
- Ajout du paquet [Python typing-extensions][89] version 4.12.2.
- Mise à jour du paquet [Python urllib3][90] vers la version 2.2.2.
- Mise à jour du paquet [Python validators][91] vers la version 0.33.0.
- Mise à jour du paquet [Python w3lib][92] vers la version 2.2.1.
- Mise à jour du paquet [Python webdriver-manager][93] vers la version 4.0.2.
- Ajout du paquet [Python websocket-client][94] version 1.8.0.

La mise à jour de tous ces paquets Python devrait permettre d'utiliser Python 3.8, 3.9, 3.10, 3.11 et 3.12 sous l'architecture ManyLinux x86_64.  
Pour les architectures win32 et win_amd64, seule la version 3.8 de Python est prise en charge. Cela signifie, puisque Python est intégré à LibreOffice pour ces architectures, que seules les versions 7.x et 24.x de LibreOffice sont prises en charge.  
Si votre architecture n'est pas encore supportée par OAuth2OOo (Mac OSX, arm...), je vous conseille d'ouvrir un [dysfonctionnement][95] pour que je puisse ajouter les fichiers binaires manquants.

### Ce qui a été fait pour la version 1.3.7:

- Mise à jour du paquet [Python attrs][96] vers la version 24.2.0.
- Mise à jour du paquet [Python cffi][69] vers la version 1.17.0.
- Mise à jour du paquet [Python idna][59] vers la version 3.8.
- Mise à jour du paquet [Python lxml][76] vers la version 5.3.0.
- Mise à jour du paquet [Python pyparsing][81] vers la version 3.1.4.
- Mise à jour du paquet [Python setuptools][85] vers la version 73.0.1.
- Mise à jour du paquet [Python soupsieve][97] vers la version 2.6.
- Mise à jour du paquet [Python tqdm][61] vers la version 4.66.5.
- Mise à jour du paquet [Python trio][88] vers la version 0.26.2.
- La journalisation accessible dans les options de l’extension s’affiche désormais correctement sous Windows.
- Les modifications apportées aux options de l'extension, qui nécessitent un redémarrage de LibreOffice, entraîneront l'affichage d'un message.
- Afin de fonctionner avec LibreOffice 24.8.x pour Windows (32 et 64 bits), ajout des fichiers binaires, pour Python version 3.9 et les architectures win32 ou win_adm64, à tous les paquets Python inclus dans l'extension.

### Ce qui a été fait pour la version 1.3.8:

- Modification des options de l'extension accessibles via : **Outils -> Options... -> Internet -> Protocole OAuth2** afin de respecter la nouvelle charte graphique.

### Ce qui a été fait pour la version 1.3.9:

- Ajout d'une nouvelle méthode `fromJson()` à l'interface [XRequestParameter][34] pour faciliter l'exécution d'une requête HTTP à partir de paramètres provenant de fichiers de configuration LibreOffice (ie: fichiers XML xcu/xcs).
- Préparation à la migration des périmètres de droits spécifiques aux connexions aux serveurs de Google.
- Quelques corrections...

### Ce qui a été fait pour la version 1.4.0:

- Toutes les données nécessaires à la gestion du flux du code d'autorisation OAuth2 sont désormais stockées dans le fichier de configuration de LibreOffice [Options.xcu][98].
- Il est désormais possible d'avoir une uri de redirection OAuth2 (ie: `redirect_uri`) en mode https comme requis par certaines API tierces, grâce au certificat SSL de Github et à JavaScript, voir le fichier [OAuth2Redirect.md][99].
- Le port TCP/IP permettant la réception du code d'autorisation des GAFA est désormais choisi au hasard parmi les ports libres (ie: plus de problèmes de conflits).
- Il est possible de construire l'archive de l'extension (ie: le fichier oxt) avec l'utilitaire [Apache Ant][100] et le fichier script [build.xml][101].
- L'extension refusera de s'installer sous OpenOffice quelle que soit la version ou LibreOffice autre que 7.x ou supérieur.
- La gestion du flux de données OAuth2 à l'aide de la copie du code d'autorisation a été supprimée. Seule la réception du code d'autorisation via HTTP est désormais prise en charge.
- Deux méthodes ont été ajoutées à l'[interface XOAuth2Service.idl][22]:
  - `isRegisteredUrl` pour savoir si une URL est enregistrée dans la configuration OAuth2.
  - `getTokenWithParameters` pour obtenir un jeton OAuth2 au format donné par les paramètres.
- Ajout des fichiers binaires nécessaires aux bibliothèques Python pour fonctionner sous Linux et LibreOffice 24.8 (ie: Python 3.9).
- De nombreuses corrections...

### Ce qui a été fait pour la version 1.4.1:

- Mise à jour du paquet [Python attrs][96] vers la version 25.1.0.
- Mise à jour du paquet [Python beautifulsoup4][67] vers la version 4.13.3.
- Mise à jour du paquet [Python certifi][68] vers la version 2025.1.31.
- Mise à jour du paquet [Python cffi][69] vers la version 1.17.1.
- Mise à jour du paquet [Python charset-normalizer][70] vers la version 3.4.1.
- Mise à jour du paquet [Python extruct][72] vers la version 0.18.0.
- Mise à jour du paquet [Python html-text][73] vers la version 0.7.0.
- Mise à jour du paquet [Python idna][59] vers la version 3.10.
- Mise à jour du paquet [Python isodate][102] vers la version 0.7.2.
- Mise à jour du paquet [Python jsonpath_ng][75] vers la version 1.7.0.
- Mise à jour du paquet [Python lxml][76] vers la version 5.3.1.
- Mise à jour du paquet [Python packaging][78] vers la version 24.2.
- Mise à jour du paquet [Python parsel][79] vers la version 1.10.0.
- Mise à jour du paquet [Python pyparsing][81] vers la version 3.2.1.
- Mise à jour du paquet [Python rdflib][103] vers la version 7.1.3.
- Mise à jour du paquet [Python selenium][84] vers la version 4.28.1.
- Mise à jour du paquet [Python setuptools][85] vers la version 75.8.0.
- Mise à jour du paquet [Python six][104] vers la version 1.17.0.
- Mise à jour du paquet [Python tqdm][61] vers la version 4.67.1.
- Mise à jour du paquet [Python trio][88] vers la version 0.29.0.
- Mise à jour du paquet [Python urllib3][90] vers la version 2.3.0.
- Mise à jour du paquet [Python validators][91] vers la version 0.34.0.
- Mise à jour du paquet [Python w3lib][92] vers la version 2.3.1.
- Support de Python version 3.13.

### Ce qui a été fait pour la version 1.5.0:

- Mise à jour du paquet [Python packaging][78] vers la version 25.0.
- Rétrogradage du paquet [Python setuptools][85] vers la version 75.3.2, afin d'assurer la prise en charge de Python 3.8.
- Mise à jour du paquet [Python h11][105] vers la version 0.16.0 afin de répondre à l'alerte de securité [Dependabot #16][106]
- Déploiement de l'enregistrement passif permettant une installation beaucoup plus rapide des extensions et de différencier les services UNO enregistrés de ceux fournis par une implémentation Java ou Python. Cet enregistrement passif est assuré par l'extension [LOEclipse][107] via les [PR#152][108] et [PR#157][109].
- Modification de [LOEclipse][107] pour prendre en charge le nouveau format de fichier `rdb` produit par l'utilitaire de compilation `unoidl-write`. Les fichiers `idl` ont été mis à jour pour prendre en charge les deux outils de compilation disponibles: idlc et unoidl-write.
- Il est désormais possible de créer le fichier oxt de l'extension OAuth2OOo uniquement avec Apache Ant et une copie du dépôt GitHub. La section [Comment créer l'extension][110] a été ajoutée à la documentation.
- Implémentation de [PEP 570][111] dans la [journalisation][112] pour prendre en charge les arguments multiples uniques.

### Ce qui a été fait pour la version 1.5.1:

Ajout d'une macro BASIC [GithubDownloadRequest][113] pour télécharger la dernière version de OAuth2OOo à partir des révisions sur le site Github.  
Pour permettre le téléchargement sur Github, cette macro utilise deux requêtes HTTP, une pour initialiser une session avec des cookies et l'autre pour effectuer le téléchargement.  
Cela pourrait m'aider à trouver une solution pour permettre la mise à jour automatique des extensions dans LibreOffice à partir des révisions Github.

### Ce qui a été fait pour la version 1.5.2:

- Correction de la macro BASIC [GithubDownloadRequest][113].
- Correction de lien vers l'historique dans le fichier `README_fr.md`.
- Vous pouvez à nouveau utiliser une URL pour lancer l'assistant OAuth2 dans les options de l'extension.
- La mise à jour automatique des extensions a été corrigée, voir [tdf#159775][114], merci à `Mike Kaganski`. Ceci sera bientôt disponible dans LibreOffice 25.8.x.
- Support de LibreOffice 25.2.x et 25.8.x sous Windows 64 bits. Voir [issue#25][115].

### Ce qui a été fait pour la version 1.5.3:

- Toutes les méthodes exécutées en arrière-plan utilisent désormais le service UNO [com.sun.star.awt.AsyncCallback][116] pour le rappel.
- Des petites corrections.

### Que reste-t-il à faire pour la version 1.5.3:

- Ajouter de nouvelles langue pour l'internationalisation...

- Tout ce qui est bienvenu...

[1]: </img/oauth2.svg#collapse>
[2]: <https://prrvchr.github.io/OAuth2OOo/>
[3]: <https://prrvchr.github.io/OAuth2OOo/CHANGELOG>
[4]: <https://prrvchr.github.io/OAuth2OOo/README_fr>
[5]: <https://github.com/prrvchr/OAuth2OOo/blob/master/uno/lib/uno/wizard/wizard.py>
[6]: <https://bugs.documentfoundation.org/show_bug.cgi?id=132110>
[7]: <https://bugs.documentfoundation.org/show_bug.cgi?id=132661>
[8]: <https://bugs.documentfoundation.org/show_bug.cgi?id=132666>
[9]: <https://en.wikipedia.org/wiki/Model%E2%80%93view%E2%80%93adapter>
[10]: <https://www.openoffice.org/api/docs/common/ref/com/sun/star/ui/dialogs/XWizardPage.html>
[11]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/service/pythonpath/oauth20/window/page1/oauth2manager.py>
[12]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/service/pythonpath/oauth20/window/page1/oauth2view.py>
[13]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/service/pythonpath/oauth20/window/page2/oauth2manager.py>
[14]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/service/pythonpath/oauth20/window/page2/oauth2view.py>
[15]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/service/pythonpath/oauth20/window/page3/oauth2manager.py>
[16]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/service/pythonpath/oauth20/window/page3/oauth2view.py>
[17]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/service/pythonpath/oauth20/window/page4/oauth2manager.py>
[18]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/service/pythonpath/oauth20/window/page4/oauth2view.py>
[19]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/service/pythonpath/oauth20/window/page5/oauth2manager.py>
[20]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/service/pythonpath/oauth20/window/page5/oauth2view.py>
[21]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/service/OAuth2Service.py>
[22]: <https://github.com/prrvchr/OAuth2OOo/blob/master/uno/rdb/idl/com/sun/star/auth/XOAuth2Service.idl>
[23]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/service/OAuth2Dispatcher.py>
[24]: <https://www.openoffice.org/api/docs/common/ref/com/sun/star/frame/XDispatchProvider.html>
[25]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/service/OAuth2Handler.py>
[26]: <https://www.openoffice.org/api/docs/common/ref/com/sun/star/task/XInteractionHandler2.html>
[27]: <https://github.com/prrvchr/OAuth2OOo/blob/master/uno/lib/uno/logger/logmanager.py>
[28]: <https://github.com/prrvchr/OAuth2OOo/blob/master/uno/lib/uno/logger/logview.py>
[29]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/service/pythonpath/oauth20/options/optionsmanager.py>
[30]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/service/pythonpath/oauth20/options/optionsview.py>
[31]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/service/pythonpath/oauth20/oauth2model.py>
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
[45]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/service/pythonpath/oauth20/requestparameter.py>
[46]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/service/pythonpath/oauth20/requestresponse.py>
[47]: <https://github.com/prrvchr/OAuth2OOo/issues/13>
[48]: <https://github.com/prrvchr/OAuth2OOo/actions/workflows/dev.yml>
[49]: <https://github.com/fluidattacks>
[50]: <https://appdefensealliance.dev/casa/tier-2/tier2-overview>
[51]: <https://prrvchr.github.io/OAuth2OOo/source/OAuth2OOo/registration/PrivacyPolicy_fr>
[52]: <https://prrvchr.github.io/OAuth2OOo/source/OAuth2OOo/registration/PrivacyPolicy_fr#nature-et-étendue-des-droits-sur-vos-données>
[53]: <https://github.com/prrvchr/OAuth2OOo/blob/master/uno/rdb/idl/com/sun/star/auth/OAuth2Service.idl>
[54]: <https://github.com/prrvchr/pyrdfa3>
[55]: <https://github.com/prrvchr/OAuth2OOo/releases/latest/download/requirements.txt>
[56]: <https://peps.python.org/pep-0508/>
[57]: <https://prrvchr.github.io/OAuth2OOo/README_fr#pr%C3%A9requis>
[58]: <https://bugs.documentfoundation.org/show_bug.cgi?id=159988>
[59]: <https://pypi.org/project/idna/>
[60]: <https://github.com/prrvchr/OAuth2OOo/security/dependabot/5>
[61]: <https://pypi.org/project/tqdm/>
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
[107]: <https://github.com/LibreOffice/loeclipse>
[108]: <https://github.com/LibreOffice/loeclipse/pull/152>
[109]: <https://github.com/LibreOffice/loeclipse/pull/157>
[110]: <https://prrvchr.github.io/OAuth2OOo/README_fr#comment-cr%C3%A9er-lextension>
[111]: <https://peps.python.org/pep-0570/>
[112]: <https://github.com/prrvchr/OAuth2OOo/blob/master/uno/lib/uno/logger/logwrapper.py#L109>
[113]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/OAuth2OOo/GithubDownloadRequest.xba>
[114]: <https://bugs.documentfoundation.org/show_bug.cgi?id=159775>
[115]: <https://github.com/prrvchr/OAuth2OOo/issues/25>
[116]: <https://www.openoffice.org/api/docs/common/ref/com/sun/star/awt/AsyncCallback.html>
