import polyline
import json

# Extracted encoded polyline from your JSON snippet
encoded_polyline = "mgloA_xciNeBYDUPD~Dp@vEz@tCf@dBZlJ`BjDf@jBZbAR`@HpCh@fEn@tCb@fDl@jAH|@FL?xEJVCZ@XJtDhA`AZxDv@jGz@rDr@hBl@xDr@jB\\hCj@fEfAtBf@z@LL@dCVbANz@VdFzAhA^nGrBvJrCnA`@nBt@vA`@|Cz@r@R~DhAxA`@f@}Cl@qEp@_EH[FGLAt@PtBd@fF~@rDv@x@PpBb@dC`@`Ev@~@LxBPt@L|@R~AXfFv@CL^Dh@HbALRFDFJFtCl@pDp@|Dx@x@PxDp@xF|@lF`AxBb@~Ch@|@Pn@HzAXxANZFz@F|Cn@dH~@pBXhAH|BVvBXbC\\jFl@zKhAzBNtBLz@BvAPrEb@rNjAdFb@lEb@hAN~Fn@VCXOFOHi@F}AUeB?cAFSX}@x@mDh@oBXw@HMZYLGTGZE^@d@HpEfAhCh@b@Jv@DtAPtC\\~Dd@`Dl@pCh@tFtAlG|AjBb@fAPhEbAdK|BxMzC`@LbD`A`EzAZJlDp@zB`@x@LHDZ^fAxBRz@NrA@f@IhDSjFIvAEpA@d@?b@@Dt@jBb@x@t@~@lBhApH~DhAp@ORA`@AbAFpBTzFHpC?ZNrAh@~F@BTzBF~@Nj@Fb@DHHDt@A~AGlCIp@?bAHjBTPAPETKTQFMTy@TaAVSh@KfNUOBNCrFQnAI^KlB~BlC~C\\`@l@n@r@b@r@Zd@Nz@LVJx@r@BDn@dAxBnCz@v@pAbAp@Xx@ZRTXZn@nAZj@tBtBdAdAn@x@Vb@HPFNLj@Fz@BrABNJRjBxCPMLAZBjD`@nFf@zAP^Rb@d@pBjCrCxDNHPB\\@dBs@j@WPC\\ClA@bAJvCTTGl@P`A\\~@f@@CbBt@t@PfEVnEj@b@HfAPz@RZXVDj@F|AHzAHH@nDq@t@Ir@E~CCJFv@Hr@@ZCRINMJOFQ@ETsAPk@Tk@d@s@`CuBf@i@n@Kn@Cv@CpBIJ?LK`AQhAMxBQ~@WfBw@dEyBv@[nAo@d@G`@ExAGh@Ap@FpCXj@Nj@PjAVd@FlAJjABv@?x@AvDDh@ApFa@vCWxASn@LH@zGv@RFRV`@T`DfAh@Nj@JfEl@nEd@?Ph@FzDb@nAFzBFxATLBVFZ@zAj@x@f@tA~@r@f@hC`BnItDnAd@fBl@~@RlAFjB@|FZLX^fD@h@Bd@BVFNZTz@f@hDnBhDjB|Av@FBb@P|A\\|AJlBB`IHbFBfDDFCPGLC`@CtCDrDJ`BHv@SVMl@QP@NHJNVh@Pl@Z|@b@~@l@rARPVThB\\~G|@VHlE`@|Gv@bCN`BPhBNrCT`@H~CXlCVxCHhCBbBI|A@xEIvEW~@A|F@hJJxBDr@DjFV\\kFb@sMJe@`BJ"

# Decode the polyline
decoded_polyline = polyline.decode(encoded_polyline)

# Swap latitude and longitude pairs
swapped_decoded_polyline = [(lon, lat) for lat, lon in decoded_polyline]

# Convert swapped decoded polyline to GeoJSON format
geojson = {
    "type": "LineString",
    "coordinates": swapped_decoded_polyline
}

# Save GeoJSON to a file
with open("decoded_route.geojson", "w") as file:
    json.dump(geojson, file)
