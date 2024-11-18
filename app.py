from flask import Flask, render_template, request, jsonify, redirect, url_for

app = Flask(__name__)

@app.route('/')
def home():
    return redirect(url_for('chat'))  # 채팅 페이지로 리디렉션

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if request.method == 'POST':
        command = request.form['command']
        # 여기서 명령어를 처리하는 로직을 추가하세요.
        response = f"명령어 '{command}'이(가) 수신되었습니다."
        return jsonify({'response': response})
    return render_template('chat.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
