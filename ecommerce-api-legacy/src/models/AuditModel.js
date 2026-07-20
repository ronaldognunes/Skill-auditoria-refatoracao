const { dbRun } = require('../database');

class AuditModel {
  async log(action) {
    return dbRun(
      "INSERT INTO audit_logs (action, created_at) VALUES (?, datetime('now'))",
      [action]
    );
  }
}

module.exports = new AuditModel();
