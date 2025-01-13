import re
import os
from datetime import datetime
from optima35.image_handler import ImageProcessor, ExifHandler
from optima35 import __version__

class OptimaManager:
    def __init__(self):
        self.name = "optima35"
        self.version = __version__
        self.image_processor = ImageProcessor()
        self.exif_handler = ExifHandler()

    def modify_timestamp_in_exif(self, data_for_exif: dict, filename: str):
            """"Takes a dict formated for exif use by piexif and adjusts the date_time_original, changing the minutes and seconds to fit the number of the filname."""
            last_three = filename[-3:len(filename)]
            total_seconds = int(re.sub(r'\D+', '', last_three))
            minutes = total_seconds // 60
            seconds = total_seconds % 60
            time = datetime.strptime(data_for_exif["date_time_original"], "%Y:%m:%d %H:%M:%S") # change date time string back to an time object for modification
            new_time = time.replace(hour=12, minute=minutes, second=seconds)
            data_for_exif["date_time_original"] = new_time.strftime("%Y:%m:%d %H:%M:%S")
            return data_for_exif

    def process_image(self, # TODO: split into two classes, one for modification for one saving..
        image_input_file,
        image_output_file,
        file_type = "jpg",
        quality = 90,
        compressing = 6,
        optimize = False,
        resize = None,
        watermark = None,
        font_size = 2,
        grayscale = False,
        brightness = None,
        contrast = None,
        dict_for_exif = None,
        gps = None,
        copy_exif = False,
        save = True):
        # Partly optimized by ChatGPT
        # Open the image file
        with self.image_processor.open_image(image_input_file) as img:
            processed_img = img
            image_name = os.path.basename(image_output_file) # for date adjustment
            # Resize
            if resize is not None:
                processed_img = self.image_processor.resize_image(
                    image=processed_img, percent = resize
                )

            # Watermark
            if watermark is not None:
                processed_img = self.image_processor.add_watermark(
                    processed_img, watermark, int(font_size)
                )

            # Grayscale
            if grayscale:
                processed_img = self.image_processor.grayscale(processed_img)

            # Brightness
            if brightness is not None:
                processed_img = self.image_processor.change_brightness(
                    processed_img, brightness
                )

            # Contrast
            if contrast is not None:
                processed_img = self.image_processor.change_contrast(
                    processed_img, contrast
                )

            # EXIF data handling
            exif_piexif_format = None
            if dict_for_exif: # todo: maybe move to ui and only accept complete exif dicts..
                selected_exif = dict_for_exif
                if "date_time_original" in dict_for_exif:
                    selected_exif = self.modify_timestamp_in_exif(selected_exif, image_name)
                exif_piexif_format = self.exif_handler.build_exif_bytes(
                    selected_exif, self.image_processor.get_image_size(processed_img)
                )

                # GPS data
                if gps is not None:
                    latitude = float(gps[0])
                    longitude = float(gps[1])
                    exif_piexif_format = self.exif_handler.add_geolocation_to_exif(exif_piexif_format, latitude, longitude)

            # Copy EXIF data if selected, and ensure size is correct in exif data
            elif copy_exif:
                try:
                    og_exif = self.exif_handler.get_exif_info(img)
                    og_exif["Exif"][40962], og_exif["Exif"][40963] = self.image_processor.get_image_size(processed_img)
                    exif_piexif_format = og_exif
                except Exception:
                    print("Copying EXIF data selected, but no EXIF data is available in the original image file.")

            if save:
                # Save the processed image
                    self.image_processor.save_image(
                        image = processed_img,
                        path = image_output_file,
                        piexif_exif_data = exif_piexif_format,
                        file_type = file_type,
                        jpg_quality = quality,
                        png_compressing = compressing,
                        optimize = optimize
                    )
            else:
                    return self.image_processor.convert_pil_to_qtimage(processed_img)

    def insert_dict_to_image(self, exif_dict, image_path, gps = None):
        image_name, ending = os.path.splitext(os.path.basename(image_path))
        img = self.image_processor.open_image(image_path)
        selected_exif = exif_dict
        if "date_time_original" in exif_dict:
            selected_exif = self.modify_timestamp_in_exif(selected_exif, image_name)

        exif_piexif_format = self.exif_handler.build_exif_bytes(
            selected_exif, self.image_processor.get_image_size(img)
        )

        # GPS data
        if gps is not None:
            latitude = float(gps[0])
            longitude = float(gps[1])
            exif_piexif_format = self.exif_handler.add_geolocation_to_exif(exif_piexif_format, latitude, longitude)

        self.exif_handler.insert_exif(exif_dict = exif_piexif_format, img_path = image_path)
