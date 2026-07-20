const { dbRun } = require('../database');

class PaymentModel {
  async create(enrollmentId, amount, status) {
    const result = await dbRun(
      'INSERT INTO payments (enrollment_id, amount, status) VALUES (?, ?, ?)',
      [enrollmentId, amount, status]
    );
    return result.lastID;
  }
}

module.exports = new PaymentModel();
