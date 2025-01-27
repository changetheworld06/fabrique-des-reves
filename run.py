from flask import Flask, render_template, request
import openai
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Variables d'environnement
PAYPAL_CLIENT_ID = os.getenv("PAYPAL_CLIENT_ID")
PAYPAL_SECRET = os.getenv("PAYPAL_SECRET")
openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)

@app.route('/')
def home():
    """
    Page d'accueil avec le formulaire pour générer une histoire.
    """
    return render_template('index.html', paypal_client_id=PAYPAL_CLIENT_ID)

@app.route('/vision')
def vision():
    """
    Page expliquant la vision du projet.
    """
    return render_template('vision.html')

@app.route('/generate', methods=['POST'])
def generate():
    """
    Génère une histoire en fonction du prénom, des centres d'intérêt de l'enfant,
    et de la durée choisie.
    """
    child_name = request.form['child_name']
    interests = request.form['interests']
    story_length = request.form['story_length']

    # Définir les indications de longueur basées sur le choix de l'utilisateur
    if story_length == "courte":
        length_instruction = "Fais en sorte que l’histoire soit courte, environ 1-2 minutes."
    elif story_length == "moyenne":
        length_instruction = "Fais en sorte que l’histoire soit de durée moyenne, environ 3-4 minutes."
    elif story_length == "longue":
        length_instruction = "Fais en sorte que l’histoire soit longue, environ 5-6 minutes."

    # Prompt pour l'API OpenAI
    prompt = (
        f"Raconte une histoire magique pour un enfant nommé {child_name}, qui aime {interests}. "
        f"{length_instruction} Fais en sorte que l’histoire soit amusante et adaptée aux enfants."
    )

    try:
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
    except Exception as e:
        return render_template('story.html', story=f"Erreur : {e}", child_name=child_name)

if __name__ == '__main__':
    app.run(debug=True)
