## Parametros Modelacion

Se indican parametros propios de la simulación, tales como $dt$ y $dx$:

### Param modelación

- **Dt[seg]**: 300
- **Dx[mts]**: 12.6
- **Retorno**: 1
- **Nodos Eval**: 1087
- **Qsim Name**: Qsim_Rain
- **Almacenamiento medio**: True
- **Separar Flujos**: True

> Parametros que afectan directamente a la modelación, se encuentra el paso de tiempo, 
	si hay retorno o no, el nodo en el cual se evalua al modelo, y si se hacen ciertos 
	calculos dentro del modelo.

### Param Deslizamientos

- **Simular Deslizamientos**: True
- **Factor de Seguridad FS**: 0.5

> Parametros para determinar si se hace modelación de deslizamientos o no, además se 
puede modificar el factor de seguridad mediante el cual se determina la vulnerabilidad 
de las celdas.

### Rutas

- **ruta_almacenamiento**: /home/nicolas/ProyectosGIT/Op_Alarmas/01_Cuenca/
	> Ruta en la cual se van a estar actualizando los almacenamientos del modelo.
- **ruta_bkc_alm**: /home/nicolas/ProyectosGIT/Op_Alarmas/01_Cuenca/03_BackSto/
	> Ruta en donde se encuentran las copias de almacenamiento que pueden remplazar a las operacionales
- **ruta_rainFile**: /home/nicolas/ProyectosGIT/Op_Alarmas/03_Resultados/01_Rain/Lluvia_actual.bin
	> Ruta donde se encuentra alojado el archivo de lluvia binario actual.
- **ruta_rainHistoryFile**: /home/nicolas/ProyectosGIT/Op_Alarmas/03_Resultados/01_Rain/Lluvia_historica.hdr
	> Archivo plano con historico de lluvia, se usa para evaluar reglas de actualizacion.
- **ruta_qsim**: /home/nicolas/ProyectosGIT/Op_Alarmas/03_Resultados/02_Caudal/
	> Ruta en la cual se van a guardar los binarios con los caudales actuales simulados.
- **ruta_qsim_hist**: /home/nicolas/ProyectosGIT/Op_Alarmas/03_Resultados/03_CaudalHistorico/
	> Ruta en donde se actualizan los archivos historicos de caudales simulados (**.csv**)
- **ruta_slides**: /home/nicolas/ProyectosGIT/Op_Alarmas/03_Resultados/Slides_map.bin
	> Ruta donde se guarda el binario con los mapas de posible ocurrencia de deslizamientos.
___
## Calibracion

|Nombre | id| evp | ks_v | kp_v | Kpp_v | v_sup | v_sub | v_supt | v_cau | Hu | Hg |
|--------:|----:|:---:|:----:|:----:|:-----:|:-----:|:-----:|:------:|:-----:|:--:|:--:|
| -c poca evp | 001 | 0.0002| 2.0|4.0|0.0|1.0|1.0|1.0|0.9|1.0|1.0|
| -c media evp | 002 | 0.0015| 2.0|4.0|0.0|1.0|1.0|1.0|0.9|1.0|1.0|
| -c alta evp | 003 | 0.0048| 2.0|4.0|0.0|1.0|1.0|1.0|0.9|1.0|1.0|

La calibración se compone de 10 parámetros escalares, los cuales son:

- R[1] : Evaporación.
- R[2] : Infiltración.
- R[3] : Percolación.
- R[4] : Pérdidas.
- R[5] : Vel Superficial.
- R[6] : Vel Sub-superficial.
- R[7] : Vel Subterranea.
- R[8] : Vel Cauces.
- R[9] : Alm capilar maximo.
- R[10] : Alm gravitacional maximo.

Los valores de calibración varían de acuerdo a la escala temporal y 
espacial de ejecución del modelo.  Cada uno de estos parámetros es 
multiplicado como un escalar por el mapa que componga una variable **X**
del modelo. 
___
## Almacenamiento 

**Tabla**: almacenamientos de ejecuciones.

|id| Nombre                   | Si o No | Tiempo | Condicion  | Calib Actualiza | Back Sto        | Slides |
|:-:|:------------------------|:-------:|:------:|:----------:|:---------------:|:---------------:|:------:|
| -s 001| Sto_wet_c01_s01.StObin | True    | 4h     | No Rain, 2h| 001          | Sto_wet-s01.StoBin | True|
| -s 002| Sto_wet_c01_s02.StObin | False   | 4h     | No Rain, 2h| 001          | None            | False  |
| -s 003| Sto_wet_c01_s03.StObin | False   | 4h     | No Rain, 2h| 001          | None            | False  |
| -s 004| Sto_wet_c02_s01.StObin | True    | 4h     | No Rain, 2h| 002          | Sto_wet-s02.StoBin | True|
| -s 005| Sto_wet_c02_s02.StObin | False   | 4h     | No Rain, 2h| 002          | None            | False  |
| -s 006| Sto_wet_c02_s03.StObin | False   | 4h     | No Rain, 2h| 002          | None            | False  |
| -s 007| Sto_wet_c03_s01.StObin | True    | 4h     | No Rain, 2h| 003          | Sto_wet-s03.StoBin | True|
| -s 008| Sto_wet_c03_s02.StObin | False   | 4h     | No Rain, 2h| 003          | None            | False  |
| -s 009| Sto_wet_c03_s03.StObin | False   | 4h     | No Rain, 2h| 003          | None            | False  |

**Tabla**: Fechas de actualizacion de almacenamientos.

|id     | Nombre                 | Ultima Actualizacion |
|:-----:|:-----------------------|:--------------------:|
| -t 001| Sto_wet_c01_s01.StObin |2017-06-09-10:10      |
| -t 002| Sto_wet_c01_s02.StObin |2017-06-09-10:10      |
| -t 003| Sto_wet_c01_s03.StObin |2017-06-09-10:10      |
| -t 004| Sto_wet_c02_s01.StObin |2017-06-09-10:10      |
| -t 005| Sto_wet_c02_s02.StObin |2017-06-09-10:10      |
| -t 006| Sto_wet_c02_s03.StObin |2017-06-09-10:10      |
| -t 007| Sto_wet_c03_s01.StObin |2017-06-09-10:10      |
| -t 008| Sto_wet_c03_s02.StObin |2017-06-09-10:10      |
| -t 009| Sto_wet_c03_s03.StObin |2017-06-09-10:10      |

Indica las rutas en donde se hara lectura y guardado de almacenamiento por el modelo. En la 
siguiente tabla se presentan los nombres de los almacenamientos de entrada.  En la tabla se indica:

- **id**: del storage
- **Nombre**: del archivo con las condiciones.
- **Si o No**: este actualiza (True) o no (False) cada tanto, esto con la finalidad de corregir problemas producidos en el largo plazo.
- **Tiempo**: Cada cuanto se actualiza: Combinaciones tipo pandas (ej, 1h, 2.5h, 15min, etc).
- **Condicion**: Si hay alguna condición para que se de la actualización (se listan a continuación):
    - **No Rain, Xh**: Que no se registren lluvias **X** horas alrededor de la fecha actual.
    - **Every Xh**: Independiente de la lluvia actualiza cada **X** horas.
    - **Every Ejec**: En cada ejecución.
- **Calib actualiza**: Calibracion a partrir de la cual se actualizan los estados del modelo.
- **Back Sto**: Archivo de background a partir del cual se cambian los estados del modelo cada **Tiempo** y con la **Condicion**.

Condiciones iniciales en caso de que no exista un binario establecido 
para alguno de los casos presentados en la tabla:

- **Inicial Capilar**: 10
- **Inicial Escorrentia**: 0.01
- **Inicial Subsup**: 7
- **Inicial Subterraneo**: 50
- **Inicial Corriente**: 0.1

**Tabla**: Ultima actualizacion

