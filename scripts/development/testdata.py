import requests

open_id_cert = """
-----BEGIN CERTIFICATE-----
MIIEAjCCAuoCAhAzMA0GCSqGSIb3DQEBCwUAMHsxCzAJBgNVBAYTAkRFMRswGQYD
VQQIDBJCYWRlbi1XdWVydHRlbWJlcmcxFzAVBgNVBAoMDk5leHRjbG91ZCBHbWJI
MTYwNAYDVQQDDC1OZXh0Y2xvdWQgQ29kZSBTaWduaW5nIEludGVybWVkaWF0ZSBB
dXRob3JpdHkwHhcNMTcwMjIwMDk1OTQwWhcNMjcwNTI5MDk1OTQwWjASMRAwDgYD
VQQDDAdnbHV1c3NvMIICIjANBgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAgEAsvdA
Dj6b75rL66dn6ddRqnN15uSkr25p3pPBrcIaMyBEdPtpQ+jshfeZc0+zEcTmn+1H
RgpTtE40iMTPFkJUNKPJk94vSzsKgNzLGx4e5aq84jLD3qDd4+g1HnAjZBuefJin
Hn/FCkI0VlR/ZVP8o5CQ30JQeGbpKcO2yKI5yxrcnKTdw8+/MteUfbwOZ35tgo5o
kkDOfpS2E7/2+2WafWP8pUl6Rxx2N7lRHE7gn9tvcPRFgsbAASIbHSfw0e52JlGl
BeRmJe1w2qv86/17YX27znZZzPc3jwT/s8mt2naxnrF6+DfR56JufnCaSkmRr/cq
nfLX+P8Ub8/u2VbwLcVEn8h42ukBoMxfS+kuW9vn2xxmPw5lNqXcyiizUgghvyov
93Q7/aVPxxUF7RAk2f8RTcoAVVLDgwL+Rqgl7x3PD4seX91gvHLJRZWDtUXjCVmj
egKf/M38gPUHXMtYkWVIsD4Ry55bv07Zvh1seCW+1PkUMaIbxQdMcI9VRRlJy7ql
e0zUefIk3cvOxO+xNjgLbhDgsapX+FWx3F6ikxojeB+ZYG/TUsFnBhvNM0h7SDft
/2D5gXgCpeKL2UTdHGgsrJhjE/ZyT9Mcaw4J4QkQlpvqlSKrysmqYwz+gYLzOdeZ
Frqlyv/BKjIa4s1qP/k70UQ+xbQ4S9wyMPHFO7sCAwEAATANBgkqhkiG9w0BAQsF
AAOCAQEAA6qlsLvbfWAH3W449lD5yAzk8IUG74EjFWyvG7e6F5gNUK161+Yp74GX
naLUcOCl9sixKnGcymMHhFLvNOmakjIRxBwPSEChcV2FDJCDAMac++WlwoQ0VPgb
zJY9xEZnrKyy/qRnNz3v3SrdD06MZrvbgJgGspkGIS6rhNwD7c1xS+ZS0oVcqeTM
EFhqpZKMWzn7TWvEft45FwPKZWBBBOTwjbzDaxrb/5CoelBJ+u0//8UKFT/G2Ejg
dtj9d3/WFtiw1hKuJeg//jBKt0Pvcc6jprcm1b9FlhfH4xgMfPq3s57/IH0Fd/se
Rm+7ANiBh5VLx+2T6nNi6PKnoRoN7Q==
-----END CERTIFICATE-----
"""

news_cert = """
-----BEGIN CERTIFICATE-----
MIID/zCCAucCAhACMA0GCSqGSIb3DQEBCwUAMHsxCzAJBgNVBAYTAkRFMRswGQYD
VQQIDBJCYWRlbi1XdWVydHRlbWJlcmcxFzAVBgNVBAoMDk5leHRjbG91ZCBHbWJI
MTYwNAYDVQQDDC1OZXh0Y2xvdWQgQ29kZSBTaWduaW5nIEludGVybWVkaWF0ZSBB
dXRob3JpdHkwHhcNMTYwOTEyMTI1MzI3WhcNMjYxMjE5MTI1MzI3WjAPMQ0wCwYD
VQQDDARuZXdzMIICIjANBgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAgEAtBFqOIGn
YAHIC4J+N5gB0NLv+frhFyjTIPww9TJGYZOhIyPYnN/ii36hRmyhD5znU4ZUxeXH
sHpOfwd8bvonpymd9YQfzN2Rh/qGeayp7NwEqkFi6/lg7yChJviax+87oSeh4+QP
hk9csnzRwXMLthEhIAsdaFvFzp08B5bG6++fxnSeh6lescxToefGm6p8YkLRxO4a
lKj5IOrecKq1W+xyx/SRgqEfts67XVgOs4SMMoMB8/oZ/R9MZK0on4oyliPrrf+q
D+rBIA617DcQ8Kn7O0QbVnEbijQIL5nrioFIxpGaQh8w/9WoxnXZc5oJD3R5xiKQ
tUdzPFG24JSLj9fSxpAXd6IKe8xiiwsD47uOhftiUw5UrUPywmzTafUkb4lGzfE8
47Z3Bcg862QNPgcDB2xxk2nHtqkPv1LHx47lNUuqSN0a1KfXmLXGA9U703YO6MAc
R33gw7QW5QTRpeVxJ2Dpwl8b/1eQRxUTVtpMQbFbm8qpTZSXZ74/LIllR1iB1GYf
SdzDKRkyGGUJh/CFOIxejFYyXO0wbKTorLqA2GUxlLjuFboQMeqF/6zcU3uwwiDp
atzK8kXbu7Rik6n4WvFJ/8LDtGU2vNNu0GYBO/yead5uKKYPsuVHyixQxvOcyULU
neNtCKg51gjOgGzCVbHFLFMu3+9gde2hb0MCAwEAATANBgkqhkiG9w0BAQsFAAOC
AQEAl4wNT0mJ1r+Hn1erYssEr4MdLwRGZ1UIxeI6fvZpE1NKR9RFJAqpqbcgFbWF
acRcFsSmWseQpTP8AnoIyh/kNWrR7inl8tdEM9+alc1ItN8NQKDtf2CD3ufLoR64
YFxjHbR3KQhAPei3MmCDiK5FMKdJBtKqFFoUkJPjAg/H4G5FsdNtkoNjw6Igr2+B
9AR8pPz+LivqyvLY4xHyNrCKcezrtCinj/9J25kqoGdM6p5cUbuznplN46+gT/kx
XIRiCDjmJr4YhdYjgByIgxVTiKAoTxuZ1wcj+nU4ve1MMjYEe/b30x2uLAA+cQmu
JvshYmx3I5aXFXOf3l0zEMmIuw==
-----END CERTIFICATE-----
"""

spreed_cert = """
-----BEGIN CERTIFICATE-----
MIIEAzCCAusCAhANMA0GCSqGSIb3DQEBCwUAMHsxCzAJBgNVBAYTAkRFMRswGQYD
VQQIDBJCYWRlbi1XdWVydHRlbWJlcmcxFzAVBgNVBAoMDk5leHRjbG91ZCBHbWJI
MTYwNAYDVQQDDC1OZXh0Y2xvdWQgQ29kZSBTaWduaW5nIEludGVybWVkaWF0ZSBB
dXRob3JpdHkwHhcNMTYwOTI2MTYxNzMzWhcNMjcwMTAyMTYxNzMzWjATMREwDwYD
VQQDEwhzcHJlZWRtZTCCAiIwDQYJKoZIhvcNAQEBBQADggIPADCCAgoCggIBAKLx
2dCPBLIgX948BnOdLij0YyI2+FKD6uZOvzxMaoi3rlxNf8MJgraNMzTBWEXtxT5b
7ZISNp89WEXhaQ1dwwCocodd/xow4Ek63m5nUvTZXsm+YSbMgrFbxzsBhYU7KuIE
T/jhKdzYgemzErwwN/gtwkLMfPo3jkgg6c8NPPohYv6k7V4VnsqtJ0JS0kX19FqM
MiNz9XkcncBHy9x0BSxy4+YnwbFcgIx/MtYKlBL8NkPuuJaB/6C1O+IPYhdEdnpX
+RaIue71nSStOYOqT4YDqHAIw7EmqgA1my09mmK+0Pn92GJVEAEN7JGBSQ+F32RI
dB3ivGAOVtUtVvJlepWdbHxj1xqeP+LCjWzHMLQjm0TyH8VqU4Cg/wxwAEFnBATH
aOaWwrggzY2d9KBo1mp0k71NArLbBdlHykFU4bgiSDWrXXMz0fZzLQVwGI0Eqcxc
ouf6t0kvrK8oKjrnso+FjBoT7lHV/H6ny4ufxIEDAJ/FEBV/gMizt5fDZ+DvmMw4
q+a088/lXoiI/vWPoGfOa77H5BQOt3y70Pmwv2uVYp46dtU8oat+ZvyW9iMmgP1h
JSEHj1WGGGlp45d10l4OghwfTB0OSuPUYwWR+lZnV8sukGvQzC9iRV1DGl/rREMC
cQ5ajRAtO5NPnThvN5/Zuh4n8JoDc0GK4jEZsIivAgMBAAEwDQYJKoZIhvcNAQEL
BQADggEBAGHMRbPV0WTI9r1w6m2iJRrMbZtbBb+mQr8NtOoXQwvSXWT1lXMP2N8u
LQ1a8U5UaUjeg7TnoUWTEOqU05HpwA8GZtdWZqPPQpe691kMNvfqF64g0le2kzOL
huMP9kpDGzSD8pEKf1ihxvEWNUBmwewrZTC3+b4gM+MJ3BBCfb5SCzMURLirfFST
axCNzc7veb2M98hS73w5ZE6vO+C/wz0GTsxuK0AoLitApT5naQnjvxSvSsjFPEGD
sUNUEU2Decyp0jxLVnrrpz6Y5UupfBR0V8yAv1t5Od/mCKLc5DxHsDWiKOpsob9U
JN+bdzJil2NNftihD4Dm7Ha7OS3O8W0=
-----END CERTIFICATE-----
"""

apps = [{
    'certificate': open_id_cert,
    'releases': [{
        'url': 'https://github.com/GluuFederation/nextcloud-oxd-plugin/blob'
               '/master/gluusso.tar.gz?raw=true'
    }]
}, {
    'certificate': news_cert,
    'releases': [{
        'url': 'https://github.com/nextcloud/news/releases/download/10.1.0'
               '/news.tar.gz'
    }]
}, {
    'certificate': spreed_cert,
    'releases': [{
        'url': 'https://apps.owncloud.com/CONTENT/content-files/174436'
               '-spreedme.tar.gz'
    }]
}]

admin = ('admin', 'admin')

for app in apps:
    requests.post('http://127.0.0.1:8000/api/v1/apps', auth=admin, json={
        'signature': 'signature',
        'certificate': app['certificate']
    })
    for release in app['releases']:
        requests.post('http://127.0.0.1:8000/api/v1/apps/releases', auth=admin,
                      json={
                          'download': release['url'],
                          'signature': 'signature',
                          'nightly': False
                      })
