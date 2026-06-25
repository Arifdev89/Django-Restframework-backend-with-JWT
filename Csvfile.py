import csv
import os
from django.core.management.base import BaseCommand
from api.products.models import Product


class Command(BaseCommand):
    help = 'Load products from products_data.csv into the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--csv',
            type=str,
            default='products_data.csv',
            help='Path to the CSV file (default: products_data.csv)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing products before loading'
        )

    def handle(self, *args, **options):
        csv_path = options['csv']

        if not os.path.exists(csv_path):
            self.stderr.write(self.style.ERROR(f'File not found: {csv_path}'))
            return

        if options['clear']:
            count, _ = Product.objects.all().delete()
            self.stdout.write(self.style.WARNING(f'Cleared {count} existing products.'))

        products_to_create = []
        skipped = 0
        total = 0

        with open(csv_path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                total += 1
                try:
                    # Parse tags: comma-separated string → list
                    raw_tags = row.get('tags', '')
                    tags = [t.strip() for t in raw_tags.split(',') if t.strip()]

                    products_to_create.append(Product(
                        id=int(row['id']),
                        product_name=row['product_name'].strip(),
                        product_description=row['product_description'].strip(),
                        category=row['category'].strip(),
                        tags=tags,
                    ))
                except Exception as e:
                    skipped += 1
                    self.stderr.write(f'Skipped row {row.get("id", "?")}: {e}')

        # Bulk insert — much faster than one-by-one
        Product.objects.bulk_create(products_to_create, ignore_conflicts=True)

        loaded = total - skipped
        self.stdout.write(self.style.SUCCESS(
            f'Done! Loaded {loaded}/{total} products. Skipped {skipped}.'
        ))
