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

**This [document][3] in english.**

**L'utilisation de ce logiciel vous soumet à nos [Conditions d'Utilisation][4] et à notre [Politique de Protection des Données][5].**

# version [1.6.0][6]

## Introduction:

**OAuth2OOo** fait partie d'une [Suite][7] d'extensions [LibreOffice][8] ~~et/ou [OpenOffice][9]~~ permettant de vous offrir des services inovants dans ces suites bureautique.

Cette extension est l'implémentation du [protocole OAuth 2.0][10]. Protocole permettant d'obtenir votre consentement pour qu'une application puisse accéder à vos données présentes chez les GAFA.

Elle permet d'**exécuter des requêtes HTTP** en [BASIC][11] et fournit les macros suivantes à titre d'exemple:
- [HTTPGetRequest][12]
- [HTTPPostRequest][13]
- [ChatGPTRequest][14]
- [GoogleAPIRequest][15]
- [GraphAPIRequest][16]
- [GithubDownloadRequest][17]

Si au préalable vous ouvrez un document, vous pouvez les lancer par:  
**Outils -> Macros -> Exécuter la macro... -> Mes macros -> OAuth2OOo -> `nom-macro` -> Main -> Exécuter**

Elle permet également de **récupérer des données Internet dans une feuille Calc**. Voir les fichiers Calc suivants à titre d'exemple:
- [LDLC MacBook Pro.ods][18]
- [LDLC Asus Zenbook.ods][19]

Et enfin, elle permet de **piloter Firefox par un fichier Calc** (ou tout autre navigateur pris en charge par [Selenium][20]). Voir les fichiers suivant:
- [Page Jaunes (Windows).ods][21]
- [Page Jaunes (Linux).ods][22]

Etant un logiciel libre je vous encourage:
- A dupliquer son [code source][23].
- A apporter des modifications, des corrections, des ameliorations.
- D'ouvrir un [dysfonctionnement][24] si nécessaire.

Bref, à participer au developpement de cette extension.
Car c'est ensemble que nous pouvons rendre le Logiciel Libre plus intelligent.

___

## Certification CASA:

Afin de garantir l'interopérabilité avec **Google**, l'extension **OAuth2OOo** nécessite la [certification CASA][25].  
Jusqu'à présent, cette certification était gratuite et réalisée par un partenaire de Google. L'application **OAuth2OOo** a obtenu sa [certification CASA][26] le 28/11/2023.

**Maintenant cette certification est devenue désormais payante et coûte 600$.**

Je n'avais jamais anticipé de tels frais et je compte sur votre contribution pour financer ce projet.

Merci pour votre aide. [![Sponsor][27]][28]

___

## Prérequis:

La version minimale de LibreOffice prise en charge par l'extension OAuth2OOo dépend de la façon dont vous avez installé LibreOffice sur votre ordinateur:

- **Quelle que soit la plateforme**, si vous avez installé LibreOffice depuis le [site de téléchargement de LibreOffice][29], **la version minimale de LibreOffice est 7.0**.

- **Sous Linux** si vous avez utilisé le gestionnaire de paquets pour installer LibreOffice, **la version minimale de LibreOffice est 6.0**. Cependant, vous devez vous assurer que la version de Python fournie par le système n'est pas inférieure à 3.8.  
De plus, vos packages Python fournis par le système peuvent être obsolètes. La journalisation de l'extension vous permettera de vérifier si c'est le cas. Elle est accessible via le menu: **Outils -> Options -> Internet -> Protocole OAuth2-> Voir journal -> Info système** et nécessite le redemarrage de LibreOffice aprés son activation.  
Si des paquets obsolètes apparaissent, vous pouvez les mettre à jour avec cette procédure:  
    - Télécharger le fichier [requirements.txt][30].
    - Installer à l'aide de [pip][31], les paquets Python nécessaires à l'extension avec la commande:  
    `pip install requirements.txt`

Si vous voulez **piloter Firefox dans Calc sous Ubuntu** alors il vous faut reinstaller Firefox à partir du PPA de Mozilla.  
Pour installer le PPA de Mozilla veuillez taper la commande:  
`sudo add-apt-repository ppa:mozillateam/ppa`

___

## Installation:

Il semble important que le fichier n'ait pas été renommé lors de son téléchargement.  
Si nécessaire, renommez-le avant de l'installer.

- ![OAuth2OOo logo][32] Installer l'extension **[OAuth2OOo.oxt][33]** [![Version][34]][33]

Redémarrez LibreOffice après l'installation.  
**Attention, redémarrer LibreOffice peut ne pas suffire.**
- **Sous Windows** pour vous assurer que LibreOffice redémarre correctement, utilisez le Gestionnaire de tâche de Windows pour vérifier qu'aucun service LibreOffice n'est visible après l'arrêt de LibreOffice (et tuez-le si ç'est le cas).
- **Sous Linux ou macOS** vous pouvez également vous assurer que LibreOffice redémarre correctement, en le lançant depuis un terminal avec la commande `soffice` et en utilisant la combinaison de touches `Ctrl + C` si après l'arrêt de LibreOffice, le terminal n'est pas actif (pas d'invité de commande).

___

## Utilisation:

Cette extension a été initialement conçue pour fournir la prise en charge du protocole [OAuth2][10] à d'autres extensions LibreOffice.  
Elle fournit également une API utilisable en [BASIC][11] pour exécuter des requêtes HTTP:

### Créer le service UNO OAuth2Service avec le support du protocole OAuth2:

```
sUser = "account@gmail.com"
sUrl = "people.googleapis.com"
oRequest = createUnoServiceWithArguments("io.github.prrvchr.OAuth2OOo.OAuth2Service", Array(sUrl, sUser))
```

### Créer le service UNO OAuth2Service sans le support du protocole OAuth2:

```
oRequest = createUnoServiceWithArguments("io.github.prrvchr.OAuth2OOo.OAuth2Service")
```

### Utiliser le service UNO OAuth2Service pour executer des requêtes HTTP:

Vous disposez désormais d'un objet `oRequest` qui répond à l'interface définie dans le fichier [XOAuth2Service.idl][35].  
Avec cette interface, deux méthodes sont nécessaires pour exécuter une requête HTTP:
- `getRequestParameter([in] string Name)`, qui vous permet d'obtenir un objet répondant à l'interface [XRequestParameter.idl][36]. Cette interface vous permet de configurer la requête HTTP avant son exécution.
- `execute([in] com::sun::star::rest::XRequestParameter Parameter)`, qui vous permet d'obtenir un objet répondant à l'interface [XRequestResponse.idl][37]. Cela vous permet d'obtenir presque tout ce qui est possible avec une réponse HTTP.

Pour aller plus loin, je vous conseille de prendre connaissance des macros qui sont livrées avec l'extension et qui implémentent tous types de requêtes HTTP.

___

## Uno OAuth2.0 API pour LibreOffice.

![OAuth2OOo Wizard Page1 screenshot][38]

![OAuth2OOo Wizard Page2 screenshot][39]

![OAuth2OOo Wizard Page3 screenshot][40]

![OAuth2OOo Browser Page1 screenshot][41]

![OAuth2OOo Browser Page2 screenshot][42]

![OAuth2OOo Browser Page3 screenshot][43]

![OAuth2OOo Browser Page4 screenshot][44]

![OAuth2OOo Wizard Page4 screenshot][45]

Le protocole OAuth2 permet d'accéder aux ressources de serveurs, après acceptation de l'autorisation de connexion, en échangeant des jetons.

La révocation a lieu dans la gestion des applications associées à votre compte.

Plus aucun mot de passe n'est stocké dans LibreOffice.

___

## Comment créer l'extension:

Normalement, l'extension est créée avec Eclipse pour Java et [LOEclipse][46]. Pour contourner Eclipse, j'ai modifié LOEclipse afin de permettre la création de l'extension avec Apache Ant.  
Pour créer l'extension OAuth2OOo avec l'aide d'Apache Ant, vous devez:
- Installer le [SDK Java][47] version 8 ou supérieure.
- Installer [Apache Ant][48] version 1.10.0 ou supérieure.
- Installer [LibreOffice et son SDK][49] version 7.x ou supérieure.
- Cloner le dépôt [OAuth2OOo][50] sur GitHub dans un dossier.
- Depuis ce dossier, accédez au répertoire: `source/OAuth2OOo/`
- Dans ce répertoire, modifiez le fichier `build.properties` afin que les propriétés `office.install.dir` et `sdk.dir` pointent vers les dossiers d'installation de LibreOffice et de son SDK, respectivement.
- Lancez la création de l'archive avec la commande: `ant`
- Vous trouverez l'archive générée dans le sous-dossier: `dist/`

___

## A été testé avec:

* LibreOffice 7.3.7.2 - Lubuntu 22.04 - Python version 3.10.12

* LibreOffice 7.5.4.2(x86) - Windows 10 - Python version 3.8.16 (sous Lubuntu 22.04 / VirtualBox 6.1.38)

* LibreOffice 7.4.3.2(x64) - Windows 10(x64) - Python version 3.8.15 (sous Lubuntu 22.04 / VirtualBox 6.1.38)

* LibreOffice 24.8.0.3 (X86_64) - Windows 10(x64) - Python version 3.9.19 (sous Lubuntu 22.04 / VirtualBox 6.1.38)

* **Ne fonctionne pas avec OpenOffice** voir [dysfonctionnement 128569][51]. N'ayant aucune solution, je vous encourrage d'installer **LibreOffice**.

Je vous encourage en cas de problème :confused:  
de créer un [dysfonctionnement][24]  
J'essaierai de le résoudre :smile:

___

## Historique:

### [Toutes les changements sont consignées dans l'Historique des versions][52]

[1]: </img/oauth2.svg#collapse>
[2]: <https://prrvchr.github.io/OAuth2OOo/>
[3]: <https://prrvchr.github.io/OAuth2OOo>
[4]: <https://prrvchr.github.io/OAuth2OOo/source/OAuth2OOo/registration/TermsOfUse_fr>
[5]: <https://prrvchr.github.io/OAuth2OOo/source/OAuth2OOo/registration/PrivacyPolicy_fr>
[6]: <https://prrvchr.github.io/OAuth2OOo/CHANGELOG_fr#ce-qui-a-été-fait-pour-la-version-160>
[7]: <https://prrvchr.github.io/README_fr>
[8]: <https://fr.libreoffice.org/download/telecharger-libreoffice/>
[9]: <https://www.openoffice.org/fr/Telecharger/>
[10]: <https://fr.wikipedia.org/wiki/OAuth>
[11]: <https://help.libreoffice.org/latest/fr/text/sbasic/shared/01000000.html?DbPAR=BASIC>
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
[25]: <https://appdefensealliance.dev/casa>
[26]: <https://github.com/prrvchr/OAuth2OOo/blob/master/LOV_OAuth2OOo.pdf>
[27]: <https://img.shields.io/static/v1?label=Sponsor&message=%E2%9D%A4&logo=GitHub&color=%23fe8e86#right>
[28]: <https://github.com/sponsors/prrvchr>
[29]: <https://fr.libreoffice.org/download/telecharger-libreoffice/>
[30]: <https://github.com/prrvchr/OAuth2OOo/releases/latest/download/requirements.txt>
[31]: <https://packaging.python.org/en/latest/tutorials/installing-packages/#use-pip-for-installing>
[32]: <https://prrvchr.github.io/OAuth2OOo/img/OAuth2OOo.svg#middle>
[33]: <https://github.com/prrvchr/OAuth2OOo/releases/latest/download/OAuth2OOo.oxt>
[34]: <https://github.com/prrvchr/OAuth2OOo/blob/master/uno/rdb/idl/com/sun/star/auth/XOAuth2Service.idl>
[35]: <https://github.com/prrvchr/OAuth2OOo/blob/master/uno/rdb/idl/com/sun/star/rest/XRequestParameter.idl>
[36]: <https://github.com/prrvchr/OAuth2OOo/blob/master/uno/rdb/idl/com/sun/star/rest/XRequestResponse.idl>
[3*]: <https://img.shields.io/github/downloads/prrvchr/OAuth2OOo/latest/total?label=v1.6.0#right>
[38]: <https://prrvchr.github.io/OAuth2OOo/img/OAuth2Wizard1_fr.png>
[39]: <https://prrvchr.github.io/OAuth2OOo/img/OAuth2Wizard2_fr.png>
[40]: <https://prrvchr.github.io/OAuth2OOo/img/OAuth2Wizard3_fr.png>
[41]: <https://prrvchr.github.io/OAuth2OOo/img/OAuth2Wizard4_fr.png>
[42]: <https://prrvchr.github.io/OAuth2OOo/img/OAuth2Wizard5_fr.png>
[43]: <https://prrvchr.github.io/OAuth2OOo/img/OAuth2Wizard6_fr.png>
[44]: <https://prrvchr.github.io/OAuth2OOo/img/OAuth2Wizard7_fr.png>
[45]: <https://prrvchr.github.io/OAuth2OOo/img/OAuth2Wizard8_fr.png>
[46]: <https://github.com/LibreOffice/loeclipse>
[47]: <https://adoptium.net/temurin/releases/?version=8&package=jdk>
[48]: <https://ant.apache.org/manual/install.html>
[49]: <https://downloadarchive.documentfoundation.org/libreoffice/old/7.6.7.2/>
[50]: <https://github.com/prrvchr/OAuth2OOo.git>
[51]: <https://bz.apache.org/ooo/show_bug.cgi?id=128569>
[52]: <https://prrvchr.github.io/OAuth2OOo/CHANGELOG_fr>
