<p align="center">
  <a href="https://github.com/JonathanArroyaveGonzalez/Integration-Proyect-SGV/actions/workflows/django.yml">
    <img src="https://github.com/JonathanArroyaveGonzalez/Integration-Proyect-SGV/actions/workflows/django.yml/badge.svg" alt="Django CI">
  </a>
  <a href="https://www.djangoproject.com/">
    <img src="https://img.shields.io/badge/Powered%20by-Django-092E20?logo=django&logoColor=white" alt="Powered by Django">
  </a>
</p>


# WMS_Copernico_Base_Integration



[![Python](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org)
[![Django](https://img.shields.io/badge/django-5.2+-green.svg)](https://www.djangoproject.com)
[![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-yellow.svg)](https://conventionalcommits.org)
[![Development Status](https://img.shields.io/badge/status-development-orange)](https://github.com/JonathanArroyaveGonzalez/Integration-Proyect-SGV)
[![Branch develop/transprensa](https://img.shields.io/badge/branch-develop%2Ftransprensa-blue)](https://github.com/JonathanArroyaveGonzalez/Integration-Proyect-SGV/tree/develop/transprensa)
[![Powered by Django](https://img.shields.io/badge/CI%20by-Django-092E20?logo=django&logoColor=white)](https://github.com/JonathanArroyaveGonzalez/Integration-Project-SGV/actions/workflows/django.yml)


Proyecto base del sistema WMS Copernico para Integración con sistemas externos.

## Convenciones de Commits y Flujo de Trabajo

### Estructura de Ramas
- `develop/transprensa`: Rama principal de desarrollo
- `feat/transprensa`: Rama de features estables

### Convenciones de Commits

Este proyecto utiliza [Conventional Commits](https://www.conventionalcommits.org/) para mantener un historial de cambios claro y estructurado.

#### Estructura del Commit
```
<tipo>[alcance opcional]: <descripción>

[cuerpo opcional]

[nota de pie opcional]
```

#### Tipos de Commits
- `feat`: Nuevas características o funcionalidades
- `fix`: Corrección de errores
- `docs`: Cambios en la documentación
- `style`: Cambios que no afectan el significado del código (espacios en blanco, formato, punto y coma faltantes, etc.)
- `refactor`: Cambios en el código que no corrigen errores ni agregan funcionalidades
- `perf`: Cambios que mejoran el rendimiento
- `test`: Agregar o corregir pruebas
- `chore`: Cambios en el proceso de construcción o herramientas auxiliares

#### Ejemplos
```
feat(customer): agregar validación de documento
fix(inventory): corregir cálculo de stock disponible
docs: actualizar instrucciones de instalación
```

### Flujo de Trabajo
1. Todo el desarrollo se realiza en la rama `develop/transprensa`
2. Los cambios se revisan y prueban en esta rama
3. Una vez que los cambios son estables, se realiza un merge a `feat/transprensa`
4. Para hacer el merge, usar el siguiente comando:
   ```bash
   git checkout feat/transprensa
   git merge develop/transprensa
   ```

### Integración Continua (CI)

El proyecto utiliza GitHub Actions para la integración continua. El pipeline de CI se ejecuta automáticamente en:
- Cada push a las ramas `develop/transprensa` y `feat/transprensa`
- Cada pull request hacia estas ramas

El pipeline incluye:
1. Construcción en Ubuntu Latest
2. Pruebas en múltiples versiones de Python (3.9, 3.10, 3.11)
3. Verificación del sistema Django (`python manage.py check`)
4. Ejecución de pruebas (`python manage.py test`)