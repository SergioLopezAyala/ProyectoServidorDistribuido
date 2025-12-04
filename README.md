# Servidor Distribuido con Balanceo de Carga y Failover

Este proyecto implementa un **servidor distribuido** capaz de:

- Recibir y distribuir carga de trabajo entre nodos.
- Gestionar el almacenamiento de las tareas y su estado.
- Monitorear la salud de los servidores mediante un **health check** continuo.
- Realizar **failover automático** a un servidor de respaldo en caso de caída del servidor principal.
- Retomar las tareas pendientes en el servidor de respaldo sin perder información.

> Ideal como base para sistemas tolerantes a fallos, procesamiento distribuido o servicios de alta disponibilidad.

---

## Características principales

- **Gestor de carga (Load Manager)**  
  - Distribuye las tareas entrantes entre los nodos disponibles.  
  - Puede aplicar distintas estrategias de balanceo (round-robin, least-load, etc. según se configure).

- **Gestor de almacenamiento (Storage Manager)**  
  - Persiste las tareas y su estado (pendiente, en proceso, completada, fallida).  
  - Permite que el servidor de respaldo retome tareas en caso de caída.

- **Health Check / Monitor de salud**  
  - Endpoint dedicado para verificar que el servicio está activo.  
  - Comprobaciones periódicas entre servidores (principal ↔ respaldo).  
  - Registro de métricas básicas de disponibilidad.

- **Failover y recuperación**  
  - Detección de caída del servidor principal.  
  - Promoción automática del servidor de respaldo a servidor activo.  
  - Reasignación de tareas en curso o pendientes usando el gestor de almacenamiento.

---

## Arquitectura (visión general)

El sistema está compuesto por:

- **Servidor Principal**  
  - Atiende las peticiones entrantes de los clientes.  
  - Coordina el gestor de carga y el gestor de almacenamiento.

- **Servidor de Respaldo**  
  - Permanece sincronizado con el estado de las tareas.  
  - Monitorea la salud del servidor principal.  
  - Toma el control cuando se detecta una caída.

- **Módulos internos**  
  - `load_manager/` – Lógica de distribución de carga.  
  - `storage_manager/` – Persistencia y recuperación de tareas.  
  - `health/` – Endpoints y lógica de health checks.  
  - `failover/` – Detección de fallos y cambio de rol principal ↔ respaldo.

> Ajusta los nombres de directorios según tu implementación real.

---

## Requisitos

- Lenguaje / runtime:  
  - `Python 3.11`
- Gestor de paquetes:  
  - pip.
- Base de datos o almacenamiento:  
  - MongoDB / sistema de archivos.
- Opcional: Docker / Docker Compose para despliegue.
  
---
