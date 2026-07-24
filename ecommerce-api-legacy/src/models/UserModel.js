const { dbGet, dbRun } = require('../database');

class UserModel {
  async findByEmail(email) {
    return dbGet('SELECT * FROM users WHERE email = ?', [email]);
  }

  async create(name, email, passwordHash) {
    const result = await dbRun(
      'INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)',
      [name, email, passwordHash]
    );
    return result.lastID;
  }

  async deleteById(id) {
    return dbRun('DELETE FROM users WHERE id = ?', [id]);
  }
}

module.exports = new UserModel();
