# yourapp/management/commands/import_drugs.py
import pandas as pd
from django.core.management.base import BaseCommand
from drugs.models import Drug  # Update the import according to your app name

class Command(BaseCommand):
    help = 'Import drugs from an Excel file'

    def add_arguments(self, parser):
        parser.add_argument('excel_file', type=str, help='Path to the Excel file')

    def handle(self, *args, **options):
        excel_file = options['excel_file']
        try:
            data = pd.read_excel(excel_file)

            required_columns = ['Name', 'Company', 'Price']
            for _, row in data.iterrows():
                if all(column in row for column in required_columns):
                    name = row['Name']
                    price = row['Price']
                    company = row['Company']

                    # Validate price
                    if pd.isna(price) or not isinstance(price, (int, float)):
                        self.stdout.write(self.style.ERROR(f"Invalid price value for {name}, skipping."))
                        continue

                    # Create or update drug instance
                    Drug.objects.update_or_create(
                        name=name,
                        defaults={
                            'price': price,
                            'company': company
                        }
                    )
                else:
                    self.stdout.write(self.style.ERROR(f"Row is missing one or more required columns: {row}"))

            self.stdout.write(self.style.SUCCESS('Successfully imported drugs'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"An error occurred: {str(e)}"))
