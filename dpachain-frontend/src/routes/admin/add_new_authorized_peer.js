const express = require('express');
const { URL } = require('url');

const router = express.Router();

// GET: display form to add a new authorized peer
router.get('/add_new_authorized_peer', (req, res) => {
  res.render('admin/add_new_authorized_peer', { title: 'Add New Authorized Peer', error: null, message: null, form: {} });
});

// POST: handle form submission
router.post('/add_new_authorized_peer', async (req, res) => {
  const { nickname, public_key, address } = req.body;
  const form = { nickname, public_key, address };

  if (!nickname || !public_key) {
    return res.render('admin/add_new_authorized_peer', {
      title: 'Add New Authorized Peer',
      error: { msg: 'Nickname and public key are required.' },
      message: null,
      form
    });
  }

  try {
    const url = new URL('http://localhost:8000/admin/add_new_authorized_peer');
    url.searchParams.append('nickname', nickname);
    url.searchParams.append('public_key', public_key);
    if (address) url.searchParams.append('adress', address);

    const apiRes = await fetch(url.toString(), { method: 'POST' });
    const data = await apiRes.json();

    if (!apiRes.ok) {
      return res.render('admin/add_new_authorized_peer', {
        title: 'Add New Authorized Peer',
        error: { msg: JSON.stringify(data) },
        message: null,
        form
      });
    }

    res.render('admin/add_new_authorized_peer', {
      title: 'Add New Authorized Peer',
      error: null,
      message: data.message,
      form: {}
    });
  } catch (err) {
    res.render('admin/add_new_authorized_peer', {
      title: 'Add New Authorized Peer',
      error: { msg: err.message },
      message: null,
      form
    });
  }
});

module.exports = router;