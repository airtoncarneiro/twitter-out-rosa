import json
from datetime import datetime
from lib.mini_twitter_api import Mini_Twitter_API
import lib.twittes_files as twFiles
from time import sleep #, time
from lib.variables import FOLDER_BASE, QTD_DIAS_RETROAGIR, QTD_TWETTES_POR_REQUEST



def save_file(json_response:dict, dtime:str, tipo_arq:str) -> None:
    """ Salva o dicionário JSON em arquivo

    Args:
        json_response (dict): JSON
        dtime (str): Data e hora para colocar como parte do nome do arquivo
        tipo_arq (str): Prefixo para o nome do arquivo
    """

    nm_arquivo = f'{FOLDER_BASE}/{tipo_arq}/' + ''.join([tipo_arq, '_', dtime, '.json'])
    with open(nm_arquivo, 'w', encoding='utf-8') as file:
        json.dump(json_response, file, ensure_ascii=False)


#timing
def download_recents_tweets() -> int:
    """ Pesquisa pelos novos twittes
        
        Returns:
            int: Quantidade de twittes localizados e baixados.
    """
    
    # Define as constantes para usar na busca dos twittes
    NEWEST_ID = twFiles.find_tweet_newest_id()

    # Instancia a API
    API = Mini_Twitter_API()

    next_token = None
    downloaded_twittes = 0
    x_rate_limit_remaining = 0
    x_rate_limit_reset = 0

    while True:
        # data e hora da requisição
        dtime_request = "{}".format((
            datetime.now().strftime("%Y_%m_%d_%H_%M_%S")))

        response = API.search_recents(
                                next_token=next_token, \
                                number_of_days=QTD_DIAS_RETROAGIR, \
                                number_of_tweets=QTD_TWETTES_POR_REQUEST,
                                since_id=NEWEST_ID)


        save_file(json_response=response.json(), dtime=dtime_request, 
                  tipo_arq='tweets')

        # soma à contabilização de twittes baixados
        downloaded_twittes += response.json()['meta'].get('result_count', 0)
        # Se existir o token, pega o valor para paginar o twitter
        next_token = response.json()['meta'].get('next_token', None)

        x_rate_limit_remaining = response.headers._store['x-rate-limit-remaining'][1]

        print('Twittes baixados: %d. Franquia restante: %s' % (downloaded_twittes,
                                                               x_rate_limit_remaining),
                                                               end='')
        print('\r', end='')

        # Se não existir, acabou os twittes
        if not next_token:
            break
        elif 'errors' in response.json().keys():
            ## todo: fazer a tratativa quando erro
            print('\n### ERROR ###', response.json_response)
            break

        if int(x_rate_limit_remaining) <= 0:
            x_rate_limit_reset = response.headers._store['x-rate-limit-reset'][1]
            sleep(x_rate_limit_reset)
    
    print('\n')
    
    #return downloaded_twittes


#timing
def download_new_user() -> None:
    """ Pesquisa por novos usuários

    Args:
        IDs (list): IDs dos usuários para baixar.
    """
    
    users_to_download = list(twFiles.return_all_new_user_IDs())

    # Instancia a API
    API = Mini_Twitter_API()

    downloaded_users = 0
    x_rate_limit_remaining = 0
    x_rate_limit_reset = 0


    while users_to_download:
        # data e hora da requisição
        dtime_request = "{}".format((
            datetime.now().strftime("%Y_%m_%d_%H_%M_%S")))

        response = API.search_users(users_to_download[0:100])

        # if 'errors' in json_response.keys():
        #     print(json_response)
        #     break

        save_file(json_response=response.json(),
                  dtime=dtime_request, 
                  tipo_arq='users')
        
        del users_to_download[0:100]

        # soma à contabilização de usuários baixados
        downloaded_users += len(response.json().get('data',''))

        x_rate_limit_remaining = response.headers._store['x-rate-limit-remaining'][1]

        print('Usuários baixados: %d. Franquia restante: %s' % (downloaded_users,
                                                               x_rate_limit_remaining),
                                                               end='')
        print('\r', end='')

        if int(x_rate_limit_remaining) <= 0:
            x_rate_limit_reset = response.headers._store['x-rate-limit-reset'][1]
            sleep(x_rate_limit_reset)
        
    print('\n')


if __name__ == '__main__':
    print('\nINÍCIO')
    download_recents_tweets()
    download_new_user()
    print('FIM')