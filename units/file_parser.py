import aioshutil
from units.normalize import normalize
from pathlib import Path
import asyncio
from time import time

# from aiopath import AsyncPath

REGISTER_EXTENSIONS = {
    'JPEG': 'IMAGES', 'PNG': 'IMAGES', 'JPG': 'IMAGES', 'SVG': 'IMAGES', 'GIF': 'IMAGES', 'ICO': 'IMAGES',
    'MP3': 'AUDIO', 'OGG': 'AUDIO', 'WAV': 'AUDIO', 'AMR': 'AUDIO', 'FLAC': 'AUDIO', 'WMA': 'AUDIO',
    'AVI': 'VIDEO', 'MP4': 'VIDEO', 'MOV': 'VIDEO', 'MKV': 'VIDEO', 'WMV': 'VIDEO',
    'DOC': 'DOCUMENTS', 'DOCX': 'DOCUMENTS', 'TXT': 'DOCUMENTS', 'PDF': 'DOCUMENTS', 'XLSX': 'DOCUMENTS',
    'PPTX': 'DOCUMENTS', 'RTF': 'DOCUMENTS',
    'BAT': 'PROGRAMS', 'CMD': 'PROGRAMS', 'EXE': 'PROGRAMS', 'C': 'PROGRAMS', 'CPP': 'PROGRAMS', 'JS': 'PROGRAMS',
    'PY': 'PROGRAMS', 'VBS': 'PROGRAMS',
    'ZIP': 'ARCHIVES', 'GZ': 'ARCHIVES', 'TAR': 'ARCHIVES'
}

FOLDERS = []
work_folder = Path('.')


def get_extension(filename: str) -> str:
    # Перетворюємо розширення файлу на назву теки .jpg -> JPG
    return Path(filename).suffix[1:].upper()


async def sort_files(file: Path, container: str, ext: str):
    if container == 'ARCHIVES':
        await handle_archive(file, work_folder / container)
    elif container == 'OTHERS' and not ext:
        new_file = work_folder / container
        await handle_file(file, new_file)
    else:
        new_file = work_folder / container / ext
        await handle_file(file, new_file)


async def scan_item(folder: Path, item: Path) -> None:
    # Якщо це тека, то додаємо її до списку FOLDERS і переходимо до наступного елемента теки
    if item.is_dir():
        # Перевіряємо, щоб тека не була тією, в яку ми вже складаємо файли
        if item.name not in ('ARCHIVES', 'VIDEO', 'AUDIO', 'DOCUMENTS', 'IMAGES', 'PROGRAMS', 'OTHERS'):
            FOLDERS.append(item)
            #  Скануємо цю вкладену теку – рекурсія
            subtasks = [scan_item(item, subfolder) for subfolder in item.iterdir()]
            await asyncio.gather(*subtasks)
            # for subfolder in item.iterdir():
            #     await scan_item(item, subfolder)
        #  Перейти до наступного елемента у сканованій теці
        return

    #  Пішла робота з файлом
    ext = get_extension(item.name)  # взяти розширення файлу
    fullname = folder / item.name  # взяти повний шлях к файлу
    if not ext:  # якщо файл не має розширення, додати до невідомих
        # OTHER.append(fullname)
        container = 'OTHERS'
    else:
        try:
            # Взяти список, куди покласти повний шлях до файлу
            container = REGISTER_EXTENSIONS[ext]
        except KeyError:
            # Якщо ми не реєстрували розширення у REGISTER_EXTENSIONS, то додати до іншого
            container = 'OTHERS'
    await sort_files(fullname, container, ext)


async def handle_file(filename: Path, target_folder: Path):
    target_folder.mkdir(exist_ok=True, parents=True)
    # filename.replace(target_folder / (normalize(filename.stem) + filename.suffix))
    await aioshutil.move(filename, target_folder / (normalize(filename.stem) + filename.suffix))


async def handle_archive(filename: Path, target_folder: Path):
    # Створюємо теку для архівів
    target_folder.mkdir(exist_ok=True, parents=True)
    # Створюємо теку, куду розпаковуємо архів
    # Беремо суфікс у файлу та прибираємо replace(filename.suffix, '')
    folder_for_file = target_folder / normalize(filename.name.replace(filename.suffix, ''))
    # Створюємо теку для архіву з іменем файлу

    folder_for_file.mkdir(exist_ok=True, parents=True)
    try:
        await aioshutil.unpack_archive(str(filename.resolve()), str(folder_for_file.resolve()))
    except aioshutil.Error:
        print(f'Обман - це не архів {filename}!')
        folder_for_file.rmdir()
        return None
    filename.unlink()


def handle_folder(folder: Path):
    try:
        folder.rmdir()
    except OSError:
        print(f'Не вдалося видалити теку {folder}')


async def file_parser():
    global FOLDERS

    FOLDERS = []
    if not work_folder.exists():
        return f'\nТеки {work_folder} не існує!'
    print(f'\n\033[033mScanning {work_folder.resolve()}...\033[0m')

    # Скануємо початкову теку
    tasks = [(scan_item(work_folder.resolve(), item)) for item in work_folder.iterdir()]
    await asyncio.gather(*tasks, return_exceptions=True)

    # Виконуємо реверс списку для того, щоб всі теки видалити.
    for folder in FOLDERS[::-1]:
        handle_folder(folder)
    return f'\nТека {work_folder} відсортована'

def start_fp():
    global work_folder

    work_folder = Path(input('Enter folder name >>> '))
    print(asyncio.run(file_parser()))
    input('\nPress any key...')


if __name__ == '__main__':
    start_fp()
