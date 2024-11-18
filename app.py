from flask import Flask, render_template, request, jsonify, redirect, url_for

app = Flask(__name__)

playlist = []
current_song = None

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

def handle_command(command):
    global current_song
    global playlist
    
    command = command.lower()
    
    if command.startswith("play "):
        song_name = command[5:]  # "play " 이후의 곡명 추출
        playlist.append(song_name)  # 플레이리스트에 추가
        if current_song is None:
            current_song = song_name  # 현재 곡으로 설정
            return f"'{song_name}'을(를) 재생하고 있습니다."
        else:
            return f"'{song_name}'이(가) 플레이리스트에 추가되었습니다."
    
    elif command == "pause":
        return "음악을 일시정지합니다."
    
    elif command == "resume":
        return "음악을 재개합니다."
    
    elif command == "stop":
        current_song = None
        playlist.clear()  # 플레이리스트 초기화
        return "음악을 중지하였습니다."
    
    elif command == "skip":
        if playlist:
            current_song = playlist.pop(0)  # 다음 곡으로 넘어감
            return f"'{current_song}'을(를) 재생하고 있습니다."
        else:
            current_song = None
            return "재생할 곡이 없습니다."
    
    elif command == "playlist":
        if not playlist:
            return "플레이리스트가 비어 있습니다."
        response = "현재 재생 중인 곡: " + (current_song if current_song else "없음") + "\n"
        response += "플레이리스트:\n"
        for idx, song in enumerate(playlist):
            response += f"{idx + 1}: {song}\n"
        return response.strip()
    
    elif command.startswith("delete "):
        try:
            index = int(command[7:]) - 1  # "delete " 이후의 번호 추출
            if 0 <= index < len(playlist):
                removed_song = playlist.pop(index)
                return f"'{removed_song}'이(가) 플레이리스트에서 삭제되었습니다."
            else:
                return "유효하지 않은 번호입니다."
        except ValueError:
            return "번호를 올바르게 입력하세요."
    
    else:
        return "알 수 없는 명령어입니다. 'play [곡명]', 'pause', 'resume', 'stop', 'skip', 'playlist', 'delete [번호]' 명령어를 사용하세요."


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
