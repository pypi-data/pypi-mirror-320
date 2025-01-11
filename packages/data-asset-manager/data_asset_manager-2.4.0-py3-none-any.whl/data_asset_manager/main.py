from io import BytesIO
from log_manager import LogManager
import os
import pandas as pd
from stop_watch import StopWatch
import traceback
from zipfile import ZipFile



class FileSpecError(ValueError):
    err_dict = {'client_id': ['File Header Row Error',
                              'Error found in File Spec. \nExpected ClientId {} but found {}'],
                'col_count': ['Column Mismatch',
                              'The number of columns found does not match the number specified. \nExpected {} columns, but found {}'],
                'fnf_error': ['File Not Found Error',
                            '{}:\n{}'],
                'hdr_row': ['File Header Row Error',
                            'Error found in file header row. \nExpected\n   {} \nbut found\n   {}'],
                'sasin_fields': ['SAS Fields Error',
                               'Error found in SasField definitions. \nExpected {} field names but found {}'],
                'no_data': ['Data Error',
                            'No readable data has been found in {}{}'],
                'data_types': ['Data Type Error',
                               'Expected data types {}\nError found in row {}'],
                'type_check': ['Data Type Validation Error',
                               'Unable to validate data types for Fields {}\nand Types {}'],
                'fld_ren_ne': ['Blob Error',
                               'Field rename: "{}" does not exist in {}'],
                'fld_ren_ae': ['Blob Error',
                               'Field rename: "{}" already exists in {}'],
                'fld_drop': ['Blob Error',
                             'Field delete: "{}" does not exist in {}']}

    def __init__(self, err_vars):
        """
Raise this when there's a file specification error
        :param err_vars:
        """
        self.err_code = err_vars[0]
        self.error = ''
        self.description = ''
        self.expected_value = ''
        self.found_value = ''
        self.set_error(err_vars)

    def __str__(self):
        return '\n'.join(['FileSpecError:', self.error, self.description])

    def set_error(self, err_vars):
        self.expected_value = err_vars[1]
        if self.err_code == 'data_types':
            self.expected_value = '|'.join(self.expected_value)

        self.found_value = err_vars[2]

        err_vals = self.err_dict.get(self.err_code)
        if err_vals:
            self.error = err_vals[0]
            err_str = err_vals[1]
        else:
            self.error = 'UnkownErrorType'
            err_str = 'An unexpected error has been found\n  Error type: ' + self.err_code + '\n  Param 1: 1.  {}\n  Param  2:  {}'
        arg_str = ''
        if len(err_vars) > 3:
            for x in err_vars[3]:
                arg_str += '\n' + x + ': ' + err_vars[3][x]

        self.description = err_str.format(self.expected_value, self.found_value) + arg_str


class Trigger:  # v1.0.1
    def __init__(self):
        """
When the Blob class was created, Pandas had an unexplained habit of calling lambda functions twice on the first row of
a DataFrame. There are many occasions where that is undesirable. This is a simple workaround.
Using:-<br>
    row_no = Trigger()<br>
    self.data_frame[column_name] = self.data_frame.apply(lambda row: function(row, row_no), axis=1)<br>
You can test for row_no.is_first() in your function and skip if True.

        """
        self.first = True

    def is_first(self):
        """
        :return: True if this is the first time we've seen the first row.
        """
        return_val = self.first
        self.first = False
        return return_val


class Blob:  # v 2.4.0
    idx = None

    def __init__(self, ini, file_type, log: LogManager, name=None, segment=False, file_spec_override=None):
        """
A container for managing Pandas DataFrames
        :param ini: The app_setup module, which stores all the job related variables
        :param file_type: The name of the template to use. (Templates are set in app_setup.py -> main_specs)
        :param log: A LogManager object used for application level logging. (Read/write logging is managed by the
        inbuilt rw_log)
        :param name: A friendly name for the dataset
        :param segment: Not yet implemented
        """
        self.rw_log = LogManager(display=False)
        if ini.verbose_logging:
            self.rw_log.start_text_logging(ini.application_log)
        self.ini = ini
        self.timer = StopWatch()
        self.segment = segment
        self.file_type = file_type
        file_specs = ini.job_specs[file_type]
        # print('*** DataAssetManger.Blob.__init__.file_specs:', file_specs)
        if file_spec_override:
            file_specs = {key: file_spec_override.get(key, val) for key, val in file_specs.items()}
        self.log = log
        # self.log.create_entry([file_specs, name, segment])
        self.data_frame = pd.DataFrame()
        self.header_check_style = 'loose'
        self.loaded = False
        self.processed = False
        self.row_count = 0
        self.index_min = 0
        self.index_max = 0
        self.file_specs = file_specs
        self.name = file_specs['Description'] if name is None else name
        self.display_name = file_type + '|' + self.name
        if self.name == 'Frame':
            self.file_name = 'Name not set'
            self.file_extn = 'csv'
            self.file_path = 'Path not set'
            self.archived_name = 'Archive name not set'
            self.df_fields = 'Fields not set'
            self.url = 'URL not set'
            self.status = 'Empty'
            self.volatile = 'False'
        else:
            self.file_name = file_specs['FileName']
            self.file_extn = file_specs['FileName'].split('.')[-1]
            self.separator = self.get_file_spec('Separator', ini.default_delimiter)
            self.df_fields: dict = file_specs['Columns']
            self.field_names = list(self.df_fields.keys())
            if file_specs['IndexColumn']:
                self.idx = file_specs['IndexColumn']
                for icol in self.idx:
                    if icol in self.field_names:
                        self.field_names.remove(icol)
                # self.field_names = self.field_names[1:]
            self.header = None if int(float(file_specs['Header'])) < 0 else int(float(file_specs['Header']))
            self.file_path = file_specs['Location']
            if segment:
                self.file_path = os.path.join(self.file_path, ini.segment_folders, self.name)
            self.volatile = self.get_file_spec('Volatile', True)
            self.archived_name = self.get_file_spec('ArchivedName', self.file_name)
            self.data_types = self.df_fields
            # address_fields = self.field_names if file_specs['AddressFields'] == '' else file_specs['AddressFields']
            self.address_fields = self.get_file_spec('AddressFields', self.field_names)
            self.status = 'Instantiated'
            self.url = os.path.join(self.file_path, self.file_name)

    def __repr__(self):
        out_str = '\n==================\nFile Specification\n------------------\n'
        out_str = out_str + f'Name: {self.name}\n'
        out_str = out_str + f'File Name: {self.file_name}\n'
        out_str = out_str + f'File Type: {self.file_type}\n'
        out_str = out_str + f'Field Delimiter: {self.separator}\n'
        out_str = out_str + f'Location: {self.file_path}\n'
        out_str = out_str + f'Archived Name: {self.archived_name}\n'
        out_str = out_str + f'Table Fields:-\n{self.df_fields}\n==================\n'
        if self.loaded:
            out_str += f'Row count: {self.row_count}\n{self.data_frame.iloc[0]}\n\n'
        else:
            out_str += self.name + ' is empty\n\n'

        return out_str

    def get_file_spec(self, spec: str, default_val: object = ''):
        out_val = self.file_specs.get(spec)
        if not out_val or out_val == '':
            out_val = default_val
        return out_val

    def read_file(self, url=None, skiprows=None, rows=None, unicode_escape=False, archive=None):
        # First check to see if we're reading from a compressed folder
        if archive:
            location = archive.get('location')
            zip_name = archive.get('zip_name')
            file_name = archive.get('file_list')
            password = archive.get('password')
            zip_url = str(os.path.join(location, zip_name))

            if not os.path.exists(zip_url):
                msg = ['No file available', zip_url, 'No data loaded into blob']
                self.log.create_entry(msg, new_lines=True)
                return msg
            input_zip = ZipFile(zip_url)
            file_path = zip_url
            file_stream = input_zip.read(file_name, pwd=password)
            read_url = BytesIO(file_stream)
        else:
            read_url = self.url if url is None else url
            file_path = read_url
            if not os.path.exists(file_path):
                msg = ['No file available', file_path, 'No data loaded into blob']
                self.log.create_entry(msg, new_lines=True)
                return msg

        field_names = self.idx.copy() if isinstance(self.idx, list) else [self.idx]
        if self.idx and self.idx[0]:
            field_names.extend(self.field_names)
        else:
            field_names = self.field_names

        try:
            # print('DAM.read_file', self.file_extn)
            if self.file_extn.lower() in ['csv', 'txt', 'tsv', 'idx']:
                if unicode_escape:
                    df = pd.read_csv(read_url, sep=self.separator, header=self.header, names=field_names, nrows=rows, on_bad_lines='warn',#lambda x: x[:len(self.header)],
                                     skiprows=skiprows, dtype=self.data_types, index_col=self.idx,
                                     encoding='unicode_escape', engine='python')
                else:
                    df = pd.read_csv(read_url, sep=self.separator, header=self.header, names=field_names, nrows=rows, on_bad_lines='warn',#lambda x: x[:len(self.header)], engine='python',
                                     skiprows=skiprows, dtype=self.data_types, index_col=self.idx,
                                     encoding_errors='ignore')
            elif self.file_extn.lower() in ['xls', 'xlsx']:
                df = pd.read_excel(read_url, nrows=rows, skiprows=skiprows)
            else:
                df = None
            self.load_data(df)
        except KeyError:
            msg = ['Key error', self, 'No data loaded into blob']
            self.log.create_entry(msg, new_lines=True)
            return msg
        except ValueError:
            e = traceback.format_exc()
            msg = ['FileSpec error', self, 'No data loaded into blob']
            self.log.create_entry(msg, new_lines=True)
            self.log.create_entry(e, new_lines=True)
            return msg
        except FileNotFoundError:
            e = traceback.format_exc()
            self.log.create_entry(e, new_lines=True)
            msg = ['Read error', file_path, 'No data loaded into blob']
            self.log.create_entry(msg, new_lines=True)
            return msg

        self.log.create_entry(['Blob Input', self.file_type, self.row_count, file_path])
        self.rw_log.create_entry(['Read', self.file_type, self.name, file_path, self.row_count])
        # return ['File loaded', self, 'Data loaded into blob']
        return self.row_count

    def file_iterator(self, chunksize, url=None, unicode_escape=False, archive=None):
        if archive:
            location = archive.get('location')
            zip_name = archive.get('zip_name')
            file_name = archive.get('file_list')
            password = archive.get('password')
            zip_url = os.path.join(location, zip_name)

            if not os.path.exists(zip_url):
                msg = ['No file available', zip_url, 'No data loaded into blob']
                self.log.create_entry(msg, new_lines=True)
                return msg
            input_zip = ZipFile(zip_url)
            file_path = zip_url
            file_stream = input_zip.read(file_name, pwd=password)
            read_url = BytesIO(file_stream)

        else:
            read_url = self.url if url is None else url
            file_path = read_url
            if not os.path.exists(file_path):
                msg = ['No file available', file_path, 'No data loaded into blob']
                self.log.create_entry(msg, new_lines=True)
                return msg
        field_names = self.idx.copy() if isinstance(self.idx, list) else [self.idx]
        if self.idx:
            field_names.extend(self.field_names)
        else:
            field_names = self.field_names
        try:
            if unicode_escape:
                df = pd.read_csv(read_url, sep=self.separator, header=self.header, names=field_names,
                                 chunksize=chunksize, dtype=self.data_types, index_col=self.idx,
                                 encoding='unicode_escape', engine='python')
            else:
                df = pd.read_csv(read_url, sep=self.separator, header=self.header, names=field_names,
                                 chunksize=chunksize, dtype=self.data_types, index_col=self.idx,
                                 encoding_errors='ignore')
            return df
        except KeyError:
            msg = ['Key error', self, 'No data loaded']
            self.log.create_entry(msg, new_lines=True)
            return msg
        except ValueError:
            e = traceback.format_exc()
            msg = ['FileSpec error', self, 'No data loaded']
            self.log.create_entry(msg, new_lines=True)
            self.log.create_entry(e, new_lines=True)
            return msg
        except FileNotFoundError:
            e = traceback.format_exc()
            self.log.create_entry(e, new_lines=True)
            msg = ['Read error', file_path, 'No data loaded']
            self.log.create_entry(msg, new_lines=True)
            return msg

    def load_data(self, df, copy=False):
        if df.shape[0] > 0:
            self.data_frame = df.copy() if copy else df
            self.data_frame.fillna('', inplace=True)
            self.index_min = self.data_frame.index.min()
            self.row_count = df.shape[0]
            self.index_max = self.data_frame.index.max()
            self.loaded = (self.row_count > 0)
            return self.index_max
        else:
            self.index_min = 0
            self.row_count = 0
            self.index_max = 0
            self.data_frame = pd.DataFrame()
            self.loaded = False
            return 0

    def write_file(self, url=None, out_fields: list = None, mode='w', make_dir=False, backup=False):
        if out_fields is None:
            out_fields = self.field_names
        header = mode == 'w' and self.header is not None
        out_url = self.url if url is None else url
        index = self.idx is not None
        idx_name = None
        if index and self.idx in out_fields:
            idx_name = self.idx
            out_fields.remove(self.idx)
        elif out_fields[0] == 'CallIndex':
            idx_name = out_fields[1]
            self.data_frame.index.rename(idx_name, inplace=True)
            out_fields = out_fields[2:]
            index = True
        if self.data_frame.shape[0] > 0:
            self.log.create_entry(['Blob Output', self.file_type,
                                   self.row_count, out_url])
            if mode == 'w' and backup and os.path.exists(out_url):
                inc = 1
                while os.path.exists(out_url.replace('.', f'_{inc}.')):
                    inc += 1
                os.rename(out_url, out_url.replace('.', f'_{inc}.'))
            if make_dir and url is None and not os.path.exists(self.file_path):
                os.makedirs(self.file_path)
            try:
                self.data_frame.to_csv(out_url, sep=self.separator, columns=out_fields, header=header, index=index,
                                       index_label=idx_name, mode=mode, encoding='utf-8-sig')
            except KeyError as e:
                err_msg = 'WriteError: ' + str(self)
                raise FileSpecError(['fld_drop', e.args[0], self.field_names])
        else:
            self.log.create_entry(['Blob Output', self.file_type, 'No data', out_url])
        self.rw_log.create_entry(['Write', self.file_type, self.name, out_url, self.row_count])

    def update_url(self, place_holder=None, var_string=None, file_name=None, file_path=None, permanent=False):
        path = self.file_path if file_path is None else file_path
        name = self.file_name if file_name is None else file_name
        if place_holder is not None:
            path = path.replace(place_holder, var_string)
            name = name.replace(place_holder, var_string)
        out_url = os.path.join(path, name)
        if permanent:
            self.file_path = path
            self.file_name = name
            self.url = out_url
        return out_url

    def copy(self, name=None, file_name=None):
        """
Creates a new empty instance of the blob using the initial file specs.
        :param name: str
        :param file_name: str
        :return: Blob
        """
        new_file = Blob(self.ini, self.file_type, self.log, name=name, segment=self.segment)
        if file_name is not None:
            new_file.update_url(file_name=file_name, permanent=True)
        return new_file

    def clone(self, name=None, file_name=None):
        """
Creates a new instance of the blob using the initial file specs, with a copy of the source DataFrame
        :param name: str
        :param file_name: str
        :return: Blob
        """
        if not file_name:
            file_name = self.file_name
        new_name = self.name if name is None else name
        new_blob = Blob(self.ini, self.file_type, self.log, name=new_name, segment=self.segment)
        new_blob.update_url(file_name=file_name, file_path=self.file_path, permanent=True)
        if self.row_count > 0:
            new_blob.load_data(self.data_frame, copy=True)
        return new_blob

    def merge_data(self, in_data_frames, inc_self=True):
        if isinstance(in_data_frames, list):
            df_list = in_data_frames
            if inc_self and self.loaded:
                df_list.insert(0, self.data_frame)
        else:
            df_list = [self.data_frame, in_data_frames]
        self.load_data(pd.concat(df_list, sort=False))
        return len(df_list)

    def merge_blobs(self, blob_list, inc_self=True):
        if isinstance(blob_list, list):
            df_list = []
            for blob in blob_list:
                if blob.data_frame.shape[0] > 0:
                    df_list.append(blob.data_frame)
                    self.merge_data(df_list, inc_self)
        else:
            self.merge_data(blob_list.data_frame, inc_self)
        return self

    def debug_write(self, file_name_suffix):
        new_url = self.update_url(file_name=self.file_name.replace('.', '_' + file_name_suffix + '.'))
        self.write_file(url=new_url)

    def reset(self, drop=False):
        if drop and self.volatile:
            if os.path.exists(self.url):
                os.remove(self.url)
        self.__init__(self.ini, self.file_type, self.log, name=self.name, segment=self.segment)
        return self

    def reshape(self, new_fields: dict, transform_method=None, inplace=False, **kwargs):
        """
Reshaping a Blob changes the column headings and types in the metadata, it does not change the DataFrame unless
inplace=True
        :param new_fields:
        :param transform_method:
        :param inplace:
        :param kwargs:
        """
        self.df_fields = new_fields
        self.field_names = list(self.df_fields.keys())
        self.data_types = self.df_fields

        if transform_method:
            self.transform(transform_method, **kwargs)
        elif inplace:
            self.load_data(self.data_frame[self.field_names], copy=True)

    def dedupe(self, columns):
        self.data_frame.drop_duplicates(subset=columns, keep='first', inplace=True)
        self.row_count = self.data_frame.shape[0]

    def purge(self, in_blob, column=None):
        if column is None:
            self.load_data(self.data_frame[~self.data_frame.index.isin(in_blob.data_frame.idx)])
        else:
            self.load_data(self.data_frame[~self.data_frame[column].isin(in_blob.data_frame[column])])

    def filter(self, column, value=None, operand='>'):
        # c = self.row_count
        try:
            if value is None:
                self.load_data(self.data_frame[self.data_frame[column] != ''].copy())
                # self.log.create_entry(['Filtered rows on', column + ' = empty', c, self.row_count])
            else:
                self.load_data(self.data_frame[eval('self.data_frame[column] ' + operand + ' value')].copy())
                # self.log.create_entry(['Filtered rows on', column + ' > ' + str(value), c, self.row_count])
        except TypeError as e:
            err_msg = 'FilterError:'  # + ddf(self.data_frame, column, 10, 10)
            raise Exception(err_msg) from e

    def reindex(self, idx_start):
        self.data_frame.index = range(idx_start, idx_start + self.row_count)

    def sort(self, sort_fields: list = None, sort_order: list = None):
        if sort_fields is None:
            if sort_order is None or len(sort_order) != 1:
                order = True
            else:
                order = sort_order[0]
            self.data_frame.sort_index(ascending=order, inplace=True)
        elif sort_order is not None and len(sort_order) == len(sort_fields):
            self.data_frame.sort_values(by=sort_fields, ascending=sort_order, inplace=True)
        else:
            self.data_frame.sort_values(by=sort_fields, inplace=True)

    def apply(self, function, *args):
        df = self.data_frame.apply(lambda r: function(r, *args), axis=1)
        self.load_data(df)
        return self

    def transform(self, transform_method, **kwargs):
        """
Perform a function as a method.
        :param transform_method: The function to be performed MUST return a DataFrame
        :param kwargs: Any arguments required by the function can be passed as keyword args. Use write=True to
        automatically output the data to the default output file.
        """
        df = transform_method(self.data_frame, **kwargs)
        self.load_data(df)
        if kwargs.get('write'):
            self.write_file()

    def create_column(self, column_name, function=None, data_type='str'):
        """
Adds a new column to the data. If a function is provided, it will be used to populate the DataFrame column. If a
data_type is provided, the default value for that type will be used.
        :param column_name: str
        :param function: function or method to be used on each row, to populate the field
        :param data_type: dtype
        """
        if function:
            fr = Trigger()
            self.data_frame[column_name] = self.data_frame.apply(lambda row: function(row, fr), axis=1)
        else:
            self.field_names.append(column_name)
            self.df_fields[column_name] = data_type
            if data_type == 'int':
                self.data_frame[column_name] = 0
            else:
                self.data_frame[column_name] = ''

    def drop_column(self, column_name):
        """
Removes the passed field from the metadata and the DataFrame
        :param column_name: str
        """
        if column_name not in self.field_names:
            raise FileSpecError(['fld_drop', column_name, self.field_names])

        self.df_fields.pop(column_name)
        self.field_names.remove(column_name)
        if self.loaded and column_name in self.data_frame.columns:
            self.data_frame.drop(columns=column_name, inplace=True)

    def rename_column(self, old_column_name, new_column_name):
        """
Renames a field in both the metadata and the DataFrame. Changing data types is not supported.
        :param old_column_name: str
        :param new_column_name: str
        """
        file_spec = {'New Field Name': new_column_name, 'Name': self.name, 'File Name': self.file_name,
                     'File Type': self.file_type, 'Location': self.file_path, 'Row Count': str(self.row_count),
                     'Table': str(self.data_frame.columns)}
        if old_column_name not in self.field_names:
            raise FileSpecError(['fld_ren_ne', old_column_name, self.field_names, file_spec])

        if new_column_name in self.field_names:
            raise FileSpecError(['fld_ren_ae', old_column_name, self.field_names, file_spec])

        self.df_fields = {new_column_name if k == old_column_name else k: v for k, v in self.df_fields.items()}
        self.field_names = [new_column_name if v == old_column_name else v for v in self.field_names]
        self.data_frame.rename(columns={old_column_name: new_column_name}, inplace=True)

    def df_layout(self, layout_file):
        """
Generates a File Layout in a CSV file, based on the metadata, not the DataFrame
        :param layout_file: The full URL for the output file
        :return:
        """

        def __check_len(field_name):
            try:
                if isinstance(self.data_frame[field_name], str):
                    return str(max(self.data_frame[field_name], key=len))
                else:
                    return 'int'
            except ValueError:
                return 'NULL'

        out_fields = self.df_fields if self.idx == '' else self.df_fields[1:]
        out_fields['MaxLen'] = out_fields.apply(lambda row: __check_len(row['name']), axis=1)
        out_fields.to_csv(layout_file, mode='a', sep='|', header=True, index=True)

        return str(out_fields)

    def html(self):
        out_str = '<table>\n'
        out_str = out_str + '<tr><th colspan=2 style="text-align:left;font-size:1.2em;">' + self.name + '</th></tr>\n'
        out_str = out_str + '<tr><td>File Name:</td><td>' + self.archived_name + '</td></tr>\n'
        out_str = out_str + '<tr><td>Field Names:-</td><td>* See layout tables below</td></tr>\n'
        if self.loaded:
            out_str += '<tr><td>Row count:</td><td>' + '{:,}'.format(self.row_count) + '</td></tr>\n'
        else:
            out_str += '<tr><td colspan=2>' + self.name + ' is empty</td></tr>\n'

        out_str += '</table>\n'
        return out_str
