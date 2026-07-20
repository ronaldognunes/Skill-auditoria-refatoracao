const express = require('express');
const { port } = require('./config/settings');
const { initDb } = require('./database');
const checkoutRoutes = require('./routes/checkoutRoutes');
const adminRoutes = require('./routes/adminRoutes');
const userRoutes = require('./routes/userRoutes');
const errorHandler = require('./middlewares/errorHandler');

const app = express();
app.use(express.json());

app.use('/api/checkout', checkoutRoutes);
app.use('/api/admin', adminRoutes);
app.use('/api/users', userRoutes);

app.use(errorHandler);

initDb()
  .then(() => {
    app.listen(port, () => {
      console.log(`Frankenstein LMS rodando na porta ${port}...`);
    });
  })
  .catch((err) => {
    console.error('Falha ao inicializar o banco de dados:', err);
    process.exit(1);
  });

module.exports = app;
