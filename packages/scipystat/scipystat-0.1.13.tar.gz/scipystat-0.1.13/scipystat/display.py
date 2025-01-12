import importlib.resources as pkg_resources
from PIL import Image
import IPython.display as display

THEORY = []

def get_png_files(subdir):
    package = f"{subdir}"
    png_files = []
    try:
        for resource in pkg_resources.contents(package):
            if resource.endswith(".png"):
                with pkg_resources.path(package, resource) as file_path:
                    png_files.append(file_path)
    except Exception as e:
        print(f"Error accessing PNG files in {subdir}: {e}")
    return png_files

def display_png_files(subdir):
    png_files = get_png_files(subdir)
    for file in png_files:
        img = Image.open(file)
        display.display(img)

def create_display_function(subdir):
    def display_function():
        display_png_files(subdir)

    display_function.__name__ = f"display_{subdir}"
    display_function.__doc__ = (
        f"Вывести все страницы из файла с теорией '{subdir.replace('_', '-')}'.\n"
        f"Эта функция сгенерирована автоматически из файла '{subdir.replace('_', '-') + '.pdf'}' "
        f"из внутрибиблиотечного каталога файлов с теорией."
    )
    globals()[display_function.__name__] = display_function
    THEORY.append(display_function)

def list_subdirectories():
    package = ""
    subdirs = []
    package_path = pkg_resources.files(package)
    for item in package_path.iterdir():
        if item.is_dir():
            subdirs.append(item.name)
    return subdirs

subdirs = list_subdirectories()
for subdir in subdirs:
    create_display_function(subdir)
