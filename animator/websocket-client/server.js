const WebSocket = require('ws')
const wss= new WebSocket.Server({ port: 8000 },()=>{
    console.log('서버 시작')
})

wss.on('connection', function connection(ws) {
   ws.on('message', (data) => {
      console.log('받은 데이터 : %s', data)
      ws.send(data);
   })
})

wss.on('listening',()=>{
   console.log('리스닝 ...')
})