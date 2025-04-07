const express = require('express');
const path = require('path');
const expressLayouts = require('express-ejs-layouts');

const app = express();

// Set EJS as templating engine
app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));

app.use(expressLayouts);
// Optionally set the default layout file (views/layout.ejs)
app.set('layout', 'layout');

// For parsing URL-encoded form data
app.use(express.urlencoded({ extended: true }));


// Mount routers
// app.use('/admin', require('./routes/admin'));
// app.use('/staff', require('./routes/staff'));
app.use('/user', require('./routes/user'));

// Home page: simple navigation page linking to each section
app.get('/', (req, res) => {
    res.render('layout', {
        title: 'DPAChain API Manager Home',
        body: `
      <div class="container mt-4">
        <h1>Welcome to DPAChain API Manager</h1>
        <ul>
          <li><a href="/admin">Admin Section</a></li>
          <li><a href="/staff">Staff Section</a></li>
          <li><a href="/user">User Section</a></li>
        </ul>
      </div>
    `
    });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Server started on http://localhost:${PORT}`);
});
