from rest_framework import serializers
import pandas as pd
from datetime import datetime
import os

class FileSerializers(serializers.Serializer):
  source = serializers.FileField(allow_empty_file=False, required=True)
  target = serializers.FileField(allow_empty_file=False, required=True)
  format = serializers.CharField(required=True)

  def validate_file_extension(self, file):
      valid_extensions = ['.csv']
      ext = os.path.splitext(file.name)[1]
      if ext.lower() not in valid_extensions:
        raise serializers.ValidationError(f'Unsupported file extension. Allowed extensions are: {", ".join(valid_extensions)}')
      return file

  def validate_source(self, source):
    return self.validate_file_extension(source)

  def validate_target(self, target):
    return self.validate_file_extension(target)

  def validate_format(self, format):
    valid_return_format = ['csv', 'html', 'json']
    format = format.lower()
    if format not in valid_return_format:
      raise serializers.ValidationError(f'Unsupported return file format. Allowed return file formats are: {", ".join(valid_return_format)}')
    return format

  def validate_columns(self, file, file_type):
    columns = [
      "ID",
      "Name",
      "Date",
      "Amount",
    ]
    file_df = pd.read_csv(file)
    if list(file_df.columns) != columns:
      missing_cols = [col for col in columns if col not in file_df.columns]
      if missing_cols:
        raise serializers.ValidationError({"error": f"Missing columns: {', '.join(missing_cols)}, in {file_type} file"})

    return file_df

  def is_valid_date(self, date_string, date_format='%Y-%m-%d'):
    try:
        datetime.strptime(date_string, date_format)
        return True
    except ValueError:
        return False

  def is_valid_number(self, value):
      try:
          float(value)
          return True
      except ValueError:
          return False

  def is_empty(self, value):
    return value.strip() == ""

  def validate(self, data):
    source = data.get('source')
    target = data.get('target')
    source_df = self.validate_columns(source, 'source')
    target_df = self.validate_columns(target, 'target')

    return_data = {
      "missing_in_source": [],
      "missing_in_target": [],
      "record_discrepancies": []
    }

    for index, row in source_df.iterrows():
      matching_records = target_df.loc[target_df["ID"] == row["ID"]]
      if matching_records["ID"].empty:
        missing_record = {
          "record_id": row["ID"],
          "data": {
            "Name": row["Name"],
            "Date": row["Date"],
            "Amount": row["Amount"]
          }
        }
        return_data["missing_in_target"].append(missing_record)
      else:
        source_name = str(row["Name"]).strip().lower()
        source_date = row["Date"]
        source_amount = row["Amount"]
        t_name = matching_records["Name"].iloc[0]
        target_name = str(t_name).strip().lower()
        target_date = (matching_records["Date"].iloc[0])
        target_amount = matching_records["Amount"].iloc[0]

        if not self.is_valid_date(source_date):
          raise serializers.ValidationError({"error": f"invalid date input in source file {source_date} from row with ID {row["ID"]}"})

        if not self.is_valid_date(target_date):
          raise serializers.ValidationError({"error": f"invalid date input in target file {target_date} from row with ID {matching_records["ID"].iloc[0]}"})

        if not self.is_valid_number(source_amount):
          raise serializers.ValidationError({"error": f"invalid amount input in source file {source_amount} from row with ID {row["ID"]}"})

        if not self.is_valid_number(target_amount):
          raise serializers.ValidationError({"error": f"invalid amount input in target file {target_amount} from row with ID {matching_records["ID"].iloc[0]}"})

        if source_name != target_name or source_date != target_date or source_amount != target_amount:
          record_discrepancy = {
            "record_id": row["ID"],
            "source_data": {
              "Name": row["Name"],
              "Date": source_date,
              "Amount": source_amount
            },
            "target_data": {
              "Name": t_name,
              "Date": target_date,
              "Amount": target_amount
            },
            "discrepancy": {}
          }

          if source_name != target_name:
            record_discrepancy["discrepancy"]["Name"] = {
              "source_value": row["Name"],
              "target_name": t_name,
            }

          if source_date != target_date:
            record_discrepancy["discrepancy"]["Date"] = {
              "source_value": source_date,
              "target_name": target_date,
            }

          if source_amount != target_amount:
            record_discrepancy["discrepancy"]["Amount"] = {
              "source_value": source_amount,
              "target_name": target_amount,
          }

          return_data["record_discrepancies"].append(record_discrepancy)

    for index, row in target_df.iterrows():
      matching_records = source_df.loc[source_df["ID"] == row["ID"]]
      if matching_records["ID"].empty:
        missing_record = {
          "record_id": row["ID"],
          "data": {
            "Name": row["Name"],
            "Date": row["Date"],
            "Amount": row["Amount"]
          }
        }
        return_data["missing_in_source"].append(missing_record)

    return return_data

  def create(self, validated_data):
      return validated_data
