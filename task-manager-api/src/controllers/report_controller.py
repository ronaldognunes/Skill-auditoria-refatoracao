from datetime import datetime, timedelta
from models.task import Task
from models.user import User
from models.category import Category
from src.middlewares.error_handler import AppError


class ReportController:
    def summary_report(self):
        all_tasks = Task.query.all()
        overdue_tasks = [t for t in all_tasks if t.is_overdue()]
        overdue_list = [
            {
                'id': t.id,
                'title': t.title,
                'due_date': str(t.due_date),
                'days_overdue': (datetime.utcnow() - t.due_date).days
            }
            for t in overdue_tasks
        ]

        seven_days_ago = datetime.utcnow() - timedelta(days=7)

        return {
            'generated_at': str(datetime.utcnow()),
            'overview': {
                'total_tasks': Task.query.count(),
                'total_users': User.query.count(),
                'total_categories': Category.query.count(),
            },
            'tasks_by_status': {
                'pending': Task.query.filter_by(status='pending').count(),
                'in_progress': Task.query.filter_by(status='in_progress').count(),
                'done': Task.query.filter_by(status='done').count(),
                'cancelled': Task.query.filter_by(status='cancelled').count(),
            },
            'tasks_by_priority': {
                'critical': Task.query.filter_by(priority=1).count(),
                'high': Task.query.filter_by(priority=2).count(),
                'medium': Task.query.filter_by(priority=3).count(),
                'low': Task.query.filter_by(priority=4).count(),
                'minimal': Task.query.filter_by(priority=5).count(),
            },
            'overdue': {
                'count': len(overdue_list),
                'tasks': overdue_list,
            },
            'recent_activity': {
                'tasks_created_last_7_days': Task.query.filter(
                    Task.created_at >= seven_days_ago
                ).count(),
                'tasks_completed_last_7_days': Task.query.filter(
                    Task.status == 'done',
                    Task.updated_at >= seven_days_ago
                ).count(),
            },
            'user_productivity': self._build_user_stats(),
        }

    def user_report(self, user_id):
        user = User.query.get(user_id)
        if not user:
            raise AppError('Usuário não encontrado', 404)

        tasks = Task.query.filter_by(user_id=user_id).all()
        total = len(tasks)
        return {
            'user': {'id': user.id, 'name': user.name, 'email': user.email},
            'statistics': {
                'total_tasks': total,
                'done': sum(1 for t in tasks if t.status == 'done'),
                'pending': sum(1 for t in tasks if t.status == 'pending'),
                'in_progress': sum(1 for t in tasks if t.status == 'in_progress'),
                'cancelled': sum(1 for t in tasks if t.status == 'cancelled'),
                'overdue': sum(1 for t in tasks if t.is_overdue()),
                'high_priority': sum(1 for t in tasks if t.priority <= 2),
                'completion_rate': round(
                    (sum(1 for t in tasks if t.status == 'done') / total) * 100, 2
                ) if total > 0 else 0
            }
        }

    def _build_user_stats(self):
        stats = []
        for u in User.query.all():
            user_tasks = Task.query.filter_by(user_id=u.id).all()
            total = len(user_tasks)
            completed = sum(1 for t in user_tasks if t.status == 'done')
            stats.append({
                'user_id': u.id,
                'user_name': u.name,
                'total_tasks': total,
                'completed_tasks': completed,
                'completion_rate': round((completed / total) * 100, 2) if total > 0 else 0
            })
        return stats
