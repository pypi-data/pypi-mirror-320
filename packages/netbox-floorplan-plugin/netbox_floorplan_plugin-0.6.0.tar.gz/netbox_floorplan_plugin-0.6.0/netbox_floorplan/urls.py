from django.urls import path
from . import models, views
from netbox.views.generic import ObjectChangeLogView

urlpatterns = (
    path('floorplans/', views.FloorplanListView.as_view(), name='floorplan_list'),
    path('floorplans/racks/', views.FloorplanRackListView.as_view(), name='floorplan_rack_list'),
    path('floorplans/devices/', views.FloorplanDeviceListView.as_view(), name='floorplan_device_list'),
    path('floorplans/add/', views.FloorplanAddView.as_view(), name='floorplan_add'),
    path('floorplans/<int:pk>/edit/', views.FloorplanMapEditView.as_view(), name='floorplan_edit'),
    path('floorplans/<int:pk>/delete/', views.FloorplanDeleteView.as_view(), name='floorplan_delete'),
    path('floorplans/<int:pk>/changelog/', ObjectChangeLogView.as_view(), name='floorplan_changelog', kwargs={'model': models.Floorplan}),
    path('floorplans/floorplanimages/', views.FloorplanImageListView.as_view(), name='floorplanimage_list'),
    path('floorplans/floorplanimages/add/', views.FloorplanImageEditView.as_view(), name='floorplanimage_add'),
    path('floorplans/floorplanimages/<int:pk>/edit/', views.FloorplanImageEditView.as_view(), name='floorplanimage_edit'),
    path('floorplans/floorplanimages/<int:pk>/delete/', views.FloorplanImageDeleteView.as_view(), name='floorplanimage_delete'),
    path('floorplans/floorplanimages/<int:pk>/', views.FloorplanImageView.as_view(), name='floorplanimage'),
    path('floorplans/floorplanimages/<int:pk>/changelog/', ObjectChangeLogView.as_view(), name='floorplanimage_changelog', kwargs={'model': models.FloorplanImage}),
)
