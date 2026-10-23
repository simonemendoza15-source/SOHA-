from __future__ import annotations

import hashlib
import hmac
import logging
import os
from abc import ABC, abstractmethod
from datetime import time

logger = logging.getLogger(__name__)

DIAS = ("Lunes", "Martes", "Miércoles", "Jueves", "Viernes")


class ConflictoHorarioError(Exception):
    pass


class DatoDuplicadoError(Exception):
    pass


class BloqueHorario:

    def __init__(self, dia: str, hora_inicio: time, hora_fin: time):
        if dia not in DIAS:
            raise ValueError(f"Día inválido '{dia}'. Use uno de: {', '.join(DIAS)}")
        if not isinstance(hora_inicio, time) or not isinstance(hora_fin, time):
            raise TypeError("hora_inicio y hora_fin deben ser datetime.time")
        if hora_inicio >= hora_fin:
            raise ValueError("hora_inicio debe ser menor que hora_fin")
        self._dia = dia
        self._hora_inicio = hora_inicio
        self._hora_fin = hora_fin

    @property
    def dia(self) -> str:
        return self._dia

    @property
    def hora_inicio(self) -> time:
        return self._hora_inicio

    @property
    def hora_fin(self) -> time:
        return self._hora_fin

    def se_solapa_con(self, otro: BloqueHorario) -> bool:
        return (self._dia == otro._dia
                and self._hora_inicio < otro._hora_fin
                and otro._hora_inicio < self._hora_fin)

    def contiene(self, otro: BloqueHorario) -> bool:
        return (self._dia == otro._dia
                and self._hora_inicio <= otro._hora_inicio
                and otro._hora_fin <= self._hora_fin)

    def duracion_horas(self) -> float:
        ini = self._hora_inicio.hour + self._hora_inicio.minute / 60
        fin = self._hora_fin.hour + self._hora_fin.minute / 60
        return fin - ini

    def __eq__(self, otro: object) -> bool:
        return (isinstance(otro, BloqueHorario)
                and (self._dia, self._hora_inicio, self._hora_fin)
                == (otro._dia, otro._hora_inicio, otro._hora_fin))

    def __hash__(self) -> int:
        return hash((self._dia, self._hora_inicio, self._hora_fin))

    def __str__(self) -> str:
        return f"{self._dia} {self._hora_inicio:%H:%M}-{self._hora_fin:%H:%M}"

    def __repr__(self) -> str:
        return f"BloqueHorario({self})"


class Materia:
    def __init__(self, codigo: str, nombre: str, horas_semanales: int):
        if horas_semanales <= 0:
            raise ValueError("horas_semanales debe ser mayor que 0")
        self._codigo = codigo
        self._nombre = nombre
        self._horas_semanales = horas_semanales

    @property
    def codigo(self) -> str:
        return self._codigo

    @property
    def nombre(self) -> str:
        return self._nombre

    @property
    def horas_semanales(self) -> int:
        return self._horas_semanales

    def __str__(self) -> str:
        return f"{self._codigo} - {self._nombre}"


class Espacio:

    def __init__(self, codigo: str, capacidad: int, tipo: str = "Aula"):
        if capacidad <= 0:
            raise ValueError("capacidad debe ser mayor que 0")
        self._codigo = codigo
        self._capacidad = capacidad
        self._tipo = tipo

    @property
    def codigo(self) -> str:
        return self._codigo

    @property
    def capacidad(self) -> int:
        return self._capacidad

    @property
    def tipo(self) -> str:
        return self._tipo

    def __str__(self) -> str:
        return f"{self._tipo} {self._codigo} (cap. {self._capacidad})"


class Paralelo:

    def __init__(self, codigo: str, materia: Materia, num_estudiantes: int):
        if num_estudiantes < 0:
            raise ValueError("num_estudiantes no puede ser negativo")
        self._codigo = codigo
        self._materia = materia
        self._num_estudiantes = num_estudiantes

    @property
    def codigo(self) -> str:
        return self._codigo

    @property
    def materia(self) -> Materia:
        return self._materia

    @property
    def num_estudiantes(self) -> int:
        return self._num_estudiantes

    def __str__(self) -> str:
        return f"{self._materia.nombre} - Paralelo {self._codigo}"


class Horario:

    def __init__(self, paralelo: Paralelo, docente: Docente,
                 espacio: Espacio, bloque: BloqueHorario):
        self._paralelo = paralelo
        self._docente = docente
        self._espacio = espacio
        self._bloque = bloque

    @property
    def paralelo(self) -> Paralelo:
        return self._paralelo

    @property
    def docente(self) -> Docente:
        return self._docente

    @property
    def espacio(self) -> Espacio:
        return self._espacio

    @property
    def bloque(self) -> BloqueHorario:
        return self._bloque

    def motivo_choque(self, otro: Horario) -> str | None:
        if not self._bloque.se_solapa_con(otro._bloque):
            return None
        if self._docente is otro._docente:
            return f"el docente {self._docente.nombre} ya tiene clase ({otro._bloque})"
        if self._espacio is otro._espacio:
            return f"el espacio {self._espacio.codigo} ya está ocupado ({otro._bloque})"
        if self._paralelo is otro._paralelo:
            return f"el paralelo {self._paralelo.codigo} ya tiene clase ({otro._bloque})"
        return None

    def __str__(self) -> str:
        return (f"{self._bloque} | {self._paralelo} | "
                f"{self._docente.nombre} | {self._espacio.codigo}")


class Usuario(ABC):

    def __init__(self, id_usuario: int, nombre: str, email: str, contrasena: str):
        self._id_usuario = id_usuario
        self._nombre = nombre
        self._email = email
        self._salt = os.urandom(16)
        self._hash = self._cifrar(contrasena)
        self._sesion_activa = False

    def _cifrar(self, contrasena: str) -> bytes:
        return hashlib.pbkdf2_hmac("sha256", contrasena.encode(), self._salt, 100_000)

    def _validar_credenciales(self, email: str, contrasena: str) -> bool:
        return (email == self._email
                and hmac.compare_digest(self._hash, self._cifrar(contrasena)))

    def iniciar_sesion(self, email: str, contrasena: str) -> bool:
        self._sesion_activa = self._validar_credenciales(email, contrasena)
        logger.info("Inicio de sesión %s: %s",
                    "exitoso" if self._sesion_activa else "fallido", self._nombre)
        return self._sesion_activa

    def cerrar_sesion(self) -> None:
        self._sesion_activa = False
        logger.info("Sesión cerrada: %s", self._nombre)

    @property
    def id_usuario(self) -> int:
        return self._id_usuario

    @property
    def nombre(self) -> str:
        return self._nombre

    @property
    def email(self) -> str:
        return self._email

    @property
    def sesion_activa(self) -> bool:
        return self._sesion_activa

    @abstractmethod
    def rol(self) -> str:
        ...

    @abstractmethod
    def consultar_horario(self, horarios: list[Horario]) -> list[Horario]:
        ...

    def __str__(self) -> str:
        return f"{self.rol()}: {self._nombre}"


class Docente(Usuario):
    def __init__(self, id_usuario: int, nombre: str, email: str, contrasena: str,
                 disponibilidad: list[BloqueHorario] | None = None,
                 preferencias: str = "",
                 descansos: list[BloqueHorario] | None = None):
        super().__init__(id_usuario, nombre, email, contrasena)
        self._disponibilidad = list(disponibilidad or [])
        self._preferencias = preferencias
        self._descansos = list(descansos or [])

    def rol(self) -> str:
        return "Docente"

    @property
    def disponibilidad(self) -> tuple[BloqueHorario, ...]:
        return tuple(self._disponibilidad)

    @property
    def descansos(self) -> tuple[BloqueHorario, ...]:
        return tuple(self._descansos)

    @property
    def preferencias(self) -> str:
        return self._preferencias

    def registrar_disponibilidad(self, bloques: list[BloqueHorario]) -> None:
        self._disponibilidad.extend(bloques)
        logger.info("%s: %d bloque(s) de disponibilidad registrados",
                    self._nombre, len(bloques))

    def cambiar_preferencias(self, nueva_pref: str) -> None:
        self._preferencias = nueva_pref

    def esta_disponible(self, bloque: BloqueHorario) -> bool:
        dentro = any(d.contiene(bloque) for d in self._disponibilidad)
        en_descanso = any(r.se_solapa_con(bloque) for r in self._descansos)
        return dentro and not en_descanso

    def consultar_horario(self, horarios: list[Horario]) -> list[Horario]:
        return [h for h in horarios if h.docente is self]


class Estudiante(Usuario):
    def __init__(self, id_usuario: int, nombre: str, email: str, contrasena: str,
                 carrera: str, paralelos: list[Paralelo] | None = None):
        super().__init__(id_usuario, nombre, email, contrasena)
        self._carrera = carrera
        self._paralelos = list(paralelos or [])

    def rol(self) -> str:
        return "Estudiante"

    @property
    def carrera(self) -> str:
        return self._carrera

    @property
    def paralelos(self) -> tuple[Paralelo, ...]:
        return tuple(self._paralelos)

    def consultar_horario(self, horarios: list[Horario]) -> list[Horario]:
        return [h for h in horarios if h.paralelo in self._paralelos]


class Administrador(Usuario):
    def __init__(self, id_usuario: int, nombre: str, email: str, contrasena: str,
                 rol_academico: str = "Coordinador"):
        super().__init__(id_usuario, nombre, email, contrasena)
        self._rol_academico = rol_academico
        self._espacios: list[Espacio] = []
        self._docentes: list[Docente] = []
        self._materias: list[Materia] = []

    def rol(self) -> str:
        return "Administrador"

    @property
    def espacios(self) -> tuple[Espacio, ...]:
        return tuple(self._espacios)

    @property
    def docentes(self) -> tuple[Docente, ...]:
        return tuple(self._docentes)

    @property
    def materias(self) -> tuple[Materia, ...]:
        return tuple(self._materias)

    def registrar_espacio(self, espacio: Espacio) -> None:
        if not isinstance(espacio, Espacio):
            raise TypeError("Se esperaba un Espacio")
        if any(e.codigo == espacio.codigo for e in self._espacios):
            raise DatoDuplicadoError(f"Ya existe el espacio {espacio.codigo}")
        self._espacios.append(espacio)

    def registrar_docente(self, docente: Docente) -> None:
        if not isinstance(docente, Docente):
            raise TypeError("Se esperaba un Docente")
        if any(d.id_usuario == docente.id_usuario for d in self._docentes):
            raise DatoDuplicadoError(f"Ya existe el docente {docente.id_usuario}")
        self._docentes.append(docente)

    def registrar_materia(self, materia: Materia) -> None:
        if not isinstance(materia, Materia):
            raise TypeError("Se esperaba una Materia")
        if any(m.codigo == materia.codigo for m in self._materias):
            raise DatoDuplicadoError(f"Ya existe la materia {materia.codigo}")
        self._materias.append(materia)

    def consultar_horario(self, horarios: list[Horario]) -> list[Horario]:
        return list(horarios)


class GestorHorarios:
    def __init__(self):
        self._horarios: list[Horario] = []

    @property
    def horarios(self) -> tuple[Horario, ...]:
        return tuple(self._horarios)

    def agregar(self, horario: Horario) -> None:
        if not horario.docente.esta_disponible(horario.bloque):
            raise ConflictoHorarioError(
                f"{horario.docente.nombre} no está disponible en {horario.bloque}")
        if horario.espacio.capacidad < horario.paralelo.num_estudiantes:
            raise ConflictoHorarioError(
                f"El espacio {horario.espacio.codigo} (cap. {horario.espacio.capacidad}) "
                f"no alcanza para {horario.paralelo.num_estudiantes} estudiantes")
        for existente in self._horarios:
            motivo = horario.motivo_choque(existente)
            if motivo:
                raise ConflictoHorarioError(f"Choque: {motivo}")
        self._horarios.append(horario)

    def horas_asignadas(self, paralelo: Paralelo) -> float:
        return sum(h.bloque.duracion_horas()
                   for h in self._horarios if h.paralelo is paralelo)

    def materia_completa(self, paralelo: Paralelo) -> bool:
        return self.horas_asignadas(paralelo) >= paralelo.materia.horas_semanales


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    admin = Administrador(1, "Ana", "ana@uni.edu", "admin123")
    prof = Docente(2, "Carlos", "carlos@uni.edu", "clave456",
                   disponibilidad=[BloqueHorario("Lunes", time(7), time(13))],
                   descansos=[BloqueHorario("Lunes", time(10), time(11))])
    admin.registrar_docente(prof)

    poo = Materia("INF101", "Programación Orientada a Objetos", 4)
    aula = Espacio("A-101", 30)
    pequena = Espacio("A-102", 10)
    admin.registrar_materia(poo)
    admin.registrar_espacio(aula)
    admin.registrar_espacio(pequena)

    paralelo = Paralelo("A", poo, 25)
    est = Estudiante(3, "Luis", "luis@uni.edu", "pass789", "Software", [paralelo])

    gestor = GestorHorarios()
    intentos = [
        Horario(paralelo, prof, aula, BloqueHorario("Lunes", time(8), time(10))),
        Horario(paralelo, prof, aula, BloqueHorario("Lunes", time(9), time(11))),
        Horario(paralelo, prof, aula, BloqueHorario("Lunes", time(10), time(11))),
        Horario(paralelo, prof, pequena, BloqueHorario("Lunes", time(11), time(12))),
    ]
    for h in intentos:
        try:
            gestor.agregar(h)
            print(f"✔ Agregado: {h}")
        except ConflictoHorarioError as e:
            print(f"✘ Rechazado: {e}")

    for u in (admin, prof, est):
        print(f"{u} -> {len(u.consultar_horario(list(gestor.horarios)))} clase(s)")
