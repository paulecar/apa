
import locale, ghostscript

def pdf2png(pdf_input_path, dpi, output_path):
    args = ["pdf2png", # actual value doesn't matter
            "-dNOPAUSE",
            "-sDEVICE=png16m",
            dpi,
            "-sOutputFile=" + output_path,
            pdf_input_path]
    # arguments have to be bytes, encode them
    encoding = locale.getpreferredencoding()
    args = [a.encode(encoding) for a in args]

    ghostscript.Ghostscript(*args)

file1="01-08-2018_scoresheet.pdf"
file2="12-18-2017_scoresheet.pdf"
file3="08-14-2017_scoresheet.pdf"
file4="02-04-2018_scoresheet.pdf"
result1_300="01-08-2018_scoresheet300.png"
result1_600="01-08-2018_scoresheet600.png"
result2_300="12-18-2017_scoresheet300.png"
result2_600="12-18-2017_scoresheet600.png"
result3_300="08-14-2017_scoresheet300.png"
result3_600="08-14-2017_scoresheet600.png"
result4_300="02-04-2018_scoresheet300.png"
result4_600="02-04-2018_scoresheet600.png"

print("Off we go!")
pdf2png(file1, "-r300", result1_300)
pdf2png(file1, "-r600", result1_600)
pdf2png(file2, "-r300", result2_300)
pdf2png(file2, "-r600", result2_600)
pdf2png(file3, "-r300", result3_300)
pdf2png(file3, "-r600", result3_600)
pdf2png(file4, "-r300", result4_300)
pdf2png(file4, "-r600", result4_600)
print("Done?")
