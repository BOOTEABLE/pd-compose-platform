# 🐳 Plataforma de Microservicios con Docker Compose

Este proyecto implementa una arquitectura basada en microservicios utilizando contenedores. Permite levantar múltiples servicios independientes de forma rápida y estandarizada en cualquier entorno de desarrollo.

## 🏗️ Arquitectura
La plataforma orquesta los siguientes servicios:
* **Books Service:** Microservicio encargado de la gestión del catálogo.
* **Users Service:** Microservicio para la administración y lógica de usuarios.

## 🚀 Cómo ejecutarlo
Para desplegar toda la infraestructura, asegúrate de tener Docker instalado y ejecuta en la raíz del proyecto:
\`\`\`bash
docker-compose up -d --build
\`\`\`
