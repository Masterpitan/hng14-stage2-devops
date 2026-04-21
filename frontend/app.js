const express = require('express');
const axios = require('axios');
const path = require('path');
const csrf = require('csurf');
const cookieParser = require('cookie-parser');

const app = express();
const API_URL = process.env.API_URL || 'http://localhost:8000';
const JOB_ID_REGEX = /^[0-9a-f-]{36}$/;

app.use(express.json());
app.use(cookieParser());
app.use(csrf({ cookie: true }));
app.use(express.static(path.join(__dirname, 'views')));

app.get('/csrf-token', (req, res) => {
  res.json({ csrfToken: req.csrfToken() });
});

app.post('/submit', async (req, res) => {
  try {
    const response = await axios.post(`${API_URL}/jobs`);
    res.json(response.data);
  } catch (err) {
    res.status(500).json({ error: 'something went wrong' });
  }
});

app.get('/status/:id', async (req, res) => {
  const { id } = req.params;
  if (!JOB_ID_REGEX.test(id)) {
    return res.status(400).json({ error: 'invalid job id' });
  }
  try {
    const response = await axios.get(`${API_URL}/jobs/${id}`);
    res.json(response.data);
  } catch (err) {
    res.status(500).json({ error: 'something went wrong' });
  }
});

app.listen(3000, () => console.log('Frontend running on port 3000'));
