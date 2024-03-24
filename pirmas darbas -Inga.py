from flask import Flask, render_template_string, jsonify, request, session, redirect, url_for
import random

app = Flask(__name__)
app.secret_key = 'your_very_secret_key'

scores_db = {}

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        session['player_name'] = request.form['name']
        return redirect(url_for('game_page'))
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="lt">
    <head>
        <meta charset="UTF-8">
        <title>Skaičių Šou</title>
        <style>
            body { background-color: #F0F8FF; font-family: 'Comic Neue', cursive; display: flex; justify-content: center; align-items: center; height: 100vh; flex-direction: column; }
            h1 { color: #FF6347; }
            input[type="text"], input[type="submit"] { border-radius: 5px; padding: 10px; border: 1px solid #ddd; margin: 5px; }
            input[type="submit"] { background-color: #4CAF50; color: white; cursor: pointer; }
            input[type="submit"]:hover { background-color: #45a049; }
            a { color: #6495ED; text-decoration: none; font-size: 18px; }
            a:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <div style="text-align: center;">
            <h1>Sveiki atvykę į Skaičių Šou</h1>
            <form method="post">
                <input type="text" name="name" required placeholder="Įveskite savo vardą">
                <input type="submit" value="Pradėti">
            </form>
            <br>
            <a href="{{ url_for('leaderboard') }}">Peržiūrėti lyderių lentelę</a>
        </div>
    </body>
    </html>
    ''')

@app.route('/game')
def game_page():
    if 'player_name' not in session:
        return redirect(url_for('home'))

    tasks = generate_tasks(10)
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="lt">
    <head>
        <meta charset="UTF-8">
        <title>Skaičių Šou</title>
        <style>
            body { font-family: 'Comic Neue', cursive; text-align: center; background-color: #FFFACD; }
            .task { margin-bottom: 20px; font-size: 20px; }
            input[type="number"] { padding: 10px; border-radius: 5px; border: 1px solid #ddd; }
            #submit { padding: 10px 20px; margin-top: 20px; background-color: #FFA07A; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 18px; }
            #submit:hover { background-color: #FA8072; }
            #score, #timer { margin-top: 20px; font-size: 20px; }
            a, #leaderboardLink { color: #6495ED; text-decoration: none; font-size: 18px; display: block; margin-top: 20px; }
            a:hover, #leaderboardLink:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <div>
            <h1>Skaičių Šou</h1>
            <div>
                <a href="/">Grįžti į pradžią</a>
            </div>
            <div id="timer">Liko laiko: <span id="time">120</span> sek.</div>
            <form id="gameForm">
                {% for task in tasks %}
                    <div class="task">
                        <label>{{ task.question }}</label>
                        <input type="number" name="answer{{ loop.index }}" step="any" required>
                    </div>
                {% endfor %}
                <button type="button" id="submit">Pateikti atsakymus</button>
            </form>
            <div id="score"></div>
            <a id="leaderboardLink" href="{{ url_for('leaderboard') }}">Peržiūrėti lyderių lentelę</a>
        </div>

        <script>
            let timeLeft = 120;
            const timerId = setInterval(() => {
                timeLeft--;
                document.getElementById('time').textContent = timeLeft;
                if (timeLeft <= 0) {
                    clearInterval(timerId);
                    document.getElementById('submit').click();
                }
            }, 1000);

            document.getElementById('submit').addEventListener('click', function() {
                clearInterval(timerId);
                let score = 0;
                const answers = [{{ tasks|map(attribute='answer')|join(', ') }}];
                for (let i = 0; i < answers.length; i++) {
                    let userAnswer = parseFloat(document.getElementsByName('answer' + (i + 1))[0].value);
                    if (userAnswer === answers[i]) {
                        score++;
                    }
                }

                const playerName = '{{ session["player_name"] }}';
                document.getElementById('score').innerText = playerName + ', jūsų rezultatas: ' + score + ' iš 10. Laikas: ' + (120 - timeLeft) + ' sek.';
                fetch('/score', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({name: playerName, score: score, time: 120 - timeLeft}),
                });
            });
        </script>
    </body>
    </html>
    ''', tasks=tasks)


@app.route('/score', methods=['POST'])
def save_score():
    data = request.get_json()
    scores_db[data['name']] = (data['score'], data['time'])
    return jsonify(success=True)

@app.route('/leaderboard')
def leaderboard():
    sorted_scores = sorted(scores_db.items(), key=lambda x: (x[1][0], -x[1][1]), reverse=True)
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="lt">
    <head>
        <meta charset="UTF-8">
        <title>Lyderių Lentelė</title>
        <style>
            body { font-family: 'Comic Neue', cursive; text-align: center; background-color: #E6E6FA; }
            h1 { color: #FF8C00; }
            ul { list-style-type: none; padding: 0; }
            li { background-color: #FFD700; margin: 5px 0; padding: 10px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);
font-size: 18px; }
            a { color: #6495ED; text-decoration: none; font-size: 18px; }
            a:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <div style="text-align: center;">
            <h1>Lyderių Lentelė</h1>
            <ul>
                {% for name, (score, time) in sorted_scores %}
                    <li>{{ name }}: {{ score }} taškai, laikas: {{ time }} sek.</li>
                {% endfor %}
            </ul>
            <a href="/">Grįžti į pradžią</a>
        </div>
    </body>
    </html>
    ''', sorted_scores=sorted_scores)
def generate_tasks(n):
    operations = ['+', '-', '*', '/']
    tasks = []
    for _ in range(n):
        num1 = random.randint(1, 10)
        num2 = random.randint(1, 10)
        operation = random.choice(operations)
        question = f"{num1} {operation} {num2}"
        answer = round(eval(question), 2)
        tasks.append({"question": question.replace('/', '÷'), "answer": answer})
    return tasks

if __name__ == "__main__":
    app.run(debug=True)