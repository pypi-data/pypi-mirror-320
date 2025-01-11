#!/usr/bin/python
import requests
import sys

def search_for_songs():
    # 1. 获取用户输入
    query = input("请输入查询关键词: ")
    
    # 2. 发送请求到API
    url = "https://api.csm.sayqz.com/search"
    params = {'keywords': query}
    response = requests.get(url, params=params)
    
    # 3. 将获取的数据转为字典
    responseMap = response.json()

    # 4. 遍历responseMap中的'result'下的'songs'列表
    if 'result' in responseMap and 'songs' in responseMap['result']:
        songs = responseMap['result']['songs']
        music_list = {}
        i = 1
        for song in songs:
            music_list[i] = [song['id'],song['name'],song['artists'][0]['name'],song['album']['name'],song['album']['id']]
            print("["+str(i)+"]", "歌名:", music_list[i][1], "歌手:", music_list[i][2], "专辑:", music_list[i][3])
            i+=1
        return music_list
    else:
        print("抱歉，没有找到歌曲信息。")
        sys.exit()

def detect_lyric(id,filename):
    response = requests.get("https://api.csm.sayqz.com/lyric",params={"id":id})
    if response.status_code == 200:
        data = response.json()
        if "lrc" in data and "lyric" in data['lrc']:
            opt = input("确认下载此歌曲的歌词吗？[y/N]")
            if opt == "y" or opt == "Y":
                with open(filename+".lrc","w") as f:
                    f.write(data['lrc']['lyric'].replace("\n","\n"))
                    print(f"歌词已下载并保存为：{filename}.lrc")
        else:
            print("抱歉，此歌曲暂无歌词")

def get_filename(filename):
    # 检查文件名是否以.mp3结尾
    if filename.endswith('.mp3'):
        new_filename = filename[:-4]
        return new_filename

def download(music_list):
    order = int(input('请输入序号:'))
    filename = sys.argv[1]
    detect_lyric(music_list[order][0],get_filename(filename))

def main():
    try:
        print("欢迎使用Orchestraw 歌词下载器!")
        music_list = search_for_songs()
        download(music_list)
    except KeyboardInterrupt:
        print('脚本已退出')
    except EOFError:
        print('脚本已退出')
    except Exception as e:
        print('脚本意外退出: ',e)

if __name__ == '__main__':
    main()