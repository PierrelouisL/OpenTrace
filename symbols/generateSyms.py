import csv
from collections import defaultdict
from pathlib import Path
import numpy

CSV_PATH = "FPGA-SC-02050-0-70-LIFCL-33U-Pinout.csv"
OUT_PATH = "lifcl-33u-fccsp104.kicad_sym"

SYMBOL_NAME = "LIFCL-33U"
REFDES = "U"

PIN_SPACING = 2.54
PIN_LENGTH = 2.54


def parse_csv(path):
    with open(path, 'r') as csv_file:
        reader = csv.reader(csv_file)

        pinNameI = 1
        pinNameExtI = 4
        bankI = 3
        pinAddr = -1
        banks = defaultdict(list)
        for row in reader:
            banks[int(row[bankI])].append({
                "pin" : row[pinAddr],
                "name": row[pinNameI] + (("/" + row[pinNameExtI]) if row[pinNameExtI] != '-' else "")
            })
        return banks


# def parse_csv(path):
#     banks = defaultdict(list)

#     with open(path, newline="", encoding="utf-8") as f:
#         reader = csv.DictReader(f)
#         for row in reader:
#             pin = row["PADN"].strip()
#             name = row["Signal Name"].strip()
#             bank = row["BANK"].strip()

#             if not pin or not name or not bank:
#                 continue

#             banks[bank].append({
#                 "pin": pin,
#                 "name": name
#             })

#     return banks


def emit_pin(pin, name, y, pin_type="bidirectional", direction=0):
    """
    Generate a KiCad symbol pin definition.
    
    Args:
        pin: Pin number/identifier (e.g., "K4")
        name: Pin name (e.g., "VCCIO2")
        y: Y position coordinate
        pin_type: Pin type (default: "bidirectional"). Options: "bidirectional", "input", "output", "power_in", etc.
        direction: Pin direction in degrees (0=left, 180=right, default=0)
    
    Returns:
        Formatted KiCad pin definition string
    """
    x_pos = -20.32 if direction == 0 else 15.24
    
    return (
        f'\t\t\t(pin {pin_type} line\n'
        f'\t\t\t\t(at {x_pos} {y:.2f} {direction})\n'
        f'\t\t\t\t(length {PIN_LENGTH})\n'
        f'\t\t\t\t(name "{name}"\n'
        f'\t\t\t\t\t(effects\n'
        f'\t\t\t\t\t\t(font\n'
        f'\t\t\t\t\t\t\t(size 1.27 1.27)\n'
        f'\t\t\t\t\t\t)\n'
        f'\t\t\t\t\t)\n'
        f'\t\t\t\t)\n'
        f'\t\t\t\t(number "{pin}"\n'
        f'\t\t\t\t\t(effects\n'
        f'\t\t\t\t\t\t(font\n'
        f'\t\t\t\t\t\t\t(size 1.27 1.27)\n'
        f'\t\t\t\t\t\t)\n'
        f'\t\t\t\t\t)\n'
        f'\t\t\t\t)\n'
        f'\t\t\t)\n'
    )


def generate_symbol(banks):
    out = []

    out.append("(kicad_symbol_lib")
    out.append("\t(version 20241209)")
    out.append('\t(generator "csv-bank-generator")')
    out.append(f'\t(symbol "{SYMBOL_NAME}"')
    out.append("\t\t(in_bom yes)")
    out.append("\t\t(on_board yes)")

    unit_index = 1

    for bank, pins in sorted(banks.items()):
        out.append(f'\t(symbol "{SYMBOL_NAME}_{unit_index}_1"')
        # out.append("\t\t(property \"Reference\" \"U\" (at 0 8 0))")
        # out.append(f"\t\t(property \"Value\" \"{SYMBOL_NAME} {bank}\" (at 0 -8 0))")

        y = 0
        for p in pins:
            out.append(emit_pin(p["pin"], p["name"], y))
            y -= PIN_SPACING

        out.append("\t)")
        unit_index += 1

    out.append("\t(embedded_fonts no)")
    out.append("))")

    return "\n".join(out)


if __name__ == "__main__":
    banks = parse_csv(CSV_PATH)
    sym = generate_symbol(banks)
    Path(OUT_PATH).write_text(sym, encoding="utf-8")
