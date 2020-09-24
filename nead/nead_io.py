
import numpy as np
import pandas as pd

def read_nead(neadfile, MKS=None, **kw):

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

        # default header values
        # attrs["column_delimiter"] = ","
        
        while True:
            line = f.readline()
            assert((line[0] == "#") | (line[0] == '\n'))
            
            if line == "# [DATA]\n": break # done reading header
            
            key_eq_val = line.split("#")[1].strip()
            assert("=" in key_eq_val)
            key,val = [_.strip() for _ in key_eq_val.split("=")]

            # column_delimiter (CD) property must be defined before these properties
            if key in ["fields", "units_offset", "units_multiplier"]:
                assert("column_delimiter" in attrs.keys())
                
            # If the CD property exists, use it to split any properties that contain it.
            if "column_delimiter" in attrs.keys():
                CD = attrs['column_delimiter']
                if CD in val:
                    val = [_.strip() for _ in val.split(CD)]
                    # convert to numeric if only contains numbers
                    if all([str(s).strip('-').replace('.','').isdigit() for s in val]):
                        val = np.array(val).astype(np.float)

            attrs[key] = val
    # done reading header

    df = pd.read_csv(neadfile,
                     comment = "#",
                     sep = attrs['column_delimiter'],
                     names = attrs["fields"],
                     **kw)

    # # convert to MKS by adding units_offset and units_multiplier to a
    # # multi-header, selecting numeric columns, and converting.
    if (MKS != False):
        assert('units_offset' in attrs.keys())
        assert('units_multiplier' in attrs.keys())
        uo = attrs['units_offset']
        um = attrs['units_multiplier']
        df.columns = pd.MultiIndex.from_tuples(list(zip(df.columns, uo, um)), names=['name','uo','um'])
        df_n = df.select_dtypes(include='number')
        uo = df_n.columns.get_level_values('uo')
        um = df_n.columns.get_level_values('um')
        df_n = (df_n  * um) + uo
        for c in df_n.columns: df[c] = df_n[c] # move back over
        df.columns = df.columns.get_level_values('name')

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
