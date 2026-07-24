const sqlite3 = require('sqlite3').verbose();
const { dbPath } = require('./config/settings');

const db = new sqlite3.Database(dbPath);

const dbRun = (sql, params = []) => new Promise((resolve, reject) => {
  db.run(sql, params, function(err) {
    if (err) reject(err);
    else resolve(this);
  });
});

const dbGet = (sql, params = []) => new Promise((resolve, reject) => {
  db.get(sql, params, (err, row) => {
    if (err) reject(err);
    else resolve(row);
  });
});

const dbAll = (sql, params = []) => new Promise((resolve, reject) => {
  db.all(sql, params, (err, rows) => {
    if (err) reject(err);
    else resolve(rows || []);
  });
});

async function initDb() {
  await dbRun("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, email TEXT UNIQUE, password_hash TEXT)");
  await dbRun("CREATE TABLE IF NOT EXISTS courses (id INTEGER PRIMARY KEY, title TEXT, price REAL, active INTEGER)");
  await dbRun("CREATE TABLE IF NOT EXISTS enrollments (id INTEGER PRIMARY KEY, user_id INTEGER, course_id INTEGER)");
  await dbRun("CREATE TABLE IF NOT EXISTS payments (id INTEGER PRIMARY KEY, enrollment_id INTEGER, amount REAL, status TEXT)");
  await dbRun("CREATE TABLE IF NOT EXISTS audit_logs (id INTEGER PRIMARY KEY, action TEXT, created_at DATETIME)");
  await dbRun("INSERT INTO courses (title, price, active) VALUES ('Clean Architecture', 997.00, 1), ('Docker', 497.00, 1)");
}

module.exports = { dbRun, dbGet, dbAll, initDb };
