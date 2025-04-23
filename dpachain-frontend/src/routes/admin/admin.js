const express = require('express');
const router = express.Router();

const addNewPeer = require('./add_new_peer');
const addNewAuthorizedPeer = require('./add_new_authorized_peer');
const getPeersList = require('./get_peers_list');
const syncChain = require('./sync_chain');

router.get('/', (req, res) => {
    res.render('admin/index', { title: 'Admin section' });
});

router.use('/', addNewPeer);
router.use('/', addNewAuthorizedPeer);
router.use('/', getPeersList);
router.use('/', syncChain)

module.exports = router;
