module.exports = {
  dbPath: process.env.DB_PATH || ':memory:',
  paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY,
  smtpUser: process.env.SMTP_USER,
  port: parseInt(process.env.PORT) || 3000,
};
