Para el **primer Sprint del 06/10**, yo no intentaría tener terminado todo el simulador. Lo importante es que puedan demostrar que **el proyecto está organizado, que la arquitectura está definida y que ya existe un prototipo funcional de las partes centrales**.

Como son **7 integrantes**, pueden dividirse por módulos, pero evitando que cada uno trabaje aislado: tiene que haber integración frecuente.

## Qué deberían tener para el Sprint

Yo apuntaría a llegar al 06/10 con:

- Repositorio/proyecto Python funcionando.

- Archivo de entrada definido.

- Carga de procesos desde archivo.

- Estructuras de datos de procesos y colas.

- Modelo de memoria:
  
  - 100K SO.
  
  - 450K usuarios.
  
  - particiones variables.
  
  - huecos.

- Algoritmo **Best-Fit** funcionando.

- Creación y liberación de particiones.

- Colas:
  
  - Nuevo.
  
  - Listo.
  
  - Listo/Suspendido.
  
  - Ejecución.
  
  - Terminado.

- Una primera versión de **SRTF**.

- Ciclo de simulación por unidades de tiempo.

- Salida básica del estado.

- Trello armado y actualizado.

- Un video/demo donde puedan explicar qué hicieron y qué falta.

No hace falta que para el primer Sprint tengan el informe estadístico perfecto, una interfaz bonita, ejecutable empaquetado, etc. Eso puede quedar para los siguientes incrementos.

---

# Cómo dividiría el equipo de 7

No dividiría simplemente "uno hace memoria, otro hace CPU", porque hay partes que dependen mucho entre sí.

Propondría esto:

| Integrante | Rol principal                             | Responsabilidades                                      |
| ---------- | ----------------------------------------- | ------------------------------------------------------ |
| 1          | **Coordinación / Integración**            | Arquitectura, integración de ramas, seguimiento Trello |
| 2          | **Entrada de procesos**                   | Archivo, validaciones, carga de procesos               |
| 3          | **Memoria MVT**                           | Particiones, Best-Fit, creación de huecos              |
| 4          | **Liberación de memoria**                 | Liberación, fusión de huecos, reasignación             |
| 5          | **Planificación SRTF**                    | CPU, tiempo restante, interrupciones                   |
| 6          | **Colas + ciclo de simulación**           | Estados, admisión, ciclo temporal                      |
| 7          | **Salida + estadísticas + documentación** | Tablas, eventos, informe, HowTo                        |

Pero **todos deberían probar e integrar**, no solamente entregar su código.

---

# 1. Integrante de coordinación/integración

Este integrante no debería ser "el jefe que hace todo", sino quien mantiene el proyecto ensamblado.

### Tareas

- Definir estructura del proyecto.

- Crear repositorio.

- Definir convenciones de nombres.

- Revisar cambios.

- Integrar las diferentes partes.

- Resolver conflictos de Git.

- Mantener actualizado Trello.

- Preparar la demo del Sprint junto con el resto.

### Trello

Crear tareas como:

```
Definir arquitectura del simulador
Crear estructura inicial del proyecto
Definir modelo de proceso
Definir modelo de memoria
Definir flujo de estados
Integrar módulos
```

---

# 2. Integrante de entrada de procesos

Se ocupa de que los procesos entren correctamente al simulador.

Por ejemplo, definir:

```
ID,TAM,TA,TI
1,100,0,5
2,200,2,8
3,50,3,4
```

Y convertirlos a:

```
{
    "id": 1,
    "tam": 100,
    "ta": 0,
    "ti": 5,
    "tx": 0
}
```

### Trello

```
Definir formato entrada.txt
Implementar lectura del archivo
Validar datos
Limitar a 10 procesos
Ordenar procesos por tiempo de arribo
Probar carga de procesos
```

---

# 3. Integrante de memoria: Best-Fit

Este es uno de los módulos más importantes porque la consigna explícitamente pide **MVT + Best-Fit**.

Debe trabajar con:

```
SO
├── 100K
└── 450K usuarios
```

Y generar algo como:

```
ID    BASE    TAM    IDP
0     0       100    SO
1     100     150    P1
2     250     100    -
3     350     200    P2
```

### Tareas

- Crear particiones.

- Buscar huecos.

- Implementar Best-Fit.

- Asignar proceso.

- Crear nuevo hueco cuando sobra espacio.

- Mantener correctamente las direcciones.

### Trello

```
Diseñar estructura de partición
Inicializar memoria
Implementar búsqueda Best-Fit
Implementar asignación
Implementar división de huecos
Probar diferentes tamaños
```

---

# 4. Integrante de liberación de memoria

Este módulo se conecta muchísimo con el anterior.

Cuando termina:

```
P1
```

debe quedar:

```
HUECO
```

y después verificar los vecinos.

Ejemplo:

```
P1 | HUECO | P2
```

Si P1 termina:

```
HUECO | HUECO | P2
```

hay que fusionarlos:

```
HUECO GRANDE | P2
```

### También

Debe trabajar con:

```
Listo/Suspendido
        ↓
Memoria auxiliar
        ↓
Memoria principal
```

### Trello

```
Implementar liberación
Fusionar con hueco anterior
Fusionar con hueco siguiente
Fusionar ambos lados
Implementar memoria auxiliar
Implementar reasignación
Probar compactación lógica mediante fusión
```

---

# 5. Integrante de SRTF

Este tiene una responsabilidad muy clara.

Debe garantizar:

```
SRTF = Shortest Remaining Time First
```

No:

```
Shortest Job First
```

La diferencia es fundamental.

Ejemplo:

```
P1:
TI = 10
TX = 7

Restante = 3
```

Si llega:

```
P2:
TI = 5
```

no debe interrumpir a P1 porque:

```
P1 restante = 3
P2 restante = 5
```

### Trello

```
Implementar tiempo restante
Ordenar cola de Listos
Implementar selección SRTF
Implementar interrupción
Probar llegada de proceso más corto
Probar empate de tiempos
```

---

# 6. Integrante de colas y ciclo de simulación

Esta persona conecta prácticamente todo.

Tiene que manejar:

```
ARRIBO
   ↓
NUEVO
   ↓
ADMITIDO
   ↓
LISTO
   ↓
EJECUCIÓN
   ↓
TERMINADO
```

o:

```
NUEVO
   ↓
LISTO/SUSPENDIDO
   ↓
LISTO
```

### También

La regla:

```
Ejecución + Listos + Listos/Suspendidos <= 5
```

### Trello

```
Implementar cola Nuevo
Implementar cola Listo
Implementar cola Listo/Suspendido
Implementar cola Terminado
Implementar límite de 5
Implementar admisión
Implementar ciclo temporal
Integrar CPU + memoria + colas
```

---

# 7. Integrante de salida, estadísticas y documentación

Este integrante puede encargarse de que **lo que hicieron sea demostrable**.

La salida tiene que mostrar:

```
Estado CPU

Memoria

Cola de Listos

Cola de Listos/Suspendidos
```

Y al final:

```
ID    TR    TE
1     10    4
2     15    7
...
```

Más:

```
Promedio TR
Promedio TE
Rendimiento
```

### Trello

```
Diseñar formato de salida
Mostrar estado CPU
Mostrar tabla de memoria
Mostrar cola de Listos
Mostrar cola Listos/Suspendidos
Implementar informe estadístico
Calcular rendimiento
Crear HowTo
```

---

# Cómo organizaría el Trello

No hagan un Trello con solamente:

```
Juan → memoria
Pedro → CPU
...
```

Eso no muestra metodología de trabajo.

Yo haría estas columnas:

```
📋 BACKLOG
      ↓
📌 SPRINT 1
      ↓
🔨 EN PROGRESO
      ↓
👀 EN REVISIÓN
      ↓
✅ TERMINADO
```

Y opcionalmente:

```
🐛 BUGS
```

---

# Ejemplo concreto de tarjetas

En `BACKLOG`:

```
[MEM] Diseñar estructura de partición

[MEM] Implementar Best-Fit

[MEM] Dividir huecos

[MEM] Liberar partición

[MEM] Fusionar huecos

[CPU] Implementar tiempo restante

[CPU] Implementar SRTF

[CPU] Implementar interrupción

[COLAS] Implementar cola Nuevo

[COLAS] Implementar cola Listo

[COLAS] Implementar cola Listo/Suspendido

[COLAS] Límite máximo de 5 procesos

[INPUT] Leer entrada.txt

[INPUT] Validar máximo 10 procesos

[OUTPUT] Mostrar memoria

[OUTPUT] Mostrar CPU

[OUTPUT] Mostrar colas

[STATS] Tiempo de retorno

[STATS] Tiempo de espera

[STATS] Rendimiento

[DOC] Crear HowTo
```

Después seleccionan las tarjetas que **sí se comprometen a terminar para el 06/10** y las pasan a:

```
SPRINT 1
```

---

# Algo muy importante: cada tarjeta debería tener responsable

Por ejemplo:

| Tarjeta              | Responsable  |
| -------------------- | ------------ |
| Implementar Best-Fit | Integrante 3 |
| Liberar memoria      | Integrante 4 |
| Implementar SRTF     | Integrante 5 |
| Cola Nuevo           | Integrante 6 |
| Lectura archivo      | Integrante 2 |
| Salida memoria       | Integrante 7 |
| Integración          | Integrante 1 |

Pero agregaría **al menos un revisor** a las partes importantes.

Por ejemplo:

```
Best-Fit
Responsable: Integrante 3
Revisor: Integrante 4
```

Así no depende todo de una sola persona.

---

# Qué deberían mostrar en el video del Sprint

Para el primer avance, yo prepararía una demo muy concreta.

### 1. Presentación del problema

Explican:

> Nuestro proyecto consiste en desarrollar un simulador de asignación de memoria con particiones variables y planificación SRTF para un único procesador.

### 2. Mostrar Trello

Explican:

- Los 7 integrantes.

- Cómo dividieron las tareas.

- Qué tareas están terminadas.

- Qué tareas están en progreso.

- Qué queda pendiente.

### 3. Mostrar arquitectura

Por ejemplo:

```
                 SIMULADOR
                     │
       ┌─────────────┼─────────────┐
       │             │             │
    PROCESOS       MEMORIA         CPU
       │             │             │
    Entrada       Best-Fit        SRTF
       │             │             │
       └─────────────┼─────────────┘
                     │
                   COLAS
                     │
                  SALIDA
```

### 4. Ejecutar un caso pequeño

Por ejemplo:

```
P1  TA=0  TI=8  TAM=100
P2  TA=1  TI=4  TAM=150
P3  TA=2  TI=2  TAM=80
```

Y mostrar cómo evolucionan.

### 5. Explicar lo que falta

Esto es importante. **No intenten aparentar que está terminado si todavía no lo está.**

Pueden decir:

> Para el siguiente Sprint tenemos planificada la integración completa entre la asignación de memoria, la suspensión/reanudación y la planificación SRTF, además de completar las estadísticas y las pruebas.

Eso demuestra que están trabajando incrementalmente.

---

# Yo dividiría el Sprint 1 así

Teniendo solamente hasta el **06/10**, haría algo bastante acotado:

### Sprint 1 — Objetivo

> **Tener un prototipo capaz de cargar procesos, asignarlos a memoria mediante MVT/Best-Fit y comenzar la planificación SRTF, mostrando el estado de las colas y memoria.**

Los 7 podrían tener estos objetivos:

```
👤 1 — Integración
    Arquitectura + Git + integración

👤 2 — Entrada
    entrada.txt + carga + validaciones

👤 3 — Memoria
    MVT + Best-Fit

👤 4 — Liberación
    liberar + fusionar + auxiliar

👤 5 — CPU
    SRTF + tiempo restante

👤 6 — Colas
    estados + admisión + ciclo temporal

👤 7 — Salida
    tablas + eventos + documentación
```

Y al final del Sprint deberían poder ejecutar algo así:

```
=====================================
Tiempo: 3

CPU:
Proceso 2

Memoria principal:
ID    BASE    TAM    IDP
0     0       100    SO
1     100     150    P1
2     250     80     P2
3     330     220    -

Cola de Listos:
P3

Cola de Listos/Suspendidos:
P4
```

Eso ya sería una **demo bastante defendible para el primer avance**.

Y una recomendación importante: **no separen el proyecto en 7 archivos independientes que después intenten unir el día anterior**. Definan ahora mismo las estructuras compartidas (`proceso`, `particion`, colas y ciclo de tiempo) y trabajen sobre esa interfaz. Ahí es donde más probablemente van a tener problemas de integración.
