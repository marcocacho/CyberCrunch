
def manageMachines(name, lab, action):
    """
    Funcion encargada de encender, apagar o reiniciar una maquina
    :param name: nombre del nodo de la red sobre el que se quiere actuar
    :param lab: laboratorio de gns3
    :param action: accion que se quiere realizar (start, stop, reload, suspend, delete, status)
    :return: None
    """
    node = lab.get_node(name)
    action_dict = {"start": node.start(),
                   "stop": node.stop(),
                   "reload": node.reload(),
                   "suspend": node.suspend(),
                   "delete": node.delete()}
    action_dict[action]


