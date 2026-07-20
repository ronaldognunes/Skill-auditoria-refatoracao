const { dbRun } = require('../database');

class EnrollmentModel {
  async create(userId, courseId) {
    const result = await dbRun(
      'INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)',
      [userId, courseId]
    );
    return result.lastID;
  }
}

module.exports = new EnrollmentModel();
