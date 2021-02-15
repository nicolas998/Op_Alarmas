# 02_Codigos

Contiene los scripts utilizados para la ejecución operacional del modelo,
desde la transformación de la lluvia, la simulación, escribir resultados y actualizar 
estados y series simuladas.

-**Cron**: Codigo escrito para ser ejecutado mediante cronetab.
-**Rain**: Codigo escrito para el analisis de la lluvia.
-**Ejec**: Codigo escrito para la ejecución del modelo como tal.
-**Graph**: Código escrito para la realización de figuras y gráficas.

De manera adicional se cuenta con un archivo llamado: **New_Project.py**, 
este archivo sólo es ejecutado en la primera ocasión que se monta un proyecto, mediante 
este se establecen variables tales como:

- La lluvia histórica de los últimos 3 días.
- El caudal Observado histórcio.

