import pandas as pd
from io import StringIO

def convert_to_csv(reconciliation_data):
  csv_data = []
  # Process 'missing_in_source'
  for item in reconciliation_data['missing_in_source']:
      csv_data.append({
          'Record ID': item['record_id'],
          'Status': 'Missing in Source',
          'Name': item['data']['Name'],
          'Date': item['data']['Date'],
          'Amount': item['data']['Amount'],
          'Discrepancy Field': '',
          'Source Value': '',
          'Target Value': ''
      })

  # Process 'missing_in_target'
  for item in reconciliation_data['missing_in_target']:
      csv_data.append({
          'Record ID': item['record_id'],
          'Status': 'Missing in Target',
          'Name': item['data']['Name'],
          'Date': item['data']['Date'],
          'Amount': item['data']['Amount'],
          'Discrepancy Field': '',
          'Source Value': '',
          'Target Value': ''
      })

  # Process 'record_discrepancies'
  for item in reconciliation_data['record_discrepancies']:
      for field, discrepancy in item['discrepancy'].items():
          csv_data.append({
              'Record ID': item['record_id'],
              'Status': 'Discrepancy',
              'Name': item['source_data']['Name'],
              'Date': item['source_data']['Date'],
              'Amount': item['source_data']['Amount'],
              'Discrepancy Field': field,
              'Source Value': discrepancy['source_value'],
              'Target Value': discrepancy['target_name']
          })

  # Convert list of dictionaries to DataFrame
  df = pd.DataFrame(csv_data)

  # Convert DataFrame to CSV
  csv_buffer = StringIO()
  df.to_csv(csv_buffer, index=False)
  return csv_buffer.getvalue().encode('utf-8')

def convert_to_html(reconciliation_data):
  # Begin the HTML template
  html_content = """
  <!DOCTYPE html>
  <html lang="en">
  <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reconciliation Report</title>
    <style>
      body { font-family: Arial, sans-serif; margin: 20px; }
      h1 { color: #333; }
      h2 { color: #555; }
      table { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
      th, td { border: 1px solid #ccc; padding: 8px; text-align: left; }
      th { background-color: #f4f4f4; }
      .discrepancy { color: red; }
    </style>
  </head>
  <body>
    <h1>Reconciliation Status</h1>
    <p>Status: <strong>success</strong></p>
    <p>Message: <strong>Reconciliation completed successfully.</strong></p>

    <h2>Discrepancies</h2>
  """

  # Add the "Missing in Target" section
  html_content += """
  <h3>Missing in Target</h3>
  <table>
    <thead>
      <tr>
        <th>Record ID</th>
        <th>Name</th>
        <th>Date</th>
        <th>Amount</th>
      </tr>
    </thead>
    <tbody>
  """

  if reconciliation_data['missing_in_target']:
    for record in reconciliation_data['missing_in_target']:
      html_content += f"""
        <tr>
          <td>{record['record_id']}</td>
          <td>{record['data']['Name']}</td>
          <td>{record['data']['Date']}</td>
          <td>{record['data']['Amount']}</td>
        </tr>
      """
  else:
    # Add placeholder when missing_in_target is empty
    html_content += """
      <tr>
        <td colspan="4" style="text-align:center;">No records missing in target.</td>
      </tr>
    """

  html_content += """
    </tbody>
  </table>
  """

  # Add the "Missing in Source" section
  html_content += """
  <h3>Missing in Source</h3>
  <table>
    <thead>
      <tr>
        <th>Record ID</th>
        <th>Name</th>
        <th>Date</th>
        <th>Amount</th>
      </tr>
    </thead>
    <tbody>
  """

  if reconciliation_data['missing_in_source']:
      for record in reconciliation_data['missing_in_source']:
        html_content += f"""
          <tr>
            <td>{record['record_id']}</td>
            <td>{record['data']['Name']}</td>
            <td>{record['data']['Date']}</td>
            <td>{record['data']['Amount']}</td>
          </tr>
        """
  else:
    # Add placeholder when missing_in_source is empty
    html_content += """
      <tr>
        <td colspan="4" style="text-align:center;">No records missing in source.</td>
      </tr>
    """

  html_content += """
    </tbody>
  </table>
  """

  # Add the "Discrepancies in Matching Records" section
  html_content += """
  <h3>Discrepancies in Matching Records</h3>
  <table>
    <thead>
      <tr>
        <th>Record ID</th>
        <th>Source Name</th>
        <th>Source Date</th>
        <th>Source Amount</th>
        <th>Target Name</th>
        <th>Target Date</th>
        <th>Target Amount</th>
        <th>Discrepancy</th>
      </tr>
    </thead>
    <tbody>
  """

  if reconciliation_data['record_discrepancies']:
    for record in reconciliation_data['record_discrepancies']:
      discrepancies = []
      for field, discrepancy in record['discrepancy'].items():
        discrepancies.append(f"{field}: {discrepancy['source_value']} vs {discrepancy['target_name']}")

      discrepancy_str = ", ".join(discrepancies)

      html_content += f"""
        <tr>
          <td>{record['record_id']}</td>
          <td>{record['source_data']['Name']}</td>
          <td>{record['source_data']['Date']}</td>
          <td>{record['source_data']['Amount']}</td>
          <td>{record['target_data']['Name']}</td>
          <td>{record['target_data']['Date']}</td>
          <td>{record['target_data']['Amount']}</td>
          <td class="discrepancy">{discrepancy_str}</td>
        </tr>
      """
  else:
    # Add placeholder when there are no discrepancies
    html_content += """
      <tr>
        <td colspan="8" style="text-align:center;">No discrepancies found in matching records.</td>
      </tr>
    """

  html_content += """
    </tbody>
  </table>
  </body>
  </html>
  """

  return html_content.encode('utf-8')
