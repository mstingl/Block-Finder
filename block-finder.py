#!/usr/bin/env python
"""
Prints a map of the entire world.
"""

import os
import json
import argparse
from multiprocessing import Process, Queue, set_start_method
from quarry.types.nbt import RegionFile
from quarry.types.chunk import BlockArray


registry = {} #LookupRegistry.from_json(os.path.realpath("./reports"))


def range_xz(start, end):
    for x in range(start, end):
        for z in range(start, end):
            yield x, z


def parse_region_file(queue, file, search_blocks):
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
    queue.put(search_results)


def main(world_folder, search_blocks):
    region_folder = os.path.join(world_folder, "region")
    region_files = os.listdir(region_folder)

    search_results = []

    queue = Queue()
    processes = []

    for file in region_files:
        p = Process(target=parse_region_file, args=(queue, os.path.join(region_folder, file), search_blocks,))
        p.start()
        processes.append(p)

    for process in processes:
        process.join()
        search_results += queue.get()

    return search_results

if __name__ == '__main__':
    set_start_method('spawn')
    parser = argparse.ArgumentParser()
    parser.add_argument('--map', dest='map')
    parser.add_argument('-b', nargs='+', help='block id', dest='blocks')

    args = parser.parse_args()
    folder = os.path.normpath(args.map)

    result = main(folder, [int(block_id) for block_id in args.blocks])
    print("Result:", json.dumps(result))
