import paramiko

"""
Se conecta a una maquina virtual de la red por ssh

Parametros:
    + user: usuario al que nos queremos conectar
    + password: contraseña del usuario
    + host: maquina a la que nos queremos conectar
    + puerto: puerto donde se encuentra el protocolo ssh (por defecto el 22)
"""
def conectSSH(user, password,host, puerto=22):
#Se puede hacer lo mismo sin contraseña si se crea con la ceracion de llaves
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
    + ssh: conexion ssh de la maquina que queremos conectarnos


"""
def addFile(localFile, hostRute, name, ssh):

    scp = ssh.open_sftp()
    scp.put(localFile, hostRute+'/'+name)