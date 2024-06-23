import requests

import time

import datetime

import os

import re

import json

import glob

import threading

import subprocess

import pytz

from getpass import getpass

def check_sudo_password_required():
    try:
        # Intenta ejecutar un comando simple que requiere sudo
        subprocess.run(['sudo', '-n', 'true'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # Si no se lanza una excepción, entonces no se requiere contraseña
        return False
    except subprocess.CalledProcessError:
        # Si se lanza una excepción, entonces se requiere contraseña
        return True
    
if check_sudo_password_required():
    print("Se requiere contraseña para usar sudo.")
    sudo_password = getpass("Ingrese la contraseña de sudo: ")
    command = "sudo -S apt update"
    os.system('echo %s | %s' % (sudo_password, command))
else:
    print("No se requiere contraseña para usar sudo.")

path_actual = subprocess.run('pwd', shell=True, check=True, capture_output=True, encoding='utf-8')
path_actual_str = path_actual.stdout
path_actual_str = path_actual_str[:-1]

def playit_hilo():
    print('Starting server...')
    subprocess.run(["playit"], check=True)

    # Obteniendo la IP del servidor
    result = subprocess.run(["playit", "status"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print("Tu ip es: " + result.stdout.decode())

def obtener_fecha_hora_chile():
    # Obtén la fecha y hora actual en tu zona horaria local
    fecha_hora_chile = datetime.datetime.now(pytz.timezone("America/Santiago"))

    # Devuelve la fecha y hora en formato ISO 8601
    return fecha_hora_chile.isoformat()

def commit_github():
    while True:
        time.sleep(2700) #45min
        try:
            fecha_hora_actual = obtener_fecha_hora_chile()
            print("COMMIT--> "+ fecha_hora_actual)
            os.system("git add --all")
            os.system("git commit -m \"autoCommit " + fecha_hora_actual + " \"")
            os.system("git push")
        except:
            print("ERROR CON COMMIT!: " + fecha_hora_actual)

commit_thread = threading.Thread(target=commit_github)
commit_thread.start()


os.makedirs(path_actual_str + "/Minecraft-server", exist_ok=True)

os.chdir(path_actual_str + "/Minecraft-server")

#lista los archivos del directorio para verificarlos
os.system('ls')


#Importacion del archivo de configuracion


config_path = path_actual_str + "/Minecraft-server/colabconfig.json"

if os.path.isfile(config_path):

    with open(config_path) as config_file:

        colabconfig = json.load(config_file)

else:

    colabconfig = {"server_type": "generic"} # Usar la configura default si no existe

    with open(config_path, 'w') as new_config_file:

        json.dump(colabconfig, new_config_file)

tunnel_service = "playit"
if tunnel_service == "ngrok":

    #Aqui se instala el ngrok en el servidor
    os.system('pip -q install pyngrok')

    from pyngrok import conf, ngrok



    # Obten tu token de ngrok

    print("Consigue tu authtoken de https://dashboard.ngrok.com/auth") #Consigue aqui tu token de ngrok, sera dinamico, si quieres que sea estatico, necesitaras la version premiun de ngrok

    import getpass



    # v - - - - - - - TOKEN - - - - - - - v
    # logeo en ngrok
    os.system('ngrok authtoken 2ei4UGGUePHQzfBYzeT6jvIXo5X_3gkPWUyHgX6mGTw5YtF2n')
    


    #Establecimiento de region de ngrok



    #v - - - - - - - REGIONES DISPONIBLES - - - - - - - v

    # ap - Asia/Pacifico (Singapore)

    # au - Australia (Sydney)

    # eu - Europa (Frankfurt - Alemania)

    # in - India (Mumbai)

    # jp - Japon (Tokyo)

    # sa - America del sur (São Paulo - Brasil)

    # us - Estados unidos (Ohio)

    conf.get_default().region = 'us' # <--- Cambia esto por la region que quieras



    # Conectar a ngrok

    url = ngrok.connect(25565, 'tcp')

    print('La IP de tu servidor es ' + ((str(url).split('"')[1::2])[0]).replace('tcp://', ''))

    #Si obtienes el servicio premiun de ngrok borra las dos lineas de codigo de arriba y quitale el # a estas a continuacion:

    #subdominio = "mi-subdominio"

    #url = ngrok.connect(25565, 'tcp', subdomain=subdominio)

    #print('La IP de tu servidor es ' + url.replace('tcp://', ''))


elif tunnel_service == "playit":

    os.system("curl -SsL https://playit-cloud.github.io/ppa/key.gpg | gpg --dearmor | sudo tee /etc/apt/trusted.gpg.d/playit.gpg >/dev/null")
    os.system("echo \"deb [signed-by=/etc/apt/trusted.gpg.d/playit.gpg] https://playit-cloud.github.io/ppa/data ./\" | sudo tee /etc/apt/sources.list.d/playit-cloud.list")
    os.system("sudo apt update")
    os.system("sudo apt install -y playit")
    


    # Iniciando el servidor con Playit.gg
    playit_thread = threading.Thread(target=playit_hilo)
    playit_thread.start()

#Obtiene la lista de usuarios de JSONPlaceholder
#Para mantener el servidor activo
def get_users():
    url = 'https://jsonplaceholder.typicode.com/users'
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            print("Lista de usuarios:")
            for user in data:
                print(f"Nombre: {user['name']}, Email: {user['email']}")
        else:
            print(f"Error al hacer la solicitud. Código de estado: {response.status_code}")
    except requests.RequestException as e:
        print(f"Error de conexión: {e}")

# Función para ejecutar get_users() cada 25 minutos
def repeat_get_users():
    while True:
        get_users()
        time.sleep(600)  # Espera 10 minutos

# Inicia un hilo para ejecutar repeat_get_users() en segundo plano
user_thread = threading.Thread(target=repeat_get_users)
#user_thread.start()


#Obtener el archivo de configuracion
stype = colabconfig["server_type"]
version = colabconfig["server_version"]

#Imprimir el tipo de servidor y la version
print("Estas jugando a minecraft: " + stype + " en su version: "+ version)

#Si el servidor es de tipo Forge antiguo no va a funcionar
if colabconfig["server_type"] == "forge" and colabconfig["server_version"] < "1.17.1":
    print("La version de Forge no es compatible con este script. Por favor, usa una version de Forge 1.17.1 o superior.")


#Si el servidor es de tipo Forge encontrara los archivos necesarios para ejecutar el servidor

if colabconfig["server_type"] == "forge":

    # Obtiene la versión de Forge
    
    forgefiles = path_actual_str + "/Minecraft-server/libraries/net/minecraftforge/forge/"
    
    forgepreversion = os.listdir(forgefiles)
        
    if forgepreversion:
        
        forgeversion = forgepreversion[0]
        forgeversionchecked = forgeversion.replace(".jar", "")
        print("La versión de Forge es:", forgeversionchecked)
        
    else:
        
        print("No se encontraron archivos en el directorio Forge.")
        
    pathtoforge = glob.glob(path_actual_str + "/Minecraft-server/libraries/net/minecraftforge/forge/" + forgeversionchecked + "/unix_args.txt")

    if pathtoforge: # Checa si la lista no esta vacia
        print('\033[91m' + "Se encontro el archivo unix_args.txt y se procedera a ejecutar el servidor.")
        path = pathtoforge[0] # Obtiene la primera ruta de la lista
        print(path,"\\n")
        # !java @user_jvm_args.txt "@{path}" "$@"
        llamada_java = 'java @user_jvm_args.txt @' + path + ' $@'
        os.system(llamada_java)

        


    else:

        print("No se encontro el archivo unix_args.txt.")

#Si el servidor es de tipo Vanilla o paper o mohist o catserver o fabric o purpur

else:

    #Ejecuta el archivo jar del servidor
    os.system('java $memory_allocation $server_flags -jar $jar_name nogui')

# Ciclo para realizar las solicitudes a JSONPlaceholder cada minuto

while True:
    time.sleep(60)  # Espera 1 minuto