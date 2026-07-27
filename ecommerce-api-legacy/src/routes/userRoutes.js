const router = require('express').Router();
const adminController = require('../controllers/AdminController');
const { requireAdmin } = require('../middlewares/authMiddleware');

router.delete('/:id', requireAdmin, (req, res, next) => adminController.deleteUser(req, res, next));

module.exports = router;
