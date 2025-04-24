const express = require('express');
const router = express.Router();
const parseDiplomas = require('../../utils/parseDiplomas')
const createDiploma = require('./create_diploma');
const { API_BASE_URL } = require('../../config');


router.get('/', (req, res) => {
    res.render('staff/index', { title: 'Staff Section' });
});


router.get('/diplomas', async (req, res) => {
    const { blocks } = req.body;
    try {
        const url = new URL('/staff/get_all_blocks', API_BASE_URL);
        const apiRes = await fetch(url.toString(), {
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

router.use('/', createDiploma);


module.exports = router;
