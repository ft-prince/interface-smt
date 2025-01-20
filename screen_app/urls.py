from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

from .views import (
    AddFixtureCleaningRecordView,
    ListFixtureCleaningRecordView,
    UpdateFixtureCleaningRecordView,
    DeleteFixtureCleaningRecordView,
    FixtureCleaningRecordDetailView,
    AddRejectionSheetView,
    ListRejectionSheetView,
    UpdateRejectionSheetView,
    DeleteRejectionSheetView,
    RejectionSheetDetailView,
    AddSolderingBitRecordView,
    ListSolderingBitRecordView,
    UpdateSolderingBitRecordView,
    DeleteSolderingBitRecordView,
    SolderingBitRecordDetailView,
    AddDailyChecklistItem,
    DailyChecklistItemDetailView,
    DeleteDailyChecklistItem,
    UpdateDailyChecklistItem,
    ListDailyChecklistItem,
    AddWeeklyChecklistItem,
    DeleteWeeklyChecklistItem,
   UpdateWeeklyChecklistItem,
   WeeklyChecklistItemDetailView,
   ListWeeklyChecklistItem,
   AddMonthlyChecklistItem,
   UpdateMonthlyChecklistItem,
   DeleteMonthlyChecklistItem,
   MonthlyChecklistItemDetailView,
   ListMonthlyChecklistItem,
    StartUpCheckSheetListView,
    startup_checksheet_create_view,
    StartUpCheckSheetDetailView,
    StartUpCheckSheetUpdateView,
    StartUpCheckSheetDeleteView,
    
    # fixture 
    ListFixtureCleaningRecordView,
    AddFixtureCleaningRecordView,
    UpdateFixtureCleaningRecordView,
    DeleteFixtureCleaningRecordView,
    FixtureCleaningRecordDetailView,
    AuditHistoryView

   
)


urlpatterns = [
    path('', views.display_screen_content, name='display_screen_content'),
    path('update_content/', views.update_content, name='update_content'),
    path('activate_product/', views.activate_product, name='activate_product'),
    path('fetch_updated_video_data/', views.fetch_updated_video_data, name='fetch_updated_video_data'),
    path('fetch_updated_pdf_data/', views.fetch_updated_pdf_data, name='fetch_updated_pdf_data'),
    path('fetch_updated_data/', views.fetch_updated_data, name='fetch_updated_data'),

# ----------------------------------------------------------------
    path('fixture/add/', AddFixtureCleaningRecordView.as_view(), name='add_fixture_cleaning_record'),
    path('fixture/list/', ListFixtureCleaningRecordView.as_view(), name='list_fixture_cleaning_records'),
    path('fixture/update/<int:pk>/', UpdateFixtureCleaningRecordView.as_view(), name='update_fixture_cleaning_record'),
    path('fixture/delete/<int:pk>/', DeleteFixtureCleaningRecordView.as_view(), name='delete_fixture_cleaning_record'),
    path('fixture/detail/<int:pk>/', FixtureCleaningRecordDetailView.as_view(), name='fixture_cleaning_record_detail'),
# ----------------------------------------------------------------
    path('rejection/add/', AddRejectionSheetView.as_view(), name='add_rejection_sheet'),
    path('rejection/list/', ListRejectionSheetView.as_view(), name='list_rejection_sheets'),
    path('rejection/update/<int:pk>/', UpdateRejectionSheetView.as_view(), name='update_rejection_sheet'),
    path('rejection/delete/<int:pk>/', DeleteRejectionSheetView.as_view(), name='delete_rejection_sheet'),
    path('rejection/detail/<int:pk>/', RejectionSheetDetailView.as_view(), name='rejection_sheet_detail'),
# ---------------------------------------------------------------- 
    path('soldering/add/', AddSolderingBitRecordView.as_view(), name='add_soldering_bit_record'),
    path('soldering/list/', ListSolderingBitRecordView.as_view(), name='list_soldering_bit_records'),
    path('soldering/update/<int:pk>/', UpdateSolderingBitRecordView.as_view(), name='update_soldering_bit_record'),
    path('soldering/delete/<int:pk>/', DeleteSolderingBitRecordView.as_view(), name='delete_soldering_bit_record'),
    path('soldering/detail/<int:pk>/', SolderingBitRecordDetailView.as_view(), name='soldering_bit_record_detail'),
# ----------------------------------------------------------------
    path('maintenance/add/', AddDailyChecklistItem.as_view(), name='add_daily'),
    path('maintenance/list/', ListDailyChecklistItem.as_view(), name='list_daily'),
    path('maintenance/update/<int:pk>/', UpdateDailyChecklistItem.as_view(), name='update_daily'),
    path('maintenance/delete/<int:pk>/', DeleteDailyChecklistItem.as_view(), name='delete_daily'),
    path('maintenance/detail/<int:pk>/', DailyChecklistItemDetailView.as_view(), name='daily_detail'),
# ----------------------------------------------------------------
    path('maintenance/weekly/add/', AddWeeklyChecklistItem.as_view(), name='add_weekly'),
    path('maintenance/weekly/list/', ListWeeklyChecklistItem.as_view(), name='list_weekly'),
    path('maintenance/weekly/update/<int:pk>/', UpdateWeeklyChecklistItem.as_view(), name='update_weekly'),
    path('maintenance/weekly/delete/<int:pk>/', DeleteWeeklyChecklistItem.as_view(), name='delete_weekly'),
    path('maintenance/weekly/detail/<int:pk>/', WeeklyChecklistItemDetailView.as_view(), name='weekly_detail'),
# ----------------------------------------------------------------
    path('maintenance/monthly/add/', AddMonthlyChecklistItem.as_view(), name='add_monthly'),
    path('maintenance/monthly/list/', ListMonthlyChecklistItem.as_view(), name='list_monthly'),
    path('maintenance/monthly/update/<int:pk>/', UpdateMonthlyChecklistItem.as_view(), name='update_monthly'),
    path('maintenance/monthly/delete/<int:pk>/', DeleteMonthlyChecklistItem.as_view(), name='delete_monthly'),
    path('maintenance/monthly/detail/<int:pk>/', MonthlyChecklistItemDetailView.as_view(), name='monthly_detail'),
# ----------------------------------------------------------------
    path('read/', views.ReadingListView.as_view(), name='reading_list'),
    path('reading/<int:pk>/', views.ReadingDetailView.as_view(), name='reading_detail'),
    path('reading/new/', views.ReadingCreateView.as_view(), name='reading_create'),
    path('reading/<int:pk>/edit/', views.ReadingUpdateView.as_view(), name='reading_update'),
    path('reading/<int:pk>/delete/', views.ReadingDeleteView.as_view(), name='reading_delete'),
    path('chart/', views.control_chart, name='control_chart'),

#  -------------------------------------------------------------------------------------------
    path('dashboard/', views.dashboard, name='dashboard'),
    path('web/', views.index, name='index'),
    path('startup/', StartUpCheckSheetListView.as_view(), name='checksheet_list'),
    path('startup/new/', views.startup_checksheet_create_view, name='checksheet_create'),
    path('startup/<int:pk>/', StartUpCheckSheetDetailView.as_view(), name='checksheet_detail'),
    path('startup/<int:pk>/edit/', StartUpCheckSheetUpdateView.as_view(), name='checksheet_edit'),
    path('startup/<int:pk>/delete/', StartUpCheckSheetDeleteView.as_view(), name='checksheet_delete'),

# ----------------------------------------------------------------
    path('get-process-info/<int:location_id>', views.get_process_info, name='get_process_info'),
    path('get-machine-skill/<int:machine_id>/', views.get_machine_skill, name='get_machine_skill'),
    
    # 

    path('pchart/', views.PChartDataListView.as_view(), name='pchart_list'),
    path('pchart/detail/<int:pk>/', views.PChartDataDetailView.as_view(), name='pchart_detail'),
    path('pchart/create/', views.PChartDataCreateView.as_view(), name='pchart_create'),
    path('pchart/update/<int:pk>/', views.PChartDataUpdateView.as_view(), name='pchart_update'),
    path('pchart/delete/<int:pk>/', views.PChartDataDeleteView.as_view(), name='pchart_delete'),
    path('pchart/chart/', views.PChartView.as_view(), name='pchart_chart'),

# ----------------------------------------------------------------
    path('audit-history/', AuditHistoryView.as_view(), name='audit_history'),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


