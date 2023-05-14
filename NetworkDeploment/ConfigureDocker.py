import docker

"""
Libreria de funciones para configurar un docker activo
"""


def connectDocker(id, ip=None, port=2376):
    """
    Se conecta a un router a traves de telnet desplegado en gns3 instalado en la maquina local.
    :param id: id del docker al que se quiere conectar
    :param ip: ip del equipo donde se esta ejecutnado docker
    :param port: puerto donde se esta escuchando, por defecto el 2376
    :return: conector al docker
    """
    if ip is not None:
        client = docker.DockerClient(base_url=f'tcp://{ip}:{port}', tls=False)
    else:
        client = docker.from_env()
    return client.containers.get(id)


def configIp(settings, docker_id):
    """
    Configura la ip de un docker a traves de telnet
    :param settings: diccionario con los datos de configuracion del docker
        claves:
            - iface: interfaz del router (formatos validos fa 0/0 y fast ethernet 0/0)
            - ip: ip de la interfaz o dhcp para usar un servidor dhcp
            - netmask(optional): mascara de la red
            - gateway(optional): router de salida
    :param docker_id: id del docker que se quiere configurar
    :return: None
    """

    docker_connection = connectDocker(docker_id)
    if settings["ip"].lower() == "dhcp":
        config_iface = "dhclient %s" % settings["iface"]
    else:
        config_iface = ["ifconfig %s up" % settings["iface"],
                        "ifconfig %s %s netmask %s" % (settings["iface"], settings["ip"], settings["netmask"]),
                        "route add default gw %s %s" % (settings["gateway"], settings["iface"])]

    for command in config_iface:
        docker_connection.exec_run(command)

def configSyslog(docker_id, ip_opensearch, port_opensearh, lab_name, settings=None):
    """
    Configura el servicio de syslog-ng en el equipo y activa el servicio para enviar los datos a un servidor de opensearch.
    Por defecto se van a monitorizar system e internal, aunque se puede añadir mas opicones dentro de settings
    :param docker_id: id del docker que se quiere configurar
    :param ip_opensearch: ip del servidor donde se encuentra opensearh
    :param port_opensearh: puerto por el que se quieren enviar los datos
    :param lab_name: nombre del laboratorio para crear su propio indice
    :param settings: array con diccionario con los datos de configuracion del docker, se puede añadir ficheros,
        claves:
            + nombre: nombre para el recurso a monitorizar
            + type: tipo de dato para syslog
            + log: ruta absoluta del log o fichero a monitorizar
    :return: None
    """
    if settings is None:
        settings = []
    syslog_route = "/etc/syslog-ng/conf.d"
    conf_file = "opensearch.conf"

    destination = f'''destination d_opensearch_http {{
    elasticsearch-http(
        index("{lab_name}")
        type("")
        url("https://{ip_opensearch}:{port_opensearh}/_bulk")
        user("admin")
        pasword("admin")
        template("$(format-json --scope rfc5424 --scope dot-nv-pairs --rekey .* --shift 1 --scope nv-pairs --exclude DATE @timestamp=${{ISODATE}})")
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
    code, result = docker_connection.exec_run(f'''mkdir -p {syslog_route}''')
    command = f'''echo '{destination}' >> {syslog_route}/{conf_file}'''
    print(command)
    code, result = docker_connection.execute(command)
    print(code)
    print(result)
    for data in settings:
        code, result = docker_connection.exec_run(f"""echo '{source.format(data['name'], data['type'], data['log'])}' >> {syslog_route}/{conf_file}""")
        code, result = docker_connection.exec_run(f'''echo '{log.format('s_'+data['name'])}' >> {syslog_route}/{conf_file}''')


