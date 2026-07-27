const router = require('express').Router();
const adminController = require('../controllers/AdminController');
const { requireAdmin } = require('../middlewares/authMiddleware');

router.get('/financial-report', requireAdmin, (req, res, next) => adminController.getFinancialReport(req, res, next));

module.exports = router;
