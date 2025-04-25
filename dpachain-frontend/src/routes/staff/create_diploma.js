const express = require('express');
const { URL } = require('url');
const { Blob } = require('buffer');
const multer = require('multer');
const parseDiploma = require('../../utils/parseDiploma');
const { API_BASE_URL } = require('../../config');

const router = express.Router();
const upload = multer({ storage: multer.memoryStorage() });

router.get('/create_diploma', (req, res) => {
  res.render('staff/create_diploma', { title: 'Create diploma', error: null, block: null, form: {} });
});

router.post('/create_diploma', upload.single('pdf_file'), async (req, res) => {
  const {
    diploma_type,
    title,
    language,
    discipline,
    is_defended,
    date_of_defense,
    university,
    faculty,
    additional_info,
    authors,
    authors_id,
    supervisor,
    reviewer
  } = req.body;

  const form = { diploma_type, title, language, discipline, is_defended, date_of_defense, university, faculty, additional_info, authors, authors_id, supervisor, reviewer };

  if (!req.file) {
    return res.render('staff/create_diploma', {
      title: 'Create diploma',
      error: { msg: 'PDF file is required.' },
      block: null,
      form
    });
  }

  try {
    const url = new URL('/staff/generate_new_block', API_BASE_URL);
    ['diploma_type', 'title', 'language', 'discipline', 'is_defended', 'date_of_defense', 'university', 'faculty']
      .forEach(key => {
        if (req.body[key] != null) {
          url.searchParams.append(key, req.body[key]);
        }
      });
    if (additional_info) {
      url.searchParams.append('additional_info', additional_info);
    }

    const formData = new FormData();
    const pdfBlob = new Blob([req.file.buffer], { type: req.file.mimetype });
    formData.append('pdf_file', pdfBlob, req.file.originalname);
    (Array.isArray(authors) ? authors : [authors]).forEach(a => formData.append('authors', a));
    (Array.isArray(authors_id) ? authors_id : [authors_id]).forEach(a => formData.append('authors_id', a));
    (Array.isArray(supervisor) ? supervisor : [supervisor]).forEach(s => formData.append('supervisor', s));
    (Array.isArray(reviewer) ? reviewer : [reviewer]).forEach(r => formData.append('reviewer', r));

    const apiRes = await fetch(url.toString(), {
      method: 'POST',
      body: formData
    });
    const data = await apiRes.json();

    if (!apiRes.ok) {
      return res.render('staff/create_diploma', {
        title: 'Create diploma',
        error: { msg: JSON.stringify(data) },
        block: null,
        form
      });
    }

    const block = parseDiploma(data.block);
    res.render('staff/create_diploma', {
      title: 'Create diploma',
      error: null,
      block,
      form: {}
    });
  } catch (err) {
    res.render('staff/create_diploma', {
      title: 'Create diploma',
      error: { msg: err.message },
      block: null,
      form
    });
  }
});

module.exports = router;
