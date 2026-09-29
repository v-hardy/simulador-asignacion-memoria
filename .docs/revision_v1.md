Sí: comparando tu implementación con la consigna, **tenés una base bastante avanzada**, pero hay varios puntos importantes que corregir para que realmente cumpla con el TPI. El más importante es que actualmente **no estás implementando Best-Fit**, sino First-Fit. Además, hay un par de errores en la lógica de admisión, SRTF y liberación de memoria.

## 1. Lo que ya cumple

Tu programa ya tiene implementado:

- Memoria principal de **550K**, con:
  
  - 100K para SO.
  
  - 450K para usuarios.

- Memoria auxiliar para procesos suspendidos.

- Estados:
  
  - Nuevo
  
  - Listo
  
  - Listo/Suspendido
  
  - Ejecución
  
  - Terminado

- Límite de 5 procesos entre:
  
  - Ejecución
  
  - Listos
  
  - Listos/Suspendidos

- Carga de procesos desde archivo.

- Planificación **SRTF** en principio.

- Liberación y fusión de huecos.

- Informe de:
  
  - Tiempo de retorno.
  
  - Tiempo de espera.
  
  - Promedios.
  
  - Rendimiento.

- Ejecución interactiva mediante `input()`, lo cual va en la dirección correcta para la consideración de que **no debe ser una corrida ininterrumpida**.

Pero hay cuestiones que conviene corregir.

---

# 2. El problema más importante: no estás usando Best-Fit

Actualmente tenés:

```
for particion in memoriaPrincipal:
    if particion["tipo"] == "hueco":
      if particion["limite"] < proceso["tam"]:
        continue
      ...
      pcb["id"] = particion["id"]
```

Esto toma **el primer hueco suficientemente grande** que encuentra.

Eso es **First-Fit**.

La consigna exige:

> La política de asignación de memoria será Best-Fit.

Best-Fit significa:

> Buscar entre todos los huecos disponibles aquel que sea suficientemente grande y que deje la menor cantidad de espacio sobrante.

Por ejemplo:

```
Huecos:

100K
250K
150K
300K

Proceso = 140K
```

Best-Fit debe elegir:

```
150K
```

porque deja solamente:

```
150 - 140 = 10K
```

Tu código elegiría el primer hueco que encuentre, que podría ser el de 250K.

### Cómo corregirlo

Podés cambiar `cargarEnMemoria()` para primero buscar el mejor hueco:

```
def buscarMejorHueco(tamano):
    mejorHueco = None

    for particion in memoriaPrincipal:
        if particion["tipo"] == "hueco" and particion["limite"] >= tamano:
            if mejorHueco is None or particion["limite"] < mejorHueco["limite"]:
                mejorHueco = particion

    return mejorHueco
```

Y después:

```
def cargarEnMemoria(proceso):
    global idPrincipal, idAuxiliar

    particion = buscarMejorHueco(proceso["tam"])

    if particion is not None:
        pcb = {
            "id": particion["id"],
            "idp": proceso["id"],
            "tipo": "proceso",
            "base": particion["base"],
            "limite": proceso["tam"]
        }

        indice = memoriaPrincipal.index(particion)

        if particion["limite"] > proceso["tam"]:
            hueco = {
                "id": idPrincipal,
                "idp": -1,
                "tipo": "hueco",
                "base": particion["base"] + proceso["tam"],
                "limite": particion["limite"] - proceso["tam"]
            }

            idPrincipal += 1

            memoriaPrincipal.insert(indice + 1, hueco)

        memoriaPrincipal[indice] = pcb

        registrarEvento(
            f"Proceso {proceso['id']} ha sido cargado en memoria principal."
        )

        return colaListo

    registrarEvento(
        f"No hay suficiente memoria principal para admitir el proceso {proceso['id']}."
    )

    nuevaBase = (
        memoriaAuxiliar[-1]["base"] + memoriaAuxiliar[-1]["limite"]
        if memoriaAuxiliar
        else 0
    )

    pcb = {
        "id": idAuxiliar,
        "idp": proceso["id"],
        "tipo": "proceso",
        "base": nuevaBase,
        "limite": proceso["tam"]
    }

    idAuxiliar += 1
    memoriaAuxiliar.append(pcb)

    registrarEvento(
        f"Proceso {proceso['id']} ha sido cargado en memoria auxiliar."
    )

    return colaListoySuspendido
```

Con esto sí estarías haciendo Best-Fit.

---

# 3. Tu duda sobre `base` y `limite`

Preguntaste:

> `ACA NO ESTARIA SUMANDO VALORES DE PUNTO EN VEZ DE "MODULOS"?`

No. **La suma que hacés está bien conceptualmente.**

Por ejemplo:

```
Hueco anterior:
base = 100
limite = 50

Proceso:
base = 150
limite = 100
```

Al liberar el proceso:

```
particion["base"] = memoria[indice - 1]["base"]
particion["limite"] += memoria[indice - 1]["limite"]
```

queda:

```
base = 100
limite = 150
```

Eso representa:

```
100 ─────────────── 250
     150K
```

Acá `limite` en tu programa está funcionando realmente como **tamaño**, no como dirección límite.

Y eso es importante.

La consigna pide:

> Id de partición, dirección de comienzo de partición, tamaño de la partición, id de proceso asignado, fragmentación interna.

Por eso te recomiendo renombrar:

```
"limite"
```

a:

```
"tam"
```

o:

```
"tamanio"
```

Porque en tu implementación:

```
"base": 100,
"limite": 450
```

significa:

```
Base = 100
Tamaño = 450
```

y **no**:

```
Base = 100
Límite = 450
```

Si fuera una dirección límite, la partición sería solamente de 350K.

---

# 4. Tu tabla de memoria no coincide exactamente con la consigna

Actualmente imprimís:

```
ID IDP TIPO BASE LÍMITE
```

Pero el TPI pide:

```
Id de partición
Dirección de comienzo
Tamaño de partición
Id de proceso
Fragmentación interna
```

Debería ser algo como:

```
ID    BASE    TAM    IDP    FRAG
0     0       100    SO     0
1     100     120    3      0
2     220     80     5      0
3     300     250    -      0
```

Podrías tener:

```
def imprimirMemoria(memoria):
    print("ID\tBASE\tTAM\tIDP\tFRAG")

    for particion in memoria:
        if particion["tipo"] == "so":
            idp = "SO"
            frag = 0
        elif particion["tipo"] == "hueco":
            idp = "-"
            frag = 0
        else:
            idp = particion["idp"]
            frag = 0

        print(
            f"{particion['id']}\t"
            f"{particion['base']}\t"
            f"{particion['limite']}\t"
            f"{idp}\t"
            f"{frag}"
        )
```

---

# 5. Ojo con la fragmentación interna

Con **MVT / particiones variables**, normalmente la memoria asignada a un proceso se ajusta exactamente a su tamaño.

Por ejemplo:

```
Proceso = 120K

Partición asignada = 120K
```

Entonces:

```
Fragmentación interna = 0K
```

Si ustedes no tienen algún mecanismo de redondeo/alineación especificado por la cátedra, **no deberías inventar fragmentación interna**.

La fragmentación que vas a tener principalmente es **externa**, representada por los huecos.

Por ejemplo:

```
SO | P1 | HUECO | P2 | HUECO
```

Esos huecos son fragmentación externa.

---

# 6. Hay un problema importante en `admitirProcesos()`

Tenés:

```
cantidadProcesos = lambda : len(colaListo) + len(colaListoySuspendido) + 1 if procesoEjecutando else 0
```

Esto funciona de forma extraña.

Si hay proceso ejecutando:

```
len(colaListo) + len(colaListoySuspendido) + 1
```

pero si **no** hay proceso ejecutando devuelve:

```
0
```

Por lo tanto, si la CPU está libre, aunque tengas 4 procesos en Listos/Suspendidos:

```
cantidadProcesos() = 0
```

Eso no representa la cantidad real.

Debería ser:

```
def cantidadProcesosAdmitidos():
    return (
        len(colaListo)
        + len(colaListoySuspendido)
        + (1 if procesoEjecutando is not None else 0)
    )
```

Y:

```
def admitirProcesos():
    while (
        len(colaNuevo) > 0
        and cantidadProcesosAdmitidos() < 5
    ):
        proceso = colaNuevo.pop(0)

        cola = cargarEnMemoria(proceso)

        ordenarProcesoEnCola(cola, proceso)

        registrarEvento(
            f"Proceso {proceso['id']} ha sido admitido."
        )
```

Esto sí representa exactamente la regla:

```
Ejecutando + Listos + Listos/Suspendidos <= 5
```

---

# 7. Hay otro problema con los procesos que no entran en memoria

Supongamos:

```
450K disponibles
```

y llega:

```
P1 = 400K
P2 = 100K
```

P1 entra.

P2 no entra:

```
P2 → memoria auxiliar
```

Eso está bien.

Pero después liberás memoria:

```
particion = liberarMemoria(procesoEjecutando, memoriaPrincipal)
reasignarMemoriaPrincipal(particion)
```

La idea es correcta.

El problema es que `reasignarMemoriaPrincipal()` está buscando un proceso suspendido dentro de **una única partición liberada**.

Con Best-Fit esto puede funcionar, pero hay que asegurarse de que después de fusionar los huecos, la partición pasada sea realmente el hueco completo.

---

# 8. Hay un problema potencial en `liberarMemoria()`

Esta parte:

```
for particion in memoria:
    if particion["idp"] == proceso["id"]:
```

está bien.

Pero después hacés varias veces:

```
memoria.index(particion)
```

mientras estás modificando la lista.

Es bastante frágil.

Te conviene obtener el índice una sola vez:

```
def liberarMemoria(proceso, memoria):
    for i, particion in enumerate(memoria):

        if particion["idp"] != proceso["id"]:
            continue

        particion["tipo"] = "hueco"
        particion["idp"] = -1

        # Fusionar con anterior
        if i > 0 and memoria[i - 1]["tipo"] == "hueco":
            anterior = memoria[i - 1]

            anterior["limite"] += particion["limite"]

            memoria.pop(i)

            particion = anterior
            i -= 1

        # Fusionar con siguiente
        if i < len(memoria) - 1 and memoria[i + 1]["tipo"] == "hueco":
            siguiente = memoria[i + 1]

            particion["limite"] += siguiente["limite"]

            memoria.pop(i + 1)

        registrarEvento(
            f"Proceso {proceso['id']} ha sido liberado de memoria."
        )

        return particion

    return None
```

Esto además hace más evidente qué está pasando.

---

# 9. SRTF: tu lógica está bastante cerca

Tenés:

```
if procesoEjecutando["ti"] > colaListo[0]["ti"]:
```

Acá está el problema.

`ti` es el **tiempo de irrupción / ráfaga original**.

SRTF debería comparar el **tiempo restante**, no el tiempo total original.

Por ejemplo:

```
P1: TI = 10

Después de ejecutar:

TX = 7
```

El tiempo restante es:

```
10 - 7 = 3
```

Si llega:

```
P2: TI = 5
```

SRTF debe comparar:

```
P1 restante = 3
P2 = 5
```

Entonces **P1 continúa**.

Tu código compara:

```
P1 TI = 10
P2 TI = 5
```

y podría interrumpir incorrectamente a P1.

### Solución

Definí:

```
def tiempoRestante(proceso):
    return proceso["ti"] - proceso["tx"]
```

Y cuando compares:

```
if tiempoRestante(procesoEjecutando) > tiempoRestante(colaListo[0]):
```

Pero hay otro detalle.

Cuando ordenás:

```
ordenarProcesoEnCola(colaListo, proceso)
```

también estás ordenando por:

```
p["ti"]
```

Eso tampoco es exactamente SRTF.

Deberías ordenar por tiempo restante:

```
def ordenarProcesoEnCola(cola, proceso):
    restante = proceso["ti"] - proceso["tx"]

    for i, p in enumerate(cola):
        restanteP = p["ti"] - p["tx"]

        if restanteP > restante:
            cola.insert(i, proceso)
            return

    cola.append(proceso)
```

---

# 10. Esto es particularmente importante para el informe

Tu cálculo:

```
tiempoRetorno = proceso["to"] - proceso["ta"]
```

está bien.

Y:

```
tiempoEspera = tiempoRetorno - proceso["ti"]
```

también está bien si `ti` representa el tiempo total de CPU requerido.

Es decir:

```
TR = TO - TA

TE = TR - TI
```

Correcto.

---

# 11. El rendimiento

Tenés:

```
cantidadProcesosSimulados / tiempo
```

La consigna pide:

> cantidad de trabajos terminados por unidad de tiempo

Eso es básicamente:

```
Rendimiento = trabajos terminados / tiempo total
```

Está bien conceptualmente.

Pero tené cuidado con qué valor tiene `tiempo` cuando termina el `while`.

Por ejemplo, si el último proceso termina en:

```
t = 20
```

y después hacés:

```
tiempo += 1
```

podés terminar calculando:

```
21
```

en lugar de:

```
20
```

Conviene definir claramente qué consideran como tiempo total en la cátedra.

---

# 12. La salida debería producirse cuando llega un proceso

La consigna dice:

> Las presentaciones de salida deberán realizarse cada vez que llega un nuevo proceso, se termina un proceso en ejecución.

Tu código actualmente hace:

```
if ocurrioEvento and pausar:
    imprimirEventos()
```

Eso significa que también pausás por otros eventos:

```
Proceso admitido
Proceso cargado en memoria
Proceso suspendido
Proceso reanudado
Proceso interrumpido
...
```

Eso no necesariamente está mal —incluso puede ser útil para mostrar el funcionamiento— pero **si quieren ajustarse estrictamente a la consigna**, convendría distinguir los eventos que obligatoriamente generan una presentación.

Por ejemplo:

```
mostrarEstado = False
```

cuando:

```
cargarProcesosNuevos()
```

y cuando termina:

```
proceso["to"] = tiempo
```

Entonces mostrar el estado en esos momentos.

---

# 13. El límite de 10 procesos

La consigna dice:

> máximo 10 procesos.

Actualmente tu programa no limita eso.

Podrías agregarlo en `cargarArchivo()`:

```
def cargarArchivo(ruta):
    archivo = None

    try:
        archivo = open(ruta, "r")
        archivo.readline()

        for line in archivo:
            if len(colaArribo) >= 10:
                print("Error: no se permiten más de 10 procesos.")
                break

            informacion = line.strip().split(",")

            colaArribo.append({
                "id": int(informacion[0]),
                "ta": int(informacion[1]),
                "ti": int(informacion[2]),
                "tam": int(informacion[3])
            })

    ...
```

Incluso mejor sería **rechazar el archivo** si tiene más de 10, en lugar de cargar solamente los primeros 10.

---

# 14. Un detalle conceptual: `ti` y `tx`

Tenés:

```
"ti": tiempo de irrupción
"tx": tiempo ejecutado
```

Está perfecto usar `tx`, pero para SRTF te recomiendo agregar:

```
"restante": ti
```

o calcularlo siempre:

```
restante = ti - tx
```

No necesitás almacenar ambas cosas.

Por ejemplo:

```
def tiempoRestante(proceso):
    return proceso["ti"] - proceso["tx"]
```

---

# 15. Cómo debería funcionar el simulador

El ciclo conceptual que te recomiendo para defender el TPI es:

```
                    ┌──────────────────┐
                    │   INICIO         │
                    └────────┬─────────┘
                             │
                             ▼
                  ┌─────────────────────┐
                  │ Leer archivo        │
                  │ máximo 10 procesos  │
                  └─────────┬───────────┘
                            │
                            ▼
                  ┌─────────────────────┐
                  │      Tiempo t       │
                  └─────────┬───────────┘
                            │
                            ▼
                ┌────────────────────────┐
                │ ¿Llegaron procesos?    │
                └───────────┬────────────┘
                            │
                            ▼
                  ┌─────────────────────┐
                  │ Cola de NUEVOS      │
                  └─────────┬───────────┘
                            │
                            ▼
                ┌────────────────────────┐
                │ ¿Hay lugar para        │
                │ admitir procesos?      │
                └───────────┬────────────┘
                            │
                            ▼
                  ┌─────────────────────┐
                  │ Best-Fit             │
                  │                     │
                  │ ¿Hay hueco?         │
                  └──────┬──────────────┘
                         │
                ┌────────┴─────────┐
                │                  │
               Sí                  No
                │                  │
                ▼                  ▼
          Memoria principal   Memoria auxiliar
                │                  │
                ▼                  ▼
             LISTO         LISTO/SUSPENDIDO
                │
                └─────────┬────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │ Aplicar SRTF    │
                 └────────┬────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │ Ejecutar 1      │
                 │ unidad de tiempo│
                 └────────┬────────┘
                          │
                          ▼
                  ┌───────────────┐
                  │ ¿Terminó?     │
                  └───────┬───────┘
                          │
                     ┌────┴────┐
                    Sí         No
                     │          │
                     ▼          │
              Liberar memoria   │
                     │          │
                     ▼          │
             ¿Hay suspendidos?  │
                     │          │
                     ▼          │
               Best-Fit         │
                     │          │
                     └────┬─────┘
                          │
                          ▼
                    Mostrar estado
                          │
                          ▼
                       t = t+1
                          │
                          ▼
                  ¿Quedan procesos?
                     │          │
                    Sí          No
                     │          │
                     └──────┐   │
                            │   ▼
                            │ INFORME
                            │
                            └────────
```

Ese flujo está mucho más alineado con la consigna.

---

# 16. Qué corregiría antes de presentar el Sprint

Yo priorizaría estas cosas:

| Prioridad | Problema                                      | Estado                |
| --------- | --------------------------------------------- | --------------------- |
| 🔴        | Implementar Best-Fit                          | Falta                 |
| 🔴        | Corregir SRTF para usar tiempo restante       | Falta                 |
| 🔴        | Corregir contador máximo de 5                 | Hay bug               |
| 🔴        | Verificar reasignación desde suspendidos      | Revisar               |
| 🟠        | Cambiar `limite` por `tamaño` conceptualmente | Recomendado           |
| 🟠        | Adaptar tabla al formato pedido               | Falta                 |
| 🟠        | Límite máximo de 10 procesos                  | Falta                 |
| 🟡        | Diferenciar fragmentación externa/interna     | Revisar               |
| 🟡        | Ajustar momentos de presentación              | Revisar               |
| 🟢        | Informe estadístico                           | Ya está bastante bien |
| 🟢        | Memoria SO 100K + usuarios 450K               | Correcto              |
| 🟢        | Estados de procesos                           | Correcto              |

## En resumen

**No tiraría tu código y empezaría de cero.** La estructura que armaste sirve. Lo que haría es corregir principalmente:

1. `cargarEnMemoria()` → **Best-Fit**.

2. `ordenarProcesoEnCola()` → ordenar por **tiempo restante**.

3. `ejecutarProceso()` → SRTF usando `ti - tx`.

4. `cantidadProcesos()` → corregir el límite de 5.

5. `liberarMemoria()` → hacer la fusión más segura.

6. Tabla de memoria → adaptar exactamente a lo solicitado.

7. Agregar límite de **10 procesos**.

8. Revisar el momento exacto en que se muestran los estados.

Con esas modificaciones, tu simulador quedaría mucho más cerca de cumplir **literalmente** la consigna del TPI, en lugar de solamente parecerse al problema planteado.
