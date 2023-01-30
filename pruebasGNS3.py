from gns3fy import Gns3Connector, Project, Node, Link

#funcion para abrir un proyecto, devuelve el proyecto solicitado por nombre
def openProyect(conector, nombre):
    lab = Project(name=nombre, connector=conector)
    try:
        lab.get()
        lab.open()
    except:
        lab.create()
    print(f"Se abre el proyecto {nombre}.")
    return lab
#Crea un enlace entre dos Switches
#Es una funcion estatica
def CreateLinks(lab, server):

    # Añadimos un shitch al proyecto
    print("Lista de switches:")
    for template in gns3_server.get_templates():
        #if "switch" in template["name"]:
            print(f"Template: {template['name']} -- ID: {template['template_id']}")

    #crea un nodo con el nombre dado y del tipo proporcionado en el template
    #lab.create_node(name = 'test-switch2', template = 'Ethernet switch')

    nodos = lab.nodes
    #listamos los nodos del proyecto
    for node in lab.nodes:
        print(f"Node: {node.name} -- Node Type: {node.node_type} -- Status: {node.status}")
    """
    for nodo in nodos:
        print(nodo.ports)
    """
    #creamos un link entre dos nodos, se necesita conocer: node_id, adapter_number, port_number
    #Se seleciona los elementos
    nodes = [
        dict(node_id=nodos[0].node_id, adapter_number=0, port_number=0),
        dict(node_id=nodos[1].node_id, adapter_number=0, port_number=0)]

    #Se crea el enlace entre los nodos
    #link = Link(project_id=lab.project_id, connector=server, nodes=nodes)
    #link.create()

#recibe la ruta de una maquina virtual y la añade a gns3 para poder crear nodos.
def AddVitualPC(nombre, ruta, server):
    server.create_template(name=nombre, template_type="qemu", hda_disk_image=ruta)

def main(lab, server):
    print("Nodos posibles del servidor")
    for template in server.get_templates():
        print(f"Template: {template['name']} -- ID: {template['template_id']}")

    print("Nodos en el del proyecto")
    for node in lab.nodes:
        print(f"Node: {node.name} -- Node Type: {node.node_type} -- Status: {node.status}")


if __name__ == '__main__':
    # Inicializamos la API de GNS3
    gns3_server = Gns3Connector(url="http://127.0.0.1:3080")
    lab: Project = openProyect(gns3_server, "test_lab")
    main(lab, gns3_server)

    #localizacion maquinas virtuales por defecto (/var/lib/libvirt/nombreMaquina), permisos de superusuario
    #AddVitualPC("maquina prueba", "/var/lib/libvirt/images/ubuntu20.04.qcow2", gns3_server)
    AddVitualPC("Permisos777", "/home/marco/ubuntu20.04.qcow2", gns3_server)




