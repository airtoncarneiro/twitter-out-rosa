import os
import requests
import time


class Mini_Twitter_API:
    """
    Classe que implementa métodos para acesso à três endpoints
    da API do Twitter.
    """

    def __init__(self) -> None:
        self.URL_BASE = "https://api.twitter.com"
        # Autenticação na API do Twitter
        self.bearer_token = os.environ.get("TWITTER_BEARER_TOKEN")


    def __bearer_oauth(self, r) -> requests.models.PreparedRequest:
        """
        Method required by bearer token authentication.
        """

        r.headers["Authorization"] = f"Bearer {self.bearer_token}"
        r.headers["User-Agent"] = "v2TweetLookupPython"
        return r


    def __connect_to_endpoint(self, url:str, params:dict=None) -> dict:
        """ Faz a requisição ao endpoint do TWITTER

        Args:
            url (str): URL completo do endpoint
            params (dict): Parâmetros da requisição

        Raises:
            Exception: _description_

        Returns:
            dict: JSON contendo o retorno da requisição (twittes ou users)
        """

        # Pausa (em segundos)
        time.sleep(1)

        response = requests.request("GET", url, auth=self.__bearer_oauth, 
                                    params=params)

        #print(response.status_code)
        # 429 - Too Many Requests
        if response.status_code != 200:
            raise Exception(response.status_code, response.text)
        
        return response
    

    def search_recents(self, number_of_days:int=6, number_of_tweets:int=10, 
                       next_token:str=None, since_id:int=0) -> dict:
        """ Busca os tweets mais recentes

        Args:
            number_of_days (int, optional): Informa em até quantos dias atrás a
              pesquisa deve se extender. O Twitter limita à 7 a partir de 30s
              atrás. Defaults to 6.
            number_of_tweets (int, optional): Quantidade de twittes por
              retorno. Defaults to 10.
            next_token (str, optional): Token para paginar. Defaults to None.
            since_id (int, optional): Se informado um ID de um twitte,
              a pesquisa retroage até ele (Obdecendo, claro, ao number_of_days).
              Defaults to 0.
            
            obs: query tem um limite de 512 caracteres no nível da conta atual.

        Returns:
            dict: JSON contendo os twittes
        """

        assert number_of_days <= 6, "Número de  dias não pode ser maior que 6!"

        URL = self.URL_BASE + "/2/tweets/search/recent"

        query_params = {"query": ' '.join('lang:pt ("outubro rosa" \
                                            OR "cancer na mama" \
                                            OR "cancer de mama" \
                                            OR "auto exame" \
                                            OR autoexame \
                                            OR "exame da mama" \
                                            OR "exame de mama" \
                                            OR mamografia \
                                            OR "autoexame de mama" \
                                            OR "autoexame da mama" \
                                            OR "ressonancia magnetica da mama" \
                                            OR #OutubroRosa \
                                            OR #CancerdeMama)'.split()),

                        "max_results": f"{number_of_tweets}",
                        #"expansions":"referenced_tweets.id,geo.place_id",
                        "expansions": "geo.place_id",
                        "place.fields": "country_code",
                        "tweet.fields": ''.join(("author_id, \
                                        conversation_id, \
                                        created_at, \
                                        id, \
                                        in_reply_to_user_id, \
                                        lang,public_metrics, \
                                        reply_settings, \
                                        text").split()),
                        }
        
        # se foi informado o o ID do último Tweet capturado,
        # buscar todos os novos até chegar nele.
        if since_id != 0:
            query_params['since_id'] = since_id

        # se há token, ir para página anterior
        if next_token:
            query_params['next_token'] = next_token

        return self.__connect_to_endpoint(url=URL, params=query_params)


    def search_users(self, ids:list) -> dict:
        """ Busca pelos usuários

        Args:
            IDs (list): Lista de IDs dos usuários para pesquisar

        Returns:
            dict: JSON contendo os usuários
        """
        
        assert len(ids) <= 100, "Qtd de IDs não pode ser maior que 100!"
        str_ids = ','.join(list(map(str, ids)))

        URL = self.URL_BASE + "/2/users"

        query_params = {"ids": f"{str_ids}",
                        "user.fields": ''.join(("created_at, \
                                        description, \
                                        id, \
                                        location, \
                                        name, \
                                        protected, \
                                        public_metrics, \
                                        username, \
                                        verified, \
                                        withheld").split()),
                        }
        
        return self.__connect_to_endpoint(url=URL, params=query_params)
