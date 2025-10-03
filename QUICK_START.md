# 🚀 QUICK START - Get Running in 5 Minutes

## For Absolute Beginners

Follow these steps exactly as written. Don't skip any step!

---

## Step 1: Open PowerShell ⚡

1. Press `Windows Key`
2. Type `PowerShell`
3. Click on **Windows PowerShell** (the blue icon)

---

## Step 2: Go to Project Folder 📁

Copy and paste this command (press Enter after pasting):

```powershell
cd "C:\Users\PKP\Documents\PRANAV\Projects\With a clear picture\9. material delivery dashboard"
```

---

## Step 3: Create Virtual Environment 🔧

Copy and paste this:

```powershell
python -m venv venv
```

Wait for it to finish (takes about 30 seconds).

---

## Step 4: Activate Virtual Environment ✅

Copy and paste this:

```powershell
.\venv\Scripts\Activate.ps1
```

**If you get an error about "execution policy"**, copy and paste this first:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Type `Y` and press Enter, then try Step 4 again.

**You'll know it worked when you see `(venv)` at the start of your command line.**

---

## Step 5: Install Everything 📦

Copy and paste this:

```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

This takes 2-3 minutes. Wait for it to complete.

---

## Step 6: Set Up Configuration ⚙️

Copy and paste these two commands:

```powershell
Copy-Item .env.example .env
notepad .env
```

A text file will open. You can leave it as-is for now (or add API keys if you have them).

Just **close the file** (it saves automatically).

---

## Step 7: Create Database 💾

Copy and paste this:

```powershell
python init_db.py --with-samples
```

When it asks "Proceed with database initialization? (yes/no):", type `yes` and press Enter.

---

## Step 8: Start the App! 🎉

Copy and paste this:

```powershell
python app.py
```

You should see something like:
```
* Running on http://0.0.0.0:5000
* Debug mode: on
```

---

## Step 9: Open Your Browser 🌐

1. Open your web browser (Chrome, Edge, Firefox, etc.)
2. Go to this address:

```
http://localhost:5000
```

**You should see the dashboard!** 🎊

---

## 🎮 What to Try First

### 1. View Sample Data
- Click around the dashboard
- Check the statistics cards
- Look at the sample materials, POs, and deliveries

### 2. Try the Chat
- Click the blue chat button (bottom-right corner)
- Type: `Show me all materials`
- Press Enter
- Wait for response

### 3. Add New Material
1. Click **Materials** in the top menu
2. Click **Add Material** button
3. Fill in the form
4. Click **Save**

---

## 🛑 How to Stop the App

In the PowerShell window where app is running:
- Press `Ctrl + C`

---

## 🔄 How to Start Again Later

Next time you want to run the app:

1. Open PowerShell
2. Run these commands:
```powershell
cd "C:\Users\PKP\Documents\PRANAV\Projects\With a clear picture\9. material delivery dashboard"
.\venv\Scripts\Activate.ps1
python app.py
```
3. Open browser to http://localhost:5000

---

## ❌ Troubleshooting

### Problem: "python is not recognized"

**Solution:** Install Python from https://www.python.org/downloads/

Make sure to check "Add Python to PATH" during installation!

---

### Problem: "pip is not recognized"

**Solution:** After installing Python, close and reopen PowerShell, then try again.

---

### Problem: Can't activate venv

**Solution:** Run this first:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

### Problem: Port 5000 is already in use

**Solution:** 
1. Close any other applications using port 5000
2. Or edit `app.py` and change `port=5000` to `port=5001`

---

### Problem: Page doesn't load

**Check:**
1. Is the app still running in PowerShell?
2. Did you see any error messages?
3. Try http://127.0.0.1:5000 instead

---

### Problem: Nothing works!

**Complete Reset:**
```powershell
# Stop the app (Ctrl+C)
# Then run:
python init_db.py --with-samples
python app.py
```

---

## 📚 Want to Learn More?

After you get it running, read these files in order:

1. `STEP_BY_STEP_GUIDE.md` - Detailed walkthrough
2. `SETUP_GUIDE.md` - Complete reference
3. `PROJECT_SUMMARY.md` - What you can do

---

## 🎯 What's Next?

### Add Your Own Data
- Replace sample materials with your actual materials
- Create real purchase orders
- Track actual deliveries

### Set Up AI (Optional)
- Get Claude API key (see STEP_BY_STEP_GUIDE.md)
- Add it to .env file
- Restart the app
- Try AI chat features

### Set Up n8n (Optional)
- Install n8n
- Create workflows
- Automate data extraction

---

## 💡 Pro Tips

1. **Keep PowerShell window open** while using the app
2. **Don't close the browser tab** - open new tabs if you need
3. **Use the chat** - it's very helpful!
4. **Check the dashboard** regularly for statistics
5. **Review AI suggestions** before approving them

---

## ✅ You're Done!

If you can see the dashboard and click around, **you're all set!**

The app is now running on your computer and you can:
- ✅ Track materials
- ✅ Manage purchase orders
- ✅ Monitor payments
- ✅ Track deliveries
- ✅ Use AI chat
- ✅ Review AI suggestions

**Congratulations!** 🎉

---

## 📞 Need Help?

1. **Check error messages** - they usually tell you what's wrong
2. **Read the guides** - especially STEP_BY_STEP_GUIDE.md
3. **Try the troubleshooting section** above
4. **Reset and try again** - use the Complete Reset commands

---

**Remember:** The app runs on YOUR computer. When you close PowerShell or stop the app, it stops running. Start it again when you need it!

---

Last Updated: October 3, 2025
Version: 1.0.0
Status: READY TO USE ✅
