import brickflowui as db
import os
from PIL import Image, ExifTags
import mimetypes

mimetypes.add_type('application/javascript', '.js')
mimetypes.add_type('application/javascript', '.mjs')
mimetypes.add_type('text/css', '.css')
app = db.App(title="Databricks in Explorer")
def get_image_paths(folder_path):
    image_extensions = {
        ".jpg", ".jpeg", ".png",
        ".bmp", ".tiff", ".tif", ".webp",
        ".gif", ".ico", ".jfif"
    }
    image_paths = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            extension = os.path.splitext(file)[1].lower()
            if extension in image_extensions:
                image_paths.append(os.path.join(root, file))
    return image_paths


def get_image_metadata(image_path):
    metadata = {}
    try:
        file_stats = os.stat(image_path)
        metadata["File Name"] = os.path.basename(image_path)
        metadata["Full Path"] = image_path
        metadata["Extension"] = os.path.splitext(image_path)[1]
        metadata["File Size (KB)"] = round(file_stats.st_size / 1024, 2)
        metadata["File Size (MB)"] = round(file_stats.st_size / (1024 * 1024), 3)
        with Image.open(image_path) as img:
            metadata["Image Format"] = img.format
            metadata["Width"] = img.width
            metadata["Height"] = img.height
            metadata["Dimensions"] = f"{img.width} x {img.height}"
            metadata["Color Mode"] = img.mode
            metadata["Image Frames"] = getattr(img, "n_frames", 1)
            metadata["DPI"] = img.info.get("dpi", "Not available")
            for key, value in img.info.items():
                if isinstance(value, bytes):
                    value = f"<binary metadata: {len(value)} bytes>"
                metadata[f"Image Info - {key}"] = str(value)
            exif_data = img.getexif()
            for tag_id, value in exif_data.items():
                tag_name = ExifTags.TAGS.get(tag_id, str(tag_id))
                if isinstance(value, bytes):
                    value = value.hex()
                metadata[f"EXIF - {tag_name}"] = str(value)
    except Exception as e:
        metadata["Metadata Error"] = str(e)
    return metadata


@app.page("/", title="Home")
def home():
    DEFAULT_STATE_DICT = {
        "DEFAULT_INT": 0,
        "DEFAULT_STRING": "",
        "DEFAULT_LIST": []
    }
    count, set_count = db.use_state(DEFAULT_STATE_DICT["DEFAULT_INT"])
    input_string, set_input_string = db.use_state(DEFAULT_STATE_DICT["DEFAULT_STRING"])
    input_int2, set_int2 = db.use_state(DEFAULT_STATE_DICT["DEFAULT_INT"])
    input_string2, set_input_string2 = db.use_state(DEFAULT_STATE_DICT["DEFAULT_STRING"])
    input_int3, set_int3 = db.use_state(DEFAULT_STATE_DICT["DEFAULT_INT"])
    image_metadata, set_image_metadata = db.use_state(DEFAULT_STATE_DICT["DEFAULT_LIST"])
    def load_images():
        if os.path.isdir(input_string):
            paths = get_image_paths(input_string)
            all_metadata = []
            for path in paths:
                metadata = get_image_metadata(path)
                all_metadata.append(metadata)
            set_image_metadata(all_metadata)
        else:
            set_image_metadata([])
    metadata_components = []
    for index, metadata in enumerate(image_metadata):
        details = [
            db.Text(f"{key}: {value}")
            for key, value in metadata.items()
        ]
        metadata_components.append(
            db.Column(
                [
                    db.Text(f"Image :- {index + 1}", variant="h2"),
                    *details
                ],
                gap=2,
                padding=4
            )
        )
    def create_counter_app(db):
        rv = [
            db.Text("Sample Counter", variant = "h1"),
            db.Button("Increment Counter", on_click = lambda: set_count(count + 1), variant = "danger"),
            db.Text(f"Counter Value: {count}", variant = "h2"),
            db.Button("Decrement Counter", on_click = lambda: set_count(count - 1), variant = "danger"),
        ]
        return rv

    def create_text_displayer_app(db):
        rv = [
            db.Text("Sample Text Displayer", variant = "h1"),
            db.Input("Enter text to display", value = input_string2, change_strategy = "blur", on_change = set_input_string2),
            db.Text(f"Displayed Text: {input_string2}", variant = "h2"),
        ]
        return rv

    def create_error_app(db,error_string):
        rv = [
            db.Text(f"Here is the error received from input box :- {error_string}", variant = "p")
        ]
        return rv




    main_app = [
        db.Text("Universal Counter App, only enter integer values:- For example, enter 2 to create 2 counter apps",variant="h1"),
        db.Input("Enter number of apps to create", value = input_int2, change_strategy = "blur", on_change = set_int2),

        db.Text("Universal Text Displayer App:- For example, enter 2 to create 2 text displayer apps",variant="h1"),
        db.Input("Enter number of apps to create", value = input_int3, change_strategy = "blur", on_change = set_int3),
        

        db.Text("Image Metadata Explorer", variant = "h1"),
        db.Input("Enter folder path", value = input_string, change_strategy = "blur", on_change = set_input_string),
        db.Button("Scan Folder", on_click = load_images),
        db.Text(f"Total Images Found: {len(image_metadata)}",variant = "h2"),
        *metadata_components
    ]
    apps = main_app
    try:
        for i in range(1, int(input_int2) + 1, 1):
            apps += create_counter_app(db)
    except Exception as e:
        error_string = "Only enter integer values!"
        apps += create_error_app(db,error_string)
        pass
    try:
        for i in range(1, int(input_int3) + 1, 1):
            apps += create_text_displayer_app(db)   
    except Exception as e:
        error_string = "Only enter integer values!"
        apps += create_error_app(db,error_string)
        pass   
    
    return db.Column(
        apps,
        gap=4,
        padding=6
    )

if __name__ == "__main__":
    app.run(host="localhost")
