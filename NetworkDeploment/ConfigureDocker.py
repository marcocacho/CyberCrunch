import docker
import tarfile
import os
import re
"""
Libreria de funciones para configurar un docker activo
"""


def connectDocker(id, ip=None, port=2375):
    """
    Se conecta a un router a traves de telnet desplegado en gns3 instalado en la maquina local.
    :param id: id del docker al que se quiere conectar
    :param ip: ip del equipo donde se esta ejecutnado docker
    :param port: puerto donde se esta escuchando, por defecto el 2375
    :return: conector al docker
    """
    if ip is not None:
        client = docker.DockerClient(base_url=f'tcp://{ip}:{port}', tls=False, version="auto")
    else:
        client = docker.from_env()
    return client.containers.get(id)


def configIp(settings, docker_id, console_ip, console_port=2375):
    """
    Configura la ip de un docker a traves de telnet
    :param settings: diccionario con los datos de configuracion del docker
        claves:
            - iface: interfaz del router (formatos validos fa 0/0 y fast ethernet 0/0)
            - ip: ip de la interfaz o dhcp para usar un servidor dhcp
            - netmask(optional): mascara de la red
            - gateway(optional): router de salida
    :param docker_id: id del docker que se quiere configurar
    :param console_ip: ip del nodo al que nos queremos conectar
    :param console_port: puerto donde se esta escuchando, por defecto el 2375
    :return: None
    """

    docker_connection = connectDocker(docker_id, console_ip, console_port)
    if settings["ip"].lower() == "dhcp":
        config_iface = "dhclient %s" % settings["iface"]
    else:
        config_iface = ["ifconfig %s up" % settings["iface"],
                        "ifconfig %s %s netmask %s" % (settings["iface"], settings["ip"], settings["netmask"]),
                        "route add default gw %s %s" % (settings["gateway"], settings["iface"])]

    for command in config_iface:
        docker_connection.exec_run(command)

def configSyslog(docker_id, name, opensearch, lab_name, settings=None):
    """
    Configura el servicio de syslog-ng en el equipo y activa el servicio para enviar los datos a un servidor de opensearch.
    Por defecto se van a monitorizar system e internal, aunque se puede añadir mas opicones dentro de settings
    :param docker_id: id del docker que se quiere configurar
    :param name: nombre del equipo
    :param opensearch: diccionario con la ip y puerto para enviar los datos a opensearch
    :param lab_name: nombre del laboratorio para crear su propio indice
    :param settings: array con diccionario con los datos de configuracion del docker, se puede añadir ficheros,
        claves:
            + name: nombre para el recurso a monitorizar
            + type: tipo de dato para syslog
            + log: ruta absoluta del log o fichero a monitorizar
    :return: None
    """
    if settings is None:
        settings = []
    syslog_path = "/etc/syslog-ng/conf.d"

    destination = f'''destination d_opensearch_http {{
    elasticsearch-http(
        index("{lab_name}")
        type("")
        url("https://{opensearch["ip"]}:{opensearch["port"]}/_bulk")
        user("admin")
        password("admin")
        template("$(format-json --scope rfc5424 --scope dot-nv-pairs --rekey .* --shift 1 --scope nv-pairs --exclude DATE --key ISODATE @timestamp=${{ISODATE}} @equipo=\\"{name}\\" @hostname=${{HOST}})")
    );
}};'''
    log = '''log {{
      source({});
      destination(d_opensearch_http);
      flags(flow-control);
}};'''
    source = '''source s_{} {{
                {}({})
}};'''
    docker_connection = connectDocker(docker_id)

    code, result = docker_connection.exec_run(f'''mkdir -p {syslog_path}''')
    config = ""
    config += f'''{destination}\n'''

    for data in settings:
        if "type" in data:
            config += f"""{source.format(data['name'], data['type'], data['log'])}"""
        config += f"""{log.format(data['name'])}"""

    conf_file = "/tmp/opensearch.conf"
    # Crear el archivo de configuración en el sistema de archivos
    with open(conf_file, 'w+') as config_file:
            config_file.write(config)

    tar_path = f"/tmp/syslog_{name}.tar"
    # Crear un archivo tar con el archivo de configuración
    with tarfile.open(tar_path, 'w') as tar:
        tar.add(conf_file, arcname=f"syslog_{name}.conf")

    # Leer el archivo tar como bytes
    with open(tar_path, 'rb') as tar_file:
        tar_data = tar_file.read()


    docker_connection.put_archive(path=syslog_path, data=tar_data)

    code, result =docker_connection.exec_run("""cat /etc/syslog-ng/syslog-ng.conf""")

    syslog_include = '@include "/etc/syslog-ng/conf.d/*.conf"'
    if  re.search(syslog_include, result.decode()):
        code, result = docker_connection.exec_run(f"""echo {syslog_include} >> /etc/syslog-ng/syslog-ng.conf""")
        print(code)
        print(result)

    docker_connection.exec_run('service syslog-ng restart')

    # Eliminar los archivos temporales
    os.remove(conf_file)
    os.remove(tar_path)