from flask import Flask, render_template, request, redirect, url_for, flash
from gtts import gTTS
from datetime import datetime
import csv
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

CSV_FILE = os.path.join(os.path.dirname(__file__), 'responses.csv')
VOICE_FILE = os.path.join('static', 'voice.mp3')

@app.route('/', methods=['GET', 'POST'])
def career_form():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        drawing = request.form.get('drawing', 'No')
        dancing = request.form.get('dancing', 'No')
        singing = request.form.get('singing', 'No')
        coding = request.form.get('coding', 'No')
        sports = request.form.get('sports', 'No')
        photography = request.form.get('photographer', 'No')

        if not name:
            flash("Name is required!", "error")
            return redirect(url_for('career_form'))

        save_to_csv([name, drawing, dancing, singing, coding, sports, photography])

        interests = {
            "drawing": drawing == "Yes",
            "dancing": dancing == "Yes",
            "singing": singing == "Yes",
            "coding": coding == "Yes",
            "sports": sports == "Yes",
            "photographer": photography == "Yes"
        }

        suggestions = get_career_suggestions(interests)

        message = f"Thanks {name}, based on your interests, you could become: {', '.join(suggestions)}!"
        flash(message, "success")

        tts = gTTS(message)
        tts.save(VOICE_FILE)

        return redirect(url_for('career_form'))

    # Send current timestamp to force audio reload
    return render_template('form.html', timestamp=datetime.utcnow().timestamp())

@app.route('/responses')
def show_responses():
    responses = []
    if os.path.isfile(CSV_FILE):
        with open(CSV_FILE, newline='') as file:
            reader = csv.reader(file)
            responses = list(reader)
    return render_template('responses.html', responses=responses)

def save_to_csv(data):
    file_exists = os.path.isfile(CSV_FILE)
    with open(CSV_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(['Name', 'Drawing', 'Dancing', 'Singing', 'Coding', 'Sports', 'Photographer'])
        writer.writerow(data)

def get_career_suggestions(interests):
    suggestions = []
    if interests["drawing"] and interests["coding"]:
        suggestions.append("UI/UX Designer")
    if interests["drawing"]:
        suggestions.append("Graphic Designer")
    if interests["dancing"] and interests["singing"]:
        suggestions.append("Performer or Stage Artist")
    if interests["dancing"]:
        suggestions.append("Choreographer")
    if interests["singing"]:
        suggestions.append("Vocal Artist")
    if interests["coding"] and interests["sports"]:
        suggestions.append("Game Developer")
    if interests["coding"]:
        suggestions.append("Software Developer")
    if interests["sports"]:
        suggestions.append("Athlete or Fitness Coach")
    if interests["photographer"]:
        suggestions.append("Photographer or News Reporter")
    if not suggestions:
        suggestions.append("Creative Professional")
    return suggestions

if __name__ == '__main__':
    if not os.path.exists('static'):
        os.makedirs('static')

    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
