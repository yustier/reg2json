import sys
import json
import argparse

def json2reg(json: dict, reglines: list, current: str):

	for valueName in json['values']:
		valueType = json['values'][valueName]['type']
		valueData = json['values'][valueName]['data']

		if args.verbose:
			print(f'[INFO] Found value: {valueName or "(Default)"} ({valueType})')

		if valueName == '': # (Default) REG_SZ
			reglines.append(f'@="{valueData}"')
		else:
			# valueName should be escaped for special characters
			valueNameEscaped = valueName.replace("\\", "\\\\").replace("\"", "\\\"")
			regline = f'"{valueNameEscaped}"='

			if valueType == 'REG_DWORD':
				regline += f'dword:{valueData:08x}'

			elif valueType == 'REG_QWORD':
				regline += 'hex(b):'
				for i in range(8):
					regline += f'{(valueData >> (i * 8)) & 0xff:02x},' # little endian
				regline = regline[:-1] # remove last comma

			elif valueType == 'REG_SZ':
				valueDataEscaped = valueData.replace("\\", "\\\\").replace("\"", "\\\"")
				regline += f'"{valueDataEscaped}"'

			elif valueType == 'REG_BINARY':
				regline += 'hex:'
				for byte in valueData:
					regline += f'{byte:02x},'
					if len(regline) > 76:
						regline += '\\'
						reglines.append(regline)
						regline = '  '
				regline = regline[:-1] # remove last comma

			elif valueType == 'REG_EXPAND_SZ':
				regline += 'hex(2):'
				for byte in valueData.encode('utf-16le'):
					regline += f'{byte:02x},'
					if len(regline) > 76:
						regline += '\\'
						reglines.append(regline)
						regline = '  '
				regline += '00,00' # null in utf-16le

			elif valueType == 'REG_MULTI_SZ':
				regline += 'hex(7):'
				valueDataStream = bytes()
				for valueDataLine in valueData:
					valueDataStream += valueDataLine.encode('utf-16le') + b'\0\0'
				for byte in valueDataStream:
					regline += f'{byte:02x},'
					if len(regline) > 76:
						regline += '\\'
						reglines.append(regline)
						regline = '  '
				# regline += '00,00' # null in utf-16le
				regline = regline[:-1] # remove last comma

			else:
				print(f'[WARN] Unknown value type: {valueName["type"]}', file=sys.stderr)
				print(f'       Ignoring this value', file=sys.stderr)
				continue

			reglines.append(regline)

	reglines.append('')

	for key in json['keys']:

		if args.verbose:
			print(f'[INFO] Found key: {current}\\{key}')

		reglines.append(f'[{current}\\{key}]')
		json2reg(json['keys'][key], reglines, f'{current}\\{key}')

	return reglines

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Convert a JSON to a Windows registry file')
	parser.add_argument('input', metavar='InFilePath', help='Input JSON file')
	parser.add_argument('-o', '--output', metavar='OutFilePath', help='Output registry file', default=None)
	parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose mode')
	args = parser.parse_args()

	if args.output is None:
		args.output = args.input + '.reg'

	with open(args.input, 'r', encoding='utf-8') as f:
		regjson = json.load(f)

	reglines = []
	reglines.append('Windows Registry Editor Version 5.00')

	for keyRoot in regjson:
		if args.verbose:
			print(f'[INFO] Found key: {keyRoot}')
		json2reg(regjson[keyRoot], reglines, keyRoot)

	reglines.append('')

	with open(args.output, 'wb') as f:
		# begin with BOM (UTF-16LE: FF FE)
		f.write(b'\xff\xfe')
		f.write('\n'.join(reglines).encode('utf-16le'))

	print(f'[INFO] Successfully wrote to {args.output}')
