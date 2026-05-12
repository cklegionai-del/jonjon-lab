const express = require('express');
const cors = require('cors');
const { exec } = require('child_process');
const path = require('path');
const app = express();

app.use(cors());
app.use(express.static('public'));
app.use(express.json());

app.get('/api/recommend', (req, res) => {
    const query = req.query.q || 'قهوة تونسية أصيلة';
    exec(`ollama run qwen3-coder "اقترح منتج قهوة تونسي لـ: ${query}"`, {timeout: 10000}, (err, stdout) => {
        if (err) return res.json({error: 'Ollama error', stdout: stdout});
        res.json({recommendation: stdout.trim()});
    });
});

app.get('*', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`☕ زيزوى يعمل على http://localhost:${PORT}`);
});
