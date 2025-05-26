# SAFE-M-CONDUCTIMETRE : Un conductimètre abbordable pou  l'enseignement  


* [Introduction](##introduction)
* [L'appareil](##appareil)
* [Scripts](##arduino-scripts)
* [Programme python](##python)

## Introduction <a class="anchor" id="introduction"></a>

* Le programme permet de contôler un conductimètre équipé d'une sonde K1 ou K10 et d'une sonde de température. 
* Il est le fruit de la collaboration entre plusieurs étudiants et enseignants chercheurs de l'Institut de Physique du Globe de Paris 
* Pour le citer :
Condé, A., Rubin, N., Parcineau, S., Perez, M., De Boisresdon, A., Jacquemard, R., Sadoudi, L., Schmeitzky, B., ..., Deutsh, G., Baussant, J., Blaise, T., Goumis, L., Junghans, G., Le Van, C., Lelieur, F., Mielle, M., Nunes, G., Perrillat Mandry, A., Sagorin, P., Shanker, P., Spiparan, T., Wu M. Lumembe, O. & Métivier F. (2025). SAFE-M-CONDUCTIMETRE Un conductimètre low cost pour l'enseignement [Computer Software]. https://github.com/adja-code/Conductimetre


## L'appareil <a class="anchor" id="appareil"></a>

* L'appareil est constitué d'une sonde conductimétrique et d'une sonde de température PT100
* Le programme python inclut la calibration du conductimètre 


## Script Arduino <a class="anchor" id="arduino-scripts"></a>

Le script arduino consiste à envoyer une série de tensions et de températures mesurées respectivement par la sonde conductimétrique et la sonde PT100. 

## Programme Python <a class="anchor" id="python-and-sql"></a>

Le programme python permet de récupérer les données envoyées par le programme arduino au port série, de les convertir dans les bonnes unités au moyen de régression linéaire, de les enregistrer et de les représenter graphiquement. 

Pour des raisons de simplicité le script doit fonctionner en mode terminal, pas d'interface utilisateur graphique donc, et offre des choix à l'étudiant. Le programme permet

* un étalonnage deux ou trois solutions tampons 
* la réutilisation d'une calibration passée;
* l'usage d'une calibration par défaut obtenue grace à une série longue de mesures;
* la mesure de la conductivité  en continu;
* la représentation graphique des données.

Calibrations et mesures sont enregistrées en continu dans des dossiers CALIB et MESURES, ce qui permet leur réutilisaiton ultérieure. La compensation de température est, pour l'heure, appliquée à la calibration uniquement. L'objectif est d'intégrer la correction de température pour chacune des mesures de conductivité. 

