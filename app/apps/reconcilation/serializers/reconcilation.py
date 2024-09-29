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

  def is_valid_string(self, value):
    return isinstance(value, str)

  def is_non_float_number(self, value):
      return isinstance(value, int)

  def validate_row(self, index, row, file_type):
    if pd.isna(row["ID"]):
      raise serializers.ValidationError({"error": f"ID value empty in {file_type} file for row in position {index + 1}"})
    else:
      id = row["ID"]

    if pd.isna(row["Name"]):
      raise serializers.ValidationError({"error": f"name value empty in {file_type} file for row with ID {row["ID"]}"})

    if pd.isna(row["Date"]):
      raise serializers.ValidationError({"error": f"date value empty in {file_type} file for row with ID {row["ID"]}"})
    else:
      source_date = str(row["Date"]).strip()

    if pd.isna(row["Amount"]):
      raise serializers.ValidationError({"error": f"amount value empty in {file_type} file for row with ID {row["ID"]}"})
    else:
      source_amount = row["Amount"]

    if not self.is_valid_number(id):
      raise serializers.ValidationError({"error": f"invalid ID type for row in position {index + 1} in {file_type} file"})

    if not self.is_non_float_number(id):
      raise serializers.ValidationError({"error": f"invalid ID type for row in position {index + 1} in {file_type} file"})

    if not self.is_valid_string(source_date) or not self.is_valid_date(source_date):
      raise serializers.ValidationError({"error": f"invalid date input in {file_type} file {source_date} from row with ID {row["ID"]}"})

    if not self.is_valid_number(source_amount):
      raise serializers.ValidationError({"error": f"invalid amount input in {file_type} file {source_amount} from row with ID {row["ID"]}"})

    return {
      "id": id,
      "source_name": str(row["Name"]).strip().lower(),
      "source_date": source_date,
      "source_amount": source_amount,
    }

  def validate_matching_record(self, index, matching_record):
    id = matching_record["ID"].iloc[0]

    if pd.isna(matching_record["Name"].iloc[0]):
      raise serializers.ValidationError({"error": f"name value empty in target file for row with ID {id}"})

    if pd.isna(matching_record["Date"].iloc[0]):
      raise serializers.ValidationError({"error": f"date value empty in target file for row with ID {id}"})
    else:
      source_date = str(matching_record["Date"].iloc[0]).strip()

    if pd.isna(matching_record["Amount"].iloc[0]):
      raise serializers.ValidationError({"error": f"amount value empty in target file for row with ID {id}"})
    else:
      source_amount = matching_record["Amount"].iloc[0]

    if not self.is_valid_string(source_date) or not self.is_valid_date(source_date):
      raise serializers.ValidationError({"error": f"invalid date input in target file {source_date} from row with ID {id}"})

    if not self.is_valid_number(source_amount):
      raise serializers.ValidationError({"error": f"invalid amount input in target file {source_amount} from row with ID {id}"})

    return {
      "id": id,
      "source_name": str(matching_record["Name"].iloc[0]).strip().lower(),
      "source_date": source_date,
      "source_amount": source_amount,
    }

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
      validated_source_row = self.validate_row(index, row, 'source')
      matching_record = target_df.loc[target_df["ID"] == validated_source_row["id"]]
      if matching_record["ID"].empty:
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
        validated_target_row = self.validate_matching_record(index, matching_record)

        source_name = validated_source_row["source_name"]
        source_date = validated_source_row["source_date"]
        source_amount = validated_source_row["source_amount"]

        t_name = matching_record["Name"].iloc[0]
        target_name = validated_target_row["source_name"]
        target_date = validated_target_row["source_date"]
        target_amount = validated_target_row["source_amount"]

        if source_name != target_name or source_date != target_date or source_amount != target_amount:
          record_discrepancy = {
            "record_id": row["ID"],
            "source_data": {
              "Name": row["Name"],
              "Date": source_date,
              "Amount": source_amount
            },
            "target_data": {
              "Name": matching_record["Name"].iloc[0],
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
      validated_source_row = self.validate_row(index, row, 'target')
      matching_record = source_df.loc[source_df["ID"] == validated_source_row["id"]]
      if matching_record["ID"].empty:
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
