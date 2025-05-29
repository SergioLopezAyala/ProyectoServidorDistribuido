import subprocess
import time

facultades = [
    ("Facultad Ingenieria", "2025-1", 8, 3),
    ("Facultad Derecho", "2025-1", 9, 2),
    ("Facultad Medicina", "2025-1", 7, 4),
    ("Facultad Educacion", "2025-1", 10, 2),
    ("Facultad Tecnologia", "2025-1", 8, 3)
]

procesos = []

for f in facultades:
    cmd = ["python3", "facultad.py", f[0], f[1], str(f[2]), str(f[3])]
    p = subprocess.Popen(cmd)
    procesos.append(p)
    time.sleep(0.2)  # leve desfase para simular tráfico realista

for p in procesos:
    p.wait()