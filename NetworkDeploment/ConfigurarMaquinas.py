import paramiko
import re

"""
Se conecta a una maquina virtual de la red por ssh

Parametros:
    + user: usuario al que nos queremos conectar
    + password: contraseña del usuario
    + host: maquina a la que nos queremos conectar
    + puerto: puerto donde se encuentra el protocolo ssh (por defecto el 22)
"""


def conectSSH(user, password, host, puerto=22):
    # Se puede hacer lo mismo sin contraseña si se crea con la ceracion de llaves
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, puerto, user, password)

    return ssh


"""
Añadade un fichero a un equipo por scp

Parametros de entrada:
    + localFile: fichero lccal que se quiere subir
    + hostRute: ruta donde se almacenara el fichero
    + Nombre que queremos dar al fichero
    + ssh: conexion ssh de la maquina 

"""


def addFile(localFile, hostRute, name, ssh):
    scp = ssh.open_sftp()
    scp.put(localFile, hostRute + '/' + name)


"""
Mueve un fichero de ruta en el equipo destino, si en el lugar destino existe este se eliminara

Prerequisito que el usuario con el que nos conectamos se encuentre dentro del grupo de Sudo 
o pueda ejecutar el comando mv como superususareio

Parametros de entrada:
    + origin: localizacion del fichero en el host
    + destiny: Nuevo lugar del fichero
    + ssh: conexion ssh de la maquina
    + password: contraseña del usuario conectado
"""
def moveFile(origin, destiny, ssh, password):
    comand = "echo " + password + " | sudo -S mv " + origin + ' ' + destiny
    ssh.exec_command(comand)

"""
Modifica el archivo selecionado manteniendo el contenido del equipo destino

Parametros de entrada:
    + text: texto a que se quiere escribir
    + rute: ruta donde se encuentra el archivo
    + ssh: conexion ssh de la maquina
    + password: contraseña del usuario conectado
    + remplace: si se quiere remplazar una parte del texto
    + pattern: expresion regular con el formato del texto
"""
def modifyFile(text, rute, ssh, password, remplace=False, pattern=""):
    if remplace: #caso replazar una parte del texto en funcion de uan estructura
        comand = "echo "+password+" | sudo -S cat "+rute
        stdin, stdout, error = ssh.exec_command(comand)
        file = stdout.read().decode("utf-8")
        line = re.search(pattern, file)
        if line:
            newFile = file.replace(line.group(), text)
            comand = "echo "+password+" | sudo -S echo '"+newFile+"' > "+rute
            ssh.exec_command(comand)
        else:
            #se tiene que ver como tratar este problema
            print("No se pudo encontrar el pattern proporcionado")

    else: #caso para añadir al final de un archivo
        comand =  "echo " + password + " | sudo -S echo '"+text+"' >> "+rute
        ssh.exec_command(comand)

"""
Reinicia, para, acrivo y desactiva un servicio de la maquina destino

Parametros de entrada:
    + service: nombre del servicio que se quiere reiniciar
    + ssh: conexion ssh de la maquina
    + password: contraseña del usuario conectado
    + actions: lista con las acciones que se quiere llevar al servicio, se ejecutaran en orden de la lista
            Por defecto se va a reiniciar el servicio.
"""
def modifyService (service, ssh, password, actions=["restart"]):
    for action in actions:
        comand= "echo "+password+" | sudo -S systemctl "+action+" "+service
        ssh.exec_command(comand)

"""
Instala uno o varios servicios en la maquina dada

Parametros de entrada:
    + services: lista de los servicios que se quieren instalar
    + ssh: conexion ssh de la maquina
    + password: contraseña del usuario conectado
    + distribution: distribucion del sistema operativo que esta corriendo en la maquina, estos pueden ser ubuntu, debian,
                arch, centos o fedora (si quieres usar dnf para instalr paquetes en centos escoja la distro de fedora).
"""
def installservice(services, ssh, password, distrubution):
    comandInstall = None #variable donde se guardan los comandos de los distintos progrmas a instalar
    if distrubution.lower().conteins("ubuntu") or distrubution.lower().conteins("debian"):
        comandUpdate = "echo " + password + " | sudo -S apt-get update"
        for service in services:
            comandInstall.append("echo " + password + " | sudo -S apt install "+service)

    elif distrubution.lower().conteins("arch"):
        comandUpdate = "echo " + password + " | sudo -S pacman -Syy"
        for service in services:
            comandInstall.append("echo " + password + " | sudo -S pacman -S"+service)

    elif distrubution.lower().conteins("centos"):
        comandUpdate ="echo " + password + " | sudo -S yum update"
        for service in services:
            comandInstall.append("echo " + password + " | sudo -S yum install "+service)

    elif distrubution.lower().conteins("fedora"):
        comandUpdate = "echo " + password + " | sudo -S dnf upgrade --refresh"
        for service in services:
            comandInstall.append("echo " + password + " | sudo -S dnf install " + service)

    ssh.exec_command(comandUpdate)
    for comand in comandInstall:
                ssh.exec_command(comand)


if __name__ == '__main__':
    ssh = conectSSH("osboxes", "osboxes.org", "192.168.181.131")
    #addFile("README.md", "/home/osboxes", "prueba", ssh)
    #moveFile("/home/osboxes/prueba", "/prueba", ssh, "osboxes.org")
    #data = '''iface eth0 inet static\n\taddress 192.168.181.128\n\tnetmask 255.255.255.0\n'''
    #dhcp = "iface eth0 inet .*"
    #static = r'^\s*iface\s+eth0\s+inet\s+static\s*\n\s*address\s+[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+\n\s*netmask\s+[0-9]+\.[0-9]+\.[0-9]+\.[0-9]\s*\n' #No funciona qui si en regex101
    #modifyFile(data, "/home/osboxes/prueba", ssh, "osboxes.org", True, static)
    #modifyService("ssh", ssh, "osboxes.org", ["enable"])