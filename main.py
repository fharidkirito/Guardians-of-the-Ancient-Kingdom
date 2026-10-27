"""Guardians of the Ancient Kingdom - ejecución y casos de prueba obligatorios."""

from personajes import Arquero, Combate, Guerrero, Mago, Personaje

resultados = []


def titulo(texto):
    print(f"\n--- {texto} ---")


def comprobar(descripcion, condicion):
    resultados.append(condicion)
    print(f"  [{'OK' if condicion else 'FALLO'}] {descripcion}")


def lanza(excepcion, funcion):
    """True si funcion() lanza la excepción indicada."""
    try:
        funcion()
    except excepcion as error:
        print(f"      -> {type(error).__name__}: {error}")
        return True
    return False


def main():
    titulo("1. Creación correcta de los tres tipos")
    arthas = Guerrero("Arthas", 100, 30, 20)
    gandalf = Mago("Gandalf", 80, 40, 10)
    legolas = Arquero("Legolas", 90, 35, 15)
    for p in (arthas, gandalf, legolas):
        print(" ", p.mostrar_estado())
    comprobar("Los tres son Personaje", all(isinstance(p, Personaje) for p in (arthas, gandalf, legolas)))

    titulo("2. Vida inválida")
    comprobar("Vida 101 rechazada", lanza(ValueError, lambda: Guerrero("X", 101, 10, 5)))
    comprobar("Vida -1 rechazada", lanza(ValueError, lambda: Mago("X", -1, 10, 5)))

    titulo("3. Nombres vacíos")
    comprobar("Nombre '' rechazado", lanza(ValueError, lambda: Arquero("", 50, 10, 5)))
    comprobar("Nombre '   ' rechazado", lanza(ValueError, lambda: Arquero("   ", 50, 10, 5)))

    titulo("4. Ataque y defensa inválidos")
    comprobar("Ataque 0 rechazado", lanza(ValueError, lambda: Guerrero("X", 50, 0, 5)))
    comprobar("Ataque negativo rechazado", lanza(ValueError, lambda: Guerrero("X", 50, -5, 5)))
    comprobar("Defensa negativa rechazada", lanza(ValueError, lambda: Guerrero("X", 50, 10, -1)))
    comprobar("Ataque de tipo texto rechazado", lanza(TypeError, lambda: Guerrero("X", 50, "10", 5)))

    titulo("5. Habilidad del Guerrero (30 de ataque vs 10 de defensa -> 26)")
    guerrero = Guerrero("Guerrero", 100, 30, 5)
    objetivo = Mago("Objetivo", 100, 10, 10)
    danio = guerrero.atacar(objetivo)
    comprobar(f"Daño = {danio}, vida objetivo = {objetivo.vida}", danio == 26 and objetivo.vida == 74)

    titulo("6. Ataque del Mago ignora defensa (40 vs 20 -> 40)")
    mago = Mago("Mago", 100, 40, 5)
    objetivo = Guerrero("Objetivo", 100, 10, 20)
    danio = mago.atacar(objetivo)
    comprobar(f"Daño = {danio}, vida objetivo = {objetivo.vida}", danio == 40 and objetivo.vida == 60)

    titulo("7. Disparo crítico del Arquero (35 vs 15 -> 40; 10 vs 15 -> 0)")
    arquero = Arquero("Arquero", 100, 35, 5)
    objetivo = Guerrero("Objetivo", 100, 10, 15)
    danio = arquero.atacar(objetivo)
    comprobar(f"Daño con ataque > defensa = {danio}", danio == 40 and objetivo.vida == 60)
    debil = Arquero("Debil", 100, 10, 5)
    danio = debil.atacar(objetivo)
    comprobar(f"Daño con ataque <= defensa = {danio}", danio == 0 and objetivo.vida == 60)

    titulo("8. La vida nunca es negativa")
    victima = Guerrero("Victima", 20, 10, 5)
    recibido = victima.recibir_danio(50)
    comprobar(f"Recibió 50 con 20 de vida: efectivo = {recibido}, vida = {victima.vida}",
              recibido == 20 and victima.vida == 0 and not victima.esta_vivo())
    comprobar("Daño negativo rechazado", lanza(ValueError, lambda: victima.recibir_danio(-5)))

    titulo("9. Un personaje derrotado no puede atacar")
    comprobar("Derrotado no ataca", lanza(ValueError, lambda: victima.atacar(gandalf)))
    comprobar("No se puede atacar a un derrotado", lanza(ValueError, lambda: gandalf.atacar(victima)))
    comprobar("Objetivo inválido rechazado", lanza(TypeError, lambda: gandalf.atacar("dragón")))

    titulo("10 y 11. Combate completo y ganador (ejemplo del enunciado)")
    arthas = Guerrero("Arthas", 100, 30, 20)
    gandalf = Mago("Gandalf", 80, 40, 10)
    combate = Combate(arthas, gandalf)
    ganador = combate.iniciar()
    comprobar("El ganador es Gandalf", ganador is gandalf and combate.resultado == "Ganador: Gandalf")
    comprobar("Arthas quedó con 0 de vida y Gandalf con 2", arthas.vida == 0 and gandalf.vida == 2)

    titulo("12. Empate técnico (nadie causa daño)")
    a1 = Arquero("Arquero A", 100, 10, 20)
    a2 = Arquero("Arquero B", 100, 10, 20)
    combate = Combate(a1, a2)
    ganador = combate.iniciar()
    comprobar("Sin ganador y empate técnico",
              ganador is None and "Empate técnico" in combate.resultado)

    total, ok = len(resultados), sum(resultados)
    print(f"\n=== Resumen: {ok}/{total} comprobaciones correctas ===")


if __name__ == "__main__":
    main()
