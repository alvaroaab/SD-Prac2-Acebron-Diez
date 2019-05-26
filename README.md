# SD-Prac2-Acebron-Diez
## Grup 
Pràctica 2 SD - Álvaro Acebrón i Marc Diez.
## Instal·lació
* Verificar els requeriments:
```
sudo apt-get install python3
sudo apt-get install python3-pip
pip3 install awscli --upgrade --user
pip3 install -U ibm-cos-sdk --upgrade --user
pip3 install boto3 --upgrade
pip3 install pyyaml --upgrade
```
* Fer login a ibmcloud:
```
ibmcloud login -a cloud.ibm.com
ibmcloud plugin install cloud-functions
```
* Clonar el repositori: 
```
git clone https://github.com/alvaroaab/SD-Prac2-Acebron-Diez
```
* Afegir el fitxer .pywren_config a la carpeta $HOME
* Per executar el programa:
```
python3 prac2.py
```

## Arquitectura i Implementació
### main
El main és el que s'encarrega d'engegar el leader i els slaves, d'inicialitzar la llista utilitzada pels slaves i d'imprimir per pantalla el resultat dels slaves
* 1r: Demana a l'usuari el nombre de slaves/maps a executar
* 2n: Crea una llista data que conté llistes que contenen el id del slave i el número de slaves/maps
* 3r: Engega el pywren del leader
* 4t: Engega el pywren dels slaves
* 5è: Espera el resultat dels slaves i el mostra per pantalla
* 6è: Neteja les dades del COS

### Leader
El leader és el que s'encarrega de rebre peticions d'escriptura i decidir quin slave pot escriure.
* 1r: Es connecta amb RabbitMQ
* 2n: Declara els canals leader i leader_finished (aquest segon canal sutilitza per comprovar quan acaba un slave)
* 3r: Es crea una llista amb els ids dels slaves
* 4t: S'executen els slaves aleatòriament. Quan es permet l'escriptura d'un slave, el leader s'espera a que el slave acabi
* 5è: S'esborren les cues i es tanquen les connexions

### Slave
Els slaves generen un número aleatori entre 0 i 1000 i es sincronitzen amb la resta de slaves per incloure el valor aleatori a totes les llistes de resultat.
* 1r: Es connecta amb RabbitMQ
* 2n: Declara els canals $id_slave, leader i leader_finished
* 3r: Els slaves esperen a que el leader els permeti escriure
* 4t: Quan el leader dóna permís al slave, es genera el valor aleatori i es publica a totes les cues de la resta de slaves
* 5è: Si el slave rep un missatge d'un altre slave, agafa el número del missatge i l'afegeix a la llista resultat
* 6è: Quan la llista ja és plena, s'esborra la cua del slave, es tanquen les connexions i es retorna la llista resultat