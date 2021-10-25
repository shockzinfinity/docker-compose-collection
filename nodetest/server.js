var express = require('express')
var app = express()

app.get('/', function(req, res) {
  res.send('Hi there')
})

app.listen(3000, function() {
  console.log('앱이 3000번 포트에서 실행중입니다....')
})