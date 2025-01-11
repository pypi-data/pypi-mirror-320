def datepaques(an):
    """Calcule la date de Pâques d'une année donnée an (=nombre entier)"""
    a = an // 100
    b = an % 100
    c = (3 * (a + 25)) // 4
    d = (3 * (a + 25)) % 4
    e = (8 * (a + 11)) // 25
    f = (5 * a + b) % 19
    g = (19 * f + c - e) % 30
    h = (f + 11 * g) // 319
    j = (60 * (5 - d) + b) // 4
    k = (60 * (5 - d) + b) % 4
    m = (2 * j - k - g + h) % 7
    n = (g - h + m + 114) // 31
    p = (g - h + m + 114) % 31
    jour = p + 1
    mois = n
    return [jour, mois, an]


def jourmoins(d, n=-1):
    """Donne la date du nième jour précédent d=[j, m, a] (n<=0)"""
    j, m, a = d
    fm = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    if (a % 4 == 0 and a % 100 != 0) or a % 400 == 0:  # bissextile?
        fm[2] = 29
    for i in range(0, abs(n)):
        j -= 1
        if j < 1:
            m -= 1
            if m < 1:
                m = 12
                a -= 1
            j = fm[m]
    return [j, m, a]


def numjoursem(d):
    """Donne le numéro du jour de la semaine d'une date d=[j,m,a]
    lundi=1, mardi=2, ..., dimanche=7
    Algorithme de Maurice Kraitchik (1882–1957)"""
    j, m, a = d
    if m < 3:
        m += 12
        a -= 1
    n = (j + 2 * m + (3 * (m + 1)) // 5 + a + a // 4 - a // 100 + a // 400 + 2) % 7
    return [6, 7, 1, 2, 3, 4, 5][n]


def joursem(d):
    """Donne le jour de semaine en texte à partir de son numéro
    lundi=1, mardi=2, ..., dimanche=7"""
    return [
        "",
        "lundi",
        "mardi",
        "mercredi",
        "jeudi",
        "vendredi",
        "samedi",
        "dimanche",
    ][numjoursem(d)]


def jourplus(d, n=1):
    """Donne la date du nième jour suivant d=[j, m, a] (n>=0)"""
    j, m, a = d
    fm = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    if (a % 4 == 0 and a % 100 != 0) or a % 400 == 0:  # bissextile?
        fm[2] = 29
    for _ in range(0, n):
        j += 1
        if j > fm[m]:
            j = 1
            m += 1
            if m > 12:
                m = 1
                a += 1
    return [j, m, a]


def datechaine(d, sep="/"):
    """Transforme une date liste=[j,m,a] en une date chaîne 'jj/mm/aaaa'"""
    return ("%02d" + sep + "%02d" + sep + "%0004d") % (d[0], d[1], d[2])
