const bcrypt = require('bcrypt');
const userModel = require('../models/UserModel');
const courseModel = require('../models/CourseModel');
const enrollmentModel = require('../models/EnrollmentModel');
const paymentModel = require('../models/PaymentModel');
const auditModel = require('../models/AuditModel');

const SALT_ROUNDS = 12;

class CheckoutController {
  async processCheckout(req, res, next) {
    try {
      const { usr: name, eml: email, pwd: password, c_id: courseId, card } = req.body;

      if (!name || !email || !password || !courseId || !card) {
        return res.status(400).json({ error: 'Bad Request: campos obrigatórios ausentes' });
      }

      const course = await courseModel.findActiveById(courseId);
      if (!course) return res.status(404).json({ error: 'Curso não encontrado' });

      let user = await userModel.findByEmail(email);
      let userId;

      if (!user) {
        const passwordHash = await bcrypt.hash(password, SALT_ROUNDS);
        userId = await userModel.create(name, email, passwordHash);
      } else {
        userId = user.id;
      }

      const paymentStatus = card.startsWith('4') ? 'PAID' : 'DENIED';
      if (paymentStatus === 'DENIED') return res.status(400).json({ error: 'Pagamento recusado' });

      const enrollmentId = await enrollmentModel.create(userId, courseId);
      await paymentModel.create(enrollmentId, course.price, paymentStatus);
      await auditModel.log(`Checkout curso ${courseId} por ${userId}`);

      res.status(200).json({ msg: 'Sucesso', enrollment_id: enrollmentId });
    } catch (err) {
      next(err);
    }
  }
}

module.exports = new CheckoutController();
