import sys
import os
from datetime import datetime

import time

from optima35.core import OptimaManager
from OptimaLab35.utils.utility import Utilities
from OptimaLab35.ui.main_window import Ui_MainWindow
#from OptimaLab35.ui.test_window import Ui_Test_Window
from OptimaLab35.ui.preview_window import Ui_Preview_Window
from OptimaLab35.ui.exif_handler_window import ExifEditor
from OptimaLab35.ui.simple_dialog import SimpleDialog  # Import the SimpleDialog class
from OptimaLab35 import __version__

from PySide6.QtCore import Signal

from PySide6 import QtWidgets
from PySide6.QtWidgets import (
    QMessageBox,
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QCheckBox,
    QFileDialog,
    QHBoxLayout,
    QSpinBox,
    QProgressBar,
)

from PySide6.QtGui import QPixmap, QIcon

class PreviewWindow(QMainWindow, Ui_Preview_Window):
    values_selected = Signal(int, int, bool)

    def __init__(self):
        super(PreviewWindow, self).__init__()
        self.ui = Ui_Preview_Window()
        self.ui.setupUi(self)
        self.o = OptimaManager()
        ## Ui interaction
        self.ui.load_Button.clicked.connect(self._browse_file)
        self.ui.update_Button.clicked.connect(self._update_preview)
        self.ui.close_Button.clicked.connect(self._close_window)

        self.ui.reset_brightness_Button.clicked.connect(lambda: self.ui.brightness_spinBox.setValue(0))
        self.ui.reset_contrast_Button.clicked.connect(lambda: self.ui.contrast_spinBox.setValue(0))
        self.preview_image = None

    def _browse_file(self):
        file = QFileDialog.getOpenFileName(self, caption = "Select File", filter = ("Images (*.png *.webp *.jpg *.jpeg)"))
        if file[0]:
            self.ui.image_path_lineEdit.setText(file[0])
            self._update_preview()

    def _update_preview(self):
        path = self.ui.image_path_lineEdit.text()
        if not os.path.isfile(path):
            return
        try:
            img = self.o.process_image(
                save = False,
                image_input_file = path,
                image_output_file = "",
                grayscale = self.ui.grayscale_checkBox.isChecked(),
                brightness = int(self.ui.brightness_spinBox.text()),
                contrast = int(self.ui.contrast_spinBox.text()),
            )
        except Exception as e:
            QMessageBox.warning(self, "Warning", "Error loading image...")
            print(f"Error loading image...\n{e}")
            return
        # Create a QPixmap object from an image file

        self.preview_image = QPixmap.fromImage(img)
        self.ui.QLabel.setPixmap(self.preview_image)

    def _close_window(self):
            # Emit the signal with the values from the spinboxes and checkbox
            if self.ui.checkBox.isChecked():
                self.values_selected.emit(self.ui.brightness_spinBox.value(), self.ui.contrast_spinBox.value(), self.ui.grayscale_checkBox.isChecked())
            self.close()

class OptimaLab35(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(OptimaLab35, self).__init__()
        self.name = "OptimaLab35"
        self.version = __version__
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.o = OptimaManager()
        self.check_version()
        self.u = Utilities()
        self.u.program_configs()
        self.exif_file = os.path.expanduser("~/.config/OptimaLab35/exif.yaml")
        self.available_exif_data = None
        self.settings = {}
        self.setWindowTitle(f"{self.name} v{self.version}")
        self._default_ui_layout()
        self._define_gui_interaction()

        self.sd = SimpleDialog()
        self._change_statusbar(f"Using {self.o.name} v{self.o.version}", 5000)
        # Instantiate the second window
        self.preview_window = PreviewWindow()

    def open_preview_window(self):
        self.preview_window.values_selected.connect(self.update_values)
        self.preview_window.show()

    def update_values(self, value1, value2, checkbox_state):
        # Update main window's widgets with the received values
        # ChatGPT
        self.ui.brightness_spinBox.setValue(value1)
        self.ui.contrast_spinBox.setValue(value2)
        self.ui.grayscale_checkBox.setChecked(checkbox_state)

    def _default_ui_layout(self):
        self.ui.png_quality_spinBox.setVisible(False)
        self.ui.png_quality_Slider.setVisible(False)
        self.ui.quality_label_2.setVisible(False)

    def _define_gui_interaction(self):
        self.ui.input_folder_button.clicked.connect(self._browse_input_folder)
        self.ui.output_folder_button.clicked.connect(self._browse_output_folder)
        self.ui.start_button.clicked.connect(self._start_process)
        self.ui.insert_exif_Button.clicked.connect(self._start_insert_exif)
        self.ui.image_type.currentIndexChanged.connect(self._update_quality_options)

        self.ui.exif_checkbox.stateChanged.connect(
            lambda state: self._handle_checkbox_state(state, 2, self._populate_exif)
        )
        self.ui.tabWidget.currentChanged.connect(self._on_tab_changed)
        self.ui.edit_exif_button.clicked.connect(self._open_exif_editor)

        self.ui.actionAbout.triggered.connect(self._info_window)
        self.ui.actionPreview.triggered.connect(self.open_preview_window)
        self.ui.preview_Button.clicked.connect(self.open_preview_window)

    def _debug(self):
        for i in range(10):
            print(f"Testing... {i}")
            time.sleep(.3)

            self._handle_qprogressbar(i, 10)
        print("Finished")
        self.ui.progressBar.setValue(0)

    def _info_window(self):
        # ChatGPT, mainly
        info_text = f"""
        <h3>{self.name} v{self.version}</h3>
        <p>(C) 2024-2025 Mr. Finchum aka CodeByMrFinchum</p>
        <p>{self.name} is a GUI for <b>{self.o.name}</b> (v{self.o.version}).</p>
        <p> Both projects are in active development, for more details, visit:</p>
        <ul>
            <li><a href="https://gitlab.com/CodeByMrFinchum/OptimaLab35">OptimaLab35 GitLab</a></li>
            <li><a href="https://gitlab.com/CodeByMrFinchum/optima35">optima35 GitLab</a></li>
        </ul>
        """

        self.sd.show_dialog(f"{self.name} v{self.version}", info_text)

    def _prepear_image(self):
        pass

    def _image_list_from_folder(self, path):
        image_files = [
            f for f in os.listdir(path) if f.lower().endswith((".png", ".jpg", ".jpeg", ".webp"))
        ]
        return image_files

    def _start_process(self):
        self._toggle_buttons(False)
        self._update_settings() # Get all user selected data
        input_folder = self.settings["input_folder"]
        output_folder = self.settings["output_folder"]
        if not input_folder or not output_folder:
            QMessageBox.warning(self, "Warning", "Input or output folder not selected")
            self._toggle_buttons(True)
            return

        input_folder_valid = os.path.exists(input_folder)
        output_folder_valid = os.path.exists(output_folder)
        if not input_folder_valid or not output_folder_valid:
            QMessageBox.warning(self, "Warning", f"Input location {input_folder_valid}\nOutput folder {output_folder_valid}...")
            self._toggle_buttons(True)
            return

        image_list = self._image_list_from_folder(input_folder)
        if len(image_list) == 0:
            QMessageBox.warning(self, "Warning", "Selected folder has no supported files.")
            self._toggle_buttons(True)
            return

        if len(self._image_list_from_folder(output_folder)) != 0:
            reply = QMessageBox.question(
                self,
                "Confirmation",
                "Output folder containes images, which might get overritten, continue?",
                QMessageBox.Yes | QMessageBox.No,
            )

            if reply == QMessageBox.No:
                self._toggle_buttons(True)
                return

        self._process_images(image_list)

        self._toggle_buttons(True)
        QMessageBox.information(self, "Information", "Finished")

    def _toggle_buttons(self, state):
        self.ui.start_button.setEnabled(state)

        if self.ui.exif_checkbox.isChecked():
            self.ui.insert_exif_Button.setEnabled(state)

    def _process_images(self, image_files):
        input_folder = self.settings["input_folder"]
        output_folder = self.settings["output_folder"]

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
                optimize = self.ui.optimize_checkBox.isChecked(),
                resize = self.settings["resize"],
                watermark = self.settings["watermark"],
                font_size = self.settings["font_size"],
                grayscale = self.settings["grayscale"],
                brightness = self.settings["brightness"],
                contrast = self.settings["contrast"],
                dict_for_exif = self.user_selected_exif,
                gps = self.settings["gps"],
                copy_exif = self.settings["copy_exif"])
            self._handle_qprogressbar(i, len(image_files))
            i += 1

        self.ui.progressBar.setValue(0)

    def _insert_exif(self, image_files):
        input_folder = self.settings["input_folder"]

        i = 1
        for image_file in image_files:

            input_path = os.path.join(input_folder, image_file)
            print(input_path)

            self.o.insert_dict_to_image(
                exif_dict = self.user_selected_exif,
                image_path = input_path,
                gps = self.settings["gps"])
            self._change_statusbar(image_file, 100)
            self._handle_qprogressbar(i, len(image_files))
            i += 1

        self.ui.progressBar.setValue(0)

    def _start_insert_exif(self):
        self._toggle_buttons(False)
        self._update_settings() # Get all user selected data
        input_folder = self.settings["input_folder"]
        output_folder = self.settings["output_folder"]
        if not input_folder:
            QMessageBox.warning(self, "Warning", "Input not selected")
            self._toggle_buttons(True)
            return

        if output_folder:
            reply = QMessageBox.question(
                self,
                "Confirmation",
                "Output folder selected, but insert exif is done to images in input folder, Continue?",
                QMessageBox.Yes | QMessageBox.No,
            )

            if reply == QMessageBox.No:
                self._toggle_buttons(True)
                return

        input_folder_valid = os.path.exists(input_folder)
        if not input_folder_valid :
            QMessageBox.warning(self, "Warning", f"Input location {input_folder_valid}")
            self._toggle_buttons(True)
            return

        image_list = self._image_list_from_folder(input_folder)
        if len(image_list) == 0:
            QMessageBox.warning(self, "Warning", "Selected folder has no supported files.")
            self._toggle_buttons(True)
            return

        self._insert_exif(image_list)

        self._toggle_buttons(True)
        QMessageBox.information(self, "Information", "Finished")


    def _open_exif_editor(self):
        """Open the EXIF Editor."""
        self.exif_editor = ExifEditor(self.available_exif_data)
        self.exif_editor.exif_data_updated.connect(self._update_exif_data)
        self.exif_editor.show()

    def _update_exif_data(self, updated_exif_data):
        """Update the EXIF data."""
        self.exif_data = updated_exif_data
        self._populate_exif()

    def _handle_checkbox_state(self, state, desired_state, action):
        """Perform an action based on the checkbox state and a desired state. Have to use lambda when calling."""
        if state == desired_state:
            action()

    def _on_tab_changed(self, index):
        """Handle tab changes."""
        # chatgpt
        if index == 1:  # EXIF Tab
            self._handle_exif_file("read")
        elif index == 0:  # Main Tab
            self._handle_exif_file("write")

    def _sort_dict_of_lists(self, input_dict):
        # Partily ChatGPT
        sorted_dict = {}
        for key, lst in input_dict.items():
            # Sort alphabetically for strings, numerically for numbers
            if key == "iso":
                lst = [int(x) for x in lst]
                lst = sorted(lst)
                lst = [str(x) for x in lst]
                sorted_dict["iso"] = lst

            elif all(isinstance(x, str) for x in lst):
                sorted_dict[key] = sorted(lst, key=str.lower)  # Case-insensitive sort for strings

        return sorted_dict


    def _handle_exif_file(self, do):
        if do == "read":
            file_dict = self.u.read_yaml(self.exif_file)
            self.available_exif_data = self._sort_dict_of_lists(file_dict)
        elif do == "write":
            self.u.write_yaml(self.exif_file, self.available_exif_data)

    def _populate_exif(self):
        # partly chatGPT
        # Mapping of EXIF fields to comboboxes in the UI
        combo_mapping = {
            "make": self.ui.make_comboBox,
            "model": self.ui.model_comboBox,
            "lens": self.ui.lens_comboBox,
            "iso": self.ui.iso_comboBox,
            "image_description": self.ui.image_description_comboBox,
            "user_comment": self.ui.user_comment_comboBox,
            "artist": self.ui.artist_comboBox,
            "copyright_info": self.ui.copyright_info_comboBox,
        }

        self._populate_comboboxes(combo_mapping)

    def _populate_comboboxes(self, combo_mapping):
        """Populate comboboxes with EXIF data."""
        # ChatGPT
        for field, comboBox in combo_mapping.items():
            comboBox.clear()  # Clear existing items
            comboBox.addItems(map(str, self.available_exif_data.get(field, [])))

    def _update_quality_options(self):
            """Update visibility of quality settings based on selected format."""
            # ChatGPT
            selected_format = self.ui.image_type.currentText()
            # Hide all quality settings
            self.ui.png_quality_spinBox.setVisible(False)
            self.ui.jpg_quality_spinBox.setVisible(False)
            self.ui.jpg_quality_Slider.setVisible(False)
            self.ui.png_quality_Slider.setVisible(False)
            self.ui.quality_label_1.setVisible(False)
            self.ui.quality_label_2.setVisible(False)
            # Show relevant settings
            if selected_format == "jpg":
                self.ui.jpg_quality_spinBox.setVisible(True)
                self.ui.jpg_quality_Slider.setVisible(True)
                self.ui.quality_label_1.setVisible(True)
            elif selected_format == "webp":
                self.ui.jpg_quality_spinBox.setVisible(True)
                self.ui.jpg_quality_Slider.setVisible(True)
                self.ui.quality_label_1.setVisible(True)
            elif selected_format == "png":
                self.ui.png_quality_spinBox.setVisible(True)
                self.ui.png_quality_Slider.setVisible(True)
                self.ui.quality_label_2.setVisible(True)

    def _browse_input_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Input Folder")
        if folder:
            self.ui.input_path.setText(folder)

    def _browse_output_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder:
            self.ui.output_path.setText(folder)

    def _change_statusbar(self, msg, timeout = 500):
        self.ui.statusBar.showMessage(msg, timeout)

    def _handle_qprogressbar(self, current, total):
        progress = int((100 / total) * current)
        self.ui.progressBar.setValue(progress)

    def _get_checkbox_value(self, checkbox, default=None):
        """Helper function to get the value of a checkbox or a default value."""
        return checkbox.isChecked() if checkbox else default

    def _get_spinbox_value(self, spinbox, default=None):
        """Helper function to get the value of a spinbox and handle empty input."""
        return int(spinbox.text()) if spinbox.text() else default

    def _get_combobox_value(self, combobox, default=None):
        """Helper function to get the value of a combobox."""
        return combobox.currentIndex() + 1 if combobox.currentIndex() != -1 else default

    def _get_text_value(self, lineedit, default=None):
        """Helper function to get the value of a text input field."""
        return lineedit.text() if lineedit.text() else default

    def _get_selected_exif(self):
        """Collect selected EXIF data and handle date and GPS if necessary."""
        selected_exif = self._collect_selected_exif() if self.ui.exif_checkbox.isChecked() else None
        if selected_exif:
            if self.ui.add_date_checkBox.isChecked():
                selected_exif["date_time_original"] = self._get_date()
        if self.ui.gps_checkBox.isChecked():
            self.settings["gps"] = [self.ui.lat_lineEdit.text(), self.ui.long_lineEdit.text()]
        else:
            self.settings["gps"] = None
        return selected_exif

    def _update_settings(self):
        """Update .settings from all GUI elements."""
        # General settings
        self.settings["input_folder"] = self._get_text_value(self.ui.input_path)
        self.settings["output_folder"] = self._get_text_value(self.ui.output_path)
        self.settings["file_format"] = self.ui.image_type.currentText()
        self.settings["jpg_quality"] = self._get_spinbox_value(self.ui.jpg_quality_spinBox)
        self.settings["png_compression"] = self._get_spinbox_value(self.ui.png_quality_spinBox)
        self.settings["invert_image_order"] = self._get_checkbox_value(self.ui.revert_checkbox)
        self.settings["grayscale"] = self._get_checkbox_value(self.ui.grayscale_checkBox)
        self.settings["copy_exif"] = self._get_checkbox_value(self.ui.exif_copy_checkBox)
        self.settings["own_exif"] = self._get_checkbox_value(self.ui.exif_checkbox)
        self.settings["font_size"] = self._get_combobox_value(self.ui.font_size_comboBox)
        self.settings["optimize"] = self._get_checkbox_value(self.ui.optimize_checkBox)
        self.settings["own_date"] = self._get_checkbox_value(self.ui.add_date_checkBox)

        # Conditional settings with logic
        self.settings["resize"] = int(self.ui.resize_spinBox.text()) if self.ui.resize_spinBox.text() != "100" else None
        #self._get_spinbox_value(self.ui.resize_spinBox) if self.ui.resize_checkbox.isChecked() else None
        self.settings["brightness"] = int(self.ui.brightness_spinBox.text()) if self.ui.brightness_spinBox.text() != "0" else None
        #self._get_spinbox_value(self.ui.brightness_spinBox) if self.ui.brightness_checkbox.isChecked() else None
        self.settings["contrast"] = int(self.ui.contrast_spinBox.text()) if self.ui.contrast_spinBox.text() != "0" else None
        #self._get_spinbox_value(self.ui.contrast_spinBox) if self.ui.contrast_checkbox.isChecked() else None

        new_name = self._get_text_value(self.ui.filename, False) if self.ui.rename_checkbox.isChecked() else False
        if isinstance(new_name, str): new_name = new_name.replace(" ", "_")
        self.settings["new_file_names"] = new_name
        self.settings["watermark"] = self.ui.watermark_lineEdit.text() if len(self.ui.watermark_lineEdit.text()) != 0 else None
        #self._get_text_value(self.ui.watermark_lineEdit) if self.ui.watermark_checkbox.isChecked() else None

        # Handle EXIF data selection
        if self.settings["own_exif"]:
            self.user_selected_exif = self._get_selected_exif()
        else:
            self.user_selected_exif = None
            self.settings["gps"] = None

    def _get_date(self):
        date_input = self.ui.dateEdit.date().toString("yyyy-MM-dd")
        new_date = datetime.strptime(date_input, "%Y-%m-%d")
        return new_date.strftime("%Y:%m:%d 00:00:00")

    def _collect_selected_exif(self):
        user_data = {}
        user_data["make"] = self.ui.make_comboBox.currentText()
        user_data["model"] = self.ui.model_comboBox.currentText()
        user_data["lens"] = self.ui.lens_comboBox.currentText()
        user_data["iso"] = self.ui.iso_comboBox.currentText()
        user_data["image_description"] = self.ui.image_description_comboBox.currentText()
        user_data["user_comment"] = self.ui.user_comment_comboBox.currentText()
        user_data["artist"] = self.ui.artist_comboBox.currentText()
        user_data["copyright_info"] = self.ui.copyright_info_comboBox.currentText()
        user_data["software"] = f"{self.name} {self.version} with {self.o.name} {self.o.version}"
        return user_data

    def closeEvent(self, event):
        self.preview_window.close()

    def check_version(self, min_version="0.6.5-a1"):
        # Mainly ChatGPT
        from packaging import version  # Use `packaging` for robust version comparison

        current_version = self.o.version
        if version.parse(current_version) < version.parse(min_version):
            msg = (
                f"optima35 version {current_version} detected.\n"
                f"Minimum required version is {min_version}.\n"
                "Please update the core package to continue.\n"
                "https://pypi.org/project/optima35/"
            )
            QMessageBox.critical(None, "Version Error", msg)
            sys.exit(1)

def main():
    app = QtWidgets.QApplication(sys.argv)
    window = OptimaLab35()
    window.show()
    app.exec()

if __name__ == "__main__":
    main()
