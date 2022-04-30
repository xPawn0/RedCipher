from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
from Crypto import Random
from Crypto.Cipher import PKCS1_OAEP 
from base64 import b64decode, b64encode, urlsafe_b64encode, urlsafe_b64decode
from getpass import getuser
from os import mkdir, listdir, chdir, getcwd, urandom, path, remove
from pathlib import Path
from src.handle_json import Handle_json
from src.aes_encryptor import AES_encryptor
import hashlib

# RSA Encryptor class
class Encryptor:

    def __init__(self):

        # initialize some objects
        self.h_obj = Handle_json()
        self.a_obj = AES_encryptor()

        # load json file (settings.json)
        self.h_obj.load_json()

        # get key-size from settings file
        self.keys_size = self.h_obj.get_keysize()


        # Path convert paths to system default format
        # path.dirname extract the dirname of a __file__
        # str(self.key_dir) convert the return value to string
        self.keys_dir = Path(path.dirname(__file__).replace("/src","") + "/Keys")
        self.public_key_file = Path(str(self.keys_dir) + "/public.pem")
        self.private_key_file = Path(str(self.keys_dir) + "/private.pem")

        


    # This Function check the main keys directory !
    def check_dir(self):
        
        # trying to cd directory
        try:
            # get current directory
            c =  getcwd()

            # change directory to keys-dir
            # this line check if the key-dir exsits or not
            chdir(self.keys_dir)

            # then we back to current directory
            chdir(c)

        # when we dont find the key-dir
        except:
            
            # make the directory
            mkdir(self.keys_dir)

            # generate keys
            self.generate_keys()
            

    # This Function check the < private.pem > & < public.pem > keys!
    def check_files(self):

        # list of keys file names
        key_files  = ["public.pem", "private.pem"]

        # list content of keys directory
        files = listdir(self.keys_dir)

        # check if the key files in key dir
        if key_files[0] and key_files[1] in files:
            
            # yes there is keys files
            return True

        else:
            # we don't find any key file
            return False



    # This Function Generate RSA keys and write them in files !
    # Args < KeySize: int / default: 2048 >
    # Notice: the keys size was taken from constructor function up! 

    def generate_keys(self, cmd=False, size=2048):

        # check if the user don't use tag -g to generate keys
        if not cmd:

            # generate RSA private key with default size of bytes
            private = RSA.generate(self.keys_size)

            # open private key file and write the private key
            with open(self.private_key_file, "wb") as private_file:
                        
                private_file.write(private.export_key())

            # open public key file and write the public key      
            with open(self.public_key_file, "wb") as public_file:
                
                # extract public key from private key
                # and export it to pem to write it in file
                public_file.write(private.publickey().export_key())

        # if user use the tag -g to generate keys
        elif cmd:

            # we do the same here

            # take the size of bytes that user has specify
            private = RSA.generate(size)

            with open(self.private_key_file, "wb") as private_file:
                        
                private_file.write(private.export_key())
                        
            with open(self.public_key_file, "wb") as public_file:

                public_file.write(private.publickey().export_key())



    # This Function Encrypt a string with tha RSA key !
    # Args < message: String >
    # Return Encrypted Message !

    def rsa_encrypt(self, message):

        # open public key file and read it
        pubFile = open(self.public_key_file).read()

        # import the public key to RSA object
        pubKey = RSA.import_key(pubFile); 
        
        # initialize RSA cipher with the pubKey
        rsa_cipher = PKCS1_OAEP.new(pubKey)

        # generate random AES key
        aes_key = self.a_obj.generate_key("None")
        
        # encrypt the message with AES key
        encrypted_data = self.a_obj.encrypt(message, aes_key)

        # encrypt AES key with RSA key
        encrypted_aes_key = rsa_cipher.encrypt(aes_key)

        # combine encrypted AES key with encrypted data
        full_encrypted = encrypted_aes_key + encrypted_data

        # finally return AES key and encrypted data as bytes
        return aes_key ,full_encrypted



    
    # This Function Decrypt a encrypted string with RSA key !
    # Args < enc_message: String >
    # Return Decrypted Message !

    def rsa_decrypt(self, enc_message):

        # open private key file and read it
        privFile = open(self.private_key_file).read()

        # import private key to RSA object
        key = RSA.import_key(privFile)
        
        # create RSA cipher with private key
        rsa_cipher = PKCS1_OAEP.new(key)

        # extraxt the frist 256 bits (Encrypted AES key)
        enc_aes_key = enc_message[:256]
        
        # decrypt aes key with RSA private key
        aes_key = rsa_cipher.decrypt(enc_aes_key)

        # skip 256 bit and extraxt the rest (Encrypted data)
        dec_data = enc_message[256:]

        # finally return AES key and decrypted data
        return aes_key, self.a_obj.decrypt(dec_data, aes_key)



    # This Function Encrypt a string with loaded RSA public key !
    # Args < message: String > & < pub_key_path: String > 
    # Return Encrypted Message !
    def rsa_encrypt_load(self, message, pub_key_path):
        
        # we do here the same as rsa_encrypt function
        # but with extra thing is the costum key file
        # that user specify in command line with tag -l (stands for load)

        # open and read the public key that user specify
        pubFileL = open(pub_key_path).read()

        key = RSA.import_key(pubFileL)
        
        rsa_cipher = PKCS1_OAEP.new(key)

        aes_key = self.a_obj.generate_key("None") 
        
        encrypted_data = self.a_obj.encrypt(message, aes_key)

        encrypted_aes_key = rsa_cipher.encrypt(aes_key)

        full_encrypted = encrypted_aes_key + encrypted_data

        return aes_key, full_encrypted


    # This Function Decrypt a Encrypted String with loaded RSA private key !
    # Args < enc_message: Bytes > & < priv_key_path: String > 
    # Return Decrypted Message !
    def rsa_decrypt_load(self, enc_message, priv_key_path):

        # we do here the same as rsa_decrypt function
        # but with extra thing is the costum key file
        # that user specify in command line with tag -l (stands for load)

        # open and read the private key that user specify
        privFileL = open(priv_key_path).read();

        key = RSA.import_key(privFileL)
        
        rsa_cipher = PKCS1_OAEP.new(key)

        enc_aes_key = enc_message[:256]
        
        aes_key = rsa_cipher.decrypt(enc_aes_key)

        dec_data = enc_message[256:]

        return aes_key, self.a_obj.decrypt(dec_data, aes_key)
