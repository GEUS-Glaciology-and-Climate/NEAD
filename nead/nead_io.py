
import pandas as pd

def read_dsv(neadfile, **kw):

    CD_convert = {"space":'\s', "whitespace":'\s+', "tab":'\t'}
    CD = None # shortcut for column delimiter, perhaps converted using above dictionary
    
    with open(neadfile) as f:
        fmt = f.readline();
        assert(fmt[0] == "#")
        assert(fmt.split("#")[1].strip() == "NEAD 1.0 UTF-8")
        
        hdr = f.readline()
        assert(hdr[0] == "#")
        assert(hdr.split("#")[1].strip() == "[HEADER]")

        line = ""
        attrs = {}
        attrs["__format__"] = fmt.split("#")[1].strip()
        while True:
            line = f.readline()
            assert(line[0] == "#")
            
            if line == "# [DATA]\n": break
            
            key_eq_val = line.split("#")[1].strip()
            assert("=" in key_eq_val)
            key,val = [_.strip() for _ in key_eq_val.split("=")]

            # The CD property is special. We need to convert
            # from "space", "whitespace" or "tab" to regex string
            # if the CD property is not a single character.
            if key == "column_delimiter":
                if len(val) > 1: assert(val in CD_convert.keys())
                CD = val if val not in CD_convert.keys() else CD_convert[val]

            # CD property must be defined before these properties
            if key in ["fields", "units_offset", "units_multiplier"]:
                assert("column_delimiter" in attrs.keys())
                
            # If the CD property exists, use it to split any properties that contain it.
            if "column_delimiter" in attrs.keys():
                val = val.split(CD) if CD not in CD_convert.values() else val.split()

            attrs[key] = val
    # done reading header

    df = pd.read_csv(neadfile,
                     comment = "#",
                     sep = CD,
                     names = attrs["fields"],
                     **kw)
    df.attrs = attrs
    return df



# def write_dsv(df, filename=None, header=None):

#     if header is None:

#         assert(df.attrs is not None)

#         # convert column delimiter to both NEAD(human) and computer-useful values
#         cds = {'\\s':"space", '\\s+':"whitespace", '\t':"tab"}
#         cd = df.attrs["column_delimiter"]
#         sepstr = cds[cd] if cd in cds.keys() else cd
#         df.attrs.pop("column_delimiter") # we'll write it manually at top

#         header = '# NEAD 1.0 UTF-8\n'
#         header += '# [HEADER]\n'
#         header += '## Written by pyNEAD\n'
#         header += '# column_delimiter = ' + sepstr + '\n'

#         for key in df.attrs:
#             if isinstance(df.attrs[key], list):
#                 header += '# ' + key + ' = ' + " ".join(str(i) for i in df.attrs[key]) + '\n'
#             else:
#                 header += '# ' + key + ' = ' + str(df.attrs[key]) + '\n'
#         header += '# [DATA]\n'

#     # Conert datetime columns to ISO-8601 format
#     for c in df.columns:
#         if df[c].dtype == "datetime64":
#             df[c] = df[c].strftime('%Y-%m-%dT%H:%M:%S')
            
#     with open(filename, "w") as f:
#         f.write(header)
#         f.write(df.to_csv(header=False, sep=sep))
