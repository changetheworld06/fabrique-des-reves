from flask import Flask, render_template, request
import openai
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Charger les variables sensibles
PAYPAL_CLIENT_ID = os.getenv("PAYPAL_CLIENT_ID", "ID_PAYPAL_INDISPONIBLE")
PAYPAL_SECRET = os.getenv("PAYPAL_SECRET", "SECRET_PAYPAL_INDISPONIBLE")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Vérification de la clé OpenAI
if not OPENAI_API_KEY:
    raise ValueError("La clé API OpenAI (OPENAI_API_KEY) n'est pas configurée. Veuillez la définir dans le fichier .env.")

# Configurer l'API OpenAI
openai.api_key = OPENAI_API_KEY

# Initialisation de l'application Flask
app = Flask(__name__)

@app.route('/')
def home():
    """
    Page d'accueil avec le formulaire pour générer une histoire.
    """
    return render_template('index.html', paypal_client_id=PAYPAL_CLIENT_ID)

@app.route('/generate', methods=['POST'])
def generate():
    """
    Génère une histoire en fonction du prénom, des centres d'intérêt de l'enfant,
    et de la durée choisie.
    """
    try:
        # Récupérer les données du formulaire
        child_name = request.form.get('child_name', '').strip()
        interests = request.form.get('interests', '').strip()
        story_length = request.form.get('story_length', 'courte')

        # Valider les champs du formulaire
        if not child_name or not interests:
            return render_template(
                'story.html',
                story="Veuillez renseigner tous les champs du formulaire.",
                child_name=child_name
            )

        # Définir les instructions de longueur
        if story_length == "courte":
            length_instruction = "Fais en sorte que l’histoire soit courte, environ 1-2 minutes."
        elif story_length == "moyenne":
            length_instruction = "Fais en sorte que l’histoire soit de durée moyenne, environ 3-4 minutes."
        elif story_length == "longue":
            length_instruction = "Fais en sorte que l’histoire soit longue, environ 5-6 minutes."
        else:
            length_instruction = "Fais en sorte que l’histoire soit de longueur moyenne."

        # Prompt pour l'API OpenAI
        prompt = (
            f"Raconte une histoire magique pour un enfant nommé {child_name}, qui aime {interests}. "
            f"{length_instruction} Fais en sorte que l’histoire soit amusante et adaptée aux enfants."
        )

        # Appel à l'API OpenAI pour générer l'histoire
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Tu es un créateur d'histoires pour enfants."},
                {"role": "user", "content": prompt}
            ]
        )
        story = response['choices'][0]['message']['content']
        return render_template('story.html', story=story, child_name=child_name)

    except openai.error.OpenAIError as e:
        # Gestion des erreurs spécifiques à OpenAI
        return render_template(
            'story.html',
            story=f"Une erreur s'est produite avec l'API OpenAI : {e}",
            child_name=""
        )
    except Exception as e:
        # Gestion générale des erreurs
        return render_template(
            'story.html',
            story=f"Une erreur inattendue s'est produite : {e}",
            child_name=""
        )

if __name__ == '__main__':
    app.run(debug=True)