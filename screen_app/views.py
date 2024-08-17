from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Screen, Product
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.templatetags.static import static  # Import the static function

@login_required
def display_screen_content(request):
    # Retrieve the logged-in user
    user = request.user

    # Filter Screen objects based on the logged-in user's manager status
    # and related to a Running product
    screens = Screen.objects.filter(manager=user, product__status='RUNNING')

    # Pass the filtered screens to the template
    return render(request, 'screen.html', {'screens': screens})

@login_required
def update_content(request):
    products = Product.objects.all()
    if request.method == 'POST':
        # Handle form submission to update content
        pass  # Add your logic here
    return render(request, 'update_content.html', {'products': products})

@staff_member_required
def activate_product(request):
    if request.method == "POST":
        product_id = request.POST.get("product")
        try:
            product = Product.objects.get(id=product_id)
            product.status = "RUNNING"
            product.save()

            # Set all other products to "Stopped" state
            other_products = Product.objects.exclude(id=product_id)
            for other_product in other_products:
                other_product.status = "STOPPED"
                other_product.save()

            # Redirect to display_screen_content view with the id of the running product
            return redirect('display_screen_content')
        except Product.DoesNotExist:
            # Handle case where selected product does not exist
            pass

    products = Product.objects.all()
    return render(request, 'activate_product.html', {'products': products})

def fetch_updated_video_data(request):
    # Retrieve updated video data from the database (e.g., Screen objects)
    updated_video_data = Screen.objects.filter(manager=request.user, product__status='RUNNING').exclude(video_path__isnull=True)

    # Construct the absolute URLs for the static video files
    serialized_video_data = []
    for screen in updated_video_data:
        video_url = static(screen.video_path)
        serialized_video_data.append({'video_path': video_url})

    # Return the serialized video data as JSON response
    return JsonResponse(serialized_video_data, safe=False)

def fetch_updated_pdf_data(request):
    # Retrieve updated PDF data from the database (e.g., Screen objects)
    updated_pdf_data = Screen.objects.filter(manager=request.user, product__status='RUNNING').exclude(pdf_path__isnull=True)

    # Construct the absolute URLs for the static PDF files
    serialized_pdf_data = []
    for screen in updated_pdf_data:
        pdf_url = static(screen.pdf_path)
        serialized_pdf_data.append({'pdf_path': pdf_url})

    # Return the serialized PDF data as JSON response
    return JsonResponse(serialized_pdf_data, safe=False)

def fetch_updated_data(request):
    # Assuming Screen model has fields video_path and pdf_path
    updated_data = []
    screens = Screen.objects.all()

    for screen in screens:
        updated_data.append({
            'video_path': static(screen.video_path),
            'pdf_path': static(screen.pdf_path),
        })

    return JsonResponse(updated_data, safe=False)


#----------------------------------------------------------------
# FixtureCleaningRecordView
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import ListView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import FixtureCleaningRecord
from .forms import FixtureCleaningRecordForm
from django.utils.decorators import method_decorator


@method_decorator(login_required, name='dispatch')
class AddFixtureCleaningRecordView(View):
    def get(self, request):
        form = FixtureCleaningRecordForm()
        return render(request, 'fixture_records/add_fixture_cleaning_record.html', {'form': form})

    def post(self, request):
        form = FixtureCleaningRecordForm(request.POST)
        if form.is_valid():
            fixture_record = form.save(commit=False)  # Create the object but don't save it yet
            fixture_record.operator_name = request.user  # Set the logged-in user as the operator_name
            fixture_record.save()  # Now save the object to the database
            return redirect('list_fixture_cleaning_records')
        return render(request, 'fixture_records/add_fixture_cleaning_record.html', {'form': form})


@method_decorator(staff_member_required, name='dispatch')
class ListFixtureCleaningRecordView(ListView):
    model = FixtureCleaningRecord
    template_name = 'fixture_records/list_fixture_cleaning_records.html'
    context_object_name = 'records'
    ordering = ['-date', '-time']

@method_decorator(staff_member_required, name='dispatch')
class UpdateFixtureCleaningRecordView(UpdateView):
    model = FixtureCleaningRecord
    form_class = FixtureCleaningRecordForm
    template_name = 'fixture_records/update_fixture_cleaning_record.html'
    success_url = reverse_lazy('list_fixture_cleaning_records')
    
@method_decorator(staff_member_required, name='dispatch')
class DeleteFixtureCleaningRecordView(DeleteView):
    model = FixtureCleaningRecord
    template_name = 'fixture_records/delete_fixture_cleaning_record.html'
    success_url = reverse_lazy('list_fixture_cleaning_records')

@method_decorator(staff_member_required, name='dispatch')
class FixtureCleaningRecordDetailView(View):
    def get(self, request, pk):
        record = get_object_or_404(FixtureCleaningRecord, pk=pk)
        return render(request, 'fixture_records/fixture_cleaning_record_detail.html', {'record': record})
    


# ----------------------------------------------------------------
# RejectionSheetForm 
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import ListView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import RejectionSheet
from .forms import RejectionSheetForm



@method_decorator(login_required, name='dispatch')
class AddRejectionSheetView(View):
    def get(self, request):
        form = RejectionSheetForm()
        return render(request, 'Rejection_records/add_rejection_sheet.html', {'form': form})

    def post(self, request):
        form = RejectionSheetForm(request.POST)
        if form.is_valid():
            rejection_sheet = form.save(commit=False)  # Create the object but don't save it yet
            rejection_sheet.operator_name = request.user  # Set the logged-in user as the operator_name
            rejection_sheet.save()  # Now save the object to the database
            return redirect('list_rejection_sheets')
        return render(request, 'Rejection_records/add_rejection_sheet.html', {'form': form})

@method_decorator(staff_member_required, name='dispatch')
class ListRejectionSheetView(ListView):
    model = RejectionSheet
    template_name = 'Rejection_records/list_rejection_sheets.html'
    context_object_name = 'sheets'
    ordering = ['-month', '-date']

@method_decorator(staff_member_required, name='dispatch')
class UpdateRejectionSheetView(UpdateView):
    model = RejectionSheet
    form_class = RejectionSheetForm
    template_name = 'Rejection_records/update_rejection_sheet.html'
    success_url = reverse_lazy('list_rejection_sheets')

@method_decorator(staff_member_required, name='dispatch')
class DeleteRejectionSheetView(DeleteView):
    model = RejectionSheet
    template_name = 'Rejection_records/delete_rejection_sheet.html'
    success_url = reverse_lazy('list_rejection_sheets')

@method_decorator(staff_member_required, name='dispatch')
class RejectionSheetDetailView(View):
    def get(self, request, pk):
        sheet = get_object_or_404(RejectionSheet, pk=pk)
        return render(request, 'Rejection_records/rejection_sheet_detail.html', {'sheet': sheet})
    

    
#----------------------------------------------------------------
# SolderingBitRecord 

from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import ListView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import SolderingBitRecord
from .forms import SolderingBitRecordForm




@method_decorator(login_required, name='dispatch')
class AddSolderingBitRecordView(View):
    def get(self, request):
        form = SolderingBitRecordForm()
        return render(request, 'SolderingBitRecord/add_soldering_bit_record.html', {'form': form})

    def post(self, request):
        form = SolderingBitRecordForm(request.POST)
        if form.is_valid():
            soldering_record = form.save(commit=False)
            soldering_record.operator_name = request.user  # Automatically set the operator name
            soldering_record.save()
            return redirect('list_soldering_bit_records')
        return render(request, 'SolderingBitRecord/add_soldering_bit_record.html', {'form': form})

@method_decorator(staff_member_required, name='dispatch')
class ListSolderingBitRecordView(ListView):
    model = SolderingBitRecord
    template_name = 'SolderingBitRecord/list_soldering_bit_records.html'
    context_object_name = 'records'
    ordering = ['-date', '-time']
    
    
@method_decorator(staff_member_required, name='dispatch')
class UpdateSolderingBitRecordView(UpdateView):
    model = SolderingBitRecord
    form_class = SolderingBitRecordForm
    template_name = 'SolderingBitRecord/update_soldering_bit_record.html'
    success_url = reverse_lazy('list_soldering_bit_records')
    
@method_decorator(staff_member_required, name='dispatch')
class DeleteSolderingBitRecordView(DeleteView):
    model = SolderingBitRecord
    template_name = 'SolderingBitRecord/delete_soldering_bit_record.html'
    success_url = reverse_lazy('list_soldering_bit_records')

class SolderingBitRecordDetailView(View):
    def get(self, request, pk):
        record = get_object_or_404(SolderingBitRecord, pk=pk)
        return render(request, 'SolderingBitRecord/soldering_bit_record_detail.html', {'record': record})
    
#----------------------------------------------------------------
 

from django.views import View
from django.views.generic import ListView, UpdateView, DeleteView
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from .models import DailyChecklistItem ,WeeklyChecklistItem ,MonthlyChecklistItem
from .forms import DailyChecklistItemForm,WeeklyChecklistItemForm ,MonthlyChecklistItemForm

from django.views import View
from django.shortcuts import render, redirect
from .forms import DailyChecklistItemForm



@method_decorator(login_required, name='dispatch')
class AddDailyChecklistItem(View):
    def get(self, request):
        form = DailyChecklistItemForm()
        return render(request, 'Maintenance/Daily/add_daily.html', {'form': form})

    def post(self, request):
        form = DailyChecklistItemForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('list_daily')
        else:
            print(form.errors)  

        return render(request, 'Maintenance/Daily/add_daily.html', {'form': form})



# ----------------------------------------------------------------
# Without Date filetring 

# from django.db.models import Q
# from django.utils.dateparse import parse_date

# class ListDailyChecklistItem(ListView):
#     model = DailyChecklistItem
#     template_name = 'Maintenance/Daily/list_daily.html'
#     context_object_name = 'records'
#     ordering = ['-month_year']
  

#     def get_queryset(self):
#         queryset = super().get_queryset()
#         query = self.request.GET.get('q')
#         if query:
#             queryset = queryset.filter(
#                 Q(doc_number__icontains=query) | 
#                 Q(machine_name__icontains=query) |
#                 Q(machine_location__icontains=query) |
#                 Q(month_year__icontains=query)            
#                 )
#         return queryset


#  With date filetering
from django.db.models import Q
from django.utils.dateparse import parse_date
from django.views.generic import ListView

@method_decorator(staff_member_required, name='dispatch')
class ListDailyChecklistItem(ListView):
    model = DailyChecklistItem
    template_name = 'Maintenance/Daily/list_daily.html'
    context_object_name = 'records'
    ordering = ['-month_year']

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('q')
        date_query = self.request.GET.get('date')

        if query:
            queryset = queryset.filter(
                Q(doc_number__icontains=query) |
                Q(machine_name__icontains=query) |
                Q(machine_location__icontains=query) |
                Q(month_year__icontains=query)
            )

        if date_query:
            try:
                date = parse_date(date_query)  # Convert the date string to a date object
                if date:
                    queryset = queryset.filter(date=date)
            except ValueError:
                # Handle invalid date format if needed
                pass

        return queryset



#----------------------------------------------------------------

#  with ending and starting date




# from django.db.models import Q
# from django.utils.dateparse import parse_date
# from django.views.generic import ListView

# class ListDailyChecklistItem(ListView):
#     model = DailyChecklistItem
#     template_name = 'Maintenance/Daily/list_daily.html'
#     context_object_name = 'records'
#     ordering = ['-month_year']

#     def get_queryset(self):
#         queryset = super().get_queryset()
#         query = self.request.GET.get('q')
#         start_date = self.request.GET.get('start_date')
#         end_date = self.request.GET.get('end_date')

#         if query:
#             queryset = queryset.filter(
#                 Q(doc_number__icontains=query) |
#                 Q(machine_name__icontains=query) |
#                 Q(machine_location__icontains=query) |
#                 Q(month_year__icontains=query)
#             )

#         if start_date and end_date:
#             try:
#                 start_date = parse_date(start_date)
#                 end_date = parse_date(end_date)
#                 if start_date and end_date:
#                     queryset = queryset.filter(date__range=(start_date, end_date))
#             except ValueError:
#                 # Handle invalid date format if needed
#                 pass

#         return queryset










@method_decorator(staff_member_required, name='dispatch')
class UpdateDailyChecklistItem(UpdateView):
    model = DailyChecklistItem
    form_class = DailyChecklistItemForm
    template_name = 'Maintenance/Daily/update_daily.html'
    success_url = reverse_lazy('list_daily')

@method_decorator(staff_member_required, name='dispatch')
class DeleteDailyChecklistItem(DeleteView):
    model = DailyChecklistItem
    template_name = 'Maintenance/Daily/delete_daily.html'
    success_url = reverse_lazy('list_daily')

@method_decorator(staff_member_required, name='dispatch')
class DailyChecklistItemDetailView(View):
    def get(self, request, pk):
        record = get_object_or_404(DailyChecklistItem, pk=pk)
        return render(request, 'Maintenance/Daily/daily_detail.html', {'record': record})

    



#  Weekly Checklist

@method_decorator(login_required, name='dispatch')
class AddWeeklyChecklistItem(View):
    def get(self, request):
        form = WeeklyChecklistItemForm()
        return render(request, 'Maintenance/weekly/add_weekly.html', {'form': form})

    def post(self, request):
        form = WeeklyChecklistItemForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('list_weekly')
        else:
            print(form.errors)  

        return render(request, 'Maintenance/weekly/add_weekly.html', {'form': form})


@method_decorator(staff_member_required, name='dispatch')
class ListWeeklyChecklistItem(ListView):
    model = WeeklyChecklistItem
    template_name = 'Maintenance/weekly/list_weekly.html'
    context_object_name = 'records'
    ordering = ['-month_year']

@method_decorator(staff_member_required, name='dispatch')
class UpdateWeeklyChecklistItem(UpdateView):
    model = WeeklyChecklistItem
    form_class = WeeklyChecklistItemForm
    template_name = 'Maintenance/weekly/update_weekly.html'
    success_url = reverse_lazy('list_weekly')


@method_decorator(staff_member_required, name='dispatch')
class DeleteWeeklyChecklistItem(DeleteView):
    model = WeeklyChecklistItem
    template_name = 'Maintenance/weekly/delete_weekly.html'
    success_url = reverse_lazy('list_weekly')


@method_decorator(staff_member_required, name='dispatch')
class WeeklyChecklistItemDetailView(View):
    def get(self, request, pk):
        record = get_object_or_404(WeeklyChecklistItem, pk=pk)
        return render(request, 'Maintenance/weekly/weekly_detail.html', {'record': record})


# Monthly

@method_decorator(login_required, name='dispatch')
class AddMonthlyChecklistItem(View):
    def get(self, request):
        form = MonthlyChecklistItemForm()
        return render(request, 'Maintenance/monthly/add_monthly.html', {'form': form})

    def post(self, request):
        form = MonthlyChecklistItemForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('list_monthly')
        else:
            print(form.errors)  

        return render(request, 'Maintenance/monthly/add_monthly.html', {'form': form})


@method_decorator(staff_member_required, name='dispatch')
class ListMonthlyChecklistItem(ListView):
    model = MonthlyChecklistItem
    template_name = 'Maintenance/monthly/list_monthly.html'
    context_object_name = 'records'
    ordering = ['-month_year']


@method_decorator(staff_member_required, name='dispatch')
class UpdateMonthlyChecklistItem(UpdateView):
    model = MonthlyChecklistItem
    form_class = MonthlyChecklistItemForm
    template_name = 'Maintenance/monthly/update_monthly.html'
    success_url = reverse_lazy('list_monthly')


@method_decorator(staff_member_required, name='dispatch')
class DeleteMonthlyChecklistItem(DeleteView):
    model = MonthlyChecklistItem
    template_name = 'Maintenance/monthly/delete_monthly.html'
    success_url = reverse_lazy('list_monthly')


@method_decorator(staff_member_required, name='dispatch')
class MonthlyChecklistItemDetailView(View):
    def get(self, request, pk):
        record = get_object_or_404(MonthlyChecklistItem, pk=pk)
        return render(request, 'Maintenance/monthly/monthly_detail.html', {'record': record})











# ----------------------------------------------------------------



from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import ControlChartReading, ControlChartStatistics
from .forms import ControlChartReadingForm

class ReadingListView(ListView):
    model = ControlChartReading
    context_object_name = 'readings'
    template_name = 'reading_list.html'
    ordering = ['-date']

class ReadingDetailView(DetailView):
    model = ControlChartReading
    context_object_name = 'reading'
    template_name = 'reading_detail.html'

class ReadingCreateView(CreateView):
    model = ControlChartReading
    form_class = ControlChartReadingForm
    template_name = 'reading_form.html'
    success_url = reverse_lazy('reading_list')

class ReadingUpdateView(UpdateView):
    model = ControlChartReading
    form_class = ControlChartReadingForm
    template_name = 'reading_form.html'
    success_url = reverse_lazy('reading_list')

class ReadingDeleteView(DeleteView):
    model = ControlChartReading
    context_object_name = 'reading'
    template_name = 'reading_confirm_delete.html'
    success_url = reverse_lazy('reading_list')

from django.shortcuts import render
from .models import ControlChartReading, ControlChartStatistics
from django.core.exceptions import ObjectDoesNotExist

from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from .models import ControlChartReading, ControlChartStatistics

def control_chart(request):
    # Fetch readings and statistics
    readings = ControlChartReading.objects.all()
    statistics = ControlChartStatistics.objects.all()
    
    # Debug prints
    print(f"Number of readings: {readings.count()}")
    print(f"Number of statistics: {statistics.count()}")
    
    # Calculate control limits
    try:
        control_limits = ControlChartStatistics.calculate_control_limits()
        print("Control limits:", control_limits)
    except Exception as e:
        print(f"Error calculating control limits: {e}")
        control_limits = {}

    # Calculate capability indices
    try:
        capability_indices = ControlChartStatistics.calculate_capability_indices(usl=375, lsl=355)
        print("Capability indices:", capability_indices)
    except Exception as e:
        print(f"Error calculating capability indices: {e}")
        capability_indices = {}

    # Pass context to template
    context = {
        'readings': readings,
        'statistics': statistics,
        'control_limits': control_limits,
        'capability_indices': capability_indices,
    }
    return render(request, 'control_chart.html', context)


from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def dashboard(request):
    return render(request, 'dashboard.html')