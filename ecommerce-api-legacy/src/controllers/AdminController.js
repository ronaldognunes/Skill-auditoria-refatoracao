const reportModel = require('../models/ReportModel');
const userModel = require('../models/UserModel');

class AdminController {
  async getFinancialReport(req, res, next) {
    try {
      const rows = await reportModel.getFinancialData();

      const reportMap = {};
      for (const row of rows) {
        if (!reportMap[row.course_id]) {
          reportMap[row.course_id] = { course: row.course_title, revenue: 0, students: [] };
        }
        if (row.status === 'PAID') {
          reportMap[row.course_id].revenue += row.amount;
        }
        if (row.student_name) {
          reportMap[row.course_id].students.push({
            student: row.student_name,
            paid: row.amount || 0,
          });
        }
      }

      res.json(Object.values(reportMap));
    } catch (err) {
      next(err);
    }
  }

  async deleteUser(req, res, next) {
    try {
      const id = parseInt(req.params.id);
      if (isNaN(id)) return res.status(400).json({ error: 'ID inválido' });

      await userModel.deleteById(id);
      res.json({ msg: 'Usuário deletado' });
    } catch (err) {
      next(err);
    }
  }
}

module.exports = new AdminController();
