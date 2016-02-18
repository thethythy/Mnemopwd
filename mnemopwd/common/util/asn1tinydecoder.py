#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
  

# This is a simple and fast ASN1 decoder without external libraries.
#
# In order to browse through the ASN1 asn1_structure you need only 3 
# functions allowing you to navigate:
#    asn1_node_root(...), asn1_node_next(...) and asn1_node_first_child(...) 
#
####################### BEGIN ASN1 DECODER ############################

# Author: Jens Getreu, 8.11.2014

# Contributor: Thierry Lemeunier, 16.02.2016
#  - der argument is now a 'bytes' type (not a 'string' type)
#  - some modifications for Python3

import binascii

##### NAVIGATE

# The following 4 functions are all you need to parse an ASN1 asn1_structure

# gets the first ASN1 asn1_structure in der
def asn1_node_root(der):
    return asn1_read_length(der,0)

# gets the next ASN1 asn1_structure following (ixs,ixf,ixl)
def asn1_node_next(der, asn1_struct):
    (ixs,ixf,ixl) = asn1_struct
    return asn1_read_length(der,ixl+1)

# opens the container (ixs,ixf,ixl) and returns the first ASN1 inside
def asn1_node_first_child(der, asn1_struct):
    (ixs,ixf,ixl) = asn1_struct
    if der[ixs] & 0x20 != 0x20:
        raise ValueError('Error: can only open constructed types. '
                         + 'Found type: 0x' + binascii.hexlify(der[ixs]))
    return asn1_read_length(der,ixf)

# is true if one ASN1 chunk is inside another chunk.
def asn1_node_is_child_of(iasn1_struct, jasn1_struct):
    (ixs,ixf,ixl) = iasn1_struct
    (jxs,jxf,jxl) = jasn1_struct
    return ( (ixf <= jxs ) and (jxl <= ixl) ) or \
           ( (jxf <= ixs ) and (ixl <= jxl) )

##### END NAVIGATE



##### ACCESS PRIMITIVES

# get content and verify type byte
def asn1_get_value_of_type(der,asn1_struct,asn1_type):
    (ixs,ixf,ixl) = asn1_struct
    asn1_type_table = {
        'BOOLEAN':           0x01, 'INTEGER':           0x02,
        'BIT STRING':        0x03, 'OCTET STRING':      0x04,
        'NULL':              0x05, 'OBJECT IDENTIFIER': 0x06,
        'SEQUENCE':          0x70, 'SET':               0x71,
        'PrintableString':   0x13, 'IA5String':         0x16,
        'UTCTime':           0x17, 'ENUMERATED':        0x0A,
        'UTF8String':        0x0C, 'PrintableString':   0x13
    }
    if asn1_type_table[asn1_type] != der[ixs]:
        raise ValueError('Error: Expected type was: ' + hex(asn1_type_table[asn1_type])
                         + ' Found: 0x' + binascii.hexlify(der[ixs]))
    return der[ixf:ixl+1]

# get value
def asn1_get_value(der,asn1_struct):
    (ixs,ixf,ixl) = asn1_struct
    return der[ixf:ixl+1]

# get type+length+value
def asn1_get_all(der,asn1_struct):
    (ixs,ixf,ixl) = asn1_struct
    return der[ixs:ixl+1]

##### END ACCESS PRIMITIVES



##### HELPER FUNCTIONS

# converter
def bitstr_to_bytestr(bitstr):
    if bitstr[0] != 0x00:
        raise ValueError('Error: only 00 padded bitstr can be converted to bytestr!')
    return bitstr[1:]

# converter
def bytestr_to_int(s):
    # converts bytestring to integer
    i = 0
    for char in s:
        i <<= 8
        i |= char
    return i

# ix points to the first byte of the asn1 structure
# Returns first byte pointer, first content byte pointer and last.
def asn1_read_length(der,ix):
    first = der[ix+1]
    if  (der[ix+1] & 0x80) == 0:
        length = first
        ix_first_content_byte = ix+2
        ix_last_content_byte = ix_first_content_byte + length -1
    else:
        lengthbytes = first & 0x7F
        length = bytestr_to_int(der[ix+2:ix+2+lengthbytes])
        ix_first_content_byte = ix+2 + lengthbytes
        ix_last_content_byte = ix_first_content_byte + length -1
    return (ix,ix_first_content_byte,ix_last_content_byte)

##### END HELPER FUNCTIONS


####################### END ASN1 DECODER ############################
