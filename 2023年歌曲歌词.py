import requests
import csv
import time


def get_playlist_songs(playlist_id, limit=10):
    """获取歌单中的歌曲信息"""
    url = f'https://music.163.com/api/v6/playlist/detail?id={playlist_id}'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
        'Referer': 'https://music.163.com/',
        'Accept': 'application/json'
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()

        songs = []
        for track in data['playlist']['tracks'][:limit]:
            song_info = {
                'song_id': track['id'],
                'song_name': track['name'],
                'artists': ' / '.join([artist['name'] for artist in track['ar']]),
                'album': track['al']['name'],
                'duration': f"{track['dt'] // 60000}:{str(track['dt'] % 60000 // 1000).zfill(2)}",
                'popularity': track['pop']  # 新增歌曲热度指标
            }
            songs.append(song_info)
        return songs
    except Exception as e:
        print(f"获取歌单失败: {str(e)}")
        return None


def get_song_lyrics(song_id):
    """获取歌曲歌词（含翻译）"""
    url = f'https://music.163.com/api/song/lyric?id={song_id}&lv=-1&tv=-1'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
        'Referer': f'https://music.163.com/song?id={song_id}'
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()

        # 处理歌词
        lrc = data.get('lrc', {}).get('lyric', '暂无歌词')
        tlyric = data.get('tlyric', {}).get('lyric', '')

        # 合并歌词和翻译
        full_lyrics = lrc
        if tlyric:
            full_lyrics += f"\n\n------翻译------\n{tlyric}"

        return full_lyrics.replace('\n', '\\n')  # 替换换行符以便CSV存储
    except Exception as e:
        print(f"获取歌词失败 (歌曲ID: {song_id}): {str(e)}")
        return '歌词获取失败'


def save_to_csv(songs_data, filename):
    """将数据保存为CSV文件"""
    with open(filename, 'w', encoding='utf-8-sig', newline='') as csvfile:
        fieldnames = ['song_id', 'song_name', 'artists', 'album', 'duration', 'popularity', 'lyrics']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for song in songs_data:
            writer.writerow(song)
    print(f"数据已成功保存到 {filename}")


def main():
    playlist_id = '2732037290'  # 2023年歌单ID
    limit = 10  # 获取前10首歌曲

    print(f"开始获取歌单 {playlist_id} 的前 {limit} 首歌曲...")
    songs = get_playlist_songs(playlist_id, limit)

    if not songs:
        print("无法获取歌单信息，请检查网络或歌单ID是否正确")
        return

    print(f"成功获取 {len(songs)} 首歌曲信息，开始获取歌词...")
    for i, song in enumerate(songs, 1):
        print(f"正在处理第 {i} 首: {song['song_name']} - {song['artists']}")
        song['lyrics'] = get_song_lyrics(song['song_id'])
        time.sleep(0.8)  # 礼貌性延迟，避免请求过快

    # 保存为CSV文件
    filename = '2023年歌曲歌词.csv'
    save_to_csv(songs, filename)
    print("所有歌曲信息及歌词已获取完成！")


if __name__ == '__main__':
    main()