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
        return render(request, 'fixture_records/add_fixture_cleaning_record.html', {'form': form})

    def post(self, request):
        form = FixtureCleaningRecordForm(request.POST)
        if form.is_valid():
            fixture_record = form.save(commit=False)
            fixture_record.operator_name = request.user
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

@method_decorator(login_required, name='dispatch')
class AddRejectionSheetView(View):
    def get(self, request):
        form = RejectionSheetForm()
        return render(request, 'Rejection_records/add_rejection_sheet.html', {'form': form})

    def post(self, request):
        form = RejectionSheetForm(request.POST)
        if form.is_valid():
            rejection_sheet = form.save(commit=False)
            rejection_sheet.operator_name = request.user
            rejection_sheet.save()
            messages.success(request, "Rejection sheet added successfully.")
            return redirect('add_rejection_sheet')
        else:
            messages.error(request, "There was an error adding the rejection sheet. Please check the form and try again.")
        return render(request, 'Rejection_records/add_rejection_sheet.html', {'form': form})
    
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
                sheet.get_stage_display(),
                sheet.get_part_description_display(),
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
                sheet.get_stage_display(),
                sheet.get_part_description_display(),
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
from .models import SolderingBitRecord
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
        return render(request, 'Maintenance/Daily/add_daily.html', {'form': form})

    def post(self, request):
        form = DailyChecklistItemForm(request.POST)

        try:
            profile = Profile.objects.get(user=request.user)
            user_skill_level = profile.my_skill
        except Profile.DoesNotExist:
            user_skill_level = 0

        if form.is_valid():
            daily_checklist_item = form.save(commit=False)

            if daily_checklist_item.machine_location.min_skill_required > user_skill_level:
                form.add_error('machine_location', 'Your skill level is insufficient for the selected option.')
                messages.error(request, 'Your skill level is insufficient for the selected option.')
            else:
                try:
                    daily_checklist_item.manager = request.user
                    daily_checklist_item.save()
                    messages.success(request, 'Daily checklist item added successfully.')
                    return redirect('add_daily')
                except Exception as e:
                    messages.error(request, f'Error saving checklist item: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')

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

        # Set column widths
        column_widths = {
            'A:A': 15,  # Doc No
            'B:B': 20,  # Machine Name
            'C:C': 25,  # Machine Location
            'D:D': 15,  # Date
            'E:K': 20,  # Check Points
            'L:R': 15,  # Remarks
            'S:T': 15,  # Signatures
        }
        
        for cols, width in column_widths.items():
            worksheet.set_column(cols, width)

        # Write headers
        headers = [
            'Doc No', 'Machine Name', 'Location', 'Date',
            'Check Point 1', 'Check Point 2', 'Check Point 3', 'Check Point 4',
            'Check Point 5', 'Check Point 6', 'Check Point 7',
            'Remark 1', 'Remark 2', 'Remark 3', 'Remark 4', 'Remark 5',
            'Remark 6', 'Remark 7',
            'Operator', 'Supervisor'
        ]
        
        for col, header in enumerate(headers):
            worksheet.write(0, col, header, header_format)

        # Write data
        for row, record in enumerate(queryset, start=1):
            data = [
                record.doc_number,
                record.get_machine_name_display(),
                record.machine_location.location_name,
                record.date.strftime('%Y-%m-%d'),
                record.check_point_1,
                record.check_point_2,
                record.check_point_3,
                record.check_point_4,
                record.check_point_5,
                record.check_point_6,
                record.check_point_7,
                record.Remark_1,
                record.Remark_2,
                record.Remark_3,
                record.Remark_4,
                record.Remark_5,
                record.Remark_6,
                record.Remark_7,
                record.checked_by_Operator,
                record.approved_by_Supervisor
            ]
            
            for col, value in enumerate(data):
                worksheet.write(row, col, value, cell_format)

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
        elements.append(Paragraph('Daily Checklist Report', title_style))
        
        # Add timestamp
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
        elements.append(Spacer(1, 20))

        # Table data
        headers = [
            'Doc No', 'Machine Name', 'Location', 'Date',
            'Check Points', 'Requirements', 'Status'
        ]
        data = [headers]

        for record in queryset:
            for i in range(1, 8):
                check_point = getattr(record, f'check_point_{i}')
                requirement = getattr(record, f'requirement_range_{i}')
                remark = getattr(record, f'Remark_{i}')
                
                if i == 1:  # First row includes basic info
                    data.append([
                        record.doc_number,
                        record.get_machine_name_display(),
                        record.machine_location.location_name,
                        record.date.strftime('%Y-%m-%d'),
                        check_point,
                        requirement,
                        remark
                    ])
                else:  # Subsequent rows only show check point data
                    data.append(['', '', '', '', check_point, requirement, remark])

        # Table style
        table_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E40AF')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BOX', (0, 0), (-1, -1), 2, colors.black),
            ('ROWHEIGHTS', (0, 0), (-1, -1), 30),
        ])

        table = Table(data)
        table.setStyle(table_style)
        elements.append(table)

        doc.build(elements)
        return response

    def export_data(self, queryset, format):
        if format == 'excel':
            return self.export_excel(queryset)
        elif format == 'pdf':
            return self.export_pdf(queryset)

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
        
        try:
            profile = Profile.objects.get(user=request.user)
            user_skill_level = profile.my_skill
        except Profile.DoesNotExist:
            user_skill_level = 0

        if form.is_valid():
            weekly_checklist_item = form.save(commit=False)

            if weekly_checklist_item.machine_location.min_skill_required > user_skill_level:
                form.add_error('machine_location', 'Your skill level is insufficient for the selected Machine Location.')
                messages.error(request, 'Your skill level is insufficient for the selected Machine Location.')
            else:
                try:
                    weekly_checklist_item.manager = request.user
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
        worksheet = workbook.add_worksheet('Weekly Checklist')
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

        # Set column widths
        worksheet.set_column('A:A', 15)  # Doc No
        worksheet.set_column('B:B', 20)  # Machine Name
        worksheet.set_column('C:C', 25)  # Location
        worksheet.set_column('D:G', 30)  # Check Points
        worksheet.set_column('H:K', 15)  # Remarks

        # Write title
        title_format = workbook.add_format({
            'bold': True,
            'font_size': 16,
            'align': 'center',
            'valign': 'vcenter',
            'font_color': '#1E40AF'
        })
        worksheet.merge_range('A1:K1', 'Weekly Checklist Report', title_format)
        worksheet.merge_range('A2:K2', 
                            f'Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
                            workbook.add_format({'align': 'right', 'italic': True}))

        # Headers
        headers = [
            'Doc No', 'Machine Name', 'Location',
            'Check Point 8', 'Check Point 9', 'Check Point 10', 'Check Point 11',
            'Remark 8', 'Remark 9', 'Remark 10', 'Remark 11'
        ]
        
        for col, header in enumerate(headers):
            worksheet.write(3, col, header, header_format)

        # Write data
        for row, record in enumerate(queryset, start=4):
            data = [
                record.doc_number,
                record.get_machine_name_display(),
                record.machine_location.location_name,
                record.check_point_8,
                record.check_point_9,
                record.check_point_10,
                record.check_point_11,
                record.Remark_8,
                record.Remark_9,
                record.Remark_10,
                record.Remark_11
            ]
            
            for col, value in enumerate(data):
                worksheet.write(row, col, value, cell_format)

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
        elements.append(Paragraph('Weekly Checklist Report', title_style))
        
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
        elements.append(Spacer(1, 20))

        # Table data
        data = [['Doc No', 'Machine Name', 'Location', 'Check Point', 'Requirement', 'Method', 'Status']]
        
        for record in queryset:
            for i in range(8, 12):
                check_point = getattr(record, f'check_point_{i}')
                requirement = getattr(record, f'requirement_range_{i}')
                method = getattr(record, f'method_of_checking_{i}')
                remark = getattr(record, f'Remark_{i}')
                
                if i == 8:  # First row includes machine info
                    data.append([
                        record.doc_number,
                        record.get_machine_name_display(),
                        record.machine_location.location_name,
                        check_point,
                        requirement,
                        method,
                        remark
                    ])
                else:  # Subsequent rows only show check point info
                    data.append(['', '', '', check_point, requirement, method, remark])

        # Table style
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E40AF')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWHEIGHTS', (0, 0), (-1, -1), 30),
        ]))

        elements.append(table)
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
        return render(request, 'Maintenance/monthly/add_monthly.html', {'form': form})

    def post(self, request):
        form = MonthlyChecklistItemForm(request.POST)
        
        try:
            profile = Profile.objects.get(user=request.user)
            user_skill_level = profile.my_skill
        except Profile.DoesNotExist:
            user_skill_level = 0

        if form.is_valid():
            monthly_checklist_item = form.save(commit=False)
            
            if monthly_checklist_item.machine_location.min_skill_required > user_skill_level:
                form.add_error(None, 'Your skill level is insufficient for the selected Machine Location.')
                messages.error(request, 'Your skill level is insufficient for the selected Machine Location.')
            else:
                monthly_checklist_item.manager = request.user
                try:
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
        worksheet = workbook.add_worksheet('Monthly Checklist')
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

        # Set column widths
        worksheet.set_column('A:A', 15)  # Doc No
        worksheet.set_column('B:B', 20)  # Machine Name
        worksheet.set_column('C:C', 25)  # Location
        worksheet.set_column('D:D', 30)  # Check Point
        worksheet.set_column('E:E', 20)  # Requirement
        worksheet.set_column('F:F', 20)  # Method
        worksheet.set_column('G:G', 15)  # Status

        # Write title
        title_format = workbook.add_format({
            'bold': True,
            'font_size': 16,
            'align': 'center',
            'valign': 'vcenter',
            'font_color': '#1E40AF'
        })
        worksheet.merge_range('A1:G1', 'Monthly Checklist Report', title_format)
        worksheet.merge_range('A2:G2', 
                            f'Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
                            workbook.add_format({'align': 'right', 'italic': True}))

        # Write headers
        headers = [
            'Doc No', 'Machine Name', 'Location', 'Check Point', 
            'Requirement', 'Method', 'Status'
        ]
        
        for col, header in enumerate(headers):
            worksheet.write(3, col, header, header_format)

        # Write data
        for row, record in enumerate(queryset, start=4):
            data = [
                record.doc_number,
                record.get_machine_name_display(),
                record.machine_location.location_name,
                record.check_point_12,
                record.requirement_range_12,
                record.method_of_checking_12,
                record.Remark_12
            ]
            
            for col, value in enumerate(data):
                worksheet.write(row, col, value, cell_format)

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
         # Add logo
        logo_path = self.get_logo_path()
        if logo_path:
            im = Image(logo_path)
            # Set logo dimensions
            im.drawHeight = 0.50*inch
            im.drawWidth = 2.5*inch
            elements.append(im)
            elements.append(Spacer(1, 12))  # Add space after logo
        doc = SimpleDocTemplate(
            response,
            pagesize=landscape(letter),
            rightMargin=30,
            leftMargin=30,
            topMargin=30,
            bottomMargin=30
        )

        elements = []

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
        elements.append(Paragraph('Monthly Checklist Report', title_style))
        elements.append(Paragraph(
            f'Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
            ParagraphStyle('Timestamp', parent=styles['Normal'], fontSize=10, textColor=colors.grey, alignment=2)
        ))
        elements.append(Spacer(1, 20))

        # Table data
        data = [['Doc No', 'Machine Name', 'Location', 'Check Point', 
                'Requirement', 'Method', 'Status']]

        for record in queryset:
            data.append([
                record.doc_number,
                record.get_machine_name_display(),
                record.machine_location.location_name,
                record.check_point_12,
                record.requirement_range_12,
                record.method_of_checking_12,
                record.Remark_12
            ])

        # Table style
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E40AF')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWHEIGHTS', (0, 0), (-1, -1), 30),
        ]))

        elements.append(table)
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
    ordering = ['-date']

    def get(self, request, *args, **kwargs):
        if request.GET.get('export') == 'excel':
            queryset = self.get_queryset()  # This gets the filtered queryset
            return self.export_excel(queryset)
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()
        selected_month = self.request.GET.get('month')

        if selected_month:
            try:
                year, month = map(int, selected_month.split('-'))
                queryset = queryset.filter(
                    date__year=year,
                    date__month=month
                )
            except (ValueError, TypeError):
                pass

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

        # Set column widths
        worksheet.set_column('A:A', 15)  # Date
        worksheet.set_column('B:F', 12)  # Readings
        worksheet.set_column('G:H', 15)  # Statistics

        # Write title
        title_text = 'Control Chart Readings Report'
        selected_month = self.request.GET.get('month')
        if selected_month:
            try:
                year, month = map(int, selected_month.split('-'))
                month_date = timezone.datetime(year, month, 1)
                title_text += f" - {month_date.strftime('%B %Y')}"
            except (ValueError, TypeError):
                pass

        worksheet.merge_range('A1:H1', title_text, 
                            workbook.add_format({
                                'bold': True,
                                'font_size': 16,
                                'align': 'center',
                                'valign': 'vcenter'
                            }))

        # Add generation timestamp
        worksheet.merge_range('A2:H2', 
                            f'Generated: {timezone.now().strftime("%Y-%m-%d %H:%M:%S")}',
                            workbook.add_format({
                                'align': 'right', 
                                'italic': True
                            }))

        # Write headers
        headers = ['Date', 'Reading 1', 'Reading 2', 'Reading 3', 'Reading 4', 'Reading 5', 'X-Bar', 'Range']
        for col, header in enumerate(headers):
            worksheet.write(3, col, header, header_format)

        # Write data
        for row, reading in enumerate(queryset, start=4):
            readings = [reading.reading1, reading.reading2, reading.reading3, 
                       reading.reading4, reading.reading5]
            x_bar = sum(readings) / len(readings)
            range_val = max(readings) - min(readings)

            worksheet.write(row, 0, reading.date.strftime('%Y-%m-%d'), cell_format)
            for col, value in enumerate(readings, start=1):
                worksheet.write(row, col, value, cell_format)
            worksheet.write(row, 6, x_bar, cell_format)
            worksheet.write(row, 7, range_val, cell_format)

        workbook.close()
        output.seek(0)

        # Generate filename based on month if filtered
        filename = 'control_chart_readings'
        if selected_month:
            try:
                year, month = map(int, selected_month.split('-'))
                month_date = timezone.datetime(year, month, 1)
                filename += f"_{month_date.strftime('%Y_%m')}"
            except (ValueError, TypeError):
                pass
        
        filename += f"_{timezone.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

        response = HttpResponse(
            output.read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search_form = ReadingSearchForm(self.request.GET)
        selected_month = self.request.GET.get('month')
        
        if selected_month:
            try:
                year, month = map(int, selected_month.split('-'))
                month_date = timezone.datetime(year, month, 1)
                context['selected_month_display'] = month_date.strftime('%B %Y')
            except (ValueError, TypeError):
                context['selected_month_display'] = 'All Months'
        else:
            context['selected_month_display'] = 'All Months'

        context['search_form'] = search_form
        return context
            
class ReadingDetailView(DetailView):
    model = ControlChartReading
    context_object_name = 'reading'
    template_name = 'reading_detail.html'

class ReadingCreateView(CreateView):
    model = ControlChartReading
    form_class = ControlChartReadingForm
    template_name = 'reading_form.html'
    success_url = reverse_lazy('reading_create')

    def form_valid(self, form):
        try:
            response = super().form_valid(form)
            messages.success(self.request, 'Reading has been successfully added.')
            return response
        except Exception as e:
            messages.error(self.request, f'Error saving reading: {str(e)}')
            return self.form_invalid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add New Reading'
        return context

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

# views.py
# views.py
from django.shortcuts import render
from django.db.models.functions import TruncMonth, TruncDate
from django.db.models import Count, Min, Max, Avg, StdDev
from django.utils import timezone
import calendar

def control_chart(request):
    """
    View function for displaying the control chart dashboard with statistical analysis
    and special cause violations detection.
    """
    # Handle month selection with fallback to current month
    selected_month = request.GET.get('month', timezone.now().strftime('%Y-%m'))
    
    try:
        year, month = map(int, selected_month.split('-'))
    except ValueError:
        current_date = timezone.now()
        year, month = current_date.year, current_date.month

    # Calculate total days in selected month
    _, total_days = calendar.monthrange(year, month)

    # Retrieve monthly statistics
    monthly_stats = ControlChartStatistics.objects.filter(
        date__year=year,
        date__month=month
    ).order_by('date')

    # Calculate monthly summary statistics
    days_with_data = monthly_stats.count()
    completion_percentage = (days_with_data / total_days * 100) if total_days else 0

    # Get the latest specification limits
    latest_stats = monthly_stats.last()
    current_usl = latest_stats.usl if latest_stats else 375  # Default USL
    current_lsl = latest_stats.lsl if latest_stats else 355  # Default LSL

    # Get data points for special cause analysis
    data_points = list(monthly_stats.values('date', 'x_bar', 'r'))
    
    if data_points:
        x_bars = [point['x_bar'] for point in data_points]
        mean = round(sum(x_bars) / len(x_bars), 1)
        std_dev = round((
            sum((x - mean) ** 2 for x in x_bars) / len(x_bars)
        ) ** 0.5, 2)
        
        # Get violations and process them for display
        violations = ControlChartStatistics.check_special_causes(data_points, mean, std_dev)
        processed_violations = process_violations(violations)
    else:
        processed_violations = []

    # Prepare monthly summary if data exists
    monthly_summary = None
    if monthly_stats.exists():
        monthly_summary = {
            'month_name': calendar.month_name[month],
            'year': year,
            'days_with_data': days_with_data,
            'total_days': total_days,
            'completion_percentage': completion_percentage,
            'first_reading_date': monthly_stats.first().date,
            'last_reading_date': monthly_stats.last().date,
            'x_bar_avg': monthly_stats.aggregate(Avg('x_bar'))['x_bar__avg'],
            'r_avg': monthly_stats.aggregate(Avg('r'))['r__avg'],
            'current_usl': current_usl,
            'current_lsl': current_lsl,
            'x_bar_avg': round(monthly_stats.aggregate(Avg('x_bar'))['x_bar__avg'], 1),
            'r_avg': round(monthly_stats.aggregate(Avg('r'))['r__avg'], 1),

        }

    # Get available months for the dropdown
    available_months = ControlChartStatistics.objects.annotate(
        month=TruncMonth('date')
    ).values('month').annotate(
        days_count=Count('id')
    ).order_by('-month')

    # Calculate control limits and capability indices
    control_limits = ControlChartStatistics.calculate_control_limits()
    capability_indices = ControlChartStatistics.calculate_capability_indices()

    # Determine overall violation severity
    violation_severity = determine_violation_severity(processed_violations)

    print("Monthly Stats Count:", monthly_stats.count())
    print("Sample X-bar values:", [stat.x_bar for stat in monthly_stats[:5]])
    print("Control Limits:", control_limits)

    # Prepare context for template
    context = {
        'statistics': monthly_stats,
        'monthly_summary': monthly_summary,
        'available_months': available_months,
        'selected_month': selected_month,
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
    
    print("Context data sample:", {
        'stats_count': len(context['statistics']),
        'has_monthly_summary': bool(context['monthly_summary']),
        'control_limits': context['control_limits']
    })
    
    return render(request, 'control_chart.html', context)

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


from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def dashboard(request):
    return render(request, 'dashboard.html')



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
    template_name = 'startup/startup_checksheet_list.html'  # Create this template
    context_object_name = 'check_sheets'

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
      
            process_operation = form.cleaned_data['process_operation']
            if user_skill_level < process_operation.min_skill_required:
                form.add_error('process_operation', 'Your skill level is not sufficient for this operation.')
                messages.error(request, 'Your skill level is not sufficient for this operation.')
            else:
                try:
                    checksheet = form.save(commit=False)
                    checksheet.manager = request.user                
                # Handle the dynamic checkpoint fields
                    for i in range(1, 26):  # Assuming 25 checkpoints
                        checkpoint_key = f'checkpoint_{i}'
                        if checkpoint_key in request.POST:
                            setattr(checksheet, checkpoint_key, request.POST[checkpoint_key])
                    
                    checksheet.save()
                    messages.success(request, 'Check sheet created successfully.')
                    return redirect('checksheet_create')  # Make sure this URL name is correct
                except Exception as e:
                    messages.error(request, f'Error saving check sheet: {str(e)}')
        else:
                messages.error(request, 'Please correct the errors below.')
    else:
            form = StartUpCheckSheetForm()

    # Prepare checkpoint fields
    checkpoint_fields = [form[f'checkpoint_{i}'] for i in range(1, 26)]  # Assuming 25 checkpoints

    # Replace this with your actual data source
    json_data = [
    {
        "s_no": 1,
        "checkpoint": "Plan के अनसु ार Part assy & Child parts Working Table पर रखें| प्लान के अनसु ार | visual प्रतिदिन",
        "specification": "Part assy & Child parts",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
        "s_no": 2,
        "checkpoint": "अपनेकार्स्य थल को साफ करे| कार्स्य थल धलू रदिि िोना चादिए | visual प्रतिदिन",
        "specification": "साफ करे",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
        "s_no": 3,
        "checkpoint": "कार्यकरनेसेपिलेWorking table पर सेअनावश्र्क Part / material िटा िें, और उसेउसकी जगि पर रखें| अनावश्र्क Part / material Working Table पर ना िों | visual प्रतिदिन",
        "specification": "Working table पर सेअनावश्र्क Part / material िटा िें",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
        "s_no": 4,
        "checkpoint": "Dirty tray को लाइन पर use ना करेउसको उसकी तनधायररि जगि पर सफाई के ललए रख िे| Dirty Tray Area visual प्रतिदिन",
        "specification": "Dirty tray को लाइन पर use ना करेउसको उसकी तनधायररि जगि पर सफाई के ललए रख िे",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
        "s_no": 5,
        "checkpoint": "चके करेंकक Fixture / Machine Condition OK िों और उसके सभी Connections ठीक िों, Loose ना िों | Fixture / Machine Condition OK, No loose connections visual प्रतिदिन",
        "specification": "Fixture / Machine Condition OK",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
        "s_no": 6,
        "checkpoint": "चके करेंकक Fixture / Machine मेंलगेCalibration / Verification Tag की Date Expire ना िों | Verification Tag / Calibration Tag visual प्रतिदिन",
        "specification": "Calibration / Verification Tag की Date Expire ना िों",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
        "s_no": 7,
        "checkpoint": "चके करेंकक ESD Wrist Band OK िों | (Where Applicable) लाल / िरा SIGNAL (As per Work instruction) Wrist Band tester प्रतिदिन",
        "specification": "ESD Wrist Band OK",
        "control_method": "Wrist Band tester",
        "frequency": "daily"
    },
    {
        "s_no": 8,
        "checkpoint": "ESD wrist band पिनें| (Where Applicable) कार्यकरिेसमर् Visual प्रतिदिन",
        "specification": "ESD wrist band पिन",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
        "s_no": 9,
        "checkpoint": "Face mask पिनें| (Where Applicable) Shop Floor पर उपलब्ध िों| (As per Work instruction) visual प्रतिदिन",
        "specification": "Face mask पिन",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
        "s_no": 10,
        "checkpoint": "ESD Jacket & Cap, ESD Gloves/Finger coats पिनें| कार्यकरिेसमर् Visual प्रतिदिन",
        "specification": "ESD Jacket & Cap, ESD Gloves/Finger coats",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
        "s_no": 11,
        "checkpoint": "चके करेंकक Red Drawer मेंNG Parts रखनेके ललए Tray उपलब्ध िों | कार्यशरूु करनेसेपिले visual प्रतिदिन",
        "specification": "Red Drawer मेंNG Parts रखनेके ललए Tray उपलब्ध िों",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
        "s_no": 12,
        "checkpoint": "चके करेंकक Drawer मेंजरूरि के अनसु ी र सभी टैग & PPE's उपलब्ध िों | Reject Tag, OK Tag, Abnormal Situation Tag etc. visual प्रतिदिन",
        "specification": "Drawer मेंजरूरि के अनसु ी र सभी टैग & PPE's उपलब्ध िों",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
        "s_no": 13,
        "checkpoint": "चके करेंकक Drawer मेंकोई भी अनपुर्ोगी वस्िुना िों | कार्यशरूु करनेसेपिले visual प्रतिदिन",
        "specification": "Drawer मेंकोई भी अनपुर्ोगी वस्िुना िों",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
        "s_no": 14,
        "checkpoint": "चके करेंकक कार्स्य थल पर जरुरि के अनसु ी र सभी Documents उपलब्ध िों | Setup & FPA, Daily monthly Rejection sheet,Control Charts etc. visual प्रतिदिन",
        "specification": "कार्स्य थल पर जरुरि के अनसु ी र सभी Documents उपलब्ध िों",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
        "s_no": 15,
        "checkpoint": "चके करेंकक Line पर OK/NG Master sample उपलब्ध िो और उसकी Date Expire ना िों | कार्यशरूु करनेसेपिले visual प्रतिदिन",
        "specification": "Line पर OK/NG Master sample उपलब्ध िो",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
        "s_no": 16,
        "checkpoint": "Tea Break और Lunch मेंबािर जािेसमर् अपनेSetup / System को OFF करके जाएँ| Tea break & Lunch visual प्रतिदिन",
        "specification": "Tea Break और Lunch मेंबािर जािेसमर् अपनेSetup / System को OFF करके जाएँ",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
        "s_no": 17,
        "checkpoint": "Tea Break और Lunch मेंबािर जािेसमर् LIGHT को OFF करके जाएँ| Tea break & Lunch visual प्रतिदिन",
        "specification": "Tea Break और Lunch मेंबािर जािेसमर् LIGHT को OFF करके जाएँ",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
        "s_no": 18,
        "checkpoint": "Tea Break & Lunch मेंर्दि Shop Floor के अन्िर िैंिो Jacket & Cap पिन कर रखें| Tea break & Lunch visual प्रतिदिन",
        "specification": "Tea Break & Lunch मेंर्दि Shop Floor के अन्िर िैंिो Jacket & Cap पिन कर रखें",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
        "s_no": 19,
        "checkpoint": "FRL (Pressure gauge) मेंलगी Pin को Push करके 10~12 Sec िक Air को तनकालें, र्दि Air के साथ साथ पानी भी आ रिा िो िो िरुंि अपनेसपु रवाइजर को सचूचि करें| (Where FRL Applicable) OK/NG Visual / Manual प्रतिदिन",
        "specification": "FRL (Pressure gauge) मेंलगी Pin को Push करके 10~12 Sec िक Air को तनकालें, र्दि Air के साथ साथ पानी भी आ रिा िो िो िरुंि अपनेसपु रवाइजर को सचूचि करें",
        "control_method": "Visual / Manual",
        "frequency": "daily"
    },
    {
        "s_no": 20,
        "checkpoint": "चके करेंकक ररजेक्ट िुए Parts के Hand over का िरीका सिी िों | OK/NG सपु रवाइजर के द्वारा प्रतिदिन",
        "specification": "ररजेक्ट िुए Parts के Hand over का िरीका सिी िों",
        "control_method": "Supervisor's verification",
        "frequency": "daily"
    },
    {
        "s_no": 21,
        "checkpoint": "ESD Shoes/Sleepers पिनें| (Where Applicable) Shop Floor पर उपलब्ध िों | visual प्रतिदिन",
        "specification": "ESD Shoes/Sleepers पिन",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
        "s_no": 22,
        "checkpoint": "Skill level Card को चके करेंकक उसकी Valid Date Expire ना िों | Shop Floor पर उपलब्ध िों और Valid Date Expire ना िों | visual प्रतिदिन",
        "specification": "Skill level Card को चके करेंकक उसकी Valid Date Expire ना िों",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
        "s_no": 23,
        "checkpoint": "चके करेंकक ESD Shoes / Sleepers OK िों | (Where Applicable) OK/NG visual प्रतिदिन",
        "specification": "ESD Shoes / Sleepers OK",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
        "s_no": 24,
        "checkpoint": "चके करेंकक िर लशफ्ट मेंकार्यशरू करनेसेपिले POGO Pins की ठीक सेसफाई करें| (Where Applicable) OK/NG visual प्रतिदिन",
        "specification": "िर लशफ्ट मेंकार्यशरू करनेसेपिले POGO Pins की ठीक सेसफाई करें",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
        "s_no": 25,
        "checkpoint": "कार्यशरू करनेसेपिलेCuring Rack की condition चके करेंकक Timer सेसेटििों और रैक Damage ना िों | (Where Applicable) OK/NG visual प्रतिदिन",
        "specification": "Curing Rack की condition चके करेंकक Timer सेसेटििों और रैक Damage ना िों",
        "control_method": "visual",
        "frequency": "daily"
    }
   
]
    context = {
        'form': form,
        'json_data': json_data,
        'checkpoint_fields': checkpoint_fields,
        'user_skill_level':user_skill_level,
       }


    return render(request, 'startup/startup_checksheet_form.html',context)

# DetailView to view details of a StartUpCheckSheet entry
class StartUpCheckSheetDetailView(DetailView):
    model = StartUpCheckSheet
    template_name = 'startup/startup_checksheet_detail.html'  # Create this template
    context_object_name = 'check_sheet'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['json_data'] = [
    {
        "s_no": 1,
        "checkpoint": "Plan के अनसु ार Part assy & Child parts Working Table पर रखें| प्लान के अनसु ार | visual प्रतिदिन",
        "specification": "Part assy & Child parts",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
        "s_no": 2,
        "checkpoint": "अपनेकार्स्य थल को साफ करे| कार्स्य थल धलू रदिि िोना चादिए | visual प्रतिदिन",
        "specification": "साफ करे",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
        "s_no": 3,
        "checkpoint": "कार्यकरनेसेपिलेWorking table पर सेअनावश्र्क Part / material िटा िें, और उसेउसकी जगि पर रखें| अनावश्र्क Part / material Working Table पर ना िों | visual प्रतिदिन",
        "specification": "Working table पर सेअनावश्र्क Part / material िटा िें",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
        "s_no": 4,
        "checkpoint": "Dirty tray को लाइन पर use ना करेउसको उसकी तनधायररि जगि पर सफाई के ललए रख िे| Dirty Tray Area visual प्रतिदिन",
        "specification": "Dirty tray को लाइन पर use ना करेउसको उसकी तनधायररि जगि पर सफाई के ललए रख िे",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
        "s_no": 5,
        "checkpoint": "चके करेंकक Fixture / Machine Condition OK िों और उसके सभी Connections ठीक िों, Loose ना िों | Fixture / Machine Condition OK, No loose connections visual प्रतिदिन",
        "specification": "Fixture / Machine Condition OK",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
        "s_no": 6,
        "checkpoint": "चके करेंकक Fixture / Machine मेंलगेCalibration / Verification Tag की Date Expire ना िों | Verification Tag / Calibration Tag visual प्रतिदिन",
        "specification": "Calibration / Verification Tag की Date Expire ना िों",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
        "s_no": 7,
        "checkpoint": "चके करेंकक ESD Wrist Band OK िों | (Where Applicable) लाल / िरा SIGNAL (As per Work instruction) Wrist Band tester प्रतिदिन",
        "specification": "ESD Wrist Band OK",
        "control_method": "Wrist Band tester",
        "frequency": "daily"
    },
    {
        "s_no": 8,
        "checkpoint": "ESD wrist band पिनें| (Where Applicable) कार्यकरिेसमर् Visual प्रतिदिन",
        "specification": "ESD wrist band पिन",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
        "s_no": 9,
        "checkpoint": "Face mask पिनें| (Where Applicable) Shop Floor पर उपलब्ध िों| (As per Work instruction) visual प्रतिदिन",
        "specification": "Face mask पिन",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
        "s_no": 10,
        "checkpoint": "ESD Jacket & Cap, ESD Gloves/Finger coats पिनें| कार्यकरिेसमर् Visual प्रतिदिन",
        "specification": "ESD Jacket & Cap, ESD Gloves/Finger coats",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
        "s_no": 11,
        "checkpoint": "चके करेंकक Red Drawer मेंNG Parts रखनेके ललए Tray उपलब्ध िों | कार्यशरूु करनेसेपिले visual प्रतिदिन",
        "specification": "Red Drawer मेंNG Parts रखनेके ललए Tray उपलब्ध िों",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
        "s_no": 12,
        "checkpoint": "चके करेंकक Drawer मेंजरूरि के अनसु ी र सभी टैग & PPE's उपलब्ध िों | Reject Tag, OK Tag, Abnormal Situation Tag etc. visual प्रतिदिन",
        "specification": "Drawer मेंजरूरि के अनसु ी र सभी टैग & PPE's उपलब्ध िों",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
        "s_no": 13,
        "checkpoint": "चके करेंकक Drawer मेंकोई भी अनपुर्ोगी वस्िुना िों | कार्यशरूु करनेसेपिले visual प्रतिदिन",
        "specification": "Drawer मेंकोई भी अनपुर्ोगी वस्िुना िों",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
        "s_no": 14,
        "checkpoint": "चके करेंकक कार्स्य थल पर जरुरि के अनसु ी र सभी Documents उपलब्ध िों | Setup & FPA, Daily monthly Rejection sheet,Control Charts etc. visual प्रतिदिन",
        "specification": "कार्स्य थल पर जरुरि के अनसु ी र सभी Documents उपलब्ध िों",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
        "s_no": 15,
        "checkpoint": "चके करेंकक Line पर OK/NG Master sample उपलब्ध िो और उसकी Date Expire ना िों | कार्यशरूु करनेसेपिले visual प्रतिदिन",
        "specification": "Line पर OK/NG Master sample उपलब्ध िो",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
        "s_no": 16,
        "checkpoint": "Tea Break और Lunch मेंबािर जािेसमर् अपनेSetup / System को OFF करके जाएँ| Tea break & Lunch visual प्रतिदिन",
        "specification": "Tea Break और Lunch मेंबािर जािेसमर् अपनेSetup / System को OFF करके जाएँ",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
        "s_no": 17,
        "checkpoint": "Tea Break और Lunch मेंबािर जािेसमर् LIGHT को OFF करके जाएँ| Tea break & Lunch visual प्रतिदिन",
        "specification": "Tea Break और Lunch मेंबािर जािेसमर् LIGHT को OFF करके जाएँ",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
        "s_no": 18,
        "checkpoint": "Tea Break & Lunch मेंर्दि Shop Floor के अन्िर िैंिो Jacket & Cap पिन कर रखें| Tea break & Lunch visual प्रतिदिन",
        "specification": "Tea Break & Lunch मेंर्दि Shop Floor के अन्िर िैंिो Jacket & Cap पिन कर रखें",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
        "s_no": 19,
        "checkpoint": "FRL (Pressure gauge) मेंलगी Pin को Push करके 10~12 Sec िक Air को तनकालें, र्दि Air के साथ साथ पानी भी आ रिा िो िो िरुंि अपनेसपु रवाइजर को सचूचि करें| (Where FRL Applicable) OK/NG Visual / Manual प्रतिदिन",
        "specification": "FRL (Pressure gauge) मेंलगी Pin को Push करके 10~12 Sec िक Air को तनकालें, र्दि Air के साथ साथ पानी भी आ रिा िो िो िरुंि अपनेसपु रवाइजर को सचूचि करें",
        "control_method": "Visual / Manual",
        "frequency": "daily"
    },
    {
        "s_no": 20,
        "checkpoint": "चके करेंकक ररजेक्ट िुए Parts के Hand over का िरीका सिी िों | OK/NG सपु रवाइजर के द्वारा प्रतिदिन",
        "specification": "ररजेक्ट िुए Parts के Hand over का िरीका सिी िों",
        "control_method": "Supervisor's verification",
        "frequency": "daily"
    },
    {
        "s_no": 21,
        "checkpoint": "ESD Shoes/Sleepers पिनें| (Where Applicable) Shop Floor पर उपलब्ध िों | visual प्रतिदिन",
        "specification": "ESD Shoes/Sleepers पिन",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
        "s_no": 22,
        "checkpoint": "Skill level Card को चके करेंकक उसकी Valid Date Expire ना िों | Shop Floor पर उपलब्ध िों और Valid Date Expire ना िों | visual प्रतिदिन",
        "specification": "Skill level Card को चके करेंकक उसकी Valid Date Expire ना िों",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
        "s_no": 23,
        "checkpoint": "चके करेंकक ESD Shoes / Sleepers OK िों | (Where Applicable) OK/NG visual प्रतिदिन",
        "specification": "ESD Shoes / Sleepers OK",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
        "s_no": 24,
        "checkpoint": "चके करेंकक िर लशफ्ट मेंकार्यशरू करनेसेपिले POGO Pins की ठीक सेसफाई करें| (Where Applicable) OK/NG visual प्रतिदिन",
        "specification": "िर लशफ्ट मेंकार्यशरू करनेसेपिले POGO Pins की ठीक सेसफाई करें",
        "control_method": "visual",
        "frequency": "daily"
    },
    {
        "s_no": 25,
        "checkpoint": "कार्यशरू करनेसेपिलेCuring Rack की condition चके करेंकक Timer सेसेटििों और रैक Damage ना िों | (Where Applicable) OK/NG visual प्रतिदिन",
        "specification": "Curing Rack की condition चके करेंकक Timer सेसेटििों और रैक Damage ना िों",
        "control_method": "visual",
        "frequency": "daily"
    }
   
    ]
        check_sheet = self.object
        context['checkpoint_fields'] = []
        for i in range(1, 26):  # Assuming 25 checkpoints
            field_name = f'checkpoint_{i}'
            field_value = getattr(check_sheet, field_name, '')
            context['checkpoint_fields'].append(field_value)
        
        return context
        
# UpdateView to update an existing StartUpCheckSheet entry
class StartUpCheckSheetUpdateView(UpdateView):
    model = StartUpCheckSheet
    form_class = StartUpCheckSheetForm
    template_name = 'startup/startup_checksheet_form.html'  # Reuse the form template
    success_url = reverse_lazy('checksheet_list')  # Redirect to list view after update

# DeleteView to delete a StartUpCheckSheet entry
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
# def get_process_info(request, process_operation_id):
#     process_operation = get_object_or_404(ProcessOperation, id=process_operation_id)
#     return JsonResponse({'required_skill': process_operation.min_skill_required})
    
    
    

from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import PChartData
from .forms import PChartDataForm

class PChartDataListView(ListView):
    model = PChartData
    template_name = 'pchart/pchart_list.html'
    context_object_name = 'pchart_data'

class PChartDataDetailView(DetailView):
    model = PChartData
    template_name = 'pchart/pchart_detail.html'
    context_object_name = 'pchart_data'

class PChartDataCreateView(CreateView):
    model = PChartData
    form_class = PChartDataForm
    template_name = 'pchart/pchart_form.html'
    success_url = reverse_lazy('pchart_list')

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
        queryset = PChartData.objects.all()
        
        if location:
            queryset = queryset.filter(location=location)
        
        chart_data = {
            'labels': [],
            'proportion': [],
            'ucl_p': [],
            'lcl_p': [],
            'center_line': []
        }
        
        avg_proportion = queryset.aggregate(avg_p=Avg('proportion'))['avg_p'] or 0
        
        for data in queryset.order_by('month'):
            chart_data['labels'].append(data.month.strftime('%Y-%m-%d'))
            chart_data['proportion'].append(float(data.proportion or 0))
            chart_data['ucl_p'].append(float(data.ucl_p or 0))
            chart_data['lcl_p'].append(float(data.lcl_p or 0))
            chart_data['center_line'].append(float(avg_proportion))
        
        context.update({
            'chart_data': json.dumps(chart_data),
            'locations': dict(MACHINE_LOCATION_CHOICES),
            'selected_location': location
        })
        return context







# views.py
from django.views.generic import ListView
from django.apps import apps
from django.utils import timezone
from datetime import timedelta
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
        
        for model in history_models:
            records = model.history.all()
            if retention_date:
                records = records.filter(history_date__gte=retention_date)
                
            for record in records:
                record.change_list = self.get_changes(record)
                record.model_name = record._meta.verbose_name.title()
            combined_history.extend(records)

        return sorted(combined_history, 
                     key=lambda x: x.history_date, 
                     reverse=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Audit History'
        context['retention_choices'] = AUDIT_HISTORY_RETENTION_CHOICES
        context['current_retention'] = self.request.GET.get('retention', DEFAULT_AUDIT_RETENTION)
        return context