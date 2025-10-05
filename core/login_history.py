"""
Login History System för Multi Team -C
Loggar och hanterar inloggningshistorik
"""

import json
import os
from datetime import datetime, timedelta
from core.debug_logger import debug, info, error


class LoginHistory:
    """Hanterar inloggningshistorik"""
    
    def __init__(self):
        self.history_file = "data/login_history.json"
        self._ensure_data_dir()
        
    def _ensure_data_dir(self):
        """Säkerställ att data-mappen finns"""
        os.makedirs("data", exist_ok=True)
        
    def log_login(self, user_email, user_name, login_time=None):
        """
        Logga en ny inloggning
        
        Args:
            user_email: Användarens email
            user_name: Användarens namn
            login_time: Tidpunkt för inloggning (default: nu)
        """
        if login_time is None:
            login_time = datetime.now()
            
        login_entry = {
            "email": user_email,
            "name": user_name,
            "timestamp": login_time.isoformat(),
            "date": login_time.strftime("%Y-%m-%d"),
            "time": login_time.strftime("%H:%M:%S"),
            "weekday": login_time.strftime("%A"),
            "formatted_date": login_time.strftime("%d %B %Y"),
            "formatted_time": login_time.strftime("%H:%M")
        }
        
        debug("LoginHistory", f"Logging login for {user_email} at {login_time}")
        
        # Läs befintlig historik
        history = self._load_history()
        
        # Lägg till ny inloggning först i listan
        history.insert(0, login_entry)
        
        # Behåll endast de senaste 50 inloggningarna PER ANVÄNDARE
        # Räkna inloggningar per email
        user_entries = [entry for entry in history if entry.get('email') == user_email]
        other_entries = [entry for entry in history if entry.get('email') != user_email]
        
        # Behåll max 50 per användare
        user_entries = user_entries[:50]
        
        # Kombinera tillbaka (behåll alla andra användares data)
        history = user_entries + other_entries
        
        # Spara uppdaterad historik
        self._save_history(history)
        
        info("LoginHistory", f"Login logged for {user_name} ({user_email})")
        debug("LoginHistory", f"Total entries in history: {len(history)}")
        debug("LoginHistory", f"User entries for {user_email}: {len(user_entries)}")
        debug("LoginHistory", f"History file path: {self.history_file}")
        
    def get_last_login(self, user_email, exclude_current=True):
        """
        Hämta senaste inloggningen för specifik användare
        
        Args:
            user_email: Användarens email att filtrera på
            exclude_current: Om True, hoppa över den allra senaste (nuvarande)
            
        Returns:
            dict: Senaste inloggningsdata eller None
        """
        history = self._load_history()
        
        # Filtrera endast denna användares inloggningar
        user_history = [entry for entry in history if entry.get('email') == user_email]
        
        if not user_history:
            debug("LoginHistory", f"No login history found for {user_email}")
            return None
            
        if exclude_current and len(user_history) > 1:
            last_login = user_history[1]  # Andra senaste (föregående)
        elif not exclude_current and len(user_history) > 0:
            last_login = user_history[0]  # Allra senaste
        else:
            debug("LoginHistory", f"No previous login found for {user_email}")
            return None
            
        debug("LoginHistory", f"Retrieved last login for {user_email}: {last_login['formatted_date']}")
        return last_login
        
    def get_login_stats(self, user_email):
        """
        Hämta inloggningsstatistik för specifik användare
        
        Args:
            user_email: Användarens email att filtrera på
            
        Returns:
            dict: Statistik om inloggningar för denna användare
        """
        history = self._load_history()
        
        # Filtrera endast denna användares inloggningar
        user_history = [entry for entry in history if entry.get('email') == user_email]
        
        if not user_history:
            return {
                "total_logins": 0,
                "first_login": None,
                "last_login": None,
                "most_active_day": None,
                "today_logins": 0,
                "week_logins": 0,
                "month_logins": 0,
                "streak_days": 0
            }
            
        now = datetime.now()
        today_str = now.strftime("%Y-%m-%d")
        
        # Räkna inloggningar för olika perioder
        today_logins = 0
        week_logins = 0
        month_logins = 0
        
        # Räkna inloggningar per dag för streak
        login_dates = set()
        day_counts = {}
        
        for entry in user_history:
            entry_date = entry["date"]
            entry_datetime = datetime.fromisoformat(entry["timestamp"])
            
            # Dagens inloggningar
            if entry_date == today_str:
                today_logins += 1
                
            # Veckans inloggningar (senaste 7 dagarna)
            days_ago = (now - entry_datetime).days
            if days_ago <= 7:
                week_logins += 1
                
            # Månadens inloggningar (senaste 30 dagarna)
            if days_ago <= 30:
                month_logins += 1
                
            # Samla unika datum för streak-beräkning
            login_dates.add(entry_date)
            
            # Räkna per veckodag
            day = entry["weekday"]
            day_counts[day] = day_counts.get(day, 0) + 1
            
        # Beräkna streak (konsekutiva dagar)
        streak_days = self._calculate_streak(login_dates, now)
        
        most_active_day = max(day_counts, key=day_counts.get) if day_counts else None
        
        stats = {
            "total_logins": len(user_history),
            "first_login": user_history[-1] if user_history else None,
            "last_login": user_history[0] if user_history else None,
            "most_active_day": most_active_day,
            "day_counts": day_counts,
            "today_logins": today_logins,
            "week_logins": week_logins,
            "month_logins": month_logins,
            "streak_days": streak_days
        }
        
        debug("LoginHistory", f"Generated login stats for {user_email}: {stats['total_logins']} total, {stats['today_logins']} today, {stats['week_logins']} this week")
        return stats
        
    def _calculate_streak(self, login_dates, current_date):
        """Beräkna konsekutiva inloggningsdagar"""
        if not login_dates:
            return 0
            
        # Sortera datum i fallande ordning
        sorted_dates = sorted([datetime.strptime(d, "%Y-%m-%d") for d in login_dates], reverse=True)
        
        streak = 0
        expected_date = current_date.date()
        
        for login_date in sorted_dates:
            if login_date.date() == expected_date:
                streak += 1
                expected_date = expected_date - timedelta(days=1)
            elif login_date.date() == expected_date + timedelta(days=1):
                # Om vi missade igår men loggade in idag, räkna ändå
                continue
            else:
                break
                
        return streak
        
    def get_achievement_message(self, stats):
        """
        Generera belöningsmeddelande baserat på statistik
        
        Args:
            stats: Statistik från get_login_stats()
            
        Returns:
            dict: Belöningsmeddelande med emoji och text
        """
        achievements = []
        
        # Dagens inloggningar
        if stats["today_logins"] >= 5:
            achievements.append({
                "emoji": "🔥",
                "title": "Power User!",
                "message": f"You've logged in {stats['today_logins']} times today!"
            })
        elif stats["today_logins"] >= 3:
            achievements.append({
                "emoji": "⚡",
                "title": "Active User!",
                "message": f"You've logged in {stats['today_logins']} times today!"
            })
        elif stats["today_logins"] == 1:
            achievements.append({
                "emoji": "👋",
                "title": "Welcome back!",
                "message": "Great to see you today!"
            })
            
        # Veckans inloggningar
        if stats["week_logins"] >= 20:
            achievements.append({
                "emoji": "🏆",
                "title": "Weekly Champion!",
                "message": f"{stats['week_logins']} logins this week - Amazing!"
            })
        elif stats["week_logins"] >= 10:
            achievements.append({
                "emoji": "🌟",
                "title": "Weekly Star!",
                "message": f"{stats['week_logins']} logins this week!"
            })
        elif stats["week_logins"] >= 5:
            achievements.append({
                "emoji": "📈",
                "title": "Getting Active!",
                "message": f"{stats['week_logins']} logins this week!"
            })
            
        # Streak belöningar
        if stats["streak_days"] >= 7:
            achievements.append({
                "emoji": "🔥",
                "title": "On Fire!",
                "message": f"{stats['streak_days']} day login streak!"
            })
        elif stats["streak_days"] >= 3:
            achievements.append({
                "emoji": "💪",
                "title": "Building Momentum!",
                "message": f"{stats['streak_days']} day streak!"
            })
            
        # Milstolpar
        if stats["total_logins"] >= 100:
            achievements.append({
                "emoji": "💎",
                "title": "Legendary User!",
                "message": f"{stats['total_logins']} total logins - You're a legend!"
            })
        elif stats["total_logins"] >= 50:
            achievements.append({
                "emoji": "🥇",
                "title": "Gold Member!",
                "message": f"{stats['total_logins']} total logins!"
            })
        elif stats["total_logins"] >= 25:
            achievements.append({
                "emoji": "🥈",
                "title": "Silver Member!",
                "message": f"{stats['total_logins']} total logins!"
            })
        elif stats["total_logins"] >= 10:
            achievements.append({
                "emoji": "🥉",
                "title": "Bronze Member!",
                "message": f"{stats['total_logins']} total logins!"
            })
            
        # Välj det bästa achievement eller skapa ett standard
        if achievements:
            best_achievement = achievements[0]  # Ta första (högsta prioritet)
        else:
            best_achievement = {
                "emoji": "🎯",
                "title": "Welcome!",
                "message": "Keep logging in to unlock achievements!"
            }
            
        debug("LoginHistory", f"Generated achievement: {best_achievement['title']}")
        return best_achievement
        
    def _load_history(self):
        """Ladda inloggningshistorik från fil"""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
                    debug("LoginHistory", f"Loaded {len(history)} login entries")
                    return history
            else:
                debug("LoginHistory", "No history file found, starting fresh")
                return []
        except Exception as e:
            error("LoginHistory", f"Failed to load history: {e}")
            return []
            
    def _save_history(self, history):
        """Spara inloggningshistorik till fil"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
                debug("LoginHistory", f"Saved {len(history)} login entries")
        except Exception as e:
            error("LoginHistory", f"Failed to save history: {e}")


# Global instans
login_history = LoginHistory()


# Export
__all__ = ['LoginHistory', 'login_history']
