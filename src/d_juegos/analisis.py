def mejores_respuestas_a(ua, j):
    col = [fila[j] for fila in ua]
    m = max(col)
    return [i for i, v in enumerate(col) if v == m]


def mejores_respuestas_b(ub, i):
    m = max(ub[i])
    return [j for j, v in enumerate(ub[i]) if v == m]


def dominantes_a(ua):
    n, m = len(ua), len(ua[0])
    estrictas, debiles = [], []
    for i in range(n):
        otras = [k for k in range(n) if k != i]
        if all(ua[i][j] > ua[k][j] for k in otras for j in range(m)):
            estrictas.append(i)
        if all(ua[i][j] >= ua[k][j] for k in otras for j in range(m)) and \
           any(ua[i][j] > ua[k][j] for k in otras for j in range(m)):
            debiles.append(i)
    return estrictas, debiles


def dominantes_b(ub):
    n, m = len(ub), len(ub[0])
    estrictas, debiles = [], []
    for j in range(m):
        otras = [k for k in range(m) if k != j]
        if all(ub[i][j] > ub[i][k] for k in otras for i in range(n)):
            estrictas.append(j)
        if all(ub[i][j] >= ub[i][k] for k in otras for i in range(n)) and \
           any(ub[i][j] > ub[i][k] for k in otras for i in range(n)):
            debiles.append(j)
    return estrictas, debiles


def equilibrios_nash_puros(ua, ub):
    n, m = len(ua), len(ua[0])
    return [(i, j) for i in range(n) for j in range(m)
            if i in mejores_respuestas_a(ua, j) and j in mejores_respuestas_b(ub, i)]


def nivel_seguridad_a(ua):
    peor = [min(fila) for fila in ua]
    v = max(peor)
    return peor.index(v), v