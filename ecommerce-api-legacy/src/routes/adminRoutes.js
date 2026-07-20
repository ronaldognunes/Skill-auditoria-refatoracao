const router = require('express').Router();
const adminController = require('../controllers/AdminController');

router.get('/financial-report', (req, res, next) => adminController.getFinancialReport(req, res, next));

module.exports = router;
