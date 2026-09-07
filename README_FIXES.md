# ATLAS SIH2026 — Bug-Fixed Build

## Fixed
1. **Login is linked to a learner profile**
   - `ananya / atlas123` → Ananya Sharma (P001)
   - `rohit / atlas123` → Rohit Verma (P002)
   - `rahul / atlas123` → Rahul Sharma (P003)
2. **No Ananya/Rohit profile leakage** after login.
3. **Old Streamlit session state is cleared** when changing/logging in as another user.
4. **Quiz state is isolated** and old answers do not leak into a new quiz.
5. **Submit Quiz works once**, saves the attempt once, then shows the result and a real Next button.
6. **Progress is read from SQLite per learner**, so Ananya's attempts do not appear for Rohit and vice versa.
7. **Recommendations page is actually Recommendations** (the previous `3_Recommendations.py` accidentally contained the Skill Gap page).
8. **Next buttons use `st.switch_page()`** so the flow is explicit:
   Profile → Skill Gap → Recommendations → AI Quiz → Progress.
9. **SQLite migration** adds `users.profile_code` to older databases and repairs old accounts where possible.

## Run
```powershell
streamlit run atlas_app\Home.py
```

If an old Streamlit process is running, stop it with `Ctrl+C` first and start it again.
Then hard-refresh the browser with `Ctrl+Shift+R`.
