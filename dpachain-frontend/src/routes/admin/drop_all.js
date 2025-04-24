const express = require('express');
const { API_BASE_URL } = require('../../config'); 

const router = express.Router();


router.get('/drop_all_blocks', (req, res) => {
    res.render('admin/drop_all_blocks', {
        message: req.query.message,
        error: req.query.error
    });
});

router.post('/drop_all_blocks', async (req, res) => {
    try {
        const apiRes = await fetch(`${API_BASE_URL}/admin/drop_all_blocks`, { method: 'POST' });
        const text = await apiRes.text();
        res.redirect(`/admin/drop_all_blocks?message=${encodeURIComponent(text)}`);
    } catch (err) {
        res.redirect(`/admin/drop_all_blocks?error=${encodeURIComponent(err.message)}`);
    }
});

module.exports = router;