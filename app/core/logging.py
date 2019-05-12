from core.models import ReviewLog, ProviderLog, \
    ServiceLog


def RepresentsInt(s):
    try:
        return int(s)
    except ValueError:
        return False


class ReviewLogging():

    def log_get(self, request):
        """Log the request"""
        user = str(getattr(request, 'user', ''))
        method = str(getattr(request, 'method', '')).upper()
        meta = getattr(request, 'META', '')
        ip = str(meta['REMOTE_ADDR'])
        request_path = str(getattr(request, 'path', ''))
        review_id = request_path.split('/')[-2]

        query_params = str(["%s: %s" % (k, v) for k, v in request.GET.items()])
        query_params = query_params if query_params else ''
        if RepresentsInt(review_id):
            print(review_id)
            ReviewLog.objects.create(ip=ip, review_id=review_id)


class ProviderLogging():

    def log_get(self, request):
        """Log the request"""
        user = str(getattr(request, 'user', ''))
        method = str(getattr(request, 'method', '')).upper()
        meta = getattr(request, 'META', '')
        ip = str(meta['REMOTE_ADDR'])
        request_path = str(getattr(request, 'path', ''))
        privider_id = request_path.split('/')[-2]

        query_params = str(["%s: %s" % (k, v) for k, v in request.GET.items()])
        query_params = query_params if query_params else ''
        if RepresentsInt(privider_id):
            ProviderLog.objects.create(ip=ip, provider_id=privider_id)


class ServiceLogging():

    def log_get(self, request):
        """Log the request"""
        user = str(getattr(request, 'user', ''))
        method = str(getattr(request, 'method', '')).upper()
        meta = getattr(request, 'META', '')
        ip = str(meta['REMOTE_ADDR'])
        request_path = str(getattr(request, 'path', ''))
        service_id = request_path.split('/')[-2]

        query_params = str(["%s: %s" % (k, v) for k, v in request.GET.items()])
        query_params = query_params if query_params else ''
        if RepresentsInt(service_id):
            ServiceLog.objects.create(ip=ip, service_id=service_id)
