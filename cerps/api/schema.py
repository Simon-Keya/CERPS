from rest_framework.schemas import get_schema_view
from rest_framework.documentation import include_docs_urls
from django.urls import path

schema_view = get_schema_view(
    title="CERPS API",
    description="API documentation for the College ERP System",
    version="1.0.0",
    public=True,
)

urlpatterns = [
    path("schema/", schema_view, name="openapi-schema"),
    path("docs/", include_docs_urls(title="CERPS API Docs")),
]
