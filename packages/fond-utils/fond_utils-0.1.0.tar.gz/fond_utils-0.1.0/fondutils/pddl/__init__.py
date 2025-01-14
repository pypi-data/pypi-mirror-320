
_all__ = ['pddl']

"""Top-level package for extending pddl parser to APP."""

def parse_domain_problem(fn):
    # able to parse files containing only domain or only problem, or domain followed by problem
    from fondutils.pddl.domprob import DomProbParser

    with open(fn, "r") as f:
        ptext = f.read()
    return DomProbParser()(ptext)
