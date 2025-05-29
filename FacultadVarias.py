import zmq
import json
import sys
import time
import psutil

# Constantes
MAX_PROGRAMAS = 5
IP_SERVIDOR_PRINCIPAL = "10.43.103.220"
PUERTO_SERVIDOR_PRINCIPAL = 5555
IP_SERVIDOR_REPLICA = "10.43.96.9"
PUERTO_SERVIDOR_REPLICA = 5556

def log(nombre_facultad, mensaje):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    with open(f"log_{nombre_facultad}.txt", "a") as f:
        f.write(f"[{timestamp}] {mensaje}\n")

def enviar_a_servidor(solicitud_agrupada, nombre_facultad):
    def intentar_envio(ip_servidor, puerto, etiqueta):
        contexto = zmq.Context()
        socket = contexto.socket(zmq.DEALER)
        socket.setsockopt(zmq.IDENTITY, nombre_facultad.encode("utf-8"))
        socket.connect(f"tcp://{ip_servidor}:{puerto}")

        poller = zmq.Poller()
        poller.register(socket, zmq.POLLIN)

        print(f"[Facultad] Enviando solicitud al servidor {etiqueta} ({ip_servidor}:{puerto})...")
        log(nombre_facultad, f"Enviando solicitud al servidor {etiqueta}")

        inicio = time.time()
        socket.send(json.dumps(solicitud_agrupada).encode("utf-8"))

        socks = dict(poller.poll(5000))  # Esperar hasta 5s

        if socket in socks:
            respuesta = socket.recv()
            fin = time.time()
            latencia = fin - inicio
            cpu = psutil.cpu_percent(interval=0.1)
            ram = psutil.virtual_memory().percent
            log(nombre_facultad, f"Respuesta recibida en {latencia:.4f}s | CPU: {cpu}% | RAM: {ram}%")
            socket.close()
            contexto.term()
            return respuesta
        else:
            print(f"[Facultad] Timeout con el servidor {etiqueta}")
            log(nombre_facultad, f"Timeout con el servidor {etiqueta}")
            socket.close()
            contexto.term()
            return None

    # Intentar primero con el servidor principal
    respuesta = intentar_envio(IP_SERVIDOR_PRINCIPAL, PUERTO_SERVIDOR_PRINCIPAL, "principal")

    # Si falla, intentar con el servidor réplica
    if respuesta is None:
        print("[Facultad] Intentando con servidor de respaldo...")
        log(nombre_facultad, "Intentando con servidor de respaldo")
        respuesta = intentar_envio(IP_SERVIDOR_REPLICA, PUERTO_SERVIDOR_REPLICA, "réplica")

    return respuesta

def main():
    if len(sys.argv) != 3:
        print("Uso: python facultad.py <nombre_facultad> <puerto>")
        return

    nombre_facultad = sys.argv[1]
    new_port = sys.argv[2]

    print(f"[Facultad: {nombre_facultad}] Esperando solicitudes de programas...")
    log(nombre_facultad, "Inicio de ejecución de la facultad")

    contexto = zmq.Context()
    socket_prog = contexto.socket(zmq.REP)
    socket_prog.bind(f"tcp://*:{new_port}")

    solicitudes_recibidas = {}

    while len(solicitudes_recibidas) < MAX_PROGRAMAS:
        mensaje = socket_prog.recv()
        solicitud = json.loads(mensaje.decode("utf-8"))
        programa = solicitud["programa"]
        print(f"[Facultad: {nombre_facultad}] Solicitud recibida de: {programa}")
        log(nombre_facultad, f"Solicitud recibida de: {programa}")
        solicitudes_recibidas[programa] = solicitud
        socket_prog.send_string("OK")

    print(f"[Facultad: {nombre_facultad}] Enviando solicitudes agrupadas al servidor...")

    agrupada = {
        "facultad": nombre_facultad,
        "semestre": list(solicitudes_recibidas.values())[0]["semestre"],
        "programas": list(solicitudes_recibidas.values())
    }

    respuesta_servidor = enviar_a_servidor(agrupada, nombre_facultad)

    if respuesta_servidor is None:
        print("[Facultad] No se pudo obtener respuesta ni del servidor principal ni de la réplica.")
        log(nombre_facultad, "ERROR: No se obtuvo respuesta de ningún servidor")
        return

    asignaciones = json.loads(respuesta_servidor.decode("utf-8"))

    print(f"[Facultad: {nombre_facultad}] Asignaciones recibidas. Detalle:")
    for programa, asignacion in asignaciones.items():
        print(f"  Programa: {programa}")
        print(f"    Estado: {asignacion['estado']}")
        print(f"    Salones: {asignacion['salones']}")
        print(f"    Laboratorios: {asignacion['laboratorios']}")
        print(f"    Aulas móviles: {asignacion['aulas_moviles']}")
        log(nombre_facultad, f"Asignación enviada a {programa} con estado: {asignacion['estado']}")

    # Paso 3: enviar asignaciones a programas
    for _ in range(MAX_PROGRAMAS):
        mensaje = socket_prog.recv()
        programa_solicitante = mensaje.decode("utf-8")
        asignacion = asignaciones.get(programa_solicitante, {"estado": "ERROR: no se encontró asignación"})
        socket_prog.send(json.dumps(asignacion).encode("utf-8"))

    socket_prog.close()
    contexto.term()

if __name__ == "__main__":
    main()
