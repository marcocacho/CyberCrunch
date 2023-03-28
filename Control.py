
def manageMachines(name, lab, action):
    """
    Funcion encargada de modifica una maquina de un proyencto de gns3
    :param name: nombre del nodo de la red sobre el que se quiere actuar
    :param lab: laboratorio de gns3
    :param action: accion que se quiere realizar (start, stop, reload, suspend, delete, status)
    :return: None
    """
    node = lab.get_node(name)
    if node is not None:
        action_dict = {"start": node.start,
                       "stop": node.stop,
                       "reload": node.reload,
                       "suspend": node.suspend,
                       "delete": node.delete}
        select = action_dict.get(action)
        if select is not None:
            select()
        else:
            print("No se encontro accion " + action)
    else:
        print("No existe el nodo seleccionado")

