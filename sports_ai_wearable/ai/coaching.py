def analyze_performance(heart_rate, total_steps, activity, max_hr=190):
    hr_zone = (heart_rate / max_hr) * 100
    advice = []
    alert_level = "green"

    # Heart rate zone advice
    if hr_zone > 90:
        advice.append("🚨 DANGER: Heart rate critically high! Stop and rest immediately.")
        alert_level = "red"
    elif hr_zone > 75:
        advice.append("⚠️ HIGH INTENSITY: You're pushing hard! Monitor your breathing.")
        alert_level = "orange"
    elif hr_zone > 50:
        advice.append("✅ OPTIMAL ZONE: Perfect training intensity! Keep it up.")
        alert_level = "green"
    else:
        advice.append("💤 LOW INTENSITY: Heart rate is low. You can push harder!")
        alert_level = "blue"

    # Activity-specific advice
    if activity == "Running" and heart_rate > 160:
        advice.append("🏃 Slow your running pace to avoid overexertion.")
    elif activity == "Resting" and heart_rate > 100:
        advice.append("😴 Heart rate is high even at rest — take a longer break.")
    elif activity == "Jumping":
        advice.append("⬆️ High-impact activity detected — land softly to protect joints.")
    elif activity == "Walking" and heart_rate < 80:
        advice.append("🚶 Steady walk pace — great for recovery.")

    if total_steps > 500:
        advice.append(f"👟 Great effort! {total_steps} steps so far — stay hydrated.")

    return advice, round(hr_zone, 1), alert_level