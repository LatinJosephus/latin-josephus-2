from pathlib import Path
p=Path(__file__).resolve().parent/'certify.py'
s=p.read_text(encoding='utf-8-sig').replace('==4001 for witness','==3722 for witness').replace('existing 4,001 Niese coordinates preserved','all 3,722 currently selectable Niese coordinates per source (7,444 source/coordinate comparisons) preserved; the 4,001 Lodge segmentation markers remain byte-identical')
p.write_text(s,encoding='utf-8')
