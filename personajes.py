"""Guardians of the Ancient Kingdom - definición de las clases del sistema.

Este módulo solo define clases. No ejecuta pruebas ni imprime nada al
importarse; para usarlo, véase main.py.
"""

from abc import ABC, abstractmethod


def _es_entero(valor):
    """True si valor es un int real (los bool no cuentan como enteros aquí)."""
    return isinstance(valor, int) and not isinstance(valor, bool)


class Personaje(ABC):
    """Clase abstracta con lo que tienen en común todos los guardianes."""

    VIDA_MAXIMA = 100

    def __init__(self, nombre, vida, ataque, defensa):
        # Se asigna mediante los setters para reutilizar las validaciones.
        self.nombre = nombre
        self.vida = vida
        self.ataque = ataque
        self.defensa = defensa

    # ---------------- Encapsulamiento: getters y setters ----------------
    @property
    def nombre(self):
        return self._nombre

    @nombre.setter
    def nombre(self, valor):
        if not isinstance(valor, str):
            raise TypeError("El nombre debe ser texto.")
        if not valor.strip():
            raise ValueError("El nombre no puede estar vacío.")
        self._nombre = valor.strip()

    @property
    def vida(self):
        return self._vida

    @vida.setter
    def vida(self, valor):
        if not _es_entero(valor):
            raise TypeError("La vida debe ser un número entero.")
        if not 0 <= valor <= self.VIDA_MAXIMA:
            raise ValueError(f"La vida debe estar entre 0 y {self.VIDA_MAXIMA}.")
        self._vida = valor

    @property
    def ataque(self):
        return self._ataque

    @ataque.setter
    def ataque(self, valor):
        if not _es_entero(valor):
            raise TypeError("El ataque debe ser un número entero.")
        if valor <= 0:
            raise ValueError("El ataque debe ser un entero positivo.")
        self._ataque = valor

    @property
    def defensa(self):
        return self._defensa

    @defensa.setter
    def defensa(self, valor):
        if not _es_entero(valor):
            raise TypeError("La defensa debe ser un número entero.")
        if valor < 0:
            raise ValueError("La defensa no puede ser negativa.")
        self._defensa = valor

    # ---------------- Comportamiento común ----------------
    def recibir_danio(self, cantidad):
        """Resta vida y devuelve el daño efectivamente recibido.

        El daño llega ya calculado: aquí no se vuelve a descontar la defensa.
        """
        if not _es_entero(cantidad):
            raise TypeError("El daño debe ser un número entero.")
        if cantidad < 0:
            raise ValueError("El daño no puede ser negativo.")
        efectivo = min(cantidad, self._vida)  # la vida nunca baja de 0
        self._vida -= efectivo
        return efectivo

    def esta_vivo(self):
        return self._vida > 0

    def mostrar_estado(self):
        """Devuelve un texto con el estado actual del personaje."""
        situacion = "vivo" if self.esta_vivo() else "derrotado"
        return (f"{self._nombre} ({type(self).__name__}) | Vida: {self._vida} | "
                f"Ataque: {self._ataque} | Defensa: {self._defensa} | {situacion}")

    def __str__(self):
        return self.mostrar_estado()

    def _validar_ataque(self, objetivo):
        """Validaciones comunes que usan los atacar() de todas las subclases."""
        if not isinstance(objetivo, Personaje):
            raise TypeError("El objetivo debe ser un Personaje.")
        if objetivo is self:
            raise ValueError("Un personaje no puede atacarse a sí mismo.")
        if not self.esta_vivo():
            raise ValueError(f"{self._nombre} está derrotado y no puede atacar.")
        if not objetivo.esta_vivo():
            raise ValueError(f"{objetivo.nombre} ya está derrotado.")

    @abstractmethod
    def atacar(self, objetivo):
        """Ataca al objetivo y devuelve el daño efectivo que recibió."""


class Guerrero(Personaje):
    """Golpe poderoso: ataque +20 % antes de descontar la defensa enemiga."""

    def _calcular_danio(self, objetivo):
        potenciado = self.ataque * 120 // 100  # enteros: redondea hacia abajo
        return max(0, potenciado - objetivo.defensa)

    def atacar(self, objetivo):
        self._validar_ataque(objetivo)
        return objetivo.recibir_danio(self._calcular_danio(objetivo))


class Mago(Personaje):
    """Hechizo penetrante: ignora por completo la defensa del objetivo."""

    def _calcular_danio(self, objetivo):
        return self.ataque

    def atacar(self, objetivo):
        self._validar_ataque(objetivo)
        return objetivo.recibir_danio(self._calcular_danio(objetivo))


class Arquero(Personaje):
    """Disparo crítico: si el ataque supera la defensa, el daño se duplica."""

    def _calcular_danio(self, objetivo):
        if self.ataque > objetivo.defensa:
            return (self.ataque - objetivo.defensa) * 2
        return 0

    def atacar(self, objetivo):
        self._validar_ataque(objetivo)
        return objetivo.recibir_danio(self._calcular_danio(objetivo))


class Combate:
    """Administra un enfrentamiento por turnos entre dos personajes.

    Agregación: los personajes se crean fuera y solo se reciben aquí.
    Polimorfismo: solo se llama a atacar(); nunca se pregunta el tipo.
    """

    MAX_RONDAS = 50

    def __init__(self, personaje1, personaje2, mostrar=True):
        for p in (personaje1, personaje2):
            if not isinstance(p, Personaje):
                raise TypeError("Los participantes deben ser Personajes.")
            if not p.esta_vivo():
                raise ValueError(f"{p.nombre} está derrotado y no puede combatir.")
        if personaje1 is personaje2:
            raise ValueError("Se necesitan dos personajes distintos.")
        self._participantes = (personaje1, personaje2)
        self._turno = 0  # índice del personaje que ataca
        self._rondas = 0
        self._ataques = 0
        self._ganador = None
        self._resultado = None  # texto final; None mientras no termine
        self._mostrar = mostrar

    # ---------------- Consultas ----------------
    @property
    def ganador(self):
        return self._ganador

    @property
    def resultado(self):
        return self._resultado

    @property
    def rondas(self):
        return self._rondas

    def _imprimir(self, texto=""):
        if self._mostrar:
            print(texto)

    # ---------------- Lógica del combate ----------------
    def cambiar_turno(self):
        self._turno = 1 - self._turno

    def verificar_ganador(self):
        """Devuelve el vencedor si el otro participante fue derrotado."""
        p1, p2 = self._participantes
        if p1.esta_vivo() and not p2.esta_vivo():
            return p1
        if p2.esta_vivo() and not p1.esta_vivo():
            return p2
        return None

    def iniciar(self):
        if self._resultado is not None:
            raise RuntimeError("Este combate ya terminó.")
        p1, p2 = self._participantes
        self._imprimir(f"=== Combate: {p1.nombre} vs {p2.nombre} ===")
        self._imprimir(p1.mostrar_estado())
        self._imprimir(p2.mostrar_estado())

        while self._resultado is None:
            danio_ronda = 0
            for _ in range(2):  # una ronda = un ataque de cada personaje
                atacante = self._participantes[self._turno]
                defensor = self._participantes[1 - self._turno]
                danio = atacante.atacar(defensor)
                danio_ronda += danio
                self._ataques += 1
                self._imprimir(f"\nTurno {self._ataques}: {atacante.nombre} ataca "
                               f"a {defensor.nombre} y causa {danio} de daño.")
                self._imprimir(p1.mostrar_estado())
                self._imprimir(p2.mostrar_estado())

                ganador = self.verificar_ganador()
                if ganador is not None:
                    self._ganador = ganador
                    self._resultado = f"Ganador: {ganador.nombre}"
                    break
                self.cambiar_turno()

            if self._resultado is not None:
                break
            self._rondas += 1
            if danio_ronda == 0:
                self._resultado = "Empate técnico: la ronda terminó sin daño."
            elif self._rondas >= self.MAX_RONDAS:
                self._resultado = f"Empate: se completaron {self.MAX_RONDAS} rondas sin ganador."

        self.mostrar_resultado()
        return self._ganador

    def mostrar_resultado(self):
        if self._resultado is None:
            self._imprimir("El combate aún no ha terminado.")
        else:
            self._imprimir(f"\n=== Resultado final ===\n{self._resultado}")
