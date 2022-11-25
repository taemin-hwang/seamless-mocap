const express = require('express');
var compression  = require('compression');
const app = express();
const path = require('path')

app.use(compression());
app.use(express.static(path.join(__dirname, '/WebGL')));

const HTTPServer = app.listen(30001, ()=>{
    console.log("Server is open at port:30001");
});

const wsModule = require('ws');

// 2. WebSocket 서버 생성/구동
var wss = new wsModule.Server({
    server: HTTPServer, // WebSocket서버에 연결할 HTTP서버를 지정한다.
    // port: 30002 // WebSocket연결에 사용할 port를 지정한다(생략시, http서버와 동일한 port 공유 사용)
});


// Broadcast to all.
wss.broadcast = function broadcast(data) {
    wss.clients.forEach(function each(client) {
        client.send(data);
    });
};

wss.on('connection', (ws, request)=>{
    // 1) 연결 클라이언트 IP 취득
    const ip = request.headers['x-forwarded-for'] || request.connection.remoteAddress;

    console.log(`새로운 클라이언트[${ip}] 접속`);

    // 2) 클라이언트에게 메시지 전송
    if(ws.readyState === ws.OPEN){ // 연결 여부 체크
        ws.send(`클라이언트[${ip}] 접속을 환영합니다 from 서버`); // 데이터 전송
    }

    // 3) 클라이언트로부터 메시지 수신 이벤트 처리
    ws.on('message', (msg)=>{
        console.log(`클라이언트[${ip}]에게 수신한 메시지 : ${msg}`);
        ws.send('메시지 잘 받았습니다! from 서버')
        wss.broadcast(msg);
    })

    // 4) 에러 처러
    ws.on('error', (error)=>{
        console.log(`클라이언트[${ip}] 연결 에러발생 : ${error}`);
    })

    // 5) 연결 종료 이벤트 처리
    ws.on('close', ()=>{
        console.log(`클라이언트[${ip}] 웹소켓 연결 종료`);
    })
});
