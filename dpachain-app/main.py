#!/usr/bin/env python3
import hashlib
import json
import jwt
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
from datetime import datetime

# ─────────────────────────────────────────────────────────────────────────────
# GENESIS BLOCK
GENESIS = {
    "blocks": [
        {
            "_id": 0,
            "keys": {
                "Politechnika Warszawska": {
                    "public_key": "-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAqgI7CaWEeQ8eCVaiazg1\noPVPvbcFM2pU3cJt70feVkrY9P1FgJ+w2YJtEoitw7IrJ4j8xqxqYyNSvCbs+HmA\nbUXdO31CmMj9P2Q7Wcvu+UEo/VEyAcq6uJq50tv05IvHXlbruL0NXdgIHMV3Pxl+\nZ/Cda/lVnufo/YNmirtVZwGNbDC4TpEo1HSYwrWHVJ+o7TIX9XY5Z+g7wjrbVIuH\nJX0yQ+P5H6Aoo8nPnOqO/jfZ7bAv0dkjM6DypGoo2BjxuuIhr+FHrPA37PcpOt2S\nbp4uMDFk8Qf+I1XzQT96kMi1dcHcxLVupbn/Rd+AUAHSlVhJVBJwynLDEMI8NoOo\nWwIDAQAB\n-----END PUBLIC KEY-----\n"
                },
                "Politechnika Gdańska": {
                    "public_key": "-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAq+ee5CH50ywkagR2QrZ+\n+tpob+oB/7RnIQC/TuG+3nTbZ2LERPqeqK6DAUYkIf7/opNxzUZGQ3OFGLP0Rvbn\nTfKpBnxpdC242lG7/0sURFuAjncXhAEYkN9exvAUuZ3jjKaZAkF/wANOpKUbdD8E\n77mwfosZVfizxOhHxNmMlplyxhnZdCGefijhaq1Ua0xkqyDskld5PKtIVUHQUWJ4\nUynA9go4Q3/OJpYjbvTAAOKaA5NtxNLASLwQqeNMawuviQ8RoUGtbOIApAsM8W+4\nh1rus0Y1tp/+N26IKbsz8xm5bSSefyd1PLoUu5vDdbtuVgxMl9cbnah94Z4BHqrb\nIQIDAQAB\n-----END PUBLIC KEY-----\n"
                },
                "Uniwersytet Warszawski": {
                    "public_key": "-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAs0CLb5Oj2N4f1fIiBFd8\nJ3nuPJdsxBt3UBZBraL5Pa6jE2m19a0kUn57Md+Z3w65kcV2+Mw0Wnrc+WXP6gY/\n0zV+7DNAn/t++mRCe8yiIldZgNAyl+ptV1j4tAw8FQyr6Oi6DWYR747wftXV2gbx\nFlBWWEURB7xecJgiarsv6boECP8ABE1ol/6zpCx0VWBEEZfWpHgLaoeGO0xKpe/j\n7BLj+9wrreIiptsaB5VVvLwiYI9MbGC3SOgEncWgCSyZQ9onxzhtGY/fVShVh8v/\nVrUyliE4dStf1bBJjOdUZzKc4wNYwAeSsNr5BkefQjf+TOhODVxPYNm8JEGeKPIy\nRwIDAQAB\n-----END PUBLIC KEY-----\n"
                },
                "Uniwersytet Gdański": {
                    "public_key": "-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAypv11dUr4gLccFnwyb+e\nOAao5DsUVbxhkU3P1pK4Jc0CmGukgfTxDWhOzW8xRTUFuQTOK/Bm9249Xixz3Ga1\n0T7VXRyZQHOcxuVIFPHrUAD3s+ZnowgWQ6QTL0ntaQ6vxiE9gKQatMzTDDFDabAZ\n71PtSvMawpOm3+4Tn4/vpPJ7WZo7ULUvHVk2+ndgeHzAbLl9WHBgoxaa4Mg2W9mB\neDREvtb6WbZbsv0VTpqas+cEenjvfsf0+amCHSEZc3w5ZFrroPrHHN8oTETSeGJW\nv7XDrQOb0z3hbpVmSd7qfzxnk9UWhQLi8UZD+tHdP4K6WNsmu5GgoyCORhNErSX6\n6QIDAQAB\n-----END PUBLIC KEY-----\n"
                },
                "Akademia Górniczo-Hutnicza": {
                    "public_key": "-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAz2N2fuYATYr/vnb7NRTd\n4wOjnxFym3KwCniGhshWj4/MDG5gxg5F5cWLtWILRVts4A6Fa1aJJKJ88audHCtN\neYN/rZM1LB7uZm8M5Cyrb3TS88XTLkmhZtN0UlYWNQOQaJmc05sMWNgDjh1e4Shh\n6EH8//IqbPBaUkFYHBmWbWp6W+EUknJX5qDGGeYWkai1Y6/efonTIHROAr9Xl3Cf\nMjcsrqETcnEBRFABb4Vr9ll6sN3kAovbwcGpbJg/Ag1Ukon/F32W2//uoX1g6o5v\n828DB0DshPMNBR40rlVDsohIUhWdwSF+jV5ucvpuJ9xeEbAKF7M1wcG3BUpzs+Fr\nDQIDAQAB\n-----END PUBLIC KEY-----\n"
                },
                "Uniwersytet Jagielloński": {
                    "public_key": "-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAy6FPgBd1Bg0FzYZZyHGS\nLINkuGSvFNxvXe44CEfwCFTfD9SMYaNZI86mguK2mymlYNQqjpYedr1dBW05QiiX\n/mjdWarM4JWuvzTwVwPoO0Po1IiArqPL+QUANncovc3txL05TF/xxLkhQ0PPzptb\nhJordo6Ox4xij5EZhUlfDlc8VEtha/bmXu9G/nX9lQyVzkhNhRoTt6wnGXmv7kwH\nJ7WtjhTsshl8QLMopZOVdlDcjXGwWLJIQVyGEi3oUM+ydxO5TGv8UnP5rlS3CzGB\nsLAoF3QHgJ4u+bgoGh+TM7bIMMfUsG5jAYpWiODmJ5ScBEB6kL9JE98gMmiEwK72\n1QIDAQAB\n-----END PUBLIC KEY-----\n"
                },
                "Politechnika Wrocławska": {
                    "public_key": "-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEApuTTRZKLAEDfa1G0Wmy1\nGebdRbdbjzJevxtMhRzmok1oKAs000dZdwzj2sBpetUQnjdoRKXarRxobviURT0u\nOM7Ovz9D1jhBftyhGwFMvNeuRoTzR5WnE4FdM1cXuI0/uCMIQgng9MQJXpdLOyzj\nO/8Bbj2NxTFNpsEP2TvcaMy7IWiyhER0wMScvHFi4JRYd3Y5FpvfykWzmXTD0c06\nf7NqxG01FamCCOsmJ9jnzdsln1CY2KA1RhgETC+yWUMbo58Ij/gZAufRE7b1dDjp\n97DSpUrTHJ2UILHjhSF9KslR2P51QMpY7NyeqJX4U8CFRBXabKNbIloFsjizZo9U\nOQIDAQAB\n-----END PUBLIC KEY-----\n"
                },
                "Uniwersytet Wrocławski": {
                    "public_key": "-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAqQgnrIYID1a1Din/bed/\nmEtT7wu7Isd6nac6yCISsmpKjCIx8fsiYsnxZhDYYLr/Dw1C8OIGmbNvkfKgPrMb\npCDqs+nTc7/0Pi2Q6mof5L8OMdqGZ1keYRtl9rKkhZIwau0W/gTbatbrI0yHII6x\nsV/+WCoOzeGnGlCIqC3e6VCkFbKtz23eKy00HJkaQlahAzosk6pDDgPkIldDN/4E\nyyXWKaVoWZ5eDy53vDwKNWDUFwUToA69y/RHW7idZSXxqix2o5B/PGU6Dzu87U9c\n1W+NAm8x8PCsDczk+hAP3vs4oQw3DqWFHnGXyKGcqHdLNmDOngvCyk3wOvO7baFW\nCQIDAQAB\n-----END PUBLIC KEY-----\n"
                }
            },
            "hash": "3299549fcb1c64c220753521fa81c4ada258a0f6b9f812e0124bfb464f4ed9ea",
            "signed_hash": "3299549fcb1c64c220753521fa81c4ada258a0f6b9f812e0124bfb464f4ed9ea",
            "jwt_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsInVuaXZlcnNpdHkiOiJQb2xpdGVjaG5pa2EgV2Fyc3phd3NrYSJ9.eyJQb2xpdGVjaG5pa2EgV2Fyc3phd3NrYSI6eyJwdWJsaWNfa2V5IjoiLS0tLS1CRUdJTiBQVUJMSUMgS0VZLS0tLS1cbk1JSUJJakFOQmdrcWhraUc5dzBCQVFFRkFBT0NBUThBTUlJQkNnS0NBUUVBcWdJN0NhV0VlUThlQ1ZhaWF6ZzFcbm9QVlB2YmNGTTJwVTNjSnQ3MGZlVmtyWTlQMUZnSit3MllKdEVvaXR3N0lySjRqOHhxeHFZeU5TdkNicytIbUFcbmJVWGRPMzFDbU1qOVAyUTdXY3Z1K1VFby9WRXlBY3E2dUpxNTB0djA1SXZIWGxicnVMME5YZGdJSE1WM1B4bCtcblovQ2RhL2xWbnVmby9ZTm1pcnRWWndHTmJEQzRUcEVvMUhTWXdyV0hWSitvN1RJWDlYWTVaK2c3d2pyYlZJdUhcbkpYMHlRK1A1SDZBb284blBuT3FPL2pmWjdiQXYwZGtqTTZEeXBHb28yQmp4dXVJaHIrRkhyUEEzN1BjcE90MlNcbmJwNHVNREZrOFFmK0kxWHpRVDk2a01pMWRjSGN4TFZ1cGJuL1JkK0FVQUhTbFZoSlZCSnd5bkxERU1JOE5vT29cbld3SURBUUFCXG4tLS0tLUVORCBQVUJMSUMgS0VZLS0tLS1cbiJ9LCJQb2xpdGVjaG5pa2EgR2RhXHUwMTQ0c2thIjp7InB1YmxpY19rZXkiOiItLS0tLUJFR0lOIFBVQkxJQyBLRVktLS0tLVxuTUlJQklqQU5CZ2txaGtpRzl3MEJBUUVGQUFPQ0FROEFNSUlCQ2dLQ0FRRUFxK2VlNUNINTB5d2thZ1IyUXJaK1xuK3Rwb2Irb0IvN1JuSVFDL1R1RyszblRiWjJMRVJQcWVxSzZEQVVZa0lmNy9vcE54elVaR1EzT0ZHTFAwUnZiblxuVGZLcEJueHBkQzI0MmxHNy8wc1VSRnVBam5jWGhBRVlrTjlleHZBVXVaM2pqS2FaQWtGL3dBTk9wS1ViZEQ4RVxuNzdtd2Zvc1pWZml6eE9oSHhObU1scGx5eGhuWmRDR2VmaWpoYXExVWEweGtxeURza2xkNVBLdElWVUhRVVdKNFxuVXluQTlnbzRRMy9PSnBZamJ2VEFBT0thQTVOdHhOTEFTTHdRcWVOTWF3dXZpUThSb1VHdGJPSUFwQXNNOFcrNFxuaDFydXMwWTF0cC8rTjI2SUtic3o4eG01YlNTZWZ5ZDFQTG9VdTV2RGRidHVWZ3hNbDljYm5haDk0WjRCSHFyYlxuSVFJREFRQUJcbi0tLS0tRU5EIFBVQkxJQyBLRVktLS0tLVxuIn0sIlVuaXdlcnN5dGV0IFdhcnN6YXdza2kiOnsicHVibGljX2tleSI6Ii0tLS0tQkVHSU4gUFVCTElDIEtFWS0tLS0tXG5NSUlCSWpBTkJna3Foa2lHOXcwQkFRRUZBQU9DQVE4QU1JSUJDZ0tDQVFFQXMwQ0xiNU9qMk40ZjFmSWlCRmQ4XG5KM251UEpkc3hCdDNVQlpCcmFMNVBhNmpFMm0xOWEwa1VuNTdNZCtaM3c2NWtjVjIrTXcwV25yYytXWFA2Z1kvXG4welYrN0ROQW4vdCsrbVJDZTh5aUlsZFpnTkF5bCtwdFYxajR0QXc4RlF5cjZPaTZEV1lSNzQ3d2Z0WFYyZ2J4XG5GbEJXV0VVUkI3eGVjSmdpYXJzdjZib0VDUDhBQkUxb2wvNnpwQ3gwVldCRUVaZldwSGdMYW9lR08weEtwZS9qXG43QkxqKzl3cnJlSWlwdHNhQjVWVnZMd2lZSTlNYkdDM1NPZ0VuY1dnQ1N5WlE5b254emh0R1kvZlZTaFZoOHYvXG5WclV5bGlFNGRTdGYxYkJKak9kVVp6S2M0d05Zd0FlU3NOcjVCa2VmUWpmK1RPaE9EVnhQWU5tOEpFR2VLUEl5XG5Sd0lEQVFBQlxuLS0tLS1FTkQgUFVCTElDIEtFWS0tLS0tXG4ifSwiVW5pd2Vyc3l0ZXQgR2RhXHUwMTQ0c2tpIjp7InB1YmxpY19rZXkiOiItLS0tLUJFR0lOIFBVQkxJQyBLRVktLS0tLVxuTUlJQklqQU5CZ2txaGtpRzl3MEJBUUVGQUFPQ0FROEFNSUlCQ2dLQ0FRRUF5cHYxMWRVcjRnTGNjRm53eWIrZVxuT0FhbzVEc1VWYnhoa1UzUDFwSzRKYzBDbUd1a2dmVHhEV2hPelc4eFJUVUZ1UVRPSy9CbTkyNDlYaXh6M0dhMVxuMFQ3VlhSeVpRSE9jeHVWSUZQSHJVQUQzcytabm93Z1dRNlFUTDBudGFRNnZ4aUU5Z0tRYXRNelREREZEYWJBWlxuNzFQdFN2TWF3cE9tMys0VG40L3ZwUEo3V1pvN1VMVXZIVmsyK25kZ2VIekFiTGw5V0hCZ294YWE0TWcyVzltQlxuZURSRXZ0YjZXYlpic3YwVlRwcWFzK2NFZW5qdmZzZjArYW1DSFNFWmMzdzVaRnJyb1BySEhOOG9URVRTZUdKV1xudjdYRHJRT2IwejNoYnBWbVNkN3FmenhuazlVV2hRTGk4VVpEK3RIZFA0SzZXTnNtdTVHZ295Q09SaE5FclNYNlxuNlFJREFRQUJcbi0tLS0tRU5EIFBVQkxJQyBLRVktLS0tLVxuIn0sIkFrYWRlbWlhIEdcdTAwZjNybmljem8tSHV0bmljemEiOnsicHVibGljX2tleSI6Ii0tLS0tQkVHSU4gUFVCTElDIEtFWS0tLS0tXG5NSUlCSWpBTkJna3Foa2lHOXcwQkFRRUZBQU9DQVE4QU1JSUJDZ0tDQVFFQXoyTjJmdVlBVFlyL3ZuYjdOUlRkXG40d09qbnhGeW0zS3dDbmlHaHNoV2o0L01ERzVneGc1RjVjV0x0V0lMUlZ0czRBNkZhMWFKSktKODhhdWRIQ3ROXG5lWU4vclpNMUxCN3VabThNNUN5cmIzVFM4OFhUTGttaFp0TjBVbFlXTlFPUWFKbWMwNXNNV05nRGpoMWU0U2hoXG42RUg4Ly9JcWJQQmFVa0ZZSEJtV2JXcDZXK0VVa25KWDVxREdHZVlXa2FpMVk2L2Vmb25USUhST0FyOVhsM0NmXG5NamNzcnFFVGNuRUJSRkFCYjRWcjlsbDZzTjNrQW92YndjR3BiSmcvQWcxVWtvbi9GMzJXMi8vdW9YMWc2bzV2XG44MjhEQjBEc2hQTU5CUjQwcmxWRHNvaElVaFdkd1NGK2pWNXVjdnB1Sjl4ZUViQUtGN00xd2NHM0JVcHpzK0ZyXG5EUUlEQVFBQlxuLS0tLS1FTkQgUFVCTElDIEtFWS0tLS0tXG4ifSwiVW5pd2Vyc3l0ZXQgSmFnaWVsbG9cdTAxNDRza2kiOnsicHVibGljX2tleSI6Ii0tLS0tQkVHSU4gUFVCTElDIEtFWS0tLS0tXG5NSUlCSWpBTkJna3Foa2lHOXcwQkFRRUZBQU9DQVE4QU1JSUJDZ0tDQVFFQXk2RlBnQmQxQmcwRnpZWlp5SEdTXG5MSU5rdUdTdkZOeHZYZTQ0Q0Vmd0NGVGZEOVNNWWFOWkk4Nm1ndUsybXltbFlOUXFqcFllZHIxZEJXMDVRaWlYXG4vbWpkV2FyTTRKV3V2elR3VndQb08wUG8xSWlBcnFQTCtRVUFObmNvdmMzdHhMMDVURi94eExraFEwUFB6cHRiXG5oSm9yZG82T3g0eGlqNUVaaFVsZkRsYzhWRXRoYS9ibVh1OUcvblg5bFF5VnpraE5oUm9UdDZ3bkdYbXY3a3dIXG5KN1d0amhUc3NobDhRTE1vcFpPVmRsRGNqWEd3V0xKSVFWeUdFaTNvVU0reWR4TzVUR3Y4VW5QNXJsUzNDekdCXG5zTEFvRjNRSGdKNHUrYmdvR2grVE03YklNTWZVc0c1akFZcFdpT0RtSjVTY0JFQjZrTDlKRTk4Z01taUV3SzcyXG4xUUlEQVFBQlxuLS0tLS1FTkQgUFVCTElDIEtFWS0tLS0tXG4ifSwiUG9saXRlY2huaWthIFdyb2NcdTAxNDJhd3NrYSI6eyJwdWJsaWNfa2V5IjoiLS0tLS1CRUdJTiBQVUJMSUMgS0VZLS0tLS1cbk1JSUJJakFOQmdrcWhraUc5dzBCQVFFRkFBT0NBUThBTUlJQkNnS0NBUUVBcHVUVFJaS0xBRURmYTFHMFdteTFcbkdlYmRSYmRianpKZXZ4dE1oUnptb2sxb0tBczAwMGRaZHd6ajJzQnBldFVRbmpkb1JLWGFyUnhvYnZpVVJUMHVcbk9NN092ejlEMWpoQmZ0eWhHd0ZNdk5ldVJvVHpSNVduRTRGZE0xY1h1STAvdUNNSVFnbmc5TVFKWHBkTE95empcbk8vOEJiajJOeFRGTnBzRVAyVHZjYU15N0lXaXloRVIwd01TY3ZIRmk0SlJZZDNZNUZwdmZ5a1d6bVhURDBjMDZcbmY3TnF4RzAxRmFtQ0NPc21KOWpuemRzbG4xQ1kyS0ExUmhnRVRDK3lXVU1ibzU4SWovZ1pBdWZSRTdiMWREanBcbjk3RFNwVXJUSEoyVUlMSGpoU0Y5S3NsUjJQNTFRTXBZN055ZXFKWDRVOENGUkJYYWJLTmJJbG9Gc2ppelpvOVVcbk9RSURBUUFCXG4tLS0tLUVORCBQVUJMSUMgS0VZLS0tLS1cbiJ9LCJVbml3ZXJzeXRldCBXcm9jXHUwMTQyYXdza2kiOnsicHVibGljX2tleSI6Ii0tLS0tQkVHSU4gUFVCTElDIEtFWS0tLS0tXG5NSUlCSWpBTkJna3Foa2lHOXcwQkFRRUZBQU9DQVE4QU1JSUJDZ0tDQVFFQXFRZ25ySVlJRDFhMURpbi9iZWQvXG5tRXRUN3d1N0lzZDZuYWM2eUNJU3NtcEtqQ0l4OGZzaVlzbnhaaERZWUxyL0R3MUM4T0lHbWJOdmtmS2dQck1iXG5wQ0RxcytuVGM3LzBQaTJRNm1vZjVMOE9NZHFHWjFrZVlSdGw5cktraFpJd2F1MFcvZ1RiYXRickkweUhJSTZ4XG5zVi8rV0NvT3plR25HbENJcUMzZTZWQ2tGYkt0ejIzZUt5MDBISmthUWxhaEF6b3NrNnBERGdQa0lsZEROLzRFXG55eVhXS2FWb1daNWVEeTUzdkR3S05XRFVGd1VUb0E2OXkvUkhXN2lkWlNYeHFpeDJvNUIvUEdVNkR6dTg3VTljXG4xVytOQW04eDhQQ3NEY3prK2hBUDN2czRvUXczRHFXRkhuR1h5S0djcUhkTE5tRE9uZ3ZDeWszd092TzdiYUZXXG5DUUlEQVFBQlxuLS0tLS1FTkQgUFVCTElDIEtFWS0tLS0tXG4ifSwic2lnbmVkX2hhc2giOiJoTmtyb2hVVkJ0R1FPYWYwK1B2bmdFa1YxcWJkcjhQbGxGTzd1L2N0M1hRUXdqek9aa0poTVgwUXdnaG45N2tXRHF1d2YwK3hIbG9aYWk1Y3NqUVJFbGRnaGJHdUc5ZTFORmRZaDhDOG1mR3V2bloraG92MkNESUJ1QmtxeTJjYkJ2dGpDR25xSTd6QVN1WWZKb2ZsVXJSdWVVTW5zWmVzTEVQc0pORWFFY0UvekJYV1B5MHp6QXVjbldyMUtpVWNRaDAxeURIQjZDWERKK3NkVVN3clRRRGVESFFOUzJBdjlneFZjSVZ0SEVXMjZOTkMraENVU2krR1dwTGFIQlFaMkNtdzMyYjU2TDJEN0c0RWZISU5QWHZPZysvc0Jrczl2UlNQVTUvM3ljNDVKd0tLS1dnSXJhY1l4TW04dHhHUWo2ZVdMVUtnSDNEN2U3U2Q3RFNlemc9PSJ9.pY1792AuofFLpm-Z_Qflq0pJ1opHjlUWpR5-SsKam_i01cg5GkVinsQtWYIpFN1ID9lztmggK-kPEysbQWqpXhxnFVXfKpi-e8v1exST7pfMNSZTyY6FlqOARz4hPmA6A_q27TKfJSMCg-PKr5WhtwroQRjxdjZTUMAfoBXCrQ2J5D5Rm31GQs_pvnVweoW_q1UDg1TwoDgekwsnDPsh_l4vSZu308KmaTfXJQrJnZLByetVzBbCmy00_2aNfti_peLbzM900eB3YV-9mYtYl2HSWvpN68E3drb2wl1tPo7ErAAjbN1-lE5U_6_tx_cEbe2lEREt4_fCB6nQqBstOg"
        }
    ]}
# ─────────────────────────────────────────────────────────────────────────────


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("DPAChain Authenticator")
        self.geometry("4560x2840")
        self.minsize(700, 600)

        self.uploaded_pdf_bytes = None
        self.calculated_pdf_hash = None
        self.jwt_payload = None

        self.style = ttk.Style(self)
        self.style.configure("Treeview", rowheight=32, font=('Segoe UI', 10))
        self.style.configure("Treeview.Heading", font=('Segoe UI', 12, 'bold'))

        self.configure(padx=20, pady=20)
        self.create_widgets()
        self.setup_grid()

    def create_widgets(self):
        self.title_label = tk.Label(
            self, text="DPAChain Authenticator", font=("Segoe UI", 18, "bold"))
        self.title_label.grid(row=0, column=0, columnspan=3,
                              pady=(0, 10), sticky="n")

        tk.Label(self, text="Paste JWT token below:").grid(
            row=1, column=0, columnspan=3, sticky="w")
        self.jwt_text = scrolledtext.ScrolledText(self, wrap=tk.WORD, height=8)
        self.jwt_text.grid(row=2, column=0, columnspan=3,
                           sticky="nsew", pady=(0, 10))

        self.upload_btn = tk.Button(
            self, text="Upload PDF (optional)", command=self.upload_pdf)
        self.upload_btn.grid(row=3, column=0, pady=(0, 10), sticky="w")

        btn_frame = tk.Frame(self)
        btn_frame.grid(row=4, column=0, columnspan=3, pady=(5, 10))

        self.auth_btn = tk.Button(
            btn_frame, text="Authenticate", command=self.authenticate)
        self.auth_btn.pack(side="left", padx=(0, 5))

        self.clear_btn = tk.Button(
            btn_frame, text="Clear", command=self.clear_input)
        self.clear_btn.pack(side="left")

        self.result_label = tk.Label(self, text="", font=("Segoe UI", 14))
        self.result_label.grid(row=5, column=0, columnspan=3, pady=(5, 5))

        # PDF hash input + copy button
        self.pdf_hash_entry = tk.Entry(self, font=(
            "Segoe UI", 10), state="readonly", width=80)
        self.pdf_hash_entry.grid(
            row=6, column=0, columnspan=2, sticky="ew", pady=(5, 5))

        self.copy_hash_btn = tk.Button(
            self, text="Copy Hash", command=self.copy_pdf_hash)
        self.copy_hash_btn.grid(row=6, column=2, sticky="w", padx=(5, 0))

        self.summary_frame = tk.Frame(self)
        self.summary_frame.grid(
            row=7, column=0, columnspan=3, sticky="ew", pady=(5, 10))
        self.summary_labels = {}
        summary_fields = [
            ('Title', 'title'),
            ('Type', 'diploma_type'),
            ('Author', 'authors'),
            ('Supervisor', 'supervisor'),
            ('Reviewer', 'reviewer'),
            ('University', 'university'),
            ('Faculty', 'faculty'),
            ('Date Of Defense', 'date_of_defense'),
        ]
        for i, (disp, key) in enumerate(summary_fields):
            lbl = tk.Label(self.summary_frame, text=f"{disp}:", font=(
                "Segoe UI", 12), anchor="w")
            lbl.grid(row=i, column=0, sticky="w", pady=2)
            val = tk.Label(self.summary_frame, text="", font=(
                "Segoe UI", 12, "bold"), anchor="w")
            val.grid(row=i, column=1, sticky="w", padx=(5, 0), pady=2)
            self.summary_labels[key] = val

        self.tree = ttk.Treeview(self, columns=(
            "Key", "Value"), show="headings")
        self.tree.heading("Key", text="Key")
        self.tree.heading("Value", text="Value")
        self.tree.column("Key", width=300, anchor="w")
        self.tree.column("Value", width=550, anchor="w")
        self.tree.grid(row=8, column=0, columnspan=3, sticky="nsew")

        vsb = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        vsb.grid(row=8, column=3, sticky='ns')
        self.tree.configure(yscrollcommand=vsb.set)

    def setup_grid(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(2, weight=0)
        self.grid_rowconfigure(8, weight=1)

    def upload_pdf(self):
        path = filedialog.askopenfilename(
            title="Select PDF", filetypes=[("PDF files", "*.pdf")])
        if path:
            with open(path, 'rb') as f:
                self.uploaded_pdf_bytes = f.read()
            self.calculated_pdf_hash = hashlib.sha256(
                self.uploaded_pdf_bytes).hexdigest()

            self.pdf_hash_entry.configure(state="normal")
            self.pdf_hash_entry.delete(0, tk.END)
            self.pdf_hash_entry.insert(0, self.calculated_pdf_hash)
            self.pdf_hash_entry.configure(state="readonly")

            if self.jwt_payload:
                self.compare_pdf_hash()
            else:
                self.result_label.config(
                    text="PDF hash calculated, waiting for JWT.", fg="blue")

            messagebox.showinfo("PDF Uploaded", "PDF uploaded successfully!")

    def copy_pdf_hash(self):
        self.clipboard_clear()
        self.clipboard_append(self.calculated_pdf_hash or "")
        self.update()
        messagebox.showinfo("Copied", "PDF hash copied to clipboard!")

    def clear_input(self):
        self.jwt_text.delete('1.0', tk.END)
        self.result_label.config(text="")
        self.pdf_hash_entry.configure(state="normal")
        self.pdf_hash_entry.delete(0, tk.END)
        self.pdf_hash_entry.configure(state="readonly")
        for item in self.tree.get_children():
            self.tree.delete(item)
        for lbl in self.summary_labels.values():
            lbl.config(text="")
        self.uploaded_pdf_bytes = None
        self.calculated_pdf_hash = None
        self.jwt_payload = None

    def authenticate(self):
        token = self.jwt_text.get("1.0", "end").strip()
        if not token:
            messagebox.showwarning(
                "Input required", "Please paste a JWT token.")
            return

        for item in self.tree.get_children():
            self.tree.delete(item)
        for lbl in self.summary_labels.values():
            lbl.config(text="")
        self.result_label.config(text="")
        self.pdf_hash_entry.configure(state="normal")
        self.pdf_hash_entry.delete(0, tk.END)
        self.pdf_hash_entry.configure(state="readonly")

        try:
            header = jwt.get_unverified_header(token)
            university = header.get("university")
            if not university:
                raise KeyError("no 'university' header")
        except Exception as e:
            self.show_result(False, f"Bad token header: {e}")
            return

        keys = GENESIS["blocks"][0]["keys"]
        uni_entry = keys.get(university)
        if not uni_entry:
            self.show_result(False, f"Unknown university: {university}")
            return
        public_key = uni_entry["public_key"]

        try:
            payload = jwt.decode(
                token,
                public_key,
                algorithms=["RS256"],
                options={"verify_aud": False}
            )
        except jwt.InvalidSignatureError:
            self.show_result(False, "Invalid signature")
            return
        except Exception as e:
            self.show_result(False, f"Failed to decode: {e}")
            return

        self.jwt_payload = payload
        self.show_result(True, "✔️ VALID TOKEN")
        self.show_summary(payload)
        self.show_payload(payload)

        if self.calculated_pdf_hash:
            self.compare_pdf_hash()

    def compare_pdf_hash(self):
        token_pdf_hash = self.jwt_payload.get(
            'pdf_hash') if self.jwt_payload else None
        if not token_pdf_hash:
            self.result_label.config(text="No pdf_hash in token.", fg="orange")
        elif token_pdf_hash == self.calculated_pdf_hash:
            self.result_label.config(text="✔️ PDF hash matches!", fg="green")
        else:
            self.result_label.config(
                text="❌ PDF hash does NOT match!", fg="red")

    def show_result(self, valid: bool, msg: str):
        self.result_label.configure(
            text=msg,
            fg="green" if valid else "red"
        )

    def show_summary(self, payload: dict):
        for key, lbl in self.summary_labels.items():
            value = payload.get(key)
            if key == 'authors' and isinstance(value, list):
                authors_id = payload.get('authors_id', [])
                authors_with_ids = [
                    f"{author} ({authors_id[i]})" for i, author in enumerate(value) if i < len(authors_id)
                ]
                authors = ", ".join(authors_with_ids)
                lbl.config(text=authors)
                continue
            if isinstance(value, list):
                value = ', '.join(value)
            if key == 'date_of_defense' and isinstance(value, str):
                try:
                    dt = datetime.fromisoformat(value)
                    value = dt.strftime('%Y-%m-%d')
                except ValueError:
                    pass
            lbl.config(text=str(value))

    def show_payload(self, payload: dict):
        for k, v in payload.items():
            self.tree.insert('', tk.END, values=(
                k, json.dumps(v, ensure_ascii=False)))

if __name__ == "__main__":
    app = App()
    app.mainloop()
