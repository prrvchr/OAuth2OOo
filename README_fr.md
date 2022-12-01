# ![OAuth2OOo logo][1] OAuth2OOo

**This [document][2] in English.**

**L'utilisation de ce logiciel vous soumet à nos** [**Conditions d'utilisation**][3] **et à notre** [**Politique de protection des données**][4].

# version [0.0.6][5]

## Introduction:

**OAuth2OOo** fait partie d'une [Suite][6] d'extensions [LibreOffice][7] et/ou [OpenOffice][8] permettant de vous offrir des services inovants dans ces suites bureautique.  
Cette extension est l'implémentation du protocole OAuth 2.0. Protocole permettant d'obtenir votre consentement pour qu'une application puisse accéder à vos données présentes chez les GAFA.

Etant un logiciel libre je vous encourage:
- A dupliquer son [code source][9].
- A apporter des modifications, des corrections, des ameliorations.
- D'ouvrir un [dysfonctionnement][10] si nécessaire.

Bref, à participer au developpement de cette extension.
Car c'est ensemble que nous pouvons rendre le Logiciel Libre plus intelligent.

## Uno OAuth2.0 API pour LibreOffice / OpenOffice.

![OAuth2OOo Wizard Page1 screenshot][11]

![OAuth2OOo Wizard Page2 screenshot][12]

![OAuth2OOo Wizard Page3 screenshot][13]

![OAuth2OOo Browser Page1 screenshot][14]

![OAuth2OOo Browser Page2 screenshot][15]

![OAuth2OOo Browser Page3 screenshot][16]

![OAuth2OOo Wizard Page4 screenshot][17]

Le protocole OAuth2 permet d'accéder aux ressources de serveurs, après acceptation de l'autorisation de connexion, en échangeant des jetons.

La révocation a lieu dans la gestion des applications associées à votre compte.

Plus aucun mot de passe n'est stocké dans LibreOffice / OpenOffice.

## Installation:

Il semble important que le fichier n'ait pas été renommé lors de son téléchargement.  
Si nécessaire, renommez-le avant de l'installer.

- Installer l'extension ![OAuth2OOo logo][1] **[OAuth2OOo.oxt][18]** version 0.0.6.

- Redémarrez LibreOffice / OpenOffice après l'installation.

## Utilisation:

Cette extension n'est pas faite pour être utilisée seule, mais fournit le service OAuth2 à d'autres extensions LibreOffice / OpenOffice.  
Voici comment nous utilisons son API:

### Créer le service OAuth2:

> identifier = "com.gmail.prrvchr.extensions.OAuth2OOo.OAuth2Service"  
> service = ctx.ServiceManager.createInstanceWithContext(identifier, ctx)

### Initialiser la Session ou au moins l'Url:

- Initialiser la Session: 

> initialized = service.initializeSession(registered_url, user_account)

- Initialiser l'Url:

> initialized = service.initializeUrl(registered_url)

La valeur renvoyée:: `initialized` est True si `registered_url` et/ou `user_account` a été récupérée de la configuration du service OAuth2.

### Obtenir le jeton d'accès:

> format = 'Bearer %s'  
> token = service.getToken(format)

## A été testé avec:

* LibreOffice 7.3.7.2 - Ubuntu 22.04 - LXQt 1.1.0

* LibreOffice 7.4.3.2.(x64) - Windows 10(x64)

* OpenOffice 4.1.13 - Lubuntu 22.04 - LXQt 0.17.0

Je vous encourage en cas de problème :-(  
de créer un [dysfonctionnement][10]  
J'essaierai de la résoudre ;-)

## Historique:

### Ce qui a été fait pour la version 0.0.5:

- Ecriture d'une nouvelle interface [XWizard][19] afin de remplacer le service Wizard devenu défectueux avec les versions 6.4.x et 7.x de LibreOffice (voir [bug 132110](https://bugs.documentfoundation.org/show_bug.cgi?id=132110)).

    Cette nouvelle interface corrige également le [bug 132661][20] et le [bug 132666][21] et permet d'accéder aux versions 6.4.x et 7.x de LibreOffice...

    De plus, ce nouveau XWizard ajoute de nouvelles fonctionnalités telles que:

    - Redimensionnement automatique de l'assistant aux dimensions de la première page affichée.
    - Déplacement automatique vers la page X à l'ouverture si possible.

- Correction d'un problème avec les jetons sans expiration (tels qu'utilisés par Dropbox) lors du test de leur validité...

- Beaucoup d'autres correctifs...

### Ce qui a été fait pour la version 0.0.6:

- Réécriture de l'assistant OAuth2 (Wizard) en essayant de suivre au mieux le model MCV. Cet assistant est composé de 5 pages héritant de l'interface UNO [XWizardPage][22]:

    - Page 1: [Controlleur][23] et [Vue][24]
    - Page 2: [Controlleur][25] et [Vue][26]
    - Page 3: [Controlleur][27] et [Vue][28]
    - Page 4: [Controlleur][29] et [Vue][30]
    - Page 5: [Controlleur][31] et [Vue][32]

- Réécriture des trois services UNO fournis par l'extension OAuth2OOo dans trois fichiers distincts:

    - Le service [OAuth2Service][33] implémentant l'interface décrite dans le fichier IDL [XOAuth2Service][34].
    - Le service [OAuth2Dispacher][35] implémentant l'interface UNO [XDispatchProvider][36].
    - Le service [OAuth2Handler][37] implémentant l'interface UNO [XInteractionHandler2][38].

- Réécriture de la fenêtre des options accessible par **Outils -> Options -> Internet -> Protocole OAuth2**. Cette fenêtre est composée de deux fenêtre:

    - La fenêtre de journalisation: [Controlleur][39] et [Vue][40].
    - La fenêtre des options de configuration de l'extension OAuth2OOo: [Controlleur][41] et [Vue][42].

- Réécriture d'un modèle unique [OAuth2Model][43] gérant l'assistant, les services, et la fenêtre des options.

- L'erreur de flux de bouclage Google a été corrigée. Voir [Dysfonctionnement #10][44]

### Que reste-t-il à faire pour la version 0.0.6:

- Ecriture de l'implémentation du bouton Aide (CommandButton5) dans la nouvelle interface [XWizard][19].

- Ajouter de nouvelles langue pour l'internationalisation...

- Tout ce qui est bienvenu...

[1]: <https://prrvchr.github.io/OAuth2OOo/img/OAuth2OOo.png>
[2]: <https://prrvchr.github.io/OAuth2OOo>
[3]: <https://prrvchr.github.io/OAuth2OOo/source/OAuth2OOo/registration/TermsOfUse_fr>
[4]: <https://prrvchr.github.io/OAuth2OOo/source/OAuth2OOo/registration/PrivacyPolicy_fr>
[5]: <https://prrvchr.github.io/OAuth2OOo/README_fr#historique>
[6]: <https://prrvchr.github.io/README_fr>
[7]: <https://fr.libreoffice.org/download/telecharger-libreoffice/>
[8]: <https://www.openoffice.org/fr/Telecharger/>
[9]: <https://github.com/prrvchr/OAuth2OOo>
[10]: <https://github.com/prrvchr/OAuth2OOo/issues/new>
[11]: <https://prrvchr.github.io/OAuth2OOo/img/OAuth2Wizard1_fr.png>
[12]: <https://prrvchr.github.io/OAuth2OOo/img/OAuth2Wizard2_fr.png>
[13]: <https://prrvchr.github.io/OAuth2OOo/img/OAuth2Wizard3_fr.png>
[14]: <https://prrvchr.github.io/OAuth2OOo/img/OAuth2Wizard4_fr.png>
[15]: <https://prrvchr.github.io/OAuth2OOo/img/OAuth2Wizard5_fr.png>
[16]: <https://prrvchr.github.io/OAuth2OOo/img/OAuth2Wizard6_fr.png>
[17]: <https://prrvchr.github.io/OAuth2OOo/img/OAuth2Wizard7_fr.png>
[18]: <https://github.com/prrvchr/OAuth2OOo/raw/master/OAuth2OOo.oxt>
[19]: <https://github.com/prrvchr/OAuth2OOo/blob/master/python/wizard.py>
[20]: <https://bugs.documentfoundation.org/show_bug.cgi?id=132661>
[21]: <https://bugs.documentfoundation.org/show_bug.cgi?id=132666>
[22]: <https://www.openoffice.org/api/docs/common/ref/com/sun/star/ui/dialogs/XWizardPage.html>
[23]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/pythonpath/oauth2/wizard/page1/oauth2manager.py>
[24]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/pythonpath/oauth2/wizard/page1/oauth2view.py>
[25]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/pythonpath/oauth2/wizard/page2/oauth2manager.py>
[26]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/pythonpath/oauth2/wizard/page2/oauth2view.py>
[27]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/pythonpath/oauth2/wizard/page3/oauth2manager.py>
[28]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/pythonpath/oauth2/wizard/page3/oauth2view.py>
[29]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/pythonpath/oauth2/wizard/page4/oauth2manager.py>
[30]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/pythonpath/oauth2/wizard/page4/oauth2view.py>
[31]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/pythonpath/oauth2/wizard/page5/oauth2manager.py>
[32]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/pythonpath/oauth2/wizard/page5/oauth2view.py>
[33]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/OAuth2Service.py>
[34]: <https://github.com/prrvchr/OAuth2OOo/blob/master/uno/rdb/idl/com/sun/star/auth/XOAuth2Service.idl>
[35]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/OAuth2Dispatcher.py>
[36]: <https://www.openoffice.org/api/docs/common/ref/com/sun/star/frame/XDispatchProvider.html>
[37]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/OAuth2Handler.py>
[38]: <https://www.openoffice.org/api/docs/common/ref/com/sun/star/task/XInteractionHandler2.html>
[39]: <https://github.com/prrvchr/OAuth2OOo/blob/master/uno/lib/uno/logger/logger.py>
[40]: <https://github.com/prrvchr/OAuth2OOo/blob/master/uno/lib/uno/logger/logview.py>
[41]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/pythonpath/oauth2/options/optionsmanager.py>
[42]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/pythonpath/oauth2/options/optionsview.py>
[43]: <https://github.com/prrvchr/OAuth2OOo/blob/master/source/OAuth2OOo/pythonpath/oauth2/oauth2model.py>
[44]: <https://github.com/prrvchr/OAuth2OOo/issues/10>
