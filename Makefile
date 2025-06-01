.PHONY: shell shell-basic test runserver help

shell:
	@echo "🚀 Starting Django Shell Plus with database info..."
	uv run python manage.py shell_plus --print-sql -c "exec(open('shell_startup.py').read())"

runserver:
	@echo "🌐 Starting Django development server..."
	uv run python manage.py runserver

help:
	@echo "Available commands:"
	@echo "  make shell       - Start shell_plus with database config display"
	@echo "  make runserver   - Start development server"
