# CyberCrunch: Herramienta para despliegue y operación de laboratorios de ciberseguridad

¡Bienvenido a CyberCrunch! Esta herramienta te permite desplegar, controlar y monitorizar redes virtuales, especialmente diseñadas para laboratorios de ciberseguridad. Sin embargo, sus aplicaciones van más allá y se adaptan a diversas necesidades.

## Descripción

CyberCrunch es una herramienta versátil que facilita el despliegue de redes virtuales, el control de las mismas y su monitorización. Su objetivo principal es crear laboratorios de ciberseguridad, brindando un entorno seguro y controlado para realizar pruebas y experimentos.

Esta herramienta usa GNS3 para virtualizar las redes y nodos.

Principales características:

- **Despliegue de redes virtuales:** Con CyberCrunch, puedes crear redes virtuales con facilidad, configurando los parámetros necesarios y estableciendo la topología deseada.
- **Control y monitorización:** La herramienta te permite tener un control completo sobre las redes desplegadas, así como monitorizar el tráfico, los dispositivos conectados y otros aspectos relevantes.
- **Laboratorios de ciberseguridad:** CyberCrunch está especialmente diseñado para la creación de laboratorios de ciberseguridad, donde los profesionales pueden simular escenarios y realizar pruebas de penetración, análisis de vulnerabilidades y otros tipos de evaluaciones.
- **Amplia utilidad:** Aunque su enfoque principal es la ciberseguridad, CyberCrunch puede adaptarse a otras necesidades, como la creación de redes de pruebas, entornos de desarrollo virtualizados y configuraciones de red personalizadas.

## Instrucciones de uso

Puedes encontrar en el archivho `LaboratoryFormat.txt` una explicacion de como crear el json, tambien puedes usar el archivo `redPrueba.json` para crear una red de ejemplo

Para utilizar CyberCrunch, se proporcionan los siguientes comandos en Python 3:

- **ConfigureNetwork.py:** Este script se encarga de configurar una red virtual utilizando un archivo JSON llamado `network.json`. Ejecuta el siguiente comando:

  ```bash
  python3 ConfigureNetwork.py network.json
  ```

  - **LabInfoUtils.py:** Este script contiene varias utilidades relacionadas con los laboratorios. Aquí tienes dos ejemplos de comandos:

   -- Imprimir información sobre una red específica (`red`), utilizando el conector GNS3 y un nodo específico:
    ```bash
    python3 LabInfoUtils.py print red conectorGns3 node
    ```
    --Exportar información sobre un laboratorio específico (`labname`) utilizando el conector GNS3:
     ```bash
     python3 LabInfoUtils.py export conectorGns3 labname
     ```

Recuerda instalar las dependencias necesarias antes de ejecutar los comandos. Puedes encontrar los requisitos en el archivo `requirements.txt`.

## Contribución

Si deseas contribuir al desarrollo de CyberCrunch, ¡eres bienvenido! Siéntete libre de enviar pull requests y reportar problemas en el repositorio oficial de CyberCrunch en GitHub.

***
## Conclusion
Esperamos que disfrutes usando CyberCrunch y que te sea de gran utilidad en tus proyectos de ciberseguridad y redes virtuales.
