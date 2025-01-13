import os
from datetime import datetime
# my packages
from optima35.core import OptimaManager
from OptimaLab35.utils.utility import Utilities
from OptimaLab35.ui.simple_tui import SimpleTUI
from OptimaLab35 import __version__

class OptimaLab35_lite():
    def __init__(self):
        self.name = "OptimaLab35-lite"
        self.version = __version__
        self.o = OptimaManager()
        self.u = Utilities()
        self.tui = SimpleTUI()
        self.u.program_configs()
        self.exif_file = os.path.expanduser("~/.config/OptimaLab35/exif.yaml")
        self.available_exif_data = self.u.read_yaml(self.exif_file)
        self.setting_file = os.path.expanduser("~/.config/OptimaLab35/tui_settings.yaml")
        self.settings = {
            "input_folder": None,
            "output_folder": None,
            "file_format": None,
            "resize": None,
            "copy_exif": None,
            "contrast": None,
            "brightness": None,
            "new_file_names": None,
            "invert_image_order": False,
            "watermark": None,
            "gps": None,
            "modifications": [],
        }
        self.settings_to_save = [
            "resize",
            "jpg_quality",
            "png_compression",
            "optimize",
            "contrast",
            "brightness"
            ]

    def _process(self):
        self._check_options() # Get all user selected data
        input_folder_valid = os.path.exists(self.settings["input_folder"])
        output_folder_valid = os.path.exists(self.settings["output_folder"])
        if not input_folder_valid or not output_folder_valid:
            print("Warning", f"Input location {input_folder_valid}\nOutput folder {output_folder_valid}...")
            return

        input_folder = self.settings["input_folder"]
        output_folder = self.settings["output_folder"]

        image_files = [
            f for f in os.listdir(input_folder) if f.lower().endswith((".png", ".jpg", ".jpeg", ".webp"))
        ]
        i = 1
        for image_file in image_files:
            input_path = os.path.join(input_folder, image_file)
            if self.settings["new_file_names"] != False:
                image_name = self.u.append_number_to_name(self.settings["new_file_names"], i, len(image_files), self.settings["invert_image_order"])
            else:
                image_name = os.path.splitext(image_file)[0]
            output_path = os.path.join(output_folder, image_name)
            self.o.process_image(
                image_input_file = input_path,
                image_output_file = output_path,
                file_type = self.settings["file_format"],
                quality = self.settings["jpg_quality"],
                compressing = self.settings["png_compression"],
                optimize = self.settings["optimize"],
                resize = self.settings["resize"],
                watermark = self.settings["watermark"],
                font_size = self.settings["font_size"],
                grayscale = self.settings["grayscale"],
                brightness = self.settings["brightness"],
                contrast = self.settings["contrast"],
                dict_for_exif = self.selected_exif,
                gps = self.settings["gps"],
                copy_exif = self.settings["copy_exif"])
            self.u.progress_bar(i, len(image_files))
            i += 1

    def _check_options(self):
        try:
            if "Resize image" in self.settings["modifications"]:
                self.settings["resize"] = self.settings["resize"]
            else:
                self.settings["resize"] = None

            if "Convert to grayscale" in self.settings["modifications"]:
                self.settings["grayscale"] = True
            else:
                self.settings["grayscale"] = False

            if "Change contrast" in self.settings["modifications"]:
                self.settings["contrast"] = self.settings["contrast"]
            else:
                self.settings["contrast"] = None

            if "Change brightness" in self.settings["modifications"]:
                self.settings["brightness"] = self.settings["brightness"]
            else:
                self.settings["brightness"] = None

            if "Rename images" in self.settings["modifications"]:
                self.settings["new_file_names"] = self.settings["new_file_names"]
            else:
                self.settings["new_file_names"] = False

            if "Invert image order" in self.settings["modifications"]:
                self.settings["invert_image_order"] = True
            else:
                self.settings["invert_image_order"] = False

            if "Add Watermark" in self.settings["modifications"]:
                self.settings["watermark"] = self.settings["watermark"]
            else:
                self.settings["watermark"] = None

            self.settings["optimize"] =  self.settings["optimize"]
            self.settings["png_compression"] = self.settings["png_compression"]
            self.settings["jpg_quality"] = self.settings["jpg_quality"]

            self.settings["input_folder"] = self.settings["input_folder"]
            self.settings["output_folder"] = self.settings["output_folder"]
            self.settings["file_format"] = self.settings["file_format"]
            self.settings["font_size"] = 2 # need to add option to select size

            self.settings["copy_exif"] = self.settings["copy_exif"]

            if "Change EXIF" in self.settings["modifications"]: #missing
                self.selected_exif = self._collect_exif_data() #
            else:
                self.selected_exif = None

        except Exception as e:
            print(f"Whoops: {e}")

    def _load_or_ask_settings(self):
        """Load settings from a YAML file or ask the user if not present or incomplete."""
        try:
            if self._read_settings(self.settings_to_save):
                for item in self.settings_to_save:
                    print(f"{item}: {self.settings[item]}")
                use_saved = self.tui.yes_no_menu("Use these settings?")
                if use_saved:
                    return
            else:
                print("No settings found...")
                self._ask_for_settings()
        except Exception as e:
            print(f"Error: {e}")
            self._ask_for_settings()

    def _ask_for_settings(self):
        print("Asking for new settings...\n")
        print(f"Settings for {self.name} v{self.version} will be saved {self.setting_file}...")
        self.settings["resize"] = self.take_input_and_validate(question = "Default resize percentage (below 100 downscale, above upscale): ", accepted_type = int, min_value = 10, max_value = 200)
        self.settings["contrast"] = self.take_input_and_validate(question = "Default contrast percentage (negative = decrease, positive = increase): ", accepted_type = int, min_value = -100, max_value = 100)
        self.settings["brightness"] = self.take_input_and_validate(question = "Default brighness percentage (negative = decrease, positive = increase): ", accepted_type = int, min_value = -100, max_value = 100)
        self.settings["jpg_quality"] = self.take_input_and_validate(question = "JPEG quality (1-100, 80 default): ", accepted_type = int, min_value = 1, max_value = 100)
        self.settings["png_compression"] = self.take_input_and_validate(question = "PNG compression level (0-9, 6 default): ", accepted_type = int, min_value = 0, max_value = 9)
        self.settings["optimize"] = self.tui.yes_no_menu("Optimize images i.e. compressing?")

        self._write_settings(self.settings_to_save)

    def _write_settings(self, keys_to_save):
        """"Write self.setting, but only specific values"""
        keys = keys_to_save
        filtered_settings = {key: self.settings[key] for key in keys if key in self.settings}
        self.u.write_yaml(self.setting_file, filtered_settings)
        print("New settings saved successfully.")

    def _read_settings(self, keys_to_load):
        """
        Read settings from the settings file and update self.settings
        with the values for specific keys without overwriting existing values.
        """
        # First draft by ChatGPT, adjusted to fit my needs.
        keys = keys_to_load
        if os.path.exists(self.setting_file):
            loaded_settings = self.u.read_yaml(self.setting_file)
            for key in keys:
                if key in loaded_settings:
                    self.settings[key] = loaded_settings[key]
            print("Settings loaded successfully.")
            return True
        else:
            print("Settings file empty.")
            return False

    def _collect_exif_data(self):
        """Collect EXIF data based on user input."""
        print(f"Exif file can be found {self.exif_file}...")
        user_data = {}
        fields = [
            "make", "model", "lens", "iso", "image_description",
            "user_comment", "artist", "copyright_info"
        ]
        for field in fields:

            choise = self.tui.choose_menu(f"Enter {field.replace('_', ' ').title()}", self.available_exif_data[field])
            user_data[field] = choise

        user_data["software"] = f"{self.o.name} {self.o.version}"
        new_date = self._get_date_input()

        if new_date:
            user_data["date_time_original"] = new_date

        self.settings["gps"] = self._get_gps_input(user_data)

        return user_data

    def _get_gps_input(self, test_exif):
        while True:
            lat = input("Enter Latitude (xx.xxxxxx): ")
            if lat == "":
                return None
            long = input("Enter Longitude (xx.xxxxxx): ")
            try:
                self.o.exif_handler.add_geolocation_to_exif(test_exif, float(lat), float(long))
                return [lat, long]
            except Exception:
                print("Invalid GPS formate, try again...")

    def _get_date_input(self):
        # Partially chatGPT
        while True:
            date_input = input("Enter a date (yyyy-mm-dd): ")
            if date_input == "":
                return None  # Skip if input is empty
            try:
                new_date = datetime.strptime(date_input, "%Y-%m-%d")
                return new_date.strftime("%Y:%m:%d 00:00:00")
            except ValueError:
                print("Invalid date format. Please enter the date in yyyy-mm-dd format.")

    def _get_user_settings(self):
        """Get initial settings from the user."""
        menu_options = [
            "Resize image",
            "Change EXIF",
            "Convert to grayscale",
            "Change contrast",
            "Change brightness",
            "Rename images",
            "Invert image order",
            "Add Watermark"
        ] # new option can be added here.

        self.settings["input_folder"] = input("Enter path of input folder: ").strip() # Add: check if folder exists.
        self.settings["output_folder"] = input("Enter path of output folder: ").strip()
        self.settings["file_format"] = self.take_input_and_validate(question = "Enter export file format (jpg, png, webp): ", accepted_input = ["jpg", "png", "webp"], accepted_type = str)
        self.settings["modifications"] = self.tui.multi_select_menu(
            f"\n{self.name} v{self.version} for {self.o.name} v.{self.o.version} \nSelect what you want to do (esc or q to exit)",
            menu_options
        )
        if "Change EXIF" not in self.settings["modifications"]:
            self.settings["copy_exif"] = self.tui.yes_no_menu("Do you want to copy exif info from original file?")
        if "Rename images" in self.settings["modifications"]:
            self.settings["new_file_names"] = input("What should be the name for the new images? ") # Need
        else:
            self.settings["new_file_names"] = False
        if "Invert image order" in self.settings["modifications"]:
            self.settings["invert_image_order"] = True
        else:
            self.settings["invert_image_order"] = False
        if "Add Watermark" in self.settings["modifications"]:
            self.settings["watermark"] = input("Enter text for watermark. ")
        else:
            self.settings["watermark"] = False

        os.makedirs(self.settings["output_folder"], exist_ok = True)

    def take_input_and_validate(self, question, accepted_input = None, accepted_type = str, min_value = None, max_value = None):
        """
        Asks the user a question, validates the input, and ensures it matches the specified criteria.
        Args:
            question (str): The question to ask the user.
            accepted_input (list): A list of acceptable inputs (optional for non-numeric types).
            accepted_type (type): The expected type of input (e.g., str, int, float).
            min_value (int/float): Minimum value for numeric inputs (optional).
            max_value (int/float): Maximum value for numeric inputs (optional).

        Returns:
            The validated user input.
        """
        # Main layout by chatGPT, but modified.
        while True:
            user_input = input(question).strip()

            try:
                # Convert input to the desired type
                if accepted_type in [int, float]:
                    user_input = accepted_type(user_input)
                    # Validate range for numeric types
                    if (min_value is not None and user_input < min_value) or (max_value is not None and user_input > max_value):
                        print(f"Input must be between {min_value} and {max_value}.")
                        continue
                elif accepted_type == str:
                    # No conversion needed for strings
                    user_input = str(user_input)
                else:
                    raise ValueError(f"Unsupported type: {accepted_type}")

                # Validate against accepted inputs if provided
                if accepted_input is not None and user_input not in accepted_input:
                    print(f"Invalid input. Must be one of: {', '.join(map(str, accepted_input))}.")
                    continue

                return user_input  # Input is valid

            except ValueError:
                print(f"Invalid input. Must be of type {accepted_type.__name__}.")

    def run(self):
        """Run the main program."""
        self._load_or_ask_settings()
        self._get_user_settings()
        self._process()
        print("Done")

def main():
    app = OptimaLab35_lite()
    app.run()

if __name__ == "__main__":
    main()
