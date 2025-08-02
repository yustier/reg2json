# reg2json
Convert Windows Registry into JSON

## Usage
```bash
python reg2json.py -o output.json input.reg
```

```bash
python json2reg.py -o output.reg input.json
```
Both scripts support `-h` or `--help` for help.

## Example
See the `example` directory.

## Structure
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
        "values": { /* ... */ },
        "keys": { /* ... */ }
      },
      "subKeyName": {
        "values": { /* ... */ },
        "keys": { /* ... */ }
      },
      // ...
    }
  }
}
```
