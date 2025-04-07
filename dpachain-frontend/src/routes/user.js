const express = require('express');
const router = express.Router();
const parseDiploma = require('../utils/parseDiploma');

// User index page with links to user actions
router.get('/', (req, res) => {
  res.render('user/index', { title: 'User Section' });
});

// GET page for "Validate a diploma"
router.get('/validate_diploma', (req, res) => {
  res.render('user/validate_diploma', { title: 'Validate a Diploma', block: null });
});

// POST handler for "Validate a diploma"
router.post('/validate_diploma', async (req, res) => {
  const { block_hash } = req.body;
  try {
    const apiRes = await fetch(`http://localhost:8000/user/get_block_by_hash?block_hash=${encodeURIComponent(block_hash)}`, {
      method: 'GET'
    });
    const data = await apiRes.json();
    // Use the helper to parse the diploma data into a structured format
    const block = parseDiploma(data);
    res.render('user/validate_diploma', { title: 'Validate a Diploma', block });
  } catch (error) {
    res.render('user/validate_diploma', { title: 'Validate a Diploma', block: [{ label: 'Error', value: error.message }] });
  }
});

module.exports = router;
