"""Pruebas automatizadas con Pytest para Guardians of the Ancient Kingdom.

Ejecutar con:  pytest -v
"""

import pytest

from personajes import Arquero, Combate, Guerrero, Mago, Personaje


# ---------------- Creación válida ----------------
@pytest.mark.parametrize("clase", [Guerrero, Mago, Arquero])
def test_creacion_valida(clase):
    p = clase("Heroe", 100, 30, 10)
    assert isinstance(p, Personaje)
    assert (p.nombre, p.vida, p.ataque, p.defensa) == ("Heroe", 100, 30, 10)
    assert p.esta_vivo()


def test_personaje_es_abstracto():
    with pytest.raises(TypeError):
        Personaje("X", 100, 10, 10)


def test_mostrar_estado_contiene_datos():
    texto = Guerrero("Arthas", 100, 30, 20).mostrar_estado()
    assert "Arthas" in texto and "100" in texto


# ---------------- Rechazo de valores incorrectos ----------------
@pytest.mark.parametrize("vida", [101, -1, 1000])
def test_vida_fuera_de_rango(vida):
    with pytest.raises(ValueError):
        Guerrero("X", vida, 10, 5)


@pytest.mark.parametrize("nombre", ["", "   "])
def test_nombre_vacio(nombre):
    with pytest.raises(ValueError):
        Mago(nombre, 50, 10, 5)


@pytest.mark.parametrize("ataque", [0, -3])
def test_ataque_invalido(ataque):
    with pytest.raises(ValueError):
        Arquero("X", 50, ataque, 5)


def test_defensa_negativa():
    with pytest.raises(ValueError):
        Arquero("X", 50, 10, -1)


@pytest.mark.parametrize("campo,valor", [("nombre", 5), ("vida", "50"), ("ataque", 2.5), ("defensa", True)])
def test_tipos_invalidos(campo, valor):
    p = Guerrero("X", 50, 10, 5)
    with pytest.raises(TypeError):
        setattr(p, campo, valor)


def test_setters_respetan_restricciones():
    p = Guerrero("X", 50, 10, 5)
    p.vida = 80
    p.ataque = 12
    p.defensa = 0
    assert (p.vida, p.ataque, p.defensa) == (80, 12, 0)
    with pytest.raises(ValueError):
        p.vida = 150


# ---------------- Daño de cada clase ----------------
def test_danio_guerrero():
    objetivo = Mago("O", 100, 10, 10)
    assert Guerrero("G", 100, 30, 5).atacar(objetivo) == 26
    assert objetivo.vida == 74


def test_guerrero_redondea_hacia_abajo():
    # 33 * 1.2 = 39.6 -> 39; 39 - 10 = 29
    objetivo = Mago("O", 100, 10, 10)
    assert Guerrero("G", 100, 33, 5).atacar(objetivo) == 29


def test_guerrero_danio_minimo_cero():
    objetivo = Guerrero("O", 100, 10, 90)
    assert Guerrero("G", 100, 10, 5).atacar(objetivo) == 0
    assert objetivo.vida == 100


def test_danio_mago_ignora_defensa():
    objetivo = Guerrero("O", 100, 10, 20)
    assert Mago("M", 100, 40, 5).atacar(objetivo) == 40


def test_danio_arquero_critico():
    objetivo = Guerrero("O", 100, 10, 15)
    assert Arquero("A", 100, 35, 5).atacar(objetivo) == 40


def test_arquero_sin_critico_si_no_supera_defensa():
    objetivo = Guerrero("O", 100, 10, 15)
    assert Arquero("A", 100, 15, 5).atacar(objetivo) == 0  # igual: no supera
    assert Arquero("A", 100, 10, 5).atacar(objetivo) == 0  # menor


# ---------------- La vida nunca es negativa ----------------
def test_vida_nunca_negativa():
    p = Guerrero("V", 20, 10, 5)
    assert p.recibir_danio(50) == 20  # devuelve el daño efectivo
    assert p.vida == 0
    assert not p.esta_vivo()


def test_recibir_danio_no_aplica_defensa():
    p = Guerrero("V", 100, 10, 50)
    p.recibir_danio(10)
    assert p.vida == 90


def test_recibir_danio_negativo_rechazado():
    with pytest.raises(ValueError):
        Guerrero("V", 100, 10, 5).recibir_danio(-1)


def test_ataque_no_deja_vida_negativa():
    objetivo = Guerrero("O", 10, 10, 5)
    assert Mago("M", 100, 40, 5).atacar(objetivo) == 10
    assert objetivo.vida == 0


# ---------------- Derrotados y objetivos inválidos ----------------
def test_derrotado_no_puede_atacar():
    caido = Guerrero("Caido", 50, 10, 5)
    caido.recibir_danio(50)
    with pytest.raises(ValueError):
        caido.atacar(Mago("M", 100, 10, 5))


def test_no_se_puede_atacar_a_un_derrotado():
    caido = Guerrero("Caido", 50, 10, 5)
    caido.recibir_danio(50)
    with pytest.raises(ValueError):
        Mago("M", 100, 10, 5).atacar(caido)


def test_objetivo_invalido_y_autoataque():
    mago = Mago("M", 100, 10, 5)
    with pytest.raises(TypeError):
        mago.atacar("no soy un personaje")
    with pytest.raises(ValueError):
        mago.atacar(mago)


# ---------------- Combate ----------------
def test_combate_ejemplo_del_enunciado():
    arthas = Guerrero("Arthas", 100, 30, 20)
    gandalf = Mago("Gandalf", 80, 40, 10)
    combate = Combate(arthas, gandalf, mostrar=False)
    assert combate.iniciar() is gandalf
    assert combate.ganador is gandalf
    assert combate.resultado == "Ganador: Gandalf"
    assert (arthas.vida, gandalf.vida) == (0, 2)


def test_combate_ganador_es_el_primero_si_derrota_antes():
    fuerte = Mago("Fuerte", 100, 100, 0)
    debil = Guerrero("Debil", 10, 5, 0)
    combate = Combate(fuerte, debil, mostrar=False)
    assert combate.iniciar() is fuerte
    assert debil.vida == 0


def test_combate_empate_tecnico():
    a = Arquero("A", 100, 10, 20)
    b = Arquero("B", 100, 10, 20)
    combate = Combate(a, b, mostrar=False)
    assert combate.iniciar() is None
    assert "Empate técnico" in combate.resultado
    assert (a.vida, b.vida) == (100, 100)


def test_combate_empate_por_50_rondas():
    # Cada ronda causa 1 de daño en total, pero 50 rondas no bastan para vencer.
    a = Guerrero("A", 100, 10, 11)   # 12 - 11 = 1 de daño a B
    b = Arquero("B", 100, 5, 11)     # no supera la defensa -> 0
    combate = Combate(a, b, mostrar=False)
    assert combate.iniciar() is None
    assert combate.rondas == 50
    assert "50 rondas" in combate.resultado
    assert b.vida == 50


def test_combate_valida_participantes():
    vivo = Guerrero("V", 100, 10, 5)
    caido = Guerrero("C", 10, 10, 5)
    caido.recibir_danio(10)
    with pytest.raises(TypeError):
        Combate(vivo, "otro")
    with pytest.raises(ValueError):
        Combate(vivo, caido)
    with pytest.raises(ValueError):
        Combate(vivo, vivo)


def test_combate_no_se_puede_iniciar_dos_veces():
    combate = Combate(Mago("A", 100, 100, 0), Guerrero("B", 10, 5, 0), mostrar=False)
    combate.iniciar()
    with pytest.raises(RuntimeError):
        combate.iniciar()


def test_cambiar_turno_alterna_atacante():
    a = Mago("A", 100, 10, 5)
    b = Mago("B", 100, 10, 5)
    combate = Combate(a, b, mostrar=False)
    assert combate._turno == 0
    combate.cambiar_turno()
    assert combate._turno == 1
    combate.cambiar_turno()
    assert combate._turno == 0


def test_verificar_ganador_sin_vencedor_devuelve_none():
    combate = Combate(Mago("A", 100, 10, 5), Mago("B", 100, 10, 5), mostrar=False)
    assert combate.verificar_ganador() is None
