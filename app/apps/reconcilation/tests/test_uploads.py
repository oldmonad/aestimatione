from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from django.core.files.uploadedfile import SimpleUploadedFile
from django import urls
from .utils import (
  response_with_discrepanies_and_missing_data_in_json_format,
  response_with_discrepanies_and_missing_data_in_csv_format,
  response_with_discrepanies_and_missing_data_in_html_format
)

class TestUpload(APITestCase):
  def setUp(self):
    self.client = APIClient()
    self.upload_url = reverse('reconcilation:upload')

  def test_cannot_upload_source_file_with_incorrect_columns(self):
    """
    Should not be able to process source file with invalid columns
    """
    source_file_data = b"Name,Date,data\nJohn Doe,2023-01-01,3"
    target_file_data = b"target,sample,data\n4,5,6"

    source_file = SimpleUploadedFile("source.csv", source_file_data, content_type="text/csv")
    target_file = SimpleUploadedFile("target.csv", target_file_data, content_type="text/csv")

    response = self.client.post(self.upload_url, {
        'source': source_file,
        'target': target_file,
        'format': 'csv'
    }, format='multipart')

    self.assertEqual(response.status_code, 422)
    self.assertEqual(response.json()["error"], ['Missing columns: ID, Amount, in source file'])

  def test_cannot_upload_file_with_incorrect_columns(self):
    """
    Should not be able to process target file with invalid columns
    """
    source_file_data = b"ID,Name,Date,Amount\n1,John Doe,2023-01-01,100"
    target_file_data = b"ID,Name,Date\n4,5,6"

    source_file = SimpleUploadedFile("source.csv", source_file_data, content_type="text/csv")
    target_file = SimpleUploadedFile("target.csv", target_file_data, content_type="text/csv")

    response = self.client.post(self.upload_url, {
        'source': source_file,
        'target': target_file,
        'format': 'csv'
    }, format='multipart')

    self.assertEqual(response.status_code, 422)
    self.assertEqual(response.json()["error"], ['Missing columns: Amount, in target file'])

  def test_cannot_process_file_without_source_or_target_inputs(self):
    """
    Should not be able to proceed without file inputs
    """
    source_file = SimpleUploadedFile("source.csv", '', content_type="text/csv")
    target_file = SimpleUploadedFile("target.csv", '', content_type="text/csv")

    response = self.client.post(self.upload_url, {
        'source': source_file,
        'target': target_file,
        'format': 'csv'
    }, format='multipart')

    self.assertEqual(response.status_code, 422)
    self.assertEqual(response.json()["source"], ['The submitted file is empty.'])
    self.assertEqual(response.json()["target"], ['The submitted file is empty.'])

  def test_cannot_upload_with_invalid_format_input(self):
    """
    Should not be able to process with invalid return format input
    """
    source_file_data = b"ID,Name,Date,Amount\n1,John Doe,2023-01-01,100"
    target_file_data = b"ID,Name,Date,Amount\n1,John Doe,2023-01-01,100"

    source_file = SimpleUploadedFile("source.csv", source_file_data, content_type="text/csv")
    target_file = SimpleUploadedFile("target.csv", target_file_data, content_type="text/csv")

    response = self.client.post(self.upload_url, {
        'source': source_file,
        'target': target_file,
        'format': 'csvv'
    }, format='multipart')

    self.assertEqual(response.status_code, 422)
    self.assertEqual(response.json()["format"], ['Unsupported return file format. Allowed return file formats are: csv, html, json'])

  def test_cannot_upload_file_with_invalid_format(self):
    """
    Should not be able to process a file with invalid format
    """
    source_file_data = b"ID,Name,Date,Amount\n1,John Doe,2023-01-01,100"
    target_file_data = b"ID,Name,Date,Amount\n1,John Doe,2023-01-01,100"

    source_file = SimpleUploadedFile("source.html", source_file_data, content_type="text/html")
    target_file = SimpleUploadedFile("target.html", target_file_data, content_type="text/html")

    response = self.client.post(self.upload_url, {
        'source': source_file,
        'target': target_file,
        'format': 'csv'
    }, format='multipart')

    self.assertEqual(response.status_code, 422)
    self.assertEqual(response.json()["source"], ['Unsupported file extension. Allowed extensions are: .csv'])
    self.assertEqual(response.json()["target"], ['Unsupported file extension. Allowed extensions are: .csv'])

  def test_can_process_files_with_discrepancies_returned_in_in_json_format(self):
    """
    Should be able to process files with discrepancies and return in json format
    """
    source_file_data = b"ID,Name,Date,Amount\n1,John Doe,2023-01-03,100.5\n2,Jane Doe,2023-01-03,200.5"
    target_file_data = b"ID,Name,Date,Amount\n1,John Doe,2023-01-01,100\n3,David Doe,2023-02-03,300.5"

    source_file = SimpleUploadedFile("source.csv", source_file_data, content_type="text/csv")
    target_file = SimpleUploadedFile("target.csv", target_file_data, content_type="text/csv")

    response = self.client.post(self.upload_url, {
        'source': source_file,
        'target': target_file,
        'format': 'json'
    }, format='multipart')

    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.json(), response_with_discrepanies_and_missing_data_in_json_format())

  def test_can_process_files_with_invalid_date_data_in_source_file(self):
      """
      Should be able to process files with invalid date inputs
      """
      source_file_data = b"ID,Name,Date,Amount\n1,John Doe,2023,100.5\n2,Jane Doe,2023-01-03,200.5"
      target_file_data = b"ID,Name,Date,Amount\n1,John Doe,2023-01-01,100\n3,David Doe,2023-02-03,300.5"

      source_file = SimpleUploadedFile("source.csv", source_file_data, content_type="text/csv")
      target_file = SimpleUploadedFile("target.csv", target_file_data, content_type="text/csv")

      response = self.client.post(self.upload_url, {
          'source': source_file,
          'target': target_file,
          'format': 'json'
      }, format='multipart')

      self.assertEqual(response.status_code, 422)
      self.assertEqual(response.json()["error"], ["invalid date input in source file 2023 from row with ID 1"])

  def test_can_process_files_with_invalid_date_data_in_target_file(self):
      """
      Should be able to process files with invalid date inputs
      """
      source_file_data = b"ID,Name,Date,Amount\n1,John Doe,2023-01-01,100.5\n2,Jane Doe,2023-01-03,200.5"
      target_file_data = b"ID,Name,Date,Amount\n1,John Doe,2023,100\n3,David Doe,2023-02-03,300.5"

      source_file = SimpleUploadedFile("source.csv", source_file_data, content_type="text/csv")
      target_file = SimpleUploadedFile("target.csv", target_file_data, content_type="text/csv")

      response = self.client.post(self.upload_url, {
          'source': source_file,
          'target': target_file,
          'format': 'json'
      }, format='multipart')

      self.assertEqual(response.status_code, 422)
      self.assertEqual(response.json()["error"], ["invalid date input in target file 2023 from row with ID 1"])

  def test_can_process_files_with_invalid_amount_data_in_source_file(self):
      """
      Should be able to process files with invalid amount inputs
      """
      source_file_data = b"ID,Name,Date,Amount\n1,John Doe,2023-01-01,Fig\n2,Jane Doe,2023-01-03,200.5"
      target_file_data = b"ID,Name,Date,Amount\n1,John Doe,2023-01-01,100\n3,David Doe,2023-02-03,300.5"

      source_file = SimpleUploadedFile("source.csv", source_file_data, content_type="text/csv")
      target_file = SimpleUploadedFile("target.csv", target_file_data, content_type="text/csv")

      response = self.client.post(self.upload_url, {
          'source': source_file,
          'target': target_file,
          'format': 'json'
      }, format='multipart')

      self.assertEqual(response.status_code, 422)
      self.assertEqual(response.json()["error"], ["invalid amount input in source file Fig from row with ID 1"])

  def test_can_process_files_with_invalid_amount_data_in_target_file(self):
      """
      Should be able to process files with invalid amount inputs
      """
      source_file_data = b"ID,Name,Date,Amount\n1,John Doe,2023-01-01,100.5\n2,Jane Doe,2023-01-03,200.5"
      target_file_data = b"ID,Name,Date,Amount\n1,John Doe,2023-01-01,Fig\n3,David Doe,2023-02-03,300.5"

      source_file = SimpleUploadedFile("source.csv", source_file_data, content_type="text/csv")
      target_file = SimpleUploadedFile("target.csv", target_file_data, content_type="text/csv")

      response = self.client.post(self.upload_url, {
          'source': source_file,
          'target': target_file,
          'format': 'json'
      }, format='multipart')

      self.assertEqual(response.status_code, 422)
      self.assertEqual(response.json()["error"], ["invalid amount input in target file Fig from row with ID 1"])

  def test_can_process_files_with_discrepancies_returned_in_in_csv_format(self):
    """
    Should be able to process files with discrepancies and return in csv format
    """
    source_file_data = b"ID,Name,Date,Amount\n1,John Doe,2023-01-03,100.5\n2,Jane Doe,2023-01-03,200.5"
    target_file_data = b"ID,Name,Date,Amount\n1,John Doe,2023-01-01,100\n3,David Doe,2023-02-03,300.5"

    source_file = SimpleUploadedFile("source.csv", source_file_data, content_type="text/csv")
    target_file = SimpleUploadedFile("target.csv", target_file_data, content_type="text/csv")

    response = self.client.post(self.upload_url, {
        'source': source_file,
        'target': target_file,
        'format': 'csv'
    }, format='multipart')

    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.content, response_with_discrepanies_and_missing_data_in_csv_format())

  def test_can_process_files_with_discrepancies_returned_in_html_format(self):
    """
    Should be able to process files with discrepancies and return in csv format
    """
    source_file_data = b"ID,Name,Date,Amount\n1,John Doe,2023-01-03,100.5\n2,Jane Doe,2023-01-03,200.5"
    target_file_data = b"ID,Name,Date,Amount\n1,John Doe,2023-01-01,100\n3,David Doe,2023-02-03,300.5"

    source_file = SimpleUploadedFile("source.csv", source_file_data, content_type="text/csv")
    target_file = SimpleUploadedFile("target.csv", target_file_data, content_type="text/csv")

    response = self.client.post(self.upload_url, {
        'source': source_file,
        'target': target_file,
        'format': 'html'
    }, format='multipart')

    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.content, response_with_discrepanies_and_missing_data_in_html_format())

  def test_cannot_process_files_with_empty_name_column_for_source_file(self):
    """
    Should not be able to process files with empty name column for source file
    """
    source_file_data = b"ID,Name,Date,Amount\n1,,2023-01-01,100.5\n2,Jane Doe,2023-01-03,200.5"
    target_file_data = b"ID,Name,Date,Amount\n1,John Doe,2023-01-01,100\n3,David Doe,2023-02-03,300.5"

    source_file = SimpleUploadedFile("source.csv", source_file_data, content_type="text/csv")
    target_file = SimpleUploadedFile("target.csv", target_file_data, content_type="text/csv")

    response = self.client.post(self.upload_url, {
        'source': source_file,
        'target': target_file,
        'format': 'html'
    }, format='multipart')

    self.assertEqual(response.status_code, 422)
    self.assertEqual(response.json()["error"], ['name value empty in source file for row with ID 1'])

  def test_cannot_process_files_with_empty_id_column_for_source_file(self):
    """
    Should not be able to process files with empty id column for source file
    """
    source_file_data = b"ID,Name,Date,Amount\n,John Doe,2023-01-01,100.5\n2,Jane Doe,2023-01-03,200.5"
    target_file_data = b"ID,Name,Date,Amount\n1,John Doe,2023-01-01,100\n3,David Doe,2023-02-03,300.5"

    source_file = SimpleUploadedFile("source.csv", source_file_data, content_type="text/csv")
    target_file = SimpleUploadedFile("target.csv", target_file_data, content_type="text/csv")

    response = self.client.post(self.upload_url, {
        'source': source_file,
        'target': target_file,
        'format': 'html'
    }, format='multipart')

    self.assertEqual(response.status_code, 422)
    self.assertEqual(response.json()["error"], ['ID value empty in source file for row in position 1'])

  def test_cannot_process_files_with_empty_date_column_for_source_file(self):
    """
    Should not be able to process files with empty date column for source file
    """
    source_file_data = b"ID,Name,Date,Amount\n1,John Doe,,100.5\n2,Jane Doe,2023-01-03,200.5"
    target_file_data = b"ID,Name,Date,Amount\n1,John Doe,2023-01-01,100\n3,David Doe,2023-02-03,300.5"

    source_file = SimpleUploadedFile("source.csv", source_file_data, content_type="text/csv")
    target_file = SimpleUploadedFile("target.csv", target_file_data, content_type="text/csv")

    response = self.client.post(self.upload_url, {
        'source': source_file,
        'target': target_file,
        'format': 'html'
    }, format='multipart')

    self.assertEqual(response.status_code, 422)
    self.assertEqual(response.json()["error"], ['date value empty in source file for row with ID 1'])

  def test_cannot_process_files_with_empty_amount_column_for_source_file(self):
    """
    Should not be able to process files with empty amount column for source file
    """
    source_file_data = b"ID,Name,Date,Amount\n1,John Doe,2023-01-01,\n2,Jane Doe,2023-01-03,200.5"
    target_file_data = b"ID,Name,Date,Amount\n1,John Doe,2023-01-01,100\n3,David Doe,2023-02-03,300.5"

    source_file = SimpleUploadedFile("source.csv", source_file_data, content_type="text/csv")
    target_file = SimpleUploadedFile("target.csv", target_file_data, content_type="text/csv")

    response = self.client.post(self.upload_url, {
        'source': source_file,
        'target': target_file,
        'format': 'html'
    }, format='multipart')

    self.assertEqual(response.status_code, 422)
    self.assertEqual(response.json()["error"], ['amount value empty in source file for row with ID 1'])

  def test_cannot_process_files_with_float_number_id_type_column_for_source_file(self):
    """
    Should not be able to process files with float number type in id column for source file
    """
    source_file_data = b"ID,Name,Date,Amount\n1.5,John Doe,2023-01-01,100\n2,Jane Doe,2023-01-03,200.5"
    target_file_data = b"ID,Name,Date,Amount\n1,John Doe,2023-01-01,100\n3,David Doe,2023-02-03,300.5"

    source_file = SimpleUploadedFile("source.csv", source_file_data, content_type="text/csv")
    target_file = SimpleUploadedFile("target.csv", target_file_data, content_type="text/csv")

    response = self.client.post(self.upload_url, {
        'source': source_file,
        'target': target_file,
        'format': 'html'
    }, format='multipart')

    self.assertEqual(response.status_code, 422)
    self.assertEqual(response.json()["error"], ['invalid ID type for row in position 1 in source file'])

  def test_cannot_process_files_with_invalid_id_type_column_for_source_file(self):
    """
    Should not be able to process files with invalid id type in id column for source file
    """
    source_file_data = b"ID,Name,Date,Amount\nFig,John Doe,2023-01-01,100\n2,Jane Doe,2023-01-03,200.5"
    target_file_data = b"ID,Name,Date,Amount\n1,John Doe,2023-01-01,100\n3,David Doe,2023-02-03,300.5"

    source_file = SimpleUploadedFile("source.csv", source_file_data, content_type="text/csv")
    target_file = SimpleUploadedFile("target.csv", target_file_data, content_type="text/csv")

    response = self.client.post(self.upload_url, {
        'source': source_file,
        'target': target_file,
        'format': 'html'
    }, format='multipart')

    self.assertEqual(response.status_code, 422)
    self.assertEqual(response.json()["error"], ['invalid ID type for row in position 1 in source file'])

  def test_cannot_process_files_with_empty_name_column_for_target_file(self):
    """
    Should not be able to process files with empty name column for target file
    """
    source_file_data = b"ID,Name,Date,Amount\n1,John Doe,2023-01-01,100.5\n2,Jane Doe,2023-01-03,200.5"
    target_file_data = b"ID,Name,Date,Amount\n1,,2023-01-01,100\n3,David Doe,2023-02-03,300.5"

    source_file = SimpleUploadedFile("source.csv", source_file_data, content_type="text/csv")
    target_file = SimpleUploadedFile("target.csv", target_file_data, content_type="text/csv")

    response = self.client.post(self.upload_url, {
        'source': source_file,
        'target': target_file,
        'format': 'html'
    }, format='multipart')

    self.assertEqual(response.status_code, 422)
    self.assertEqual(response.json()["error"], ['name value empty in target file for row with ID 1'])

  def test_cannot_process_files_with_empty_id_column_for_target_file(self):
    """
    Should not be able to process files with empty id column for target file
    """
    source_file_data = b"ID,Name,Date,Amount\n1,John Doe,2023-01-01,100.5\n2,Jane Doe,2023-01-03,200.5"
    target_file_data = b"ID,Name,Date,Amount\n,John Doe,2023-01-01,100\n3,David Doe,2023-02-03,300.5"

    source_file = SimpleUploadedFile("source.csv", source_file_data, content_type="text/csv")
    target_file = SimpleUploadedFile("target.csv", target_file_data, content_type="text/csv")

    response = self.client.post(self.upload_url, {
        'source': source_file,
        'target': target_file,
        'format': 'html'
    }, format='multipart')

    self.assertEqual(response.status_code, 422)
    self.assertEqual(response.json()["error"], ['ID value empty in target file for row in position 1'])

  def test_cannot_process_files_with_empty_date_column_for_target_file(self):
    """
    Should not be able to process files with empty date column for target file
    """
    source_file_data = b"ID,Name,Date,Amount\n1,John Doe,2023-01-01,100.5\n2,Jane Doe,2023-01-03,200.5"
    target_file_data = b"ID,Name,Date,Amount\n1,John Doe,,100\n3,David Doe,2023-02-03,300.5"

    source_file = SimpleUploadedFile("source.csv", source_file_data, content_type="text/csv")
    target_file = SimpleUploadedFile("target.csv", target_file_data, content_type="text/csv")

    response = self.client.post(self.upload_url, {
        'source': source_file,
        'target': target_file,
        'format': 'html'
    }, format='multipart')

    self.assertEqual(response.status_code, 422)
    self.assertEqual(response.json()["error"], ['date value empty in target file for row with ID 1'])

  def test_cannot_process_files_with_empty_amount_column_for_target_file(self):
    """
    Should not be able to process files with empty amount column for target file
    """
    source_file_data = b"ID,Name,Date,Amount\n1,John Doe,2023-01-01,100\n2,Jane Doe,2023-01-03,200.5"
    target_file_data = b"ID,Name,Date,Amount\n1,John Doe,2023-01-01,\n3,David Doe,2023-02-03,300.5"

    source_file = SimpleUploadedFile("source.csv", source_file_data, content_type="text/csv")
    target_file = SimpleUploadedFile("target.csv", target_file_data, content_type="text/csv")

    response = self.client.post(self.upload_url, {
        'source': source_file,
        'target': target_file,
        'format': 'html'
    }, format='multipart')

    self.assertEqual(response.status_code, 422)
    self.assertEqual(response.json()["error"], ['amount value empty in target file for row with ID 1'])

  def test_cannot_process_files_with_float_number_id_type_column_for_target_file(self):
    """
    Should not be able to process files with float number type id column for target file
    """
    source_file_data = b"ID,Name,Date,Amount\n1,John Doe,2023-01-01,100\n2,Jane Doe,2023-01-03,200.5"
    target_file_data = b"ID,Name,Date,Amount\n1.5,John Doe,2023-01-01,100\n3,David Doe,2023-02-03,300.5"

    source_file = SimpleUploadedFile("source.csv", source_file_data, content_type="text/csv")
    target_file = SimpleUploadedFile("target.csv", target_file_data, content_type="text/csv")

    response = self.client.post(self.upload_url, {
        'source': source_file,
        'target': target_file,
        'format': 'html'
    }, format='multipart')

    self.assertEqual(response.status_code, 422)
    self.assertEqual(response.json()["error"], ['invalid ID type for row in position 1 in target file'])

  def test_cannot_process_files_with_invalid_id_type_column_for_target_file(self):
    """
    Should not be able to process files with invalid id type for target file
    """
    source_file_data = b"ID,Name,Date,Amount\n1,John Doe,2023-01-01,100\n2,Jane Doe,2023-01-03,200.5"
    target_file_data = b"ID,Name,Date,Amount\nFig,John Doe,2023-01-01,100\n3,David Doe,2023-02-03,300.5"

    source_file = SimpleUploadedFile("source.csv", source_file_data, content_type="text/csv")
    target_file = SimpleUploadedFile("target.csv", target_file_data, content_type="text/csv")

    response = self.client.post(self.upload_url, {
        'source': source_file,
        'target': target_file,
        'format': 'html'
    }, format='multipart')

    self.assertEqual(response.status_code, 422)
    self.assertEqual(response.json()["error"], ['invalid ID type for row in position 1 in target file'])
