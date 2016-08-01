# -*- coding: utf-8 -*-

# Copyright (c) 2016, Thierry Lemeunier <thierry at lemeunier dot net>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this 
# list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
# OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
# OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
# ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import ssl
import time
import calendar

from .asn1tinydecoder import asn1_node_root, asn1_node_first_child,\
                             asn1_node_next, asn1_get_value_of_type

"""
A simple X509 class to control the certificate validity period.

It uses the ASN.1 decoder developed by Jens Getreu:
http://www.getreu.net/public/downloads/software/ASN1_decoder

An extract of the ASN.1 syntax is the following
(see https://tools.ietf.org/html/rfc5280):

Certificate  ::=  SEQUENCE  {
                    tbsCertificate       TBSCertificate,
                    signatureAlgorithm   AlgorithmIdentifier,
                    signature            BIT STRING  }

TBSCertificate  ::=  SEQUENCE  {
                    version         [0]  Version DEFAULT v1,
                    serialNumber         CertificateSerialNumber,
                    signature            AlgorithmIdentifier,
                    issuer               Name,
                    validity             Validity,
                    subject              Name,
                    subjectPublicKeyInfo SubjectPublicKeyInfo,
                    issuerUniqueID  [1]  IMPLICIT UniqueIdentifier OPTIONAL,
                                         -- If present, version MUST be v2 or v3
                    subjectUniqueID [2]  IMPLICIT UniqueIdentifier OPTIONAL,
                                         -- If present, version MUST be v2 or v3
                    extensions      [3]  Extensions OPTIONAL
                                         -- If present, version MUST be v3 --  }

Version  ::=  INTEGER  {  v1(0), v2(1), v3(2)  }

CertificateSerialNumber  ::=  INTEGER

AlgorithmIdentifier  ::=  SEQUENCE  {
                    algorithm            OBJECT IDENTIFIER,
                    parameters           ANY DEFINED BY algorithm OPTIONAL  }
                                         -- contains a value of the type
                                         -- registered for use with the
                                         -- algorithm object identifier value

Name ::= CHOICE { -- only one possibility for now --
                    rdnSequence  RDNSequence }

Validity ::= SEQUENCE {
                    notBefore      Time,
                    notAfter       Time  }

Time ::= CHOICE {
                    utcTime        UTCTime,
                    generalTime    GeneralizedTime  }
"""


class X509:
    """
    A simple class to represent a X509 certificate.
    The certificate is encoding according the DER format.
    """

    def __init__(self, filename):
        """Initialize the X509 object"""
        self.certfile = filename
        with open(self.certfile) as file:
            self.der = ssl.PEM_cert_to_DER_cert(file.read())
            
    def check_validity_period(self):
        """
        Control the validity period. Raise an exception if the control fails.
        """
        
        # Navigate to the 'Validity' sequence
        i = asn1_node_root(self.der)  # Certificate
        i = asn1_node_first_child(self.der, i)  # tbsCertificate
        i = asn1_node_first_child(self.der, i)  # version
        i = asn1_node_next(self.der, i)  # serialNumber
        i = asn1_node_next(self.der, i)  # signature
        i = asn1_node_next(self.der, i)  # issuer
        i = asn1_node_next(self.der, i)  # validity
        
        # Get the validity period
        i = asn1_node_first_child(self.der, i)  # notBefore
        bytestr = asn1_get_value_of_type(self.der, i, 'UTCTime')
        not_valid_before = time.strptime(
            bytestr.decode('ASCII', 'strict'), '%y%m%d%H%M%SZ')

        i = asn1_node_next(self.der, i)  # notAfter
        bytestr = asn1_get_value_of_type(self.der, i, 'UTCTime')
        not_valid_after = time.strptime(
            bytestr.decode('ASCII', 'strict'), '%y%m%d%H%M%SZ')

        # Control the validity period
        if calendar.timegm(not_valid_before) > calendar.timegm(time.gmtime()):
            str_not_valid_before = time.strftime("%d %b %Y %H:%M:%S", not_valid_before)
            raise Exception("The certifcat '{}' has an invalid period of validty : not before {}"
                            .format(self.certfile, str_not_valid_before))

        if calendar.timegm(not_valid_after) < calendar.timegm(time.gmtime()):
            str_not_valid_after = time.strftime("%d %b %Y %H:%M:%S", not_valid_after)
            raise Exception("The certifcat '{}' has an invalid period of validty : not after {}"
                            .format(self.certfile, str_not_valid_after))
