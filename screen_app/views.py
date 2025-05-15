import math
from django.shortcuts import render, redirect
from django.http import Http404, HttpResponseRedirect, JsonResponse
from .models import QSF, ProcessMachineMapping, Screen, Product
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


def get_logo_path(self):
        """Get the absolute path to the logo file from static files"""
        return finders.find('images/company_logo.png')

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
from .forms import FixtureCleaningRecordForm,FixtureCleaningRecordSearchForm
from django.utils.decorators import method_decorator


from django.contrib import messages

@method_decorator(login_required, name='dispatch')
class AddFixtureCleaningRecordView(View):
    def get(self, request):
        form = FixtureCleaningRecordForm()
        qsf_documents = QSF.objects.all()  # Get all QSF documents for reference
        process_machine=ProcessMachineMapping.objects.all()        
        return render(request, 'fixture_records/add_fixture_cleaning_record.html', {
            
            'form': form,
            'qsf_documents': qsf_documents,
            'process_machine':process_machine
        })

    def post(self, request):
        form = FixtureCleaningRecordForm(request.POST)
        if form.is_valid():
            fixture_record = form.save(commit=False)
            fixture_record.operator_name = request.user
            fixture_record.request = request
            fixture_record.save()
            messages.success(request, "Fixture cleaning record added successfully.")
            return redirect('add_fixture_cleaning_record')
        else:
            messages.error(request, "There was an error adding the fixture cleaning record. Please check the form and try again.")
        return render(request, 'fixture_records/add_fixture_cleaning_record.html', {'form': form})

# views.py
from django.http import HttpResponse
import csv
from datetime import datetime
from django.db.models import Q
import xlsxwriter
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from django.contrib.staticfiles import finders
from reportlab.platypus import Image
from reportlab.lib.units import inch





class ListFixtureCleaningRecordView(ListView):
    model = FixtureCleaningRecord
    template_name = 'fixture_records/list_fixture_cleaning_records.html'
    context_object_name = 'records'
    ordering = ['-date', '-time']
    def get(self, request, *args, **kwargs):
        # Handle export requests separately
        export_format = request.GET.get('export')
        if export_format:
            queryset = self.get_filtered_queryset()
            return self.export_data(queryset, export_format)
        
        # Regular page display
        return super().get(request, *args, **kwargs)
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = FixtureCleaningRecordSearchForm(self.request.GET)
        return context

    def get_filtered_queryset(self):
        queryset = self.model.objects.all().order_by(*self.ordering)
        form = FixtureCleaningRecordSearchForm(self.request.GET)
        
        if form.is_valid():
            if start_date := form.cleaned_data.get('start_date'):
                queryset = queryset.filter(date__gte=start_date)
            if end_date := form.cleaned_data.get('end_date'):
                queryset = queryset.filter(date__lte=end_date)
            if fixture_location := form.cleaned_data.get('fixture_location'):
                queryset = queryset.filter(fixture_location=fixture_location)
            if shift := form.cleaned_data.get('shift'):
                queryset = queryset.filter(shift=shift)
            if verification_status := form.cleaned_data.get('verification_status'):
                queryset = queryset.filter(
                    Q(verification_tag_available=verification_status) |
                    Q(verification_tag_condition=verification_status)
                )
            if fixture_control_no := form.cleaned_data.get('fixture_control_no'):
                queryset = queryset.filter(fixture_control_no__icontains=fixture_control_no)
        
        return queryset

    def get_queryset(self):
        return self.get_filtered_queryset()


    def export_data(self, queryset, format):
        if format == 'excel':
            return self.export_excel(queryset)
        elif format == 'pdf':
            return self.export_pdf(queryset)

    def get_logo_path(self):
        """Get the absolute path to the logo file from static files"""
        return finders.find('images/image.png')
        

    def export_excel(self, queryset):
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet('Fixture Cleaning Records')
        # Insert logo
        logo_path = self.get_logo_path()
        if logo_path:
            worksheet.insert_image('A1', logo_path, {
                'x_scale': 0.5,
                'y_scale': 0.5,
                'x_offset': 10,
                'y_offset': 10
            })
        # Define formats
        header_format = workbook.add_format({
            'bold': True,
            'font_size': 12,
            'font_name': 'Arial',
            'bg_color': '#1E40AF',  # primaryColor
            'font_color': 'white',
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'text_wrap': True
        })

        cell_format = workbook.add_format({
            'font_size': 11,
            'font_name': 'Arial',
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'text_wrap': True
        })

        date_format = workbook.add_format({
            'font_size': 11,
            'font_name': 'Arial',
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'num_format': 'yyyy-mm-dd'
        })

        status_format_available = workbook.add_format({
            'font_size': 11,
            'font_name': 'Arial',
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#DCF5DC'  # Light green background
        })

        status_format_not_available = workbook.add_format({
            'font_size': 11,
            'font_name': 'Arial',
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#FFE6E6'  # Light red background
        })

        # Set column widths
        worksheet.set_column('A:A', 15)  # Control No
        worksheet.set_column('B:B', 20)  # Location
        worksheet.set_column('C:C', 8)   # Shift
        worksheet.set_column('D:D', 12)  # Date
        worksheet.set_column('E:E', 20)  # Operator Name
        worksheet.set_column('F:I', 15)  # Status columns

        # Write title
        title_format = workbook.add_format({
            'bold': True,
            'font_size': 16,
            'font_name': 'Arial',
            'align': 'center',
            'valign': 'vcenter',
            'font_color': '#1E40AF'  # primaryColor
        })
        worksheet.merge_range('A1:I1', 'Fixture Cleaning Records Report', title_format)
        worksheet.set_row(0, 30)  # Set title row height

        # Write timestamp
        timestamp_format = workbook.add_format({
            'italic': True,
            'font_size': 10,
            'align': 'right'
        })
        worksheet.merge_range('A2:I2', f'Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', timestamp_format)

        # Headers (start from row 3)
        headers = ['Control No', 'Location', 'Shift', 'Date', 'Operator Name', 
                  'Tag Available', 'Tag Condition', 'No Dust', 'No Epoxy Coating']
        for col, header in enumerate(headers):
            worksheet.write(3, col, header, header_format)

        # Write data
        for row, record in enumerate(queryset, start=4):
            worksheet.write(row, 0, record.fixture_control_no, cell_format)
            worksheet.write(row, 1, record.fixture_location, cell_format)
            worksheet.write(row, 2, record.shift, cell_format)
            worksheet.write(row, 3, record.date, date_format)
            worksheet.write(row, 4, record.operator_name.username if record.operator_name else '-', cell_format)
            
            # Status columns with conditional formatting
            for col, status in enumerate([record.verification_tag_available, 
                                       record.verification_tag_condition,
                                       record.no_dust_on_fixture,
                                       record.no_epoxy_coating_on_fixture], 5):
                format_to_use = status_format_available if status == 'Available' else status_format_not_available
                worksheet.write(row, col, status, format_to_use)

        workbook.close()
        output.seek(0)

        response = HttpResponse(
            output.read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename=fixture_cleaning_records_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        return response

    def export_pdf(self, queryset):
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename=fixture_cleaning_records_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'


        # Create the PDF object using ReportLab
        doc = SimpleDocTemplate(
            response,
            pagesize=landscape(letter),
            rightMargin=30,
            leftMargin=30,
            topMargin=30,
            bottomMargin=30
        )

        # Container for PDF elements
        elements = []
         # Add logo
        logo_path = self.get_logo_path()
        if logo_path:
            im = Image(logo_path)
            # Set logo dimensions
            im.drawHeight = 0.50*inch
            im.drawWidth = 2.5*inch
            elements.append(im)
            elements.append(Spacer(1, 12))  # Add space after logo

        # Define styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1E40AF'),
            spaceAfter=30,
            alignment=1
        )

        # Add title
        elements.append(Paragraph('Fixture Cleaning Records Report', title_style))
        
        # Add timestamp
        timestamp_style = ParagraphStyle(
            'Timestamp',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.grey,
            alignment=2
        )
        elements.append(Paragraph(
            f'Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
            timestamp_style
        ))
        elements.append(Spacer(1, 20))

        # Prepare data for table
        data = [['Control No', 'Location', 'Shift', 'Date', 'Operator Name', 
                'Tag Available', 'Tag Condition', 'No Dust', 'No Epoxy Coating']]
        
        # Add data rows
        for record in queryset:
            data.append([
                record.fixture_control_no,
                record.fixture_location,
                record.shift,
                record.date.strftime('%Y-%m-%d'),
                record.operator_name.username if record.operator_name else '-',
                record.verification_tag_available,
                record.verification_tag_condition,
                record.no_dust_on_fixture,
                record.no_epoxy_coating_on_fixture
            ])

        # Calculate column widths based on content
        table_style = TableStyle([
            # Header styling
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E40AF')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            
            # Data rows
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWHEIGHTS', (0, 0), (-1, -1), 30),
        ])

        # Add conditional background colors for status columns
        for row_idx in range(1, len(data)):
            for col_idx in range(5, 9):  # Status columns (5-8)
                if data[row_idx][col_idx] == 'Available':
                    table_style.add('BACKGROUND', (col_idx, row_idx), (col_idx, row_idx), 
                                colors.HexColor('#DCF5DC'))
                elif data[row_idx][col_idx] == 'Not Available':
                    table_style.add('BACKGROUND', (col_idx, row_idx), (col_idx, row_idx), 
                                colors.HexColor('#FFE6E6'))

        # Create table with calculated column widths
        col_widths = [
            1.2*inch,  # Control No
            1.5*inch,  # Location
            0.7*inch,  # Shift
            1.0*inch,  # Date
            1.5*inch,  # Operator Name
            1.1*inch,  # Tag Available
            1.1*inch,  # Tag Condition
            1.1*inch,  # No Dust
            1.1*inch   # No Epoxy Coating
        ]
        
        table = Table(data, colWidths=col_widths, repeatRows=1)
        table.setStyle(table_style)
        elements.append(table)

        # Build the PDF document
        doc.build(elements)
        return response    
    
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
from .forms import RejectionSheetForm,RejectionSheetSearchForm



from django.contrib import messages
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views import View
from django.shortcuts import render, redirect
import json

@method_decorator(login_required, name='dispatch')
class AddRejectionSheetView(View):
    def get(self, request):
        form = RejectionSheetForm()
        qsf_documents = QSF.objects.all()
        process_machine = ProcessMachineMapping.objects.all()
        machine_name = None
        
        # Check if user is logged into a machine to pre-populate fields
        browser_key = request.session.get('browser_key')
        
        if browser_key:
            from machineapp.models import MachineLoginTracker
            active_login = MachineLoginTracker.objects.filter(
                browser_key=browser_key,
                is_active=True
            ).order_by('-created_at').first()
            
            if active_login and active_login.machine:
                machine_name = active_login.machine.name
                
                # Find the process machine mapping for this machine
                matching_process_machine = ProcessMachineMapping.objects.filter(
                    process=machine_name
                ).first()
                
                if matching_process_machine:
                    # Pre-select the process_machine in the form
                    form.fields['process_machine'].initial = matching_process_machine.id
                    
                    # Pre-select defect type based on machine
                    machine_lower = machine_name.lower()
                    
                    # Special case handling for Adhesive Application and PCB Screwing
                    if "adhesive application" in machine_lower:
                        form.fields['defect_type'].initial = "adhesive"
                        form.fields['defect'].initial = "Adhesive improper"
                    elif "pcba screwing" in machine_lower or "heat sink" in machine_lower or "heatsink" in machine_lower:
                        form.fields['defect_type'].initial = "pcb_screwing"
                        form.fields['defect'].initial = "Thermal Paste Shape not OK"
                    # Standard machine types
                    elif "visual" in machine_lower or "inspection" in machine_lower:
                        form.fields['defect_type'].initial = "visual"
                    elif "programming" in machine_lower or ("testing" in machine_lower and not "final" in machine_lower):
                        form.fields['defect_type'].initial = "programming"
                    elif "final testing" in machine_lower or "automatic" in machine_lower:
                        form.fields['defect_type'].initial = "automatic_testing"
                    else:
                        # Default to visual for unknown machines
                        form.fields['defect_type'].initial = "visual"

        # This context definition and render should be outside all the if statements
        context = {
            'form': form,
            'qsf_documents': qsf_documents,
            'process_machine': process_machine,
            'machine_name': machine_name,
            'model': {
                'VISUAL_CHOICES': json.dumps(RejectionSheet.VISUAL_CHOICES),
                'PROGRAMMING_CHOICES': json.dumps(RejectionSheet.PROGRAMMING_CHOICES),
                'AUTOMATIC_TESTING_CHOICES': json.dumps(RejectionSheet.AUTOMATIC_TESTING_CHOICES),
                'ADHESIVE_CHOICES': json.dumps(RejectionSheet.ADHESIVE_CHOICES),
                'PCB_SCREWING_CHOICES': json.dumps(RejectionSheet.PCB_SCREWING_CHOICES),
            }
        }
        return render(request, 'Rejection_records/add_rejection_sheet.html', context)
    
    def post(self, request):
        form = RejectionSheetForm(request.POST)
        
        # Print form data for debugging
        print("Form data:", request.POST)
        
        # Check if total_rejection_qty is 0, if so, temporarily make defect fields not required
        total_rejection_qty = request.POST.get('total_rejection_qty', '0')
        if total_rejection_qty == '0':
            form.fields['defect'].required = False
            form.fields['defect_type'].required = False
        
        if form.is_valid():
            rejection_sheet = form.save(commit=False)
            rejection_sheet.operator_name = request.user
            
            # Handle the "Others" option
            if rejection_sheet.defect == 'Others' and request.POST.get('custom_defect'):
                custom_defect_text = request.POST.get('custom_defect')
                rejection_sheet.custom_defect = custom_defect_text
            
            # Pass the request to the model for context
            rejection_sheet.request = request
            
            try:
                rejection_sheet.save()
                messages.success(request, "Rejection sheet added successfully.")
                return redirect('add_rejection_sheet')
            except Exception as e:
                print(f"Error saving: {str(e)}")
                messages.error(request, f"Error saving: {str(e)}")
        else:
            # Print detailed form errors
            for field, errors in form.errors.items():
                error_msg = f"Field '{field}': {', '.join(errors)}"
                print(error_msg)
                messages.error(request, error_msg)
        
        # If form validation fails, pass along the context again
        qsf_documents = QSF.objects.all()
        process_machine = ProcessMachineMapping.objects.all()
        
        context = {
            'form': form,
            'qsf_documents': qsf_documents,
            'process_machine': process_machine,
            'model': {
                'VISUAL_CHOICES': json.dumps(RejectionSheet.VISUAL_CHOICES),
                'PROGRAMMING_CHOICES': json.dumps(RejectionSheet.PROGRAMMING_CHOICES),
                'AUTOMATIC_TESTING_CHOICES': json.dumps(RejectionSheet.AUTOMATIC_TESTING_CHOICES),
                'ADHESIVE_CHOICES': json.dumps(RejectionSheet.ADHESIVE_CHOICES),
                'PCB_SCREWING_CHOICES': json.dumps(RejectionSheet.PCB_SCREWING_CHOICES),
            }
        }
        
        messages.error(request, "There was an error adding the rejection sheet. Please check the form and try again.")
        return render(request, 'Rejection_records/add_rejection_sheet.html', context)    
      
@method_decorator(staff_member_required, name='dispatch')
class ListRejectionSheetView(ListView):
    model = RejectionSheet
    template_name = 'Rejection_records/list_rejection_sheets.html'
    context_object_name = 'sheets'
    ordering = ['-month', '-date']

    def get(self, request, *args, **kwargs):
        export_format = request.GET.get('export')
        if export_format:
            queryset = self.get_filtered_queryset()
            return self.export_data(queryset, export_format)
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = RejectionSheetSearchForm(self.request.GET)
        return context

    def get_filtered_queryset(self):
        queryset = self.model.objects.all().order_by(*self.ordering)
        form = RejectionSheetSearchForm(self.request.GET)
        
        if form.is_valid():
            if start_date := form.cleaned_data.get('start_date'):
                queryset = queryset.filter(date__gte=start_date)
            if end_date := form.cleaned_data.get('end_date'):
                queryset = queryset.filter(date__lte=end_date)
            if station := form.cleaned_data.get('station'):
                queryset = queryset.filter(station=station)
            if stage := form.cleaned_data.get('stage'):
                queryset = queryset.filter(stage=stage)
            if part_description := form.cleaned_data.get('part_description'):
                queryset = queryset.filter(part_description=part_description)
        
        return queryset

    def get_queryset(self):
        return self.get_filtered_queryset()

    def export_data(self, queryset, format):
        if format == 'excel':
            return self.export_excel(queryset)
        elif format == 'pdf':
            return self.export_pdf(queryset)
    def get_logo_path(self):
        """Get the absolute path to the logo file from static files"""
        return finders.find('images/image.png')
    
    
    def export_excel(self, queryset):
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet('Rejection Sheets')
        # Insert logo
        logo_path = self.get_logo_path()
        if logo_path:
            worksheet.insert_image('A1', logo_path, {
                'x_scale': 0.5,
                'y_scale': 0.5,
                'x_offset': 10,
                'y_offset': 10
            })

        # Define formats
        header_format = workbook.add_format({
            'bold': True,
            'font_size': 12,
            'font_name': 'Arial',
            'bg_color': '#1E40AF',
            'font_color': 'white',
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'text_wrap': True
        })

        cell_format = workbook.add_format({
            'font_size': 11,
            'font_name': 'Arial',
            'border': 1,
            'align': 'center',
            'valign': 'vcenter'
        })

        # Set column widths
        column_widths = {
            'A:A': 15,  # Station
            'B:B': 12,  # Stage
            'C:C': 25,  # Part Description
            'D:D': 15,  # Opening Balance
            'E:E': 15,  # Receive from Rework
            'F:F': 15,  # Total Pass Qty
            'G:G': 15,  # Total Rejection Qty
            'H:H': 15,  # Closing Balance
            'I:I': 20,  # Operator
            'J:J': 15,  # Month
        }
        
        for cols, width in column_widths.items():
            worksheet.set_column(cols, width)

        # Write title
        title_format = workbook.add_format({
            'bold': True,
            'font_size': 16,
            'font_name': 'Arial',
            'align': 'center',
            'valign': 'vcenter',
            'font_color': '#1E40AF'
        })
        worksheet.merge_range('A1:J1', 'Rejection Sheets Report', title_format)
        worksheet.set_row(0, 30)

        # Write timestamp
        worksheet.merge_range('A2:J2', 
                            f'Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', 
                            workbook.add_format({'align': 'right', 'italic': True}))

        # Headers
        headers = ['Station', 'Stage', 'Part Description', 'Opening Balance', 
                  'Receive from Rework', 'Total Pass Qty', 'Total Rejection Qty', 
                  'Closing Balance', 'Operator', 'Month']
        
        for col, header in enumerate(headers):
            worksheet.write(3, col, header, header_format)

        # Write data
        for row, sheet in enumerate(queryset, start=4):
            data = [
                sheet.station,
                sheet.stage,
                sheet.part_description,
                sheet.opening_balance,
                sheet.receive_from_rework,
                sheet.total_pass_qty,
                sheet.total_rejection_qty,
                sheet.closing_balance,
                sheet.operator_name.username if sheet.operator_name else '-',
                sheet.month.strftime('%B %Y')
            ]
            for col, value in enumerate(data):
                worksheet.write(row, col, value, cell_format)

        workbook.close()
        output.seek(0)

        response = HttpResponse(
            output.read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename=rejection_sheets_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        return response

    def export_pdf(self, queryset):
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename=rejection_sheets_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'

        doc = SimpleDocTemplate(
            response,
            pagesize=landscape(letter),
            rightMargin=30,
            leftMargin=30,
            topMargin=30,
            bottomMargin=30
        )

        elements = []
    # Add logo
        logo_path = self.get_logo_path()
        if logo_path:
            im = Image(logo_path)
            # Set logo dimensions
            im.drawHeight = 0.50*inch
            im.drawWidth = 2.5*inch
            elements.append(im)
            elements.append(Spacer(1, 12))  # Add space after logo

        # Title
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1E40AF'),
            spaceAfter=30,
            alignment=1
        )
        elements.append(Paragraph('Rejection Sheets Report', title_style))
        
        # Timestamp
        timestamp_style = ParagraphStyle(
            'Timestamp',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.grey,
            alignment=2
        )
        elements.append(Paragraph(
            f'Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
            timestamp_style
        ))
        elements.append(Spacer(1, 20))

        # Table data
        data = [['Station', 'Stage', 'Part Description', 'Opening Balance', 
                 'Receive from Rework', 'Total Pass Qty', 'Total Rejection Qty', 
                 'Closing Balance', 'Operator', 'Month']]
        
        for sheet in queryset:
            data.append([
                sheet.station,
                sheet.stage,
                sheet.part_description,
                str(sheet.opening_balance),
                str(sheet.receive_from_rework),
                str(sheet.total_pass_qty),
                str(sheet.total_rejection_qty),
                str(sheet.closing_balance),
                sheet.operator_name.username if sheet.operator_name else '-',
                sheet.month.strftime('%B %Y')
            ])

        # Table style
        table_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E40AF')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWHEIGHTS', (0, 0), (-1, -1), 30),
        ])

        # Create table with column widths
        col_widths = [
            1.0*inch,  # Station
            0.7*inch,  # Stage
            1.5*inch,  # Part Description
            1.0*inch,  # Opening Balance
            1.0*inch,  # Receive from Rework
            1.0*inch,  # Total Pass Qty
            1.0*inch,  # Total Rejection Qty
            1.0*inch,  # Closing Balance
            1.2*inch,  # Operator
            1.0*inch,  # Month
        ]
        
        table = Table(data, colWidths=col_widths, repeatRows=1)
        table.setStyle(table_style)
        elements.append(table)

        doc.build(elements)
        return response
    
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
from .models import SolderingBitRecord,Defects
from .forms import SolderingBitRecordForm,SolderingBitRecordSearchForm




from django.contrib import messages
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views import View
from django.shortcuts import render, redirect

@method_decorator(login_required, name='dispatch')
class AddSolderingBitRecordView(View):
    def get(self, request):
        form = SolderingBitRecordForm()
        return render(request, 'SolderingBitRecord/add_soldering_bit_record.html', {'form': form})

    def post(self, request):
        form = SolderingBitRecordForm(request.POST)
        
        if form.is_valid():
            soldering_bit_record = form.save(commit=False)
            soldering_bit_record.operator_name = request.user
            
            # Handle the defect fields properly
            defect_type = request.POST.get('defect_type', '')
            defect = request.POST.get('defect', '')
            custom_defect = request.POST.get('custom_defect', '')
            
            if defect_type:
                soldering_bit_record.defect_type = defect_type
                soldering_bit_record.defect = defect
                
                if defect == 'Others' and custom_defect:
                    soldering_bit_record.custom_defect = custom_defect
                else:
                    soldering_bit_record.custom_defect = ''
            else:
                # No defect type selected
                soldering_bit_record.defect_type = None
                soldering_bit_record.defect = None
                soldering_bit_record.custom_defect = None
            
            soldering_bit_record.save()
            messages.success(request, "Soldering bit record added successfully.")
            return redirect('add_soldering_bit_record')
        else:
            messages.error(request, "There was an error adding the soldering bit record. Please check the form and try again.")
            return render(request, 'SolderingBitRecord/add_soldering_bit_record.html', {'form': form})
    
@method_decorator(staff_member_required, name='dispatch')
class ListSolderingBitRecordView(ListView):
    model = SolderingBitRecord
    template_name = 'SolderingBitRecord/list_soldering_bit_records.html'
    context_object_name = 'records'
    ordering = ['-date', '-time']

    def get(self, request, *args, **kwargs):
        export_format = request.GET.get('export')
        if export_format:
            queryset = self.get_filtered_queryset()
            return self.export_data(queryset, export_format)
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = SolderingBitRecordSearchForm(self.request.GET)
        return context

    def get_filtered_queryset(self):
        queryset = self.model.objects.all().order_by(*self.ordering)
        form = SolderingBitRecordSearchForm(self.request.GET)
        
        if form.is_valid():
            if start_date := form.cleaned_data.get('start_date'):
                queryset = queryset.filter(date__gte=start_date)
            if end_date := form.cleaned_data.get('end_date'):
                queryset = queryset.filter(date__lte=end_date)
            if machine_no := form.cleaned_data.get('machine_no'):
                queryset = queryset.filter(machine_no=machine_no)
            if machine_location := form.cleaned_data.get('machine_location'):
                queryset = queryset.filter(machine_location=machine_location)
            if part_name := form.cleaned_data.get('part_name'):
                queryset = queryset.filter(part_name=part_name)
            if bit_size := form.cleaned_data.get('bit_size'):
                queryset = queryset.filter(bit_size=bit_size)
        
        return queryset

    def get_queryset(self):
        return self.get_filtered_queryset()
    def get_logo_path(self):
        """Get the absolute path to the logo file from static files"""
        return finders.find('images/image.png')
    def export_excel(self, queryset):
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet('Soldering Bit Records')
        # Insert logo
        logo_path = self.get_logo_path()
        if logo_path:
            worksheet.insert_image('A1', logo_path, {
                'x_scale': 0.5,
                'y_scale': 0.5,
                'x_offset': 10,
                'y_offset': 10
            })

        # Define formats
        title_format = workbook.add_format({
            'bold': True,
            'font_size': 16,
            'font_name': 'Arial',
            'align': 'center',
            'valign': 'vcenter',
            'font_color': '#1E40AF'
        })

        header_format = workbook.add_format({
            'bold': True,
            'font_size': 12,
            'font_name': 'Arial',
            'bg_color': '#1E40AF',
            'font_color': 'white',
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'text_wrap': True
        })

        cell_format = workbook.add_format({
            'font_size': 11,
            'font_name': 'Arial',
            'border': 1,
            'align': 'center',
            'valign': 'vcenter'
        })

        number_format = workbook.add_format({
            'font_size': 11,
            'font_name': 'Arial',
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'num_format': '#,##0'
        })

        # Set column widths
        column_widths = {
            'A:A': 15,  # Doc No
            'B:B': 20,  # Part Name
            'C:C': 15,  # Machine No
            'D:D': 20,  # Location
            'E:E': 12,  # Bit Size
            'F:F': 15,  # Date
            'G:G': 15,  # Shift A Qty
            'H:H': 15,  # Shift B Qty
            'I:I': 15,  # Total Qty
            'J:J': 20,  # Total Points
            'K:K': 20,  # Life Remaining
            'L:L': 15,  # Change Date
        }
        
        for cols, width in column_widths.items():
            worksheet.set_column(cols, width)

        # Write title
        worksheet.merge_range('A1:L1', 'Soldering Bit Records Report', title_format)
        worksheet.set_row(0, 30)

        # Write timestamp
        worksheet.merge_range('A2:L2', 
                            f'Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', 
                            workbook.add_format({'align': 'right', 'italic': True}))

        # Headers
        headers = [
            'Doc No', 'Part Name', 'Machine No', 'Location', 'Bit Size', 'Date',
            'Shift A Qty', 'Shift B Qty', 'Total Qty', 'Total Points',
            'Life Remaining', 'Change Date'
        ]
        
        for col, header in enumerate(headers):
            worksheet.write(3, col, header, header_format)

        # Write data
        for row, record in enumerate(queryset, start=4):
            data = [
                record.doc_number,
                record.get_part_name_display(),
                record.machine_no.location_name,
                record.get_machine_location_display(),
                record.get_bit_size_display(),
                record.date.strftime('%Y-%m-$d'),
                record.produce_quantity_shift_a,
                record.produce_quantity_shift_b,
                record.total_quantity,
                record.total_soldering_points,
                record.bit_life_remaining,
                record.bit_change_date.strftime('%Y-%m-%d')
            ]
            
            for col, value in enumerate(data):
                format_to_use = number_format if isinstance(value, (int, float)) else cell_format
                worksheet.write(row, col, value, format_to_use)

        workbook.close()
        output.seek(0)

        response = HttpResponse(
            output.read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename=soldering_bit_records_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        return response

    def export_pdf(self, queryset):
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename=soldering_bit_records_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'

        doc = SimpleDocTemplate(
            response,
            pagesize=landscape(letter),
            rightMargin=30,
            leftMargin=30,
            topMargin=30,
            bottomMargin=30
        )

        elements = []
         # Add logo
        logo_path = self.get_logo_path()
        if logo_path:
            im = Image(logo_path)
            # Set logo dimensions
            im.drawHeight = 0.50*inch
            im.drawWidth = 2.5*inch
            elements.append(im)
            elements.append(Spacer(1, 12))  # Add space after logo        

        # Title
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1E40AF'),
            spaceAfter=30,
            alignment=1
        )
        elements.append(Paragraph('Soldering Bit Records Report', title_style))
        
        # Timestamp
        timestamp_style = ParagraphStyle(
            'Timestamp',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.grey,
            alignment=2
        )
        elements.append(Paragraph(
            f'Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
            timestamp_style
        ))
        elements.append(Spacer(1, 20))

        # Table data
        headers = ['Doc No', 'Part Name', 'Machine No', 'Location', 'Bit Size', 'Date',
         'Shift A Qty', 'Shift B Qty', 'Total Qty', 'Total Points',
         'Life Remaining', 'Change Date']
        data = [headers]
        
        for record in queryset:
            data.append([
                record.doc_number,
                record.get_part_name_display(),
                record.machine_no.location_name,
                record.get_machine_location_display(),
                record.get_bit_size_display(),
                record.date.strftime('%Y-%m-%d'),
                str(record.produce_quantity_shift_a),
                str(record.produce_quantity_shift_b),
                str(record.total_quantity),
                str(record.total_soldering_points),
                str(record.bit_life_remaining),
                record.bit_change_date.strftime('%Y-%m-%d')
            ])

        # Table style
        table_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E40AF')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWHEIGHTS', (0, 0), (-1, -1), 30),
        ])

        # Create table with column widths
        col_widths = [0.8*inch] * 12  # Equal widths for all columns
        table = Table(data, colWidths=col_widths, repeatRows=1)
        table.setStyle(table_style)
        elements.append(table)

        doc.build(elements)
        return response

    def export_data(self, queryset, format):
        if format == 'excel':
            return self.export_excel(queryset)
        elif format == 'pdf':
            return self.export_pdf(queryset)    
    
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
from .forms import DailyChecklistItemForm,WeeklyChecklistItemForm ,MonthlyChecklistItemForm,MonthlyChecklistItemSearchForm

from django.views import View
from django.shortcuts import render, redirect
from .forms import DailyChecklistItemForm,DailyChecklistItemSearchForm,WeeklyChecklistItemSearchForm



@method_decorator(login_required, name='dispatch')
class AddDailyChecklistItem(View):
    def get(self, request):
        form = DailyChecklistItemForm()
        qsf_documents = QSF.objects.all()  # Get all QSF documents for reference
        process_machine=ProcessMachineMapping.objects.all()
        return render(request, 'Maintenance/Daily/add_daily.html', {
            'form': form,
            'qsf_documents': qsf_documents,
            'process_machine':process_machine
        })

    def post(self, request):
        form = DailyChecklistItemForm(request.POST)

    
        if form.is_valid():
            daily_checklist_item = form.save(commit=False)
            
            try:
                daily_checklist_item.manager = request.user
                daily_checklist_item.request = request

                daily_checklist_item.save()
                messages.success(request, 'Daily checklist item added successfully.')
                return redirect('add_daily')
            except Exception as e:
                    messages.error(request, f'Error saving checklist item: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')

        return render(request, 'Maintenance/Daily/add_daily.html', {'form': form})





#  With date filetering
from django.db.models import Q
from django.utils.dateparse import parse_date
from django.views.generic import ListView

@method_decorator(staff_member_required, name='dispatch')
class ListDailyChecklistItem(ListView):
    model = DailyChecklistItem
    template_name = 'Maintenance/Daily/list_daily.html'
    context_object_name = 'records'
    ordering = ['-month_year', '-date']

    def get(self, request, *args, **kwargs):
        export_format = request.GET.get('export')
        if export_format:
            queryset = self.get_filtered_queryset()
            return self.export_data(queryset, export_format)
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = DailyChecklistItemSearchForm(self.request.GET)
        return context

    def get_filtered_queryset(self):
        queryset = self.model.objects.all().order_by(*self.ordering)
        form = DailyChecklistItemSearchForm(self.request.GET)
        
        if form.is_valid():
            if start_date := form.cleaned_data.get('start_date'):
                queryset = queryset.filter(date__gte=start_date)
            if end_date := form.cleaned_data.get('end_date'):
                queryset = queryset.filter(date__lte=end_date)
            if machine_name := form.cleaned_data.get('machine_name'):
                queryset = queryset.filter(machine_name=machine_name)
            if machine_location := form.cleaned_data.get('machine_location'):
                queryset = queryset.filter(machine_location=machine_location)
            if check_status := form.cleaned_data.get('check_status'):
                status_filter = Q()
                for i in range(1, 8):
                    status_filter |= Q(**{f'Remark_{i}': check_status})
                queryset = queryset.filter(status_filter)

        return queryset

    def get_queryset(self):
        return self.get_filtered_queryset()
    def get_logo_path(self):
        """Get the absolute path to the logo file from static files"""
        return finders.find('images/image.png')
    
    def export_excel(self, queryset):
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet('Daily Checklist Items')
        
        # Set column widths - Updated with new columns
        column_widths = {
            'A:A': 20,  # Doc No
            'B:B': 15,  # Rev No
            'C:C': 15,  # Rev Date
            'D:D': 25,  # Machine Name
            'E:E': 20,  # Control Number
            'F:F': 20,  # Process Number
            'G:G': 30,  # Machine Location
            'H:H': 18,  # Date
            'I:I': 60,  # Check Points
            'J:J': 30,  # Requirements
            'K:K': 15,  # Status
        }
        
        for cols, width in column_widths.items():
            worksheet.set_column(cols, width)
        
        # Define formats
        title_format = workbook.add_format({
            'bold': True,
            'font_size': 24,
            'font_color': '#1E40AF',
            'align': 'center',
            'valign': 'vcenter'
        })
        
        subtitle_format = workbook.add_format({
            'italic': True,
            'font_size': 10,
            'font_color': '#666666',
            'align': 'right'
        })
        
        header_format = workbook.add_format({
            'bold': True,
            'font_size': 12,
            'bg_color': '#1E40AF',
            'font_color': 'white',
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'text_wrap': True
        })
        
        cell_format = workbook.add_format({
            'font_size': 11,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter'
        })
        
        # Logo placement - leave space at top
        row_offset = 6  # Start data after logo and title
        
        # Insert logo
        logo_path = self.get_logo_path()
        if logo_path:
            worksheet.insert_image('A1', logo_path, {
                'x_scale': 0.6,
                'y_scale': 1.2,
                'x_offset': 10,
                'y_offset': 10
            })
        
        # Add title - centered across columns (update columns range)
        worksheet.merge_range('A3:K3', 'Daily Checklist Report', title_format)
        
        # Add timestamp (update columns range)
        worksheet.merge_range('A4:K4', f'Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', subtitle_format)
        
        # Add some spacing
        worksheet.set_row(5, 20)  # Empty row for spacing
        
        # Write headers
        headers = [
            'Doc No', 'Rev No', 'Rev Date', 'Machine Name', 'Control Number', 'Process Number', 'Location', 'Date',
            'Check Points', 'Requirements', 'Status'
        ]
        
        for col, header in enumerate(headers):
            worksheet.write(row_offset, col, header, header_format)
        
        # Define hardcoded check points and requirements
        check_points = [
            'Clean Machine Surface',
            'Check ON/OFF Switch',
            'Check Emergency Switch',
            'Check any Abnormal Sound in M/C',
            'Check Spray Nozzle',
            'Check all Tubbing & Feeder pipe',
            'Check Maintenance & Calibration Tag'
        ]
        
        requirements = [
            'Proper Clean',
            'Proper Working',
            'Proper Working',
            'No any Abnormal Sound',
            'No Blockage No leakage',
            'No Cut & No Damage',
            'No Expiry date on tag'
        ]
        
        # Write data
        row = row_offset + 1
        for record in queryset:
            # Add a bit of spacing between different records
            if row > row_offset + 1:
                worksheet.set_row(row, 5)  # Small gap between records
                row += 1
                
            for i in range(1, 8):
                idx = i - 1  # Convert to 0-indexed for arrays
                remark = getattr(record, f'Remark_{i}')
                
                if i == 1:  # First row includes basic info
                    if hasattr(record, 'qsf_document') and record.qsf_document:
                        doc_number = record.qsf_document.doc_number
                        rev_number = record.qsf_document.rev_number
                        rev_date = record.qsf_document.rev_date.strftime('%Y-%m-%d') if record.rev_date else 'N/A'                    
                    else:
                        doc_number = getattr(record, 'doc_number', 'N/A')
                        rev_number = getattr(record, 'rev_number', 'N/A')
                        rev_date = getattr(record, 'rev_date', datetime.now()).strftime('%Y-%m-%d') if record.rev_date else 'N/A'                    
                    # Fix column indices to match the headers
                    worksheet.write(row, 0, doc_number, cell_format)
                    worksheet.write(row, 1, rev_number, cell_format)
                    worksheet.write(row, 2, rev_date, cell_format)
                    worksheet.write(row, 3, record.machine_name, cell_format)
                    worksheet.write(row, 4, record.control_number, cell_format)
                    
                    # Get process_no from process_machine if available
                    process_no = getattr(record.process_machine, 'process_no', 'N/A') if record.process_machine else 'N/A'
                    worksheet.write(row, 5, process_no, cell_format)
                    
                    # Check if machine_location is None before accessing location_name
                    location_name = record.machine_location.location_name if record.machine_location else 'N/A'
                    worksheet.write(row, 6, location_name, cell_format)
                    
                    worksheet.write(row, 7, record.date.strftime('%Y-%m-%d'), cell_format)
                    worksheet.write(row, 8, check_points[idx], cell_format)
                    worksheet.write(row, 9, requirements[idx], cell_format)
                    worksheet.write(row, 10, remark, cell_format)
                else:  # Subsequent rows only show check point data
                    worksheet.write(row, 0, "", cell_format)
                    worksheet.write(row, 1, "", cell_format)
                    worksheet.write(row, 2, "", cell_format)
                    worksheet.write(row, 3, "", cell_format)
                    worksheet.write(row, 4, "", cell_format)
                    worksheet.write(row, 5, "", cell_format)
                    worksheet.write(row, 6, "", cell_format)
                    worksheet.write(row, 7, "", cell_format)
                    worksheet.write(row, 8, check_points[idx], cell_format)
                    worksheet.write(row, 9, requirements[idx], cell_format)
                    worksheet.write(row, 10, remark, cell_format)
                
                row += 1
        
        # Add footer information (update columns range)
        row += 2  # Add space before footer
        footer_format = workbook.add_format({
            'font_size': 10,
            'italic': True,
            'align': 'center'
        })
        worksheet.merge_range(f'A{row}:K{row}', 'Confidential Document - For Internal Use Only', footer_format)
        
        workbook.close()
        output.seek(0)
        
        response = HttpResponse(
            output.read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename=daily_checklist_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        return response



    def export_pdf(self, queryset):
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename=daily_checklist_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'

        doc = SimpleDocTemplate(
            response,
            pagesize=landscape(letter),
            rightMargin=30,
            leftMargin=30,
            topMargin=30,
            bottomMargin=30
        )

        elements = []

        # Add logo
        logo_path = self.get_logo_path()
        if logo_path:
            logo = Image(logo_path)
            logo.drawHeight = 0.5 * inch
            logo.drawWidth = 2.5 * inch
            elements.append(logo)
            elements.append(Spacer(1, 12))

        # Add Title
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'TitleStyle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1E40AF'),
            alignment=1,
            spaceAfter=20
        )
        elements.append(Paragraph('Daily Checklist Report', title_style))

        # Add timestamp
        timestamp_style = ParagraphStyle(
            'Timestamp',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.grey,
            alignment=2
        )
        elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", timestamp_style))
        elements.append(Spacer(1, 20))

        # Table headers
        headers = [
            'Doc No', 'Rev No', 'Rev Date', 'Machine Name', 'Location', 'Date',
            'Check Points', 'Requirements', 'Status'
        ]
        data = [headers]

        # Static checklist items
        check_points = [
            'Clean Machine Surface',
            'Check ON/OFF Switch',
            'Check Emergency Switch',
            'Check any Abnormal Sound in M/C',
            'Check Spray Nozzle',
            'Check all Tubbing & Feeder pipe',
            'Check Maintenance & Calibration Tag'
        ]

        requirements = [
            'Proper Clean',
            'Proper Working',
            'Proper Working',
            'No any Abnormal Sound',
            'No Blockage No leakage',
            'No Cut & No Damage',
            'No Expiry date on tag'
        ]

        # Fill data
        for record in queryset:
            for i in range(1, 8):
                idx = i - 1
                remark = getattr(record, f'Remark_{i}')

                if i == 1:
                    # QSF Document fallback
                    if hasattr(record, 'qsf_document') and record.qsf_document:
                        doc_no = record.qsf_document.doc_number
                        rev_no = record.qsf_document.rev_number
                        # Add a check for None before calling strftime
                        rev_date = record.rev_date.strftime('%Y-%m-%d') if record.rev_date else 'N/A'
                    else:
                        doc_no = getattr(record, 'doc_number', 'N/A')
                        rev_no = getattr(record, 'rev_number', 'N/A')
                        rev_date = getattr(record, 'rev_date', datetime.now()).strftime('%Y-%m-%d') if record.rev_date else 'N/A'

                    data.append([
                        doc_no,
                        rev_no,
                        rev_date,
                        record.machine_name,

                        record.machine_location.location_name,
                        record.date.strftime('%Y-%m-%d'),
                        check_points[idx],
                        requirements[idx],
                        remark
                    ])
                else:
                    # Empty cells for repeated data
                    data.append(['', '', '', '', '', '', check_points[idx], requirements[idx], remark])

        # Table Styling
        table = Table(data, repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E40AF')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('BOX', (0, 0), (-1, -1), 1.25, colors.black),
            ('ROWHEIGHTS', (0, 0), (-1, -1), 25),
        ]))

        elements.append(table)

        # Optional: footer or end note
        elements.append(Spacer(1, 20))
        footer = Paragraph(
            'Confidential Document - For Internal Use Only',
            ParagraphStyle('FooterStyle', fontSize=10, alignment=1, italic=True)
        )
        elements.append(footer)

        # Build PDF
        doc.build(elements)
        return response




    def export_data(self, queryset, format):
            if format == 'excel':
                return self.export_excel(queryset)
            elif format == 'pdf':
                return self.export_pdf(queryset)

#----------------------------------------------------------------


@method_decorator(staff_member_required, name='dispatch')
class UpdateDailyChecklistItem(UpdateView):
    model = DailyChecklistItem
    form_class = DailyChecklistItemForm
    template_name = 'Maintenance/Daily/update_daily.html'
    success_url = reverse_lazy('list_daily')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['qsf_documents'] = QSF.objects.all()
        return context
    
    def form_valid(self, form):
        # Make sure qsf_document is set properly
        instance = form.save(commit=False)
        instance.qsf_document = form.cleaned_data.get('qsf_document')
        instance.save()
        return super().form_valid(form)
    
    
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
        qsf_documents = QSF.objects.all()  # Get all QSF documents for reference
        process_machine=ProcessMachineMapping.objects.all()
        
        
        return render(request, 'Maintenance/Weekly/add_weekly.html', {
            'form': form,
            'qsf_documents': qsf_documents,
            'process_machine':process_machine
        })
    def post(self, request):
        form = WeeklyChecklistItemForm(request.POST)
        

        if form.is_valid():
            weekly_checklist_item = form.save(commit=False)

            try:
                weekly_checklist_item.manager = request.user
                weekly_checklist_item.request = request
                
                weekly_checklist_item.save()
                messages.success(request, 'Weekly checklist item added successfully.')
                return redirect('add_weekly')
            except Exception as e:
                 messages.error(request, f'Error saving checklist item: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')

        return render(request, 'Maintenance/weekly/add_weekly.html', {'form': form})


from django.db.models import Q
from django.http import HttpResponse
from datetime import datetime
import xlsxwriter
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from io import BytesIO

@method_decorator(staff_member_required, name='dispatch')
class ListWeeklyChecklistItem(ListView):
    model = WeeklyChecklistItem
    template_name = 'Maintenance/weekly/list_weekly.html'
    context_object_name = 'records'
    ordering = ['-month_year']

    def get(self, request, *args, **kwargs):
        export_format = request.GET.get('export')
        if export_format:
            queryset = self.get_filtered_queryset()
            return self.export_data(queryset, export_format)
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = WeeklyChecklistItemSearchForm(self.request.GET)
        return context

    def get_filtered_queryset(self):
        queryset = self.model.objects.all().order_by(*self.ordering)
        form = WeeklyChecklistItemSearchForm(self.request.GET)
        
        if form.is_valid():
            if start_date := form.cleaned_data.get('start_date'):
                queryset = queryset.filter(date__gte=start_date)
            if end_date := form.cleaned_data.get('end_date'):
                queryset = queryset.filter(date__lte=end_date)
            if machine_name := form.cleaned_data.get('machine_name'):
                queryset = queryset.filter(machine_name=machine_name)
            if machine_location := form.cleaned_data.get('machine_location'):
                queryset = queryset.filter(machine_location=machine_location)
            if check_status := form.cleaned_data.get('check_status'):
                status_filter = Q()
                for i in range(8, 12):  # Weekly checklist has points 8-11
                    status_filter |= Q(**{f'Remark_{i}': check_status})
                queryset = queryset.filter(status_filter)
        
        return queryset

    def get_queryset(self):
        return self.get_filtered_queryset()
    def get_logo_path(self):
        """Get the absolute path to the logo file from static files"""
        return finders.find('images/image.png')
    
    def export_excel(self, queryset):
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet('Weekly Checklist Items')
        
        # Set column widths
        column_widths = {
            'A:A': 20,  # Doc No
            'B:B': 15,  # Rev No
            'C:C': 15,  # Rev Date
            'D:D': 25,  # Machine Name
            'E:E': 20,  # Control Number
            'F:F': 20,  # Process Number
            'G:G': 30,  # Machine Location
            'H:H': 18,  # Date
            'I:I': 60,  # Check Points
            'J:J': 30,  # Requirements
            'K:K': 15,  # Status
        }
        
        for cols, width in column_widths.items():
            worksheet.set_column(cols, width)
        
        # Define formats
        title_format = workbook.add_format({
            'bold': True,
            'font_size': 24,
            'font_color': '#1E40AF',
            'align': 'center',
            'valign': 'vcenter'
        })
        
        subtitle_format = workbook.add_format({
            'italic': True,
            'font_size': 10,
            'font_color': '#666666',
            'align': 'right'
        })
        
        header_format = workbook.add_format({
            'bold': True,
            'font_size': 12,
            'bg_color': '#1E40AF',
            'font_color': 'white',
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'text_wrap': True
        })
        
        cell_format = workbook.add_format({
            'font_size': 11,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter'
        })
        
        # Logo placement - leave space at top
        row_offset = 6  # Start data after logo and title
        
        # Insert logo
        logo_path = self.get_logo_path()
        if logo_path:
            worksheet.insert_image('A1', logo_path, {
                'x_scale': 0.6,
                'y_scale': 1.2,
                'x_offset': 10,
                'y_offset': 10
            })
        
        # Add title - centered across columns (update the range to match all columns)
        worksheet.merge_range('A3:K3', 'Weekly Checklist Report', title_format)
        
        # Add timestamp (update the range to match all columns)
        worksheet.merge_range('A4:K4', f'Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', subtitle_format)
        
        # Add some spacing
        worksheet.set_row(5, 20)  # Empty row for spacing
        
        # Write headers
        headers = [
            'Doc No', 'Rev No', 'Rev Date', 'Machine Name', 'Control Number', 'Process Number', 'Location', 'Date',
            'Check Points', 'Requirements', 'Status'
        ]

        
        for col, header in enumerate(headers):
            worksheet.write(row_offset, col, header, header_format)
        
        # Define hardcoded check points and requirements
        check_points = [
            'Check Conveyor Belts',
            'Check Solder bit Assembly. For any Bolts & Screw Loose',
            'Check Wire & Cable',
            'Electrical Insulation'
        ]
        
        requirements = [
            'No Damage',
            'Proper Tight',
            'No Damage No Broken',
            'No Cut & No Damage Wire'
        ]
        
        # Write data
        row = row_offset + 1
        for record in queryset:
            # Add a bit of spacing between different records
            if row > row_offset + 1:
                worksheet.set_row(row, 5)  # Small gap between records
                row += 1
                
            # Weekly uses checkpoints 8-11
            for i in range(8, 12):
                idx = i - 8  # Convert to 0-indexed for arrays
                remark = getattr(record, f'Remark_{i}')
                
                if i == 8:  # First row includes basic info
                    # Use qsf_document fields if available, otherwise fall back to direct attributes
                    if hasattr(record, 'qsf_document') and record.qsf_document:
                        doc_number = record.qsf_document.doc_number
                        rev_number = record.qsf_document.rev_number
                        rev_date = record.qsf_document.rev_date.strftime('%Y-%m-%d')
                    else:
                        doc_number = getattr(record, 'doc_number', 'N/A')
                        rev_number = getattr(record, 'rev_number', 'N/A')
                        rev_date = getattr(record, 'rev_date', datetime.now()).strftime('%Y-%m-%d') if record.rev_date else 'N/A'                    
                    
                    # Fix column indices and handle possible None values safely
                    worksheet.write(row, 0, doc_number, cell_format)
                    worksheet.write(row, 1, rev_number, cell_format)
                    worksheet.write(row, 2, rev_date, cell_format)
                    
                    # Handle machine_name as string, not a function call
                    worksheet.write(row, 3, record.machine_name or 'N/A', cell_format)
                    
                    # Add control_number
                    worksheet.write(row, 4, record.control_number or 'N/A', cell_format)
                    
                    # Get process_no from process_machine if available
                    process_no = getattr(record.process_machine, 'process_no', 'N/A') if record.process_machine else 'N/A'
                    worksheet.write(row, 5, process_no, cell_format)
                    
                    # Check if machine_location is None before accessing location_name
                    location_name = record.machine_location.location_name if record.machine_location else 'N/A'
                    worksheet.write(row, 6, location_name, cell_format)
                    
                    worksheet.write(row, 7, record.date.strftime('%Y-%m-%d'), cell_format)
                    worksheet.write(row, 8, check_points[idx], cell_format)
                    worksheet.write(row, 9, requirements[idx], cell_format)
                    worksheet.write(row, 10, remark, cell_format)
                else:  # Subsequent rows only show check point data
                    worksheet.write(row, 0, "", cell_format)
                    worksheet.write(row, 1, "", cell_format)
                    worksheet.write(row, 2, "", cell_format)
                    worksheet.write(row, 3, "", cell_format)
                    worksheet.write(row, 4, "", cell_format)
                    worksheet.write(row, 5, "", cell_format)
                    worksheet.write(row, 6, "", cell_format)
                    worksheet.write(row, 7, "", cell_format)
                    worksheet.write(row, 8, check_points[idx], cell_format)
                    worksheet.write(row, 9, requirements[idx], cell_format)
                    worksheet.write(row, 10, remark, cell_format)
                
                row += 1
        
        # Add footer information (update columns range)
        row += 2  # Add space before footer
        footer_format = workbook.add_format({
            'font_size': 10,
            'italic': True,
            'align': 'center'
        })
        worksheet.merge_range(f'A{row}:K{row}', 'Confidential Document - For Internal Use Only', footer_format)
        
        workbook.close()
        output.seek(0)
        
        response = HttpResponse(
            output.read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename=weekly_checklist_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        return response
    
    
    
    
    
    def export_pdf(self, queryset):
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename=weekly_checklist_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'

        doc = SimpleDocTemplate(
            response,
            pagesize=landscape(letter),
            rightMargin=30,
            leftMargin=30,
            topMargin=50,
            bottomMargin=30
        )

        elements = []
        styles = getSampleStyleSheet()

        # Header with logo and title
        logo_path = self.get_logo_path()
        if logo_path:
            im = Image(logo_path)
            im.drawHeight = 0.5 * inch
            im.drawWidth = 1.5 * inch

            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#1E40AF'),
                alignment=1
            )

            header_data = [[im, Paragraph('Weekly Checklist Report', title_style)]]
            header_table = Table(header_data, colWidths=[2 * inch, 6 * inch])
            header_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (0, 0), 'LEFT'),
                ('ALIGN', (1, 0), (1, 0), 'CENTER'),
                ('VALIGN', (0, 0), (1, 0), 'MIDDLE'),
            ]))
            elements.append(header_table)
        else:
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#1E40AF'),
                alignment=1
            )
            elements.append(Paragraph('Weekly Checklist Report', title_style))

        elements.append(Spacer(1, 20))

        # Timestamp
        elements.append(Paragraph(
            f'Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
            ParagraphStyle(
                'Timestamp',
                parent=styles['Normal'],
                fontSize=10,
                textColor=colors.grey,
                alignment=2
            )
        ))
        elements.append(Spacer(1, 30))

        para_style = ParagraphStyle(
            'WrappedText',
            parent=styles['Normal'],
            fontSize=10,
            leading=12,
            alignment=1
        )

        # Headers
        headers = [
            'Doc No', 'Rev No', 'Rev Date', 'Machine Name', 'Location', 'Date',
            'Check Points', 'Requirements', 'Status'
        ]
        header_paragraphs = [Paragraph(header, para_style) for header in headers]
        data = [header_paragraphs]

        check_points = [
            'Check Conveyor Belts',
            'Check Solder bit Assembly. For any Bolts & Screw Loose',
            'Check Wire & Cable',
            'Electrical Insulation'
        ]
        requirements = [
            'No Damage',
            'Proper Tight',
            'No Damage No Broken',
            'No Cut & No Damage Wire'
        ]

        for idx, record in enumerate(queryset):
            if idx > 0:
                data.append([''] * 9)

            # Use qsf_document fields if available
            if hasattr(record, 'qsf_document') and record.qsf_document:
                doc_number = record.qsf_document.doc_number
                rev_number = record.qsf_document.rev_number
                rev_date = record.rev_date.strftime('%Y-%m-%d')
            else:
                doc_number = getattr(record, 'doc_number', 'N/A')
                rev_number = getattr(record, 'rev_number', 'N/A')
                rev_date = getattr(record, 'rev_date', datetime.now()).strftime('%Y-%m-%d') if record.rev_date else 'N/A'                    

            for i in range(8, 12):
                cp_idx = i - 8
                remark = getattr(record, f'Remark_{i}', '')

                if i == 8:
                    row_data = [
                        Paragraph(str(doc_number), para_style),
                        Paragraph(str(rev_number), para_style),
                        Paragraph(rev_date, para_style),
                        Paragraph(record.machine_name, para_style),
                        Paragraph(record.machine_location.location_name, para_style),
                        Paragraph(record.date.strftime('%Y-%m-%d'), para_style),
                        Paragraph(check_points[cp_idx], para_style),
                        Paragraph(requirements[cp_idx], para_style),
                        Paragraph(remark, para_style),
                    ]
                else:
                    row_data = [
                        Paragraph('', para_style),
                        Paragraph('', para_style),
                        Paragraph('', para_style),
                        Paragraph('', para_style),
                        Paragraph('', para_style),
                        Paragraph('', para_style),
                        Paragraph(check_points[cp_idx], para_style),
                        Paragraph(requirements[cp_idx], para_style),
                        Paragraph(remark, para_style),
                    ]
                data.append(row_data)

        col_widths = [70, 50, 70, 90, 90, 70, 160, 120, 60]

        table = Table(data, colWidths=col_widths, repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E40AF')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))

        elements.append(table)
        elements.append(Spacer(1, 20))

        # Footer
        elements.append(Paragraph(
            'Confidential Document - For Internal Use Only',
            ParagraphStyle(
                'Footer',
                parent=styles['Normal'],
                fontSize=9,
                italic=True,
                alignment=1
            )
        ))

        doc.build(elements)
        return response

    def export_data(self, queryset, format):
            if format == 'excel':
                return self.export_excel(queryset)
            elif format == 'pdf':
                return self.export_pdf(queryset)
        
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
        qsf_documents = QSF.objects.all()  # Get all QSF documents for reference
        process_machine=ProcessMachineMapping.objects.all()
        return render(request, 'Maintenance/monthly/add_monthly.html', {
             'form': form,
            'qsf_documents': qsf_documents,
            'process_machine':process_machine
        })


    def post(self, request):
        form = MonthlyChecklistItemForm(request.POST)
    
        if form.is_valid():
            monthly_checklist_item = form.save(commit=False)
            
            try:
                monthly_checklist_item.manager = request.user
                monthly_checklist_item.request = request
                monthly_checklist_item.save()
                messages.success(request, 'Monthly checklist item added successfully.')
                return redirect('add_monthly')
            except Exception as e:
                messages.error(request, f'Error saving checklist item: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')

        return render(request, 'Maintenance/monthly/add_monthly.html', {'form': form})


@method_decorator(staff_member_required, name='dispatch')
class ListMonthlyChecklistItem(ListView):
    model = MonthlyChecklistItem
    template_name = 'Maintenance/monthly/list_monthly.html'
    context_object_name = 'records'
    ordering = ['-month_year']

    def get(self, request, *args, **kwargs):
        export_format = request.GET.get('export')
        if export_format:
            queryset = self.get_filtered_queryset()
            return self.export_data(queryset, export_format)
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = MonthlyChecklistItemSearchForm(self.request.GET)
        return context

    def get_filtered_queryset(self):
        queryset = self.model.objects.all().order_by(*self.ordering)
        form = MonthlyChecklistItemSearchForm(self.request.GET)
        
        if form.is_valid():
            if start_date := form.cleaned_data.get('start_date'):
                queryset = queryset.filter(date__gte=start_date)
            if end_date := form.cleaned_data.get('end_date'):
                queryset = queryset.filter(date__lte=end_date)
            if machine_name := form.cleaned_data.get('machine_name'):
                queryset = queryset.filter(machine_name=machine_name)
            if machine_location := form.cleaned_data.get('machine_location'):
                queryset = queryset.filter(machine_location=machine_location)
            if check_status := form.cleaned_data.get('check_status'):
                queryset = queryset.filter(Remark_12=check_status)
        
        return queryset

    def get_queryset(self):
        return self.get_filtered_queryset()
    def get_logo_path(self):
        """Get the absolute path to the logo file from static files"""
        return finders.find('images/image.png')
    def export_excel(self, queryset):
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet('Monthly Checklist Items')
        
        # Set column widths (updated to include Control Number and Process Number)
        column_widths = {
            'A:A': 20,  # Doc No
            'B:B': 15,  # Rev No
            'C:C': 15,  # Rev Date
            'D:D': 25,  # Machine Name
            'E:E': 20,  # Control Number
            'F:F': 20,  # Process Number
            'G:G': 30,  # Machine Location
            'H:H': 18,  # Date
            'I:I': 30,  # Check Points
            'J:J': 30,  # Requirements
            'K:K': 15,  # Status
        }
        
        for cols, width in column_widths.items():
            worksheet.set_column(cols, width)
        
        # Define formats
        title_format = workbook.add_format({
            'bold': True,
            'font_size': 24,
            'font_color': '#1E40AF',
            'align': 'center',
            'valign': 'vcenter'
        })
        
        subtitle_format = workbook.add_format({
            'italic': True,
            'font_size': 10,
            'font_color': '#666666',
            'align': 'right'
        })
        
        header_format = workbook.add_format({
            'bold': True,
            'font_size': 12,
            'bg_color': '#1E40AF',
            'font_color': 'white',
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'text_wrap': True
        })
        
        cell_format = workbook.add_format({
            'font_size': 11,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'text_wrap': True
        })
        
        row_offset = 6  # Start after logo/title

        # Insert logo
        logo_path = self.get_logo_path()
        if logo_path:
            worksheet.insert_image('A1', logo_path, {
                'x_scale': 0.3,
                'y_scale': 0.3,
                'x_offset': 10,
                'y_offset': 10
            })
        
        # Add title and timestamp (updated range to include all columns)
        worksheet.merge_range('A3:K3', 'Monthly Checklist Report', title_format)
        worksheet.merge_range('A4:K4', f'Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', subtitle_format)
        worksheet.set_row(5, 20)
        
        # Headers (updated to include Control Number and Process Number)
        headers = [
            'Doc No', 'Rev No', 'Rev Date', 'Machine Name', 'Control Number', 'Process Number', 
            'Location', 'Date', 'Check Points', 'Requirements', 'Status'
        ]
        
        for col, header in enumerate(headers):
            worksheet.write(row_offset, col, header, header_format)
        
        # Write data
        row = row_offset + 1
        for record in queryset:
            if row > row_offset + 1:
                worksheet.set_row(row, 5)
                row += 1
            
            # Fetch qsf_document data if exists
            if hasattr(record, 'qsf_document') and record.qsf_document:
                doc_number = record.qsf_document.doc_number
                rev_number = record.qsf_document.rev_number
                rev_date = record.qsf_document.rev_date.strftime('%Y-%m-%d') if record.rev_date else 'N/A'                    
            else:
                doc_number = getattr(record, 'doc_number', 'N/A')
                rev_number = getattr(record, 'rev_number', 'N/A')
                rev_date = getattr(record, 'rev_date', datetime.now()).strftime('%Y-%m-%d') if record.rev_date else 'N/A'                    

            # Only one checklist row for monthly (updated to include all fields with proper error handling)
            worksheet.write(row, 0, doc_number, cell_format)
            worksheet.write(row, 1, rev_number, cell_format)
            worksheet.write(row, 2, rev_date, cell_format)
            worksheet.write(row, 3, record.machine_name or 'N/A', cell_format)
            worksheet.write(row, 4, record.control_number or 'N/A', cell_format)
            
            # Get process_no from process_machine if available
            process_no = getattr(record.process_machine, 'process_no', 'N/A') if record.process_machine else 'N/A'
            worksheet.write(row, 5, process_no, cell_format)
            
            # Safely access machine_location
            location_name = record.machine_location.location_name if record.machine_location else 'N/A'
            worksheet.write(row, 6, location_name, cell_format)
            
            worksheet.write(row, 7, record.date.strftime('%Y-%m-%d'), cell_format)
            worksheet.write(row, 8, 'Check Machine Earthing (Leakage Voltage)', cell_format)
            worksheet.write(row, 9, '< 2 V', cell_format)
            worksheet.write(row, 10, record.Remark_12, cell_format)
            
            row += 1
        
        # Footer (updated range to include all columns)
        row += 2
        footer_format = workbook.add_format({
            'font_size': 10,
            'italic': True,
            'align': 'center'
        })
        worksheet.merge_range(f'A{row}:K{row}', 'Confidential Document - For Internal Use Only', footer_format)
        
        workbook.close()
        output.seek(0)
        
        response = HttpResponse(
            output.read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename=monthly_checklist_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        return response


    def export_pdf(self, queryset):
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename=monthly_checklist_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'

        doc = SimpleDocTemplate(
            response,
            pagesize=landscape(letter),
            rightMargin=30,
            leftMargin=30,
            topMargin=50,
            bottomMargin=30
        )

        elements = []
        
        # Create a table for header with logo and title
        logo_path = self.get_logo_path()
        if logo_path:
            im = Image(logo_path)
            # Set logo dimensions
            im.drawHeight = 0.5*inch
            im.drawWidth = 1.5*inch
            
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#1E40AF'),
                alignment=1  # Center alignment
            )
            
            # Create header with logo and title
            header_data = [[im, Paragraph('Monthly Checklist Report', title_style)]]
            header_table = Table(header_data, colWidths=[2*inch, 6*inch])
            header_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (0, 0), 'LEFT'),
                ('ALIGN', (1, 0), (1, 0), 'CENTER'),
                ('VALIGN', (0, 0), (1, 0), 'MIDDLE'),
            ]))
            elements.append(header_table)
        else:
            # Just title if no logo
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#1E40AF'),
                alignment=1
            )
            elements.append(Paragraph('Monthly Checklist Report', title_style))
        
        elements.append(Spacer(1, 20))
        
        # Add timestamp
        elements.append(Paragraph(
            f'Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
            ParagraphStyle(
                'Timestamp',
                parent=styles['Normal'],
                fontSize=10,
                textColor=colors.grey,
                alignment=2  # Right alignment
            )
        ))
        elements.append(Spacer(1, 30))

        # Define cell styles for text wrapping
        para_style = ParagraphStyle(
            'WrappedText',
            parent=styles['Normal'],
            fontSize=10,
            leading=12,  # Line spacing
            alignment=1,  # Center aligned
        )

        # Table headers
        headers = [
            'Doc No', 'Machine Name', 'Location', 'Date',
            'Check Points', 'Requirements', 'Status'
        ]
        
        # Convert headers to Paragraph objects for consistent formatting
        header_paragraphs = [Paragraph(header, para_style) for header in headers]
        
        # Table data starting with formatted headers
        data = [header_paragraphs]

        # Add space between records
        for idx, record in enumerate(queryset):
            # Add a spacer row between records if not the first record
            if idx > 0:
                data.append([''] * 7)  # Empty row for spacing
            
            # Monthly checklist only has one checkpoint (12)
            row_data = [
                Paragraph(record.doc_number, para_style),
                Paragraph(record.machine_name, para_style),
                Paragraph(str(record.machine_location.location_name), para_style),
                Paragraph(record.date.strftime('%Y-%m-%d'), para_style),
                Paragraph('Check Machine Earthing (Leakage Voltage)', para_style),
                Paragraph('< 2 V', para_style),
                Paragraph(record.Remark_12, para_style)
            ]
            data.append(row_data)

        # Column widths - adjust to fit content properly
        col_widths = [80, 100, 100, 80, 150, 120, 60]
        
        # Table style with improved formatting
        table_style = TableStyle([
            # Header formatting
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E40AF')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 12),
            
            # All cells
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
            
            # Text wrapping
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
            ('TOPPADDING', (0, 1), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 10),
        ])
        
        # Add alternating colors for rows
        for i in range(len(queryset)):
            start_row = 1 + (i * 2)  # Account for header and spacer rows
            if i % 2 == 1:
                table_style.add('BACKGROUND', (0, start_row), (-1, start_row), colors.lightgrey)
        
        # Create table with automatic row heights to accommodate wrapped text
        table = Table(data, colWidths=col_widths, repeatRows=1)
        table.setStyle(table_style)
        elements.append(table)
        
        # Add footer
        elements.append(Spacer(1, 20))
        footer_text = Paragraph(
            'Confidential Document - For Internal Use Only',
            ParagraphStyle(
                'Footer',
                parent=styles['Normal'],
                fontSize=8,
                textColor=colors.grey,
                alignment=1  # Center
            )
        )
        elements.append(footer_text)

        doc.build(elements)
        return response

    def export_data(self, queryset, format):
        if format == 'excel':
            return self.export_excel(queryset)
        elif format == 'pdf':
            return self.export_pdf(queryset)




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

# views.py
from django.views.generic import ListView
from django.http import HttpResponse
from django.utils import timezone
from django.db.models import Q
from io import BytesIO
import xlsxwriter
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .forms import ReadingSearchForm

class ReadingListView(ListView):
    model = ControlChartReading
    context_object_name = 'readings'
    template_name = 'reading_list.html'
    ordering = ['-date', '-time']

    def dispatch(self, request, *args, **kwargs):
        # Get the active machine for this session
        self.active_machine = self.get_active_machine(request)
        
        # For admin/staff users, we'll show all readings regardless of machine
        self.is_staff_view = request.user.is_staff or request.user.is_superuser
        
        # For regular users, require active machine
        if not self.is_staff_view and not self.active_machine:
            messages.error(request, "No active machine found. Please log into a machine first.")
            return redirect('home')  # Redirect to machine login
            
        # For regular users, check if the machine has control chart feature enabled
        if not self.is_staff_view and not self.active_machine.show_reading_list:
            messages.error(request, f"Control chart readings are not enabled for {self.active_machine.name}.")
            return redirect('home')
            
        return super().dispatch(request, *args, **kwargs)
    
    def get_active_machine(self, request):
        """Helper function to get the currently active machine for this session"""
        browser_key = request.session.get('browser_key')
        
        if not browser_key:
            return None
        
        # Get all active machine logins for this browser
        machine_statuses = MachineLoginTracker.objects.filter(
            browser_key=browser_key,
            is_active=True
        ).select_related('machine')
        
        if not machine_statuses:
            return None
        
        # Get the most recently accessed machine as the active one
        active_login = machine_statuses.order_by('-created_at').first()
        return active_login.machine if active_login else None

    def get(self, request, *args, **kwargs):
        if request.GET.get('export') == 'excel':
            queryset = self.get_queryset()  # This gets the filtered queryset
            return self.export_excel(queryset)
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # For staff/admin users, we show all readings regardless of machine
        # For regular users, filter by the active machine
        if not self.is_staff_view:
            queryset = queryset.filter(machine=self.active_machine)
        
        filter_type = self.request.GET.get('filter_type', 'today')  # Default to today's readings
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        selected_date = self.request.GET.get('date')
        
        # Always default to today's readings when first loading the page
        if not self.request.GET:
            today = timezone.localdate()
            queryset = queryset.filter(date=today)
            
        # Filter by the selected filter type
        elif filter_type == 'today':
            today = timezone.localdate()
            queryset = queryset.filter(date=today)
        elif filter_type == 'date_range' and start_date:
            try:
                queryset = queryset.filter(date__gte=start_date)
                if end_date:
                    queryset = queryset.filter(date__lte=end_date)
            except (ValueError, TypeError):
                pass
        elif filter_type == 'date' and selected_date:
            try:
                queryset = queryset.filter(date=selected_date)
            except (ValueError, TypeError):
                pass
            
        # Calculate stats for each reading
        for reading in queryset:
            # Filter out None values from readings
            readings = [r for r in [reading.reading1, reading.reading2, reading.reading3, 
                                    reading.reading4, reading.reading5] if r is not None]
            
            # Only calculate if there are valid readings
            if readings:
                reading.x_bar = sum(readings) / len(readings)
                reading.range_val = max(readings) - min(readings)
                reading.has_zero_range = (reading.range_val == 0)
            else:
                # Handle the case where all readings are None
                reading.x_bar = None
                reading.range_val = None
                reading.has_zero_range = False
            
        return queryset.order_by(*self.ordering)
    
    def get_logo_path(self):
        """Get the absolute path to the logo file from static files"""
        return finders.find('images/image.png')
    
    def export_excel(self, queryset):
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet('Control Chart Readings')
        
        # Insert logo
        logo_path = self.get_logo_path()
        if logo_path:
            worksheet.insert_image('A1', logo_path, {
                'x_scale': 0.5,
                'y_scale': 0.5,
                'x_offset': 10,
                'y_offset': 10
            })

        # Define formats
        header_format = workbook.add_format({
            'bold': True,
            'font_size': 12,
            'bg_color': '#0033CC',
            'font_color': 'white',
            'border': 1,
            'align': 'center',
            'valign': 'vcenter'
        })

        cell_format = workbook.add_format({
            'font_size': 11,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter'
        })

        date_format = workbook.add_format({
            'font_size': 11,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'num_format': 'yyyy-mm-dd'
        })

        # Set column widths
        worksheet.set_column('A:A', 15)  # Date
        worksheet.set_column('B:B', 15)  # Machine
        worksheet.set_column('C:C', 12)  # Time
        worksheet.set_column('D:H', 12)  # Readings
        worksheet.set_column('I:J', 15)  # Statistics
        worksheet.set_column('K:L', 15)  # Spec Limits

        # Write title
        title_text = 'Control Chart Readings Report'
        if not self.is_staff_view and self.active_machine:
            title_text += f' - {self.active_machine.name}'
        
        # Determine filter for title text
        filter_type = self.request.GET.get('filter_type', 'today')
        if filter_type == 'today':
            title_text += f" - {timezone.localdate().strftime('%B %d, %Y')}"
        elif filter_type == 'date_range':
            start_date = self.request.GET.get('start_date')
            end_date = self.request.GET.get('end_date')
            if start_date and end_date:
                title_text += f" - {start_date} to {end_date}"
            elif start_date:
                title_text += f" - From {start_date}"
        elif filter_type == 'date' and self.request.GET.get('date'):
            title_text += f" - {self.request.GET.get('date')}"

        worksheet.merge_range('A1:L1', title_text, 
                            workbook.add_format({
                                'bold': True,
                                'font_size': 16,
                                'align': 'center',
                                'valign': 'vcenter'
                            }))

        # Add generation timestamp
        worksheet.merge_range('A2:L2', 
                            f'Generated: {timezone.now().strftime("%Y-%m-%d %H:%M:%S")}',
                            workbook.add_format({
                                'align': 'right', 
                                'italic': True
                            }))

        # Write headers
        headers = [
            'Date', 'Machine', 'Time', 'Reading 1', 'Reading 2', 'Reading 3', 
            'Reading 4', 'Reading 5', 'X-Bar', 'Range', 'USL', 'LSL'
        ]
        for col, header in enumerate(headers):
            worksheet.write(3, col, header, header_format)

        # Write data
        for row, reading in enumerate(queryset, start=4):
            valid_readings = [r for r in [reading.reading1, reading.reading2, reading.reading3, 
                           reading.reading4, reading.reading5] if r is not None]
            
            # Only calculate if there are valid readings
            if valid_readings:
                x_bar = sum(valid_readings) / len(valid_readings)
                range_val = max(valid_readings) - min(valid_readings)
            else:
                x_bar = None
                range_val = None
            
            # Write date
            worksheet.write(row, 0, reading.date, date_format)
            
            # Write machine name
            worksheet.write(row, 1, reading.machine.name, cell_format)
            
            # Write time if available
            if hasattr(reading, 'time') and reading.time:
                worksheet.write(row, 2, reading.time.strftime('%H:%M:%S'), cell_format)
            else:
                worksheet.write(row, 2, 'N/A', cell_format)
            
            # Write all readings (even None values)
            readings = [reading.reading1, reading.reading2, reading.reading3, 
                    reading.reading4, reading.reading5]
            for col, value in enumerate(readings, start=3):
                if value is not None:
                    worksheet.write(row, col, value, cell_format)
                else:
                    worksheet.write(row, col, 'N/A', cell_format)
            
            # Write calculated values and limits
            if x_bar is not None:
                worksheet.write(row, 8, x_bar, cell_format)
            else:
                worksheet.write(row, 8, 'N/A', cell_format)
                
            if range_val is not None:
                worksheet.write(row, 9, range_val, cell_format)  
            else:
                worksheet.write(row, 9, 'N/A', cell_format)
                
            # Write USL and LSL (handle potential None values)
            if hasattr(reading, 'usl') and reading.usl is not None:
                worksheet.write(row, 10, reading.usl, cell_format)
            else:
                worksheet.write(row, 10, 'N/A', cell_format)
                
            if hasattr(reading, 'lsl') and reading.lsl is not None:
                worksheet.write(row, 11, reading.lsl, cell_format)
            else:
                worksheet.write(row, 11, 'N/A', cell_format)
        
        workbook.close()
        output.seek(0)
        
        # Create response
        response = HttpResponse(
            output.read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=readings.xlsx'
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add active machine and staff view flag to context
        context['active_machine'] = self.active_machine
        context['is_staff_view'] = self.is_staff_view
        
        # Set filter_type to 'today' if not specified in request
        if not self.request.GET:
            filter_type = 'today'
        else:
            filter_type = self.request.GET.get('filter_type', 'today')
            
        search_form = ReadingSearchForm(self.request.GET)
        
        # Set display text based on filter type and user type
        if self.is_staff_view:
            # For staff users, show all machines
            if filter_type == 'today':
                context['selected_filter_display'] = f"All Machines - Today ({timezone.localdate().strftime('%B %d, %Y')})"
            elif filter_type == 'date_range':
                start_date = self.request.GET.get('start_date')
                end_date = self.request.GET.get('end_date')
                if start_date and end_date:
                    context['selected_filter_display'] = f"All Machines - Date Range: {start_date} to {end_date}"
                elif start_date:
                    context['selected_filter_display'] = f"All Machines - Date Range: From {start_date}"
                else:
                    context['selected_filter_display'] = "All Machines - All Dates"
            elif filter_type == 'date' and self.request.GET.get('date'):
                context['selected_filter_display'] = f"All Machines - Date: {self.request.GET.get('date')}"
            else:
                context['selected_filter_display'] = "All Machines - All Readings"
        else:
            # For regular users, show only their active machine
            if filter_type == 'today':
                context['selected_filter_display'] = f"{self.active_machine.name} - Today ({timezone.localdate().strftime('%B %d, %Y')})"
            elif filter_type == 'date_range':
                start_date = self.request.GET.get('start_date')
                end_date = self.request.GET.get('end_date')
                if start_date and end_date:
                    context['selected_filter_display'] = f"{self.active_machine.name} - Date Range: {start_date} to {end_date}"
                elif start_date:
                    context['selected_filter_display'] = f"{self.active_machine.name} - Date Range: From {start_date}"
                else:
                    context['selected_filter_display'] = f"{self.active_machine.name} - All Dates"
            elif filter_type == 'date' and self.request.GET.get('date'):
                context['selected_filter_display'] = f"{self.active_machine.name} - Date: {self.request.GET.get('date')}"
            else:
                context['selected_filter_display'] = f"{self.active_machine.name} - All Readings"

        # Pass form and filter type to template
        context['search_form'] = search_form
        context['filter_type'] = filter_type
        context['today'] = timezone.localdate()
        
        return context     
          
from django.views.generic import DetailView
from .models import ControlChartReading

class ReadingDetailView(DetailView):
    model = ControlChartReading
    template_name = 'reading_detail.html'
    context_object_name = 'reading'
    
    def dispatch(self, request, *args, **kwargs):
        # Get the active machine for this session
        self.active_machine = self.get_active_machine(request)
        
        # Set flag for staff/admin users
        self.is_staff_view = request.user.is_staff or request.user.is_superuser
        
        # For regular users, require active machine
        if not self.is_staff_view and not self.active_machine:
            messages.error(request, "No active machine found. Please log into a machine first.")
            return redirect('home')  # Redirect to machine login
            
        # For regular users, check if machine has control chart feature enabled
        if not self.is_staff_view and not self.active_machine.show_reading_list:
            messages.error(request, f"Control chart readings are not enabled for {self.active_machine.name}.")
            return redirect('home')
            
        return super().dispatch(request, *args, **kwargs)
    
    def get_active_machine(self, request):
        """Helper function to get the currently active machine for this session"""
        browser_key = request.session.get('browser_key')
        
        if not browser_key:
            return None
        
        machine_statuses = MachineLoginTracker.objects.filter(
            browser_key=browser_key,
            is_active=True
        ).select_related('machine')
        
        if not machine_statuses:
            return None
        
        active_login = machine_statuses.order_by('-created_at').first()
        return active_login.machine if active_login else None
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add active machine and staff view flag to context
        context['active_machine'] = self.active_machine
        context['is_staff_view'] = self.is_staff_view
        
        reading = self.object
        
        # Check if this reading belongs to the active machine (only for regular users)
        if not self.is_staff_view and reading.machine != self.active_machine:
            raise Http404("Reading not found for the active machine.")
        
        # Add the machine for this specific reading to context
        context['reading_machine'] = reading.machine
        
        # Calculate the average directly in the view
        valid_readings = [r for r in [reading.reading1, reading.reading2, reading.reading3, 
                                    reading.reading4, reading.reading5] if r is not None]
        
        if valid_readings:
            context['avg'] = sum(valid_readings) / len(valid_readings)
            context['range'] = max(valid_readings) - min(valid_readings)
        else:
            context['avg'] = None
            context['range'] = None
        
        return context

from django.http import JsonResponse
from django.views.generic.edit import CreateView
from django.contrib import messages
from django.urls import reverse_lazy

from django.utils import timezone
from django.urls import reverse

from .forms import SingleReadingForm

class ReadingCreateView(View):
    template_name = 'reading_form.html'
    
    def dispatch(self, request, *args, **kwargs):
        # Get the active machine for this session
        self.active_machine = self.get_active_machine(request)
        
        # For admin users, always allow access even without an active machine
        if request.user.is_staff or request.user.is_superuser:
            if not self.active_machine:
                # If no active machine, use the first one for admin users
                self.active_machine = Machine.objects.first()
                if not self.active_machine:
                    messages.error(request, "No machines available in the system.")
                    return redirect('home')
            return super().dispatch(request, *args, **kwargs)
        
        # For regular users, require active machine
        if not self.active_machine:
            messages.error(request, "No active machine found. Please log into a machine first.")
            return redirect('home')  # Redirect to machine login
            
        # Check if machine has control chart feature enabled
        if not self.active_machine.show_reading_list:
            messages.error(request, f"Control chart readings are not enabled for {self.active_machine.name}.")
            return redirect('home')
            
        return super().dispatch(request, *args, **kwargs)
    
    def get_active_machine(self, request):
        """Helper function to get the currently active machine for this session"""
        browser_key = request.session.get('browser_key')
        
        if not browser_key:
            return None
        
        machine_statuses = MachineLoginTracker.objects.filter(
            browser_key=browser_key,
            is_active=True
        ).select_related('machine')
        
        if not machine_statuses:
            return None
        
        active_login = machine_statuses.order_by('-created_at').first()
        return active_login.machine if active_login else None
    
    def get(self, request):
        # Get today's reading for this machine or create a new one
        today = timezone.localdate()
        today_reading = ControlChartReading.objects.filter(
            machine=self.active_machine,
            date=today
        ).first()
        
        # Check if all readings are completed for today
        if today_reading and today_reading.reading5 is not None:
            messages.info(request, f"All readings for {self.active_machine.name} have been completed today.")
            return redirect('reading_list')
        
        # Check if enough time has passed since last reading
        can_add = ControlChartReading.can_add_new_reading(self.active_machine)  # Remove request.user
        next_reading_time = ControlChartReading.get_next_reading_time(self.active_machine)  # Remove request.user
        minutes_remaining = 0
        
        if not can_add:
            time_diff = next_reading_time - timezone.now()
            minutes_remaining = time_diff.total_seconds() / 60
            
        # Rest of method remains the same...        
        # Get process machine mapping for the active machine
        process_machine = ProcessMachineMapping.objects.filter(
            process=self.active_machine.name
        ).first()
        
        # Initialize form with USL/LSL values from:
        # 1. Today's reading if exists
        # 2. Process machine mapping if exists
        # 3. Default values otherwise
        initial_data = {}
        if today_reading:
            initial_data = {
                'usl': today_reading.usl,
                'lsl': today_reading.lsl
            }
        elif process_machine:
            initial_data = {
                'usl': process_machine.Usl,
                'lsl': process_machine.Lsl
            }
        
        form = SingleReadingForm(initial=initial_data)
        
        context = {
            'form': form,
            'active_machine': self.active_machine,
            'today_reading': today_reading,
            'can_add_reading': can_add,
            'next_reading_time': next_reading_time,
            'minutes_remaining': int(minutes_remaining),
            'next_reading_number': today_reading.get_next_reading_index() if today_reading else 1,
            'title': f'Add Reading for {self.active_machine.name}',
            'process_machine': process_machine  # Pass this to template if needed
        }
        
        return render(request, self.template_name, context)
        
    def post(self, request):
        form = SingleReadingForm(request.POST)
        today = timezone.localdate()
        today_reading = ControlChartReading.objects.filter(
            machine=self.active_machine,
            date=today
        ).first()
        
        # Get process machine mapping for this machine
        process_machine = ProcessMachineMapping.objects.filter(
            process=self.active_machine.name
        ).first()
        
        # Check if we can add a new reading (time constraint)
        if not ControlChartReading.can_add_new_reading(self.active_machine, request.user):
            next_time = ControlChartReading.get_next_reading_time(self.active_machine, request.user)
            minutes_diff = (next_time - timezone.now()).total_seconds() / 60
            minutes_remaining = max(0, int(minutes_diff))
            
            messages.error(
                request, 
                f"You must wait {minutes_remaining} minutes before adding the next reading."
            )
            return redirect('reading_create')
        
        if form.is_valid():
            reading_value = form.cleaned_data['reading_value']
            
            # Get USL/LSL values preferably from process_machine if available
            usl = form.cleaned_data['usl']
            lsl = form.cleaned_data['lsl']
            
            if process_machine:
                if process_machine.Usl is not None:
                    usl = process_machine.Usl
                if process_machine.Lsl is not None:
                    lsl = process_machine.Lsl
            
            if today_reading:
                # Update existing record with new reading
                next_index = today_reading.get_next_reading_index()
                if next_index == 1:
                    today_reading.reading1 = reading_value
                elif next_index == 2:
                    today_reading.reading2 = reading_value
                elif next_index == 3:
                    today_reading.reading3 = reading_value
                elif next_index == 4:
                    today_reading.reading4 = reading_value
                elif next_index == 5:
                    today_reading.reading5 = reading_value
                
                today_reading.usl = usl
                today_reading.lsl = lsl
                today_reading.time = timezone.now().time()  # Update time to current time
                
                # Set process_machine relationship if available
                if process_machine:
                    today_reading.process_machine = process_machine
                    
                today_reading.save()
                
                messages.success(request, f"Reading #{next_index} has been added successfully for {self.active_machine.name}.")
            else:
                # Create new record with first reading
                today_reading = ControlChartReading(
                    machine=self.active_machine,  # Associate with the active machine
                    date=today,
                    reading1=reading_value,
                    reading2=None,
                    reading3=None,
                    reading4=None,
                    reading5=None,
                    usl=usl,
                    lsl=lsl,
                    process_machine=process_machine  # Set the relationship
                )
                today_reading.save()
                
                messages.success(request, f"First reading of the day has been added successfully for {self.active_machine.name}.")
            
            # Check if we completed all readings
            if today_reading.reading5 is not None:
                messages.info(request, f"All readings for {self.active_machine.name} have been completed today!")
                return redirect('reading_list')
                
            # Redirect to same page but with count parameter to refresh counter
            next_number = today_reading.get_next_reading_index()
            return redirect(f"{reverse('reading_create')}?count={next_number-1}")
        
        # Form validation failed
        context = {
            'form': form,
            'active_machine': self.active_machine,
            'today_reading': today_reading,
            'can_add_reading': ControlChartReading.can_add_new_reading(self.active_machine),
            'next_reading_time': ControlChartReading.get_next_reading_time(self.active_machine),
            'minutes_remaining': int((ControlChartReading.get_next_reading_time(self.active_machine) - timezone.now()).total_seconds() / 60),
            'next_reading_number': today_reading.get_next_reading_index() if today_reading else 1,
            'title': f'Add Reading for {self.active_machine.name}',
            'process_machine': process_machine  # Pass this to template if needed
        }
        
        return render(request, self.template_name, context)    
    
# In views.py
from datetime import datetime, timedelta  # Correct import statement
from django.http import JsonResponse

# views.py
# views.py
def reading_status_api(request):
    """API endpoint to check if a new reading can be added for the active machine"""
    # Get the active machine
    active_machine = get_active_machine(request)
    
    if not active_machine:
        return JsonResponse({
            'success': False,
            'error': 'No active machine found. Please log into a machine first.'
        })
    
    # Check if reading list is enabled for this machine
    if not active_machine.show_reading_list:
        return JsonResponse({
            'success': False,
            'error': 'Reading list is not enabled for this machine.'
        })
    
    can_add = ControlChartReading.can_add_new_reading(active_machine, request.user)
    today = timezone.localdate()
    todays_readings = ControlChartReading.objects.filter(
        machine=active_machine,
        date=today
    ).first()
    
    todays_readings_count = 0
    next_reading_index = 1
    
    if todays_readings:
        # Count non-None readings
        readings = [
            todays_readings.reading1, 
            todays_readings.reading2, 
            todays_readings.reading3, 
            todays_readings.reading4, 
            todays_readings.reading5
        ]
        todays_readings_count = sum(1 for r in readings if r is not None)
        next_reading_index = todays_readings.get_next_reading_index() or 6  # 6 means all completed
    
    data = {
        'success': True,
        'machine_id': active_machine.id,
        'machine_name': active_machine.name,
        'can_add_reading': can_add,
        'todays_readings_count': todays_readings_count,
        'next_reading_index': next_reading_index,
        'max_readings_per_day': 5
    }
    
    if not can_add:
        next_time = ControlChartReading.get_next_reading_time(active_machine, request.user)
        data['next_reading_time'] = next_time.isoformat() if next_time else None
        if next_time:
            minutes_diff = (next_time - timezone.now()).total_seconds() / 60
            data['minutes_remaining'] = max(0, int(minutes_diff))
        else:
            data['minutes_remaining'] = 0
    
    return JsonResponse(data)


def get_active_machine(request):
    """Helper function to get the currently active machine for this session"""
    # For admin/staff users, either get their active machine or return the first machine
    if request.user.is_staff or request.user.is_superuser:
        browser_key = request.session.get('browser_key')
        
        # Try to get the active machine from browser key first
        if browser_key:
            from machineapp.models import MachineLoginTracker, Machine
            machine_statuses = MachineLoginTracker.objects.filter(
                browser_key=browser_key,
                is_active=True
            ).select_related('machine')
            
            if machine_statuses.exists():
                active_login = machine_statuses.order_by('-created_at').first()
                return active_login.machine
        
        # If no active machine found, return the first machine for admin users
        from machineapp.models import Machine
        return Machine.objects.first()
    
    # For regular users, check for browser key
    browser_key = request.session.get('browser_key')
    
    if not browser_key:
        return None
    
    # Get all active machine logins for this browser
    from machineapp.models import MachineLoginTracker
    machine_statuses = MachineLoginTracker.objects.filter(
        browser_key=browser_key,
        is_active=True
    ).select_related('machine')
    
    if not machine_statuses:
        return None
    
    # Get the most recently accessed machine as the active one
    active_login = machine_statuses.order_by('-created_at').first()
    return active_login.machine if active_login else None



class ReadingUpdateView(UpdateView):
    model = ControlChartReading
    form_class = ControlChartReadingForm
    template_name = 'reading_form.html'
    success_url = reverse_lazy('reading_list')
    
    def dispatch(self, request, *args, **kwargs):
        # Get the active machine for this session
        self.active_machine = self.get_active_machine(request)
        
        # Set flag for staff/admin users
        self.is_staff_view = request.user.is_staff or request.user.is_superuser
        
        # For regular users, require active machine
        if not self.is_staff_view and not self.active_machine:
            messages.error(request, "No active machine found. Please log into a machine first.")
            return redirect('home')  # Redirect to machine login
            
        # For regular users, check if machine has control chart feature enabled
        if not self.is_staff_view and not self.active_machine.show_reading_list:
            messages.error(request, f"Control chart readings are not enabled for {self.active_machine.name}.")
            return redirect('home')
            
        # For regular users, check if the reading belongs to their active machine
        if not self.is_staff_view:
            try:
                reading = self.get_object()
                if reading.machine != self.active_machine:
                    messages.error(request, "You can only edit readings for your active machine.")
                    return redirect('reading_list')
            except:
                pass  # Object might not exist yet, let the parent class handle it
        
        return super().dispatch(request, *args, **kwargs)
    
    def get_active_machine(self, request):
        """Helper function to get the currently active machine for this session"""
        browser_key = request.session.get('browser_key')
        
        if not browser_key:
            return None
        
        machine_statuses = MachineLoginTracker.objects.filter(
            browser_key=browser_key,
            is_active=True
        ).select_related('machine')
        
        if not machine_statuses:
            return None
        
        active_login = machine_statuses.order_by('-created_at').first()
        return active_login.machine if active_login else None
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add staff view flag to context
        context['is_staff_view'] = self.is_staff_view
        
        # Get the reading being edited
        reading = self.object
        
        # Add the machine for this specific reading to context
        context['reading_machine'] = reading.machine
        
        # For staff view, set title to show which machine's reading is being edited
        if self.is_staff_view:
            context['title'] = f'Edit Reading for {reading.machine.name}'
            context['active_machine'] = None  # Active machine not relevant for staff
        else:
            context['title'] = f'Edit Reading for {self.active_machine.name}'
            context['active_machine'] = self.active_machine
        
        # Add the missing context variables
        today = timezone.localdate()
        
        # For staff view, show overall counts
        if self.is_staff_view:
            context['todays_readings_count'] = ControlChartReading.objects.filter(
                date=today
            ).count()
        else:
            # For regular users, show machine-specific counts
            context['todays_readings_count'] = ControlChartReading.objects.filter(
                machine=self.active_machine,
                date=today
            ).count()
            
        context['max_readings_per_day'] = 5
        
        return context
        
    def form_valid(self, form):
        reading = form.instance
        machine_name = reading.machine.name
        
        messages.success(self.request, f'Reading for {machine_name} has been successfully updated.')
        return super().form_valid(form)
        
    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)
        
class ReadingDeleteView(DeleteView):
    model = ControlChartReading
    context_object_name = 'reading'
    template_name = 'reading_confirm_delete.html'
    success_url = reverse_lazy('reading_list')
    
    def dispatch(self, request, *args, **kwargs):
        # Get the active machine for this session
        self.active_machine = self.get_active_machine(request)
        
        # For admin users, always allow access even without an active machine
        if request.user.is_staff or request.user.is_superuser:
            if not self.active_machine:
                # If no active machine, use the first one for admin users
                self.active_machine = Machine.objects.first()
                if not self.active_machine:
                    messages.error(request, "No machines available in the system.")
                    return redirect('home')
            return super().dispatch(request, *args, **kwargs)
        
        # For regular users, require active machine
        if not self.active_machine:
            messages.error(request, "No active machine found. Please log into a machine first.")
            return redirect('home')  # Redirect to machine login
            
        # Check if machine has control chart feature enabled
        if not self.active_machine.show_reading_list:
            messages.error(request, f"Control chart readings are not enabled for {self.active_machine.name}.")
            return redirect('home')
            
        return super().dispatch(request, *args, **kwargs)
    
    def get_active_machine(self, request):
        """Helper function to get the currently active machine for this session"""
        browser_key = request.session.get('browser_key')
        
        if not browser_key:
            return None
        
        machine_statuses = MachineLoginTracker.objects.filter(
            browser_key=browser_key,
            is_active=True
        ).select_related('machine')
        
        if not machine_statuses:
            return None
        
        active_login = machine_statuses.order_by('-created_at').first()
        return active_login.machine if active_login else None
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_machine'] = self.active_machine
        return context
    
    def delete(self, request, *args, **kwargs):
        reading = self.get_object()
        machine_name = reading.machine.name
        messages.success(request, f"Reading for {machine_name} has been deleted successfully.")
        return super().delete(request, *args, **kwargs)
    

from django.shortcuts import render
from .models import ControlChartReading, ControlChartStatistics
from django.core.exceptions import ObjectDoesNotExist

# views.py
from django.shortcuts import render, redirect
from django.db.models.functions import TruncMonth, TruncDate
from django.db.models import Count, Min, Max, Avg, StdDev
from django.utils import timezone
from django.contrib import messages
import calendar

def process_violations(violations):
    """
    Process raw violations data into a format suitable for display.
    """
    processed_violations = []
    for violation in violations:
        if 'date_range' in violation:
            date_display = (
                f"{violation['date_range'][0].strftime('%Y-%m-%d')} to "
                f"{violation['date_range'][1].strftime('%Y-%m-%d')}"
            )
        else:
            date_display = violation['date'].strftime('%Y-%m-%d')
            
        processed_violations.append({
            'rule': violation['rule'],
            'message': violation['message'],
            'date_display': date_display,
            'severity': violation['severity'],
            'points': violation.get('points', []),
            'value': violation.get('value'),
            'trend': violation.get('trend')
        })
    
    return processed_violations

def determine_violation_severity(violations):
    """
    Determine the overall severity level based on violation types.
    """
    if not violations:
        return 'low'
    
    high_severity_rules = {'A', 'B', 'E', 'H'}
    has_high_severity = any(
        v['rule'] in high_severity_rules for v in violations
    )
    
    return 'high' if has_high_severity else 'medium'

# @method_decorator(staff_member_required, name='dispatch')
def control_chart(request):
    """
    View function for displaying the control chart dashboard with statistical analysis
    and special cause violations detection.
    """
    # Check if user is staff/admin
    is_staff_view = request.user.is_staff or request.user.is_superuser
    
    # Get the active machine for this session
    active_machine = get_active_machine(request)
    
    # Get all available machines for staff users
    all_machines = []
    if is_staff_view:
        from machineapp.models import Machine
        all_machines = Machine.objects.all()
        
        # If no machine is specified but filter_machine is set to 'all', don't use any machine
        if request.GET.get('filter_machine') == 'all':
            active_machine = None
        # Otherwise, allow selection of any machine for staff
        elif request.GET.get('machine_id'):
            try:
                active_machine = Machine.objects.get(id=request.GET.get('machine_id'))
            except (Machine.DoesNotExist, ValueError):
                pass
        # If no active machine is selected and not viewing all, use the first one
        elif not active_machine and all_machines.exists() and request.GET.get('filter_machine') != 'all':
            active_machine = all_machines.first()
    
    # For regular users, require active machine
    if not is_staff_view:
        if not active_machine:
            messages.error(request, "No active machine found. Please log into a machine first.")
            return redirect('home')  # Redirect to machine login
            
        # Check if machine has control chart feature enabled
        if not hasattr(active_machine, 'show_reading_list') or not active_machine.show_reading_list:
            messages.error(request, f"Control chart readings are not enabled for {active_machine.name}.")
            return redirect('home')
    
    # Handle month selection with fallback to current month
    selected_month = request.GET.get('month', timezone.now().strftime('%Y-%m'))
    
    try:
        year, month = map(int, selected_month.split('-'))
    except ValueError:
        current_date = timezone.now()
        year, month = current_date.year, current_date.month

    # Calculate total days in selected month
    _, total_days = calendar.monthrange(year, month)
    
    from screen_app.models import ControlChartReading, ControlChartStatistics
    
    # Get the raw data for the selected month
    # If we're in staff mode with 'all' machines, don't filter by machine
    raw_readings_query = ControlChartReading.objects.filter(
        date__year=year,
        date__month=month
    )
    
    # Only filter by machine if we're not viewing all machines
    if active_machine:
        raw_readings_query = raw_readings_query.filter(machine=active_machine)
        
    raw_readings = raw_readings_query.order_by('date', 'time')
    
    # Group readings by machine and date
    daily_readings = {}
    
    for reading in raw_readings:
        # Use machine ID and date as key
        machine_id = reading.machine_id
        date_key = reading.date.strftime('%Y-%m-%d')
        key = f"{machine_id}_{date_key}"
        
        if key not in daily_readings:
            daily_readings[key] = {
                'machine': reading.machine,
                'date': reading.date,
                'readings': [],
                'usl': reading.usl,
                'lsl': reading.lsl
            }
        
        # Add only non-None readings from this entry to the list
        valid_readings = [r for r in [
            reading.reading1, reading.reading2, reading.reading3, 
            reading.reading4, reading.reading5
        ] if r is not None]
        
        daily_readings[key]['readings'].extend(valid_readings)
    
    # Create or get ControlChartStatistics entries for each day/machine
    for key, data in daily_readings.items():
        readings = data['readings']
        if readings:  # Skip empty days
            # Calculate statistics for the day
            x_bar = round(sum(readings) / len(readings), 2)
            r = round(max(readings) - min(readings), 2) if len(readings) > 1 else 0
            
            # Create or update the statistics entry
            ControlChartStatistics.objects.update_or_create(
                machine=data['machine'],
                date=data['date'],
                defaults={
                    'x_bar': x_bar,
                    'r': r,
                    'usl': data['usl'],
                    'lsl': data['lsl']
                }
            )

    # Retrieve monthly statistics for selected machine(s)
    monthly_stats_query = ControlChartStatistics.objects.filter(
        date__year=year,
        date__month=month
    )
    
    # Only filter by machine if we're not viewing all machines
    if active_machine:
        monthly_stats_query = monthly_stats_query.filter(machine=active_machine)
        
    monthly_stats = monthly_stats_query.order_by('date')

    # Calculate monthly summary statistics
    days_with_data = len(set(stat.date for stat in monthly_stats))
    completion_percentage = (days_with_data / total_days * 100) if total_days else 0

    # Get the latest specification limits
    latest_stats = monthly_stats.last()
    current_usl = latest_stats.usl if latest_stats else 375  # Default USL
    current_lsl = latest_stats.lsl if latest_stats else 355  # Default LSL

    # Convert monthly_stats to chart-ready format with dates
    chart_data = []
    dates_set = set()
    
    for stat in monthly_stats:
        date_str = stat.date.strftime('%Y-%m-%d')
        dates_set.add(date_str)
        
        chart_data.append({
            'date': date_str,
            'date_display': stat.date.strftime('%b %d'),
            'x_bar': stat.x_bar,
            'r': stat.r,
            'machine_id': stat.machine_id,
            'machine_name': stat.machine.name if hasattr(stat.machine, 'name') else 'Unknown'
        })
    
    # Sort by date for consistent charting
    chart_data.sort(key=lambda x: x['date'])
    
    # For staff views with all machines, group by machine for the chart data
    machine_grouped_data = {}
    if is_staff_view and not active_machine:
        for item in chart_data:
            machine_id = item['machine_id']
            if machine_id not in machine_grouped_data:
                machine_grouped_data[machine_id] = {
                    'machine_name': item['machine_name'],
                    'data': []
                }
            machine_grouped_data[machine_id]['data'].append(item)
    
    # Get data points for special cause analysis - using date + machine as combined key
    data_points = []
    for stat in monthly_stats:
        data_points.append({
            'date': stat.date,
            'machine_id': stat.machine_id,
            'x_bar': stat.x_bar,
            'r': stat.r
        })
    
    processed_violations = []
    if data_points:
        # Check for None or invalid values in x_bars
        x_bars = [point['x_bar'] for point in data_points if point['x_bar'] is not None]
        
        if x_bars:  # Only calculate if we have valid data
            mean = round(sum(x_bars) / len(x_bars), 1)
            std_dev = round((
                sum((x - mean) ** 2 for x in x_bars) / len(x_bars)
            ) ** 0.5, 2)
            
            # Get violations and process them for display
            violations = ControlChartStatistics.check_special_causes(data_points, mean, std_dev)
            processed_violations = process_violations(violations)

    # Prepare monthly summary if data exists
    monthly_summary = None
    if monthly_stats.exists():
        x_bar_avg = monthly_stats.aggregate(Avg('x_bar'))['x_bar__avg']
        r_avg = monthly_stats.aggregate(Avg('r'))['r__avg']
        
        # Calculate standard deviation for display
        x_bars = [stat.x_bar for stat in monthly_stats if stat.x_bar is not None]
        monthly_std_dev = None
        if x_bars:
            mean = sum(x_bars) / len(x_bars)
            monthly_std_dev = math.sqrt(sum((x - mean) ** 2 for x in x_bars) / len(x_bars))
        
        monthly_summary = {
            'month_name': calendar.month_name[month],
            'year': year,
            'days_with_data': days_with_data,
            'total_days': total_days,
            'completion_percentage': completion_percentage,
            'first_reading_date': min(dates_set) if dates_set else None,
            'last_reading_date': max(dates_set) if dates_set else None,
            'current_usl': current_usl,
            'current_lsl': current_lsl,
            'x_bar_avg': round(x_bar_avg, 1) if x_bar_avg is not None else None,
            'r_avg': round(r_avg, 1) if r_avg is not None else None,
            'std_dev': round(monthly_std_dev, 2) if monthly_std_dev is not None else 0
        }

    # Get available months for the dropdown - for staff view with all machines, don't filter by machine
    if is_staff_view and not active_machine:
        available_months = ControlChartStatistics.objects.annotate(
            month=TruncMonth('date')
        ).values('month').annotate(
            days_count=Count('id')
        ).order_by('-month')
    else:
        available_months = ControlChartStatistics.objects.filter(
            machine=active_machine
        ).annotate(
            month=TruncMonth('date')
        ).values('month').annotate(
            days_count=Count('id')
        ).order_by('-month')

    # Calculate control limits and capability indices
    if active_machine:
        control_limits = ControlChartStatistics.calculate_control_limits(machine=active_machine)
        capability_indices = ControlChartStatistics.calculate_capability_indices(machine=active_machine)
    else:
        # For all machines view, calculate overall control limits
        control_limits = ControlChartStatistics.calculate_control_limits()
        capability_indices = ControlChartStatistics.calculate_capability_indices()

    # Determine overall violation severity
    violation_severity = determine_violation_severity(processed_violations)

    # Prepare context for template
    context = {
        'is_staff_view': is_staff_view,
        'active_machine': active_machine,
        'all_machines': all_machines,
        'viewing_all_machines': is_staff_view and not active_machine,
        'chart_data': chart_data,
        'machine_grouped_data': machine_grouped_data,
        'statistics': monthly_stats,
        'monthly_summary': monthly_summary,
        'available_months': available_months,
        'selected_month': selected_month,
        'dates_in_month': sorted(list(dates_set)),
        'control_limits': control_limits,
        'capability_indices': capability_indices,
        'specification_limits': {
            'usl': current_usl,
            'lsl': current_lsl
        },
        'violations': processed_violations,
        'has_violations': bool(processed_violations),
        'violation_count': len(processed_violations),
        'violation_severity': violation_severity
    }
    
    return render(request, 'control_chart.html', context)

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from machineapp.models import Machine, MachineLoginTracker

@login_required
def dashboard(request):
    # Get the browser key from the session
    browser_key = request.session.get('browser_key')
    active_machine = None
    
    if browser_key:
        # Import the model - add this at the top of your file
        # from machineapp.models import MachineLoginTracker
        
        # Get the active machine for this browser
        machine_status = MachineLoginTracker.objects.filter(
            browser_key=browser_key,
            is_active=True
        ).select_related('machine').order_by('-created_at').first()
        
        if machine_status:
            active_machine = machine_status.machine
            print(f"Active machine in dashboard: {active_machine.name}")
            print(f"Checklist settings: Fixture={active_machine.show_fixture_cleaning}, Rejection={active_machine.show_rejection_sheets}")
    
    context = {
        'active_machine': active_machine,
    }
    
    return render(request, 'dashboard.html', context)


from django.shortcuts import render

def index(request):
    return render(request, 'index.html')




from django.template.defaulttags import register

@register.filter
def index(indexable, i):
    return indexable[i]


# ----------------------------------------------------------------
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import StartUpCheckSheet
from .forms import StartUpCheckSheetForm



# ListView to display all StartUpCheckSheet entries
class StartUpCheckSheetListView(ListView):
    model = StartUpCheckSheet
    template_name = 'startup/startup_checksheet_list.html'
    context_object_name = 'check_sheets'
    paginate_by = 10  # Add pagination for better performance

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Get filter parameters from request
        process = self.request.GET.get('process')
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        revision = self.request.GET.get('revision')
        
        # Apply filters if provided
        if process:
            queryset = queryset.filter(process_operation_id=process)
        
        if revision:
            queryset = queryset.filter(revision_no=revision)
        
        if start_date:
            queryset = queryset.filter(effective_date__gte=start_date)
            
        if end_date:
            queryset = queryset.filter(effective_date__lte=end_date)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add filter values to context for maintaining form state
        context['process'] = self.request.GET.get('process', '')
        context['start_date'] = self.request.GET.get('start_date', '')
        context['end_date'] = self.request.GET.get('end_date', '')
        context['revision'] = self.request.GET.get('revision', '')
        
        # Get list of processes for the dropdown filter
        context['process_list'] = MachineLocation.objects.all()
        
        return context

def get_logo_path():
    """Get the absolute path to the logo file from static files"""
    return finders.find('images/image.png')

def export_checksheet_excel(request):
    import xlsxwriter
    from io import BytesIO
    from datetime import datetime
    import os
    from django.conf import settings
    from django.http import HttpResponse
    
    # Get filtered queryset based on request parameters
    process = request.GET.get('process')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    revision = request.GET.get('revision')
    
    queryset = StartUpCheckSheet.objects.all()
    
    
    if process:
        queryset = queryset.filter(process_operation_id=process)
    
    if revision:
        queryset = queryset.filter(revision_no=revision)
    
    if start_date:
        queryset = queryset.filter(effective_date__gte=start_date)
        
    if end_date:
        queryset = queryset.filter(effective_date__lte=end_date)
    
    # Create Excel file
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet('StartUp Check Sheets')
    
    # Load checkpoint data 
    json_data = [
    {
        "s_no": 1,
        "checkpoint": "प्लान के अनुसार पार्ट असेंबली और चाइल्ड पार्ट्स को वर्किंग टेबल पर रखें।",
        "specification": "Part assy & Child parts",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
        "s_no": 2,
        "checkpoint": "अपने कार्य स्थल को साफ रखें, कार्य स्थल पर धूल या गंदगी नहीं होनी चाहिए।",
        "specification": "साफ-सफाई",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
        "s_no": 3,
        "checkpoint": "कार्य शुरू करने से पहले वर्किंग टेबल से अनावश्यक पार्ट्स / मटेरियल हटा दें और उन्हें उनकी निर्धारित जगह पर रखें।",
        "specification": "वर्किंग टेबल पर अनावश्यक पार्ट्स / मटेरियल न हों",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
        "s_no": 4,
        "checkpoint": "गंदे ट्रे का उपयोग लाइन पर न करें, उसे साफ करने के लिए निर्धारित स्थान पर रखें।",
        "specification": "गंदे ट्रे लाइन पर न हों",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
        "s_no": 5,
        "checkpoint": "चेक करें कि फिक्स्चर / मशीन की स्थिति ठीक हो और सभी कनेक्शन्स सही व टाइट हों।",
        "specification": "फिक्स्चर / मशीन कंडीशन सही हो",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
        "s_no": 6,
        "checkpoint": "फिक्स्चर / मशीन पर लगे कैलिब्रेशन / वेरिफिकेशन टैग की डेट एक्सपायर न हो।",
        "specification": "कैलिब्रेशन / वेरिफिकेशन टैग वैलिड हो",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
        "s_no": 7,
        "checkpoint": "चेक करें कि ESD रिस्ट बैंड ठीक हो (जहां लागू हो), और वर्क इंस्ट्रक्शन के अनुसार सिग्नल लाल/हरा हो।",
        "specification": "ESD रिस्ट बैंड ठीक हो",
        "control_method": "Wrist Band tester",
        "frequency": "daily"
    },
    {
        "s_no": 8,
        "checkpoint": "ESD रिस्ट बैंड पहनें (जहां लागू हो)।",
        "specification": "ESD रिस्ट बैंड पहनना",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
        "s_no": 9,
        "checkpoint": "फेस मास्क पहनें (जहां लागू हो), और वह शॉप फ्लोर पर उपलब्ध हो।",
        "specification": "फेस मास्क पहनना",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
        "s_no": 10,
        "checkpoint": "ESD जैकेट और कैप, ESD ग्लव्स / फिंगर कोट्स पहनें।",
        "specification": "ESD जैकेट, कैप, ग्लव्स/फिंगर कोट्स पहनना",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
        "s_no": 11,
        "checkpoint": "चेक करें कि रेड ड्रॉअर में NG पार्ट्स रखने के लिए ट्रे उपलब्ध हो।",
        "specification": "NG पार्ट्स के लिए ट्रे उपलब्ध हो",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
        "s_no": 12,
        "checkpoint": "ड्रॉअर में आवश्यक टैग्स और PPEs उपलब्ध हों, जैसे: Reject Tag, OK Tag, Abnormal Situation Tag आदि।",
        "specification": "सभी आवश्यक टैग्स और PPEs उपलब्ध हों",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
        "s_no": 13,
        "checkpoint": "चेक करें कि ड्रॉअर में कोई अनुपयोगी वस्तु न हो।",
        "specification": "अनुपयोगी वस्तुएं न हों",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
        "s_no": 14,
        "checkpoint": "कार्य स्थल पर आवश्यक डॉक्युमेंट्स जैसे सेटअप शीट, FPA, डेली/मंथली रिजेक्शन शीट्स आदि उपलब्ध हों।",
        "specification": "सभी आवश्यक डॉक्युमेंट्स उपलब्ध हों",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
        "s_no": 15,
        "checkpoint": "लाइन पर OK/NG मास्टर सैंपल उपलब्ध हो और उसकी डेट एक्सपायर न हो।",
        "specification": "OK/NG मास्टर सैंपल वैलिड हो",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
        "s_no": 16,
        "checkpoint": "टी ब्रेक और लंच के समय बाहर जाते समय अपना सेटअप/सिस्टम बंद करें।",
        "specification": "ब्रेक में सिस्टम बंद करना",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
        "s_no": 17,
        "checkpoint": "टी ब्रेक और लंच में जाते समय लाइट्स बंद करें।",
        "specification": "ब्रेक में लाइट्स बंद करना",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
        "s_no": 18,
        "checkpoint": "ब्रेक के दौरान शॉप फ्लोर पर रहते समय जैकेट और कैप पहन कर रखें।",
        "specification": "ब्रेक में भी जैकेट और कैप पहनना",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
        "s_no": 19,
        "checkpoint": "FRL (प्रेशर गेज) की पिन को पुश करके 10-12 सेकंड तक एयर निकालें। यदि एयर के साथ पानी भी निकलता है तो तुरंत सुपरवाइजर को सूचित करें।",
        "specification": "FRL की पिन से एयर रिलीज करना",
        "control_method": "Visual / Manual",
        "frequency": "daily"
    },
    {
        "s_no": 20,
        "checkpoint": "रिजेक्ट हुए पार्ट्स के हैंडओवर की प्रक्रिया सही होनी चाहिए।",
        "specification": "हैंडओवर प्रक्रिया सही हो",
        "control_method": "Supervisor's verification",
        "frequency": "daily"
    },
    {
        "s_no": 21,
        "checkpoint": "ESD शूज़/स्लीपर्स पहनें (जहां लागू हो) और वे शॉप फ्लोर पर उपलब्ध हों।",
        "specification": "ESD शूज़/स्लीपर्स पहनना",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
        "s_no": 22,
        "checkpoint": "स्किल लेवल कार्ड चेक करें कि उसकी वैलिड डेट एक्सपायर न हो।",
        "specification": "स्किल कार्ड वैलिड हो",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
        "s_no": 23,
        "checkpoint": "ESD शूज़ / स्लीपर्स की स्थिति सही हो (जहां लागू हो)।",
        "specification": "ESD शूज़ / स्लीपर्स OK हों",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
        "s_no": 24,
        "checkpoint": "हर शिफ्ट की शुरुआत में POGO पिन्स की अच्छी तरह से सफाई करें।",
        "specification": "POGO पिन्स की सफाई",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
        "s_no": 25,
        "checkpoint": "कार्य शुरू करने से पहले क्योरिंग रैक की कंडीशन चेक करें कि टाइमर सेट हो और रैक डैमेज न हो।",
        "specification": "क्योरिंग रैक की स्थिति सही हो",
        "control_method": "visual",
        "frequency": "daily"
    },
        {
    "s_no": 26,
    "checkpoint": "सुनिश्चित करें कि ESD ब्रश का स्थिर चार्ज (Static Charge) <125V है| - By Supervisor (Where Applicable)",
    "specification": "<125 V",
    "control_method": "Electrostatic Field Meter",
    "frequency": "प्रतिमास"
},
        
]




    # Set column widths - using column numbers instead of letters
    worksheet.set_column(0, 0, 10)  # A - S.No
    worksheet.set_column(1, 1, 30)  # B - Process/Operation
    worksheet.set_column(2, 2, 12)  # C - Revision No
    worksheet.set_column(3, 3, 15)  # D - Effective Date
    worksheet.set_column(4, 4, 15)  # E - Month
    worksheet.set_column(5, 5, 12)  # F - Manager
    
    # Set checkpoint columns with consistent width - using column numbers
    for i in range(6, 31):  # Columns for 25 checkpoints
        worksheet.set_column(i, i, 8)
    worksheet.set_column(31, 31, 12)  # Verified column
    
    # Define formats
    title_format = workbook.add_format({
        'bold': True,
        'font_size': 24,
        'font_color': '#1E40AF',
        'align': 'center',
        'valign': 'vcenter'
    })
    
    subtitle_format = workbook.add_format({
        'italic': True,
        'font_size': 10,
        'font_color': '#666666',
        'align': 'right'
    })
    
    header_format = workbook.add_format({
        'bold': True,
        'font_size': 12,
        'bg_color': '#1E40AF',
        'font_color': 'white',
        'border': 1,
        'align': 'center',
        'valign': 'vcenter',
        'text_wrap': True
    })
    
    cell_format = workbook.add_format({
        'font_size': 11,
        'border': 1,
        'align': 'center',
        'valign': 'vcenter'
    })
    
    ok_format = workbook.add_format({
        'font_size': 11,
        'border': 1,
        'align': 'center',
        'valign': 'vcenter',
        'bg_color': '#DCFCE7',  # Light green
        'color': '#166534'      # Dark green
    })
    
    not_ok_format = workbook.add_format({
        'font_size': 11,
        'border': 1,
        'align': 'center',
        'valign': 'vcenter',
        'bg_color': '#FEE2E2',  # Light red
        'color': '#991B1B'      # Dark red
    })
    
    # Logo placement - leave space at top
    row_offset = 6  # Start data after logo and title
        # With your new code:
    logo_path = get_logo_path()
    if logo_path:
        worksheet.insert_image('A1', logo_path, {
            'x_scale': 0.3,
            'y_scale': 0.3,
            'x_offset': 10,
            'y_offset': 10
        })

    # Insert logo
    try:
        logo_path = os.path.join(settings.STATIC_ROOT, 'images', 'logo.png')  # Adjust path as needed
        if os.path.exists(logo_path):
            worksheet.insert_image('A1', logo_path, {
                'x_scale': 1,
                'y_scale': 1.8,
                'x_offset': 10,
                'y_offset': 10
            })
    except Exception as e:
        # Handle exception if logo cannot be inserted
        pass
    
    # Add title - use worksheet.merge_range with row/column indices instead of cell references
    worksheet.merge_range(2, 0, 2, 31, 'Start Up Check Sheet Report', title_format)
    
    # Add timestamp
    worksheet.merge_range(3, 0, 3, 31, f'Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', subtitle_format)
    
    # Add some spacing
    worksheet.set_row(5, 20)  # Empty row for spacing
    
    # Generate headers
    headers = ['S.No', 'Process/Operation', 'Rev. No', 'Effective Date', 'Month', 'Operator']
    
    # Add checkpoint labels in first row
    for i in range(1, 27):
        headers.append(f'CP{i}')
    
    # Add verified header
    headers.append('Verified')
    
    # Write headers
    for col, header in enumerate(headers):
        worksheet.write(row_offset, col, header, header_format)
    
    # Add a legend/description row with checkpoint details
    legend_row = row_offset + 1
    checkpoint_format = workbook.add_format({
        'font_size': 9,
        'text_wrap': True,
        'align': 'center',
        'valign': 'top',
        'bg_color': '#F0F9FF',  # Light blue background
        'border': 1
    })
    
    # Get checkpoint descriptions
    # If you have the JSON data available, use it here
    checkpoint_descriptions = []
    try:
        for i in range(1, 27):
            if i <= len(json_data):
                checkpoint_descriptions.append({
                    'specification': json_data[i-1]['specification'],
                    'control_method': json_data[i-1]['control_method']
                })
            else:
                checkpoint_descriptions.append({
                    'specification': f'Checkpoint {i}',
                    'control_method': 'visual'
                })
    except NameError:
        # If json_data isn't available, create default descriptions
        checkpoint_descriptions = [
            {'specification': f'Checkpoint {i}', 'control_method': 'visual'} 
            for i in range(1, 27)
        ]
    
    # Write the legend for checkpoints
    for i, item in enumerate(checkpoint_descriptions):
        if i < 26:  # We only have 25 checkpoints
            col = i + 6  # Start after the main columns
            cell_text = f"{item['specification']}\n({item['control_method']})"
            worksheet.write(legend_row, col, cell_text, checkpoint_format)
    
    worksheet.set_row(legend_row, 40)  # Height for the checkpoint descriptions
    
    # Write data
    row = legend_row + 1  # Start data after legend row
    for i, obj in enumerate(queryset):
        worksheet.write(row, 0, i+1, cell_format)  # S.No
        worksheet.write(row, 1, str(obj.process_operation), cell_format)  # Process/Operation
        worksheet.write(row, 2, obj.rev_number, cell_format)  # Rev No
        worksheet.write(row, 3, obj.effective_date.strftime('%Y-%m-%d'), cell_format)  # Effective Date
        worksheet.write(row, 4, obj.month.strftime('%Y-%m'), cell_format)  # Month
        worksheet.write(row, 5, obj.manager.username, cell_format)  # Manager
        
        # Write checkpoint statuses
        for j in range(1, 27):
            checkpoint_value = getattr(obj, f'checkpoint_{j}')
            if checkpoint_value == '✔':
                worksheet.write(row, 5+j, checkpoint_value, ok_format)
            else:
                worksheet.write(row, 5+j, checkpoint_value, not_ok_format)
        
        # Write verified status
        if obj.verified_by == '✔':
            worksheet.write(row, 32, 'Verified', ok_format)
        else:
            worksheet.write(row, 32, 'Not Verified', not_ok_format)
        
        row += 1
    
    # Add footer information
    row += 2  # Add space before footer
    footer_format = workbook.add_format({
        'font_size': 10,
        'italic': True,
        'align': 'center'
    })
    worksheet.merge_range(row, 0, row, 32, 'Confidential Document - For Internal Use Only', footer_format)
    
    workbook.close()
    output.seek(0)
    
    response = HttpResponse(
        output.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename=startup_checksheets_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    return response


# CreateView to create a new StartUpCheckSheet entry
from django.contrib import messages
from .forms import StartUpCheckSheetForm
from user_app.models import Profile
from .models import StartUpCheckSheet, MachineLocation
from django.views.decorators.http import require_http_methods

@require_http_methods(["GET", "POST"])
def startup_checksheet_create_view(request):
    try:
        profile = Profile.objects.get(user=request.user)
        user_skill_level = profile.my_skill
    except Profile.DoesNotExist:
        user_skill_level = 0  # Default skill level if no profile exists
    
    if request.method == 'POST':
        form = StartUpCheckSheetForm(request.POST)
        if form.is_valid():
      
            try:
                    checksheet = form.save(commit=False)
                    checksheet.manager = request.user   
                    checksheet.request = request
             
                # Handle the dynamic checkpoint fields
                    for i in range(1, 27):  # Assuming 25 checkpoints
                        checkpoint_key = f'checkpoint_{i}'
                        if checkpoint_key in request.POST:
                            setattr(checksheet, checkpoint_key, request.POST[checkpoint_key])
                    
                    checksheet.save()
                    messages.success(request, 'Check sheet created successfully.')
                    return redirect('checksheet_create')  # Make sure this URL name is correct
            except Exception as e:
                    messages.error(request, f'Error saving check sheet: {str(e)}')
        else:
                print("Form is not valid.")
                print("Form errors:", form.errors)
                messages.error(request, 'Please correct the errors below.')
    else:
            form = StartUpCheckSheetForm()

    # Prepare checkpoint fields
    checkpoint_fields = [form[f'checkpoint_{i}'] for i in range(1, 27)]  # Assuming 25 checkpoints

    # Replace this with your actual data source
    json_data = [
    {
        "s_no": 1,
        "checkpoint": "प्लान के अनुसार पार्ट असेंबली और चाइल्ड पार्ट्स को वर्किंग टेबल पर रखें।",
        "specification": "Part assy & Child parts",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
        "s_no": 2,
        "checkpoint": "अपने कार्य स्थल को साफ रखें, कार्य स्थल पर धूल या गंदगी नहीं होनी चाहिए।",
        "specification": "साफ-सफाई",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
        "s_no": 3,
        "checkpoint": "कार्य शुरू करने से पहले वर्किंग टेबल से अनावश्यक पार्ट्स / मटेरियल हटा दें और उन्हें उनकी निर्धारित जगह पर रखें।",
        "specification": "वर्किंग टेबल पर अनावश्यक पार्ट्स / मटेरियल न हों",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
        "s_no": 4,
        "checkpoint": "गंदे ट्रे का उपयोग लाइन पर न करें, उसे साफ करने के लिए निर्धारित स्थान पर रखें।",
        "specification": "गंदे ट्रे लाइन पर न हों",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
        "s_no": 5,
        "checkpoint": "चेक करें कि फिक्स्चर / मशीन की स्थिति ठीक हो और सभी कनेक्शन्स सही व टाइट हों।",
        "specification": "फिक्स्चर / मशीन कंडीशन सही हो",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
        "s_no": 6,
        "checkpoint": "फिक्स्चर / मशीन पर लगे कैलिब्रेशन / वेरिफिकेशन टैग की डेट एक्सपायर न हो।",
        "specification": "कैलिब्रेशन / वेरिफिकेशन टैग वैलिड हो",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
        "s_no": 7,
        "checkpoint": "चेक करें कि ESD रिस्ट बैंड ठीक हो (जहां लागू हो), और वर्क इंस्ट्रक्शन के अनुसार सिग्नल लाल/हरा हो।",
        "specification": "ESD रिस्ट बैंड ठीक हो",
        "control_method": "Wrist Band tester",
        "frequency": "daily"
    },
    {
        "s_no": 8,
        "checkpoint": "ESD रिस्ट बैंड पहनें (जहां लागू हो)।",
        "specification": "ESD रिस्ट बैंड पहनना",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
        "s_no": 9,
        "checkpoint": "फेस मास्क पहनें (जहां लागू हो), और वह शॉप फ्लोर पर उपलब्ध हो।",
        "specification": "फेस मास्क पहनना",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
        "s_no": 10,
        "checkpoint": "ESD जैकेट और कैप, ESD ग्लव्स / फिंगर कोट्स पहनें।",
        "specification": "ESD जैकेट, कैप, ग्लव्स/फिंगर कोट्स पहनना",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
        "s_no": 11,
        "checkpoint": "चेक करें कि रेड ड्रॉअर में NG पार्ट्स रखने के लिए ट्रे उपलब्ध हो।",
        "specification": "NG पार्ट्स के लिए ट्रे उपलब्ध हो",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
        "s_no": 12,
        "checkpoint": "ड्रॉअर में आवश्यक टैग्स और PPEs उपलब्ध हों, जैसे: Reject Tag, OK Tag, Abnormal Situation Tag आदि।",
        "specification": "सभी आवश्यक टैग्स और PPEs उपलब्ध हों",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
        "s_no": 13,
        "checkpoint": "चेक करें कि ड्रॉअर में कोई अनुपयोगी वस्तु न हो।",
        "specification": "अनुपयोगी वस्तुएं न हों",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
        "s_no": 14,
        "checkpoint": "कार्य स्थल पर आवश्यक डॉक्युमेंट्स जैसे सेटअप शीट, FPA, डेली/मंथली रिजेक्शन शीट्स आदि उपलब्ध हों।",
        "specification": "सभी आवश्यक डॉक्युमेंट्स उपलब्ध हों",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
        "s_no": 15,
        "checkpoint": "लाइन पर OK/NG मास्टर सैंपल उपलब्ध हो और उसकी डेट एक्सपायर न हो।",
        "specification": "OK/NG मास्टर सैंपल वैलिड हो",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
        "s_no": 16,
        "checkpoint": "टी ब्रेक और लंच के समय बाहर जाते समय अपना सेटअप/सिस्टम बंद करें।",
        "specification": "ब्रेक में सिस्टम बंद करना",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
        "s_no": 17,
        "checkpoint": "टी ब्रेक और लंच में जाते समय लाइट्स बंद करें।",
        "specification": "ब्रेक में लाइट्स बंद करना",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
        "s_no": 18,
        "checkpoint": "ब्रेक के दौरान शॉप फ्लोर पर रहते समय जैकेट और कैप पहन कर रखें।",
        "specification": "ब्रेक में भी जैकेट और कैप पहनना",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
        "s_no": 19,
        "checkpoint": "FRL (प्रेशर गेज) की पिन को पुश करके 10-12 सेकंड तक एयर निकालें। यदि एयर के साथ पानी भी निकलता है तो तुरंत सुपरवाइजर को सूचित करें।",
        "specification": "FRL की पिन से एयर रिलीज करना",
        "control_method": "Visual / Manual",
        "frequency": "daily"
    },
    {
        "s_no": 20,
        "checkpoint": "रिजेक्ट हुए पार्ट्स के हैंडओवर की प्रक्रिया सही होनी चाहिए।",
        "specification": "हैंडओवर प्रक्रिया सही हो",
        "control_method": "Supervisor's verification",
        "frequency": "daily"
    },
    {
        "s_no": 21,
        "checkpoint": "ESD शूज़/स्लीपर्स पहनें (जहां लागू हो) और वे शॉप फ्लोर पर उपलब्ध हों।",
        "specification": "ESD शूज़/स्लीपर्स पहनना",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
        "s_no": 22,
        "checkpoint": "स्किल लेवल कार्ड चेक करें कि उसकी वैलिड डेट एक्सपायर न हो।",
        "specification": "स्किल कार्ड वैलिड हो",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
        "s_no": 23,
        "checkpoint": "ESD शूज़ / स्लीपर्स की स्थिति सही हो (जहां लागू हो)।",
        "specification": "ESD शूज़ / स्लीपर्स OK हों",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
        "s_no": 24,
        "checkpoint": "हर शिफ्ट की शुरुआत में POGO पिन्स की अच्छी तरह से सफाई करें।",
        "specification": "POGO पिन्स की सफाई",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
        "s_no": 25,
        "checkpoint": "कार्य शुरू करने से पहले क्योरिंग रैक की कंडीशन चेक करें कि टाइमर सेट हो और रैक डैमेज न हो।",
        "specification": "क्योरिंग रैक की स्थिति सही हो",
        "control_method": "visual",
        "frequency": "daily"
    },
        {
    "s_no": 26,
    "checkpoint": "सुनिश्चित करें कि ESD ब्रश का स्थिर चार्ज (Static Charge) <125V है| - By Supervisor (Where Applicable)",
    "specification": "<125 V",
    "control_method": "Electrostatic Field Meter",
    "frequency": "प्रतिमास"
},
]

    context = {
        'form': form,
        'json_data': json_data,
        'checkpoint_fields': checkpoint_fields,
        'user_skill_level':user_skill_level,
       }


    return render(request, 'startup/startup_checksheet_form.html',context)




def get_checkpoint_data():
    return [
    {
        "s_no": 1,
        "checkpoint": "प्लान के अनुसार पार्ट असेंबली और चाइल्ड पार्ट्स को वर्किंग टेबल पर रखें।",
        "specification": "Part assy & Child parts",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
        "s_no": 2,
        "checkpoint": "अपने कार्य स्थल को साफ रखें, कार्य स्थल पर धूल या गंदगी नहीं होनी चाहिए।",
        "specification": "साफ-सफाई",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
        "s_no": 3,
        "checkpoint": "कार्य शुरू करने से पहले वर्किंग टेबल से अनावश्यक पार्ट्स / मटेरियल हटा दें और उन्हें उनकी निर्धारित जगह पर रखें।",
        "specification": "वर्किंग टेबल पर अनावश्यक पार्ट्स / मटेरियल न हों",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
        "s_no": 4,
        "checkpoint": "गंदे ट्रे का उपयोग लाइन पर न करें, उसे साफ करने के लिए निर्धारित स्थान पर रखें।",
        "specification": "गंदे ट्रे लाइन पर न हों",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
        "s_no": 5,
        "checkpoint": "चेक करें कि फिक्स्चर / मशीन की स्थिति ठीक हो और सभी कनेक्शन्स सही व टाइट हों।",
        "specification": "फिक्स्चर / मशीन कंडीशन सही हो",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
        "s_no": 6,
        "checkpoint": "फिक्स्चर / मशीन पर लगे कैलिब्रेशन / वेरिफिकेशन टैग की डेट एक्सपायर न हो।",
        "specification": "कैलिब्रेशन / वेरिफिकेशन टैग वैलिड हो",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
        "s_no": 7,
        "checkpoint": "चेक करें कि ESD रिस्ट बैंड ठीक हो (जहां लागू हो), और वर्क इंस्ट्रक्शन के अनुसार सिग्नल लाल/हरा हो।",
        "specification": "ESD रिस्ट बैंड ठीक हो",
        "control_method": "Wrist Band tester",
        "frequency": "daily"
    },
    {
        "s_no": 8,
        "checkpoint": "ESD रिस्ट बैंड पहनें (जहां लागू हो)।",
        "specification": "ESD रिस्ट बैंड पहनना",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
        "s_no": 9,
        "checkpoint": "फेस मास्क पहनें (जहां लागू हो), और वह शॉप फ्लोर पर उपलब्ध हो।",
        "specification": "फेस मास्क पहनना",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
        "s_no": 10,
        "checkpoint": "ESD जैकेट और कैप, ESD ग्लव्स / फिंगर कोट्स पहनें।",
        "specification": "ESD जैकेट, कैप, ग्लव्स/फिंगर कोट्स पहनना",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
        "s_no": 11,
        "checkpoint": "चेक करें कि रेड ड्रॉअर में NG पार्ट्स रखने के लिए ट्रे उपलब्ध हो।",
        "specification": "NG पार्ट्स के लिए ट्रे उपलब्ध हो",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
        "s_no": 12,
        "checkpoint": "ड्रॉअर में आवश्यक टैग्स और PPEs उपलब्ध हों, जैसे: Reject Tag, OK Tag, Abnormal Situation Tag आदि।",
        "specification": "सभी आवश्यक टैग्स और PPEs उपलब्ध हों",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
        "s_no": 13,
        "checkpoint": "चेक करें कि ड्रॉअर में कोई अनुपयोगी वस्तु न हो।",
        "specification": "अनुपयोगी वस्तुएं न हों",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
        "s_no": 14,
        "checkpoint": "कार्य स्थल पर आवश्यक डॉक्युमेंट्स जैसे सेटअप शीट, FPA, डेली/मंथली रिजेक्शन शीट्स आदि उपलब्ध हों।",
        "specification": "सभी आवश्यक डॉक्युमेंट्स उपलब्ध हों",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
        "s_no": 15,
        "checkpoint": "लाइन पर OK/NG मास्टर सैंपल उपलब्ध हो और उसकी डेट एक्सपायर न हो।",
        "specification": "OK/NG मास्टर सैंपल वैलिड हो",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
        "s_no": 16,
        "checkpoint": "टी ब्रेक और लंच के समय बाहर जाते समय अपना सेटअप/सिस्टम बंद करें।",
        "specification": "ब्रेक में सिस्टम बंद करना",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
        "s_no": 17,
        "checkpoint": "टी ब्रेक और लंच में जाते समय लाइट्स बंद करें।",
        "specification": "ब्रेक में लाइट्स बंद करना",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
        "s_no": 18,
        "checkpoint": "ब्रेक के दौरान शॉप फ्लोर पर रहते समय जैकेट और कैप पहन कर रखें।",
        "specification": "ब्रेक में भी जैकेट और कैप पहनना",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
        "s_no": 19,
        "checkpoint": "FRL (प्रेशर गेज) की पिन को पुश करके 10-12 सेकंड तक एयर निकालें। यदि एयर के साथ पानी भी निकलता है तो तुरंत सुपरवाइजर को सूचित करें।",
        "specification": "FRL की पिन से एयर रिलीज करना",
        "control_method": "Visual / Manual",
        "frequency": "daily"
    },
    {
        "s_no": 20,
        "checkpoint": "रिजेक्ट हुए पार्ट्स के हैंडओवर की प्रक्रिया सही होनी चाहिए।",
        "specification": "हैंडओवर प्रक्रिया सही हो",
        "control_method": "Supervisor's verification",
        "frequency": "daily"
    },
    {
        "s_no": 21,
        "checkpoint": "ESD शूज़/स्लीपर्स पहनें (जहां लागू हो) और वे शॉप फ्लोर पर उपलब्ध हों।",
        "specification": "ESD शूज़/स्लीपर्स पहनना",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
        "s_no": 22,
        "checkpoint": "स्किल लेवल कार्ड चेक करें कि उसकी वैलिड डेट एक्सपायर न हो।",
        "specification": "स्किल कार्ड वैलिड हो",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
        "s_no": 23,
        "checkpoint": "ESD शूज़ / स्लीपर्स की स्थिति सही हो (जहां लागू हो)।",
        "specification": "ESD शूज़ / स्लीपर्स OK हों",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
        "s_no": 24,
        "checkpoint": "हर शिफ्ट की शुरुआत में POGO पिन्स की अच्छी तरह से सफाई करें।",
        "specification": "POGO पिन्स की सफाई",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
        "s_no": 25,
        "checkpoint": "कार्य शुरू करने से पहले क्योरिंग रैक की कंडीशन चेक करें कि टाइमर सेट हो और रैक डैमेज न हो।",
        "specification": "क्योरिंग रैक की स्थिति सही हो",
        "control_method": "visual",
        "frequency": "daily"
    },
        {
    "s_no": 26,
    "checkpoint": "सुनिश्चित करें कि ESD ब्रश का स्थिर चार्ज (Static Charge) <125V है| - By Supervisor (Where Applicable)",
    "specification": "<125 V",
    "control_method": "Electrostatic Field Meter",
    "frequency": "प्रतिमास"
},
]




class StartUpCheckSheetDetailView(DetailView):
    model = StartUpCheckSheet
    template_name = 'startup/startup_checksheet_detail.html'  # Create this template
    context_object_name = 'check_sheet'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['json_data'] = [

    {
        "s_no": 1,
        "checkpoint": "प्लान के अनुसार पार्ट असेंबली और चाइल्ड पार्ट्स को वर्किंग टेबल पर रखें।",
        "specification": "Part assy & Child parts",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
        "s_no": 2,
        "checkpoint": "अपने कार्य स्थल को साफ रखें, कार्य स्थल पर धूल या गंदगी नहीं होनी चाहिए।",
        "specification": "साफ-सफाई",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
        "s_no": 3,
        "checkpoint": "कार्य शुरू करने से पहले वर्किंग टेबल से अनावश्यक पार्ट्स / मटेरियल हटा दें और उन्हें उनकी निर्धारित जगह पर रखें।",
        "specification": "वर्किंग टेबल पर अनावश्यक पार्ट्स / मटेरियल न हों",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
        "s_no": 4,
        "checkpoint": "गंदे ट्रे का उपयोग लाइन पर न करें, उसे साफ करने के लिए निर्धारित स्थान पर रखें।",
        "specification": "गंदे ट्रे लाइन पर न हों",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
        "s_no": 5,
        "checkpoint": "चेक करें कि फिक्स्चर / मशीन की स्थिति ठीक हो और सभी कनेक्शन्स सही व टाइट हों।",
        "specification": "फिक्स्चर / मशीन कंडीशन सही हो",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
        "s_no": 6,
        "checkpoint": "फिक्स्चर / मशीन पर लगे कैलिब्रेशन / वेरिफिकेशन टैग की डेट एक्सपायर न हो।",
        "specification": "कैलिब्रेशन / वेरिफिकेशन टैग वैलिड हो",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
        "s_no": 7,
        "checkpoint": "चेक करें कि ESD रिस्ट बैंड ठीक हो (जहां लागू हो), और वर्क इंस्ट्रक्शन के अनुसार सिग्नल लाल/हरा हो।",
        "specification": "ESD रिस्ट बैंड ठीक हो",
        "control_method": "Wrist Band tester",
        "frequency": "daily"
    },
    {
        "s_no": 8,
        "checkpoint": "ESD रिस्ट बैंड पहनें (जहां लागू हो)।",
        "specification": "ESD रिस्ट बैंड पहनना",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
        "s_no": 9,
        "checkpoint": "फेस मास्क पहनें (जहां लागू हो), और वह शॉप फ्लोर पर उपलब्ध हो।",
        "specification": "फेस मास्क पहनना",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
        "s_no": 10,
        "checkpoint": "ESD जैकेट और कैप, ESD ग्लव्स / फिंगर कोट्स पहनें।",
        "specification": "ESD जैकेट, कैप, ग्लव्स/फिंगर कोट्स पहनना",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
        "s_no": 11,
        "checkpoint": "चेक करें कि रेड ड्रॉअर में NG पार्ट्स रखने के लिए ट्रे उपलब्ध हो।",
        "specification": "NG पार्ट्स के लिए ट्रे उपलब्ध हो",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
        "s_no": 12,
        "checkpoint": "ड्रॉअर में आवश्यक टैग्स और PPEs उपलब्ध हों, जैसे: Reject Tag, OK Tag, Abnormal Situation Tag आदि।",
        "specification": "सभी आवश्यक टैग्स और PPEs उपलब्ध हों",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
        "s_no": 13,
        "checkpoint": "चेक करें कि ड्रॉअर में कोई अनुपयोगी वस्तु न हो।",
        "specification": "अनुपयोगी वस्तुएं न हों",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
        "s_no": 14,
        "checkpoint": "कार्य स्थल पर आवश्यक डॉक्युमेंट्स जैसे सेटअप शीट, FPA, डेली/मंथली रिजेक्शन शीट्स आदि उपलब्ध हों।",
        "specification": "सभी आवश्यक डॉक्युमेंट्स उपलब्ध हों",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
        "s_no": 15,
        "checkpoint": "लाइन पर OK/NG मास्टर सैंपल उपलब्ध हो और उसकी डेट एक्सपायर न हो।",
        "specification": "OK/NG मास्टर सैंपल वैलिड हो",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
        "s_no": 16,
        "checkpoint": "टी ब्रेक और लंच के समय बाहर जाते समय अपना सेटअप/सिस्टम बंद करें।",
        "specification": "ब्रेक में सिस्टम बंद करना",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
        "s_no": 17,
        "checkpoint": "टी ब्रेक और लंच में जाते समय लाइट्स बंद करें।",
        "specification": "ब्रेक में लाइट्स बंद करना",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
        "s_no": 18,
        "checkpoint": "ब्रेक के दौरान शॉप फ्लोर पर रहते समय जैकेट और कैप पहन कर रखें।",
        "specification": "ब्रेक में भी जैकेट और कैप पहनना",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
        "s_no": 19,
        "checkpoint": "FRL (प्रेशर गेज) की पिन को पुश करके 10-12 सेकंड तक एयर निकालें। यदि एयर के साथ पानी भी निकलता है तो तुरंत सुपरवाइजर को सूचित करें।",
        "specification": "FRL की पिन से एयर रिलीज करना",
        "control_method": "Visual / Manual",
        "frequency": "daily"
    },
    {
        "s_no": 20,
        "checkpoint": "रिजेक्ट हुए पार्ट्स के हैंडओवर की प्रक्रिया सही होनी चाहिए।",
        "specification": "हैंडओवर प्रक्रिया सही हो",
        "control_method": "Supervisor's verification",
        "frequency": "daily"
    },
    {
        "s_no": 21,
        "checkpoint": "ESD शूज़/स्लीपर्स पहनें (जहां लागू हो) और वे शॉप फ्लोर पर उपलब्ध हों।",
        "specification": "ESD शूज़/स्लीपर्स पहनना",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
        "s_no": 22,
        "checkpoint": "स्किल लेवल कार्ड चेक करें कि उसकी वैलिड डेट एक्सपायर न हो।",
        "specification": "स्किल कार्ड वैलिड हो",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
        "s_no": 23,
        "checkpoint": "ESD शूज़ / स्लीपर्स की स्थिति सही हो (जहां लागू हो)।",
        "specification": "ESD शूज़ / स्लीपर्स OK हों",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
        "s_no": 24,
        "checkpoint": "हर शिफ्ट की शुरुआत में POGO पिन्स की अच्छी तरह से सफाई करें।",
        "specification": "POGO पिन्स की सफाई",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
        "s_no": 25,
        "checkpoint": "कार्य शुरू करने से पहले क्योरिंग रैक की कंडीशन चेक करें कि टाइमर सेट हो और रैक डैमेज न हो।",
        "specification": "क्योरिंग रैक की स्थिति सही हो",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
    "s_no": 26,
    "checkpoint": "सुनिश्चित करें कि ESD ब्रश का स्थिर चार्ज (Static Charge) <125V है| - By Supervisor (Where Applicable)",
    "specification": "<125 V",
    "control_method": "Electrostatic Field Meter",
    "frequency": "प्रतिमास"
},
]

   
    
        check_sheet = self.object
        context['checkpoint_fields'] = []
        for i in range(1, 27):  # Assuming 25 checkpoints
            field_name = f'checkpoint_{i}'
            field_value = getattr(check_sheet, field_name, '')
            context['checkpoint_fields'].append(field_value)
        
        return context
        
class StartUpCheckSheetUpdateView(UpdateView):
    model = StartUpCheckSheet
    form_class = StartUpCheckSheetForm
    template_name = 'startup/startup_checksheet_form.html'  # Reuse the form template
    success_url = reverse_lazy('checksheet_list')  # Redirect to list view after update
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['json_data'] = get_checkpoint_data()
        return context
    

class StartUpCheckSheetDeleteView(DeleteView):
    model = StartUpCheckSheet
    template_name = 'startup/startup_checksheet_confirm_delete.html'  # Create this template
    success_url = reverse_lazy('checksheet_list')  # Redirect to list view after deletion





# from django.http import JsonResponse
# from .models import MachineLocation

# def get_process_info(request):
#     process_operation_id = request.GET.get('process_operation_id')
#     try:
#         process_operation = MachineLocation.objects.get(id=process_operation_id)
#         data = {
#             'name': process_operation.name,
#             'min_skill_required': process_operation.min_skill_required,
#             # Add any other necessary fields here
#         }
#         return JsonResponse(data)
#     except MachineLocation.DoesNotExist:
#         return JsonResponse({'error': 'Process operation not found'}, status=404)
    
    
    
from .models import MachineLocation  # Assuming you have imported MachineLocation

def get_process_info(request, location_id):
    try:
        machine_location = get_object_or_404(MachineLocation, id=location_id)
        return JsonResponse({'required_skill': machine_location.min_skill_required})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def get_machine_skill(request, machine_id):
    try:
        machine = get_object_or_404(MachineLocation, id=machine_id)
        try:
            profile = Profile.objects.get(user=request.user)
            user_skill_level = profile.my_skill
        except Profile.DoesNotExist:
            user_skill_level = 0

        return JsonResponse({
            'required_skill': machine.min_skill_required,
            'user_skill_level': user_skill_level
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
    
    
    

from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import PChartData
from .forms import PChartDataForm

from django.http import HttpResponse
import xlsxwriter
from io import BytesIO
from django.utils import timezone

class PChartDataListView(ListView):
    model = PChartData
    template_name = 'pchart/pchart_list.html'
    context_object_name = 'pchart_data'

    def get(self, request, *args, **kwargs):
        if request.GET.get('export') == 'excel':
            queryset = self.get_queryset()
            return self.export_excel(queryset)
        return super().get(request, *args, **kwargs)

    def export_excel(self, queryset):
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet('P-Chart Data')

        # Define formats
        header_format = workbook.add_format({
            'bold': True,
            'font_size': 12,
            'bg_color': '#0033CC',
            'font_color': 'white',
            'border': 1,
            'align': 'center',
            'valign': 'vcenter'
        })

        cell_format = workbook.add_format({
            'font_size': 11,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter'
        })
        
        # Add date format - specify the format strings more explicitly
        date_format = workbook.add_format({
            'font_size': 11,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'num_format': 'yyyy-mm-dd'  # Standard date format
        })

        # Write title
        worksheet.merge_range('A1:G1', 'P-Chart Data Report', 
            workbook.add_format({
                'bold': True,
                'font_size': 16,
                'align': 'center',
                'valign': 'vcenter'
            }))

        # Add generation timestamp
        worksheet.merge_range('A2:G2', 
            f'Generated: {timezone.now().strftime("%Y-%m-%d %H:%M:%S")}',
            workbook.add_format({
                'align': 'right', 
                'italic': True
            }))

        # Set column widths
        worksheet.set_column('A:A', 20)  # Location
        worksheet.set_column('B:B', 30)  # Part Number and Name
        worksheet.set_column('C:C', 15)  # Sample Size
        worksheet.set_column('D:D', 15)  # Rejection
        worksheet.set_column('E:E', 15)  # UCL-P
        worksheet.set_column('F:F', 15)  # LCL-P
        worksheet.set_column('G:G', 20)  # Date

        # Write headers
        headers = ['Location', 'Part Number and Name', 'Sample Size', 'Rejection', 'UCL-P', 'LCL-P', 'Date']
        for col, header in enumerate(headers):
            worksheet.write(3, col, header, header_format)

        # Write data
        for row, data in enumerate(queryset, start=4):
            worksheet.write(row, 0, data.location, cell_format)
            worksheet.write(row, 1, data.part_number_and_name, cell_format)
            worksheet.write(row, 2, data.sample_size, cell_format)
            worksheet.write(row, 3, data.nonconforming_units, cell_format)
            worksheet.write(row, 4, data.ucl_p, cell_format)
            worksheet.write(row, 5, data.lcl_p, cell_format)
            
            # Handle date field specifically
            try:
                # Try to convert the date string to datetime if it's not already
                if isinstance(data.date_control_limits_calculated, str):
                    from datetime import datetime
                    # Try different formats if needed
                    try:
                        # Try standard ISO format
                        date_obj = datetime.strptime(data.date_control_limits_calculated, '%Y-%m-%d')
                    except ValueError:
                        try:
                            # Try with time component
                            date_obj = datetime.strptime(data.date_control_limits_calculated, '%Y-%m-%d %H:%M:%S')
                        except ValueError:
                            # If all else fails, just write as string
                            worksheet.write(row, 6, data.date_control_limits_calculated, cell_format)
                            continue
                    
                    # Write the datetime object with date format
                    worksheet.write_datetime(row, 6, date_obj, date_format)
                else:
                    # Already a datetime object
                    worksheet.write_datetime(row, 6, data.date_control_limits_calculated, date_format)
            except Exception:
                # Fallback - just write the value as is
                worksheet.write(row, 6, str(data.date_control_limits_calculated), cell_format)

        workbook.close()
        output.seek(0)

        # Generate filename
        filename = f"pchart_data_{timezone.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

        response = HttpResponse(
            output.read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response
        
class PChartDataDetailView(DetailView):
    model = PChartData
    template_name = 'pchart/pchart_detail.html'
    context_object_name = 'pchart_data'

class PChartDataCreateView(CreateView):
    model = PChartData
    form_class = PChartDataForm
    template_name = 'pchart/pchart_form.html'
    success_url = reverse_lazy('dashboard')  # Redirects to the dashboard

    def form_valid(self, form):
        """
        Override form_valid to attach the request object to the instance
        before saving, which enables machine detection in the save method.
        """
        self.object = form.save(commit=False)
        # Attach the request to the instance
        self.object.request = self.request
        # Save the instance
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())

class PChartDataUpdateView(UpdateView):
    model = PChartData
    form_class = PChartDataForm
    template_name = 'pchart/pchart_form.html'
    success_url = reverse_lazy('pchart_list')

class PChartDataDeleteView(DeleteView):
    model = PChartData
    template_name = 'pchart/pchart_confirm_delete.html'
    success_url = reverse_lazy('pchart_list')    
    
    
from django.views.generic import TemplateView
from django.db.models import Avg
import json

from .models import PChartData, MACHINE_LOCATION_CHOICES

class PChartView(TemplateView):
    template_name = 'pchart/pchart_chart.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        location = self.request.GET.get('location')
        selected_month = self.request.GET.get('selected_month')
        
        queryset = PChartData.objects.all().order_by('date')
        
        if location:
            queryset = queryset.filter(location=location)
        
        # Store available months for the dropdown
        available_months = []
        month_set = set()
        
        for data in queryset:
            month_key = data.date.strftime('%Y-%m')
            month_display = data.date.strftime('%b %Y')
            
            if month_key not in month_set:
                month_set.add(month_key)
                available_months.append({
                    'value': month_key,
                    'display': month_display
                })
        
        # Sort months chronologically
        available_months.sort(key=lambda x: x['value'])
        
        # Process monthly data (aggregated view)
        monthly_data = {}
        
        for data in queryset:
            month_key = data.date.strftime('%Y-%m')
            if month_key not in monthly_data:
                monthly_data[month_key] = {
                    'month_display': data.date.strftime('%b %Y'),
                    'entries': [],
                    'total_sample_size': 0,
                    'total_nonconforming': 0,
                    'days_count': 0
                }
            
            monthly_data[month_key]['entries'].append(data)
            monthly_data[month_key]['total_sample_size'] += data.sample_size
            monthly_data[month_key]['total_nonconforming'] += data.nonconforming_units
            monthly_data[month_key]['days_count'] += 1
        
        # Calculate monthly averages and control limits
        chart_data = {
            'labels': [],
            'proportion': [],
            'ucl_p': [],
            'lcl_p': [],
            'center_line': [],
            'sample_sizes': [],
            'days_count': []
        }
        
        overall_proportion = 0
        total_entries = 0
        
        for month_key in sorted(monthly_data.keys()):
            month_info = monthly_data[month_key]
            
            # Skip months with no data
            if month_info['days_count'] == 0:
                continue
            
            # Calculate monthly proportion
            monthly_proportion = month_info['total_nonconforming'] / month_info['total_sample_size'] if month_info['total_sample_size'] > 0 else 0
            
            # Calculate average sample size per day for this month
            avg_sample_size = month_info['total_sample_size'] / month_info['days_count']
            
            # Calculate control limits for this month
            if monthly_proportion > 0 and monthly_proportion < 1 and avg_sample_size > 0:
                p_std = ((monthly_proportion * (1 - monthly_proportion)) / avg_sample_size) ** 0.5
                ucl = min(1, monthly_proportion + 3 * p_std)
                lcl = max(0, monthly_proportion - 3 * p_std)
            else:
                ucl = 0
                lcl = 0
            
            # Add to chart data
            chart_data['labels'].append(month_info['month_display'])
            chart_data['proportion'].append(round(monthly_proportion, 4))
            chart_data['ucl_p'].append(round(ucl, 4))
            chart_data['lcl_p'].append(round(lcl, 4))
            chart_data['sample_sizes'].append(month_info['total_sample_size'])
            chart_data['days_count'].append(month_info['days_count'])
            
            # Accumulate for overall average
            overall_proportion += monthly_proportion
            total_entries += 1
        
        # Calculate overall average proportion for center line
        avg_proportion = overall_proportion / total_entries if total_entries > 0 else 0
        chart_data['center_line'] = [round(avg_proportion, 4)] * len(chart_data['labels'])
        
        # Process daily data if a month is selected
        daily_data = {
            'labels': [],
            'proportion': [],
            'ucl_p': [],
            'lcl_p': [],
            'center_line': [],
            'sample_sizes': [],
            'nonconforming': [],
            'month_display': ''
        }
        
        if selected_month:
            # Filter data for the selected month
            year, month = selected_month.split('-')
            daily_queryset = queryset.filter(date__year=int(year), 
                                            date__month=int(month))
            
            if daily_queryset.exists():
                # Get month display name
                daily_data['month_display'] = daily_queryset.first().date.strftime('%B %Y')
                
                # Calculate control lines for daily data
                total_sample = sum(d.sample_size for d in daily_queryset)
                total_nonconforming = sum(d.nonconforming_units for d in daily_queryset)
                p_bar = total_nonconforming / total_sample if total_sample > 0 else 0
                
                # Process each day's data
                for data in daily_queryset.order_by('date'):
                    date_str = data.date.strftime('%d %b')
                    
                    # Use existing control limits if available, otherwise calculate
                    if hasattr(data, 'ucl_p') and hasattr(data, 'lcl_p') and data.date_control_limits_calculated:
                        ucl = data.ucl_p
                        lcl = data.lcl_p
                        proportion = data.proportion
                    else:
                        proportion = data.nonconforming_units / data.sample_size if data.sample_size > 0 else 0
                        
                        # Calculate control limits
                        if p_bar > 0 and p_bar < 1 and data.sample_size > 0:
                            p_std = ((p_bar * (1 - p_bar)) / data.sample_size) ** 0.5
                            ucl = min(1, p_bar + 3 * p_std)
                            lcl = max(0, p_bar - 3 * p_std)
                        else:
                            ucl = 0
                            lcl = 0
                    
                    daily_data['labels'].append(date_str)
                    daily_data['proportion'].append(round(proportion, 4))
                    daily_data['ucl_p'].append(round(ucl, 4))
                    daily_data['lcl_p'].append(round(lcl, 4))
                    daily_data['sample_sizes'].append(data.sample_size)
                    daily_data['nonconforming'].append(data.nonconforming_units)
                
                # Set center line (average proportion)
                daily_data['center_line'] = [round(p_bar, 4)] * len(daily_data['labels'])
        
        context.update({
            'chart_data': json.dumps(chart_data),
            'daily_data': json.dumps(daily_data),
            'locations': dict(MACHINE_LOCATION_CHOICES),
            'selected_location': location,
            'selected_month': selected_month,
            'available_months': available_months
        })
        
        return context





# views.py
from django.views.generic import ListView
from django.apps import apps
from django.utils import timezone
from datetime import timedelta, datetime
from .settings import AUDIT_HISTORY_RETENTION_CHOICES, DEFAULT_AUDIT_RETENTION

class AuditHistoryView(ListView):
    template_name = 'audit_history.html'
    paginate_by = 50
    context_object_name = 'history_records'

    def get_changes(self, record):
        if record.history_type == '~':
            try:
                old_record = record.prev_record
                changes = []
                for field in record._meta.fields:
                    if field.name not in ['history_id', 'history_date', 'history_type', 'history_user', 'history_change_reason', 'id']:
                        old_value = getattr(old_record, field.name) if old_record else None
                        new_value = getattr(record, field.name)
                        if old_value != new_value:
                            changes.append({
                                'field': field.verbose_name.title(),
                                'old': old_value,
                                'new': new_value
                            })
                return changes
            except:
                return []
        return []

    def get_retention_date(self):
        retention_period = self.request.GET.get('retention', DEFAULT_AUDIT_RETENTION)
        if retention_period == 'all':
            return None
            
        retention_days = AUDIT_HISTORY_RETENTION_CHOICES[retention_period]['days']
        return timezone.now() - timedelta(days=retention_days)

    def get_queryset(self):
        history_models = []
        for model in apps.get_models():
            if hasattr(model, 'history'):
                history_models.append(model)

        combined_history = []
        retention_date = self.get_retention_date()
        
        # Get date filters
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')
        module = self.request.GET.get('module')
        event_type = self.request.GET.get('event_type')
        
        for model in history_models:
            records = model.history.all()
            
            if retention_date:
                records = records.filter(history_date__gte=retention_date)
            if date_from:
                records = records.filter(history_date__date__gte=datetime.strptime(date_from, '%Y-%m-%d').date())
            if date_to:
                records = records.filter(history_date__date__lte=datetime.strptime(date_to, '%Y-%m-%d').date())
            if event_type:
                records = records.filter(history_type=event_type)
                
            for record in records:
                record.change_list = self.get_changes(record)
                record.model_name = record._meta.verbose_name.title()
                if module and record.model_name != module:
                    continue
                combined_history.append(record)

        return sorted(combined_history, 
                     key=lambda x: x.history_date, 
                     reverse=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset()
        context.update({
            'title': 'Audit History',
            'retention_choices': AUDIT_HISTORY_RETENTION_CHOICES,
            'current_retention': self.request.GET.get('retention', DEFAULT_AUDIT_RETENTION),
            'available_modules': sorted(set(record.model_name for record in queryset)),
            'date_from': self.request.GET.get('date_from', ''),
            'date_to': self.request.GET.get('date_to', ''),
            'selected_module': self.request.GET.get('module', ''),
            'selected_event_type': self.request.GET.get('event_type', '')
        })
        return context
    
    
    
from django.http import JsonResponse
from django.utils import timezone



def check_notifications(request):
    latest_reading = ControlChartReading.objects.filter(date=timezone.now().date()).first()
    
    if latest_reading:
        should_notify = (
            not latest_reading.last_notification_time or 
            (timezone.now() - latest_reading.last_notification_time).total_seconds() >= 3600
        )
        
        if should_notify:
            latest_reading.update_notification_status()
            
        return JsonResponse({
            'show_notification': should_notify,
            'remaining_entries': latest_reading.remaining_entries,
        })
    
    return JsonResponse({
        'show_notification': True,
        'remaining_entries': 5
    })    
    



# --------
from django.views import View
from django.views.generic import ListView, UpdateView, DeleteView
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.db.models import Q
from datetime import datetime
from io import BytesIO
import xlsxwriter
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from django.contrib.staticfiles import finders

from .models import PCBPanelInspectionRecord, ProcessMachineMapping
from .forms import PCBPanelInspectionRecordForm, PCBPanelInspectionRecordSearchForm


@method_decorator(login_required, name='dispatch')
class AddPCBPanelInspectionRecordView(View):
    def get(self, request):
        form = PCBPanelInspectionRecordForm()
        process_machines = ProcessMachineMapping.objects.all()
        return render(request, 'pcb/pcb_form.html', {
            'form': form,
            'process_machines': process_machines
        })

    def post(self, request):
        form = PCBPanelInspectionRecordForm(request.POST)
        if form.is_valid():
            pcb_record = form.save(commit=False)
            pcb_record.operator_name = request.user
            pcb_record.request = request  # Pass request to access session in save method
            pcb_record.save()
            messages.success(request, "PCB panel inspection record added successfully.")
            return redirect('add_pcb_inspection_record')
        else:
            messages.error(request, "There was an error adding the PCB inspection record. Please check the form and try again.")
        return render(request, 'pcb/pcb_form.html', {'form': form})


class ListPCBPanelInspectionRecordView(ListView):
    model = PCBPanelInspectionRecord
    template_name = 'pcb/list_pcb_records.html'
    context_object_name = 'records'
    ordering = ['-date']
    
    def get(self, request, *args, **kwargs):
        # Handle export requests separately
        export_format = request.GET.get('export')
        if export_format:
            queryset = self.get_filtered_queryset()
            return self.export_data(queryset, export_format)
        
        # Regular page display
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = PCBPanelInspectionRecordSearchForm(self.request.GET)
        return context

    def get_filtered_queryset(self):
        queryset = self.model.objects.all().order_by(*self.ordering)
        form = PCBPanelInspectionRecordSearchForm(self.request.GET)
        
        if form.is_valid():
            if start_date := form.cleaned_data.get('start_date'):
                queryset = queryset.filter(date__gte=start_date)
            if end_date := form.cleaned_data.get('end_date'):
                queryset = queryset.filter(date__lte=end_date)
            if pcb_number := form.cleaned_data.get('pcb_number'):
                queryset = queryset.filter(pcb_number__icontains=pcb_number)
            if customer := form.cleaned_data.get('customer'):
                queryset = queryset.filter(customer__icontains=customer)
            if pcb_batch_code := form.cleaned_data.get('pcb_batch_code'):
                queryset = queryset.filter(pcb_batch_code__icontains=pcb_batch_code)
            if shift := form.cleaned_data.get('shift'):
                queryset = queryset.filter(shift=shift)
            if inspection_status := form.cleaned_data.get('inspection_status'):
                queryset = queryset.filter(
                    Q(no_masking_issue=inspection_status) | 
                    Q(no_dust_contamination=inspection_status) | 
                    Q(no_track_damage=inspection_status)
                )
        
        return queryset

    def get_queryset(self):
        return self.get_filtered_queryset()
    
    def get_logo_path(self):
        """Get the absolute path to the logo file from static files"""
        return finders.find('images/image.png')

    def export_data(self, queryset, format):
        if format == 'excel':
            return self.export_excel(queryset)
        elif format == 'pdf':
            return self.export_pdf(queryset)

    def export_excel(self, queryset):
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet('PCB Panel Inspection Records')
        
        # Insert logo
        logo_path = self.get_logo_path()
        if logo_path:
            worksheet.insert_image('A1', logo_path, {
                'x_scale': 0.5,
                'y_scale': 0.5,
                'x_offset': 10,
                'y_offset': 10
            })
            
        # Define formats
        header_format = workbook.add_format({
            'bold': True,
            'font_size': 12,
            'font_name': 'Arial',
            'bg_color': '#1E40AF',  # primaryColor
            'font_color': 'white',
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'text_wrap': True
        })

        cell_format = workbook.add_format({
            'font_size': 11,
            'font_name': 'Arial',
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'text_wrap': True
        })

        date_format = workbook.add_format({
            'font_size': 11,
            'font_name': 'Arial',
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'num_format': 'yyyy-mm-dd'
        })

        ok_format = workbook.add_format({
            'font_size': 11,
            'font_name': 'Arial',
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#DCF5DC'  # Light green background
        })

        not_ok_format = workbook.add_format({
            'font_size': 11,
            'font_name': 'Arial',
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#FFE6E6'  # Light red background
        })

        # Set column widths
        worksheet.set_column('A:A', 15)  # PCB Number
        worksheet.set_column('B:B', 15)  # Customer
        worksheet.set_column('C:C', 15)  # Batch Code
        worksheet.set_column('D:D', 8)   # Shift
        worksheet.set_column('E:E', 12)  # Date
        worksheet.set_column('F:F', 10)  # Qty
        worksheet.set_column('G:I', 15)  # Inspection columns
        worksheet.set_column('J:J', 20)  # Operator
        worksheet.set_column('K:K', 20)  # Verified By

        # Write title
        title_format = workbook.add_format({
            'bold': True,
            'font_size': 16,
            'font_name': 'Arial',
            'align': 'center',
            'valign': 'vcenter',
            'font_color': '#1E40AF'  # primaryColor
        })
        worksheet.merge_range('A1:K1', 'PCB Panel Inspection Records Report', title_format)
        worksheet.set_row(0, 30)  # Set title row height

        # Write timestamp
        timestamp_format = workbook.add_format({
            'italic': True,
            'font_size': 10,
            'align': 'right'
        })
        worksheet.merge_range('A2:K2', f'Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', timestamp_format)

        # Headers (start from row 3)
        headers = [
            'PCB No./Rev.', 'Customer', 'Batch Code', 'Shift', 'Date', 'Inspection Qty',
            'No Masking Issue', 'No Dust/Contamination', 'No Track Damage', 
            'Operator', 'Verified By'
        ]
        for col, header in enumerate(headers):
            worksheet.write(3, col, header, header_format)

        # Write data
        for row, record in enumerate(queryset, start=4):
            worksheet.write(row, 0, record.pcb_number, cell_format)
            worksheet.write(row, 1, record.customer, cell_format)
            worksheet.write(row, 2, record.pcb_batch_code, cell_format)
            worksheet.write(row, 3, record.shift, cell_format)
            worksheet.write(row, 4, record.date, date_format)
            worksheet.write(row, 5, record.inspection_qty, cell_format)
            
            # Status columns with conditional formatting
            for col, status in enumerate([
                record.no_masking_issue,
                record.no_dust_contamination,
                record.no_track_damage
            ], 6):
                format_to_use = ok_format if status == 'OK' else not_ok_format
                worksheet.write(row, col, status, format_to_use)
            
            worksheet.write(row, 9, record.operator_name.username if record.operator_name else '-', cell_format)
            worksheet.write(row, 10, record.verified_by.username if record.verified_by else '-', cell_format)

        workbook.close()
        output.seek(0)

        response = HttpResponse(
            output.read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename=pcb_inspection_records_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        return response

    def export_pdf(self, queryset):
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename=pcb_inspection_records_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'

        # Create the PDF object using ReportLab
        doc = SimpleDocTemplate(
            response,
            pagesize=landscape(letter),
            rightMargin=30,
            leftMargin=30,
            topMargin=30,
            bottomMargin=30
        )

        # Container for PDF elements
        elements = []
        
        # Add logo
        logo_path = self.get_logo_path()
        if logo_path:
            im = Image(logo_path)
            # Set logo dimensions
            im.drawHeight = 0.50*inch
            im.drawWidth = 2.5*inch
            elements.append(im)
            elements.append(Spacer(1, 12))  # Add space after logo

        # Define styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1E40AF'),
            spaceAfter=30,
            alignment=1
        )

        # Add title
        elements.append(Paragraph('PCB Panel Inspection Records Report', title_style))
        
        # Add timestamp
        timestamp_style = ParagraphStyle(
            'Timestamp',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.grey,
            alignment=2
        )
        elements.append(Paragraph(
            f'Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
            timestamp_style
        ))
        elements.append(Spacer(1, 20))

        # Prepare data for table
        data = [[
            'PCB No./Rev.', 'Customer', 'Batch Code', 'Shift', 'Date', 'Qty',
            'No Masking', 'No Dust', 'No Damage', 'Operator', 'Verified By'
        ]]
        
        # Add data rows
        for record in queryset:
            data.append([
                record.pcb_number,
                record.customer,
                record.pcb_batch_code,
                record.shift,
                record.date.strftime('%Y-%m-%d'),
                str(record.inspection_qty),
                record.no_masking_issue,
                record.no_dust_contamination,
                record.no_track_damage,
                record.operator_name.username if record.operator_name else '-',
                record.verified_by.username if record.verified_by else '-',
            ])

        # Define table style
        table_style = TableStyle([
            # Header styling
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E40AF')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            
            # Data rows
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWHEIGHTS', (0, 0), (-1, -1), 30),
        ])

        # Add conditional background colors for status columns
        for row_idx in range(1, len(data)):
            for col_idx in range(6, 9):  # Status columns (6-8)
                if data[row_idx][col_idx] == 'OK':
                    table_style.add('BACKGROUND', (col_idx, row_idx), (col_idx, row_idx), 
                                colors.HexColor('#DCF5DC'))
                elif data[row_idx][col_idx] == 'Not OK':
                    table_style.add('BACKGROUND', (col_idx, row_idx), (col_idx, row_idx), 
                                colors.HexColor('#FFE6E6'))

        # Create table with calculated column widths
        col_widths = [
            1.1*inch,  # PCB No./Rev.
            1.1*inch,  # Customer
            1.1*inch,  # Batch Code
            0.5*inch,  # Shift
            0.8*inch,  # Date
            0.5*inch,  # Qty
            0.8*inch,  # No Masking
            0.8*inch,  # No Dust
            0.8*inch,  # No Damage
            1.0*inch,  # Operator
            1.0*inch   # Verified By
        ]
        
        table = Table(data, colWidths=col_widths, repeatRows=1)
        table.setStyle(table_style)
        elements.append(table)

        # Build the PDF document
        doc.build(elements)
        return response


@method_decorator(staff_member_required, name='dispatch')
class UpdatePCBPanelInspectionRecordView(UpdateView):
    model = PCBPanelInspectionRecord
    form_class = PCBPanelInspectionRecordForm
    template_name = 'pcb/update_pcb_record.html'
    success_url = reverse_lazy('list_pcb_inspection_records')

    def form_valid(self, form):
        pcb_record = form.save(commit=False)
        pcb_record.request = self.request  # Pass request to access session in save method
        messages.success(self.request, "PCB panel inspection record updated successfully.")
        return super().form_valid(form)


@method_decorator(staff_member_required, name='dispatch')
class DeletePCBPanelInspectionRecordView(DeleteView):
    model = PCBPanelInspectionRecord
    template_name = 'pcb/delete_pcb_record.html'
    success_url = reverse_lazy('list_pcb_inspection_records')

    def delete(self, request, *args, **kwargs):
        messages.success(request, "PCB panel inspection record deleted successfully.")
        return super().delete(request, *args, **kwargs)


@method_decorator(staff_member_required, name='dispatch')
class PCBPanelInspectionRecordDetailView(View):
    def get(self, request, pk):
        record = get_object_or_404(PCBPanelInspectionRecord, pk=pk)
        return render(request, 'pcb/pcb_record_detail.html', {'record': record})
    
    
    
#--------------------------------------

from django.views import View
from django.views.generic import ListView, UpdateView, DeleteView
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.db.models import Q
from datetime import datetime
from io import BytesIO
import xlsxwriter
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from django.contrib.staticfiles import finders

from .models import ReworkAnalysisRecord
from .forms import ReworkAnalysisRecordForm, ReworkAnalysisRecordSearchForm

@method_decorator(login_required, name='dispatch')
class AddReworkAnalysisRecordView(View):
    def get(self, request):
        form = ReworkAnalysisRecordForm()
        return render(request, 'rework/rework_form.html', {
            'form': form,
        })

    def post(self, request):
        form = ReworkAnalysisRecordForm(request.POST)
        if form.is_valid():
            rework_record = form.save(commit=False)
            rework_record.created_by = request.user
            rework_record.request = request  # Pass request to access in save method
            rework_record.save()
            messages.success(request, "Rework analysis record added successfully.")
            return redirect('add_rework_analysis_record')
        else:
            messages.error(request, "There was an error adding the rework analysis record. Please check the form and try again.")
        return render(request, 'rework/rework_form.html', {'form': form})


class ListReworkAnalysisRecordView(ListView):
    model = ReworkAnalysisRecord
    template_name = 'rework/list_rework_records.html'
    context_object_name = 'records'
    
    def get(self, request, *args, **kwargs):
        # Handle export requests separately
        export_format = request.GET.get('export')
        if export_format:
            queryset = self.get_filtered_queryset()
            return self.export_data(queryset, export_format)
        
        # Regular page display
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = ReworkAnalysisRecordSearchForm(self.request.GET)
        return context

    def get_filtered_queryset(self):
        queryset = self.model.objects.all()
        form = ReworkAnalysisRecordSearchForm(self.request.GET)
        
        if form.is_valid():
            if start_date := form.cleaned_data.get('start_date'):
                queryset = queryset.filter(problem_found_date__gte=start_date)
            if end_date := form.cleaned_data.get('end_date'):
                queryset = queryset.filter(problem_found_date__lte=end_date)
            if part_identification := form.cleaned_data.get('part_identification'):
                queryset = queryset.filter(part_identification_no__icontains=part_identification)
            if defect_type := form.cleaned_data.get('defect_type'):
                queryset = queryset.filter(defects_details__icontains=defect_type)
            if part_status := form.cleaned_data.get('part_status'):
                queryset = queryset.filter(part_status=part_status)
            if verification_status := form.cleaned_data.get('verification_status'):
                queryset = queryset.filter(part_re_verification=verification_status)
            if department := form.cleaned_data.get('department'):
                queryset = queryset.filter(department_name__icontains=department)
        
        return queryset

    def get_queryset(self):
        return self.get_filtered_queryset()
    
    def get_logo_path(self):
        """Get the absolute path to the logo file from static files"""
        return finders.find('images/image.png')

    def export_data(self, queryset, format):
        if format == 'excel':
            return self.export_excel(queryset)
        elif format == 'pdf':
            return self.export_pdf(queryset)

    def export_excel(self, queryset):
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet('Rework Analysis Records')
        
        # Insert logo
        logo_path = self.get_logo_path()
        if logo_path:
            worksheet.insert_image('A1', logo_path, {
                'x_scale': 0.5,
                'y_scale': 0.5,
                'x_offset': 10,
                'y_offset': 10
            })
            
        # Define formats
        header_format = workbook.add_format({
            'bold': True,
            'font_size': 12,
            'font_name': 'Arial',
            'bg_color': '#1E40AF',  # primaryColor
            'font_color': 'white',
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'text_wrap': True
        })

        cell_format = workbook.add_format({
            'font_size': 11,
            'font_name': 'Arial',
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'text_wrap': True
        })

        date_format = workbook.add_format({
            'font_size': 11,
            'font_name': 'Arial',
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'num_format': 'yyyy-mm-dd'
        })

        pass_format = workbook.add_format({
            'font_size': 11,
            'font_name': 'Arial',
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#DCF5DC'  # Light green background
        })

        fail_format = workbook.add_format({
            'font_size': 11,
            'font_name': 'Arial',
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#FFE6E6'  # Light red background
        })

        # Set title & document info
        title_format = workbook.add_format({
            'bold': True,
            'font_size': 16,
            'font_name': 'Arial',
            'align': 'center',
            'valign': 'vcenter',
            'font_color': '#1E40AF'  # primaryColor
        })
        worksheet.merge_range('A1:U1', 'Rework Analysis & Re-verification Sheet', title_format)
        worksheet.merge_range('A2:U2', f'Document: QSF-22-02, Rev.03, Dated:29.12.2023', workbook.add_format({
            'font_size': 12,
            'font_name': 'Arial',
            'align': 'center',
            'valign': 'vcenter',
        }))
        worksheet.merge_range('A3:U3', f'Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', workbook.add_format({
            'italic': True,
            'font_size': 10,
            'align': 'right'
        }))

        # Set column widths
        worksheet.set_column('A:A', 5)   # Sr. No
        worksheet.set_column('B:C', 12)  # Dates
        worksheet.set_column('D:D', 10)  # Line/Shift
        worksheet.set_column('E:E', 15)  # Part ID
        worksheet.set_column('F:F', 10)  # Short Code
        worksheet.set_column('G:G', 15)  # Problem Stage
        worksheet.set_column('H:H', 20)  # Defect Details
        worksheet.set_column('I:I', 15)  # Location
        worksheet.set_column('J:J', 8)   # Qty
        worksheet.set_column('K:K', 12)  # Analysis Date
        worksheet.set_column('L:M', 15)  # Child part, Component
        worksheet.set_column('N:N', 20)  # Reason
        worksheet.set_column('O:O', 20)  # Rework Details
        worksheet.set_column('P:P', 12)  # Rework Date
        worksheet.set_column('Q:Q', 15)  # Rework by
        worksheet.set_column('R:R', 10)  # Status
        worksheet.set_column('S:S', 10)  # Verification
        worksheet.set_column('T:T', 15)  # Verified by
        worksheet.set_column('U:U', 15)  # Remarks

        # Headers (start from row 4)
        headers = [
            'Sr. No', 'Problem Found Date', 'Part Received Date', 'Line/Shift', 
            'Part ID No.', 'Short Code', 'Problem Stage', 'Defect Details', 
            'Defect Location', 'Qty', 'Analysis Date', 'Child Part Code', 
            'Component Size', 'Reason for Defect', 'Rework Details', 'Rework Date', 
            'Rework Done By', 'Part Status', 'Verification', 'Verified By', 'Remarks'
        ]
        for col, header in enumerate(headers):
            worksheet.write(4, col, header, header_format)

        # Write data
        for row, record in enumerate(queryset, start=5):
            worksheet.write(row, 0, record.sr_no, cell_format)
            worksheet.write(row, 1, record.problem_found_date, date_format)
            worksheet.write(row, 2, record.part_received_date, date_format)
            worksheet.write(row, 3, record.line_shift, cell_format)
            worksheet.write(row, 4, record.part_identification_no, cell_format)
            worksheet.write(row, 5, record.short_code, cell_format)
            worksheet.write(row, 6, record.problem_found_stage, cell_format)
            worksheet.write(row, 7, record.defects_details, cell_format)
            worksheet.write(row, 8, record.defect_location_on_pcb, cell_format)
            worksheet.write(row, 9, record.defect_qty, cell_format)
            worksheet.write(row, 10, record.analysis_date, date_format)
            worksheet.write(row, 11, record.child_part_im_code, cell_format)
            worksheet.write(row, 12, record.component_package_size, cell_format)
            worksheet.write(row, 13, record.reason_for_defect, cell_format)
            worksheet.write(row, 14, record.rework_details, cell_format)
            worksheet.write(row, 15, record.rework_date, date_format)
            worksheet.write(row, 16, record.rework_done_by, cell_format)
            worksheet.write(row, 17, record.part_status, cell_format)
            
            # Status column with conditional formatting
            format_to_use = pass_format if record.part_re_verification == 'Pass' else fail_format
            worksheet.write(row, 18, record.part_re_verification, format_to_use)
            
            worksheet.write(row, 19, record.verified_by, cell_format)
            worksheet.write(row, 20, record.remarks, cell_format)

        workbook.close()
        output.seek(0)

        response = HttpResponse(
            output.read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename=rework_analysis_records_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        return response

    def export_pdf(self, queryset):
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename=rework_analysis_records_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'

        # Create the PDF object using ReportLab
        doc = SimpleDocTemplate(
            response,
            pagesize=landscape(letter),
            rightMargin=30,
            leftMargin=30,
            topMargin=30,
            bottomMargin=30
        )

        # Container for PDF elements
        elements = []
        
        # Add logo
        logo_path = self.get_logo_path()
        if logo_path:
            im = Image(logo_path)
            # Set logo dimensions
            im.drawHeight = 0.50*inch
            im.drawWidth = 2.5*inch
            elements.append(im)
            elements.append(Spacer(1, 12))  # Add space after logo

        # Define styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=20,
            textColor=colors.HexColor('#1E40AF'),
            spaceAfter=10,
            alignment=1
        )
        subtitle_style = ParagraphStyle(
            'Subtitle',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#1E40AF'),
            spaceAfter=20,
            alignment=1
        )

        # Add title
        elements.append(Paragraph('Rework Analysis & Re-verification Sheet', title_style))
        elements.append(Paragraph('QSF-22-02, Rev.03, Dated:29.12.2023', subtitle_style))
        
        # Add timestamp
        timestamp_style = ParagraphStyle(
            'Timestamp',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.grey,
            alignment=2
        )
        elements.append(Paragraph(
            f'Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
            timestamp_style
        ))
        elements.append(Spacer(1, 20))

        # For PDF, we'll use simplified headers to fit the landscape page
        simplified_headers = [
            'Sr.No', 'Date', 'Part ID', 'Stage', 'Defect', 'Location', 
            'Analysis Date', 'Reason', 'Rework Details', 'Status', 'Verified By'
        ]
        
        # Prepare data for table
        data = [simplified_headers]
        
        # Add data rows
        for record in queryset:
            data.append([
                record.sr_no,
                record.problem_found_date.strftime('%Y-%m-%d'),
                record.part_identification_no,
                record.problem_found_stage,
                record.defects_details,
                record.defect_location_on_pcb,
                record.analysis_date.strftime('%Y-%m-%d'),
                record.reason_for_defect,
                record.rework_details,
                f"{record.part_status} ({record.part_re_verification})",
                record.verified_by
            ])

        # Table style
        table_style = TableStyle([
            # Header styling
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E40AF')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            
            # Data rows
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ])

        # Add conditional coloring for pass/fail status
        for row_idx in range(1, len(data)):
            if "Pass" in data[row_idx][9]:
                table_style.add('BACKGROUND', (9, row_idx), (9, row_idx), colors.HexColor('#DCF5DC'))
            elif "Fail" in data[row_idx][9]:
                table_style.add('BACKGROUND', (9, row_idx), (9, row_idx), colors.HexColor('#FFE6E6'))

        # Define column widths (proportional to content)
        col_widths = [
            0.4*inch,  # Sr.No
            0.8*inch,  # Date
            1.0*inch,  # Part ID
            0.9*inch,  # Stage
            1.5*inch,  # Defect
            1.0*inch,  # Location
            0.8*inch,  # Analysis Date
            1.5*inch,  # Reason
            1.5*inch,  # Rework Details
            0.8*inch,  # Status
            1.0*inch,  # Verified By
        ]
        
        table = Table(data, colWidths=col_widths, repeatRows=1)
        table.setStyle(table_style)
        elements.append(table)

        # Build the PDF document
        doc.build(elements)
        return response


@method_decorator(staff_member_required, name='dispatch')
class UpdateReworkAnalysisRecordView(UpdateView):
    model = ReworkAnalysisRecord
    form_class = ReworkAnalysisRecordForm
    template_name = 'rework/update_rework_record.html'
    success_url = reverse_lazy('list_rework_analysis_records')

    def form_valid(self, form):
        rework_record = form.save(commit=False)
        rework_record.request = self.request  # Pass request to access session in save method
        messages.success(self.request, "Rework analysis record updated successfully.")
        return super().form_valid(form)


@method_decorator(staff_member_required, name='dispatch')
class DeleteReworkAnalysisRecordView(DeleteView):
    model = ReworkAnalysisRecord
    template_name = 'rework/delete_rework_record.html'
    success_url = reverse_lazy('list_rework_analysis_records')

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Rework analysis record deleted successfully.")
        return super().delete(request, *args, **kwargs)


@method_decorator(staff_member_required, name='dispatch')
class ReworkAnalysisRecordDetailView(View):
    def get(self, request, pk):
        record = get_object_or_404(ReworkAnalysisRecord, pk=pk)
        return render(request, 'rework/rework_record_detail.html', {'record': record}) 
    
    
    
    # 
from django.views import View
from django.views.generic import ListView, UpdateView, DeleteView
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.db.models import Q
from datetime import datetime
from io import BytesIO
import xlsxwriter
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from django.contrib.staticfiles import finders

from .models import SolderPasteControl
from .forms import SolderPasteControlForm, SolderPasteControlSearchForm

@method_decorator(login_required, name='dispatch')
class AddSolderPasteControlView(View):
    def get(self, request):
        form = SolderPasteControlForm()
        return render(request, 'solder_paste/solder_paste_form.html', {
            'form': form,
        })
    
    def post(self, request):
        form = SolderPasteControlForm(request.POST)
        if form.is_valid():
            solder_paste_record = form.save(commit=False)
            # Store the request for use in the model's save method
            solder_paste_record.request = request
            solder_paste_record.save()
            messages.success(request, "Solder paste control record added successfully.")
            return redirect('add_solder_paste_control')
        else:
            messages.error(request, "There was an error adding the solder paste control record. Please check the form and try again.")
            # Debug: Print form errors
            print(form.errors)
        return render(request, 'solder_paste/solder_paste_form.html', {'form': form})

class ListSolderPasteControlView(ListView):
    model = SolderPasteControl
    template_name = 'solder_paste/list_solder_paste_records.html'
    context_object_name = 'records'
    
    def get(self, request, *args, **kwargs):
        # Handle export requests separately
        export_format = request.GET.get('export')
        if export_format:
            queryset = self.get_filtered_queryset()
            return self.export_data(queryset, export_format)
        
        # Regular page display
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = SolderPasteControlSearchForm(self.request.GET)
        return context

    def get_filtered_queryset(self):
        queryset = self.model.objects.all()
        form = SolderPasteControlSearchForm(self.request.GET)
        
        if form.is_valid():
            if start_date := form.cleaned_data.get('start_date'):
                queryset = queryset.filter(psr_date__gte=start_date)
            if end_date := form.cleaned_data.get('end_date'):
                queryset = queryset.filter(psr_date__lte=end_date)
            if serial_number := form.cleaned_data.get('serial_number'):
                queryset = queryset.filter(serial_number__icontains=serial_number)
            if lot_number := form.cleaned_data.get('lot_number'):
                queryset = queryset.filter(lot_number__icontains=lot_number)
            if expiry_status := form.cleaned_data.get('expiry_status'):
                queryset = queryset.filter(expiry_status=expiry_status)
        
        return queryset

    def get_queryset(self):
        return self.get_filtered_queryset()
    
    def get_logo_path(self):
        """Get the absolute path to the logo file from static files"""
        return finders.find('images/image.png')

    def export_data(self, queryset, format):
        if format == 'excel':
            return self.export_excel(queryset)
        elif format == 'pdf':
            return self.export_pdf(queryset)

    def export_excel(self, queryset):
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet('Solder Paste Controls')
        
        # Insert logo
        logo_path = self.get_logo_path()
        if logo_path:
            worksheet.insert_image('A1', logo_path, {
                'x_scale': 0.5,
                'y_scale': 0.5,
                'x_offset': 10,
                'y_offset': 10
            })
            
        # Define formats
        header_format = workbook.add_format({
            'bold': True,
            'font_size': 12,
            'font_name': 'Arial',
            'bg_color': '#1E40AF',  # primaryColor
            'font_color': 'white',
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'text_wrap': True
        })

        cell_format = workbook.add_format({
            'font_size': 11,
            'font_name': 'Arial',
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'text_wrap': True
        })

        date_format = workbook.add_format({
            'font_size': 11,
            'font_name': 'Arial',
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'num_format': 'yyyy-mm-dd'
        })

        time_format = workbook.add_format({
            'font_size': 11,
            'font_name': 'Arial',
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'num_format': 'hh:mm'
        })

        status_ok_format = workbook.add_format({
            'font_size': 11,
            'font_name': 'Arial',
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#DCF5DC'  # Light green background
        })

        status_ng_format = workbook.add_format({
            'font_size': 11,
            'font_name': 'Arial',
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#FFE6E6'  # Light red background
        })

        # Set title & document info
        title_format = workbook.add_format({
            'bold': True,
            'font_size': 16,
            'font_name': 'Arial',
            'align': 'center',
            'valign': 'vcenter',
            'font_color': '#1E40AF'  # primaryColor
        })
        worksheet.merge_range('A1:W1', 'SMT Line - Solder Paste Control', title_format)
        worksheet.merge_range('A2:W2', f'Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', workbook.add_format({
            'italic': True,
            'font_size': 10,
            'align': 'right'
        }))

        # Product specifications (above the data table)
        spec_format = workbook.add_format({
            'font_size': 11,
            'font_name': 'Arial',
            'align': 'left',
            'valign': 'vcenter',
            'bold': True
        })
        worksheet.write('A4', 'Type:', spec_format)
        worksheet.write('B4', 'Lead Free Solder Paste', cell_format)
        worksheet.write('A5', 'Make:', spec_format)
        worksheet.write('B5', 'Heraeus', cell_format)
        worksheet.write('A6', 'Part Number:', spec_format)
        worksheet.write('B6', 'F640SA30C5-89M30', cell_format)
        worksheet.write('C4', 'Alloy:', spec_format)
        worksheet.write('D4', 'Sn 96.5; Ag 3; Cu 0.5', cell_format)
        worksheet.write('C5', 'Type:', spec_format)
        worksheet.write('D5', 'Type 3 =25 -45 microns (325/=500mesh)', cell_format)
        worksheet.write('C6', 'Net Wt.:', spec_format)
        worksheet.write('D6', '500 Gms', cell_format)
        worksheet.write('E4', 'Code:', spec_format)
        worksheet.write('E5', 'G1', cell_format)

        # Headers (start from row 8)
        headers = [
            'S No\nG1-', 'PSR\nDate', 'PSR\nNo.', 'Make\nOK/NG', 'Part No\nOK/NG', 
            'Alloy\nOK/NG', 'Net Wt\nOK/NG', 'Lot No', 'Expiry\nDate', 'Deep Storage\nJar No.',
            'Thawing\nDate', 'Thawing\nTime', 'Expiry\nStatus', 'Thawing\nSign',
            'Mixing\nDate', 'Mixing\nTime', 'First Use\nDate', 'First Use\nTime', 'First Use\nSign',
            'Second Use\nDate', 'Second Use\nTime', 'Second Use\nSign', 'Remarks'
        ]
        for col, header in enumerate(headers):
            worksheet.write(8, col, header, header_format)
            
        # Set row height for header
        worksheet.set_row(8, 40)

        # Write data
        for row, record in enumerate(queryset, start=9):
            worksheet.write(row, 0, record.serial_number, cell_format)
            worksheet.write(row, 1, record.psr_date, date_format)
            worksheet.write(row, 2, record.psr_number, cell_format)
            
            # Status columns with conditional formatting
            for col, status in enumerate([
                record.make_status, record.part_number_status, 
                record.alloy_status, record.net_weight_status
            ], 3):
                format_to_use = status_ok_format if status == 'OK' else status_ng_format
                worksheet.write(row, col, status, format_to_use)
                
            worksheet.write(row, 7, record.lot_number, cell_format)
            worksheet.write(row, 8, record.expiry_date, date_format)
            worksheet.write(row, 9, record.deep_storage_jar_number, cell_format)
            
            # Thawing information
            if record.thawing_date:
                worksheet.write(row, 10, record.thawing_date, date_format)
            else:
                worksheet.write(row, 10, "-", cell_format)
                
            if record.thawing_time:
                worksheet.write(row, 11, record.thawing_time, time_format)
            else:
                worksheet.write(row, 11, "-", cell_format)
                
            expiry_format = status_ok_format if record.expiry_status == 'Valid' else status_ng_format
            worksheet.write(row, 12, record.expiry_status, expiry_format)
            worksheet.write(row, 13, record.thawing_sign or "-", cell_format)
            
            # Mixing information
            if record.mixing_date:
                worksheet.write(row, 14, record.mixing_date, date_format)
            else:
                worksheet.write(row, 14, "-", cell_format)
                
            if record.mixing_time:
                worksheet.write(row, 15, record.mixing_time, time_format)
            else:
                worksheet.write(row, 15, "-", cell_format)
            
            # First use information
            if record.first_use_date:
                worksheet.write(row, 16, record.first_use_date, date_format)
            else:
                worksheet.write(row, 16, "-", cell_format)
                
            if record.first_use_time:
                worksheet.write(row, 17, record.first_use_time, time_format)
            else:
                worksheet.write(row, 17, "-", cell_format)
                
            worksheet.write(row, 18, record.first_use_sign or "-", cell_format)
            
            # Second use information
            if record.second_use_date:
                worksheet.write(row, 19, record.second_use_date, date_format)
            else:
                worksheet.write(row, 19, "-", cell_format)
                
            if record.second_use_time:
                worksheet.write(row, 20, record.second_use_time, time_format)
            else:
                worksheet.write(row, 20, "-", cell_format)
                
            worksheet.write(row, 21, record.second_use_sign or "-", cell_format)
            
            # Remarks
            worksheet.write(row, 22, record.remarks or "", cell_format)

        # Auto fit column widths (excluding remarks which can be long)
        for col in range(22):
            worksheet.set_column(col, col, 15)
        
        # Remarks column can be wider
        worksheet.set_column(22, 22, 25)

        workbook.close()
        output.seek(0)

        response = HttpResponse(
            output.read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename=solder_paste_control_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        return response

    def export_pdf(self, queryset):
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename=solder_paste_control_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'

        # Create the PDF object using ReportLab
        doc = SimpleDocTemplate(
            response,
            pagesize=landscape(letter),
            rightMargin=30,
            leftMargin=30,
            topMargin=30,
            bottomMargin=30
        )

        # Container for PDF elements
        elements = []
        
        # Add logo
        logo_path = self.get_logo_path()
        if logo_path:
            im = Image(logo_path)
            # Set logo dimensions
            im.drawHeight = 0.50*inch
            im.drawWidth = 2.5*inch
            elements.append(im)
            elements.append(Spacer(1, 12))  # Add space after logo

        # Define styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=20,
            textColor=colors.HexColor('#1E40AF'),
            spaceAfter=10,
            alignment=1
        )
        subtitle_style = ParagraphStyle(
            'Subtitle',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#1E40AF'),
            spaceAfter=20,
            alignment=1
        )

        # Add title
        elements.append(Paragraph('SMT Line - Solder Paste Control', title_style))
        
        # Add specifications table
        spec_data = [
            ['Type:', 'Lead Free Solder Paste', 'Alloy:', 'Sn 96.5; Ag 3; Cu 0.5', 'Code:', 'G1'],
            ['Make:', 'Heraeus', 'Type:', 'Type 3 =25 -45 microns (325/=500mesh)', '', ''],
            ['Part Number:', 'F640SA30C5-89M30', 'Net Wt.:', '500 Gms', '', '']
        ]
        
        spec_table = Table(spec_data, colWidths=[1*inch, 1.5*inch, 1*inch, 2*inch, 0.7*inch, 0.8*inch])
        spec_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('FONTNAME', (4, 0), (4, -1), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        elements.append(spec_table)
        elements.append(Spacer(1, 15))
        
        # Add timestamp
        timestamp_style = ParagraphStyle(
            'Timestamp',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.grey,
            alignment=2
        )
        elements.append(Paragraph(
            f'Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
            timestamp_style
        ))
        elements.append(Spacer(1, 15))

        # For PDF, we'll use simplified headers to fit the landscape page
        simplified_headers = [
            'S.No', 'PSR\nDate', 'Lot No', 'Expiry\nDate', 'Jar No.', 
            'Thawing\nDate', 'Mixing\nDate', 'First Use\nDate', 'Second Use\nDate', 'Status'
        ]
        
        # Prepare data for table
        data = [simplified_headers]
        
        # Add data rows
        for record in queryset:
            status_checks = []
            if record.make_status == 'NG' or record.part_number_status == 'NG' or record.alloy_status == 'NG' or record.net_weight_status == 'NG':
                status_checks.append('Check Failed')
            if record.expiry_status == 'Expired':
                status_checks.append('Expired')
                
            status = ', '.join(status_checks) if status_checks else 'All OK'
            
            data.append([
                record.serial_number,
                record.psr_date.strftime('%Y-%m-%d'),
                record.lot_number,
                record.expiry_date.strftime('%Y-%m-%d'),
                record.deep_storage_jar_number,
                record.thawing_date.strftime('%Y-%m-%d') if record.thawing_date else '-',
                record.mixing_date.strftime('%Y-%m-%d') if record.mixing_date else '-',
                record.first_use_date.strftime('%Y-%m-%d') if record.first_use_date else '-',
                record.second_use_date.strftime('%Y-%m-%d') if record.second_use_date else '-',
                status
            ])

        # Table style
        table_style = TableStyle([
            # Header styling
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E40AF')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            
            # Data rows
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ])

        # Add conditional coloring for status
        for row_idx in range(1, len(data)):
            status = data[row_idx][-1]
            if 'Check Failed' in status or 'Expired' in status:
                table_style.add('BACKGROUND', (-1, row_idx), (-1, row_idx), colors.HexColor('#FFE6E6'))
            else:
                table_style.add('BACKGROUND', (-1, row_idx), (-1, row_idx), colors.HexColor('#DCF5DC'))

        # Define even column widths that fit the page
        col_widths = [0.9*inch] * len(simplified_headers)
        
        table = Table(data, colWidths=col_widths, repeatRows=1)
        table.setStyle(table_style)
        elements.append(table)

        # Build the PDF document
        doc.build(elements)
        return response


@method_decorator(staff_member_required, name='dispatch')
class UpdateSolderPasteControlView(UpdateView):
    model = SolderPasteControl
    form_class = SolderPasteControlForm
    template_name = 'solder_paste/update_solder_paste_record.html'
    success_url = reverse_lazy('list_solder_paste_controls')

    def form_valid(self, form):
        solder_paste_record = form.save(commit=False)
        solder_paste_record.request = self.request  # Pass request to access session in save method
        messages.success(self.request, "Solder paste control record updated successfully.")
        return super().form_valid(form)


@method_decorator(staff_member_required, name='dispatch')
class DeleteSolderPasteControlView(DeleteView):
    model = SolderPasteControl
    template_name = 'solder_paste/delete_solder_paste_record.html'
    success_url = reverse_lazy('list_solder_paste_controls')

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Solder paste control record deleted successfully.")
        return super().delete(request, *args, **kwargs)


@method_decorator(staff_member_required, name='dispatch')
class SolderPasteControlDetailView(View):
    def get(self, request, pk):
        record = get_object_or_404(SolderPasteControl, pk=pk)
        return render(request, 'solder_paste/solder_paste_record_detail.html', {'record': record})    
    
    
    
    
# 



from .models import TipVoltageResistanceRecord, QSF, ProcessMachineMapping
from .forms import TipVoltageResistanceRecordForm, TipVoltageResistanceRecordSearchForm


@method_decorator(login_required, name='dispatch')
class AddTipVoltageResistanceRecordView(View):
    def get(self, request):
        form = TipVoltageResistanceRecordForm()
        qsf_documents = QSF.objects.all()
        process_machines = ProcessMachineMapping.objects.all()
        
        return render(request, 'tip_records/add_tip_voltage_resistance_record.html', {
            'form': form,
            'qsf_documents': qsf_documents,
            'process_machines': process_machines
        })

    def post(self, request):
        form = TipVoltageResistanceRecordForm(request.POST)
        if form.is_valid():
            record = form.save(commit=False)
            record.operator = request.user
            record.request = request  # Pass request to model for machine identification
            record.save()
            messages.success(request, "Tip voltage and resistance record added successfully.")
            return redirect('add_tip_voltage_resistance_record')
        else:
            messages.error(request, "There was an error adding the record. Please check the form and try again.")
        
        return render(request, 'tip_records/add_tip_voltage_resistance_record.html', {'form': form})


class ListTipVoltageResistanceRecordView(ListView):
    model = TipVoltageResistanceRecord
    template_name = 'tip_records/list_tip_voltage_resistance_records.html'
    context_object_name = 'records'
    ordering = ['-date', 'frequency']
    
    def get(self, request, *args, **kwargs):
        # Handle export requests separately
        export_format = request.GET.get('export')
        if export_format:
            queryset = self.get_filtered_queryset()
            return self.export_data(queryset, export_format)
        
        # Regular page display
        return super().get(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = TipVoltageResistanceRecordSearchForm(self.request.GET)
        return context

    def get_filtered_queryset(self):
        queryset = self.model.objects.all().order_by(*self.ordering)
        form = TipVoltageResistanceRecordSearchForm(self.request.GET)
        
        if form.is_valid():
            if start_date := form.cleaned_data.get('start_date'):
                queryset = queryset.filter(date__gte=start_date)
            if end_date := form.cleaned_data.get('end_date'):
                queryset = queryset.filter(date__lte=end_date)
            if frequency := form.cleaned_data.get('frequency'):
                queryset = queryset.filter(frequency=frequency)
            if shift := form.cleaned_data.get('shift'):
                queryset = queryset.filter(shift=shift)
            if status := form.cleaned_data.get('status'):
                if status == 'ok':
                    queryset = queryset.filter(tip_voltage__lt=1.0, tip_resistance__lt=10.0)
                elif status == 'not_ok':
                    queryset = queryset.filter(Q(tip_voltage__gte=1.0) | Q(tip_resistance__gte=10.0))
            if control_no := form.cleaned_data.get('soldering_station_control_no'):
                queryset = queryset.filter(soldering_station_control_no__icontains=control_no)
        
        return queryset

    def get_queryset(self):
        return self.get_filtered_queryset()

    def export_data(self, queryset, format):
        if format == 'excel':
            return self.export_excel(queryset)
        elif format == 'pdf':
            return self.export_pdf(queryset)

    def get_logo_path(self):
        """Get the absolute path to the logo file from static files"""
        return finders.find('images/image.png')

    def export_excel(self, queryset):
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet('Tip Voltage & Resistance Records')
        
        # Insert logo
        logo_path = self.get_logo_path()
        if logo_path:
            worksheet.insert_image('A1', logo_path, {
                'x_scale': 0.5,
                'y_scale': 0.5,
                'x_offset': 10,
                'y_offset': 10
            })
        
        # Define formats
        header_format = workbook.add_format({
            'bold': True,
            'font_size': 12,
            'font_name': 'Arial',
            'bg_color': '#1E40AF',  # primaryColor
            'font_color': 'white',
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'text_wrap': True
        })

        cell_format = workbook.add_format({
            'font_size': 11,
            'font_name': 'Arial',
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'text_wrap': True
        })

        date_format = workbook.add_format({
            'font_size': 11,
            'font_name': 'Arial',
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'num_format': 'yyyy-mm-dd'
        })

        value_format_ok = workbook.add_format({
            'font_size': 11,
            'font_name': 'Arial',
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#DCF5DC'  # Light green background
        })

        value_format_not_ok = workbook.add_format({
            'font_size': 11,
            'font_name': 'Arial',
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#FFE6E6'  # Light red background
        })

        # Set column widths
        worksheet.set_column('A:A', 15)  # Control No
        worksheet.set_column('B:B', 12)  # Date
        worksheet.set_column('C:C', 8)   # Frequency
        worksheet.set_column('D:D', 8)   # Shift
        worksheet.set_column('E:E', 12)  # Tip Voltage
        worksheet.set_column('F:F', 12)  # Tip Resistance
        worksheet.set_column('G:G', 20)  # Operator
        worksheet.set_column('H:H', 10)  # Op. Signature
        worksheet.set_column('I:I', 10)  # Sup. Signature

        # Write title
        title_format = workbook.add_format({
            'bold': True,
            'font_size': 16,
            'font_name': 'Arial',
            'align': 'center',
            'valign': 'vcenter',
            'font_color': '#1E40AF'  # primaryColor
        })
        
        worksheet.merge_range('A1:I1', 'Tip Voltage & Resistance Records Report', title_format)
        worksheet.set_row(0, 30)  # Set title row height

        # Write timestamp
        timestamp_format = workbook.add_format({
            'italic': True,
            'font_size': 10,
            'align': 'right'
        })
        
        worksheet.merge_range('A2:I2', f'Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', timestamp_format)

        # Headers (start from row 3)
        headers = ['Control No', 'Date', 'Frequency', 'Shift', 'Tip Voltage (<1V)', 
                  'Tip Resistance (<10Ω)', 'Operator', 'Op. Sign', 'Sup. Sign']
        
        for col, header in enumerate(headers):
            worksheet.write(3, col, header, header_format)

        # Write data
        for row, record in enumerate(queryset, start=4):
            worksheet.write(row, 0, record.soldering_station_control_no, cell_format)
            worksheet.write(row, 1, record.date, date_format)
            worksheet.write(row, 2, record.frequency, cell_format)
            worksheet.write(row, 3, record.shift, cell_format)
            
            # Tip voltage with conditional formatting
            tip_v_format = value_format_ok if record.tip_voltage < 1.0 else value_format_not_ok
            worksheet.write(row, 4, record.tip_voltage, tip_v_format)
            
            # Tip resistance with conditional formatting
            tip_r_format = value_format_ok if record.tip_resistance < 10.0 else value_format_not_ok
            worksheet.write(row, 5, record.tip_resistance, tip_r_format)
            
            worksheet.write(row, 6, record.operator.username if record.operator else '-', cell_format)
            worksheet.write(row, 7, record.operator_signature, cell_format)
            worksheet.write(row, 8, record.supervisor_signature, cell_format)

        workbook.close()
        output.seek(0)

        response = HttpResponse(
            output.read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename=tip_voltage_resistance_records_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        return response

    def export_pdf(self, queryset):
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename=tip_voltage_resistance_records_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'

        # Create the PDF object using ReportLab
        doc = SimpleDocTemplate(
            response,
            pagesize=landscape(letter),
            rightMargin=30,
            leftMargin=30,
            topMargin=30,
            bottomMargin=30
        )

        # Container for PDF elements
        elements = []
        
        # Add logo
        logo_path = self.get_logo_path()
        if logo_path:
            im = Image(logo_path)
            # Set logo dimensions
            im.drawHeight = 0.50*inch
            im.drawWidth = 2.5*inch
            elements.append(im)
            elements.append(Spacer(1, 12))  # Add space after logo

        # Define styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1E40AF'),
            spaceAfter=30,
            alignment=1
        )

        # Add title
        elements.append(Paragraph('Tip Voltage & Resistance Records Report', title_style))
        
        # Add timestamp
        timestamp_style = ParagraphStyle(
            'Timestamp',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.grey,
            alignment=2
        )
        
        elements.append(Paragraph(
            f'Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
            timestamp_style
        ))
        
        elements.append(Spacer(1, 20))

        # Prepare data for table
        data = [['Control No', 'Date', 'Frequency', 'Shift', 'Tip Voltage (<1V)', 
                'Tip Resistance (<10Ω)', 'Operator', 'Op. Sign', 'Sup. Sign']]
        
        # Add data rows
        for record in queryset:
            data.append([
                record.soldering_station_control_no,
                record.date.strftime('%Y-%m-%d'),
                record.frequency,
                record.shift,
                f"{record.tip_voltage:.2f}V",
                f"{record.tip_resistance:.2f}Ω",
                record.operator.username if record.operator else '-',
                record.operator_signature,
                record.supervisor_signature
            ])

        # Table styling
        table_style = TableStyle([
            # Header styling
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E40AF')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            
            # Data rows
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWHEIGHTS', (0, 0), (-1, -1), 30),
        ])

        # Add conditional background colors for tip voltage and resistance
        for row_idx in range(1, len(data)):
            # Parse values from formatted strings
            voltage = float(data[row_idx][4].replace('V', ''))
            resistance = float(data[row_idx][5].replace('Ω', ''))
            
            # Apply conditional formatting
            if voltage < 1.0:
                table_style.add('BACKGROUND', (4, row_idx), (4, row_idx), colors.HexColor('#DCF5DC'))
            else:
                table_style.add('BACKGROUND', (4, row_idx), (4, row_idx), colors.HexColor('#FFE6E6'))
                
            if resistance < 10.0:
                table_style.add('BACKGROUND', (5, row_idx), (5, row_idx), colors.HexColor('#DCF5DC'))
            else:
                table_style.add('BACKGROUND', (5, row_idx), (5, row_idx), colors.HexColor('#FFE6E6'))

        # Create table with calculated column widths
        col_widths = [
            1.2*inch,  # Control No
            1.0*inch,  # Date
            0.8*inch,  # Frequency
            0.7*inch,  # Shift
            1.1*inch,  # Tip Voltage
            1.1*inch,  # Tip Resistance
            1.5*inch,  # Operator
            0.8*inch,  # Op. Sign
            0.8*inch   # Sup. Sign
        ]
        
        table = Table(data, colWidths=col_widths, repeatRows=1)
        table.setStyle(table_style)
        elements.append(table)

        # Build the PDF document
        doc.build(elements)
        return response


@method_decorator(staff_member_required, name='dispatch')
class UpdateTipVoltageResistanceRecordView(UpdateView):
    model = TipVoltageResistanceRecord
    form_class = TipVoltageResistanceRecordForm
    template_name = 'tip_records/update_tip_voltage_resistance_record.html'
    success_url = reverse_lazy('list_tip_voltage_resistance_records')


@method_decorator(staff_member_required, name='dispatch')
class DeleteTipVoltageResistanceRecordView(DeleteView):
    model = TipVoltageResistanceRecord
    template_name = 'tip_records/delete_tip_voltage_resistance_record.html'
    success_url = reverse_lazy('list_tip_voltage_resistance_records')


@method_decorator(staff_member_required, name='dispatch')
class TipVoltageResistanceRecordDetailView(View):
    def get(self, request, pk):
        record = get_object_or_404(TipVoltageResistanceRecord, pk=pk)
        return render(request, 'tip_records/tip_voltage_resistance_record_detail.html', {'record': record})
