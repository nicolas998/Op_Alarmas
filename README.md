# Op_Alarmas

Respositorio que nace del repositorio anterior **Op_Radar**, en este se busca corregir 
algunos problemas que se dejaron en el anterior y agregar nuevas funcionalidades, de igual 
manera se busca presentar una herramienta de fácil replicaciion a diferentes cuencas, 
sin la necesidad de un gran esfuerzo más que la edición de algunas rutas y archivos.

Las funciones necesarias para la ejecución del esquema operacional se alojan en alarmas.py, codigo base de repo de Alarmas.

La estructura de cada carpeta-cuenca en este repo es:

-**Rutas.md**: Archivo de texto plano con las rutas de configuracion base para la ejecución.
- **01_Cuenca**: contiene toda la información referente a la cuenca que se esta simulando: el archivo **.nc** de ejecución,
el archivo **Config.md** que aloja las parametrizaciones y todas las condiciones de ejecución, los estados de almacenamiento actualizados y 
demás archivos de respaldo.
- **02_Codigos**: Contiene los codigos de ejecución.
- **03_Resultados**: Carpeta en donde se alojaran los resultados de modelación. 
