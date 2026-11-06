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
    input_string4, set_input_string4 = db.use_state(DEFAULT_STATE_DICT["DEFAULT_STRING"])
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


    def create_image_displayer_app(db,relative_folder_path):
        image_extensions = [
            ".jpg", ".jpeg", ".png",
            ".bmp", ".tiff", ".tif", ".webp",
            ".gif", ".ico", ".jfif"
        ]

        rv = []
        filenames = os.listdir(relative_folder_path)
        for filename in filenames:
            possible_path = os.path.join(relative_folder_path,filename)
            for image_extension in image_extensions:
                if possible_path.endswith(image_extension):
                    image_path = possible_path
                    image_path = rf"./{image_path}"
                    rv.append(db.Image(src=image_path))
                    break
        return rv


    main_app = [
        db.Text("Press anywhere outside the input box after following all the steps", variant="h1"),
        db.Text("Copy paste all images in current working folder that you want to display and then Type ./ of folder to show images",variant="h1"),
        db.Input("Copy paste all images in current working folder and then Type ./ of folder to show images", value = input_string4, change_strategy = "blur", on_change = set_input_string4),
        
        db.Text("Press anywhere outside the input box after following all the steps", variant="h1"),
        db.Text("Universal Counter App, only enter integer values:- For example, Type 2 to create 2 counter apps",variant="h1"),
        db.Input("Enter number of apps to create", value = input_int2, change_strategy = "blur", on_change = set_int2),

        db.Text("Press anywhere outside the input box after following all the steps", variant="h1"),
        db.Text("Universal Text Displayer App:- For example, Type 2 to create 2 text displayer apps",variant="h1"),
        db.Input("Enter number of apps to create", value = input_int3, change_strategy = "blur", on_change = set_int3),

        db.Text("Press anywhere outside the input box after following all the steps", variant="h1"),
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
        pass
    try:
        for i in range(1, int(input_int3) + 1, 1):
            apps += create_text_displayer_app(db)
    except Exception as e:
        pass
    try:
        apps += create_image_displayer_app(db,input_string4)
    except Exception as e:
        pass
    return db.Column(
        apps,
        gap=4,
        padding=6
    )

if __name__ == "__main__":
    app.run(host="localhost")

