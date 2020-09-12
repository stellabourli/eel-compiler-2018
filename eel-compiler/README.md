# eel-compiler

## EEL Compiler
Simple LL(1) compiler in python.  

### Περιεχόμενα
- Λεκτική ανάλυση  
- Συντακτική ανάλυση  
- Σημασιολογική ανάλυση  
- Παραγωγή ενδιάμεσου κώδικα  
- Βελτιστοποίηση ενδιάμεσου κώδικα  
- Παραγωγή τελικού κώδικα

### Εκφραστική δύναμη
- Συναρτήσεις και διαδικασίες  
- Μετάδοση παραμέτρων με αναφορά και τιμή  
- Φώλιασμα στη δήλωση συναρτήσεων και διαδικασιών  
- Βρόχους  
- Τύπος δεδομένων: Πραγματικοί αριθμοί
- κ.α.  
  
Η συντακτική ανάλυση γίνεται με αναδρομική κατάβαση και βασίζεται στη γραμματική LL(1).

### /files
Assignment and report.

### /tests
Working tests.  
Most updated test: full_example.eel

### Use
python3 eel.py tests/full_example.eel

### Note
This application produces 3 files. (For example by running file.eel)  
1) file.int : intermediate code  
2) file.c : intermediate code, written in C  
3) file.asm : final code, writen in Assembly

### Tested on
Python 3.6.9  
Mars 4.5 (Assembly)
