
import pandas as pd

def read_dsv(neadfile):

    with open(neadfile) as f:
        fmt = f.readline(); assert( fmt[0:6] == "# NEAD" )
        hdr = f.readline(); assert(hdr == "# [HEADER]\n")

        line = ""
        attrs = {}
        attrs["format"] = fmt.split("#")[1].strip()
        while True:
            line = f.readline()
            if line == "# [DATA]\n": break
            s = line.split("=")
            key = s[0].split("#")[1].strip()
            attrs[key] = s[1].strip()
    # done reading header

    # handle special column delimiters
    assert("column_delimiter" in attrs.keys())
    if attrs["column_delimiter"] in ['" "', "' '", '\s+', "space"]:
        print("'column_delimiter' appears to be 'space'")
        attrs["column_delimiter"] = "\s+"
    if attrs["column_delimiter"] in ['\t', "tab"]:
        print("'column_delimiter' appears to be 'tab'")
        attrs["column_delimiter"] = "\t"
    delimiter=attrs["column_delimiter"]
    
    # split header fields on delimiter
    assert("fields" in attrs.keys())       
    for f in ["fields", "units_offset", "units_multiplier"]:
        if f in attrs.keys():
            # split on delimiter (or just ".split()" if delimiter is whitespace)
            attrs[f] = attrs[f].split(delimiter if delimiter.isspace() else None)

    header = attrs["fields"]
    df = pd.read_csv(neadfile, comment="#", sep=delimiter, names=header, index_col=0, parse_dates=True)
    df.attrs = attrs
    return df



def write_dsv(df, filename=None, header=None):

    sep = df.attrs["column_delimiter"]
    if sep[0:2] == '\\s':
        sep = " "
        sepstr = "space"
    if sep[0:2] == '\\t':
        sep = '\t'
        sepstr = "tab"
    
    if header is None:
        header = '# NEAD 0.1 ASCII\n'
        header += '# [HEADER]\n'
        for key in df.attrs:
            if key == "format": continue
            if isinstance(df.attrs[key], list):
                header += '# ' + key + ' = ' + " ".join(str(i) for i in df.attrs[key]) + '\n'
                continue
            if key == "column_delimiter":
                header += '# ' + key + ' = ' + sepstr + '\n'
                continue
            header += '# ' + key + ' = ' + str(df.attrs[key]) + '\n'
        header += '# [DATA]\n'

    # ISO8601
    df.index = df.index.strftime('%Y-%m-%dT%H:%M:%S')
    with open(filename, "w") as f:
        f.write(header)
        f.write(df.to_csv(header=False, sep=sep))
