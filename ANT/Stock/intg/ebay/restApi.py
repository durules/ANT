import hashlib

from django.http import JsonResponse, HttpResponse


def delete_account(request):
    if request.method == 'POST':
        return HttpResponse()
    else:
        # Определеям текущую ссылку
        host = ''
        if 'HTTP_HOST' in request.META:
            host = request.META['HTTP_HOST']

        relative_path = request.path

        end_point = host + relative_path

        # определяем параметр проверочного кода
        params = request.GET

        challenge_code = ''
        if "challenge_code" in params:
            challenge_code = params['challenge_code']

        # получаем токен.
        verification_token = 'SBX-23495a34b3cd1-991c1-43001-9fc21-8def1'

        resp = hashlib.sha256((challenge_code + verification_token + end_point).encode('utf-8'))

        return JsonResponse({
            'challengeResponse': resp.hexdigest(),
        })

