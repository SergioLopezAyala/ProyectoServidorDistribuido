import zmq
import json
import threading
import os

# Recursos disponibles compartidos por cada worker
salones_disponibles = ["A-110114-{:03d}".format(i) for i in range(1, 381)]
laboratorios_disponibles = ["L-01220-{:03d}".format(i) for i in range(1, 61)]
lock = threading.Lock()

LOG_PATH = "log_asignaciones_broker.json"

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

def main():
    contexto = zmq.Context()
    socket = contexto.socket(zmq.REP)
    socket.connect("tcp://localhost:5556")  # Conecta al backend del broker

    print("[Worker] Esperando solicitudes del broker...")

    while True:
        mensaje = socket.recv()
        solicitud = json.loads(mensaje.decode("utf-8"))

        facultad = solicitud["facultad"]
        semestre = solicitud["semestre"]
        programas = solicitud["programas"]

        print(f"[Worker] Procesando solicitud de facultad: {facultad}")

        resultado = {}
        for programa in programas:
            nombre, asignacion = procesar_programa(programa)
            resultado[nombre] = asignacion

        entrada_log = {
            "facultad": facultad,
            "semestre": semestre,
            "asignaciones": resultado
        }
        guardar_log(entrada_log)

        socket.send(json.dumps(resultado).encode("utf-8"))

if __name__ == "__main__":
    main()
