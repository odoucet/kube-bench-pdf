# kube-bench-pdf
Convert a kube-bench report to PDF

## Usage
Generate report like this : 
```bash
./kube-bench.sh > report.txt
```

Then convert it to PDF like this : 
```bash
kube-bench --json --include-test-output --outputfile report.json
```

And launch this tool : 
```bash
# syntax: python kube-bench-pdf.py <input> <output>
python kube-bench-pdf.py report.json report.pdf
```

Easy ! To install the dependencies, just run : 
```bash
pip install -r requirements.txt
```