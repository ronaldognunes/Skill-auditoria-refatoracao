const { dbAll } = require('../database');

class ReportModel {
  async getFinancialData() {
    return dbAll(`
      SELECT
        c.id     AS course_id,
        c.title  AS course_title,
        u.name   AS student_name,
        p.amount,
        p.status
      FROM courses c
      LEFT JOIN enrollments e ON e.course_id = c.id
      LEFT JOIN users u ON u.id = e.user_id
      LEFT JOIN payments p ON p.enrollment_id = e.id
    `);
  }
}

module.exports = new ReportModel();
