const express = require('express');
const { API_BASE_URL } = require('../../config');

const router = express.Router();

router.get('/sync_chain', (req, res) => {
  res.render('admin/sync_chain', {
    title: 'Sync Chain',
    message: req.query.message,
    error: req.query.error
  });
});

router.post('/sync_chain', async (req, res) => {
  try {
    const apiRes = await fetch(`${API_BASE_URL}/admin/sync_chain`, {
      method: 'POST'
    });
    const text = await apiRes.text();
    if (!apiRes.ok) throw new Error(text);

    res.redirect(`/admin/sync_chain?message=${encodeURIComponent(text)}`);
  } catch (err) {
    res.redirect(`/admin/sync_chain?error=${encodeURIComponent(err.message)}`);
  }
});

module.exports = router;
