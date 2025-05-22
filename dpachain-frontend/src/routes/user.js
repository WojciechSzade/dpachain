const express = require('express');
const router = express.Router();
const { parseDiplomaSummary, parseDiplomaDetails } = require('../utils/parseDiploma');
const { API_BASE_URL } = require('../config');
const multer = require('multer');
const upload = multer({ storage: multer.memoryStorage() });
const { Blob } = require('buffer');

router.get('/', (req, res) => {
  res.render('user/index', { title: 'User Section' });
});

router.get('/validate_diploma', async (req, res) => {
  const { block_hash } = req.query;
  if (!block_hash) {
    return res.render('user/validate_diploma', { title: 'Validate a Diploma', apiBaseUrl: API_BASE_URL });
  }

  try {
    const apiRes = await fetch(
      `${API_BASE_URL}/user/get_block_by_hash?block_hash=${encodeURIComponent(block_hash)}`
    );
    const data = await apiRes.json();
    if (apiRes.status === 404) {
      return res.render('user/validate_diploma', {
        title: 'Validate a Diploma',
        error: { msg: "A diploma with specified hash doesn't exists" },
        apiBaseUrl: API_BASE_URL
      });
    }
    if (!apiRes.ok || !data.block) {
      const msg = data.detail || 'Error fetching diploma.';
      return res.render('user/validate_diploma', { title: 'Validate a Diploma', error: { msg }, apiBaseUrl: API_BASE_URL });
    }

    const summary = parseDiplomaSummary(data.block);
    const details = parseDiplomaDetails(data.block);
    res.render('user/validate_diploma', {
      title: 'Validate a Diploma',
      blockSummary: summary,
      blockDetails: details,
      apiBaseUrl: API_BASE_URL
    });
  } catch (error) {
    res.render('user/validate_diploma', {
      title: 'Validate a Diploma',
      error: { msg: error.message || 'Unexpected error' },
      apiBaseUrl: API_BASE_URL
    });
  }
});

module.exports = router;

router.post('/calculate_pdf_hash_local', upload.single('pdf_file'), async (req, res) => {
  if (!req.file) {
    return res.status(400).json({ error: 'PDF file is required.' });
  }

  try {
    const url = new URL('/user/calculate_pdf_hash', API_BASE_URL);

    const formData = new FormData();
    const pdfBlob = new Blob([req.file.buffer], { type: req.file.mimetype });
    formData.append('pdf_file', pdfBlob, req.file.originalname);

    const apiRes = await fetch(url.toString(), {
      method: 'POST',
      body: formData
    });
    const data = await apiRes.json();

    if (!apiRes.ok) {
      return res.status(400).json(data);
    }

    res.json(data);
  } catch (error) {
    res.status(500).json({ error: error.message || 'Unexpected error' });
  }
});