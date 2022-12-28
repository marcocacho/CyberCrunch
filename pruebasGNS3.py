from gns3fy import Gns3Connector, Project

def obtener_informacion_proyecto(api, project_id):
    # Obtenemos el proyecto con el ID especificado
    project = api.projects.get(project_id)

    # Imprimimos información sobre el proyecto
    printf('Nombre del proyecto: {project["name"]}')
    printf('Descripción del proyecto: {project["description"]}')

def main():
    # Inicializamos la API de GNS3
    gns3_server = Gns3Connector(url="http://127.0.0.1:3080")
    print(gns3_server.get_version())
"""
    # Creamos un proyecto con el nombre "Mi proyecto"
    lab = Project(name="test_lab", connector=gns3_server)
    lab.create()
    printf('Se crea el proyecto test_lab')
"""
    # Añadimos un router al proyecto
"""
    router = gns3_api.nodes.create(
        project_id=project['project_id'],
        node_type='vpcs',
        name='Router1'
    )
    printf('Router añadido con ID {router["node_id"]}')
"""
    # Obtenemos información sobre el proyecto
#    obtener_informacion_proyecto(gns3_api, project['project_id'])

if __name__ == '__main__':
    main()
