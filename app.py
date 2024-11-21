from flask import Flask, render_template, request, jsonify, redirect, url_for
import subprocess
import youtube_dl

app = Flask(__name__)

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
        return jsonify({'response': response})  # JSON 형식으로 응답 반환
    return render_template('chat.html')  # GET 요청 시 HTML 페이지 반환

def handle_command(command):
    global current_song
    global playlist
    
    command = command.lower()
    
    if command.startswith("play "):
        song_name = command[5:]  # "play " 이후의 곡명 추출
        playlist.append(song_name)  # 플레이리스트에 추가
        if current_song is None:
            current_song = song_name  # 현재 곡으로 설정
            play_song(song_name)  # 실제 곡 재생 함수 호출
            return f"'{song_name}'을(를) 재생하고 있습니다."
        else:
            return f"'{song_name}'이(가) 플레이리스트에 추가되었습니다."
    
    elif command == "pause":
        pause_song()  # 음악 일시정지 함수 호출
        return "음악을 일시정지합니다."
    
    elif command == "resume":
        resume_song()  # 음악 재개 함수 호출
        return "음악을 재개합니다."
    
    elif command == "stop":
        stop_song()  # 음악 중지 함수 호출
        current_song = None
        playlist.clear()  # 플레이리스트 초기화
        return "음악을 중지하였습니다."
    
    elif command == "skip":
        if playlist:
            current_song = playlist.pop(0)  # 다음 곡으로 넘어감
            play_song(current_song)  # 실제 곡 재생 함수 호출
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

def play_song(song_name):
    # 유튜브에서 비디오 검색 후 재생
    video_url = search_youtube(song_name)
    if video_url:
        subprocess.run(["cvlc", video_url])  # VLC로 비디오 URL 재생
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
