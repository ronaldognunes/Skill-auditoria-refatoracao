const router = require('express').Router();
const checkoutController = require('../controllers/CheckoutController');

router.post('/', (req, res, next) => checkoutController.processCheckout(req, res, next));

module.exports = router;
