import zmq
import threading
import json
import os

# Recursos globales compartidos
salones_disponibles = ["A-110114-{:03d}".format(i) for i in range(1, 381)]
laboratorios_disponibles = ["L-01220-{:03d}".format(i) for i in range(1, 61)]
lock = threading.Lock()

LOG_PATH = "log_asignaciones.json"
PUERTO = 5556

# Inicializar log si no existe
if not os.path.exists(LOG_PATH):
    with open(LOG_PATH, "w") as f:
        json.dump([], f)

def guardar_log(entrada):
    with lock:
        with open(LOG_PATH, "r+", encoding="utf-8") as f:
            data = json.load(f)
            data.append(entrada)
            f.seek(0)
            json.dump(data, f, indent=4)

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
    with lock:
        solicitud = json.loads(mensaje_json.decode("utf-8"))
        facultad = solicitud["facultad"]
        semestre = solicitud["semestre"]
        programas = solicitud["programas"]

        print(f"[Servidor] Recibida solicitud de {facultad}, {len(programas)} programas")

        resultado = {}
        for programa in programas:
            nombre_prog, asignacion = procesar_programa(programa)
            resultado[nombre_prog] = asignacion

        # Guardar en log
        entrada_log = {
            "facultad": facultad,
            "semestre": semestre,
            "asignaciones": resultado
        }
        guardar_log(entrada_log)

        respuesta = json.dumps(resultado).encode("utf-8")
        socket.send_multipart([identidad, b"", respuesta])

def main():
    contexto = zmq.Context()
    socket = contexto.socket(zmq.ROUTER)
    socket.bind(f"tcp://10.43.103.169:{PUERTO}")
    print(f"[Servidor] Escuchando en puerto {PUERTO}...")

    while True:
        identidad, separador, mensaje = socket.recv_multipart()
        threading.Thread(
            target=atender_solicitud,
            args=(socket, identidad, mensaje),
            daemon=True
        ).start()

if __name__ == "__main__":
    main()
