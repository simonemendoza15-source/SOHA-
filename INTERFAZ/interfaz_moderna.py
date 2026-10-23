"""
SOHA · Interfaz moderna (Tkinter, sin instalar nada extra).
Ejecutar:  python interfaz_moderna.py        (necesita soha_modelo.py en la misma carpeta)

Cuentas de demostración:
    Administrador  ana@uni.edu     / admin123
    Docente        carlos@uni.edu  / clave456
    Estudiante     luis@uni.edu    / pass789
"""
from __future__ import annotations

import tkinter as tk
from collections import Counter
from datetime import datetime, time
from tkinter import font as tkfont
from tkinter import ttk

from soha_modelo import (
    DIAS, Administrador, BloqueHorario, ConflictoHorarioError, DatoDuplicadoError,
    Docente, Espacio, Estudiante, GestorHorarios, Horario, Materia, Paralelo, Usuario,
)

# ----------------------------------------------------------------------
# Paleta y tipografía
# ----------------------------------------------------------------------
BG, PANEL, CARD, CARD2, LINE, FIELD = "#0b0f1a", "#0f1424", "#151b2e", "#1b2340", "#263052", "#0e1324"
TXT, MUTED = "#e8ebf7", "#8b93b3"
ACC, ACC_H, ACC_DIM, CYAN = "#7c5cff", "#6a49f0", "#241d52", "#22d3ee"
OK, ERR, WARN = "#34d399", "#f87171", "#fbbf24"
TINTES = [("#2b2358", "#c4b5ff"), ("#12343d", "#8aeaf8"), ("#3b2b16", "#fcd48a"),
          ("#3a1f33", "#f5a8dc"), ("#173a2b", "#8df0c0"), ("#2a2f4d", "#aab6ff")]
FAM = "TkDefaultFont"
ERRORES = (ValueError, TypeError, ConflictoHorarioError, DatoDuplicadoError)
TIPOS_ESPACIO = ["Aula", "Laboratorio"]


def F(tam: int = 10, negrita: bool = False):
    return (FAM, tam, "bold" if negrita else "normal")


# ======================================================================
# Lógica (sin Tkinter)
# ======================================================================
class Sistema:
    def __init__(self):
        self.admin = Administrador(1, "Ana", "ana@uni.edu", "admin123")
        self.gestor = GestorHorarios()
        self.estudiantes: list[Estudiante] = []
        self.paralelos: list[Paralelo] = []
        self._sembrar()

    def _sembrar(self) -> None:
        carlos = Docente(2, "Carlos", "carlos@uni.edu", "clave456",
                         disponibilidad=[BloqueHorario("Lunes", time(7), time(13)),
                                         BloqueHorario("Martes", time(7), time(13)),
                                         BloqueHorario("Miércoles", time(7), time(13))],
                         descansos=[BloqueHorario("Lunes", time(10), time(11))])
        self.admin.registrar_docente(carlos)
        poo = Materia("INF101", "Programación Orientada a Objetos", 4)
        bd = Materia("INF102", "Bases de Datos", 3)
        for m in (poo, bd):
            self.admin.registrar_materia(m)
        a101, a102 = Espacio("A-101", 30), Espacio("A-102", 10)
        self.admin.registrar_espacio(a101)
        self.admin.registrar_espacio(a102)
        pa, pb = Paralelo("A", poo, 25), Paralelo("A", bd, 22)
        self.paralelos += [pa, pb]
        self.estudiantes.append(Estudiante(3, "Luis", "luis@uni.edu", "pass789", "Software", [pa, pb]))
        self.gestor.agregar(Horario(pa, carlos, a101, BloqueHorario("Lunes", time(8), time(10))))

    # -- utilidades ----------------------------------------------------
    @property
    def docentes(self) -> list[Docente]:
        return list(self.admin.docentes)

    def usuarios(self) -> list[Usuario]:
        return [self.admin, *self.admin.docentes, *self.estudiantes]

    def ordenados(self, horarios=None) -> list[Horario]:
        lista = self.gestor.horarios if horarios is None else horarios
        return sorted(lista, key=lambda h: (DIAS.index(h.bloque.dia), h.bloque.hora_inicio))

    @staticmethod
    def _entero(texto, nombre: str) -> int:
        try:
            return int(str(texto).strip())
        except ValueError:
            raise ValueError(f"{nombre} debe ser un número entero") from None

    @staticmethod
    def _hora(texto, nombre: str) -> time:
        try:
            return datetime.strptime(str(texto).strip(), "%H:%M").time()
        except ValueError:
            raise ValueError(f"{nombre} debe tener formato HH:MM (ej. 08:30)") from None

    @staticmethod
    def _req(texto, nombre: str) -> str:
        if not str(texto).strip():
            raise ValueError(f"{nombre} es obligatorio")
        return str(texto).strip()

    def _validar_usuario(self, nombre, email, clave):
        nombre, email = self._req(nombre, "El nombre"), self._req(email, "El correo")
        if "@" not in email or "." not in email.split("@")[-1]:
            raise ValueError("El correo no es válido")
        if len(clave) < 6:
            raise ValueError("La contraseña debe tener al menos 6 caracteres")
        if any(u.email == email for u in self.usuarios()):
            raise DatoDuplicadoError(f"Ya existe un usuario con el correo {email}")
        return nombre, email

    def _nuevo_id(self) -> int:
        return max(u.id_usuario for u in self.usuarios()) + 1

    # -- operaciones -----------------------------------------------------
    def autenticar(self, email: str, clave: str) -> Usuario | None:
        for u in self.usuarios():
            if u.iniciar_sesion(email.strip(), clave):
                return u
        return None

    def crear_docente(self, nombre, email, clave) -> str:
        nombre, email = self._validar_usuario(nombre, email, clave)
        self.admin.registrar_docente(Docente(self._nuevo_id(), nombre, email, clave))
        return f"Docente {nombre} registrado"

    def crear_materia(self, codigo, nombre, horas) -> str:
        codigo, nombre = self._req(codigo, "El código"), self._req(nombre, "El nombre")
        self.admin.registrar_materia(Materia(codigo, nombre, self._entero(horas, "Horas semanales")))
        return f"Materia {codigo} registrada"

    def crear_espacio(self, codigo, capacidad, tipo) -> str:
        codigo = self._req(codigo, "El código")
        self.admin.registrar_espacio(Espacio(codigo, self._entero(capacidad, "Capacidad"), tipo or "Aula"))
        return f"Espacio {codigo} registrado"

    def crear_paralelo(self, codigo, materia, estudiantes) -> str:
        codigo = self._req(codigo, "El código")
        if materia is None:
            raise ValueError("Primero registre una materia")
        if any(p.codigo == codigo and p.materia is materia for p in self.paralelos):
            raise DatoDuplicadoError(f"Ya existe el paralelo {codigo} de {materia.nombre}")
        self.paralelos.append(Paralelo(codigo, materia, self._entero(estudiantes, "Estudiantes")))
        return f"Paralelo {codigo} de {materia.nombre} registrado"

    def crear_estudiante(self, nombre, email, clave, carrera, paralelo) -> str:
        nombre, email = self._validar_usuario(nombre, email, clave)
        carrera = self._req(carrera, "La carrera")
        self.estudiantes.append(Estudiante(self._nuevo_id(), nombre, email, clave, carrera,
                                           [paralelo] if paralelo else []))
        return f"Estudiante {nombre} registrado"

    def registrar_disponibilidad(self, docente, dia, inicio, fin) -> str:
        if docente is None:
            raise ValueError("Seleccione un docente")
        bloque = BloqueHorario(dia, self._hora(inicio, "La hora de inicio"), self._hora(fin, "La hora de fin"))
        docente.registrar_disponibilidad([bloque])
        return f"Disponibilidad registrada: {bloque}"

    def asignar_horario(self, paralelo, docente, espacio, dia, inicio, fin) -> str:
        if None in (paralelo, docente, espacio):
            raise ValueError("Complete paralelo, docente y espacio")
        bloque = BloqueHorario(dia, self._hora(inicio, "La hora de inicio"), self._hora(fin, "La hora de fin"))
        self.gestor.agregar(Horario(paralelo, docente, espacio, bloque))
        return f"Clase asignada: {bloque} · {paralelo.materia.codigo}-{paralelo.codigo}"

    # -- asistente: análisis y generación automática ----------------------
    def faltan(self, p: Paralelo) -> float:
        return p.materia.horas_semanales - self.gestor.horas_asignadas(p)

    def estadisticas(self) -> dict:
        return {"docentes": len(self.docentes), "espacios": len(self.admin.espacios),
                "paralelos": len(self.paralelos), "clases": len(self.gestor.horarios),
                "asignadas": sum(h.bloque.duracion_horas() for h in self.gestor.horarios),
                "requeridas": sum(p.materia.horas_semanales for p in self.paralelos)}

    def insights(self) -> list[tuple[str, str]]:
        out: list[tuple[str, str]] = []
        max_cap = max((e.capacidad for e in self.admin.espacios), default=0)
        for p in self.paralelos:
            if p.num_estudiantes > max_cap:
                out.append(("err", f"{p} tiene {p.num_estudiantes} estudiantes y ningún espacio alcanza (máx. {max_cap})"))
            elif self.faltan(p) > 0:
                out.append(("warn", f"{p.materia.codigo}-{p.codigo}: faltan {self.faltan(p):g} h por asignar"))
        out += [("warn", f"{d.nombre} no tiene disponibilidad registrada") for d in self.docentes if not d.disponibilidad]
        uso = Counter(h.espacio.codigo for h in self.gestor.horarios)
        if uso:
            cod, n = uso.most_common(1)[0]
            out.append(("info", f"Espacio más usado: {cod} ({n} clase(s) por semana)"))
        if self.paralelos and not any(n in ("err", "warn") for n, _ in out):
            out.insert(0, ("ok", "Todos los paralelos tienen su carga completa"))
        return out or [("info", "Registra docentes, espacios y paralelos para empezar")]

    def _es_valido(self, h: Horario) -> bool:
        return (h.docente.esta_disponible(h.bloque)
                and h.espacio.capacidad >= h.paralelo.num_estudiantes
                and not any(h.motivo_choque(o) for o in self.gestor.horarios))

    def _buscar_hueco(self, p: Paralelo) -> Horario | None:
        carga_dia = Counter(h.bloque.dia for h in self.gestor.horarios if h.paralelo is p)
        previos = {id(h.docente) for h in self.gestor.horarios if h.paralelo is p}
        docentes = sorted(self.docentes, key=lambda d: id(d) not in previos)
        espacios = sorted(self.admin.espacios, key=lambda e: e.capacidad)       # el más ajustado
        for dia in sorted(DIAS, key=lambda d: carga_dia[d]):                    # reparte la carga
            for hora in range(7, 19):
                bloque = BloqueHorario(dia, time(hora), time(hora + 1))
                for d in docentes:
                    for e in espacios:
                        cand = Horario(p, d, e, bloque)
                        if self._es_valido(cand):
                            return cand
        return None

    def autogenerar(self) -> tuple[int, list[str]]:
        creadas, pendientes = 0, []
        for p in self.paralelos:
            while self.faltan(p) > 0:
                h = self._buscar_hueco(p)
                if h is None:
                    pendientes.append(f"{p.materia.codigo}-{p.codigo}")
                    break
                self.gestor.agregar(h)
                creadas += 1
        return creadas, pendientes


# ======================================================================
# Widgets propios
# ======================================================================
def _rr(c: tk.Canvas, x1, y1, x2, y2, r, **kw):
    pts = [x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r, x2, y2 - r, x2, y2,
           x2 - r, y2, x1 + r, y2, x1, y2, x1, y2 - r, x1, y1 + r, x1, y1]
    return c.create_polygon(pts, smooth=True, **kw)


def tarjeta(master, **kw) -> tk.Frame:
    return tk.Frame(master, bg=CARD, highlightbackground=LINE, highlightthickness=1, **kw)


class Boton(tk.Canvas):
    ESTILOS = {"primario": (ACC, ACC_H, "#ffffff"), "suave": (CARD2, LINE, TXT), "peligro": (ERR, "#ef4444", "#fff")}

    def __init__(self, master, texto, comando, estilo="primario", ancho=150, alto=38):
        super().__init__(master, width=ancho, height=alto, bg=master["bg"], highlightthickness=0, cursor="hand2")
        self.cmd, (self.c0, self.c1, fg) = comando, self.ESTILOS[estilo]
        self.fondo = _rr(self, 1, 1, ancho - 1, alto - 1, 12, fill=self.c0, outline="")
        self.create_text(ancho / 2, alto / 2, text=texto, fill=fg, font=F(10, True))
        self.bind("<Enter>", lambda e: self.itemconfig(self.fondo, fill=self.c1))
        self.bind("<Leave>", lambda e: self.itemconfig(self.fondo, fill=self.c0))
        self.bind("<ButtonRelease-1>", lambda e: self.cmd())


def campo(master, etiqueta: str, tipo: str, ancho: int = 20):
    cont = tk.Frame(master, bg=master["bg"])
    tk.Label(cont, text=etiqueta, bg=cont["bg"], fg=MUTED, font=F(9)).pack(anchor="w", pady=(0, 3))
    if tipo == "lista":
        w = ttk.Combobox(cont, state="readonly", width=ancho - 2, style="Dark.TCombobox", font=F(10))
        w.pack(ipady=4)
    else:
        borde = tk.Frame(cont, bg=LINE)
        borde.pack()
        w = tk.Entry(borde, width=ancho, bg=FIELD, fg=TXT, insertbackground=TXT, relief="flat",
                     font=F(10), show="•" if tipo == "clave" else "")
        w.pack(padx=1, pady=1, ipady=7, ipadx=6)
        w.bind("<FocusIn>", lambda e: borde.config(bg=ACC))
        w.bind("<FocusOut>", lambda e: borde.config(bg=LINE))
    return cont, w


def aplicar_estilos(root: tk.Tk) -> None:
    st = ttk.Style(root)
    st.theme_use("clam")
    st.layout("Dark.Treeview", [("Treeview.treearea", {"sticky": "nswe"})])
    st.configure("Dark.Treeview", background=CARD, fieldbackground=CARD, foreground=TXT,
                 rowheight=36, borderwidth=0, font=F(10))
    st.configure("Dark.Treeview.Heading", background=CARD2, foreground=MUTED, relief="flat",
                 font=F(9, True), padding=9)
    st.map("Dark.Treeview", background=[("selected", ACC)], foreground=[("selected", "#fff")])
    st.map("Dark.Treeview.Heading", background=[("active", CARD2)])
    st.configure("Dark.TCombobox", fieldbackground=FIELD, background=CARD2, foreground=TXT,
                 arrowcolor=MUTED, bordercolor=LINE, lightcolor=FIELD, darkcolor=FIELD, padding=6,
                 selectbackground=FIELD, selectforeground=TXT)
    st.map("Dark.TCombobox", fieldbackground=[("readonly", FIELD)], foreground=[("readonly", TXT)],
           selectbackground=[("readonly", FIELD)], selectforeground=[("readonly", TXT)])
    st.configure("Dark.Vertical.TScrollbar", background=CARD2, troughcolor=CARD, bordercolor=CARD,
                 arrowcolor=MUTED, lightcolor=CARD2, darkcolor=CARD2)
    for opcion, valor in (("background", FIELD), ("foreground", TXT), ("selectBackground", ACC), ("selectForeground", "#fff")):
        root.option_add(f"*TCombobox*Listbox.{opcion}", valor)


# ======================================================================
# Páginas
# ======================================================================
class PaginaCrud(tk.Frame):
    """Formulario opcional + tabla. campos = [(etiqueta, 'texto'|'clave'|'lista', fuente)]."""

    def __init__(self, master, app, campos, columnas, filas, crear=None, boton="Agregar"):
        super().__init__(master, bg=BG)
        self.app, self.filas, self.crear = app, filas, crear
        self.widgets: list[tuple[str, object, tk.Widget]] = []
        self.mapas: list[dict] = []
        if campos:
            form = tarjeta(self)
            form.pack(fill="x", pady=(0, 16))
            ui = tk.Frame(form, bg=CARD)
            ui.pack(fill="x", padx=20, pady=16)
            tk.Label(ui, text="Nuevo registro", bg=CARD, fg=TXT, font=F(11, True)).grid(
                row=0, column=0, columnspan=5, sticky="w", pady=(0, 10))
            for i, (etiqueta, tipo, fuente) in enumerate(campos):
                cont, w = campo(ui, etiqueta, tipo)
                cont.grid(row=1 + i // 4, column=i % 4, padx=(0, 16), pady=(0, 8), sticky="w")
                if tipo != "lista":
                    w.bind("<Return>", lambda e: self._enviar())
                self.widgets.append((tipo, fuente, w))
            n = len(campos)
            Boton(ui, boton, self._enviar).grid(row=1 + (n - 1) // 4, column=n % 4 if n % 4 else 4,
                                                sticky="sw", pady=(0, 8))
        caja = tarjeta(self)
        caja.pack(fill="both", expand=True)
        self.tabla = ttk.Treeview(caja, columns=columnas, show="headings", style="Dark.Treeview")
        for c in columnas:
            self.tabla.heading(c, text=c.upper(), anchor="w")
            self.tabla.column(c, anchor="w", width=140, stretch=True)
        self.tabla.tag_configure("par", background=CARD)
        self.tabla.tag_configure("impar", background="#181f36")
        barra = ttk.Scrollbar(caja, orient="vertical", command=self.tabla.yview, style="Dark.Vertical.TScrollbar")
        self.tabla.configure(yscrollcommand=barra.set)
        self.tabla.pack(side="left", fill="both", expand=True, padx=(2, 0), pady=2)
        barra.pack(side="right", fill="y")

    def refrescar(self) -> None:
        self.mapas = []
        for tipo, fuente, w in self.widgets:
            if tipo != "lista":
                self.mapas.append({})
                continue
            mapa = {str(o): o for o in fuente()}
            self.mapas.append(mapa)
            actual = w.get()
            w["values"] = list(mapa)
            if actual not in mapa:
                w.set(next(iter(mapa), ""))
        self.tabla.delete(*self.tabla.get_children())
        for i, fila in enumerate(self.filas()):
            self.tabla.insert("", "end", values=fila, tags=("par" if i % 2 == 0 else "impar",))

    def _enviar(self) -> None:
        valores = [m.get(w.get()) if t == "lista" else w.get()
                   for (t, _f, w), m in zip(self.widgets, self.mapas)]
        try:
            mensaje = self.crear(*valores)
        except ERRORES as e:
            self.app.toast(str(e), "err")
            return
        for t, _f, w in self.widgets:
            if t != "lista":
                w.delete(0, "end")
        self.app.toast(mensaje, "ok")
        self.app.refrescar_todo()


class PaginaSemana(tk.Frame):
    def __init__(self, master, fuente):
        super().__init__(master, bg=BG)
        self.fuente = fuente
        self.caja = tarjeta(self)
        self.caja.pack(fill="both", expand=True)

    def refrescar(self) -> None:
        for w in self.caja.winfo_children():
            w.destroy()
        hs = self.fuente()
        ini = min([7] + [h.bloque.hora_inicio.hour for h in hs])
        fin = max([17] + [h.bloque.hora_fin.hour + (h.bloque.hora_fin.minute > 0) for h in hs])
        colores: dict[str, tuple] = {}
        celdas: dict[tuple[int, str], list] = {}
        for h in hs:
            t = colores.setdefault(h.paralelo.materia.codigo, TINTES[len(colores) % len(TINTES)])
            b = h.bloque
            for hora in range(b.hora_inicio.hour, b.hora_fin.hour + (b.hora_fin.minute > 0)):
                celdas.setdefault((hora, b.dia), []).append(
                    (f"{h.paralelo.materia.codigo}-{h.paralelo.codigo}\n{h.docente.nombre} · {h.espacio.codigo}", t))
        malla = tk.Frame(self.caja, bg=CARD)
        malla.pack(fill="both", expand=True, padx=12, pady=12)
        for c, dia in enumerate(DIAS, start=1):
            tk.Label(malla, text=dia.upper(), bg=CARD, fg=MUTED, font=F(9, True)).grid(row=0, column=c, pady=(0, 6))
            malla.columnconfigure(c, weight=1, uniform="d")
        for r, hora in enumerate(range(ini, fin), start=1):
            malla.rowconfigure(r, weight=1)
            tk.Label(malla, text=f"{hora:02d}:00", bg=CARD, fg=MUTED, font=F(9)).grid(row=r, column=0, padx=(0, 8), sticky="n")
            for c, dia in enumerate(DIAS, start=1):
                items = celdas.get((hora, dia))
                bg, fg = (items[0][1] if items else (FIELD, MUTED))
                tk.Label(malla, text="\n".join(t for t, _ in items) if items else "", bg=bg, fg=fg,
                         font=F(8, bool(items)), justify="left", anchor="w", padx=8, pady=4,
                         wraplength=130).grid(row=r, column=c, sticky="nsew", padx=2, pady=2)


class PaginaInicio(tk.Frame):
    def __init__(self, master, app):
        super().__init__(master, bg=BG)
        self.app = app

    def _stat(self, padre, valor, etiqueta, color):
        t = tarjeta(padre)
        tk.Frame(t, bg=color, height=3).pack(fill="x")
        tk.Label(t, text=str(valor), bg=CARD, fg=TXT, font=F(26, True)).pack(anchor="w", padx=18, pady=(12, 0))
        tk.Label(t, text=etiqueta, bg=CARD, fg=MUTED, font=F(9)).pack(anchor="w", padx=18, pady=(0, 14))
        return t

    def _barra(self, padre, fraccion):
        c = tk.Canvas(padre, height=8, bg=CARD, highlightthickness=0)
        c.pack(fill="x", pady=(2, 10))
        def dibujar(_e=None, c=c):
            c.delete("all")
            w = max(c.winfo_width(), 10)
            _rr(c, 0, 0, w, 8, 4, fill=FIELD, outline="")
            if fraccion > 0:
                _rr(c, 0, 0, max(8, w * min(fraccion, 1)), 8, 4, fill=OK if fraccion >= 1 else ACC, outline="")
        c.bind("<Configure>", dibujar)

    def refrescar(self) -> None:
        for w in self.winfo_children():
            w.destroy()
        s, u = self.app.sistema, self.app.usuario
        fila = tk.Frame(self, bg=BG)
        fila.pack(fill="x")
        if isinstance(u, Administrador):
            e = s.estadisticas()
            datos = [(e["docentes"], "Docentes", ACC), (e["espacios"], "Espacios", CYAN),
                     (e["paralelos"], "Paralelos", WARN), (e["clases"], "Clases asignadas", OK),
                     (f'{e["asignadas"]:g}/{e["requeridas"]}', "Horas cubiertas", ACC)]
        else:
            mis = self.app.mis_horarios()
            datos = [(len(mis), "Clases por semana", ACC),
                     (f'{sum(h.bloque.duracion_horas() for h in mis):g}', "Horas por semana", CYAN),
                     (len({h.paralelo.materia.codigo for h in mis}), "Materias", OK)]
        for i, (v, et, col) in enumerate(datos):
            fila.columnconfigure(i, weight=1, uniform="s")
            self._stat(fila, v, et, col).grid(row=0, column=i, sticky="nsew", padx=(0 if i == 0 else 8, 0))

        cuerpo = tk.Frame(self, bg=BG)
        cuerpo.pack(fill="both", expand=True, pady=(16, 0))
        cuerpo.columnconfigure((0, 1), weight=1, uniform="c")
        izq, der = tarjeta(cuerpo), tarjeta(cuerpo)
        izq.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        der.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        if isinstance(u, Administrador):
            tk.Label(izq, text="✦  Asistente SOHA", bg=CARD, fg=TXT, font=F(12, True)).pack(anchor="w", padx=20, pady=(18, 2))
            tk.Label(izq, text="Análisis automático de tu planificación", bg=CARD, fg=MUTED, font=F(9)).pack(anchor="w", padx=20, pady=(0, 10))
            colores = {"ok": OK, "warn": WARN, "err": ERR, "info": CYAN}
            for nivel, texto in s.insights():
                f = tk.Frame(izq, bg=CARD)
                f.pack(fill="x", padx=20, pady=3)
                tk.Label(f, text="●", bg=CARD, fg=colores[nivel], font=F(10)).pack(side="left", anchor="n")
                tk.Label(f, text=texto, bg=CARD, fg=TXT, font=F(10), wraplength=360, justify="left").pack(side="left", padx=8)
            Boton(izq, "✦  Generar horarios automáticamente", self.app.autogenerar, ancho=290).pack(anchor="w", padx=20, pady=18)

            tk.Label(der, text="Avance por paralelo", bg=CARD, fg=TXT, font=F(12, True)).pack(anchor="w", padx=20, pady=(18, 10))
            caja = tk.Frame(der, bg=CARD)
            caja.pack(fill="x", padx=20, pady=(0, 14))
            for p in s.paralelos:
                req = p.materia.horas_semanales
                top = tk.Frame(caja, bg=CARD)
                top.pack(fill="x")
                tk.Label(top, text=f"{p.materia.codigo} · Paralelo {p.codigo}", bg=CARD, fg=TXT, font=F(10)).pack(side="left")
                tk.Label(top, text=f"{s.gestor.horas_asignadas(p):g} / {req} h", bg=CARD, fg=MUTED, font=F(9)).pack(side="right")
                self._barra(caja, s.gestor.horas_asignadas(p) / req)
            if not s.paralelos:
                tk.Label(caja, text="Aún no hay paralelos.", bg=CARD, fg=MUTED).pack(anchor="w")
        else:
            tk.Label(izq, text=f"Hola, {u.nombre}", bg=CARD, fg=TXT, font=F(14, True)).pack(anchor="w", padx=20, pady=(18, 2))
            tk.Label(izq, text="Este es el resumen de tu semana.", bg=CARD, fg=MUTED, font=F(10)).pack(anchor="w", padx=20)
            tk.Label(der, text="Tus próximas clases", bg=CARD, fg=TXT, font=F(12, True)).pack(anchor="w", padx=20, pady=(18, 10))
            for h in s.ordenados(self.app.mis_horarios())[:6]:
                tk.Label(der, text=f"{h.bloque}  ·  {h.paralelo.materia.codigo}  ·  {h.espacio.codigo}", bg=CARD,
                         fg=TXT, font=F(10)).pack(anchor="w", padx=20, pady=3)
            if not self.app.mis_horarios():
                tk.Label(der, text="Todavía no tienes clases asignadas.", bg=CARD, fg=MUTED).pack(anchor="w", padx=20)


class Degradado(tk.Canvas):
    def __init__(self, master):
        super().__init__(master, bg=BG, highlightthickness=0)
        self.bind("<Configure>", self._dibujar)

    def _dibujar(self, _e=None) -> None:
        w, h = self.winfo_width(), self.winfo_height()
        self.delete("all")
        a, b = self.winfo_rgb("#2a1d6e"), self.winfo_rgb("#080b14")
        for y in range(0, h, 2):
            t = y / max(h, 1)
            col = "#%02x%02x%02x" % tuple(int((p + (q - p) * t) / 256) for p, q in zip(a, b))
            self.create_rectangle(0, y, w, y + 2, fill=col, outline="")
        for r in range(80, 560, 70):
            self.create_oval(w - r, h - r, w + r, h + r, outline="#352a85", width=1)
        self.create_text(56, h * 0.30, text="SOHA", anchor="w", fill="#ffffff", font=F(44, True))
        self.create_text(58, h * 0.30 + 52, text="Sistema de Horarios Optimizado", anchor="w", fill="#b9a8ff", font=F(14))
        for i, txt in enumerate(("Detecta choques de docentes, aulas y paralelos",
                                 "Respeta disponibilidad y descansos",
                                 "Genera horarios automáticamente")):
            self.create_text(58, h * 0.30 + 120 + i * 30, text=f"✦  {txt}", anchor="w", fill="#cfd5f0", font=F(11))


class PantallaLogin(tk.Frame):
    def __init__(self, master, app):
        super().__init__(master, bg=BG)
        self.app = app
        Degradado(self).place(relx=0, rely=0, relwidth=0.56, relheight=1)
        der = tk.Frame(self, bg=BG)
        der.place(relx=0.56, rely=0, relwidth=0.44, relheight=1)
        caja = tarjeta(der)
        caja.place(relx=0.5, rely=0.5, anchor="center")
        ui = tk.Frame(caja, bg=CARD)
        ui.pack(padx=36, pady=32)
        tk.Label(ui, text="Bienvenido", bg=CARD, fg=TXT, font=F(20, True)).pack(anchor="w")
        tk.Label(ui, text="Inicia sesión para continuar", bg=CARD, fg=MUTED, font=F(10)).pack(anchor="w", pady=(0, 18))
        c1, self.email = campo(ui, "Correo", "texto", 30)
        c1.pack(anchor="w", pady=(0, 10))
        c2, self.clave = campo(ui, "Contraseña", "clave", 30)
        c2.pack(anchor="w", pady=(0, 6))
        self.error = tk.Label(ui, text="", bg=CARD, fg=ERR, font=F(9))
        self.error.pack(anchor="w", pady=(0, 6))
        Boton(ui, "Iniciar sesión", self._entrar, ancho=280, alto=42).pack(pady=(4, 14))
        tk.Label(ui, bg=CARD, fg=MUTED, font=F(9), justify="left", text=(
            "Cuentas de prueba\nana@uni.edu · admin123  (Administrador)\n"
            "carlos@uni.edu · clave456  (Docente)\nluis@uni.edu · pass789  (Estudiante)")).pack(anchor="w")
        self.email.bind("<Return>", lambda e: self.clave.focus())
        self.clave.bind("<Return>", lambda e: self._entrar())
        self.email.focus()

    def _entrar(self) -> None:
        if not self.app.entrar(self.email.get(), self.clave.get()):
            self.error.config(text="Correo o contraseña incorrectos")
            self.clave.delete(0, "end")


class ItemMenu(tk.Frame):
    def __init__(self, master, icono, texto, comando):
        super().__init__(master, bg=PANEL, cursor="hand2")
        self.activo = False
        self.barra = tk.Frame(self, bg=PANEL, width=3)
        self.barra.pack(side="left", fill="y")
        self.lbl = tk.Label(self, text=f" {icono}   {texto}", bg=PANEL, fg=MUTED, font=F(10), anchor="w", padx=12, pady=11)
        self.lbl.pack(side="left", fill="x", expand=True)
        for w in (self, self.lbl):
            w.bind("<Button-1>", lambda e: comando())
            w.bind("<Enter>", lambda e: self._pintar(True))
            w.bind("<Leave>", lambda e: self._pintar(False))

    def _pintar(self, hover: bool) -> None:
        bg = ACC_DIM if (self.activo or hover) else PANEL
        self.config(bg=bg)
        self.lbl.config(bg=bg, fg=TXT if (self.activo or hover) else MUTED)
        self.barra.config(bg=ACC if self.activo else bg)

    def activar(self, valor: bool) -> None:
        self.activo = valor
        self._pintar(False)


# ======================================================================
# Aplicación
# ======================================================================
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        global FAM
        familias = set(tkfont.families())
        FAM = next((f for f in ("Segoe UI", "SF Pro Display", "Helvetica Neue", "Inter", "Ubuntu", "Cantarell", "DejaVu Sans")
                    if f in familias), "TkDefaultFont")
        self.title("SOHA · Sistema de Horarios Optimizado")
        self.geometry("1240x760")
        self.minsize(1040, 660)
        self.configure(bg=BG)
        aplicar_estilos(self)
        self.sistema = Sistema()
        self.usuario: Usuario | None = None
        self.paginas: dict[str, tk.Widget] = {}
        self.items: dict[str, ItemMenu] = {}
        self.actual: str | None = None
        self._toast: tk.Label | None = None
        self.mostrar_login()

    def _limpiar(self) -> None:
        for w in self.winfo_children():
            w.destroy()
        self.paginas, self.items, self.actual, self._toast = {}, {}, None, None

    # -- sesión ----------------------------------------------------------
    def mostrar_login(self) -> None:
        self._limpiar()
        PantallaLogin(self, self).pack(fill="both", expand=True)

    def entrar(self, email: str, clave: str) -> bool:
        u = self.sistema.autenticar(email, clave)
        if u is None:
            return False
        self.usuario = u
        self.mostrar_principal()
        return True

    def salir(self) -> None:
        if self.usuario:
            self.usuario.cerrar_sesion()
        self.usuario = None
        self.mostrar_login()

    # -- estructura ----------------------------------------------------------
    def mis_horarios(self):
        return self.usuario.consultar_horario(list(self.sistema.gestor.horarios))

    def _filas(self, horarios):
        return [(str(h.bloque), f"{h.paralelo.materia.codigo} · {h.paralelo.codigo}", h.docente.nombre, h.espacio.codigo)
                for h in self.sistema.ordenados(horarios)]

    def mostrar_principal(self) -> None:
        self._limpiar()
        u = self.usuario
        lateral = tk.Frame(self, bg=PANEL, width=240)
        lateral.pack(side="left", fill="y")
        lateral.pack_propagate(False)
        tk.Label(lateral, text="SOHA", bg=PANEL, fg="#fff", font=F(20, True)).pack(anchor="w", padx=22, pady=(24, 0))
        tk.Label(lateral, text="Horarios optimizados", bg=PANEL, fg=MUTED, font=F(9)).pack(anchor="w", padx=22, pady=(0, 22))
        menu = tk.Frame(lateral, bg=PANEL)
        menu.pack(fill="x")
        pie = tk.Frame(lateral, bg=PANEL)
        pie.pack(side="bottom", fill="x", padx=18, pady=18)
        tk.Label(pie, text=u.nombre, bg=PANEL, fg=TXT, font=F(11, True)).pack(anchor="w")
        tk.Label(pie, text=u.rol(), bg=PANEL, fg=CYAN, font=F(9)).pack(anchor="w", pady=(0, 10))
        Boton(pie, "Cerrar sesión", self.salir, "suave", ancho=200, alto=36).pack(anchor="w")

        derecha = tk.Frame(self, bg=BG)
        derecha.pack(side="left", fill="both", expand=True, padx=28, pady=22)
        self.titulo = tk.Label(derecha, text="", bg=BG, fg=TXT, font=F(22, True))
        self.titulo.pack(anchor="w")
        self.subtitulo = tk.Label(derecha, text="", bg=BG, fg=MUTED, font=F(10))
        self.subtitulo.pack(anchor="w", pady=(0, 16))
        self.cuerpo = tk.Frame(derecha, bg=BG)
        self.cuerpo.pack(fill="both", expand=True)

        for clave, icono, titulo, sub, pagina in self._definir_paginas():
            self.paginas[clave] = (pagina, titulo, sub)
            self.items[clave] = ItemMenu(menu, icono, titulo, lambda c=clave: self.navegar(c))
            self.items[clave].pack(fill="x")
        self.navegar(next(iter(self.paginas)))

    def navegar(self, clave: str) -> None:
        if self.actual:
            self.paginas[self.actual][0].pack_forget()
            self.items[self.actual].activar(False)
        pagina, titulo, sub = self.paginas[clave]
        self.actual = clave
        self.titulo.config(text=titulo)
        self.subtitulo.config(text=sub)
        self.items[clave].activar(True)
        pagina.refrescar()
        pagina.pack(fill="both", expand=True)

    def refrescar_todo(self) -> None:
        for pagina, _t, _s in self.paginas.values():
            pagina.refrescar()

    def autogenerar(self) -> None:
        creadas, pendientes = self.sistema.autogenerar()
        if pendientes:
            self.toast(f"{creadas} clases generadas. Sin hueco para: {', '.join(pendientes)}", "err")
        elif creadas:
            self.toast(f"✦ {creadas} clases generadas sin conflictos", "ok")
        else:
            self.toast("No había nada pendiente por generar", "info")
        self.refrescar_todo()

    def toast(self, mensaje: str, tipo: str = "ok") -> None:
        if self._toast is not None:
            self._toast.destroy()
        color = {"ok": OK, "err": ERR, "info": ACC}[tipo]
        simbolo = {"ok": "✔", "err": "⚠", "info": "ℹ"}[tipo]
        t = tk.Label(self, text=f"{simbolo}  {mensaje}", bg=CARD2, fg=TXT, font=F(10), padx=18, pady=12,
                     highlightbackground=color, highlightthickness=2, wraplength=420, justify="left")
        t.place(relx=1, rely=1, x=-28, y=-28, anchor="se")
        t.lift()
        self._toast = t
        self.after(4500 if tipo == "err" else 3000, lambda: self._cerrar_toast(t))

    def _cerrar_toast(self, t: tk.Label) -> None:
        try:
            t.destroy()
        except tk.TclError:
            pass
        if self._toast is t:
            self._toast = None

    # -- páginas por rol -----------------------------------------------------
    def _definir_paginas(self):
        s, a, c = self.sistema, self.sistema.admin, self.cuerpo
        crud = lambda *args, **kw: PaginaCrud(c, self, *args, **kw)
        inicio = ("inicio", "⌂", "Inicio", "Resumen general", PaginaInicio(c, self))
        cols_h = ("Día y hora", "Paralelo", "Docente", "Espacio")

        if isinstance(self.usuario, Administrador):
            return [
                inicio,
                ("horarios", "◷", "Horarios", "Asigna clases validando choques, capacidad y disponibilidad", crud(
                    [("Paralelo", "lista", lambda: s.paralelos), ("Docente", "lista", lambda: s.docentes),
                     ("Espacio", "lista", lambda: a.espacios), ("Día", "lista", lambda: DIAS),
                     ("Inicio (HH:MM)", "texto", None), ("Fin (HH:MM)", "texto", None)],
                    cols_h, lambda: self._filas(None), s.asignar_horario, "Asignar")),
                ("semana", "▦", "Semana", "Vista semanal de todas las clases", PaginaSemana(c, lambda: list(s.gestor.horarios))),
                ("disp", "◐", "Disponibilidad", "Franjas en las que cada docente puede dar clase", crud(
                    [("Docente", "lista", lambda: s.docentes), ("Día", "lista", lambda: DIAS),
                     ("Inicio (HH:MM)", "texto", None), ("Fin (HH:MM)", "texto", None)],
                    ("Docente", "Bloque", "Tipo"),
                    lambda: [(d.nombre, str(b), "Disponible") for d in s.docentes for b in d.disponibilidad]
                            + [(d.nombre, str(b), "Descanso") for d in s.docentes for b in d.descansos],
                    s.registrar_disponibilidad, "Registrar")),
                ("docentes", "☺", "Docentes", "Registro de docentes", crud(
                    [("Nombre", "texto", None), ("Correo", "texto", None), ("Contraseña", "clave", None)],
                    ("ID", "Nombre", "Correo", "Disponibilidad"),
                    lambda: [(d.id_usuario, d.nombre, d.email, f"{len(d.disponibilidad)} bloque(s)") for d in s.docentes],
                    s.crear_docente)),
                ("materias", "✎", "Materias", "Asignaturas y carga horaria", crud(
                    [("Código", "texto", None), ("Nombre", "texto", None), ("Horas semanales", "texto", None)],
                    ("Código", "Nombre", "Horas semanales"),
                    lambda: [(m.codigo, m.nombre, m.horas_semanales) for m in a.materias], s.crear_materia)),
                ("espacios", "▣", "Espacios", "Aulas y laboratorios", crud(
                    [("Código", "texto", None), ("Capacidad", "texto", None), ("Tipo", "lista", lambda: TIPOS_ESPACIO)],
                    ("Código", "Tipo", "Capacidad"),
                    lambda: [(e.codigo, e.tipo, e.capacidad) for e in a.espacios], s.crear_espacio)),
                ("paralelos", "☰", "Paralelos", "Grupos de estudiantes por materia", crud(
                    [("Código", "texto", None), ("Materia", "lista", lambda: a.materias), ("Estudiantes", "texto", None)],
                    ("Paralelo", "Materia", "Estudiantes", "Horas asignadas", "Estado"),
                    lambda: [(p.codigo, p.materia.nombre, p.num_estudiantes,
                              f"{s.gestor.horas_asignadas(p):g} / {p.materia.horas_semanales}",
                              "Completo" if s.gestor.materia_completa(p) else "Pendiente") for p in s.paralelos],
                    s.crear_paralelo)),
                ("estudiantes", "✦", "Estudiantes", "Registro de estudiantes", crud(
                    [("Nombre", "texto", None), ("Correo", "texto", None), ("Contraseña", "clave", None),
                     ("Carrera", "texto", None), ("Paralelo", "lista", lambda: s.paralelos)],
                    ("ID", "Nombre", "Correo", "Carrera", "Paralelos"),
                    lambda: [(e.id_usuario, e.nombre, e.email, e.carrera,
                              ", ".join(f"{p.materia.codigo}-{p.codigo}" for p in e.paralelos) or "—") for e in s.estudiantes],
                    s.crear_estudiante)),
            ]
        mis = lambda: self._filas(self.mis_horarios())
        paginas = [inicio,
                   ("mi", "◷", "Mi horario", "Tus clases ordenadas por día", crud([], cols_h, mis)),
                   ("semana", "▦", "Semana", "Tu semana de un vistazo", PaginaSemana(c, self.mis_horarios))]
        if isinstance(self.usuario, Docente):
            u = self.usuario
            paginas.append(("disp", "◐", "Mi disponibilidad", "Franjas en las que puedes dar clase", crud(
                [("Día", "lista", lambda: DIAS), ("Inicio (HH:MM)", "texto", None), ("Fin (HH:MM)", "texto", None)],
                ("Bloque", "Tipo"),
                lambda: [(str(b), "Disponible") for b in u.disponibilidad] + [(str(b), "Descanso") for b in u.descansos],
                lambda dia, ini, fin: s.registrar_disponibilidad(u, dia, ini, fin), "Registrar")))
        return paginas


if __name__ == "__main__":
    App().mainloop()
