const jwt = require('jsonwebtoken');
const { jwtSecret } = require('../config/settings');

function requireAuth(req, res, next) {
  const auth = req.headers.authorization || '';
  if (!auth.startsWith('Bearer ')) {
    return res.status(401).json({ error: 'Token ausente' });
  }
  const token = auth.split(' ')[1];
  try {
    req.currentUser = jwt.verify(token, jwtSecret);
    next();
  } catch {
    res.status(401).json({ error: 'Token inválido ou expirado' });
  }
}

function requireAdmin(req, res, next) {
  requireAuth(req, res, () => {
    if (req.currentUser?.role !== 'admin') {
      return res.status(403).json({ error: 'Acesso negado' });
    }
    next();
  });
}

module.exports = { requireAuth, requireAdmin };
