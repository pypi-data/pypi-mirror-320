import click
from pathlib import Path
import pandas as pd


@click.group()
def cli():
    pass


@click.command()
@click.argument('file')
@click.argument('tags')
@click.argument('value')
def put(file: str, tags: str, value: str):
    """
    :param file: filename
    :param tags: tags for link. eg: python:multiprocess:socket
    :param value: value for link
    :return:
    """
    home = Path.joinpath(Path.home(), 'savetxt')
    header = ["tags", "value"]
    Path(home).mkdir(exist_ok=True)
    filepath = Path.joinpath(home, f'{file}.json')
    row_to_add = pd.DataFrame(columns=header, data=[[tags, value]])
    if filepath.exists():
        row_to_add.to_json(filepath, mode='a', orient='records', lines=True, index=None)
    else:
        row_to_add.to_json(filepath, mode='w', orient='records', lines=True, index=None)


@click.command()
@click.argument('file')
def cat(file: str):
    home = Path.joinpath(Path.home(), 'savetxt')
    filepath = Path.joinpath(home, f'{file}.json')
    if filepath.exists():
        data = pd.read_json(filepath, orient='records', lines=True)
        pd.set_option('display.max_colwidth', None)
        print(data)


def get_site(row):
    return row.split('|')[1]


cli.add_command(put)
cli.add_command(cat)

if __name__ == '__main__':
    cli()