# UTF Cleaner 🧼

A *powerful* package that removes non-UTF characters from a string.

---

### **Example Usage**
```python
from utf_cleaner import UTFStringCleaner

text = "Hello, Wørld! 𝄞 💖 \x80\x99"  # Contains non-UTF bytes

cleaner = UTFStringCleaner(use_multiprocessing=True)
cleaned_text = cleaner.clean(text)

print(cleaned_text)  # Output: "Hello, Wørld! 𝄞 💖"