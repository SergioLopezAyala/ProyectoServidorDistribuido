import subprocess
import time

# Configura aquí los 5 programas académicos
programas = [
    {"nombre": "Sistemas", "salas": 5, "labs": 2},
    {"nombre": "Civil", "salas": 6, "labs": 1},
    {"nombre": "Industrial", "salas": 4, "labs": 2},
    {"nombre": "Electronica", "salas": 5, "labs": 3},
    {"nombre": "Ambiental", "salas": 3, "labs": 2}
]

semestre = "2025-10"
ip_facultad = "10.43.96.9"  # IP de la facultad

print("[Lanzador] Iniciando programas académicos...\n")

for prog in programas:
    comando = [
        "python", "program_client.py",
        prog["nombre"],
        semestre,
        str(prog["salas"]),
        str(prog["labs"]),
        ip_facultad
    ]
    print(f"[Lanzador] Ejecutando: {' '.join(comando)}")
    subprocess.Popen(comando)
    time.sleep(1)  # pequeña pausa para no saturar

print("\n[Lanzador] Todos los programas han sido lanzados.")
