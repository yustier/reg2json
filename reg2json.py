import sys
import json
import argparse

def find_key(regjson: json, keyPath: str) -> dict:
	keys = keyPath.split('\\')
	if keys[0] not in regjson:
		regjson[keys[0]] = {
			'values': {},
			'keys': {}
		}
	current = regjson[keys[0]]
	for key in keys[1:]:
		if key not in current['keys']:
			current['keys'][key] = {
				'values': {},
				'keys': {}
			}
		current = current['keys'][key]
	return current

def pop_first_quoted_string(line: str):
	if not line.startswith('"'):
		return None, line
	s = ''
	i = 1
	while i < len(line):
		if line[i] == '\\':
			s += line[i+1]
			i += 2
		elif line[i] == '"': # end of the value name
			break
		else:
			s += line[i]
			i += 1
	return s, line[i+1:]

def append_bytes_to_array(arr: list, s: str):
	# input is two-digit hex separated by ','
	for byte in s.split(','):
		if byte:
			arr.append(int(byte, 16))

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Convert a Windows registry file to JSON')
	parser.add_argument('input', metavar='InFilePath', help='Input registry file')
	parser.add_argument('-o', '--output', metavar='OutFilePath', help='Output JSON file', default=None)
	parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose mode')
	args = parser.parse_args()

	if args.output is None:
		args.output = args.input + '.json'

	with open(args.input, 'rb') as f:
		lines = f.read().decode('utf-16').splitlines()

	if not lines.pop(0).strip().startswith('Windows Registry Editor Version'):
		print('[FATAL] Invalid registry file given. Terminating', file=sys.stderr)
		sys.exit(1)

	regjson = {}

	lineNum = 1
	while lines:

		lineOrig = lines.pop(0).strip()
		lineNum += 1
		line = lineOrig

		if not line:
			continue

		if line.startswith(';'):  # comment
			continue

		if line.startswith('['):  # key

			keyPath = line[1:-1]
			current = find_key(regjson, keyPath)

			if args.verbose:
				print(f'[INFO] Found key: {keyPath}')

			while lines:

				lineOrig = lines.pop(0).strip()
				lineNum += 1
				line = lineOrig

				if not line:
					continue

				if line.startswith(';'):  # comment
					continue

				if line.startswith('['):  # next key
					lines.insert(0, lineOrig)  # put it back for the next iteration
					lineNum -= 1
					break

				if '=' in line:  # value

					# (Default) REG_SZ
					if line.startswith('@'):  # default value
						valueName = ''
						valueType = 'REG_SZ'
						valueData = line[2:].strip('"')

					elif line.startswith('"'):  # named value

						valueName, line = pop_first_quoted_string(line)

						if line.startswith('='):
							line = line[1:]
						else:
							print(f'[WARN] Invalid line at line {lineNum}:', file=sys.stderr)
							print(f'       {lineOrig}', file=sys.stderr)
							print( '       Expected = after value name, ignoring this line', file=sys.stderr)
							continue

						lineNumOrig = lineNum

						# REG_DWORD
						if line.startswith('dword:'):
							valueType = 'REG_DWORD'
							valueData = int(line[6:], 16)

						# REG_QWORD (little endian)
						elif line.startswith('hex(b):'):
							valueType = 'REG_QWORD'
							valueData = 0
							for i, byte in enumerate(line[7:].split(',')):
								valueData += int(byte, 16) << (i * 8)

						# REG_SZ
						elif line.startswith('"'):
							valueType = 'REG_SZ'
							valueData, _ = pop_first_quoted_string(line)

						elif line.startswith('hex'):
							# REG_EXPAND_SZ
							if line.startswith('hex(2):'):
								valueType = 'REG_EXPAND_SZ'
								line = line[7:]
							# REG_MULTI_SZ
							elif line.startswith('hex(7):'):
								valueType = 'REG_MULTI_SZ'
								line = line[7:]
							# REG_BINARY
							elif line.startswith('hex:'):
								valueType = 'REG_BINARY'
								line = line[4:]

							hexdata = []
							while line.endswith('\\'):
								append_bytes_to_array(hexdata, line[:-1].strip())
								line = lines.pop(0).strip()
								lineNum += 1
							append_bytes_to_array(hexdata, line.strip())

							if valueType == 'REG_BINARY':
								valueData = hexdata
							elif valueType == 'REG_EXPAND_SZ':
								valueData = bytes(hexdata).decode('utf-16le').replace('\0', '')
							elif valueType == 'REG_MULTI_SZ':
								valueData = bytes(hexdata).decode('utf-16le').split('\0')[:-1]

						else:
							print(f'[WARN] Invalid line at line {lineNumOrig}:', file=sys.stderr)
							print(f'       {lineOrig}', file=sys.stderr)
							print( '       Ignoring this line', file=sys.stderr)
							continue

						if args.verbose:
							print(f'[INFO] Found value: {valueName or "(Default)"} ({valueType})')

					current['values'][valueName] = {
						'type': valueType,
						'data': valueData
					}

				else:
					print(f'[WARN] Invalid line at line {lineNum}:', file=sys.stderr)
					print(f'       {lineOrig}', file=sys.stderr)
					print( '       Ignoring this line', file=sys.stderr)
		else:
			print(f'[WARN] Invalid line at line {lineNum}:', file=sys.stderr)
			print(f'       {lineOrig}', file=sys.stderr)
			print( '       Ignoring this line', file=sys.stderr)

	with open(args.output, 'w', encoding='utf-8') as f:
		json.dump(regjson, f, ensure_ascii=False, indent='\t')

	print(f'[INFO] Successfully converted registry file to JSON: {args.output}')
