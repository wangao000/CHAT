from aip import AipSpeech

""" 你的 APPID AK SK """
APP_ID = '82135857'
API_KEY = 'hfqtzNqqLhFbqse429WIk8m1'
SECRET_KEY = 'k6AcYL0psc2dylRI2duU5I8ppiBcD2Oi'

client = AipSpeech(APP_ID, API_KEY, SECRET_KEY)
def get_file_content(filePath):
    with open(filePath, 'rb') as fp:
        return fp.read()

# 识别本地文件
def speech2text(audio_path):
    result = client.asr(get_file_content(audio_path), 'wav', 16000, {
        'dev_pid': 1537,
    })
    if result['err_no'] == 0:
        return result['result'][0],True
    else:
        return result,False