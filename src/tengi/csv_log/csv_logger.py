import csv
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple


class CsvLogger:
    def __init__(self, dir_path, file_name_prefix):
        self.dir_path = dir_path
        self.file_name_prefix = file_name_prefix

        self.date = None
        self.csv_file = None
        self.writer = None
        self.columns_set = None

    def write_row(self, row):
        self._ensure_writer(new_col_names=row.keys())
        self.writer.writerow(row)
        self.csv_file.flush()

    def _clean_state(self):
        if self.csv_file is not None:
            self.csv_file.close()
        self.csv_file = None
        self.writer = None
        self.columns_set = None

    def _ensure_writer(self, new_col_names) -> None:
        today = datetime.utcnow().date()
        if self.date != today:  # None or other date
            self._clean_state()

            self.date = today
            file_path, _ = self._find_date_latest_file(self.date)

            # More complex, check format change options also
            if file_path is not None:
                with open(file_path, 'r') as infile:
                    reader = csv.DictReader(infile)
                    old_col_names = reader.fieldnames

                if old_col_names is not None:
                    self.columns_set = set(old_col_names)
                    self.csv_file = open(file_path, 'a')
                    self.writer = csv.DictWriter(self.csv_file, fieldnames=old_col_names, dialect='excel')

        if (self.writer is None) or (not set(new_col_names).issubset(self.columns_set)):
            # Create a new file
            self._clean_state()
            file_path = self._create_date_next_file(today)
            self.columns_set = set(new_col_names)
            file_path.parent.mkdir(exist_ok=True, parents=True)
            self.csv_file = open(file_path, 'w')
            self.writer = csv.DictWriter(self.csv_file, fieldnames=new_col_names, dialect='excel')
            self.writer.writeheader()
            self.csv_file.flush()

    def _find_date_latest_file(self, date) -> Tuple[Optional[Path], Optional[int]]:
        prefix_w_date = f'{self.file_name_prefix}_{date}'
        files = list(self.dir_path.glob(f'{prefix_w_date}*'))
        if len(files) == 0:
            return None, None
        else:
            suffixes = [x.name.replace(prefix_w_date, '') for x in files]
            suffixes = [x.replace('.csv', '') for x in suffixes]
            num_suffixes = [x.replace('_', '') for x in suffixes]
            num_suffixes = [int(x) if x.isdigit() else None for x in num_suffixes]

            num_suffixes_w_value = [x for x in num_suffixes if x is not None]

            if len(num_suffixes_w_value) == 0:
                file_idx = suffixes.index('') if '' in suffixes else None
                if file_idx is not None:
                    return files[file_idx], None
                else:
                    return None, None
            else:
                variant_num = max(num_suffixes_w_value)
                file_idx = num_suffixes.index(variant_num)
                return files[file_idx], variant_num

    def _create_date_next_file(self, date) -> Path:
        cur_latest_file, latest_variant_num = self._find_date_latest_file(date)

        if cur_latest_file is None:
            file_name = f'{self.file_name_prefix}_{date}.csv'
        else:
            variant_num = latest_variant_num + 1 if latest_variant_num is not None else 1
            file_name = f'{self.file_name_prefix}_{date}_{variant_num}.csv'
        return self.dir_path / file_name
