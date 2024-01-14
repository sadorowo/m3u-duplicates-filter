## M3U+ Duplicates Filter

Simple script that will remove worse qualities from your M3U8 list, if detected.

### NOTE!
This may **NOT** be 100% accurate.
This script is in BETA phase. Please report any bugs!

### Based on
- argparse
- pathlib
- [ipytv](https://github.com/Beer4Ever83/ipytv)

### Usage
```bash
python3 <path-to-script> -i "<m3u path>" (-v)
```

### Result
When everything is done, file is **OVERWRITTEN**!

### Example usage
```bash
python3 <path-to-script> -m "m3u_list.m3u"
```

### Available parameters
- -m/--m3u - absolute path to m3u+ file
- -v/--verbose - enable verbose mode