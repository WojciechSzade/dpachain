const express = require('express');
const router = express.Router();
const parseDiploma = require('../utils/parseDiploma');

router.get('/', (req, res) => {
  res.render('user/index', { title: 'User Section' });
});

router.get('/validate_diploma', async (req, res) => {
  const { block_hash } = req.query;

  if (!block_hash) {
    return res.render('user/validate_diploma', { title: 'Validate a Diploma' });
  }

  try {
    const apiRes = await fetch(`http://localhost:8000/user/get_block_by_hash?block_hash=${encodeURIComponent(block_hash)}`);
    const data = await apiRes.json();

    if (!apiRes.ok) {
      return res.render('user/validate_diploma', {
        title: 'Validate a diploma',
        error: { msg: JSON.stringify(data) },
        block: null
      });
    }

    const block = parseDiploma(data.block);
    res.render('user/validate_diploma', { title: 'Validate a Diploma', block });
  } catch (error) {
    res.render('user/validate_diploma', {
      title: 'Validate a Diploma',
      error: { msg: error.message },
      block: null
    });
  }
});


module.exports = router;
