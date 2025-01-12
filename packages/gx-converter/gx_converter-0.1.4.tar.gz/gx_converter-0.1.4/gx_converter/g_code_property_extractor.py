"""g_code_property_extractor.py

This module contains the GCodePropertyExtractor class, which is used for retrieving various
properties in the g-code to be used in gx header generation.
"""

from re import search, RegexFlag


class GCodePropertyExtractor:
    """Methods for retrieving properties in g-code"""

    @staticmethod
    def get_print_time(gcode: str) -> int:
        """Get print time from g-code

        Args:
            gcode: original g-code

        Returns:
            Print time
        """

        return GCodePropertyExtractor._extract_comment_value("TIME", gcode)

    @staticmethod
    def get_layer_height(gcode: str) -> int:
        """Get layer height in microns (µ) from g-code

        Args:
            gcode: original g-code

        Returns:
            Layer height
        """

        height = GCodePropertyExtractor._extract_comment_value("Layer height", gcode)
        return height * 10

    @staticmethod
    def get_filament_usage(gcode: str) -> int:
        """Get filament usage from g-code

        Args:
            gcode: original g-code

        Returns:
            Filament usage
        """

        return GCodePropertyExtractor._extract_comment_value("Filament used", gcode)

    @staticmethod
    def get_nozzle_temperature(gcode: str) -> int:
        """Get nozzle temperature from g-code

        Args:
            gcode: original g-code

        Returns:
            Nozzle temperature
        """

        return GCodePropertyExtractor._extract_command_value("M104", "S", gcode)

    @staticmethod
    def get_hotbed_temperature(gcode: str) -> int:
        """Get hotbed temperature from g-code

        Args:
            gcode: original g-code

        Returns:
            Hotbed temperature
        """

        return GCodePropertyExtractor._extract_command_value("M140", "S", gcode)

    @staticmethod
    def _extract_comment_value(comment: str, gcode: str) -> int:
        """Extract a numerical value from g-code

        Args:
            comment: The command containing the value (e.g., TIME)
            gcode: G-code from which to extract

        Returns:
            Numerical value, 0 if failure
        """

        # ;FLAVOR:Marlin
        # ;TIME:399
        # ;Filament used: 0.270103m
        # ;Layer height: 0.18

        result = search(f"^;{comment}:.*", gcode, RegexFlag.MULTILINE)
        if not result:
            return 0

        result = result.group(0)
        value = result.split(":")[1].strip()

        if "m" in value:
            # strip notation and convert meters to mm
            value = value.replace("m", "")
            value_parts = value.split(".")
            value_after_decimal = value_parts[1][:3]
            value = value_parts[0] + value_after_decimal

        # "convert" floats by removing decimal point
        value = value.replace(".", "")

        return int(value)

    @staticmethod
    def _extract_command_value(command: str, value_marker: str, gcode: str) -> int:
        """Extract a numerical value from g-code

        Args:
            command: The command containing the value (e.g., M104)
            value_marker: The marker preceding the desired value (e.g., S)
            gcode: G-code from which to extract

        Returns:
            Numerical value, 0 if failure
        """

        result = search(f"^{command} {value_marker}.*", gcode, RegexFlag.MULTILINE)
        if not result:
            return 0

        result = result.group(0)
        value = 0

        for argument in result.split():
            if value_marker in argument:
                value = int(argument[1:])
                break

        return value
