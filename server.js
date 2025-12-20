const express = require('express');
const AWS = require('aws-sdk');
const cors = require('cors');
const bodyParser = require('body-parser');
require('dotenv').config();
const path = require('path');

const app = express();

app.use(cors());
app.use(bodyParser.json());
app.use(express.static(path.join(__dirname, 'public')));

app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

let users = [];

function generateToken() {
    return Math.random().toString(36).substring(2);
}

app.post('/login', (req, res) => {
    const { username, password } = req.body;
    const user = users.find(u => u.username === username && u.password === password);
    if (!user) return res.status(401).json({ error: "Invalid Login" });

    const token = generateToken();
    user.sessionToken = token;
    res.json({ sessionToken: token, username: user.username, role: user.role });
});

app.post('/register', (req, res) => {
    const { username, password, role } = req.body;
    if (!username || !password || !role) return res.status(400).json({ error: "Missing username, password or role" });

    if (users.some(u => u.username === username)) {
        return res.status(400).json({ error: "Username already exists" });
    }

    const token = generateToken();
    const newUser = { username, password, role, sessionToken: token };
    users.push(newUser);
    res.json({ sessionToken: token, username, role });
});

app.get('/profile', (req, res) => {
    const token = req.headers.authorization;
    const user = users.find(u => u.sessionToken === token);
    if (!user) return res.status(401).json({ error: "You are not logged in" });

    res.json({ username: user.username, role: user.role });
});

app.post('/update-profile', (req, res) => {
    const token = req.headers.authorization;
    const user = users.find(u => u.sessionToken === token);
    if (!user) return res.status(401).json({ error: "You are not logged in" });

    const { username, role } = req.body;
    if (username) user.username = username;
    if (role) user.role = role;

    res.json({ success: true, username: user.username, role: user.role });
});


const s3 = new AWS.S3({
    accessKeyId: process.env.AWS_ACCESS_KEY,
    secretAccessKey: process.env.AWS_SECRET_KEY,
    region: process.env.AWS_REGION
});

app.get('/upload', (req, res) => {
    const { fileName } = req.query;
    if (!fileName) return res.status(400).json({ error: "you are missing filename" });

    const params = {
        Bucket: process.env.S3_BUCKET,
        Key: fileName,
        Expires: 60,
        ContentType: 'text/csv'
    };

    s3.getSignedUrl('putObject', params, (err, url) => {
        if (err) return res.status(500).json({ error: err.message });
        res.json({ uploadURL: url });
    });
});

const PORT = process.env.PORT || 3008;
app.listen(PORT, () => console.log(`Server running on http://localhost:${PORT}`));
