from datetime import date


def year(request):
    """Добавляет переменную с текущим годом."""
    now = int(date.today().year)
    return {
        'year': now
    }
