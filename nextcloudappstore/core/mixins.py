from nextcloudappstore.core.models import App, Category

########################################################################
class CategoryContextMixin(object):
    """Adds the catgeory list to the template context."""

    def get_context_data(self, **kwargs):
        context = super().get_context_data( **kwargs)
        context['categories'] = Category.objects.all()
        return context


########################################################################
class RecommendedAppsContextMixin(object):
    """Adds the recommended apps to the template context."""

    def get_context_data(self, **kwargs):
        context = super().get_context_data( **kwargs)
        #TODO: actually filter the recommended apps.
        context['recommended_apps'] = App.objects.all()
        return context
