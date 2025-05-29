import zmq
import threading
import json
import os
import time
import psutil

PUERTO = 5555

salones_disponibles = ["A-110114-{:03d}".format(i) for i in range(1, 381)]
laboratorios_disponibles = ["L-01220-{:03d}".format(i) for i in range(1, 61)]
lock = threading.Lock()

LOG_ASIGNACIONES = "log_asignaciones.json"
LOG_METRICAS = "log_metricas_servidor.txt"

if not os.path.exists(LOG_ASIGNACIONES):
    with open(LOG_ASIGNACIONES, "w", encoding="utf-8") as f:
        json.dump([], f, indent=4)

def guardar_log(entrada):
    try:
        if os.path.exists(LOG_ASIGNACIONES):
            with open(LOG_ASIGNACIONES, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    print("[Servidor] Log corrupto. Reiniciando...")
                    data = []
        else:
            data = []

        data.append(entrada)

        with open(LOG_ASIGNACIONES, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    except Exception as e:
        print(f"[Servidor] Error al guardar log: {e}")

def guardar_metricas(facultad, duracion, uso_cpu, uso_memoria):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    with open(LOG_METRICAS, "a") as f:
        f.write(f"[{timestamp}] Facultad: {facultad} | Latencia: {duracion:.4f}s | CPU: {uso_cpu}% | RAM: {uso_memoria}%\n")

def procesar_programa(programa):
    nombre = programa["programa"]
    n_salas = programa["n_salas"]
    n_labs = programa["n_labs"]

    asignacion = {
        "salones": [],
        "laboratorios": [],
        "aulas_moviles": [],
        "estado": "OK"
    }

    with lock:
        if len(salones_disponibles) >= n_salas:
            for _ in range(n_salas):
                asignacion["salones"].append(salones_disponibles.pop(0))
        else:
            asignacion["estado"] = "ERROR: No hay suficientes salones"

        if len(laboratorios_disponibles) >= n_labs:
            for _ in range(n_labs):
                asignacion["laboratorios"].append(laboratorios_disponibles.pop(0))
        elif len(salones_disponibles) >= n_labs:
            for _ in range(n_labs):
                asignacion["aulas_moviles"].append(salones_disponibles.pop(0))
        else:
            if "ERROR" in asignacion["estado"]:
                asignacion["estado"] += " ni laboratorios disponibles"
            else:
                asignacion["estado"] = "ERROR: No hay laboratorios ni aulas móviles"

    return nombre, asignacion

def atender_solicitud(socket, identidad, mensaje_json):
    try:
        inicio = time.time()

        solicitud = json.loads(mensaje_json.decode("utf-8"))
        facultad = solicitud.get("facultad")
        semestre = solicitud.get("semestre")
        programas = solicitud.get("programas")

        if facultad is None or semestre is None or programas is None:
            raise ValueError("Solicitud incompleta")

        print(f"[Servidor] Recibida solicitud de {facultad}, {len(programas)} programas")

        resultado = {}
        for programa in programas:
            try:
                nombre_prog, asignacion = procesar_programa(programa)
                resultado[nombre_prog] = asignacion
                print(f"[Servidor] Asignado a {nombre_prog}: {asignacion['estado']}")
            except Exception as pe:
                nombre_fallo = programa.get("programa", "desconocido")
                resultado[nombre_fallo] = {
                    "salones": [],
                    "laboratorios": [],
                    "aulas_moviles": [],
                    "estado": f"ERROR al procesar: {str(pe)}"
                }

        entrada_log = {
            "facultad": facultad,
            "semestre": semestre,
            "asignaciones": resultado
        }
        guardar_log(entrada_log)

        fin = time.time()
        uso_cpu = psutil.cpu_percent(interval=0.1)
        uso_mem = psutil.virtual_memory().percent
        guardar_metricas(facultad, fin - inicio, uso_cpu, uso_mem)

        respuesta = json.dumps(resultado).encode("utf-8")
        print(f"[Servidor] Enviando respuesta a {facultad} con identidad {identidad}")
        socket.send_multipart([identidad, respuesta])

    except Exception as e:
        print(f"[Servidor] ERROR GENERAL: {e}")
        error_msg = {"estado": f"ERROR en servidor: {str(e)}"}
        try:
            socket.send_multipart([identidad, json.dumps(error_msg).encode("utf-8")])
        except Exception as err_envio:
            print(f"[Servidor] No se pudo enviar error: {err_envio}")

def main():
    contexto = zmq.Context()
    socket = contexto.socket(zmq.ROUTER)
    socket.bind(f"tcp://*:{PUERTO}")
    print(f"[Servidor] Escuchando en puerto {PUERTO}...")

    while True:
        partes = socket.recv_multipart()
        if len(partes) == 3:
            identidad, _, mensaje = partes
        elif len(partes) == 2:
            identidad, mensaje = partes
        else:
            print(f"[Servidor] Error: mensaje con {len(partes)} partes")
            continue

        if mensaje == b"ping":
            print(f"[Servidor] Recibido ping de {identidad}, respondiendo pong")
            socket.send_multipart([identidad, b"pong"])
            continue

        threading.Thread(
            target=atender_solicitud,
            args=(socket, identidad, mensaje)
        ).start()

if __name__ == "__main__":
    main()
