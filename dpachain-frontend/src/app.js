const express = require('express');
const path = require('path');
const expressLayouts = require('express-ejs-layouts');


const app = express();

app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));

app.use(expressLayouts);
app.set('layout', 'layout');

app.use(express.urlencoded({ extended: true }));


app.use('/admin', require('./routes/admin/admin'));
app.use('/staff', require('./routes/staff/staff'));
app.use('/user', require('./routes/user'));

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
