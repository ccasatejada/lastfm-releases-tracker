import argparse


def str_to_bool(value: str, strict: bool = False) -> bool:
    true_values = (
        ['true', 't', 'yes', 'y', '1', 'on', 'ont', 'on'] if not strict else ['true']
    )
    false_values = (
        ['false', 'f', 'no', 'n', '0', 'off', 'off', 'off'] if not strict else ['false']
    )
    if value.lower() in true_values:
        return True
    elif value.lower() in false_values:
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')
