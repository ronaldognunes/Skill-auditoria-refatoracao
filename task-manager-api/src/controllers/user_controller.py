import re
import jwt
from datetime import datetime, timedelta
from database import db
from models.user import User
from models.task import Task
from src.config.settings import SECRET_KEY, JWT_EXPIRATION_HOURS
from src.middlewares.error_handler import AppError

_EMAIL_REGEX = r'^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$'
_VALID_ROLES = ['user', 'admin', 'manager']


class UserController:
    def list_users(self):
        return [
            {
                'id': u.id,
                'name': u.name,
                'email': u.email,
                'role': u.role,
                'active': u.active,
                'created_at': str(u.created_at),
                'task_count': len(u.tasks)
            }
            for u in User.query.all()
        ]

    def get_user(self, user_id):
        user = User.query.get(user_id)
        if not user:
            raise AppError('Usuário não encontrado', 404)
        data = user.to_dict()
        data['tasks'] = [t.to_dict() for t in Task.query.filter_by(user_id=user_id).all()]
        return data

    def create_user(self, data):
        name = data.get('name')
        email = data.get('email')
        password = data.get('password')
        role = data.get('role', 'user')

        if not name:
            raise AppError('Nome é obrigatório', 400)
        if not email:
            raise AppError('Email é obrigatório', 400)
        if not password:
            raise AppError('Senha é obrigatória', 400)
        if not re.match(_EMAIL_REGEX, email):
            raise AppError('Email inválido', 400)
        if len(password) < 4:
            raise AppError('Senha deve ter no mínimo 4 caracteres', 400)
        if role not in _VALID_ROLES:
            raise AppError('Role inválido', 400)
        if User.query.filter_by(email=email).first():
            raise AppError('Email já cadastrado', 409)

        user = User()
        user.name = name
        user.email = email
        user.set_password(password)
        user.role = role

        db.session.add(user)
        db.session.commit()
        return user.to_dict()

    def update_user(self, user_id, data):
        user = User.query.get(user_id)
        if not user:
            raise AppError('Usuário não encontrado', 404)

        if 'name' in data:
            user.name = data['name']
        if 'email' in data:
            if not re.match(_EMAIL_REGEX, data['email']):
                raise AppError('Email inválido', 400)
            existing = User.query.filter_by(email=data['email']).first()
            if existing and existing.id != user_id:
                raise AppError('Email já cadastrado', 409)
            user.email = data['email']
        if 'password' in data:
            if len(data['password']) < 4:
                raise AppError('Senha muito curta', 400)
            user.set_password(data['password'])
        if 'role' in data:
            if data['role'] not in _VALID_ROLES:
                raise AppError('Role inválido', 400)
            user.role = data['role']
        if 'active' in data:
            user.active = data['active']

        db.session.commit()
        return user.to_dict()

    def delete_user(self, user_id):
        user = User.query.get(user_id)
        if not user:
            raise AppError('Usuário não encontrado', 404)
        Task.query.filter_by(user_id=user_id).delete()
        db.session.delete(user)
        db.session.commit()

    def get_user_tasks(self, user_id):
        if not User.query.get(user_id):
            raise AppError('Usuário não encontrado', 404)
        tasks = Task.query.filter_by(user_id=user_id).all()
        return [
            {
                'id': t.id,
                'title': t.title,
                'description': t.description,
                'status': t.status,
                'priority': t.priority,
                'created_at': str(t.created_at),
                'due_date': str(t.due_date) if t.due_date else None,
                'overdue': t.is_overdue()
            }
            for t in tasks
        ]

    def login(self, data):
        email = data.get('email')
        password = data.get('password')
        if not email or not password:
            raise AppError('Email e senha são obrigatórios', 400)

        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            raise AppError('Credenciais inválidas', 401)
        if not user.active:
            raise AppError('Usuário inativo', 403)

        payload = {
            'user_id': user.id,
            'role': user.role,
            'exp': datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
        return {
            'message': 'Login realizado com sucesso',
            'user': user.to_dict(),
            'token': token
        }
