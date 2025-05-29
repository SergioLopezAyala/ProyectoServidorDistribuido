import time
import zmq
import subprocess

IP_SERVIDOR = "10.43.103.220"  # IP del servidor principal
PUERTO = 5555
TIEMPO_CHECK = 2  # segundos
INTENTOS_FALLO = 3

def servidor_esta_activo():
    contexto = zmq.Context()
    socket = contexto.socket(zmq.DEALER)
    socket.setsockopt(zmq.IDENTITY, b"health_checker")
    socket.setsockopt(zmq.LINGER, 0)

    try:
        socket.connect(f"tcp://{IP_SERVIDOR}:{PUERTO}")
        socket.send(b"ping")

        poller = zmq.Poller()
        poller.register(socket, zmq.POLLIN)
        socks = dict(poller.poll(1500))  # Esperar 1.5 segundos

        if socket in socks:
            respuesta = socket.recv()
            return respuesta == b"pong"
        else:
            print("[HealthCheck] Timeout esperando respuesta del servidor.")
            return False
    except Exception as e:
        print(f"[HealthCheck] Error al contactar al servidor: {e}")
        return False
    finally:
        socket.close()
        contexto.term()

def activar_replicado():
    print("[HealthCheck] Iniciando servidor réplica...")
    subprocess.Popen(["python3", "ServidorReplica.py"])

def main():
    print("[HealthCheck] Iniciando monitoreo...")
    fallos = 0

    while True:
        activo = servidor_esta_activo()

        if activo:
            print("[HealthCheck] Servidor OK")
            fallos = 0
        else:
            fallos += 1
            print(f"[HealthCheck] Falla detectada ({fallos})")

        if fallos >= INTENTOS_FALLO:
            activar_replicado()
            break

        time.sleep(TIEMPO_CHECK)

if __name__ == "__main__":
    main()