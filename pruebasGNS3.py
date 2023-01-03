from gns3fy import Gns3Connector, Project, Node, Link

def main():
    #comprobamos la version
    print("Version: ")
    print(gns3_server.get_version())

    # Creamos un proyecto con el nombre "Mi proyecto"
    print('Se crea el proyecto test_lab, estado:')
    print(lab.status)


    # Añadimos un shitch al proyecto



    # print("Lista de switches:")
    for template in gns3_server.get_templates():
        if "switch" in template["name"]:
            print(f"Template: {template['name']} -- ID: {template['template_id']}")

    lab.create_node(name = 'test-switch01', template = 'Ethernet switch')

"""    
Template: Ethernet switch -- ID: 1966b864-93e7-32d5-965f-001384eec461
Template: Frame Relay switch -- ID: dd0f6f3a-ba58-3249-81cb-a1dd88407a47
Template: ATM switch -- ID: aaa764e2-b383-300f-8a0e-3493bbfdb7d2


    gns3_server.get_template_by_name("Ethernet switch")
    {'builtin': True,
     'category': 'switch',
     'console_type': 'none',
     'name': 'Ethernet switch',
     'symbol': ':/symbols/ethernet_switch.svg',
     'template_id': '1966b864-93e7-32d5-965f-001384eec461',
     'template_type': 'ethernet_switch'}
"""
    #borro el proyecto.


if __name__ == '__main__':
    # Inicializamos la API de GNS3
    gns3_server = Gns3Connector(url="http://127.0.0.1:3080")
    lab = Project(name="test_lab", connector=gns3_server)
    #lab.__dict__.pop("__pydantic_initialised__")
    #lab.create()
    lab.get()

    main()


