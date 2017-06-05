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

|*Nombre* | *id*| evp | ks_v | kp_v | Kpp_v | v_sup | v_sub | v_supt | v_cau | Hu | Hg |
|--------:|----:|:---:|:----:|:----:|:-----:|:-----:|:-----:|:------:|:-----:|:--:|:--:|
|poca evp | 001 | 0.0002| 2.0|4.0|0.0|1.0|1.0|1.0|0.9|1.0|1.0|
|media evp | 001 | 0.0015| 2.0|4.0|0.0|1.0|1.0|1.0|0.9|1.0|1.0|
|alta evp | 001 | 0.0048| 2.0|4.0|0.0|1.0|1.0|1.0|0.9|1.0|1.0|
