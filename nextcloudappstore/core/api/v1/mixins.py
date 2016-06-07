from rest_framework.generics import GenericAPIView
from rest_framework.mixins import ListModelMixin, DestroyModelMixin


class ListDestroyAPIView(ListModelMixin, DestroyModelMixin, GenericAPIView):
    """
    Concrete view for listing or deleting a model instance.
    """

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


