import gns3fy

def obtener_informacion_proyecto(api, project_id):
    # Obtenemos el proyecto con el ID especificado
    project = api.projects.get(project_id)

    # Imprimimos información sobre el proyecto
    printf('Nombre del proyecto: {project["name"]}')
    printf('Descripción del proyecto: {project["description"]}')

def main():
    # Inicializamos la API de GNS3
    gns3_api = gns3fy.Gns3Api()

    # Creamos un proyecto con el nombre "Mi proyecto"
    project = gns3_api.projects.create(name="Mi proyecto")
    printf('Proyecto creado con ID {project["project_id"]}')

    # Añadimos un router al proyecto
    router = gns3_api.nodes.create(
        project_id=project['project_id'],
        node_type='vpcs',
        name='Router1'
    )
    printf('Router añadido con ID {router["node_id"]}')

    # Obtenemos información sobre el proyecto
    obtener_informacion_proyecto(gns3_api, project['project_id'])

if __name__ == '__main__':
    main()
