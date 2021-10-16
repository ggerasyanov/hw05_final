from django.shortcuts import render


def page_not_found(request, exception):
    """Кастомная страница ошибки 404"""
    return render(request, 'core/404.html', {'path': request.path}, status=404)


def csrf_failure(request, reason=''):
    """Кастомная страница ошибки 403"""
    return render(request, 'core/403csrf.html')


def server_error(request):
    """Кастомная страница ошибки 500"""
    return render(request, 'core/500.html', {'path': request.path}, status=500)
