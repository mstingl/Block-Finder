#!/usr/bin/env python
"""
Search coordinates of blocks in the entire map
"""

import os
import sys
import json
import argparse
from multiprocessing import set_start_method, Pool
from quarry.types.nbt import RegionFile
from quarry.types.chunk import BlockArray


registry = {}


def range_xz(start, end):
    for x in range(start, end):
        for z in range(start, end):
            yield x, z


def parse_region_file(file, search_blocks):
    print("Start processing", file)
    search_results = []
    with RegionFile(file) as region:
        for x, z in range_xz(0, 32):
            try:
                chunk = region.load_chunk(x, z)
                x_pos = chunk.body.value["Level"].value['xPos'].value
                z_pos = chunk.body.value["Level"].value['zPos'].value
                sections = chunk.body.value["Level"].value["Sections"].value
                for section in sections:
                    blocks = BlockArray(
                        registry,
                        section.value["Blocks"].value,
                        bits=8,
                    )
                    y_pos = section.value['Y'].value

                    for i in range(4096):
                        block_id = blocks.data[i]
                        if block_id in search_blocks:
                            block_x = x_pos * 16 + i % 16
                            block_y = y_pos * 16 + i // 256
                            block_z = z_pos * 16 + i % 256 // 16
                            print("Block found on index %s on coordinates %s, %s, %s" % (i, block_x, block_y, block_z))

                            search_results.append((block_id, block_x, block_y, block_z))

            except Exception: # pylint: disable=broad-except  # catch any occurring errors to prevent script from stopping somewhere parsing the world
                pass

    print("Completed processing", file)
    return search_results


def main(world_folder, search_blocks, pool_processes):
    region_folder = os.path.join(world_folder, "region")
    region_files = os.listdir(region_folder)

    search_results = []

    with Pool(pool_processes) as p:
        p_results = [p.apply_async(parse_region_file, (os.path.join(region_folder, file), search_blocks,)) for file in region_files]
        for p in p_results:
            search_results += p.get()

    return search_results

if __name__ == '__main__':
    set_start_method('spawn')
    parser = argparse.ArgumentParser()
    parser.add_argument('--map', dest='map', help='Path of the world folder')
    parser.add_argument('-b', nargs='+', dest='blocks', help='IDs of Blocks to search for')
    parser.add_argument('-p', dest='processes', default=4, type=int, help='How many processes to use for parallel searching')
    parser.add_argument('--result-file', dest='result_file', default='result.json', help='Path of the result file')

    args = parser.parse_args()

    if not args.map or not args.blocks:
        parser.print_help()
        sys.exit(1)

    folder = os.path.normpath(args.map)

    result = main(folder, [int(block_id) for block_id in args.blocks], args.processes)

    with open(os.path.normpath(args.result_file), "w") as f:
        f.write(json.dumps(result))

    print("Completed! See", os.path.normpath(args.result_file))
