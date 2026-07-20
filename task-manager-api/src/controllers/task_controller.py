from datetime import datetime
from sqlalchemy import or_
from sqlalchemy.orm import joinedload
from database import db
from models.task import Task
from models.user import User
from models.category import Category
from src.middlewares.error_handler import AppError

_VALID_STATUSES = ['pending', 'in_progress', 'done', 'cancelled']


class TaskController:
    def list_tasks(self):
        tasks = Task.query.options(
            joinedload(Task.user),
            joinedload(Task.category)
        ).all()
        return [self._task_to_dict(t) for t in tasks]

    def get_task(self, task_id):
        task = Task.query.get(task_id)
        if not task:
            raise AppError('Task não encontrada', 404)
        data = task.to_dict()
        data['overdue'] = task.is_overdue()
        return data

    def create_task(self, data):
        title = data.get('title')
        if not title:
            raise AppError('Título é obrigatório', 400)
        if len(title) < 3:
            raise AppError('Título muito curto', 400)
        if len(title) > 200:
            raise AppError('Título muito longo', 400)

        status = data.get('status', 'pending')
        if status not in _VALID_STATUSES:
            raise AppError('Status inválido', 400)

        try:
            priority = int(data.get('priority', 3))
        except (TypeError, ValueError):
            raise AppError('Prioridade inválida', 400)
        if priority < 1 or priority > 5:
            raise AppError('Prioridade deve ser entre 1 e 5', 400)

        user_id = data.get('user_id')
        category_id = data.get('category_id')

        if user_id and not User.query.get(user_id):
            raise AppError('Usuário não encontrado', 404)
        if category_id and not Category.query.get(category_id):
            raise AppError('Categoria não encontrada', 404)

        task = Task()
        task.title = title
        task.description = data.get('description', '')
        task.status = status
        task.priority = priority
        task.user_id = user_id
        task.category_id = category_id

        due_date_str = data.get('due_date')
        if due_date_str:
            try:
                task.due_date = datetime.strptime(due_date_str, '%Y-%m-%d')
            except ValueError:
                raise AppError('Formato de data inválido. Use YYYY-MM-DD', 400)

        tags = data.get('tags')
        if tags:
            task.tags = ','.join(tags) if isinstance(tags, list) else tags

        db.session.add(task)
        db.session.commit()
        return task.to_dict()

    def update_task(self, task_id, data):
        task = Task.query.get(task_id)
        if not task:
            raise AppError('Task não encontrada', 404)

        if 'title' in data:
            if len(data['title']) < 3:
                raise AppError('Título muito curto', 400)
            if len(data['title']) > 200:
                raise AppError('Título muito longo', 400)
            task.title = data['title']
        if 'description' in data:
            task.description = data['description']
        if 'status' in data:
            if data['status'] not in _VALID_STATUSES:
                raise AppError('Status inválido', 400)
            task.status = data['status']
        if 'priority' in data:
            try:
                p = int(data['priority'])
            except (TypeError, ValueError):
                raise AppError('Prioridade inválida', 400)
            if p < 1 or p > 5:
                raise AppError('Prioridade deve ser entre 1 e 5', 400)
            task.priority = p
        if 'user_id' in data:
            if data['user_id'] and not User.query.get(data['user_id']):
                raise AppError('Usuário não encontrado', 404)
            task.user_id = data['user_id']
        if 'category_id' in data:
            if data['category_id'] and not Category.query.get(data['category_id']):
                raise AppError('Categoria não encontrada', 404)
            task.category_id = data['category_id']
        if 'due_date' in data:
            if data['due_date']:
                try:
                    task.due_date = datetime.strptime(data['due_date'], '%Y-%m-%d')
                except ValueError:
                    raise AppError('Formato de data inválido', 400)
            else:
                task.due_date = None
        if 'tags' in data:
            tags = data['tags']
            task.tags = ','.join(tags) if isinstance(tags, list) else tags

        task.updated_at = datetime.utcnow()
        db.session.commit()
        return task.to_dict()

    def delete_task(self, task_id):
        task = Task.query.get(task_id)
        if not task:
            raise AppError('Task não encontrada', 404)
        db.session.delete(task)
        db.session.commit()

    def search_tasks(self, q='', status='', priority='', user_id=''):
        query = Task.query
        if q:
            query = query.filter(
                or_(Task.title.like(f'%{q}%'), Task.description.like(f'%{q}%'))
            )
        if status:
            query = query.filter(Task.status == status)
        if priority:
            try:
                query = query.filter(Task.priority == int(priority))
            except ValueError:
                raise AppError('Prioridade inválida', 400)
        if user_id:
            try:
                query = query.filter(Task.user_id == int(user_id))
            except ValueError:
                raise AppError('user_id inválido', 400)
        return [t.to_dict() for t in query.all()]

    def get_stats(self):
        total = Task.query.count()
        done = Task.query.filter_by(status='done').count()
        overdue_count = sum(1 for t in Task.query.all() if t.is_overdue())
        return {
            'total': total,
            'pending': Task.query.filter_by(status='pending').count(),
            'in_progress': Task.query.filter_by(status='in_progress').count(),
            'done': done,
            'cancelled': Task.query.filter_by(status='cancelled').count(),
            'overdue': overdue_count,
            'completion_rate': round((done / total) * 100, 2) if total > 0 else 0
        }

    def _task_to_dict(self, task):
        data = task.to_dict()
        data['overdue'] = task.is_overdue()
        data['user_name'] = task.user.name if task.user else None
        data['category_name'] = task.category.name if task.category else None
        return data
