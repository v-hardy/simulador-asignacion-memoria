import sys

pausar = True
colaArribo = []
colaNuevo = []
colaListo = []
colaListoySuspendido = []
colaTerminado = []
memoriaPrincipal = [
  {"id": 0,"idp": -1,"tipo": "so","base": 0, "limite": 100},
  {"id": 1,"idp": -1,"tipo": "hueco","base": 100, "limite": 450}
]
idPrincipal = 2
memoriaAuxiliar = []
idAuxiliar = 0
procesoEjecutando = None
tiempo = 0
ocurrioEvento = False
eventos = []

def imprimirColasyMemoria():
  print("\nEstado de CPU: ", end='')
  if procesoEjecutando:
    print("Ejecutando un proceso")
    print("ID\tTA\tTI\tTAM\tTX\tTO")
    print(f"{procesoEjecutando['id']}\t{procesoEjecutando['ta']}\t{procesoEjecutando['ti']}", end='')
    print(f"\t{procesoEjecutando['tam']}\t{procesoEjecutando.get('tx','-')}\t{procesoEjecutando.get('to','-')}")
  else:
    print("Libre.")

  memorias = [
    {"msj": "\nMemoria principal:", "memoria": memoriaPrincipal},
    {"msj": "\nMemoria auxiliar:", "memoria": memoriaAuxiliar}
  ]
  for m in memorias:
    print(m["msj"])
    print("ID\tIDP\tTIPO\tBASE\tLÍMITE")
    for particion in m["memoria"]:
      print(f"{particion['id']}\t{particion['idp']}\t{particion['tipo']}\t{particion['base']}\t{particion['limite']}")

  colas = [
    {"msj": "\nCola de arribo:", "cola": colaArribo},
    {"msj": "\nCola de nuevos:", "cola": colaNuevo},
    {"msj": "\nCola de listos:", "cola": colaListo},
    {"msj": "\nCola de listos y suspendidos:", "cola": colaListoySuspendido},
    {"msj": "\nCola de terminados:", "cola": colaTerminado}
  ]
  for c in colas:
    print(c["msj"])
    print("ID\tTA\tTI\tTAM\tTX\tTO")
    for proceso in c["cola"]:
      print(f"{proceso['id']}\t{proceso['ta']}\t{proceso['ti']}\t{proceso['tam']}\t{proceso.get('tx','-')}\t{proceso.get('to','-')}")

def registrarEvento(evento):
  global ocurrioEvento
  ocurrioEvento = True
  eventos.append(f"- {evento}")

def imprimirEventos():
  global ocurrioEvento
  print("\n=====================================")
  print(f"\nTiempo: {tiempo}")
  print("\nEventos:")
  for evento in eventos:
    print(evento)
  eventos.clear()
  input("\nPresione Enter para ver estado de memoria y colas...")
  imprimirColasyMemoria()
  input("\nPresione Enter para ir al siguiente ciclo con eventos...")
  ocurrioEvento = False

def cargarArchivo(ruta):
  archivo = None
  try:
    archivo = open(ruta, "r")
    archivo.readline() # saltar encabezado
    for line in archivo:
      informacion = line.strip().split(",")
      colaArribo.append({
        "id": int(informacion[0]), 
        "ta": int(informacion[1]), 
        "ti": int(informacion[2]), 
        "tam": int(informacion[3])
      })
  except FileNotFoundError:
      print("Error: No se encontró el archivo de entrada.")
      print("Asegúrese de que el archivo 'entrada.txt' esté en el mismo directorio que este script.")
      exit(1)
  finally:
    if archivo:
      archivo.close()
  colaArribo.sort(key=lambda x: x["ta"])

def cargarProcesosNuevos():
  while len(colaArribo) > 0 and colaArribo[0]["ta"] == tiempo:
    proceso = colaArribo.pop(0)
    proceso["tx"] = 0
    colaNuevo.append(proceso)
    registrarEvento(f"Proceso {proceso['id']} ha llegado a la cola de nuevos.")

def cargarEnMemoria(proceso):
  global memoriaPrincipal, idPrincipal, idAuxiliar
  pcb = {
    "id": None,
    "idp": proceso["id"],
    "tipo": "proceso",
    "base": None,
    "limite": proceso["tam"]
  }
  for particion in memoriaPrincipal:  # Esto toma el primer hueco suficientemente grande que encuentra. EsTo es First-Fit.
    if particion["tipo"] == "hueco":
      if particion["limite"] < proceso["tam"]:
        continue
      if particion["limite"] > proceso["tam"]:
        hueco = {
          "id": idPrincipal,
          "idp": -1,
          "tipo": "hueco",
          "base": particion["base"] + proceso["tam"],
          "limite": particion["limite"] - proceso["tam"]
        }
        idPrincipal += 1
        memoriaPrincipal.insert(memoriaPrincipal.index(particion) + 1, hueco)
      pcb["id"] = particion["id"]
      pcb["base"] = particion["base"]
      memoriaPrincipal[memoriaPrincipal.index(particion)] = pcb
      registrarEvento(f"Proceso {proceso['id']} ha sido cargado en memoria principal.")
      return colaListo
  
  registrarEvento(f"No hay suficiente memoria principal para admitir el proceso {proceso['id']}.")

  nuevaBase = memoriaAuxiliar[-1]["base"] + memoriaAuxiliar[-1]["limite"] if len(memoriaAuxiliar) > 0 else 0
  pcb["id"] = idAuxiliar
  pcb["base"] = nuevaBase if len(memoriaAuxiliar) > 0 else 0
  idAuxiliar += 1
  memoriaAuxiliar.append(pcb)
  registrarEvento(f"Proceso {proceso['id']} ha sido cargado en memoria auxiliar.")
  return colaListoySuspendido

def ordenarProcesoEnCola(cola, proceso):
  for p in cola:
    if p["ti"] > proceso["ti"]:
      cola.insert(cola.index(p), proceso)
      break
  else:
    cola.append(proceso)

def admitirProcesos():
  cantidadProcesos = lambda : len(colaListo) + len(colaListoySuspendido) + 1 if procesoEjecutando else 0
  while len(colaNuevo) > 0 and cantidadProcesos() < 5:
    proceso = colaNuevo.pop(0)
    cola = cargarEnMemoria(proceso)
    ordenarProcesoEnCola(cola, proceso)
    registrarEvento(f"Proceso {proceso['id']} ha sido admitido.")

def liberarMemoria(proceso, memoria):
  for particion in memoria:
    if particion["idp"] == proceso["id"]:
      # mirar procesos adyacentes para fusionar huecos
      if memoria.index(particion) > 0 and memoria[memoria.index(particion) - 1]["tipo"] == "hueco":
        particion["base"] = memoria[memoria.index(particion) - 1]["base"]
        particion["limite"] += memoria[memoria.index(particion) - 1]["limite"] # ACA NO ESTARIA SUMANDO VALORES DE PUNTO EN VEZ DE "MODULOS"?
        memoria.pop(memoria.index(particion) - 1)
      if memoria.index(particion) < len(memoria) - 1 and memoria[memoria.index(particion) + 1]["tipo"] == "hueco":
        particion["limite"] += memoria[memoria.index(particion) + 1]["limite"]
        memoria.pop(memoria.index(particion) + 1)
      particion["idp"] = -1
      particion["tipo"] = "hueco"
      registrarEvento(f"Proceso {proceso['id']} ha sido liberado de memoria.")
      return particion

def reasignarMemoriaPrincipal(particion):
  global idPrincipal
  # REFLEJAR ESTO EN EL DIAGRAMA DE FLUJO: ni bien liberado memoria se comprueba que algun suspendido pueda entrar
  for proceso in colaListoySuspendido:
    if particion["limite"] < proceso["tam"]:
      continue
    if particion["limite"] > proceso["tam"]:
      hueco = {
        "id": idPrincipal,
        "idp": -1,
        "tipo": "hueco",
        "base": particion["base"] + proceso["tam"],
        "limite": particion["limite"] - proceso["tam"]
      }
      idPrincipal += 1
      memoriaPrincipal.insert(memoriaPrincipal.index(particion) + 1, hueco)
    particion["idp"] = proceso["id"]
    particion["tipo"] = "proceso"
    particion["limite"] = proceso["tam"]
    liberarMemoria(proceso, memoriaAuxiliar)
    registrarEvento(f"Proceso {proceso['id']} paso de la memoria auxiliar a la memoria principal.")
    ordenarProcesoEnCola(colaListo, colaListoySuspendido.pop(colaListoySuspendido.index(proceso)))
    registrarEvento(f"Proceso {proceso['id']} paso de la cola de Listo y Suspendido a la cola de Listo.")
    break

def ejecutarProceso():
  global procesoEjecutando
  hayProcesosListos = lambda : len(colaListo) > 0
  
  if hayProcesosListos():
    if procesoEjecutando == None:
      procesoEjecutando = colaListo.pop(0)
      registrarEvento(f"Proceso {procesoEjecutando['id']} ha comenzado a ejecutarse.")
      return
    else:
      if procesoEjecutando["ti"] > colaListo[0]["ti"]:
        registrarEvento(f"Proceso {procesoEjecutando['id']} ha sido interrumpido por el proceso {colaListo[0]['id']}.")
        ordenarProcesoEnCola(colaListo, procesoEjecutando)
        procesoEjecutando = colaListo.pop(0)
        registrarEvento(f"Proceso {procesoEjecutando['id']} ha comenzado a ejecutarse.")
        return
        
  if procesoEjecutando != None:
    procesoEjecutando["tx"] += 1
    if procesoEjecutando["ti"] == procesoEjecutando["tx"]:
      procesoEjecutando["to"] = tiempo
      registrarEvento(f"Proceso {procesoEjecutando['id']} ha terminado su ejecución.")
      colaTerminado.append(procesoEjecutando)
      particion = liberarMemoria(procesoEjecutando, memoriaPrincipal)
      reasignarMemoriaPrincipal(particion)
      if hayProcesosListos():
        procesoEjecutando = colaListo.pop(0)
        registrarEvento(f"Proceso {procesoEjecutando['id']} ha comenzado a ejecutarse.")
      else:
        procesoEjecutando = None

def generarInformeEstadistico():
  sumatoriaTiempoRetorno = 0
  sumatoriaTiempoEspera = 0
  cantidadProcesosSimulados = 0
  
  print("\n=====================================")
  print("\n         INFORME ESTADISTICO")
  print("\nTiempos de Retorno y Espera por cada proceso")
  print("ID\tTR\tTE")
  
  for proceso in colaTerminado:
    tiempoRetorno = proceso["to"] - proceso["ta"]
    tiempoEspera = tiempoRetorno - proceso["ti"]
    print(f"{proceso['id']}\t{tiempoRetorno}\t{tiempoEspera}")
    sumatoriaTiempoRetorno += tiempoRetorno
    sumatoriaTiempoEspera += tiempoEspera
    cantidadProcesosSimulados += 1
  print(f"total\t{sumatoriaTiempoRetorno}\t{sumatoriaTiempoEspera}")
  print(f"\nCantidad de procesos simulados: {cantidadProcesosSimulados}")
  print(f"\nPromedio de Tiempo de Retorno: {(sumatoriaTiempoRetorno/cantidadProcesosSimulados):.2f}")
  print(f"\nPromedio de Tiempo de Espera: {(sumatoriaTiempoEspera/cantidadProcesosSimulados):.2f}")
  print(f"\nEl Rendimiento del Sistema es de {(cantidadProcesosSimulados/tiempo):.2f} cantidad de trabajo por unidad de tiempo.\n")

def bucle():
  global tiempo
  cantidadProcesos = lambda : len(colaArribo) + len(colaNuevo) + len(colaListo) + len(colaListoySuspendido)
  quedanProcesos = lambda : cantidadProcesos() > 0 or procesoEjecutando != None
  
  while quedanProcesos():
    cargarProcesosNuevos()
    admitirProcesos()
    ejecutarProceso()
    
    if ocurrioEvento and pausar:
      imprimirEventos()
    tiempo += 1

  generarInformeEstadistico()

if __name__ == "__main__":
  ruta = "entrada.txt"
  for i,arg in enumerate(sys.argv):
    if i != 0:
      if arg.startswith('-'):
        pausar = False
      else:
        ruta = arg
  print("\nSimulador de planificación de procesos")
  print("\n=====================================")
  print("\nCargando archivo de entrada...")
  cargarArchivo(ruta)
  print("Archivo cargado correctamente.")
  print("Iniciando simulación...")
  bucle()
