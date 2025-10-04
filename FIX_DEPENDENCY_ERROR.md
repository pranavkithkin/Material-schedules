# 🔧 QUICK FIX - Anthropic Dependency Error

## ❌ Error You're Seeing:
```
TypeError: Client.__init__() got an unexpected keyword argument 'proxies'
```

## ✅ Solution:

### Run this in WSL (with venv activated):
```bash
pip install --upgrade anthropic httpx
```

**OR** run the fix script:
```bash
bash fix_dependencies.sh
```

## 📝 What This Does:
- Updates `anthropic` from 0.7.7 → 0.34.2
- Updates `httpx` to compatible version
- Fixes the `proxies` argument error

## ⏱️ Time: ~30 seconds

## Then Try Again:
```bash
python app.py
```

Should work now! 🚀

---

## Alternative: Skip AI Features for Now

If you just want to test the **Data Processing Agent** (Sprint 1), you can:

1. **Remove API keys from .env** (temporarily):
   ```bash
   # Comment out these lines in .env:
   # ANTHROPIC_API_KEY=...
   # OPENAI_API_KEY=...
   ```

2. **Run app.py** - Chat service will skip AI initialization with a warning

3. **Test the validation agent** - Works without AI! (Zero tokens!)

---

**Recommended:** Just run the pip upgrade command above. It's quick! 👍
