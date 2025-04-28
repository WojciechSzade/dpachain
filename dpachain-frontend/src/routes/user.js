const express = require('express');
const router = express.Router();
const { parseDiplomaSummary, parseDiplomaDetails } = require('../utils/parseDiploma');
const { API_BASE_URL } = require('../config');

router.get('/', (req, res) => {
  res.render('user/index', { title: 'User Section' });
});

router.get('/validate_diploma', async (req, res) => {
  const { block_hash } = req.query;
  if (!block_hash) {
    return res.render('user/validate_diploma', { title: 'Validate a Diploma' });
  }

  try {
    const apiRes = await fetch(
      `${API_BASE_URL}/user/get_block_by_hash?block_hash=${encodeURIComponent(block_hash)}`
    );
    const data = await apiRes.json();
    if (!apiRes.ok || !data.block) {
      const msg = data.detail || 'Error fetching diploma.';
      return res.render('user/validate_diploma', { title: 'Validate a Diploma', error: { msg } });
    }

    const summary = parseDiplomaSummary(data.block);
    const details = parseDiplomaDetails(data.block);
    res.render('user/validate_diploma', {
      title: 'Validate a Diploma',
      blockSummary: summary,
      blockDetails: details
    });
  } catch (error) {
    res.render('user/validate_diploma', {
      title: 'Validate a Diploma',
      error: { msg: error.message || 'Unexpected error' }
    });
  }
});

module.exports = router;
