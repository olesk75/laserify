#!/usr/bin/env python
__author__ = 'Ole Jakob Skjelten'


"""
	Takes a g-code file and removes pauses, z-movement (if requested), turns laser off when traversing and such.

	Alternatively, replaces z-movement with something laser compatible if multiple passes are required

	The objective is create a file that can be used for laser cutters based on a g-code file for CNC routers
"""

import argparse
import sys
import re

parser = argparse.ArgumentParser(description="Converts a normal g-code file for CNC milling to laser compatible g-code")

parser.add_argument('infile', type=argparse.FileType('r'), help='original g-code file to import')
parser.add_argument('-o', '--outfile', nargs='?', type=argparse.FileType('w'), help='output file (defaults to STDOUT)')
parser.add_argument('-z', '--zero', help='set all z-movement to 0', action='store_true')
parser.add_argument('-lon', '--laser-on', help='set all z-movement to 0', default="M3")
parser.add_argument('-loff', '--laser-off', help='set all z-movement to 0', default="M5")
parser.add_argument('-v', '--verbose', help='increase output verbosity', action='store_true')

args = parser.parse_args()

if args.outfile is None: args.outfile = sys.stdout

lines = map(str.strip, args.infile.readlines())     # Reading all lines and removing trailing whitespace


if args.verbose:
	print("Reading", fileLength, "lines from", args.infile.name, "and 'laserifying'. Saving result to", args.outfile.name)
	print("---------------------------------------> snip <---------------------------------------\n")

"""
	One of the main challenges is that some people like making multiline g-codes, like this:
			G1 Z2.0000
				Y101.600

"""

lines = [i.lstrip() for i in lines if i.rstrip() != '']      # Removing empty list elements


lineCounter = 0
previousCode = 'G0'

doubleLines = list(zip(lines[1:], lines))  # We create a list of tuples with line n and n-1 (previous line last in tuple)

skipNext = False

for n in range(0, len(doubleLines) - 1):

	if re.match(r'G0+\s', doubleLines[n][1].upper(), flags=re.IGNORECASE): previousCode = "G0"  # Previous line contains a G0
	if re.match(r'G0*1', doubleLines[n][1].upper(), flags=re.IGNORECASE): previousCode = "G1"  # Previous line contains a G1

	if skipNext is True:    # To skip lines after we have combined two
		skipNext = False

	if re.match(r'X|Y|Z', doubleLines[n][0].upper(), flags=re.IGNORECASE):          # Current line has a X/Y/Z move with no G-code
		if re.match(r'^(G0*[0-3]\s+)', doubleLines[n][1].upper(), flags=re.IGNORECASE):   # Previous line contains either a G0 (move) or a G1 (feed)
			lineCounter -= 1    # We move one step up, as this element is supposed to replace the previous which was only a G-code by itself
			lines[lineCounter] = doubleLines[n][1] + " " + doubleLines[n][0]        # Combined line into lines list
			#print(lines[lineCounter])

			skipNext = True # We have removed a line, so next iteration we skip to avoid including the part we moved one line up
		else:
			lines[lineCounter] = re.sub(r'^(X|Y|Z\.*)', previousCode + r' \g<1>', doubleLines[n][0].upper(), flags=re.IGNORECASE)

	elif not (re.match(r'^(G0*[0-3] +)', doubleLines[n][0].upper(), flags=re.IGNORECASE) and re.match(r'X|Y|Z', doubleLines[n + 1][0].upper(), flags=re.IGNORECASE)):
		lines[lineCounter] = doubleLines[n][0]
		#print(lines[lineCounter])

	lineCounter += 1


lineCounter = 0
previousCode = "undef"

for n in range(0, len(lines)):
	"""
		This is the main loop where do out substitutions
	"""
	# Removing the spindle on commands. If we start the laser before we are in position we will have "interesting" results
	lines[n] = re.sub(r'(G04.*)', r';\g<1> (pauses are dangerous!)', lines[n].upper(), flags=re.IGNORECASE)

	# Setting all Z-movements to zero when requested
	if args.zero:
		lines[n] = re.sub(r'(G\d*.*Z\s*)(-?\d*\.\d*)(.*)', r'\g<1>0.0000\g<3> (reduced Z to zero for laser)', lines[n].upper(), flags=re.IGNORECASE)

	# If we don't want to zero everything we nevertheless want to ensure that the laser is off when we're only moving in the Z-direction,
	# otherwise we'll burn the material
	elif re.search(r'G0*[0-3].*Z\s*', lines[n].upper(), flags=re.IGNORECASE) and not re.search(r'G\d*.*(X|Y)\s*', lines[n].upper(), flags=re.IGNORECASE): # G0 moves are handles seperately, so here we look of Z-only G1/G2/G3 moves
			lines[n] = args.laser_off + " (stop laser)\n" + lines[n] + " (we stop and restart laser on pure vertical move)\n" + args.laser_on + " (start laser)"


	# Removing pauses - they are bad when having an enabled laser eating through your wasteboard!
	lines[n] = re.sub(r'(M3.*)', r';\g<1> (starting too early is dangerous!)', lines[n].upper(), flags=re.IGNORECASE)


	if re.search(r'G0+\s', lines[lineCounter].upper(), flags=re.IGNORECASE) and previousCode != "G0":
		lines[n] = args.laser_off + " (stop laser)\n" + lines[n]   # Disable laser as we move
		previousCode = "G0"

	if re.search(r'G0*1', lines[lineCounter].upper(), flags=re.IGNORECASE) and previousCode != "G1":
		lines[n] = args.laser_on + " (start laser)\n" + lines[n]  # Enable laser as we're cutting
		previousCode = "G1"

	formattedLines = ['{0}\n'.format(line) for line in lines]    # Adding back newline

	args.outfile.write(formattedLines[n])
	lineCounter += 1


Copyright Ole Jakob Skjelten
