import requests
import csv
import time
import json
from datetime import datetime


class NeteaseMusicCrawler:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
            'Referer': 'https://music.163.com/',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Origin': 'https://music.163.com'
        })

    def get_playlist_songs(self, playlist_id, limit=10):
        """获取歌单中的歌曲信息"""
        url = f'https://music.163.com/api/v6/playlist/detail?id={playlist_id}'

        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data.get('code', 200) != 200:
                raise ValueError(f"API返回错误: {data.get('message', '未知错误')}")

            songs = []
            for track in data['playlist']['tracks'][:limit]:
                song_info = {
                    'song_id': track['id'],
                    'song_name': track['name'],
                    'artists': ' / '.join([artist['name'] for artist in track['ar']]),
                    'artists_id': ' / '.join([str(artist['id']) for artist in track['ar']]),
                    'album': track['al']['name'],
                    'album_id': track['al']['id'],
                    'duration': f"{track['dt'] // 60000}:{str(track['dt'] % 60000 // 1000).zfill(2)}",
                    'popularity': track['pop'],
                    'publish_time': self._format_timestamp(track.get('publishTime')),
                    'copyright': '有' if track.get('copyright') == 1 else '无'
                }
                songs.append(song_info)
            return songs
        except Exception as e:
            print(f"获取歌单失败: {str(e)}")
            return None

    def get_song_lyrics(self, song_id):
        """获取歌曲歌词（含翻译和时间轴）"""
        url = f'https://music.163.com/api/song/lyric?id={song_id}&lv=-1&tv=-1'

        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data.get('code', 200) != 200:
                return f'歌词获取失败: {data.get("message", "未知错误")}'

            lyrics_data = []
            # 原歌词
            if 'lrc' in data and data['lrc'].get('lyric'):
                lyrics_data.append("[原歌词]")
                lyrics_data.append(data['lrc']['lyric'])

            # 翻译歌词
            if 'tlyric' in data and data['tlyric'].get('lyric'):
                lyrics_data.append("\n[翻译歌词]")
                lyrics_data.append(data['tlyric']['lyric'])

            # 逐字歌词
            if 'klyric' in data and data['klyric'].get('lyric'):
                lyrics_data.append("\n[逐字歌词]")
                lyrics_data.append(data['klyric']['lyric'])

            return '\\n'.join(lyrics_data) if lyrics_data else '暂无歌词'
        except Exception as e:
            print(f"获取歌词失败 (歌曲ID: {song_id}): {str(e)}")
            return '歌词获取失败'

    def _format_timestamp(self, timestamp):
        """格式化时间戳"""
        if not timestamp:
            return '未知'
        try:
            return datetime.fromtimestamp(timestamp / 1000).strftime('%Y-%m-%d')
        except:
            return '未知'

    def save_to_csv(self, songs_data, filename):
        """将数据保存为CSV文件"""
        try:
            with open(filename, 'w', encoding='utf-8-sig', newline='') as csvfile:
                fieldnames = [
                    'song_id', 'song_name', 'artists', 'artists_id',
                    'album', 'album_id', 'duration', 'popularity',
                    'publish_time', 'copyright', 'lyrics'
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                writer.writeheader()
                for song in songs_data:
                    writer.writerow(song)
            print(f"数据已成功保存到 {filename}")
            return True
        except Exception as e:
            print(f"保存文件失败: {str(e)}")
            return False


def main():
    crawler = NeteaseMusicCrawler()
    playlist_id = '629287734'  # 2025年歌单ID
    limit = 10  # 获取前10首歌曲

    print(f"开始获取2025年歌单 (ID: {playlist_id}) 的前 {limit} 首歌曲...")
    start_time = time.time()

    # 获取歌曲基本信息
    songs = crawler.get_playlist_songs(playlist_id, limit)
    if not songs:
        print("无法获取歌单信息，请检查网络连接或歌单ID是否正确")
        return

    print(f"成功获取 {len(songs)} 首歌曲基本信息，开始获取歌词...")

    # 获取歌词
    success_count = 0
    for i, song in enumerate(songs, 1):
        print(f"[{i}/{len(songs)}] 正在处理: {song['song_name']} - {song['artists']}")
        song['lyrics'] = crawler.get_song_lyrics(song['song_id'])
        if '失败' not in song['lyrics']:
            success_count += 1
        time.sleep(1.5)  # 礼貌性延迟，避免请求过快被限制

    # 保存结果
    filename = '2025年歌曲歌词.csv'
    if crawler.save_to_csv(songs, filename):
        end_time = time.time()
        print(f"任务完成! 成功获取 {success_count}/{len(songs)} 首歌曲的完整信息")
        print(f"总耗时: {end_time - start_time:.2f}秒")


if __name__ == '__main__':
    main()