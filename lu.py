"""
    Paquetage pour factorisation LU
    Contient : Trois fonctions (lutri, descente, remontee)
"""

import matplotlib.pyplot as plt
import numpy as np
from pprint import pprint

plt.style.use("ggplot")


def lutri(a, b, c):
    """
        Effectue une factorisation LU d'une matrice A tridiagonale
        Entrée : a un vecteur réel de dimension n (diagonale de A)
                 b un vecteur réel de dimension n - 1 (sous-diagonale de A)
                 c un vecteur réel de dimension n - 1 (sur-diagonale de A)
        Sortie : [l, v] : [sous-diagonale de L vecteur réel de dimension n - 1, 
                           diagonale de U vecteur réel de dimension n]
    """
    n = len(a)
    l, v = [], [a[0]]
    for i in range(1, n):
        l.append(b[i - 1] / v[i - 1])
        v.append(a[i] - l[i - 1] * c[i - 1])
    return [l, v]


def descente(l, z):
    """
        Effectue l'étape de descente lors de la factorisation LU d'une matrice A tridiagonale
        On cherche à résoudre Ly = z
        Entrée : l un vecteur réel de dimension n - 1
                 z un vecteur réel de dimension n
        Sortie : y un vecteur réel de dimension n
    """
    n = len(z)
    y = [z[0]]
    for i in range(1, n):
        y.append(z[i] - l[i - 1] * y[i - 1])
    return y


def remontee(v, c, y):
    """
        Effectue l'étape de remontée lors de la factorisation LU d'une matrice A tridiagonale
        On cherche à résoudre Ux = y
        Entrée : v un vecteur réel de dimension n
                 c un vecteur réel de dimension n - 1
                 y un vecteur réel de dimension n
        Sortie : x un vecteur réel de dimension n
    """
    n = len(y)
    x = [y[n - 1] / v[n - 1]]
    for i in range(n - 2, -1, -1):
        x.insert(0, (y[i] - c[i] * x[0]) / v[i])
    return x


def solve_debye_huckel(n, mu):
    """
        Résolution de l'équation de Debye-Huckel.

        Sortie : x vecteur réel de dimension n, u vecteur solution de dimension n
    """
    h = 10 / n
    # Initialisation
    x = [1] * n
    b, a, c, z = [0] * (n - 1), [-(2 + h ** 2)] * n, [0] * (n - 1), [0] * n
    c[0], z[0] = 2, mu * h * (h - 2)
    # Attribution
    for i in range(1, n - 1):
        xi = 1 + i * h
        b[i - 1] = 1 - h / (2 * xi)
        c[i] = 1 + h / (2 * xi)
        x[i] = xi
    # Dernier élément
    xn = 1 + (n - 1) * h
    b[n - 2] = 1 - h / (2 * xn)
    x[n - 1] = xn

    l, v = lutri(a, b, c)
    y = descente(l, z)
    u = remontee(v, c, y)

    return x, np.array(u), [b, a, c]


def plot_debye_huckel(x, u, mu):
    plt.plot(x, u, label=f"Debye-Huckel mu = {mu}")
    plt.xlabel("Points de discrétisations $x_i$")
    plt.ylabel("Solutions ponctuelles $u_i$")
    plt.title("Schéma aux différences finies de l'équation de Debye-Huckel")
    plt.legend()


def plot_echantillon_q5(mu):
    """
        Affichage des couples (xi, ui)
    """
    x, u, _ = solve_debye_huckel(n=1000, mu=mu)
    plot_debye_huckel(x, u, mu)


def plot_echantillon_q6(mu):
    """
        Etude de l'influence du pas de discrétisation
    """
    u0, h = [], []
    for n in [10, 15, 30, 70, 100, 1000, 10000]:
        _, u, _ = solve_debye_huckel(n, mu=mu)
        # plot_debye_huckel(x, u, mu)
        # plt.show()
        u0.append(u[0])
        h.append(10 / n)
    # print(h, u0)
    plt.plot(h, u0, "o", label="$u_0$")
    plt.xlabel("Pas de discrétisations $h$")
    plt.ylabel("Solutions ponctuelles $u_0$")
    plt.title("Influence du pas de la discrétisation")
    plt.legend()


def solve_poisson_boltzmann(u, n, mu):
    """
        Résolution de l'équation de Poisson-Boltzmann avec la méthode des approximations successives

        On calcule u(k+1) à partir de u(k).

        Sortie : x vecteur réel de dimension n, u vecteur solution de dimension n
    """
    h = 10 / n
    g = lambda x: np.sinh(x) - x
    # Initialisation
    x = [1] * n
    b, a, c, z = [0] * (n - 1), [-(2 + h ** 2)] * n, [0] * (n - 1), [0] * n
    c[0], z[0] = 2, (h ** 2) * g(u[0]) + mu * h * (h - 2)
    # Attribution
    for i in range(1, n - 1):
        xi = 1 + i * h
        b[i - 1] = 1 - h / (2 * xi)
        c[i] = 1 + h / (2 * xi)
        z[i] = (h ** 2) * g(u[i])
        x[i] = xi
    # Dernier élément
    xn = 1 + (n - 1) * h
    b[n - 2] = 1 - h / (2 * xn)
    z[n - 1] = (h ** 2) * g(u[n - 1])
    x[n - 1] = xn

    l, v = lutri(a, b, c)
    y = descente(l, z)
    u_suivant = remontee(v, c, y)

    return x, np.array(u_suivant), np.array(z)


def tridiag(diags, k1=-1, k2=0, k3=1):
    """Retourne une matrice tridiagonale."""
    b, a, c = diags
    return np.diag(b, k1) + np.diag(a, k2) + np.diag(c, k3)


def calcul_uk0(mu=1):
    # Paramètres de la simualtion
    mu1, mu2 = 10e-12, 10e-9
    n = 1000

    # Initialisation de u et calcul de A
    _, u, diags = solve_debye_huckel(n, mu)
    A = tridiag(diags)
    # Initialisation des écarts
    ecart1 = A.dot(u)
    ecart2 = u

    k = 0
    while not (
        k > 200
        or (
            np.linalg.norm(ecart1, np.inf) < mu1
            and np.linalg.norm(ecart2, np.inf) < mu2
        )
    ):
        x, u_suivant, z = solve_poisson_boltzmann(u, n, mu)
        ecart1 = A.dot(u_suivant) - z
        ecart2 = u_suivant - u
        u = u_suivant
        k += 1

    return x, u, k


def plot_echantillon_q8(mu):
    x, u, k = calcul_uk0(mu=mu)
    print(f"k vaut {k} pour mu = {mu}")
    plt.plot(x, u, label=f"Poisson-Boltzmann mu = {mu}")
    plt.xlabel("Points de discrétisations $x_i$")
    plt.ylabel("Solutions ponctuelles $u_i$")
    plt.title("Schéma aux différences finies de l'équation de Poisson-Boltzmann")
    plt.legend()


def plot_variations_mu():
    """
        Au dela de mu = 6.4 :
            RuntimeWarning: overflow encountered in sinh
            RuntimeWarning: invalid value encountered in double_scalars
            g = lambda x: np.sinh(x) - x
    """

    fig = plt.figure()
    for mu in np.linspace(0.1, 6.4, 10):
        mu = round(mu, 3)
        plot_echantillon_q5(mu)
    fig.savefig("debye_mu_variations.png")

    fig = plt.figure()
    for mu in np.linspace(0.1, 6.4, 10):
        mu = round(mu, 3)
        plot_echantillon_q8(mu)
    fig.savefig("poisson_mu_variations.png")
    # pour mu = 5.7 et mu = 6.4 on retombe ie. diverge

    for mu in np.linspace(0.1, 6.4, 10):
        mu = round(mu, 3)
        fig = plt.figure()
        plot_echantillon_q5(mu)
        plot_echantillon_q8(mu)
        fig.savefig(f"superposed_mu{mu}.png")


def find_convergence_mu():
    debut = 0
    fin = 7
    ecart = fin - debut
    while ecart > 10e-6:
        m = (debut + fin) / 2
        _, _ , k = calcul_uk0(mu=m)
        # print(m, k)
        if k > 200:
            fin = m
        else:
            debut = m
        ecart = fin - debut
    return m


def solve_poisson_boltzmann_newton(u, n, mu):
    """
        Résolution de l'équation de Poisson-Boltzmann avec la méthode de Newton

        On calcule u(k+1) à partir de u(k).

        Sortie : x vecteur réel de dimension n, u vecteur solution de dimension n, F vecteur de la fonction
    """
    h = 10 / n
    # Initialisation
    x = [1] * n
    b, a, c, F = [0] * (n - 1), -2 - (h ** 2) * np.cosh(u), [0] * (n - 1), [0] * n
    F[0] = - 2 * u[0] - (h ** 2) * np.sinh(u[0]) + 2 * u[1] + mu * h * (2 - h)
    # Attribution
    for i in range(1, n - 1):
        xi = 1 + i * h
        bi = 1 - h / (2 * xi)
        ci = 1 + h / (2 * xi)
        b[i - 1] = bi
        c[i] = ci
        F[i] = bi * u[i - 1] - 2 * u[i] - (h ** 2) * np.sinh(u[i]) + ci * u[i + 1]
        x[i] = xi
    # Dernier élément
    xn = 1 + (n - 1) * h
    bn = 1 - h / (2 * xn)
    b[n - 2] = bn
    F[n - 1] = bn * u[n - 2] - 2 * u[n - 1] - (h ** 2) * np.sinh(u[n - 1])
    x[n - 1] = xn

    print(F)
    F = np.array(F)

    inv_Jk = np.linalg.inv(tridiag([b, a, c]))
    u_suivant = u - inv_Jk.dot(F)

    return x, u_suivant, F


def calcul_uk0_newton(mu=1):
    # Paramètres de la simualtion
    mu1, mu2 = 10e-12, 10e-9
    n = 1000

    # Initialisation de u et calcul de A
    _, u, diags = solve_debye_huckel(n, mu)
    A = tridiag(diags)
    # Initialisation des écarts
    ecart1 = A.dot(u)
    ecart2 = u

    k = 0
    while not (
        k > 50
        or (
            np.linalg.norm(ecart1, np.inf) < mu1
            and np.linalg.norm(ecart2, np.inf) < mu2
        )
    ):
        x, u_suivant, F = solve_poisson_boltzmann_newton(u, n, mu)
        ecart1 = F
        ecart2 = u_suivant - u
        print(k, np.linalg.norm(ecart1, np.inf), np.linalg.norm(ecart2, np.inf))
        u = u_suivant
        k += 1

    return x, u, k


def main():
    # b, a, c = [2, 6], [1, 10, 10], [4, 5]
    # l, v = lutri(a, b, c)
    # print(l, v)
    # y = descente(l, [3, 3, 3])
    # print(y)
    # x = remontee(v, c, [3, 3, 3])
    # print(x)

    # plot_echantillon_q5(1)
    # plt.show()
    # plot_echantillon_q6(1)
    # plt.show()

    # plot_echantillon_q5(1)
    # plot_echantillon_q8(1)
    # plt.show()
    # plot_echantillon_q5(4)
    # plot_echantillon_q8(4)
    # plt.show()

    # plot_variations_mu()

    # mu = find_convergence_mu()
    # print(mu) # 4.828635215759277

    print(calcul_uk0_newton(mu=1))

    # b, a, c = [-4, -3, -2, 2], [-2, 5, -1, 4, -2], [1, 2, -1, 1]
    # l, v = lutri(a, b, c)
    # assert(l == [2.0, -1.0, -2.0, 1.0] and v == [-2, 3.0, 1.0, 2.0, -3.0])
    # print(l, v)


main()
