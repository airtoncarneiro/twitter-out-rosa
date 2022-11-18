import json
import pathlib
from typing import Generator
from lib.variables import FOLDER_TWEETE, FOLDER_USER


def __return_all_files(folder:str, mask:str) -> Generator[str, None, None]:
    """
    Lista todos os arquivos encontrados num diretório.
    """

    return pathlib.Path(folder).glob(mask)


def find_tweet_newest_id() -> int:
    """
    Faz uma busca interna nos arquivos dos tweets pelo seu ID
    retornando o mais recente.
    Este ID será a base para definir quando a busca por novos
    tweetes deve chegar ao fim.
    """

    newest_id = 0
    files = __return_all_files(f'{FOLDER_TWEETE}', 'tweets*.json')
    for file in files:
        with open(file.absolute(), 'r', encoding='utf-8') as file:
            json_data = json.load(file)
            newest_id_file = int(json_data['meta']['newest_id'])
            
        if newest_id_file > newest_id:
            newest_id = newest_id_file
    
    return newest_id


def return_all_new_user_IDs() -> set:
    """
    Depois de capturar todos os IDs dos usuários dos twittes,
    identifica quais IDs não estão nos arquivos de usuários do twitter
    (identifica os novos usuários).
    """

    # pesquisa pelos IDs nos arquivos dos twittes
    users_ids = set()
    files = __return_all_files(f'{FOLDER_TWEETE}', 'tweets*.json')
    for file in files:
        with open(file.absolute(), 'r', encoding='utf-8') as file_json:
            json_data = json.load(file_json)
            datas = json_data['data']
        
        for data in datas:
            users_ids.add(data['author_id'])

    # pesquisa pelos IDs nos arquivos dos usuários
    users_ids_already_exist = set()
    files = __return_all_files(f'{FOLDER_USER}', 'users*.json')
    for file in files:
        with open(file.absolute(), 'r', encoding='utf-8') as file_json:
            json_data = json.load(file_json)
            #datas = json_data['data']
            datas = json_data.get('data', None)
        
        if datas:
            for data in datas:
                users_ids_already_exist.add(data['id'])

    # deixa apenas os ID novos (que existem nos twittes mas não no users)
    users_ids = list(users_ids)
    users_ids_already_exist = list(users_ids_already_exist)

    new_ids = set(users_ids) - set(users_ids_already_exist)

    return new_ids