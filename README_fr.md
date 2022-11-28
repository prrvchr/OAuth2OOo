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

![OAuth2OOo Wizard Page4 screenshot][14]

Le protocole OAuth2.0 permet la connexion aux ressources de serveurs, après acceptation de l'autorisation de connexion, par échange de jetons.

La révocation a lieu dans la gestion des applications associées à votre compte.

Plus aucun mot de passe n'est stocké dans LibreOffice / OpenOffice.

## Installation:

Il semble important que le fichier n'ait pas été renommé lors de son téléchargement.  
Si nécessaire, renommez-le avant de l'installer.

- Installer l'extension ![OAuth2OOo logo][1] **[OAuth2OOo.oxt][15]** version 0.0.6.

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

- Ecriture d'une nouvelle interface [XWizard][16] afin de remplacer le service Wizard devenu défectueux avec les versions 6.4.x et 7.x de LibreOffice (voir [bug 132110](https://bugs.documentfoundation.org/show_bug.cgi?id=132110)).

    Cette nouvelle interface corrige également le [bug 132661][17] et le [bug 132666][18] et permet d'accéder aux versions 6.4.x et 7.x de LibreOffice...

    De plus, ce nouveau XWizard ajoute de nouvelles fonctionnalités telles que:

    - Redimensionnement automatique de l'assistant aux dimensions de la première page affichée.
    - Déplacement automatique vers la page X à l'ouverture si possible.

- Correction d'un problème avec les jetons sans expiration (tels qu'utilisés par Dropbox) lors du test de leur validité...

- Beaucoup d'autres correctifs...

### Ce qui a été fait pour la version 0.0.6:

- L'erreur de flux de bouclage Google a été corrigée. Voir [Dysfonctionnement #10][19]

### Que reste-t-il à faire pour la version 0.0.6:

- Ecriture de l'implémentation du bouton Aide (CommandButton5) dans la nouvelle interface [XWizard][16].

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
[15]: <https://github.com/prrvchr/OAuth2OOo/raw/master/OAuth2OOo.oxt>
[16]: <https://github.com/prrvchr/OAuth2OOo/blob/master/python/wizard.py>
[17]: <https://bugs.documentfoundation.org/show_bug.cgi?id=132661>
[18]: <https://bugs.documentfoundation.org/show_bug.cgi?id=132666>
[19]: <https://github.com/prrvchr/OAuth2OOo/issues/10>
