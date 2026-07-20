const router = require('express').Router();
const adminController = require('../controllers/AdminController');

router.delete('/:id', (req, res, next) => adminController.deleteUser(req, res, next));

module.exports = router;
