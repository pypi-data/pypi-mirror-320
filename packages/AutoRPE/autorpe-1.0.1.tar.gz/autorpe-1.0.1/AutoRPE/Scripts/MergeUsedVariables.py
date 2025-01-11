import argparse

def get_parser() -> argparse.ArgumentParser:

    help_text = """
    This script takes as arguments the path to the vault (-v/--vault) 
    created by SourcesWithRPE and a flagless list (namelists) of the namelist paths.
    """
    #parser = argparse.ArgumentParser(usage=help_text)
    parser = argparse.ArgumentParser()

    parser.add_argument("-o", "--output", default="used_variables.txt", help="Path to the output file.")

    parser.add_argument('used_variables', metavar='used_variables', type=str, nargs='+',
                        help='List of used_variables.txt.')

    return parser


def get_command_line_arguments():
    parser = get_parser()
    return parser.parse_args()


def main():
    # TODO move this script to the workflow of panther
    args = get_command_line_arguments()
    output_file = args.output
    used_variables = args.used_variables

    # Copy first file contents
    with open(used_variables.pop(0)) as _f:
        output_lines = _f.readlines()

    # Update lines when True
    for f in used_variables:
        with open(f) as _f:
            for i, line in enumerate(_f):
                if line.count("T"):
                    output_lines[i] = line
    
    # Write out the results
    with open(output_file, "w") as output:
        output.writelines(output_lines)


if __name__ == "__main__":
    main()
