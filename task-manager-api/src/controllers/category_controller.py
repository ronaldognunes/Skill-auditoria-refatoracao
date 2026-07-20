from database import db
from models.category import Category
from models.task import Task
from src.middlewares.error_handler import AppError


class CategoryController:
    def list_categories(self):
        result = []
        for c in Category.query.all():
            data = c.to_dict()
            data['task_count'] = Task.query.filter_by(category_id=c.id).count()
            result.append(data)
        return result

    def create_category(self, data):
        name = data.get('name')
        if not name:
            raise AppError('Nome é obrigatório', 400)
        category = Category()
        category.name = name
        category.description = data.get('description', '')
        category.color = data.get('color', '#000000')
        db.session.add(category)
        db.session.commit()
        return category.to_dict()

    def update_category(self, cat_id, data):
        cat = Category.query.get(cat_id)
        if not cat:
            raise AppError('Categoria não encontrada', 404)
        if 'name' in data:
            cat.name = data['name']
        if 'description' in data:
            cat.description = data['description']
        if 'color' in data:
            cat.color = data['color']
        db.session.commit()
        return cat.to_dict()

    def delete_category(self, cat_id):
        cat = Category.query.get(cat_id)
        if not cat:
            raise AppError('Categoria não encontrada', 404)
        db.session.delete(cat)
        db.session.commit()
