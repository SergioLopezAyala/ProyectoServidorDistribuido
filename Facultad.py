import zmq
import json
import sys
import time

# Constantes
MAX_PROGRAMAS = 5
PUERTO_LOCAL = 6000
PUERTO_SERVIDOR = 5555
IP_SERVIDOR_PRINCIPAL = "10.43.103.220"
IP_SERVIDOR_REPLICA = "10.43.96.9"


def enviar_a_servidor(solicitud_agrupada, nombre_facultad):
    def intentar_envio(ip_servidor, etiqueta):
        contexto = zmq.Context()
        socket = contexto.socket(zmq.DEALER)
        socket.setsockopt(zmq.IDENTITY, nombre_facultad.encode("utf-8"))
        socket.connect(f"tcp://{ip_servidor}:{PUERTO_SERVIDOR}")

        poller = zmq.Poller()
        poller.register(socket, zmq.POLLIN)

        print(f"[Facultad] Enviando solicitud al servidor {etiqueta} ({ip_servidor})...")
        socket.send(json.dumps(solicitud_agrupada).encode("utf-8"))

        socks = dict(poller.poll(5000))  # Esperar hasta 5s

        if socket in socks:
            respuesta = socket.recv()
            print(f"[Facultad] Respuesta recibida desde servidor {etiqueta}")
            socket.close()
            contexto.term()
            return respuesta
        else:
            print(f"[Facultad] Timeout con el servidor {etiqueta}")
            socket.close()
            contexto.term()
            return None

    # Intentar primero con el servidor principal
    respuesta = intentar_envio(IP_SERVIDOR_PRINCIPAL, "principal")

    # Si falla, intentar con el servidor réplica
    if respuesta is None:
        print("[Facultad] Intentando con servidor de respaldo...")
        respuesta = intentar_envio(IP_SERVIDOR_REPLICA, "réplica")

    return respuesta

def main():
    if len(sys.argv) != 2:
        print("Uso: python facultad.py <nombre_facultad>")
        return

    nombre_facultad = sys.argv[1]

    print(f"[Facultad: {nombre_facultad}] Esperando solicitudes de programas...")

    contexto = zmq.Context()
    socket_prog = contexto.socket(zmq.REP)
    socket_prog.bind(f"tcp://*:{PUERTO_LOCAL}")

    solicitudes_recibidas = {}

    # Paso 1: recibir solicitudes de programas
    while len(solicitudes_recibidas) < MAX_PROGRAMAS:
        mensaje = socket_prog.recv()
        solicitud = json.loads(mensaje.decode("utf-8"))
        programa = solicitud["programa"]

        print(f"[Facultad: {nombre_facultad}] Solicitud recibida de: {programa}")

        solicitudes_recibidas[programa] = solicitud
        socket_prog.send_string("OK")  # Confirmación

    print(f"[Facultad: {nombre_facultad}] Enviando solicitudes agrupadas al servidor...")

    agrupada = {
        "facultad": nombre_facultad,
        "semestre": list(solicitudes_recibidas.values())[0]["semestre"],
        "programas": list(solicitudes_recibidas.values())
    }

    respuesta_servidor = enviar_a_servidor(agrupada, nombre_facultad)

    if respuesta_servidor is None:
        print("[Facultad] No se pudo obtener respuesta del servidor.")
        return

    asignaciones = json.loads(respuesta_servidor.decode("utf-8"))

    print(f"[Facultad: {nombre_facultad}] Asignaciones recibidas. Enviando a programas...")
    for programa, asignacion in asignaciones.items():
        print(f"  Programa: {programa}")
        print(f"    Estado: {asignacion['estado']}")
        print(f"    Salones: {asignacion['salones']}")
        print(f"    Laboratorios: {asignacion['laboratorios']}")
        print(f"    Aulas móviles: {asignacion['aulas_moviles']}")

    # Paso 3: enviar asignaciones a programas
    for _ in range(MAX_PROGRAMAS):
        mensaje = socket_prog.recv()
        programa_solicitante = mensaje.decode("utf-8")
        asignacion = asignaciones.get(programa_solicitante, {"estado": "ERROR: no se encontró asignación"})
        socket_prog.send(json.dumps(asignacion).encode("utf-8"))

    socket_prog.close()
    contexto.term()

if __name__ == "_main_":
    main()