"""
LPO Service Layer
Business logic for LPO creation, updates, and management
"""
from models import db
from models.lpo import LPO, LPOHistory
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import func, extract


class LPOService:
    """Service for managing Local Purchase Orders"""
    
    @staticmethod
    def generate_lpo_number(year=None):
        """
        Generate next LPO number in format: LPO/PKP/YYYY/NNNN
        Example: LPO/PKP/2025/0001
        """
        if year is None:
            year = datetime.now().year
        
        # Get the last LPO number for this year
        last_lpo = db.session.query(LPO).filter(
            extract('year', LPO.lpo_date) == year
        ).order_by(LPO.lpo_number.desc()).first()
        
        if last_lpo and last_lpo.lpo_number:
            # Extract the sequence number from last LPO
            # Format: LPO/PKP/2025/0001
            parts = last_lpo.lpo_number.split('/')
            if len(parts) == 4:
                try:
                    last_seq = int(parts[3])
                    next_seq = last_seq + 1
                except (ValueError, IndexError):
                    next_seq = 1
            else:
                next_seq = 1
        else:
            next_seq = 1
        
        # Format: LPO/PKP/YYYY/NNNN
        lpo_number = f"LPO/PKP/{year}/{next_seq:04d}"
        
        # Ensure uniqueness (in case of race condition)
        while db.session.query(LPO).filter_by(lpo_number=lpo_number).first():
            next_seq += 1
            lpo_number = f"LPO/PKP/{year}/{next_seq:04d}"
        
        return lpo_number
    
    @staticmethod
    def calculate_item_totals(item, vat_percentage=5.0):
        """
        Calculate totals for a single item
        Returns updated item dict with calculated fields
        """
        qty = Decimal(str(item.get('quantity', 0) or item.get('qty', 0) or 0))
        unit_price = Decimal(str(item.get('unit_price', 0) or item.get('rate', 0) or item.get('price', 0) or 0))
        
        # Calculate subtotal
        subtotal = qty * unit_price
        
        # Calculate VAT
        vat_rate = Decimal(str(vat_percentage)) / Decimal('100')
        vat_amount = subtotal * vat_rate
        
        # Calculate total
        total_amount = subtotal + vat_amount
        
        # Update item with calculated values
        item['unit_price'] = float(unit_price)
        item['vat_amount'] = float(vat_amount)
        item['total_amount'] = float(total_amount)
        
        return item
    
    @staticmethod
    def calculate_lpo_totals(items, vat_percentage=5.0):
        """
        Calculate subtotal, VAT, and grand total for all items
        Returns dict with totals
        """
        subtotal = Decimal('0')
        vat_total = Decimal('0')
        
        for item in items:
            qty = Decimal(str(item.get('quantity', 0) or item.get('qty', 0) or 0))
            unit_price = Decimal(str(item.get('unit_price', 0) or item.get('rate', 0) or item.get('price', 0) or 0))
            
            item_subtotal = qty * unit_price
            subtotal += item_subtotal
        
        # Calculate VAT on subtotal
        vat_rate = Decimal(str(vat_percentage)) / Decimal('100')
        vat_total = subtotal * vat_rate
        
        # Calculate grand total
        grand_total = subtotal + vat_total
        
        return {
            'subtotal': float(subtotal),
            'vat_amount': float(vat_total),
            'grand_total': float(grand_total)
        }
    
    @staticmethod
    def create_lpo(data, created_by=None):
        """
        Create a new LPO
        
        Args:
            data: Dict containing LPO data
            created_by: Username of creator
        
        Returns:
            Created LPO object
        """
        # Generate LPO number if not provided
        if 'lpo_number' not in data or not data['lpo_number']:
            data['lpo_number'] = LPOService.generate_lpo_number()
        
        # Process items and calculate totals
        items = data.get('items', [])
        vat_percentage = data.get('vat_percentage', 5.0)
        
        # Calculate totals for each item
        processed_items = []
        for idx, item in enumerate(items, 1):
            item['number'] = idx
            processed_item = LPOService.calculate_item_totals(item, vat_percentage)
            processed_items.append(processed_item)
        
        # Calculate overall totals
        totals = LPOService.calculate_lpo_totals(processed_items, vat_percentage)
        
        # Create LPO object
        lpo = LPO(
            lpo_number=data['lpo_number'],
            revision=data.get('revision', '00'),
            status=data.get('status', 'draft'),
            lpo_date=data.get('lpo_date', date.today()),
            quotation_date=data.get('quotation_date'),
            delivery_date=data.get('delivery_date'),
            project_name=data['project_name'],
            project_location=data.get('project_location'),
            consultant=data.get('consultant'),
            supplier_name=data['supplier_name'],
            supplier_address=data.get('supplier_address'),
            supplier_trn=data.get('supplier_trn'),
            supplier_tel=data.get('supplier_tel'),
            supplier_fax=data.get('supplier_fax'),
            contact_person=data.get('contact_person'),
            contact_number=data.get('contact_number'),
            quotation_ref=data.get('quotation_ref'),
            quotation_pdf_path=data.get('quotation_pdf_path'),
            column_structure=data['column_structure'],
            items=processed_items,
            subtotal=totals['subtotal'],
            vat_percentage=vat_percentage,
            vat_amount=totals['vat_amount'],
            grand_total=totals['grand_total'],
            payment_terms=data.get('payment_terms'),
            delivery_terms=data.get('delivery_terms'),
            warranty_terms=data.get('warranty_terms'),
            other_terms=data.get('other_terms'),
            notes=data.get('notes'),
            internal_notes=data.get('internal_notes'),
            created_by=created_by,
            extraction_method=data.get('extraction_method', 'manual'),
            extraction_confidence=data.get('extraction_confidence'),
            extraction_notes=data.get('extraction_notes')
        )
        
        db.session.add(lpo)
        db.session.commit()
        
        # Create history entry
        LPOService.add_history(
            lpo.id,
            action='created',
            new_status='draft',
            notes='LPO created',
            performed_by=created_by
        )
        
        return lpo
    
    @staticmethod
    def update_lpo(lpo_id, data, updated_by=None):
        """Update an existing LPO"""
        lpo = db.session.query(LPO).get(lpo_id)
        if not lpo:
            raise ValueError(f"LPO with id {lpo_id} not found")
        
        if not lpo.is_editable:
            raise ValueError(f"LPO {lpo.lpo_number} cannot be edited (status: {lpo.status})")
        
        # Track changes for history
        changes = {}
        
        # Update fields
        updatable_fields = [
            'project_name', 'project_location', 'consultant',
            'supplier_name', 'supplier_address', 'supplier_trn',
            'supplier_tel', 'supplier_fax', 'contact_person',
            'contact_number', 'quotation_ref', 'quotation_date',
            'delivery_date', 'payment_terms', 'delivery_terms',
            'warranty_terms', 'other_terms', 'notes', 'internal_notes'
        ]
        
        for field in updatable_fields:
            if field in data:
                old_value = getattr(lpo, field)
                new_value = data[field]
                if old_value != new_value:
                    changes[field] = {'old': old_value, 'new': new_value}
                    setattr(lpo, field, new_value)
        
        # Update items if provided
        if 'items' in data:
            items = data['items']
            vat_percentage = data.get('vat_percentage', lpo.vat_percentage)
            
            # Process items
            processed_items = []
            for idx, item in enumerate(items, 1):
                item['number'] = idx
                processed_item = LPOService.calculate_item_totals(item, vat_percentage)
                processed_items.append(processed_item)
            
            # Calculate totals
            totals = LPOService.calculate_lpo_totals(processed_items, vat_percentage)
            
            lpo.items = processed_items
            lpo.column_structure = data.get('column_structure', lpo.column_structure)
            lpo.subtotal = totals['subtotal']
            lpo.vat_percentage = vat_percentage
            lpo.vat_amount = totals['vat_amount']
            lpo.grand_total = totals['grand_total']
            
            changes['items'] = {'old': 'updated', 'new': f'{len(processed_items)} items'}
        
        lpo.updated_at = datetime.utcnow()
        db.session.commit()
        
        # Add history
        if changes:
            LPOService.add_history(
                lpo.id,
                action='updated',
                changes=changes,
                notes='LPO updated',
                performed_by=updated_by
            )
        
        return lpo
    
    @staticmethod
    def change_status(lpo_id, new_status, performed_by=None, notes=None):
        """Change LPO status"""
        lpo = db.session.query(LPO).get(lpo_id)
        if not lpo:
            raise ValueError(f"LPO with id {lpo_id} not found")
        
        old_status = lpo.status
        lpo.status = new_status
        lpo.updated_at = datetime.utcnow()
        
        if new_status == 'issued':
            lpo.issued_at = datetime.utcnow()
        
        db.session.commit()
        
        # Add history
        LPOService.add_history(
            lpo.id,
            action='status_changed',
            old_status=old_status,
            new_status=new_status,
            notes=notes or f'Status changed from {old_status} to {new_status}',
            performed_by=performed_by
        )
        
        return lpo
    
    @staticmethod
    def get_lpo(lpo_id):
        """Get LPO by ID"""
        return db.session.query(LPO).get(lpo_id)
    
    @staticmethod
    def get_lpo_by_number(lpo_number):
        """Get LPO by number"""
        return db.session.query(LPO).filter_by(lpo_number=lpo_number).first()
    
    @staticmethod
    def list_lpos(filters=None, page=1, per_page=20):
        """
        List LPOs with optional filters
        
        Args:
            filters: Dict with filter criteria
            page: Page number
            per_page: Items per page
        
        Returns:
            Paginated list of LPOs
        """
        query = db.session.query(LPO)
        
        if filters:
            if 'status' in filters:
                query = query.filter(LPO.status == filters['status'])
            
            if 'supplier_name' in filters:
                query = query.filter(LPO.supplier_name.ilike(f"%{filters['supplier_name']}%"))
            
            if 'project_name' in filters:
                query = query.filter(LPO.project_name.ilike(f"%{filters['project_name']}%"))
            
            if 'from_date' in filters:
                query = query.filter(LPO.lpo_date >= filters['from_date'])
            
            if 'to_date' in filters:
                query = query.filter(LPO.lpo_date <= filters['to_date'])
        
        # Order by LPO number descending (newest first)
        query = query.order_by(LPO.lpo_number.desc())
        
        # Paginate
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return pagination
    
    @staticmethod
    def delete_lpo(lpo_id, performed_by=None):
        """Delete LPO (soft delete by setting status to cancelled)"""
        lpo = db.session.query(LPO).get(lpo_id)
        if not lpo:
            raise ValueError(f"LPO with id {lpo_id} not found")
        
        old_status = lpo.status
        lpo.status = 'cancelled'
        lpo.updated_at = datetime.utcnow()
        db.session.commit()
        
        # Add history
        LPOService.add_history(
            lpo.id,
            action='cancelled',
            old_status=old_status,
            new_status='cancelled',
            notes='LPO cancelled',
            performed_by=performed_by
        )
        
        return lpo
    
    @staticmethod
    def add_history(lpo_id, action, old_status=None, new_status=None, 
                   changes=None, notes=None, performed_by=None):
        """Add history entry for LPO"""
        history = LPOHistory(
            lpo_id=lpo_id,
            action=action,
            old_status=old_status,
            new_status=new_status,
            changes=changes,
            notes=notes,
            performed_by=performed_by,
            performed_at=datetime.utcnow()
        )
        db.session.add(history)
        db.session.commit()
        return history
