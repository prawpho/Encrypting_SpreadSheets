import gspread, argparse, base64, re, string, random, sys, pathlib, json
import pandas as pd
from cryptography.fernet import Fernet
from tqdm import tqdm
from datetime import datetime
tqdm.pandas()

# my module
# sys.path.insert(0, r'D:\prawploy.p')
# from module.initial import LineNotify

class ProtectData:
    def __init__(self, key, gspread_url=None, data = None, service_account=None, salt=None, path_save_key=None) -> None: 
        self.key = str(key)+'='
        self.gspread_url = gspread_url
        self.data = data
        self.fernet = object()
        if service_account is not None: self.service_account = gspread.service_account(filename=service_account)
        else: self.service_account = None
        self.sheet = object()
        self.worksheet = object()
        self.salt = salt
        self.path_key = path_save_key
        
    # def start_fernet(self,):
    #     self.fernet = Fernet(self.key)
        
    def is_gspread(self, sheetname=None):
        if (self.gspread_url is not None) and (self.data is None):
            self._transform_gspread(sheetname)
          
        assert self.data is not None, "Your input is not correct"    
        # assert (self.data is None) and (self.gspread_url is None), "Your input is empty"
        assert ((self.gspread_url is not None) and (self.data is not None)), "Put only one source of data"     
        
    
    def _text_to_string(self, value):
        if isinstance(value, datetime):
            return value.strftime("%Y-%m-%d")
        return str(value)
    
    def _is_encrypted(self, text):
        return isinstance(text, str) and text.startswith("ENC:")
    
    def _hash_key(self, key_bytes):
        return [(byte + index) % 256 for index, byte in enumerate(key_bytes)]
        
    def _generate_hmac(self, data, key):
        _key_hash = self._hash_key(key)
        return [(byte ^ _key_hash[index % len(_key_hash)]) & 0xff for index, byte in enumerate(data)][:16]
    
    def _generate_salt(self, length):
        return [random.randint(0, 255) for _ in range(length)]
        
    def _transform_gspread(self, sheetname):
        self.sheet = self.service_account.open_by_url(self.gspread_url)
        
        if sheetname is None:
            self.worksheet = self.sheet.get_worksheet(0)
        else:
            self.worksheet = self.sheet.worksheet(sheetname)
            
        _data_sheets = self.worksheet.get_all_values()
        self.data = pd.DataFrame(_data_sheets[1:], columns=_data_sheets[0])
        
    def _normalize_bytes(self, bytes_list):
        return [byte & 0xff for byte in bytes_list]
    
    def _arrays_equal(self, array1, array2):
        return array1 == array2
        
    def _encrypt(self, value):
        if r'e+' in value.lower():
            raise AssertionError(f"Please change your number from scientific notation to standard form, for example: '{value}'")
        # value = self.fernet.encrypt(value.encode()).decode()
        try:
        
                
            _text_bytes = self._text_to_string(value).encode("utf-8")
            _key_bytes = self.key.encode("utf-8")
            _hashed_key = self._hash_key(list(_key_bytes))
            _salt = self._generate_salt(16)
            _salted_text = _salt + list(_text_bytes)
            _encrypted_bytes = [(byte ^ _hashed_key[i % len(_hashed_key)]) & 0xff for i, byte in enumerate(_salted_text)]
            _hmac = self._generate_hmac(_salt + _encrypted_bytes, _hashed_key)
            _combined = _salt + _encrypted_bytes + _hmac

            
            ###
            
            return "ENC:" + base64.b64encode(bytes(self._normalize_bytes(_combined))).decode("utf-8")
        except Exception as e:
            print(value, '->',e)
            return value
    
    def _decrypt(self, value):
        # กำลังแก้อันนี้
        if not self._is_encrypted(value):
            raise ValueError("The text is not encrypted.")
        try:
            
            # value = re.sub(r'^enx:', 'gAAAAAB', value)
            # value = re.sub(r'\*\*$', '==', value)
            # value = self.fernet.decrypt(value).decode()
            
            _encrypted_bytes = list(base64.b64decode(value.replace("ENC:", "")))
            _salt_length = 16
            _hmac_length = 16
            
            # Extract parts
            _salt = _encrypted_bytes[:_salt_length]
            _cipher_bytes = _encrypted_bytes[_salt_length:-_hmac_length]
            _extracted_hmac = _encrypted_bytes[-_hmac_length:]

            # Hash the key
            _key_bytes = self.key.encode("utf-8")
            _hashed_key = self._hash_key(list(_key_bytes))

            # Verify HMAC
            _computed_hmac = self._generate_hmac(_salt + _cipher_bytes, _hashed_key)
            if not self._arrays_equal(_extracted_hmac, _computed_hmac):
                raise ValueError("Data integrity check failed. HMAC does not match.")

            # Decrypt cipher bytes
            _decrypted_bytes = [(byte ^ _hashed_key[i % len(_hashed_key)]) & 0xff for i, byte in enumerate(_cipher_bytes)]

            # Exclude the salt from the decrypted bytes
            _original_text_bytes = _decrypted_bytes[_salt_length:]

            # Return decrypted text as a string
            return bytes(_original_text_bytes).decode("utf-8")
        except Exception as e:
            print(value, '->',e)
            return value
    
    def _find_colidx(self, n, column='', i=0):
        case_idx = string.ascii_uppercase
        if n>26:
            i = int(n%26)
            n = n//26
            column = column+str(case_idx[i-1])
            return self._find_colidx(n, column, i)
        else:
            i = int(n%26)
            if i == 0: 
                column = str(column)+str(case_idx[26])
            else: 
                column = str(column)+str(case_idx[i-1])
            return column[::-1]
                
    def encrypt_data(self, columns_name: list):
        print('INFO: Encrypting data...')        
        for col in columns_name:
            self.data[col] = self.data[col].progress_apply(lambda x: self._encrypt(x))
            
    def decrypt_data(self, columns_name: list):
        print('INFO: Decrypting data...')          
        for col in columns_name:
            self.data[col] = self.data[col].progress_apply(lambda x: self._decrypt(x))
            
    def replace_worksheets(self, ):
        # print('INFO: Clearing worksheet...')
        # self.worksheet.clear()
        
        # print('INFO: Wait for sheet clear complete...')
        # _wait_clear = self.worksheet.acell('A1').value
        # while _wait_clear:
        #     _wait_clear = self.worksheet.acell('A1').value
            
        # print('INFO: Google Sheets is resizing...')
        # self.worksheet.resize(rows=len(self.data)+1 , cols=len(self.data.columns.values.tolist()))
        
        print('INFO: Google Sheets is updating...')
        self.data = self.data.astype(str)
        self.worksheet.update(range_name=f'A1:{self._find_colidx(self.data.shape[1])}{len(self.data)+1}',values=[self.data.columns.values.tolist()] + self.data.values.tolist())
        
    def save_key(self,):
        if self.path_key is None:
            self.path_key = str(pathlib.Path(__file__).parent.resolve())
        if '.json' not in self.path_key:
            self.path_key = self.path_key.split('\\')
            if '' in self.path_key: self.path_key.remove('')
            self.path_key = '/'.join(self.path_key)+'/your_key.json'
            
        _fkey = open(self.path_key, 'w', encoding='utf8')
        _json_text = {"Token":{
            "Key":str(self.key) }}
        if self.salt is not None:
            _json_text['Token']['Salt'] = self.salt
        _json_text = json.dumps(_json_text)
        _fkey.write(_json_text)
        
        _fkey.close()
            
        

if __name__ == '__main__':
    
    '''
    Note: 
    สำคัญ! โปรดตรวจสอบว่าข้อมูลที่ encrypt นั้นอยู่ในรูปแบบ Scienctific notation หรือไม่ 
    หากใช่ โปรดแก้ไข format ก่อน
    มิฉะนั้นอาจไม่สามารถกู้คืนข้อมูลกลับคืนมาได้!
    '''
    
    parser = argparse.ArgumentParser(
                prog='EncryptAndDecryptSpreadSheets',
                description='',
                epilog='This program processes only one sheet once')
    
    parser.add_argument('-k', '--key', help='Put your key to encrypt/decrypt')
    parser.add_argument('-p', '--path_key', help='Put your path to keep your private key', default=None)
    parser.add_argument('-en', '--encrypt', action='store_true',help='Put True if you want to encrypt')
    parser.add_argument('-de', '--decrypt', action='store_true',help='Put True if you want to decrypt')
    parser.add_argument('-sv', '--service_account', help='A service account with JSON file format', default=None)
    parser.add_argument('-gsp', '--gspread_url', help='Your spread sheets URL', default=None)
    parser.add_argument('-shn', '--sheet_name', help='Your spread sheet\'s name', default=None)
    parser.add_argument('-col', '--columns_name', help='Your spread sheet columns\' name (Please input with format -> ColumnName1,ColumnName2,Columnname3 ...)', default=None)
    args = parser.parse_args()
    
    # ------------------------------------------------------------------- #
    try:
        encrypt_data = ProtectData(
            key = args.key,
            service_account = args.service_account,
            gspread_url = args.gspread_url,
            salt=args.salt,
            )
        
        # encrypt_data.start_fernet()
        encrypt_data.save_key()
        encrypt_data.is_gspread(sheetname=args.sheet_name)
        

        columnnames = list()
        # columnnames = ['Patient ID1', 'Operator ID']
        while True:
            col = input('Enter a column name (enter a blank value to end it): ')
            if col == '':
                break
            else:
                columnnames.append(col)
            
        if (args.encrypt != None) and (args.decrypt != None):
            if args.encrypt:
                encrypt_data.encrypt_data(columns_name = columnnames)
                print(encrypt_data.data.head(10))
            
            if args.decrypt:
                encrypt_data.decrypt_data(columns_name = columnnames)
                print(encrypt_data.data.head(10))
        
        # encrypt_data.replace_worksheets()
        
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        text = f'ไม่สามารถทำ Cryptography ได้ กรุณาตรวจสอบปัญหา\n---------\nข้อความ: {e}\nบรรทัดที่: {exc_tb.tb_lineno}'
        print(text)
        # notify_fail = LineNotify(text=text, token=token, url_notify=url_notify)
        # msg = notify_fail.send_text()
    
    print('\n\nAll Process are successfully!!\n\n')
    