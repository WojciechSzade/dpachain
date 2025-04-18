const express = require('express');
const router = express.Router();
const parseDiplomas = require('../utils/parseDiplomas')

router.get('/', (req, res) => {
    res.render('staff/index', { title: 'Staff Section' });
});


router.get('/diplomas', async (req, res) => {
    const { blocks } = req.body;
    try {
        const apiRes = await fetch(`http://localhost:8000/staff/get_all_blocks`, {
            method: 'GET'
        });
        const response = await apiRes;
        const data = await response.json()
        if (!response.ok) {
            console.log(data)
            return res.render('staff/diplomas', { title: 'Diplomas list', error: { "msg": JSON.stringify(data) } })
        }
        const [labels, blocks] = parseDiplomas(data.blocks);
        res.render('staff/diplomas', { title: 'Diplomas list', blocks, labels });
    } catch (error) {
        res.render('staff/diplomas', { title: 'Diplomas list', blocks: [[{ label: 'Error', value: error.message }]] });
    }
});

module.exports = router;
