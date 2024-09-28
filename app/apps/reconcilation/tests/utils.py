
def response_with_discrepanies_and_missing_data_in_json_format():
  return {
    'missing_in_source': [
      {
        'record_id': 3,
        'data': {
          'Name': 'David Doe',
          'Date': '2023-02-03',
          'Amount': 300.5
        }
      }
    ],
    'missing_in_target': [
      {
        'record_id': 2,
        'data': {
          'Name': 'Jane Doe',
          'Date': '2023-01-03',
          'Amount': 200.5
        }
      }
    ],
    'record_discrepancies': [
      {
        'record_id': 1,
        'source_data': {
          'Name': 'John Doe',
          'Date': '2023-01-03',
          'Amount': 100.5
        },
        'target_data': {
          'Name': 'John Doe',
          'Date': '2023-01-01',
          'Amount': 100.0
        },
        'discrepancy': {
          'Date': {
            'source_value': '2023-01-03',
            'target_name': '2023-01-01'
          },
          'Amount': {
            'source_value': 100.5,
            'target_name': 100.0
          }
        }
      }
    ]
  }


def response_with_discrepanies_and_missing_data_in_csv_format():
  return b'Record ID,Status,Name,Date,Amount,Discrepancy Field,Source Value,Target Value\n3,Missing in Source,David Doe,2023-02-03,300.5,,,\n2,Missing in Target,Jane Doe,2023-01-03,200.5,,,\n1,Discrepancy,John Doe,2023-01-03,100.5,Date,2023-01-03,2023-01-01\n1,Discrepancy,John Doe,2023-01-03,100.5,Amount,100.5,100.0\n'

def response_with_discrepanies_and_missing_data_in_html_format():
  return b'\n  <!DOCTYPE html>\n  <html lang="en">\n  <head>\n    <meta charset="UTF-8">\n    <meta name="viewport" content="width=device-width, initial-scale=1.0">\n    <title>Reconciliation Report</title>\n    <style>\n      body { font-family: Arial, sans-serif; margin: 20px; }\n      h1 { color: #333; }\n      h2 { color: #555; }\n      table { width: 100%; border-collapse: collapse; margin-bottom: 20px; }\n      th, td { border: 1px solid #ccc; padding: 8px; text-align: left; }\n      th { background-color: #f4f4f4; }\n      .discrepancy { color: red; }\n    </style>\n  </head>\n  <body>\n    <h1>Reconciliation Status</h1>\n    <p>Status: <strong>success</strong></p>\n    <p>Message: <strong>Reconciliation completed successfully.</strong></p>\n\n    <h2>Discrepancies</h2>\n  \n  <h3>Missing in Target</h3>\n  <table>\n    <thead>\n      <tr>\n        <th>Record ID</th>\n        <th>Name</th>\n        <th>Date</th>\n        <th>Amount</th>\n      </tr>\n    </thead>\n    <tbody>\n  \n        <tr>\n          <td>2</td>\n          <td>Jane Doe</td>\n          <td>2023-01-03</td>\n          <td>200.5</td>\n        </tr>\n      \n    </tbody>\n  </table>\n  \n  <h3>Missing in Source</h3>\n  <table>\n    <thead>\n      <tr>\n        <th>Record ID</th>\n        <th>Name</th>\n        <th>Date</th>\n        <th>Amount</th>\n      </tr>\n    </thead>\n    <tbody>\n  \n          <tr>\n            <td>3</td>\n            <td>David Doe</td>\n            <td>2023-02-03</td>\n            <td>300.5</td>\n          </tr>\n        \n    </tbody>\n  </table>\n  \n  <h3>Discrepancies in Matching Records</h3>\n  <table>\n    <thead>\n      <tr>\n        <th>Record ID</th>\n        <th>Source Name</th>\n        <th>Source Date</th>\n        <th>Source Amount</th>\n        <th>Target Name</th>\n        <th>Target Date</th>\n        <th>Target Amount</th>\n        <th>Discrepancy</th>\n      </tr>\n    </thead>\n    <tbody>\n  \n        <tr>\n          <td>1</td>\n          <td>John Doe</td>\n          <td>2023-01-03</td>\n          <td>100.5</td>\n          <td>John Doe</td>\n          <td>2023-01-01</td>\n          <td>100.0</td>\n          <td class="discrepancy">Date: 2023-01-03 vs 2023-01-01, Amount: 100.5 vs 100.0</td>\n        </tr>\n      \n    </tbody>\n  </table>\n  </body>\n  </html>\n  '
