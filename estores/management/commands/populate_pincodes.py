"""
Management command to populate Indian PIN codes for an estore.

Usage:
    python manage.py populate_pincodes --estore-id 1
    python manage.py populate_pincodes --estore-name "My Store"
    python manage.py populate_pincodes --estore-id 1 --csv-file path/to/pincodes.csv
    python manage.py populate_pincodes --estore-id 1 --cod-default False
"""

import csv
import os
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from estores.models import EStore, DeliveryPin


class Command(BaseCommand):
    help = 'Populate all Indian PIN codes for an estore'

    def add_arguments(self, parser):
        parser.add_argument(
            '--estore-id',
            type=int,
            help='ID of the estore to populate PIN codes for',
        )
        parser.add_argument(
            '--estore-name',
            type=str,
            help='Name of the estore to populate PIN codes for',
        )
        parser.add_argument(
            '--csv-file',
            type=str,
            help='Path to CSV file with PIN codes (columns: pincode, city, state)',
        )
        parser.add_argument(
            '--cod-default',
            type=str,
            default='True',
            choices=['True', 'False', 'true', 'false'],
            help='Default COD availability for all PIN codes (default: True)',
        )
        parser.add_argument(
            '--clear-existing',
            action='store_true',
            help='Clear existing PIN codes for this estore before populating',
        )

    def handle(self, *args, **options):
        estore_id = options.get('estore_id')
        estore_name = options.get('estore_name')
        csv_file = options.get('csv_file')
        cod_default_str = options.get('cod_default', 'True')
        cod_default = cod_default_str.lower() == 'true'
        clear_existing = options.get('clear_existing', False)

        # Get the estore
        if estore_id:
            try:
                estore = EStore.objects.get(id=estore_id)
            except EStore.DoesNotExist:
                raise CommandError(f'EStore with ID {estore_id} does not exist.')
        elif estore_name:
            try:
                estore = EStore.objects.get(name=estore_name)
            except EStore.DoesNotExist:
                raise CommandError(f'EStore with name "{estore_name}" does not exist.')
            except EStore.MultipleObjectsReturned:
                raise CommandError(f'Multiple estores found with name "{estore_name}". Please use --estore-id instead.')
        else:
            raise CommandError('You must provide either --estore-id or --estore-name.')

        self.stdout.write(f'Populating PIN codes for estore: {estore.name} (ID: {estore.id})')

        # Clear existing PIN codes if requested
        if clear_existing:
            deleted_count = DeliveryPin.objects.filter(estore=estore).delete()[0]
            self.stdout.write(self.style.WARNING(f'Deleted {deleted_count} existing PIN codes.'))

        # Get PIN code data
        if csv_file:
            pin_data = self._load_from_csv(csv_file)
        else:
            # Use built-in comprehensive Indian PIN code dataset
            pin_data = self._get_indian_pincodes()

        # Create DeliveryPin objects in bulk
        created_count = 0
        skipped_count = 0
        errors = []

        with transaction.atomic():
            # Use bulk_create for better performance
            delivery_pins = []
            existing_pins = set(
                DeliveryPin.objects.filter(estore=estore).values_list('pin_code', flat=True)
            )

            for pin_info in pin_data:
                pin_code = str(pin_info['pincode']).strip()
                
                # Skip if already exists
                if pin_code in existing_pins:
                    skipped_count += 1
                    continue

                # Validate PIN code (Indian PIN codes are 6 digits)
                if not pin_code.isdigit() or len(pin_code) != 6:
                    errors.append(f'Invalid PIN code: {pin_code}')
                    continue

                delivery_pin = DeliveryPin(
                    estore=estore,
                    pin_code=pin_code,
                    city=pin_info.get('city', '').strip()[:100] if pin_info.get('city') else None,
                    state=pin_info.get('state', '').strip()[:100] if pin_info.get('state') else None,
                    cod_available=cod_default,
                )
                delivery_pins.append(delivery_pin)
                existing_pins.add(pin_code)

            # Bulk create in batches of 1000
            batch_size = 1000
            for i in range(0, len(delivery_pins), batch_size):
                batch = delivery_pins[i:i + batch_size]
                DeliveryPin.objects.bulk_create(batch, ignore_conflicts=True)
                created_count += len(batch)
                self.stdout.write(f'Created batch: {len(batch)} PIN codes (Total: {i + len(batch)})')

        # Summary
        self.stdout.write(self.style.SUCCESS(
            f'\nSuccessfully populated PIN codes for {estore.name}:\n'
            f'  - Created: {created_count}\n'
            f'  - Skipped (already exists): {skipped_count}\n'
            f'  - Errors: {len(errors)}'
        ))

        if errors:
            self.stdout.write(self.style.WARNING(f'\nErrors encountered:\n' + '\n'.join(errors[:10])))
            if len(errors) > 10:
                self.stdout.write(self.style.WARNING(f'... and {len(errors) - 10} more errors.'))

    def _load_from_csv(self, csv_file_path):
        """Load PIN codes from a CSV file."""
        if not os.path.exists(csv_file_path):
            raise CommandError(f'CSV file not found: {csv_file_path}')

        pin_data = []
        seen_pincodes = set()  # To avoid duplicates
        try:
            with open(csv_file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Handle different possible column names for pincode
                    pincode_raw = (row.get('pincode') or row.get('pin_code') or 
                                  row.get('PIN') or row.get('Pincode'))
                    pincode = str(pincode_raw).strip() if pincode_raw else None
                    
                    # Handle different possible column names for city
                    city_raw = (row.get('city') or row.get('City') or row.get('CITY') or 
                               row.get('district') or row.get('District') or row.get('DISTRICT') or 
                               row.get('officename') or row.get('OfficeName'))
                    city = str(city_raw).strip() if city_raw else ''
                    
                    # Handle different possible column names for state
                    state_raw = (row.get('state') or row.get('State') or row.get('STATE') or 
                                row.get('statename') or row.get('StateName') or row.get('STATENAME'))
                    state = str(state_raw).strip() if state_raw else ''

                    if pincode:
                        # Convert pincode to string and ensure it's 6 digits
                        pincode_str = str(pincode).strip()
                        # Skip if already processed (avoid duplicates)
                        if pincode_str not in seen_pincodes:
                            seen_pincodes.add(pincode_str)
                            pin_data.append({
                                'pincode': pincode_str,
                                'city': city[:100] if city else None,  # Limit to 100 chars
                                'state': state[:100] if state else None,  # Limit to 100 chars
                            })
        except Exception as e:
            raise CommandError(f'Error reading CSV file: {str(e)}')

        self.stdout.write(f'Loaded {len(pin_data)} unique PIN codes from CSV file.')
        return pin_data

    def _get_indian_pincodes(self):
        """
        Get comprehensive Indian PIN code dataset.
        Tries to use indiapins package if available, otherwise falls back to sample data.
        """
        # Try to use indiapins package if available
        try:
            import indiapins
            self.stdout.write('Using indiapins package for comprehensive PIN code data...')
            pin_data = []
            
            # Get all PIN codes from the package
            # The package structure may vary, so we'll try common methods
            if hasattr(indiapins, 'get_all_pincodes'):
                all_pins = indiapins.get_all_pincodes()
                for pin_info in all_pins:
                    pin_data.append({
                        'pincode': str(pin_info.get('pincode', '')).zfill(6),
                        'city': pin_info.get('city', '') or pin_info.get('office_name', ''),
                        'state': pin_info.get('state', '') or pin_info.get('state_name', ''),
                    })
            elif hasattr(indiapins, 'data'):
                # If package has a data attribute
                for pin_info in indiapins.data:
                    pin_data.append({
                        'pincode': str(pin_info.get('pincode', '')).zfill(6),
                        'city': pin_info.get('city', '') or pin_info.get('office_name', ''),
                        'state': pin_info.get('state', '') or pin_info.get('state_name', ''),
                    })
            else:
                # Try to access data directly
                import indiapins.data as pin_data_module
                for pin_info in pin_data_module:
                    pin_data.append({
                        'pincode': str(pin_info.get('pincode', '')).zfill(6),
                        'city': pin_info.get('city', '') or pin_info.get('office_name', ''),
                        'state': pin_info.get('state', '') or pin_info.get('state_name', ''),
                    })
            
            if pin_data:
                self.stdout.write(f'Loaded {len(pin_data)} PIN codes from indiapins package.')
                return pin_data
        except ImportError:
            self.stdout.write(self.style.WARNING(
                'indiapins package not found. Install it with: pip install indiapins\n'
                'Or use --csv-file option with a complete PIN code dataset.'
            ))
        except Exception as e:
            self.stdout.write(self.style.WARNING(
                f'Error loading indiapins package: {str(e)}\n'
                'Falling back to sample dataset.'
            ))

        # Fallback to sample dataset
        self.stdout.write(self.style.WARNING(
            'Using sample PIN code dataset. For complete data:\n'
            '  1. Install indiapins: pip install indiapins\n'
            '  2. Or use --csv-file with a complete dataset from:\n'
            '     - https://data.gov.in (Government of India open data)\n'
            '     - https://github.com/IndiaPost/pin\n'
            '     - Or other reliable sources'
        ))
        
        sample_pincodes = [
            # Major cities - sample data
            {'pincode': '110001', 'city': 'New Delhi', 'state': 'Delhi'},
            {'pincode': '110002', 'city': 'New Delhi', 'state': 'Delhi'},
            {'pincode': '110003', 'city': 'New Delhi', 'state': 'Delhi'},
            {'pincode': '400001', 'city': 'Mumbai', 'state': 'Maharashtra'},
            {'pincode': '400002', 'city': 'Mumbai', 'state': 'Maharashtra'},
            {'pincode': '400003', 'city': 'Mumbai', 'state': 'Maharashtra'},
            {'pincode': '560001', 'city': 'Bangalore', 'state': 'Karnataka'},
            {'pincode': '560002', 'city': 'Bangalore', 'state': 'Karnataka'},
            {'pincode': '560003', 'city': 'Bangalore', 'state': 'Karnataka'},
            {'pincode': '600001', 'city': 'Chennai', 'state': 'Tamil Nadu'},
            {'pincode': '600002', 'city': 'Chennai', 'state': 'Tamil Nadu'},
            {'pincode': '600003', 'city': 'Chennai', 'state': 'Tamil Nadu'},
            {'pincode': '700001', 'city': 'Kolkata', 'state': 'West Bengal'},
            {'pincode': '700002', 'city': 'Kolkata', 'state': 'West Bengal'},
            {'pincode': '700003', 'city': 'Kolkata', 'state': 'West Bengal'},
            {'pincode': '380001', 'city': 'Ahmedabad', 'state': 'Gujarat'},
            {'pincode': '380002', 'city': 'Ahmedabad', 'state': 'Gujarat'},
            {'pincode': '380003', 'city': 'Ahmedabad', 'state': 'Gujarat'},
            {'pincode': '500001', 'city': 'Hyderabad', 'state': 'Telangana'},
            {'pincode': '500002', 'city': 'Hyderabad', 'state': 'Telangana'},
            {'pincode': '500003', 'city': 'Hyderabad', 'state': 'Telangana'},
            {'pincode': '411001', 'city': 'Pune', 'state': 'Maharashtra'},
            {'pincode': '411002', 'city': 'Pune', 'state': 'Maharashtra'},
            {'pincode': '411003', 'city': 'Pune', 'state': 'Maharashtra'},
            {'pincode': '302001', 'city': 'Jaipur', 'state': 'Rajasthan'},
            {'pincode': '302002', 'city': 'Jaipur', 'state': 'Rajasthan'},
            {'pincode': '302003', 'city': 'Jaipur', 'state': 'Rajasthan'},
            {'pincode': '110092', 'city': 'New Delhi', 'state': 'Delhi'},
            {'pincode': '400070', 'city': 'Mumbai', 'state': 'Maharashtra'},
            {'pincode': '560100', 'city': 'Bangalore', 'state': 'Karnataka'},
        ]
        
        return sample_pincodes
