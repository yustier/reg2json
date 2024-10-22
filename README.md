# reg2json
Convert Windows Registry into JSON

## Usage
```bash
python reg2json.py -i input.reg output.json
```

```bash
python json2reg.py -i input.json output.reg
```
Both scripts support `-h` or `--help` for help.

## Example
```
[ ] keyName
    - valueName: valueType = valueData
    [ ] subKeyName
```

```json
{
  "keyName": {
    "values": {
      "valueName": {
        "type": "valueType",
        "data": "valueData" // it may be a string, number, or array
      }
    },
    "keys": {
      "subKeyName": {
        "values": {},
        "keys": {}
      }
    }
  }
}
```
