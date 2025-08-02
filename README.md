reg2json
========

Convert Windows Registry into JSON

> [!WARNING]
> Currently this program does not have:
>
> - Support for IF conditions
> - Support for deleting a key
> - Support for deleting a value
>
> <https://learn.microsoft.com/en-us/previous-versions/windows/embedded/gg469889(v=winembedded.80)>

Usage
-----

```bash
python reg2json.py -o output.json input.reg
```

```bash
python json2reg.py -o output.reg input.json
```
Both scripts support `-h` or `--help` for help.

Example
-------

See the `example` directory.

Structure
---------

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
