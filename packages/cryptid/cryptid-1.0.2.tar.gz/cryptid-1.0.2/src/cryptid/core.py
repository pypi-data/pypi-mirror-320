from PIL import Image

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding

import hashlib
import os
import base64
import pickle
import wave

class InvalidToken(InvalidToken): pass

class Cryptid:
	def __init__(self, key: str):
		if key is not None:
			self.__key = self.__process_key(key)
		else:
			raise ValueError('key cannot be empty')
	
	def __process_key(self, key):
		hashed_key = hashlib.sha256(key.encode()).digest()
		return base64.urlsafe_b64encode(hashed_key)
	
	def encrypt(self, obj) -> bytes:
		pickled_obj = pickle.dumps(obj)
		fernet = Fernet(self.__key)
		enc_obj = fernet.encrypt(pickled_obj)
		return enc_obj
	
	def decrypt(self, obj):
		fernet = Fernet(self.__key)
		try:
			dec_pickled_obj = fernet.decrypt(obj)
		except Exception as e:
			raise InvalidToken(e)
		obj = pickle.loads(dec_pickled_obj)
		return obj
	
	@staticmethod
	def generate_key(salt: str | None = None) -> str:
		if salt:
			hashed_key = hashlib.sha256(salt.encode()).digest()
			key = base64.urlsafe_b64encode(hashed_key)
		else:
			key = Fernet.generate_key()
		return key.decode()

class Cryptext:
	def __init__(self, key: str):
		self.__key = hashlib.sha256(key.encode()).digest()[:16]
		self.__iv = os.urandom(16)

	def encrypt(self, data: str) -> str:
		try:
			padder = padding.PKCS7(128).padder()
			padded_data = padder.update(data.encode()) + padder.finalize()
			
			cipher = Cipher(algorithms.AES(self.__key), modes.CBC(self.__iv), backend=default_backend())
			encryptor = cipher.encryptor()
			encrypted_data = self.__iv + encryptor.update(padded_data) + encryptor.finalize()
			return base64.b64encode(encrypted_data).decode('utf-8')
		except Exception as e:
			raise InvalidToken(e)

	def decrypt(self, encrypted_data: str) -> str:
		try:
			encrypted_data = base64.b64decode(encrypted_data.encode('utf-8'))
			iv = encrypted_data[:16]
			
			actual_ciphertext = encrypted_data[16:]
			cipher = Cipher(algorithms.AES(self.__key), modes.CBC(iv), backend=default_backend())
			decryptor = cipher.decryptor()
			
			padded_plaintext = decryptor.update(actual_ciphertext) + decryptor.finalize()
			unpadder = padding.PKCS7(128).unpadder()
			result = unpadder.update(padded_plaintext) + unpadder.finalize()
			return result if type(result) is str else result.decode('utf-8')
		except Exception as e:
			raise InvalidToken(e)

class Steganography:
	def __init__(self):
		self.__delimiter = '$$END$$'
	
	def text2binary(self, text: str) -> str:
		binary_data = ''.join(format(byte, '08b') for byte in (text.encode('utf-8') if type(text) is str else text) + self.__delimiter.encode('utf-8'))
		return binary_data
	
	def binary2text(self, binary: str) -> str | None:
		byte_data = bytearray()
		for i in range(0, len(binary), 8):
			byte = binary[i:i+8]
			byte_data.append(int(byte, 2))
			try:
				text = byte_data.decode('utf-8')
				if text.endswith(self.__delimiter):
					return text[:-len(self.__delimiter)]
			except UnicodeDecodeError:
				continue
		return None
	
	def encode(
		self,
		image_path: str,
		message: str,
		output_path: str,
		password: str | None = None
	) -> bool:
		if password:
			message = Cryptext(password).encrypt(message)
		binary_message = self.text2binary(message)
		with Image.open(image_path) as img:
			if img.mode != 'RGB':
				img = img.convert('RGB')
			pixels = bytearray(img.tobytes())
			if len(binary_message) > len(pixels):
				raise ValueError('Message too large for the image capacity.')
			
			for i in range(len(binary_message)):
				pixels[i] = (pixels[i] & 0xFE) | int(binary_message[i])
			
			encoded_image = Image.frombytes(img.mode, img.size, bytes(pixels))
			encoded_image.save(output_path, 'PNG')
			return True
	
	def decode(
		self,
		image_path: str,
		password: str | None = None
	) -> str:
		with Image.open(image_path) as img:
			if img.mode != 'RGB':
				img = img.convert('RGB')
			pixels = bytearray(img.tobytes())
			binary_message = []
			for pixel_value in pixels:
				binary_message.append(str(pixel_value & 1))
				if len(binary_message) % 8 == 0:
					text = self.binary2text(''.join(binary_message))
					if text is not None:
						if password:
							text = Cryptext(password).decrypt(text)
						return text
			return None

class AudioSteganography(Steganography):
	def __init__(self):
		super().__init__()
	
	def encode(
		self,
		audio_path: str,
		message: str,
		output_path: str,
		password: str | None = None
	) -> bool:
		if password:
			message = Cryptext(password).encrypt(message)
		
		binary_message = self.text2binary(message)
		bit_index = 0
		
		with wave.open(audio_path, 'rb') as audio:
			params = audio.getparams()
			frames = bytearray(audio.readframes(audio.getnframes()))
		
		for i in range(len(frames)):
			if bit_index < len(binary_message):
				frames[i] = (frames[i] & 0xFE) | int(binary_message[bit_index])
				bit_index += 1
		
		with wave.open(output_path, 'wb') as audio:
			audio.setparams(params)
			audio.writeframes(frames)
		return True
	
	def decode(
		self,
		audio_path: str,
		password: str | None = None
	) -> str:
		binary_message = ''
		with wave.open(audio_path, 'rb') as audio:
			frames = bytearray(audio.readframes(audio.getnframes()))
		
		for byte in frames:
			binary_message += str(byte & 1)
		message = self.binary2text(binary_message)
		return Cryptext(password).decrypt(message) if password else message
