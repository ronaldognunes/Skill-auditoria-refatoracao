const { dbGet } = require('../database');

class CourseModel {
  async findActiveById(id) {
    return dbGet('SELECT * FROM courses WHERE id = ? AND active = 1', [id]);
  }
}

module.exports = new CourseModel();
