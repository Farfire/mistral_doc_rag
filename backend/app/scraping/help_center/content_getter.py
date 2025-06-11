import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import time
from colorama import Fore, Style


def get_content_from_url(url: str) -> tuple[str, str]:
    """
    Récupère le contenu textuel d'une page du help center de Mistral.
    
    Args:
        url (str): L'URL de la page du help center (ex: https://help.mistral.ai/en/articles/...)
        
    Returns:
        str: Le contenu textuel de la page, ou une chaîne vide en cas d'erreur
    """
    try:
        # Vérifier que c'est bien une URL du help center de Mistral
        parsed_url = urlparse(url)
        if not parsed_url.netloc == "docs.mistral.ai":
            raise ValueError("L'URL doit être une page du help center de Mistral")
            
        # Ajouter un User-Agent pour éviter d'être bloqué
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Lève une exception si erreur HTTP
        
        # Parser le HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Trouver le contenu principal
        # Le contenu est généralement dans un article ou une div avec une classe spécifique
        content = soup.find()
        
        if not content:
            print("Contenu principal non trouvé dans la page")
            return "", ""
            
        # Extraire le texte en préservant la structure
        text_content = []
        
        # Titre
        title = content.find('h1')
        if title:
            text_content.append(title.get_text())
            text_content.append("\n")
            
        # print('tiiiiiiitle', text_content)
        
        # Sous-titres et paragraphes
        elements = content.find_all()
        VALID_TAGS = ['p', 'h1', 'h2', 'h3', 'ul', 'ol', 'code']

        for element in elements:
            if element.get_text().startswith('Text generation, enables streaming and provides'):
                break
                
            if element.get_text().startswith('Getting StartedIntroductionQuickstar'):
                continue
            
            # if element.name in VALID_TAGS:
            #     print(f'{Fore.GREEN if element.name in VALID_TAGS else Fore.RED}{element.name} ???? {element.get_text()}{Style.RESET_ALL}')
            
            if element.name in ['h2', 'h3']:
                text_content.append("\n" + element.get_text())
            elif element.name == 'p':
                text_content.append(element.get_text())
            elif element.name in ['ul', 'ol']:
                for li in element.find_all('li'):
                    text_content.append("• " + li.get_text())
            elif element.name in ['pre', 'code']:
                code_text = element.get_text()
                text_content.append(code_text)
                    
        return title.get_text(), "\n".join(text_content)
        
    except requests.RequestException as e:
        print(f"Erreur lors de la requête HTTP: {e}")
        return "", ""
    except Exception as e:
        print(f"Erreur inattendue: {e}")
        return "", ""

# Exemple d'utilisation
if __name__ == "__main__":
    url = "https://help.mistral.ai/en/articles/316419-how-do-i-connect-google-drive-to-le-chat-beta"
    content = get_content_from_url(url)
    print("\nContenu extrait:")
    print("-" * 50)
    print(content)
    print("-" * 50) 