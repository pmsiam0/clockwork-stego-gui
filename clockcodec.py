import math, struct, hashlib
from xml.etree.ElementTree import Element, SubElement, tostring, parse

def _bytes_to_bitstring(b):
    return ''.join(f'{x:08b}' for x in b)

def _bitstring_to_6groups(bs):
    pad = (-len(bs)) % 6
    bs2 = bs + '0'*pad
    return [bs2[i:i+6] for i in range(0, len(bs2), 6)]

def _render_clock(svg, cx, cy, r, a_idx, b_idx, ident):
    SubElement(svg, 'circle', cx=str(cx), cy=str(cy), r=str(r), fill="none", stroke="#000", stroke_width="0.5")
    SubElement(svg, 'circle', cx=str(cx), cy=str(cy), r=str(0.8), fill="#000")
    angA = math.radians(a_idx*45 - 90)
    xA = cx + (r*0.5)*math.cos(angA)
    yA = cy + (r*0.5)*math.sin(angA)
    SubElement(svg, 'line', id=f"{ident}_A", x1=str(cx), y1=str(cy), x2=str(xA), y2=str(yA), stroke="#000", stroke_width="1.5", stroke_linecap="round")
    angB = math.radians(b_idx*45 - 90)
    xB = cx + (r*0.85)*math.cos(angB)
    yB = cy + (r*0.85)*math.sin(angB)
    SubElement(svg, 'line', id=f"{ident}_B", x1=str(cx), y1=str(cy), x2=str(xB), y2=str(yB), stroke="#000", stroke_width="1", stroke_linecap="round")

def _key6(passphrase):
    if not passphrase:
        return 0
    h = hashlib.sha256(passphrase.encode('utf-8')).digest()
    return h[0] & 0b00111111

def encode_message_to_svg(message, out_svg_path, key_passphrase=None, cols=16):
    data = message.encode('utf-8')
    header = struct.pack('>H', len(data))
    payload = header + data
    bs = _bytes_to_bitstring(payload)
    groups = _bitstring_to_6groups(bs)
    k = _key6(key_passphrase)
    vals = [(int(g,2) ^ k) for g in groups]
    rows = (len(vals) + cols - 1) // cols
    w = cols*40 + 10
    h = rows*40 + 10
    svg = Element('svg', xmlns="http://www.w3.org/2000/svg", version="1.1", width=str(w), height=str(h))
    r = 12
    for i, v in enumerate(vals):
        a = (v >> 3) & 7
        b = v & 7
        col = i % cols
        row = i // cols
        cx = 10 + col*40 + 20
        cy = 10 + row*40 + 20
        _render_clock(svg, cx, cy, r, a, b, f"c{i}")
    xml = tostring(svg, encoding='utf-8', method='xml')
    with open(out_svg_path, 'wb') as f:
        f.write(xml)

def _angle_of_line(x1,y1,x2,y2):
    return math.degrees(math.atan2(y2-y1, x2-x1))

def _norm(a):
    return a % 360

def _idx(angle_deg):
    return int(round((angle_deg + 90)/45) % 8)

def decode_svg(in_svg_path, key_passphrase=None):
    tree = parse(in_svg_path)
    root = tree.getroot()
    lines = root.findall('.//{http://www.w3.org/2000/svg}line')
    groups = {}
    for ln in lines:
        i = ln.attrib.get('id','')
        p = i.split('_')
        if len(p) >= 2:
            cid = p[0]
            t = p[1]
            x1 = float(ln.attrib['x1']); y1 = float(ln.attrib['y1'])
            x2 = float(ln.attrib['x2']); y2 = float(ln.attrib['y2'])
            ang = _angle_of_line(x1,y1,x2,y2)
            if cid not in groups:
                groups[cid] = {}
            groups[cid][t] = ang
    items = sorted(groups.items(), key=lambda kv: int(kv[0][1:]))
    k = _key6(key_passphrase)
    vals = []
    for cid, d in items:
        if 'A' in d and 'B' in d:
            a = _idx(_norm(d['A']))
            b = _idx(_norm(d['B']))
            v = ((a & 7) << 3) | (b & 7)
            vals.append(v ^ k)
    bits = ''.join(f'{v:06b}' for v in vals)
    if len(bits) < 16:
        raise ValueError('insufficient data')
    n = int(bits[:16],2)
    data_bits = bits[16:16 + n*8]
    out = bytearray()
    for i in range(0, len(data_bits), 8):
        chunk = data_bits[i:i+8]
        if len(chunk) < 8:
            break
        out.append(int(chunk,2))
    return bytes(out)
