import csv
from datetime import date, datetime
from decimal import Decimal
import io
import logging

from django.conf import settings

from .exceptions import EmptyFileError
from .utils import (
    retrieve_all_transactions, escape_csv_formula, reconcile_for_date
)

logger = logging.getLogger('mtp')


def generate_refund_file_for_date(api_session, receipt_date):
    start_date, end_date = reconcile_for_date(api_session, receipt_date)

    transactions_to_refund = retrieve_all_transactions(
        api_session,
        status='refundable',
        received_at__gte=start_date,
        received_at__lt=end_date
    )

    filedata = generate_refund_file(transactions_to_refund)

    refunded_transactions = [
        {'id': t['id'], 'refunded': True} for t in transactions_to_refund if not t['refunded']
    ]

    # mark transactions as refunded
    api_session.patch('transactions/', json=refunded_transactions)

    return (settings.REFUND_OUTPUT_FILENAME.format(date=date.today()), filedata)


def generate_refund_file(transactions):
    if len(transactions) == 0:
        raise EmptyFileError()

    with io.StringIO() as out:
        writer = csv.writer(out)

        for transaction in transactions:
            cells = map(escape_csv_formula, [
                transaction['sender_sort_code'],
                transaction['sender_account_number'],
                transaction['sender_name'],
                '%.2f' % (Decimal(transaction['amount'])/100),
                refund_reference(transaction)
            ])
            writer.writerow(list(cells))

        return out.getvalue()


def refund_reference(transaction):
    if transaction.get('sender_roll_number'):
        return transaction['sender_roll_number']
    else:
        receipt_date = datetime.strptime(transaction['received_at'][:10], '%Y-%m-%d')
        date_part = receipt_date.strftime('%d%m')
        ref_part = transaction['ref_code'][1:]
        return settings.REFUND_REFERENCE % (date_part, ref_part)
