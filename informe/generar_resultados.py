"""Genera las tablas (tablas.tex) y las figuras (imagenes/*.pdf) del informe a partir de logs/."""
import glob
import os
import re
import statistics as st
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import extracion_datos  # noqa: E402

SALIDA = os.path.dirname(os.path.abspath(__file__))
IMAGENES = os.path.join(SALIDA, "imagenes")
DATOS = os.path.join(RAIZ, "Material de práctica 1 y 2-20260910")

INSTANCIAS = ["ch130", "pr144", "a280", "u1060", "d18512"]
OPTIMOS = {"ch130": 6110, "pr144": 58537, "a280": 2579, "u1060": 224094, "d18512": 645238}
ALGORITMOS = ["gre", "grea", "b_local", "tabu"]
NOMBRES = {"gre": "Greedy", "grea": "Greedy aleatorio", "b_local": "Búsqueda local", "tabu": "Búsqueda tabú"}
COLORES = {"gre": "#9e9e9e", "grea": "#616161", "b_local": "#e08a2c", "tabu": "#2c6fbb"}


def leer_logs():
    """Devuelve {(instancia, algoritmo): [ {semilla, ejecucion, coste, tiempo, fichero}, ... ]}."""
    datos = {}
    for ruta in glob.glob(os.path.join(RAIZ, "logs", "*", "*.log")):
        alg = os.path.basename(os.path.dirname(ruta))
        texto = open(ruta, encoding="utf-8").read()
        fichero = re.search(r"SUMMARY\] Fichero: (\w+)", texto)
        if alg not in ALGORITMOS or fichero is None:
            continue
        datos.setdefault((fichero.group(1), alg), []).append({
            "semilla": int(re.search(r"SUMMARY\] Semilla: (\d+)", texto).group(1)),
            "ejecucion": int(re.search(r"SUMMARY\] ejecucion: (\d+)", texto).group(1)),
            "coste": float(re.findall(r"SUMMARY\] Resultado: ([\d.]+)", texto)[-1]),
            "tiempo": float(re.findall(r"Tiempo de ejecución \(s\): ([\d.]+)", texto)[-1]),
            "ruta": ruta,
        })
    for v in datos.values():
        v.sort(key=lambda r: r["ejecucion"])
    return datos


def desv(coste, inst):
    return 100 * (coste - OPTIMOS[inst]) / OPTIMOS[inst]


def num(x, dec=2):
    """Número con formato español para LaTeX (punto de miles con {.}, coma decimal con {,})."""
    s = f"{x:,.{dec}f}"
    return s.replace(",", "X").replace(".", "{,}").replace("X", "{.}")


def tabla_algoritmo(datos, alg):
    filas = []
    n_ejec = max(len(datos.get((i, alg), [])) for i in INSTANCIAS)
    cab = " & ".join(f"\\multicolumn{{2}}{{c}}{{{i}}}" for i in INSTANCIAS)
    filas.append("\\begin{table}[H]\n\\centering\\scriptsize\\setlength{\\tabcolsep}{3pt}")
    filas.append("\\resizebox{\\textwidth}{!}{%\n\\begin{tabular}{l" + "rr" * len(INSTANCIAS) + "}\n\\toprule")
    filas.append(f" & {cab} \\\\")
    filas.append(" & " + " & ".join(["Coste & T (s)"] * len(INSTANCIAS)) + " \\\\\n\\midrule")
    for k in range(n_ejec):
        celdas = []
        for i in INSTANCIAS:
            v = datos.get((i, alg), [])
            celdas += [num(v[k]["coste"]), num(v[k]["tiempo"], 3)] if k < len(v) else ["--", "--"]
        filas.append(f"Ejecución {k + 1} & " + " & ".join(celdas) + " \\\\")
    filas.append("\\midrule")
    for etiqueta, f in (("Media", st.mean), ("Desv. típica", st.stdev)):
        celdas = []
        for i in INSTANCIAS:
            v = datos.get((i, alg), [])
            if len(v) >= (2 if f is st.stdev else 1):
                celdas += [num(f([r["coste"] for r in v])), num(f([r["tiempo"] for r in v]), 3)]
            else:
                celdas += ["--", "--"]
        filas.append(f"{etiqueta} & " + " & ".join(celdas) + " \\\\")
    filas.append("\\bottomrule\n\\end{tabular}}")
    semillas = "; ".join(
        f"{i}: " + ", ".join(str(r["semilla"]) for r in datos.get((i, alg), [])) for i in INSTANCIAS
        if datos.get((i, alg))
    )
    filas.append(f"\\caption[Resultados de {NOMBRES[alg]}]{{Resultados de {NOMBRES[alg]} (semillas por instancia, en orden de ejecución: {semillas}).}}")
    filas.append(f"\\label{{tab:{alg}-res}}\n\\end{{table}}\n")
    return "\n".join(filas)


def tabla_resumen(datos):
    filas = ["\\begin{table}[H]\n\\centering\\scriptsize\\setlength{\\tabcolsep}{3pt}",
             "\\resizebox{\\textwidth}{!}{%\n\\begin{tabular}{l" + "rr" * (len(INSTANCIAS) + 1) + "}\n\\toprule",
             " & " + " & ".join(f"\\multicolumn{{2}}{{c}}{{{i}}}" for i in INSTANCIAS)
             + " & \\multicolumn{2}{c}{Media} \\\\",
             " & " + " & ".join(["Desv (\\%) & T (s)"] * (len(INSTANCIAS) + 1)) + " \\\\\n\\midrule"]
    for alg in ALGORITMOS:
        celdas, ds, ts = [], [], []
        for i in INSTANCIAS:
            v = datos.get((i, alg), [])
            if v:
                d = st.mean(desv(r["coste"], i) for r in v)
                t = st.mean(r["tiempo"] for r in v)
                ds.append(d)
                ts.append(t)
                celdas += [num(d), num(t, 3)]
            else:
                celdas += ["--", "--"]
        celdas += [num(st.mean(ds)), num(st.mean(ts), 3)]
        filas.append(f"{NOMBRES[alg]} & " + " & ".join(celdas) + " \\\\")
    filas += ["\\bottomrule\n\\end{tabular}}",
              "\\caption{Desviación media respecto al óptimo y tiempo medio por algoritmo e instancia.}",
              "\\label{tab:resumen}\n\\end{table}\n"]
    return "\n".join(filas)


def tabla_tabu(datos):
    filas = ["\\begin{table}[H]\n\\centering\\footnotesize",
             "\\begin{tabular}{lrrrrr}\n\\toprule",
             "Instancia & Ejec. & Empeoramientos & Reinicios (I/D) & Última mejora global & Coste final \\\\\n\\midrule"]
    for i in INSTANCIAS:
        for r in datos.get((i, "tabu"), []):
            texto = open(r["ruta"], encoding="utf-8").read()
            emp = texto.count("EMPEORAMIENTO")
            intens = len(re.findall(r"nueva solución por intensificación", texto))
            divers = len(re.findall(r"nueva solución por diversificación", texto))
            it, ultima, prev = 0, 0, None
            for linea in texto.splitlines():
                m = re.search(r"\[TABU\] Iteración (\d+):", linea)
                if m:
                    it = int(m.group(1))
                m = re.search(r"mejor global: ([\d.]+);", linea)
                if m and m.group(1) != prev:
                    prev, ultima = m.group(1), it
            filas.append(f"{i} & {r['ejecucion']} & {num(emp, 0)} & {intens + divers} ({intens}/{divers}) "
                         f"& {num(ultima, 0)} & {num(r['coste'])} \\\\")
    filas += ["\\bottomrule\n\\end{tabular}",
              "\\caption{Comportamiento interno de la búsqueda tabú (10.000 iteraciones por ejecución).}",
              "\\label{tab:tabu}\n\\end{table}\n"]
    return "\n".join(filas)


def tabla_bl(datos):
    filas = ["\\begin{table}[H]\n\\centering\\small",
             "\\begin{tabular}{lrrl}\n\\toprule",
             "Instancia & Ejec. & Movimientos & Motivo de parada \\\\\n\\midrule"]
    for i in INSTANCIAS:
        for r in datos.get((i, "b_local"), []):
            texto = open(r["ruta"], encoding="utf-8").read()
            mov = int(re.search(r"SUMMARY\] Movimientos realizados: (\d+)", texto).group(1))
            motivo = re.search(r"SUMMARY\] Motivo de finalización: (.+)", texto).group(1)
            filas.append(f"{i} & {r['ejecucion']} & {num(mov, 0)} & {motivo} \\\\")
    filas += ["\\bottomrule\n\\end{tabular}",
              "\\caption{Movimientos realizados por la búsqueda local y motivo de parada.}",
              "\\label{tab:bl-parada}\n\\end{table}\n"]
    return "\n".join(filas)


def convergencia(ruta, tabu):
    """Lista de (iteración, coste actual, mejor global) de un log."""
    puntos, it, mejor = [], 0, None
    for linea in open(ruta, encoding="utf-8"):
        m = re.search(r"Iteración (\d+): intercambio", linea)
        if m:
            it = int(m.group(1))
            continue
        m = re.search(r"Coste nuevo: ([\d.]+)", linea)
        if m:
            coste = float(m.group(1))
            mejor = coste if mejor is None else min(mejor, coste)
            puntos.append((it, coste, mejor))
        if tabu:
            m = re.search(r"\[RESTART\]   Coste: ([\d.]+)", linea)
            if m:
                puntos.append((it, float(m.group(1)), mejor))
    return puntos


def mejor_ejecucion(datos, inst, alg):
    return min(datos[(inst, alg)], key=lambda r: r["coste"])


def figura_convergencia(datos):
    insts = [i for i in ("ch130", "a280", "u1060") if (i, "tabu") in datos and (i, "b_local") in datos]
    fig, ejes = plt.subplots(len(insts), 1, figsize=(8, 3.1 * len(insts)))
    for ax, inst in zip(ejes, insts):
        rt = mejor_ejecucion(datos, inst, "tabu")
        rb = mejor_ejecucion(datos, inst, "b_local")
        pt = convergencia(rt["ruta"], True)
        pb = convergencia(rb["ruta"], False)
        ax.plot([p[0] for p in pt], [p[1] for p in pt], color=COLORES["tabu"], lw=0.5, alpha=0.45,
                label="Tabú: solución actual")
        ax.plot([p[0] for p in pt], [p[2] for p in pt], color=COLORES["tabu"], lw=1.6, label="Tabú: mejor global")
        ax.plot([p[0] for p in pb], [p[1] for p in pb], color=COLORES["b_local"], lw=1.6, label="Búsqueda local")
        ax.axhline(OPTIMOS[inst], color="black", ls="--", lw=0.8, label="Óptimo")
        ax.set_yscale("log")
        ax.set_title(f"{inst} (tabú semilla {rt['semilla']}, BL semilla {rb['semilla']})", fontsize=10)
        ax.set_xlabel("Iteración")
        ax.set_ylabel("Coste")
        ax.grid(alpha=0.3)
    ejes[0].legend(fontsize=8, loc="upper right")
    fig.tight_layout()
    fig.savefig(os.path.join(IMAGENES, "convergencia.pdf"))
    plt.close(fig)


def figura_boxplot(datos):
    insts = [i for i in INSTANCIAS if any((i, a) in datos for a in ALGORITMOS)]
    fig, ejes = plt.subplots(1, len(insts), figsize=(2.6 * len(insts), 3.6))
    algs = ["grea", "b_local", "tabu"]
    for ax, inst in zip(ejes, insts):
        valores = [[desv(r["coste"], inst) for r in datos.get((inst, a), [])] for a in algs]
        presentes = [(a, v) for a, v in zip(algs, valores) if v]
        caja = ax.boxplot([v for _, v in presentes], patch_artist=True, widths=0.6)
        for parche, (a, _) in zip(caja["boxes"], presentes):
            parche.set_facecolor(COLORES[a])
            parche.set_alpha(0.75)
        for k, (_, v) in enumerate(presentes, start=1):
            ax.scatter([k] * len(v), v, s=10, color="black", zorder=3)
        ax.set_xticks(range(1, len(presentes) + 1))
        ax.set_xticklabels([{"grea": "GA", "b_local": "BL", "tabu": "Tabú"}[a] for a, _ in presentes])
        ax.set_yscale("log")
        ax.set_title(inst, fontsize=10)
        ax.grid(alpha=0.3, axis="y")
    ejes[0].set_ylabel("Desviación respecto al óptimo (%)")
    fig.tight_layout()
    fig.savefig(os.path.join(IMAGENES, "boxplot.pdf"))
    plt.close(fig)


def figura_desviacion(datos):
    fig, ax = plt.subplots(figsize=(8, 3.6))
    ancho = 0.2
    for k, alg in enumerate(ALGORITMOS):
        xs, ys = [], []
        for j, inst in enumerate(INSTANCIAS):
            v = datos.get((inst, alg), [])
            if v:
                xs.append(j + (k - 1.5) * ancho)
                ys.append(st.mean(desv(r["coste"], inst) for r in v))
        ax.bar(xs, ys, ancho, color=COLORES[alg], label=NOMBRES[alg])
    ax.set_xticks(range(len(INSTANCIAS)))
    ax.set_xticklabels([f"{i}\n(n={n})" for i, n in zip(INSTANCIAS, [130, 144, 280, 1060, 18512])])
    ax.set_yscale("log")
    ax.set_ylabel("Desviación media (%)")
    ax.grid(alpha=0.3, axis="y")
    ax.legend(fontsize=8, ncol=4, loc="upper left")
    fig.tight_layout()
    fig.savefig(os.path.join(IMAGENES, "desviacion.pdf"))
    plt.close(fig)


def figura_tiempos(datos):
    tam = {"ch130": 130, "pr144": 144, "a280": 280, "u1060": 1060, "d18512": 18512}
    fig, ax = plt.subplots(figsize=(7, 3.6))
    for alg in ALGORITMOS:
        pts = [(tam[i], st.mean(r["tiempo"] for r in datos[(i, alg)])) for i in INSTANCIAS if (i, alg) in datos]
        pts.sort()
        ax.plot([p[0] for p in pts], [p[1] for p in pts], "o-", color=COLORES[alg], label=NOMBRES[alg])
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Número de ciudades (n)")
    ax.set_ylabel("Tiempo medio (s)")
    ax.grid(alpha=0.3, which="both")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(os.path.join(IMAGENES, "tiempos.pdf"))
    plt.close(fig)


def leer_solucion(ruta, tabu):
    lineas = open(ruta, encoding="utf-8").read().splitlines()
    marca = "Mejor solución global:" if tabu else "Solución final:"
    for k, linea in enumerate(lineas):
        if marca in linea:
            return [int(x) for x in re.findall(r"\d+", lineas[k + 1].split("]", 2)[-1])]
    return None


def figura_recorridos(datos, inst="ch130"):
    _, coords, _, _, _ = extracion_datos.extraccion_Archivo(os.path.join(DATOS, f"{inst}.tsp"))
    # El log del greedy aleatorio no guarda la solución, así que solo se dibujan BL y tabú
    fig, ejes = plt.subplots(1, 2, figsize=(9, 4.2))
    for ax, alg in zip(ejes, ("b_local", "tabu")):
        r = mejor_ejecucion(datos, inst, alg)
        sol = leer_solucion(r["ruta"], alg == "tabu")
        ruta = sol + sol[:1]
        ax.plot(coords[ruta, 0], coords[ruta, 1], "-", color=COLORES[alg], lw=0.9)
        ax.scatter(coords[:, 0], coords[:, 1], s=6, color="black", zorder=3)
        ax.set_title(f"{NOMBRES[alg]}: coste {r['coste']:.0f} ({desv(r['coste'], inst):.1f} %)", fontsize=10)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_aspect("equal")
    fig.tight_layout()
    fig.savefig(os.path.join(IMAGENES, f"recorridos_{inst}.pdf"))
    plt.close(fig)


def main():
    os.makedirs(IMAGENES, exist_ok=True)
    datos = leer_logs()
    # Una tabla por fichero en tablas/, que contenido.tex incluye con \input
    tablas = {f"tabla_{alg}": tabla_algoritmo(datos, alg) for alg in ALGORITMOS}
    tablas.update(tabla_resumen=tabla_resumen(datos), tabla_tabu_interna=tabla_tabu(datos),
                  tabla_bl_parada=tabla_bl(datos))
    os.makedirs(os.path.join(SALIDA, "tablas"), exist_ok=True)
    for nombre, contenido in tablas.items():
        with open(os.path.join(SALIDA, "tablas", f"{nombre}.tex"), "w", encoding="utf-8") as f:
            f.write("% Generado por generar_resultados.py a partir de logs/: no editar a mano\n")
            f.write(contenido)
    figura_convergencia(datos)
    figura_boxplot(datos)
    figura_desviacion(datos)
    figura_tiempos(datos)
    figura_recorridos(datos)
    for (inst, alg), v in sorted(datos.items()):
        print(inst, alg, len(v), round(st.mean(r["coste"] for r in v), 1))


if __name__ == "__main__":
    main()
