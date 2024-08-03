from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage


def paginate(request, queryset, results):
    page = request.GET.get('page')
    paginator = Paginator(queryset, results)

    try:
        queryset = paginator.page(page)
    except PageNotAnInteger:
        page = 1
        queryset = paginator.page(page)
    except EmptyPage:
        page = paginator.num_pages
        queryset = paginator.page(page)

    right_index = int(page) + 5

    if right_index > paginator.num_pages:
        right_index = paginator.num_pages + 1

    left_index = int(page) - 4

    if left_index < 1:
        left_index = 1

    custom_range = range(left_index, right_index)
    return custom_range, queryset
