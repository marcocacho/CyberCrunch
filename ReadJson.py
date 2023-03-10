import json
import NetworkDeploment.ConfigureRouter
"""
Se encarga de ir leyendo los distintos elementos de la red y ir configurandolos paso a paso:
Parametros de entrada:
    file: fichero donde se contiene la red que se desea desplegar
"""
def readJson (file):
    f = open(file, "r")
    network = json.load(f)
    for deviceType in network:
        if deviceType == "connection_list": # apartado de crear las conexiones entre maquinas
            print("connection_list")
        else: # apartado de crear los nodos y configurarlos
            machineType = network[deviceType]
            if machineType["machineType"] == "switch":
                print("switch")
            elif machineType["machineType"] == "router":
                print("router")
                settings = {"router": machineType["router"], "port": machineType["port"], "interfaces": machineType["interfaces"]}
                NetworkDeploment.ConfigureRouter.confIp(settings)
            elif machineType["machineType"] == "docker":
                print("docker")
    f.close()

if __name__ == "__main__":
    readJson("redPrueba.json")