const express = require('express');
const { URL } = require('url');

const router = express.Router();

router.get('/add_new_peer', (req, res) => {
  res.render('admin/add_new_peer', { title: 'Add New Peer', error: null, message: null, form: {} });
});

router.post('/add_new_peer', async (req, res) => {
  const { nickname, address } = req.body;
  const form = { nickname, address };

  if (!nickname) {
    return res.render('admin/add_new_peer', {
      title: 'Add New Peer',
      error: { msg: 'Nickname is required.' },
      message: null,
      form
    });
  }

  try {
    const url = new URL('http://localhost:8000/admin/add_new_peer');
    url.searchParams.append('nickname', nickname);
    if (address) url.searchParams.append('adress', address);

    const apiRes = await fetch(url.toString(), { method: 'POST' });
    const data = await apiRes.json();

    if (!apiRes.ok) {
      return res.render('admin/add_new_peer', {
        title: 'Add New Peer',
        error: { msg: JSON.stringify(data) },
        message: null,
        form
      });
    }

    res.render('admin/add_new_peer', {
      title: 'Add New Peer',
      error: null,
      message: data.message,
      form: {}
    });
  } catch (err) {
    res.render('admin/add_new_peer', {
      title: 'Add New Peer',
      error: { msg: err.message },
      message: null,
      form
    });
  }
});

module.exports = router;