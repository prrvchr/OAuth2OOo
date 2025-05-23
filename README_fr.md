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
# Documentation

**This [document][3] in english.**

**L'utilisation de ce logiciel vous soumet à nos [Conditions d'Utilisation][4] et à notre [Politique de Protection des Données][5].**

# version [1.5.0][6]

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

La version minimale de LibreOffice prise en charge par l'extension OAuth2OOo dépend de la façon dont vous avez installé LibreOffice sur votre ordinateur:

- **Quelle que soit la plateforme**, si vous avez installé LibreOffice depuis le [site de téléchargement de LibreOffice][23], **la version minimale de LibreOffice est 7.0**.

- **Sous Linux** si vous avez utilisé le gestionnaire de paquets pour installer LibreOffice, **la version minimale de LibreOffice est 6.0**. Cependant, vous devez vous assurer que la version de Python fournie par le système n'est pas inférieure à 3.8.  
De plus, vos packages Python fournis par le système peuvent être obsolètes. La journalisation de l'extension vous permettera de vérifier si c'est le cas. Elle est accessible via le menu: **Outils -> Options -> Internet -> Protocole OAuth2-> Voir journal -> Info système** et nécessite le redemarrage de LibreOffice aprés son activation.  
Si des paquets obsolètes apparaissent, vous pouvez les mettre à jour avec cette procédure:  
    - Télécharger le fichier [requirements.txt][24].
    - Installer à l'aide de [pip][25], les paquets Python nécessaires à l'extension avec la commande:  
    `pip install requirements.txt`

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

## Comment créer l'extension:

Normalement, l'extension est créée avec Eclipse pour Java et [LOEclipse][37]. Pour contourner Eclipse, j'ai modifié LOEclipse afin de permettre la création de l'extension avec Apache Ant.  
Pour créer l'extension OAuth2OOo avec l'aide d'Apache Ant, vous devez:
- Installer le [SDK Java][38] version 8 ou supérieure.
- Installer [Apache Ant][39] version 1.10.0 ou supérieure.
- Installer [LibreOffice et son SDK][40] version 7.x ou supérieure.
- Cloner le dépôt [OAuth2OOo][41] sur GitHub dans un dossier.
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

* **Ne fonctionne pas avec OpenOffice** voir [dysfonctionnement 128569][42]. N'ayant aucune solution, je vous encourrage d'installer **LibreOffice**.

Je vous encourage en cas de problème :confused:  
de créer un [dysfonctionnement][22]  
J'essaierai de le résoudre :smile:

___

## Historique:

### [Toutes les changements sont consignées dans l'Historique des versions][43]

[1]: </img/oauth2.svg#collapse>
[2]: <https://prrvchr.github.io/OAuth2OOo/>
[3]: <https://prrvchr.github.io/OAuth2OOo>
[4]: <https://prrvchr.github.io/OAuth2OOo/source/OAuth2OOo/registration/TermsOfUse_fr>
[5]: <https://prrvchr.github.io/OAuth2OOo/source/OAuth2OOo/registration/PrivacyPolicy_fr>
[6]: <https://prrvchr.github.io/OAuth2OOo/CHANGELOG_fr#ce-qui-a-été-fait-pour-la-version-150>
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
[23]: <https://fr.libreoffice.org/download/telecharger-libreoffice/>
[24]: <https://github.com/prrvchr/OAuth2OOo/releases/latest/download/requirements.txt>
[25]: <https://packaging.python.org/en/latest/tutorials/installing-packages/#use-pip-for-installing>
[26]: <https://prrvchr.github.io/OAuth2OOo/img/OAuth2OOo.svg#middle>
[27]: <https://github.com/prrvchr/OAuth2OOo/releases/latest/download/OAuth2OOo.oxt>
[28]: <https://img.shields.io/github/downloads/prrvchr/OAuth2OOo/latest/total?label=v1.5.0#right>
[29]: <https://prrvchr.github.io/OAuth2OOo/img/OAuth2Wizard1_fr.png>
[30]: <https://prrvchr.github.io/OAuth2OOo/img/OAuth2Wizard2_fr.png>
[31]: <https://prrvchr.github.io/OAuth2OOo/img/OAuth2Wizard3_fr.png>
[32]: <https://prrvchr.github.io/OAuth2OOo/img/OAuth2Wizard4_fr.png>
[33]: <https://prrvchr.github.io/OAuth2OOo/img/OAuth2Wizard5_fr.png>
[34]: <https://prrvchr.github.io/OAuth2OOo/img/OAuth2Wizard6_fr.png>
[35]: <https://prrvchr.github.io/OAuth2OOo/img/OAuth2Wizard7_fr.png>
[36]: <https://prrvchr.github.io/OAuth2OOo/img/OAuth2Wizard8_fr.png>
[37]: <https://github.com/LibreOffice/loeclipse>
[38]: <https://adoptium.net/temurin/releases/?version=8&package=jdk>
[39]: <https://ant.apache.org/manual/install.html>
[40]: <https://downloadarchive.documentfoundation.org/libreoffice/old/7.6.7.2/>
[41]: <https://github.com/prrvchr/OAuth2OOo.git>
[42]: <https://bz.apache.org/ooo/show_bug.cgi?id=128569>
[43]: <https://prrvchr.github.io/OAuth2OOo/CHANGELOG_fr>
