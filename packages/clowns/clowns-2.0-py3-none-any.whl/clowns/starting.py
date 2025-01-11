import importlib.resources as pkg_resources

teor = {
    "0": "0",
    "1": "r",
    "2": "p",
    "3": "питон",
    "4": "таблица",
    "5": "анализ",
    "6": "границы"
}

content = ''


def write(name):
    global content

    resource_package = 'clowns.t'

    keys = [key for key, val in teor.items() if val == name]

    resource_path = f'{keys[0]}.txt'
    with pkg_resources.open_text(resource_package, resource_path) as file:
        content = file.read()
    return content
