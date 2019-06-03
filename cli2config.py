#!/usr/bin/env python3

# Copyright Daniel Hooper 2019
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.



# This script works with iNav (version 2.2 as of writing), and can be used
# to interpret a command-line settings dump from the drone and convert it
# to C-style code for use in target/YOUR_TARGET/config.c
# This script uses settings.yaml located in the src/main/fc directory to
# translate from CLI names to source code names.
#
# The output is not guaranteed to compile and may need some hand-holding
# to work properly. This is intended to save a huge amount of time in looking
# up configuration struct names.


import yaml
import math
import argparse

parser = argparse.ArgumentParser(description="This script converts 'set settingname = value' lines from iNav CLI dumps into " \
"C commands that can be inserted into a target's config.c file.",
epilog="This is intended to help iNav hardware target developers create custom default setups. " \
"YOUR MILEAGE MAY VARY -- this is not guaranteed to produce correct code, but to save time chasing down config value names. "
"Currently it does not handle any other dump commands besides 'set'.")

parser.add_argument('infile', type=argparse.FileType('r'),
                    help='input text dump from CLI')
parser.add_argument('-inyaml', type=argparse.FileType('r'), metavar='SETTINGS.YAML', default='settings.yaml',
                    help='settings.yaml file. Looks in current directory by default.')
parser.add_argument('outfile', type=argparse.FileType('w+'),
					help='C command output file')
parser.add_argument('-c', '--comments', action='store_true',
					help='adds the cli command string as a comment in output')
parser.add_argument('-t', '--tabsize', type=int, default=8,
					help='sets tab size (default is 8)')
parser.add_argument('-s', '--start-col', type=int, default=0,
					help='column location to start comments if possible. Make sure this is a multiple of --tabsize')
parser.add_argument('--force-spaces', action='store_true',
					help='forces spaces to be used instead of tabs')


args = parser.parse_args()

if args.force_spaces:
	args.tabsize = 1

#######
# 
#  Open settings.yaml file and build a flattened decoder ring
#
#######

settings = yaml.safe_load(args.inyaml)
args.inyaml.close()

groups = settings["groups"]

lookup = []

for group in groups:
	#print(group["name"])
	for member in group["members"]:
		if 'field' in member:			# some members don't have a full field list for some reason, ie "looptime"
			lookup.append({"group_name": group["name"], "group_type": group["type"], "member_field": member["field"], "member_name": member["name"] })

#print(lookup)
#print(settings["groups"])

######
#
#  Open the CLI dump file and build a list of items to process
#
#####

config_entries = []

#for line in dumpinput:
for line in args.infile:
	tokens = line.split()
	if len(tokens) == 4 and tokens[0] == 'set':					# Only grab 'set variable = value' lines
		for lookupentry in lookup:
			if lookupentry["member_name"] == tokens[1]:			# Search lookup for setting name
				#print(values[1],lookupentry["member_field"])
				config_entries.append(dict(lookupentry, **{"value" : tokens[3], "cli_command" : line}))

args.infile.close()
#print(config_entries)


######
#
#  Format config_entries into an output file
#
#  Note: this relies on the group.type in the YAML file following the following convention
#  YAML      structName_t
#  Variable  structNameMutable()
#
#####

for entry in config_entries:
	# Generally the CLI names and enums/constants have the same (or similar) names.
	# If you find more than ON/true OFF/false, you can make simple substitutions here.
	if entry["value"] == "ON":
		entry["value"] = "true"
	if entry["value"] == "OFF":
		entry["value"] = "false"

	c_code = "{}Mutable()->{} = {};".format(entry["group_type"][:-2], entry["member_field"], entry["value"])

	if args.comments:
		code_len = len(c_code)
		remainder_len = code_len % args.tabsize

		if remainder_len > 0:
			total_len = code_len + args.tabsize-remainder_len	# length of line with one tab appended
		else:
			total_len = code_len

		if args.force_spaces:
			spacing_char = " "
		else:
			spacing_char = "\t"

		if total_len <= args.start_col:
			if remainder_len > 0:
				c_code += spacing_char

			c_code += spacing_char * math.ceil((args.start_col - total_len)/args.tabsize)
		else:
			c_code += " "

		c_code += "// " + entry["cli_command"]

	else:
		c_code += "\n"

	args.outfile.write(c_code)

args.outfile.close()


