"""API de avistamientos organizada con Clean Architecture (Martin, 2012).

Círculos, de adentro hacia afuera (las dependencias solo apuntan hacia adentro):

    domain/        Entidades y reglas de negocio de la empresa
    application/   Casos de uso y puertos (interfaces)
    adapters/      Controlador, presentador y repositorio concreto
    frameworks/    Flask y la composición de todas las piezas
"""
