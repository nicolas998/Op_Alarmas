## Parametros Modelacion

Se indican parametros propios de la simulación, tales como $dt$ y $dx$:

### Param modelación

- **Dt[seg]**: 300
- **Dx[mts]**: 12.6
- **Retorno**: 1
- **Almacenamiento medio**: True
- **Separar Flujos**: True
- **ruta_almacenamiento**: /home/nicolas/ProyectosGIT/Op_Alarmas/01_Cuenca/
- **ruta_out_alm**: /home/nicolas/ProyectosGIT/Op_Alarmas/01_Cuenca/03_TempSto/
- **ruta_rainFile**: /home/nicolas/ProyectosGIT/Op_Alarmas/03_Resultados/01_Rain/Lluvia_actual.bin

### Param Deslizamientos

- **Simular Deslizamientos**: True
- **Factor de Seguridad FS**: 1.5

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

| Descripcion     | id | Nombre           | Si o No | Tiempo | Condicion  | Calib Actualiza |
|--------------:|:---:|:-----------------|:-------:|:------:|:---------:|:-----:|
|-s Cond humedas |001| Storage_wet_ope1.sto | True    | 4h     | Every Ejec| 001 |
|-s Cond humedas |002| Storage_wet_ope2.sto | True    | 4h     | Every Ejec| 001 |
|-s Cond humedas |003| Storage_wet_ope3.sto | True    | 4h     | Every Ejec| 002 |
|-s Cond humedas |004| Storage_wet1.sto | False   | 4h     | No Rain, 2h| NaN |
|-s Cond humedas |005| Storage_wet2.sto | False   | 4h     | No Rain, 2h| NaN |
|-s Cond humedas |006| Storage_wet3.sto | False   | 4h     | No Rain, 2h| NaN |


Indica las rutas en donde se hara lectura y guardado de almacenamiento por el modelo. En la 
siguiente tabla se presentan los nombres de los almacenamientos de entrada.  En la tabla se indica:

- Descripción de las condiciones de humedad.
- Nombre del archivo con las condiciones.
- Si este actualiza (True) o no (False).
- Cada cuanto se actualiza: Combinaciones tipo pandas (ej, 1h, 2.5h, 15min, etc).
- Si hay alguna condición para que se de la actualización (se listan a continuación):
    - **No Rain, Xh**: Que no se registren lluvias **X** horas alrededor de la fecha actual.
    - **Every Xh**: Independiente de la lluvia actualiza cada **X** horas.
    - **Every Ejec**: En cada ejecución.

Condiciones iniciales en caso de que no exista un binario establecido 
para alguno de los casos presentados en la tabla:

- **Inicial Capilar**: 10
- **Inicial Escorrentia**: 0.01
- **Inicial Subsup**: 7
- **Inicial Subterraneo**: 50
- **Inicial Corriente**: 0.1
