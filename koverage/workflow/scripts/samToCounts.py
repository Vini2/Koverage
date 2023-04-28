#!/usr/bin/env python3

import os
import atexit
import logging


def exitLogCleanup(*args):
    """Cleanup the logging file(s) prior to exiting"""
    for logFile in args:
        os.unlink(logFile)
    return None


atexit.register(exitLogCleanup, snakemake.log[0])
logging.basicConfig(filename=snakemake.log[0], filemode="w", level=logging.DEBUG)

logging.debug("Collecting contig counts")

sam = open(snakemake.input[0], 'r')
logging.debug("Open pipe to save bame")
outSam = open(snakemake.output.sam, 'a')

contigLens = dict()
contigCounts = dict()

# parse header
logging.debug("Parsing header")
for line in sam:
    outSam.write(line)
    if line.startswith("@"):
        if line.startswith("@SQ"):
            l = line.strip().split()
            c = l[1].split(":")
            n = l[2].split(":")
            contigLens[c[1]] = n[1]
            contigCounts[c[1]] = 0
    else:
        logging.debug("End of header")
        l = line.strip().split()
        contigCounts[l[2]] = contigCounts[l[2]] + 1
        break

# parse body and echo to output pipe
logging.debug("parsing body")
for line in sam:
    outSam.write(line)
    l = line.strip().split()
    contigCounts[l[2]] = contigCounts[l[2]] + 1

# print output
logging.debug("Writing output")
with open(snakemake.output.tsv, 'w') as outTsv:
    for contig in contigCounts.keys():
        outTsv.write(f"{contig}\t{contigLens[contig]}\t{contigCounts[contig]}\n")
