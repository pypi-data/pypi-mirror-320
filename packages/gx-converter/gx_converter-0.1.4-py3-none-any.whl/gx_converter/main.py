"""main.py

Main entry point for gx_converter. This script converts gcode created in Cura to a format that
can be used with current firmware versions of FlashForge Adventurer 3 and Monoprice Voxel 3"""

import argparse

from pathlib import Path

from .g_code_property_extractor import GCodePropertyExtractor
from .g_code_transformer import GCodeTransformer
from .header import Header


def get_parser():
    parser = argparse.ArgumentParser(description="Convert Cura gcode to .gx format")
    parser.add_argument("gcode", type=str, help="File to convert")
    parser.add_argument(
        "--output",
        type=str,
        help="Output file. If not specified, will output based on gcode filename.",
        required=False,
    )
    return parser


def main():
    """Entry point for application"""

    parser = get_parser()
    args = parser.parse_args()

    gcode_file = Path(args.gcode)
    if not gcode_file.exists():
        print("File not found")
        raise SystemExit

    with open(gcode_file, "r") as f:
        code = f.read()

    hotbed_temp = GCodePropertyExtractor.get_hotbed_temperature(code)
    nozzle_temp = GCodePropertyExtractor.get_nozzle_temperature(code)
    print_time = GCodePropertyExtractor.get_print_time(code)
    filament_usage = GCodePropertyExtractor.get_filament_usage(code)
    layer_height = GCodePropertyExtractor.get_layer_height(code)
    shell_count = 3
    print_speed = 60

    code = GCodeTransformer.convert(code)

    header = Header(
        print_time,
        filament_usage,
        layer_height,
        shell_count,
        print_speed,
        hotbed_temp,
        nozzle_temp,
    )

    gx = header.assembled_header + code.encode("utf-8")
    output_file = (
        Path(args.output)
        if args.output
        else Path(gcode_file.parent, gcode_file.stem + ".gx")
    )

    with open(output_file, "wb") as f:
        f.write(gx)


if __name__ == "__main__":
    main()
