from flask import Flask, render_template, request, jsonify, redirect, url_for
import subprocess
import yt_dlp as youtube_dl

app = Flask(__name__)

# 전역 상태 변수
playlist = []
current_song = None

@app.route('/')
def home():
    return redirect(url_for('chat'))  # 채팅 페이지로 리디렉션

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if request.method == 'POST':
        command = request.form['command']  # 사용자가 입력한 명령어
        response = handle_command(command)  # 명령어 처리
        return response  # JSON 형식으로 응답 반환
    return render_template('chat.html')  # GET 요청 시 HTML 페이지 반환

def handle_command(command):
    global current_song
    global playlist
    
    command = command.lower()
    
    print(f"Received command: {command}")  # 콘솔에 명령어 출력

    if command.startswith("play "):
        song_name = command[5:]  # "play " 이후의 곡명 추출
        playlist.append(song_name)  # 플레이리스트에 추가
        if current_song is None:
            current_song = song_name  # 현재 곡으로 설정
            response = play_song(song_name)  # 실제 곡 재생 함수 호출
            return jsonify({'response': response, 'current_song': current_song, 'playlist': playlist})
        else:
            return jsonify({'response': f"'{song_name}'이(가) 플레이리스트에 추가되었습니다.", 'current_song': current_song, 'playlist': playlist})
    
    elif command == "pause":
        pause_song()  # 음악 일시정지 함수 호출
        return jsonify({'response': "음악을 일시정지합니다.", 'current_song': current_song, 'playlist': playlist})
    
    elif command == "resume":
        resume_song()  # 음악 재개 함수 호출
        return jsonify({'response': "음악을 재개합니다.", 'current_song': current_song, 'playlist': playlist})
    
    elif command == "stop":
        stop_song()  # 음악 중지 함수 호출
        current_song = None
        playlist.clear()  # 플레이리스트 초기화
        return jsonify({'response': "음악을 중지하였습니다.", 'current_song': None, 'playlist': playlist})
    
    elif command == "skip":
        if playlist:
            current_song = playlist.pop(0)  # 다음 곡으로 넘어감
            response = play_song(current_song)  # 실제 곡 재생 함수 호출
            return jsonify({'response': response, 'current_song': current_song, 'playlist': playlist})
        else:
            current_song = None
            return jsonify({'response': "재생할 곡이 없습니다.", 'current_song': None, 'playlist': playlist})
    
    elif command == "playlist":
        if not playlist:
            return jsonify({'response': "플레이리스트가 비어 있습니다.", 'current_song': current_song, 'playlist': playlist})
        response = "현재 재생 중인 곡: " + (current_song if current_song else "없음") + "\n"
        response += "플레이리스트:\n"
        for idx, song in enumerate(playlist):
            response += f"{idx + 1}: {song}\n"
        return jsonify({'response': response.strip(), 'current_song': current_song, 'playlist': playlist})
    
    elif command.startswith("delete "):
        try:
            index = int(command[7:]) - 1  # "delete " 이후의 번호 추출
            if 0 <= index < len(playlist):
                removed_song = playlist.pop(index)
                return jsonify({'response': f"'{removed_song}'이(가) 플레이리스트에서 삭제되었습니다.", 'current_song': current_song, 'playlist': playlist})
            else:
                return jsonify({'response': "유효하지 않은 번호입니다.", 'current_song': current_song, 'playlist': playlist})
        except ValueError:
            return jsonify({'response': "번호를 올바르게 입력하세요.", 'current_song': current_song, 'playlist': playlist})
    
    else:
        return jsonify({'response': "알 수 없는 명령어입니다. 'play [곡명]', 'pause', 'resume', 'stop', 'skip', 'playlist', 'delete [번호]' 명령어를 사용하세요.", 'current_song': current_song, 'playlist': playlist})

def play_song(song_name):
    # 유튜브에서 비디오 검색 후 재생
    video_url = search_youtube(song_name)
    if video_url:
        print(f"Playing: {video_url}")  # 재생할 URL 콘솔에 출력
        result = subprocess.run(["cvlc", video_url], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # 재생 결과 확인
        if result.returncode != 0:
            error_message = result.stderr.decode().strip()
            print(f"Error: {error_message}")  # 오류 메시지 콘솔에 출력
            return "기기 연결 실패: 음악을 재생할 수 없습니다."
        
        return f"'{song_name}'을(를) 재생하고 있습니다."
    else:
        return "유튜브에서 비디오를 찾을 수 없습니다."

def search_youtube(song_name):
    # youtube-dl을 사용하여 유튜브에서 비디오 검색
    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'quiet': True
    }
    
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        try:
            search_query = f"ytsearch:{song_name}"  # 검색 쿼리 생성
            info = ydl.extract_info(search_query, download=False)  # 다운로드 하지 않고 정보 추출
            video_url = info['entries'][0]['url']  # 첫 번째 결과의 URL 반환
            return video_url
        except Exception as e:
            print(f"Error: {e}")
            return None

def pause_song():
    # VLC 프로세스를 일시정지
    subprocess.run(["pkill", "-STOP", "vlc"])  # VLC 프로세스를 일시정지

def resume_song():
    # VLC 프로세스를 재개
    subprocess.run(["pkill", "-CONT", "vlc"])  # VLC 프로세스를 재개

def stop_song():
    # VLC 프로세스 종료
    subprocess.run(["pkill", "vlc"])  # VLC 프로세스 종료

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)  # 모든 IP에서 접근 가능
