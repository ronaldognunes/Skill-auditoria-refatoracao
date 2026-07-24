module.exports = {
  dbPath: process.env.DB_PATH || ':memory:',
  port: parseInt(process.env.PORT) || 3000,
};
