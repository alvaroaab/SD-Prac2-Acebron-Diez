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
pip3 install pika
pip3 install pywren-ibm-cloud
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