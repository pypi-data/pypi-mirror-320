import argparse

from pddl.formatter import domain_to_string, problem_to_string

from .normalizer import normalize
from .determizer import determinize
from .pddl import parse_domain_problem


def main():
    parser = argparse.ArgumentParser(description="Utilities to process FOND PDDL")

    parser.add_argument("command", choices=["check", "determinize", "normalize"])
    parser.add_argument("--input", required=True, help="Input domain file")
    parser.add_argument("--output", help="Output domain file")
    parser.add_argument("--outproblem", help="Optional output problem file")
    parser.add_argument(
        "--prefix",
        default="_DETDUP_",
        help="Prefix for determinized action outcome identifier (Default: %(default)s)",
    )
    parser.add_argument(
        "--suffix", default="", help="Suffix for determinized action outcome identifier"
    )

    parser.add_argument(
        "--console", action="store_true", help="Print the domain after processing"
    )
    args = parser.parse_args()

    # the input may be a domain alone or a domain+problem
    fond_domain, fond_problem = parse_domain_problem(args.input)

    if fond_domain is None:
        parser.error("a domain is needed for this tool")

    if (
        (args.command in ["determinize", "normalize"])
        and (not args.output)
        and (not args.console)
    ):
        parser.error(f"--output is required for {args.command} command")

    # if (
    #     (fond_problem is not None)
    #     and (not args.outproblem)
    #     and (not args.command == "check")
    # ):
    #     parser.error("--outproblem is required for domain+problem input")

    if args.command == "check":
        print("\n  Checking domain/problem file (if parsed well, domain/problem is printed nicely)...\n")
        if fond_domain:
            print(domain_to_string(fond_domain))
        if fond_problem is not None:
            print(problem_to_string(fond_problem))
        return

    elif args.command == "determinize":
        new_domain = determinize(fond_domain, args.prefix, args.suffix)

    elif args.command == "normalize":
        new_domain = normalize(fond_domain)

    if args.output:
        with open(args.output, "w") as f:
            f.write(domain_to_string(new_domain))

            # write the problem (if any) in the same file as new domain
            if fond_problem is not None and args.outproblem is None:
                f.write("\n\n")
                f.write(problem_to_string(fond_problem))

    # write the problem (if any) in a separate problem file
    if args.outproblem and fond_problem is not None:
        with open(args.outproblem, "w") as f:
            f.write(problem_to_string(fond_problem))

    if args.console:
        print(domain_to_string(new_domain))

        if fond_problem is not None:
            print(problem_to_string(fond_problem))


if __name__ == '__main__':
    main()
