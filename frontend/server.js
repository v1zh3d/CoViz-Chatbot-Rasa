var express= require('express');
const app = express();
var path = require('path');
const server = require('http').createServer(app);
var cors = require('cors');
const PORT = process.env.PORT || 3000;
server.listen(PORT);
console.log(`Server is running on port ${PORT}`);

app.use(cors());
app.use(express.static(path.join(__dirname, 'static')));

app.get('/', (req, res) => {
    res.sendFile(__dirname + '/index.html');
 });