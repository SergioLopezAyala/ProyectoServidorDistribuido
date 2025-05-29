import zmq
import json
import sys
import os
from datetime import datetime

def guardar_respuesta(programa, semestre, solicitud, respuesta):
    archivo = f"respuesta_{programa}_{semestre}.json"
    entrada = {
        "programa": programa,
        "semestre": semestre,
        "solicitud": solicitud,
        "respuesta": respuesta,
        "timestamp": datetime.now().isoformat()
    }

    if os.path.exists(archivo):
        with open(archivo, "r+", encoding="utf-8") as f:
            data = json.load(f)
            data.append(entrada)
            f.seek(0)
            json.dump(data, f, indent=4)
    else:
        with open(archivo, "w", encoding="utf-8") as f:
            json.dump([entrada], f, indent=4)


def main():
    if len(sys.argv) != 7:
        print("Uso: python program_client.py <programa> <semestre> <n_salas> <n_labs> <ip_facultad>")
        return

    programa = sys.argv[1]
    semestre = sys.argv[2]
    n_salas = int(sys.argv[3])
    n_labs = int(sys.argv[4])
    ip_facultad = sys.argv[5]
    new_port = sys.argv[6]

    solicitud = {
        "programa": programa,
        "semestre": semestre,
        "n_salas": n_salas,
        "n_labs": n_labs
    }

    contexto = zmq.Context()
    socket = contexto.socket(zmq.REQ)
    socket.connect(f"tcp://{ip_facultad}:{new_port}")  # Puerto fijo de la Facultad

    print(f"[{programa}] Enviando solicitud a la Facultad...")
    socket.send(json.dumps(solicitud).encode("utf-8"))

    respuesta_bytes = socket.recv()
    respuesta = json.loads(respuesta_bytes.decode("utf-8"))

    print(f"[{programa}] Respuesta recibida:")
    print(json.dumps(respuesta, indent=4))

    guardar_respuesta(programa, semestre, solicitud, respuesta)

if __name__ == "__main__":
    main()