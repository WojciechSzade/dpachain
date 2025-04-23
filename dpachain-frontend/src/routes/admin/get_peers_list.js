const express = require('express');
const parsePeer = require('../../utils/parsePeer');

const router = express.Router();

router.get('/get_peers_list', async (req, res) => {
    try {
        const apiRes = await fetch('http://localhost:8000/admin/get_peers_list', { method: 'GET' });
        const data = await apiRes.json();
        if (!apiRes.ok) throw new Error(JSON.stringify(data));

        const peers = (data.peers || []).map(parsePeer);
        res.render('admin/get_peers_list', { title: 'Peers List', peers });
    } catch (err) {
        res.render('admin/get_peers_list', { title: 'Peers List', peers: [], error: err.message });
    }
});

router.get('/peer/:nickname', async (req, res) => {
    const { nickname } = req.params;
    const { error, message } = req.query;
    try {
      const apiRes = await fetch('http://localhost:8000/admin/get_peers_list');
      const data = await apiRes.json();
      if (!apiRes.ok) throw new Error(JSON.stringify(data));
  
      const raw = (data.peers || []).find(p => p.nickname === nickname);
      if (!raw) throw new Error('Peer not found');
      const peer = parsePeer(raw);
  
      res.render('admin/peer_detail', {
        title: 'Peer Detail',
        peer,
        message: message || null,
        error: error || null
      });
    } catch (err) {
      res.render('admin/peer_detail', {
        title: 'Peer Detail',
        peer: null,
        message: null,
        error: error || err.message
      });
    }
  });

router.post('/peer/:nickname/:action', async (req, res) => {
    const { nickname, action } = req.params;
    const allowed = ['remove_peer', 'ban_peer', 'unban_peer', 'present_to_peer', 'ask_peer_to_sync'];
    if (!allowed.includes(action)) return res.status(400).send('Invalid action');

    try {
        const url = new URL(`http://localhost:8000/admin/${action}`);
        url.searchParams.append('nickname', nickname);
        const apiRes = await fetch(url.toString(), { method: 'POST' });
        const text = await apiRes.text();
        const redirectUrl = `/admin/peer/${encodeURIComponent(nickname)}?message=${encodeURIComponent(text)}`;
        res.redirect(redirectUrl);
    } catch (err) {
        const redirectUrl = `/admin/peer/${encodeURIComponent(nickname)}?error=${encodeURIComponent(err.message)}`;
        res.redirect(redirectUrl);
    }
});


module.exports = router;