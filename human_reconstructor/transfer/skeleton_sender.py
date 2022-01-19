from easymocap.socket.base_client import BaseSocketClient

client = BaseSocketClient('127.0.0.1', 9999)

def send_3d_skeletons(skeletons):
    data = []
    data.append({})
    data[0]['id'] = 0
    data[0]['keypoints3d'] = skeletons
    client.send(data)