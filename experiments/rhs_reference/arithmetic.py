"""Independent coefficient-conditioned stoichiometry and exact rational error bounds.

No rate, EOS, reference or project routines are imported/called here.
"""

import math
from collections import Counter, defaultdict
from fractions import Fraction as Q

U = Q(1, 2**53)
NORMAL = Q(1, 2**1022)
MAXIMUM = Q.from_float(float.fromhex("0x1.fffffffffffffp+1023"))


def require(test, reason):
    if not test:
        raise ValueError(reason)


def upper_float(value):
    result = float(value)
    return math.nextafter(result, math.inf) if Q(result) < value else result


def gamma(n):
    require(n * U < 1, "Invalid operation count")
    return n * U / (1 - n * U)


def product_bound(operands):
    """Any binary association, nearest rounding, with optional DAZ/FTZ.

    Each flush loses < NORMAL, amplified by remaining factors. 4*n counts
    original-input flushes plus operand/result flushes at all n-1 products.
    Fused operations require no more rounding/flush events than this envelope.
    """
    exact, amplification = Q(1), Q(1)
    for value in operands:
        value = Q(value)
        exact *= value
        amplification *= max(Q(1), abs(value))
    n = len(operands)
    error = gamma(n - 1) * abs(exact)
    error += 4 * n * NORMAL * amplification * (1 + U) ** (n - 1)
    return exact, error


def mapping_terms(groups, masses):
    """Validate multiplicities independently of the producer's extended maps.

    csect has no counting factor. a contains signed multiplicity / native symmetry.
    Native source convention is factorial(largest multiplicity), not the product
    of all multiplicity factorials; preserve it without claiming physical truth.
    Separate destruction/creation entries for the same species are allowed.
    """
    masses = list(map(Q, masses))
    ny = len(masses)
    terms = [[] for _ in masses]
    reaction_base = 0
    for group in groups:
        order = group["order"]
        observed = defaultdict(int)
        expected = {}
        for k, participants in enumerate(group["participants"]):
            reactants, products = participants[:order], participants[order:]
            require(all(1 <= x <= ny for x in reactants), "Invalid reactant")
            require(all(0 <= x <= ny for x in products), "Invalid product")
            symmetry = math.factorial(max(Counter(reactants).values()))
            net = Counter(x for x in products if x)
            net.subtract(reactants)
            require(
                sum(masses[i - 1] * v for i, v in net.items()) == 0,
                "Reaction baryon defect",
            )
            expected[k] = (symmetry, net)
        for target, mu, factor in group["extended"]:
            require(
                1 <= target <= ny and 0 <= mu < len(expected), "Invalid extended index"
            )
            require(math.isfinite(factor), "Nonfinite multiplicity factor")
            symmetry, _ = expected[mu]
            numerators = [k for k in range(-6, 7) if float(Q(k, symmetry)) == factor]
            require(len(numerators) == 1, "Unrecognized combinatorial factor")
            k = numerators[0]
            observed[target, mu] += k
            terms[target - 1].append(
                (
                    reaction_base + mu,
                    group["participants"][mu][:order],
                    factor,
                    Q(k, symmetry),
                )
            )
        for mu, (symmetry, net) in expected.items():
            for target in range(1, ny + 1):
                require(
                    observed[target, mu] == net[target],
                    "Stoichiometry/mapping disagreement",
                )
        reaction_base += len(expected)
    return terms


def assemble_check(y, coefficients, fresh, terms, masses):
    """Return exact algebraic residuals and operation/flush-derived bounds.

    No application tolerance is selected. Overflow envelope violations stop.
    Charge is reported, never constrained to zero for weak reactions.
    """
    require(all(math.isfinite(v) and 0 <= v <= 1 for v in y), "Invalid bound input Y")
    require(
        all(math.isfinite(v) for v in coefficients + fresh), "Nonfinite assembly input"
    )
    masses = list(map(Q, masses))
    yy, cc = list(map(Q, y)), list(map(Q, coefficients))
    exact_values, bounds, residuals = [], [], []
    for actual, species_terms in zip(fresh, terms, strict=True):
        exact = Q(0)
        magnitudes, products_error, coefficient_error = Q(0), Q(0), Q(0)
        for reaction, reactants, a_float, a_rational in species_terms:
            operands = [Q(a_float), cc[reaction], *(yy[i - 1] for i in reactants)]
            p, error = product_bound(operands)
            flux = cc[reaction] * math.prod(yy[i - 1] for i in reactants)
            exact += a_rational * flux
            coefficient_error += abs(Q(a_float) - a_rational) * abs(flux)
            magnitudes += abs(p) + error
            products_error += error
        # All partial sums are finite for any association inside this envelope.
        require(magnitudes < MAXIMUM, "Assembly overflow envelope unsupported")
        n = (
            len(species_terms) + 3
        )  # per-class zero additions and 3 final class additions
        summation_error = gamma(n) * magnitudes + 4 * n * NORMAL / (1 - n * U)
        bound = coefficient_error + products_error + summation_error
        residual = abs(Q(actual) - exact)
        require(residual <= bound, "Fresh RHS outside coefficient-conditioned bound")
        exact_values.append(exact)
        bounds.append(bound)
        residuals.append(residual)
    require(
        sum(a * f for a, f in zip(masses, exact_values, strict=True)) == 0,
        "Exact baryon assembly defect",
    )
    baryon = abs(sum(a * Q(f) for a, f in zip(masses, fresh, strict=True)))
    baryon_bound = sum(a * e for a, e in zip(masses, bounds, strict=True))
    require(baryon <= baryon_bound, "Fresh baryon residual outside derived bound")
    return {
        "component_absolute_residual": [float(v) for v in residuals],
        "component_absolute_bound": [upper_float(v) for v in bounds],
        "fresh_baryon_absolute_residual": float(baryon),
        "baryon_absolute_bound": upper_float(baryon_bound),
        "conditional_assembly_check": True,
        "scientific_accuracy_acceptance": False,
    }
