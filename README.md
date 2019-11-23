# Block Finder
## Find all blocks in a Minecraft world by their id

The Block Finder is a CLI Script, which can be used to search a map for
occurrences of specific blocks.
The searching is done in parallel processing to speed it up.
As result you get a json file containing a list of found blocks with
their id and the coordinates.

### Example result json
```
[[1, 51, 30, -84], [1, 52, 30, -87], ...]
```
First value is the block id, the other values are X, Y and Z coordinates.


## Usage
The Script is built for command line usage.

Example:
`python3 block_finder.py --map '%appdata%\.minecraft\saves\MyWorld' -b 54 20`

or, using the binary file:
`block_finder.exe --map '%appdata%\.minecraft\saves\MyWorld' -b 54 20`
