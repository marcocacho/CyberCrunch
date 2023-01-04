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
def main(lab):

    # Añadimos un shitch al proyecto
    print("Lista de switches:")
    for template in gns3_server.get_templates():
        #if "switch" in template["name"]:
            print(f"Template: {template['name']} -- ID: {template['template_id']}")

    lab.create_node(name = 'test-switch01', template = 'Ethernet switch')



if __name__ == '__main__':
    # Inicializamos la API de GNS3
    gns3_server = Gns3Connector(url="http://127.0.0.1:3080")
    lab: Project = openProyect(gns3_server, "test_lab")
    main(lab)


