import requests
import csv
import time


def get_playlist_songs(playlist_id, limit=10):
    """获取歌单中的歌曲信息"""
    url = f'https://music.163.com/api/v6/playlist/detail?id={playlist_id}'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
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
                'artists': ', '.join([artist['name'] for artist in track['ar']]),
                'album': track['al']['name']
            }
            songs.append(song_info)
        return songs
    except Exception as e:
        print(f"获取歌单失败: {e}")
        return None


def get_song_lyrics(song_id):
    """获取歌曲歌词"""
    url = f'https://music.163.com/api/song/lyric?id={song_id}&lv=1'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()

        # 获取歌词文本
        lyrics = data.get('lrc', {}).get('lyric', '暂无歌词')
        return lyrics.replace('\n', '\\n')  # 替换换行符以便CSV存储
    except Exception as e:
        print(f"获取歌词失败 (歌曲ID: {song_id}): {e}")
        return '获取歌词失败'


def save_to_csv(songs_data, filename):
    """将数据保存为CSV文件"""
    with open(filename, 'w', encoding='utf-8-sig', newline='') as csvfile:
        fieldnames = ['song_id', 'song_name', 'artists', 'album', 'lyrics']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for song in songs_data:
            writer.writerow(song)
    print(f"数据已保存到 {filename}")


def main():
    playlist_id = '7351366698'  # 歌单ID
    limit = 10  # 获取前10首歌曲

    print(f"正在获取歌单 {playlist_id} 的前 {limit} 首歌曲...")
    songs = get_playlist_songs(playlist_id, limit)

    if not songs:
        print("无法获取歌单信息，程序终止")
        return

    print("正在获取每首歌曲的歌词...")
    for song in songs:
        song['lyrics'] = get_song_lyrics(song['song_id'])
        time.sleep(1)  # 添加延迟避免请求过于频繁

    # 保存为CSV文件
    filename = '2022年歌曲歌词.csv'
    save_to_csv(songs, filename)


if __name__ == '__main__':
    main()