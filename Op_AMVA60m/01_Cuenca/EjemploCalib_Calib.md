## Parametros Modelacion

Se indican parametros propios de la simulación, tales como $dt$ y $dx$:

### Param modelación

- **Dt[seg]**: 300
- **Dx[mts]**: 12.6
- **Almacenamiento medio**: True
- **Separar Flujos**: True
- **Retorno**: 1
- **Nodos Eval**: 1087
- **Qsim Name**: Qsim_Rain
- **Almacenamiento medio**: True


> Parametros que afectan directamente a la modelación, se encuentra el paso de tiempo, 
	si hay retorno o no, el nodo en el cual se evalua al modelo, y si se hacen ciertos 
	calculos dentro del modelo.

### Param Deslizamientos

- **Simular Deslizamientos**: True
- **Factor de Seguridad FS**: 0.5
- **Factor Corrector Zg**: 1.0

> Parametros para determinar si se hace modelación de deslizamientos o no, además se 
puede modificar el factor de seguridad mediante el cual se determina la vulnerabilidad 
de las celdas.

### Rutas

- **ruta_almsim**: /media/nicolas/Home/Jupyter/Soraya/Op_Alarmas/Op_AMVA60m/03_Resultados/03_almacenamiento/
	> Ruta en la cual se van a estar actualizando los almacenamientos del modelo.
- **ruta_almhist**: /media/nicolas/Home/Jupyter/Soraya/Op_Alarmas/Op_AMVA60m/03_Resultados/03_almacenamiento/01_almacenamiento_hist/
	> Ruta en la cual se van a estar actualizando los almacenamientos del modelo.
- **ruta_bkc_alm**: /media/nicolas/Home/Jupyter/Soraya/Op_Alarmas/Op_AMVA60m/01_Cuenca/02_BackSto/
	> Ruta en donde se encuentran las copias de almacenamiento que pueden remplazar a las operacionales
- **ruta_rainFile**: /media/nicolas/Home/Jupyter/Soraya/Op_Alarmas/Op_AMVA60m/03_Resultados/01_rain/Lluvia_actual.bin
	> Ruta donde se encuentra alojado el archivo de lluvia binario actual.
- **ruta_rainHistoryFile**: /media/nicolas/Home/Jupyter/Soraya/Op_Alarmas/Op_AMVA60m/03_Resultados/01_rain/Lluvia_historica.hdr
	> Archivo plano con historico de lluvia, se usa para evaluar reglas de actualizacion.
- **ruta_qsim**: /media/nicolas/Home/Jupyter/Soraya/Op_Alarmas/Op_AMVA60m/03_Resultados/02
	> Ruta en la cual se van a guardar los binarios con los caudales actuales simulados.
- **ruta_qsim_hist**: /media/nicolas/Home/Jupyter/Soraya/Op_Alarmas/Op_AMVA60m/03_Resultados/02CaudalHistorico/
	> Ruta en donde se actualizan los archivos historicos de caudales simulados 
- **ruta_slides**: /media/nicolas/Home/Jupyter/Soraya/Op_Alarmas/Op_AMVA60m/03_Resultados/04_slides/Slides_results.bin
	> Ruta donde se guarda el binario con los mapas de posible ocurrencia de deslizamientos.
- **ruta_qsim2Json**: /media/nicolas/Home/Jupyter/Soraya/Op_Alarmas/Op_AMVA60m/03_Resultados/02_caudal/Qsim_Rain_s_001.msg
	> Ruta de donde se toma los resultados de caudal actual de la parametrizacion que se va a montar en el .json
- **ruta_qhist2Json**: /media/nicolas/Home/Jupyter/Soraya/Op_Alarmas/Op_AMVA60m/03_Resultados/02CaudalHistorico/Qsim_Rain_s_001hist.msg
	> Ruta de donde se toma los resultados de caudal historicos de la parametrizacion que se va a montar en el .json
___
## Parametrizacion

|Nombre | id| evp | ks_v | kp_v | Kpp_v | v_sup | v_sub | v_supt | v_cau | Hu | Hg |
|--------:|----:|:---:|:----:|:----:|:-----:|:-----:|:-----:|:------:|:-----:|:--:|:--:|
| -c | 001 |0.001|150|1.0|0.0|0.6|4.0|0.3|0.99|1.0|1.0|
| -c | 002 |0.0005|180|15|0.0|0.5|4.0|0.3|0.99|1.5|1.0|
| -c | 003 |0.0001|120|10|0.0|0.4|2.5|0.2|0.99|1.0|1.0|
| -c | 004 |0.0003|129|5 |0.0|0.4|0.2|0.2|0.99|1.5|1.0|


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

|id| Nombre                   | Update | Tiempo[h] | Condicion  | Calib Actualiza | Back Sto        | Slides |
|:-:|:------------------------|:-------:|:------:|:----------:|:---------------:|:---------------:|:------:|
| -s 001| CuBarbosa_001_001.StObin | False    | 7     | No Rain Next 2h| 001          | Sto_wet-s01.StoBin | True|
| -s 002| CuBarbosa_001_002.StObin| False    | 5     | No Rain 4h| 002          | Sto_wet-s01.StoBin | True|
| -s 003| CuBarbosa_001_003.StObin | False    | 5    | No Rain 4h | 003          | None            | True  |
| -s 004| CuBarbosa_001_004.StObin | False   |  5     | No Rain 4h | 004          | Sto_wet-s03.StoBin | True  |


**Tabla**: Fechas de actualizacion de almacenamientos.

|id     | Nombre                 | Ultima Actualizacion |
|:-----:|:-----------------------|:--------------------:|
| -t 001|CuBarbosa_001_001.StObin|2017-09-20-15:50|
| -t 002|CuBarbosa_001_002.StObin|2017-09-20-15:35|
| -t 003|CuBarbosa_001_003.StObin|2017-09-20-15:35|
| -t 004|CuBarbosa_001_004.StObin|2017-09-20-15:35|
|

Indica las rutas en donde se hara lectura y guardado de almacenamiento por el modelo. En la 
siguiente tabla se presentan los nombres de los almacenamientos de entrada.  En la tabla se indica:

- **id**: del storage
- **Nombre**: del archivo con las condiciones.
- **Update**: este actualiza (True) o no (False) cada tanto, esto con la finalidad de corregir problemas producidos en el largo plazo.
- **Tiempo**: Cada cuanto se actualiza: Combinaciones tipo pandas (ej, 1h, 2.5h, 15min, etc).
- **Condicion**: Si hay alguna condición para que se de la actualización (se listan a continuación):
    - **No Rain Next Xh**: No se registren lluvias en las siguientes **X** horas.
    - **No Rain Last Xh**: No se registren lluvias en las ultimas **X** horas.
    - **No Rain Xh**: Que no se registren lluvias **X** horas alrededor de la fecha actual.
    > Se pueden incluir más definidas por el usuario.
- **Calib actualiza**: Calibracion a partrir de la cual se actualizan los estados del modelo.
- **Back Sto**: Archivo de background a partir del cual se cambian los estados del modelo cada **Tiempo** y con la **Condicion**.

Condiciones iniciales en caso de que no exista un binario establecido 
para alguno de los casos presentados en la tabla:

- **Inicial Capilar**:
- **Inicial Escorrentia**: 
- **Inicial Subsup**: 
- **Inicial Subterraneo**:
- **Inicial Corriente**: 

___
## Figuras

Dentro de este apartado se indican las rutas donde se guardan las figuras 
de las simulaciones y los mapas producidos por el modelo. Igualmente se 
indican cual de las parametrizaciones es la que se usa para graficar algunas 
de las variables tales como la animacion de caudales y la evolucion de la 
humedad en la cuenca.

- **ruta_map_qsim**: /media/nicolas/Home/Jupyter/Soraya/Op_Alarmas/Result_to_web/Res_OpAMVA60m/StreamMaps
	> ruta donde se guardan los mapas de caudales simulados. 
- **ruta_map_humedad**: /media/nicolas/Home/Jupyter/Soraya/Op_Alarmas/Result_to_web/Res_OpAMVA60m/HumedadMaps
	> Ruta donde se guardan los mapas de humedad.
- **ruta_map_riskvector**: /media/nicolas/Home/Jupyter/Soraya/Op_Alarmas/Result_to_web/Res_OpAMVA60m/risk_vector.png
- **ruta_map_slides**: /media/nicolas/Home/Jupyter/Soraya/Op_Alarmas/Result_to_web/Res_OpAMVA60m/SlidesMaps
	> Ruta donde se guardan los mapas de deslizamientos producidos por la modelación.
- **ruta_serie_qsim**: /media/nicolas/Home/Jupyter/Soraya/Op_Alarmas/Result_to_web/Res_OpAMVA60m/LevelsGraphs
	> Ruta donde se sgeneran las figuras de simulacion de caudales y niveles.
- **ruta_Json**: /media/nicolas/Home/Jupyter/Soraya/Op_Alarmas/Result_to_web/Res_OpAMVA60m/Qsim.json
	> Ruta donde se guarda el json con la Qsim de la parametrizacion escogida.

**Tabla**: Variables y parametrizaciones a plotear.

| Variable		  | Variable |
|:---------------:|:--------:|
| -p Qsim_map 		  | 001,002,003,004|
| -p Humedad_map 	  | 001,002,003,004|
| -p Slides 		  | 001,002,003,004|


