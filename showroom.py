import os
import json
from typing import Union

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv


class ShowroomPriveAuthenticator:
    """
    Classe permettant la connexion à son espace Showroom afin de récupérer
    la liste des commandes, et le détail de chaque commande.
    """
    def __init__(self, login: str, password: str, session_file: str = "session.json") -> None:
        """
        Méthode qui vérifie la validité des identifiants, qui initie
        une session, puis qui authentifie l'utilisateur.

        :param login: Correspond à l'adresse mail du compte
        :param password: Mot de passe associé à l'adresse mail
        :param session_file: Chemin vers le fichier pour sauvegarder les cookies de session
        """
        if not isinstance(login, str):
            raise ValueError("Le login doit être une chaîne de caractères.")

        if not isinstance(password, str):
            raise ValueError("Le mot de passe doit être une chaîne de caractères.")

        self.__session = requests.Session()
        self.session_file = session_file
        self.url = "https://www.showroomprive.com/ajax/onboarding/onboarding.aspx?action=login"
        self.params = {
            "login": login,
            "password": password,
            "stay": True,
            "direction": "https://www.showroomprive.com/"
        }

        self.__authenticate()

    def __is_authenticated(self) -> bool:
        """
        Vérifie si l'utilisateur est déjà authentifié.
        """
        # Charger les cookies de session à partir du fichier s'il existe
        try:
            with open(self.session_file, 'r') as f:
                __cookies = json.load(f)
                self.__session.cookies.update(__cookies)
        except FileNotFoundError:
            pass

        # Vérifier en accédant à une page accessible après l'authentification
        __verification_url = "https://www.showroomprive.com/moncompte/mescoordonnees.aspx"
        __response = self.__session.post(__verification_url)

        if __response.ok:
            return __response.url == __verification_url

    def __authenticate(self) -> Union[bool, requests.ConnectionError]:
        """
        Méthode de gestion de l'authentification.
        """
        if self.__is_authenticated():
            return True

        response = self.__session.post(self.url, json=self.params)

        if not response.ok:
            raise requests.ConnectionError("Le site n'est pas accessible.")

        if (response.status_code != 200 or
                response.json().get("status").get("code") != 1):
            raise requests.ConnectionError("L'authentification a échoué.")

        # Enregistrer les cookies de session dans un fichier
        with open(self.session_file, 'w') as f:
            json.dump(self.__session.cookies.get_dict(), f)

        return True

    def __get(self, url: str, pattern: str) -> Union[list, list[dict]]:
        """
        Méthode permettant de scrapper une page en fonction d'un motif.
        :param url: Ressource à scrapper
        :param pattern: Motif à rechercher dans la page
        :return: Liste contenant les éléments trouvés ou bien une liste vide.
        """
        if not isinstance(url, str) or not isinstance(pattern, str):
            raise ValueError("Les champs url et pattern doivent être des chaînes de caractères.")

        __request = self.__session.get(url)

        # Si la requête n'est pas ok, on lève une erreur.
        if not __request.ok:
            raise requests.ConnectionError("La ressource n'est pas accessible.")

        # On crée parse le contenu de la page.
        __soup = BeautifulSoup(__request.text, 'html.parser')

        # On cherche ce qui nous intéresse
        __data = []
        if script := __soup.find('script', string=lambda x: x and pattern in x):
            # On récupère le contenu de la variable JSONGlobalMesCommandes
            start_index = script.text.find('[{')
            end_index = script.text.find('}]') + 2
            json_content = script.text[start_index:end_index]

            # Charger le JSON en tant qu'objet Python
            __data = json.loads(json_content)

        return __data

    def orders(self) -> Union[list, list[dict]]:
        """
        Méthode qui permet de récupérer l'ensemble des commandes associées
        à un compte Showroom.
        :return: La liste des commandes ou une liste vide.
        """
        return self.__get(
            "https://www.showroomprive.com/moncompte/mescommandes.aspx",
            "OrderCtrl.JSONGlobalMesCommandes"
        )

    def items(self, order_id: int) -> Union[list, list[dict]]:
        """
        Méthode qui permet de récupérer la liste des articles associés à une commande.
        :param order_id: Identifiant de la commande
        :return: Liste des articles ou liste une liste vide
        """
        if not isinstance(order_id, int):
            raise ValueError("Le numéro de commande doit est un entier.")

        return self.__get(
            f"https://www.showroomprive.com/moncompte/CommandeDetail.aspx?comid={order_id}",
            "JsonOrder"
        )


if __name__ == "__main__":
    load_dotenv()
    email = os.getenv("SRP_EMAIL")
    password = os.getenv("SRP_PASSWORD")

    srp = ShowroomPriveAuthenticator(email, password)
    orders = srp.orders()
    # print(orders)
    # items = srp.items() # <- Entrer ici un numéro de commande
